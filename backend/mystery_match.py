"""
Mystery Match Backend API
Progressive profile unlock system for anonymous dating
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import random
import os
import logging

logger = logging.getLogger(__name__)

# Create router
mystery_router = APIRouter(prefix="/api/mystery", tags=["Mystery Match"])

# Database connection helper
def get_db_connection():
    """Get PostgreSQL database connection from environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return psycopg2.connect(database_url)
    else:
        # Fallback to individual environment variables
        return psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', '5432'),
            database=os.getenv('POSTGRES_DB', 'luvhive_bot'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres123')
        )

# ==========================================
# MODELS
# ==========================================

class MysteryMatchRequest(BaseModel):
    user_id: int  # Telegram user ID
    preferred_gender: Optional[str] = None  # Only for premium users
    preferred_age_min: Optional[int] = 18
    preferred_age_max: Optional[int] = 100
    preferred_city: Optional[str] = None  # Only for premium users

class MessageRequest(BaseModel):
    match_id: int
    sender_id: int
    message_text: str

class SecretChatRequest(BaseModel):
    match_id: int
    requester_id: int
    duration_minutes: int  # 5, 10, 15, 30, 60

class UnmatchRequest(BaseModel):
    match_id: int
    user_id: int

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def is_premium_user(user_id: int) -> bool:
    """Check if user has active premium subscription"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # First check users table for is_premium and premium_until
            cursor.execute("""
                SELECT is_premium, premium_until
                FROM users 
                WHERE tg_user_id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            
            if user:
                # Check if user has is_premium flag
                if user['is_premium']:
                    # If premium_until exists, check if it's still valid
                    if user['premium_until']:
                        from datetime import datetime
                        if user['premium_until'] > datetime.now():
                            conn.close()
                            return True
                    else:
                        # is_premium is True but no expiry = lifetime premium
                        conn.close()
                        return True
            
            # Fallback: Check payments table for completed subscriptions
            cursor.execute("""
                SELECT * FROM payments 
                WHERE user_id = %s 
                AND status = 'completed'
                AND expires_at > NOW()
                ORDER BY expires_at DESC
                LIMIT 1
            """, (user_id,))
            
            subscription = cursor.fetchone()
            conn.close()
            return subscription is not None
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False

def get_daily_match_count(user_id: int) -> int:
    """Get how many matches user has made today"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM mystery_matches
                WHERE (user1_id = %s OR user2_id = %s)
                AND DATE(created_at) = CURRENT_DATE
            """, (user_id, user_id))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
    except Exception as e:
        logger.error(f"Error getting daily match count: {e}")
        return 0

def get_unlock_level(message_count: int) -> int:
    """Determine unlock level based on message count
    Thresholds:
    - 10 msgs: Level 1 (Age + City)
    - 30 msgs: Level 2 (Blurred Photo)
    - 50 msgs: Level 3 (Interests + Bio + Clearer Photo)
    - 100 msgs: Level 4 (Full Profile - Photo + Real Name)
    """
    if message_count >= 100:
        return 4  # Full profile unlocked
    elif message_count >= 50:
        return 3  # Interests + Bio + Clearer photo
    elif message_count >= 30:
        return 2  # Blurred photo
    elif message_count >= 10:
        return 1  # Age + City
    else:
        return 0  # Nothing unlocked yet

def get_unlocked_profile_data(user_id: int, unlock_level: int, is_premium: bool = False):
    """Get profile data based on unlock level"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    tg_user_id,
                    gender,
                    age,
                    city,
                    bio,
                    interests,
                    profile_photo_url
                FROM users
                WHERE tg_user_id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return None
            
            # Premium users see everything instantly
            if is_premium or unlock_level >= 4:
                return {
                    "user_id": user["tg_user_id"],
                    "age": user["age"],
                    "gender": user["gender"],
                    "city": user["city"],
                    "bio": user["bio"],
                    "interests": user["interests"],
                    "photo_url": user["profile_photo_url"],
                    "photo_blur": 0,
                    "unlock_level": 4
                }
            
            # Progressive unlock for free users
            profile = {
                "user_id": "Mystery User",
                "unlock_level": unlock_level
            }
            
            if unlock_level >= 1:  # 10+ messages
                profile["age"] = user["age"]
                profile["city"] = user["city"]
            
            if unlock_level >= 2:  # 30+ messages
                profile["photo_url"] = user["profile_photo_url"]
                profile["photo_blur"] = 50  # 50% blur
            
            if unlock_level >= 3:  # 50+ messages
                profile["interests"] = user["interests"]
                profile["bio"] = user["bio"]
                profile["photo_blur"] = 25  # 25% blur
            
            return profile
            
    except Exception as e:
        logger.error(f"Error getting profile data: {e}")
        return None

# ==========================================
# API ENDPOINTS
# ==========================================

@mystery_router.post("/find-match")
async def find_mystery_match(request: MysteryMatchRequest):
    """
    Find a new mystery match
    - Free users: 3 matches per day, random matching
    - Premium users: Unlimited matches, can filter by gender/city
    """
    try:
        user_id = request.user_id
        
        # Check if user exists
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE tg_user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                raise HTTPException(status_code=404, detail="User not found. Please register first.")
        
        # Check premium status
        is_premium = is_premium_user(user_id)
        
        # Check daily limit for free users
        if not is_premium:
            daily_count = get_daily_match_count(user_id)
            if daily_count >= 3:
                conn.close()
                return {
                    "success": False,
                    "error": "daily_limit_reached",
                    "message": "You've reached your daily limit of 3 matches. Upgrade to Premium for unlimited matches!",
                    "matches_today": daily_count,
                    "limit": 3
                }
        
        # Build matching query
        query = """
            SELECT tg_user_id, age, gender, city 
            FROM users 
            WHERE tg_user_id != %s
            AND tg_user_id NOT IN (
                -- Exclude users already matched
                SELECT CASE 
                    WHEN user1_id = %s THEN user2_id 
                    ELSE user1_id 
                END
                FROM mystery_matches
                WHERE (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
            )
        """
        
        query_params = [user_id, user_id, user_id, user_id]
        
        # Add filters for premium users
        if is_premium:
            if request.preferred_gender:
                query += " AND gender = %s"
                query_params.append(request.preferred_gender)
            
            if request.preferred_city:
                query += " AND city ILIKE %s"
                query_params.append(f"%{request.preferred_city}%")
        
        # Age filter (for all users)
        query += " AND age BETWEEN %s AND %s"
        query_params.extend([request.preferred_age_min, request.preferred_age_max])
        
        # Execute query
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, query_params)
            potential_matches = cursor.fetchall()
            
            if not potential_matches:
                conn.close()
                
                # Premium user specific gender messages
                if is_premium and request.preferred_gender and request.preferred_gender != 'random':
                    gender_label = "Female" if request.preferred_gender.lower() == 'female' else "Male"
                    alternative_gender = "male" if request.preferred_gender.lower() == 'female' else "female"
                    alternative_label = "Male" if alternative_gender == 'male' else "Female"
                    
                    return {
                        "success": False,
                        "error": "gender_not_available",
                        "message": f"{gender_label} users are not currently available. You can match with {alternative_label} users or try again later.",
                        "requested_gender": request.preferred_gender,
                        "alternative_gender": alternative_gender
                    }
                
                return {
                    "success": False,
                    "error": "no_matches_found",
                    "message": "No matches found right now. Try again in a few minutes!"
                }
            
            # Random selection
            selected_match = random.choice(potential_matches)
            match_user_id = selected_match["tg_user_id"]
            
            # Create mystery match
            cursor.execute("""
                INSERT INTO mystery_matches 
                (user1_id, user2_id, created_at, expires_at, message_count, is_active, user1_unlock_level, user2_unlock_level)
                VALUES (%s, %s, NOW(), NOW() + INTERVAL '48 hours', 0, TRUE, 0, 0)
                RETURNING id
            """, (user_id, match_user_id))
            
            match_id = cursor.fetchone()["id"]
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "match_id": match_id,
                "mystery_user": {
                    "display_name": "Mystery User",
                    "silhouette": True,
                    "unlock_level": 0
                },
                "expires_at": (datetime.now() + timedelta(hours=48)).isoformat(),
                "message_count": 0,
                "next_unlock_at": 10,  # First unlock at 10 messages (Age + City)
                "is_premium": is_premium
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in find_mystery_match: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.get("/my-matches/{user_id}")
async def get_my_matches(user_id: int):
    """Get all active mystery matches for a user"""
    try:
        conn = get_db_connection()
        is_premium = is_premium_user(user_id)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    id as match_id,
                    CASE 
                        WHEN user1_id = %s THEN user2_id 
                        ELSE user1_id 
                    END as partner_id,
                    CASE 
                        WHEN user1_id = %s THEN user1_unlock_level 
                        ELSE user2_unlock_level 
                    END as my_unlock_level,
                    CASE 
                        WHEN user1_id = %s THEN user2_unlock_level 
                        ELSE user1_unlock_level 
                    END as partner_unlock_level,
                    message_count,
                    created_at,
                    expires_at,
                    secret_chat_active
                FROM mystery_matches
                WHERE (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
                ORDER BY created_at DESC
            """, (user_id, user_id, user_id, user_id, user_id))
            
            matches = cursor.fetchall()
            
            # Get unlock level for each match
            result = []
            for match in matches:
                unlock_level = get_unlock_level(match["message_count"])
                partner_profile = get_unlocked_profile_data(
                    match["partner_id"], 
                    unlock_level,
                    is_premium
                )
                
                result.append({
                    "match_id": match["match_id"],
                    "partner": partner_profile if partner_profile else {"display_name": "Mystery User"},
                    "message_count": match["message_count"],
                    "unlock_level": unlock_level,
                    "next_unlock_at": [10, 30, 50, 100][unlock_level] if unlock_level < 4 else None,  # Unlock thresholds
                    "created_at": match["created_at"].isoformat(),
                    "expires_at": match["expires_at"].isoformat(),
                    "time_remaining": str(match["expires_at"] - datetime.now()),
                    "secret_chat_active": match["secret_chat_active"]
                })
            
            conn.close()
            
            return {
                "success": True,
                "matches": result,
                "total": len(result),
                "is_premium": is_premium,
                "daily_limit": None if is_premium else f"{get_daily_match_count(user_id)}/3"
            }
            
    except Exception as e:
        logger.error(f"Error in get_my_matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.post("/send-message")
async def send_message(request: MessageRequest):
    """
    Send a message in mystery match
    Automatically unlocks profile pieces at milestones (10, 30, 50, 100 messages)
    """
    try:
        conn = get_db_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify match exists and is active
            cursor.execute("""
                SELECT * FROM mystery_matches 
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
            """, (request.match_id, request.sender_id, request.sender_id))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found or expired")
            
            # Check if match has expired
            if match["expires_at"] < datetime.now():
                cursor.execute("""
                    UPDATE mystery_matches 
                    SET is_active = FALSE 
                    WHERE id = %s
                """, (request.match_id,))
                conn.commit()
                conn.close()
                raise HTTPException(status_code=410, detail="Match has expired")
            
            # Insert message
            cursor.execute("""
                INSERT INTO match_messages 
                (match_id, sender_id, message_text, created_at, is_secret_chat)
                VALUES (%s, %s, %s, NOW(), %s)
                RETURNING id
            """, (request.match_id, request.sender_id, request.message_text, match["secret_chat_active"]))
            
            message_id = cursor.fetchone()["id"]
            
            # Increment message count
            cursor.execute("""
                UPDATE mystery_matches 
                SET message_count = message_count + 1
                WHERE id = %s
                RETURNING message_count
            """, (request.match_id,))
            
            new_count = cursor.fetchone()["message_count"]
            
            # Check if unlock milestone reached
            old_level = get_unlock_level(new_count - 1)
            new_level = get_unlock_level(new_count)
            
            unlock_achieved = None
            if new_level > old_level:
                # Unlock achieved!
                unlock_achieved = {
                    "level": new_level,
                    "unlocked": []
                }
                
                if new_level == 1:
                    unlock_achieved["unlocked"] = ["age", "city"]
                elif new_level == 2:
                    unlock_achieved["unlocked"] = ["blurred_photo"]
                elif new_level == 3:
                    unlock_achieved["unlocked"] = ["interests", "bio", "clearer_photo"]
                elif new_level == 4:
                    unlock_achieved["unlocked"] = ["full_photo", "real_name"]
                
                # Update unlock levels in database
                if match["user1_id"] == request.sender_id:
                    cursor.execute("""
                        UPDATE mystery_matches 
                        SET user1_unlock_level = %s
                        WHERE id = %s
                    """, (new_level, request.match_id))
                else:
                    cursor.execute("""
                        UPDATE mystery_matches 
                        SET user2_unlock_level = %s
                        WHERE id = %s
                    """, (new_level, request.match_id))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message_id": message_id,
                "message_count": new_count,
                "unlock_level": new_level,
                "unlock_achieved": unlock_achieved,
                "next_unlock_at": [10, 30, 50, 100][new_level] if new_level < 4 else None  # Unlock thresholds
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.get("/chat/{match_id}")
async def get_chat_messages(match_id: int, user_id: int):
    """Get all messages for a mystery match"""
    try:
        conn = get_db_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify user is part of this match
            cursor.execute("""
                SELECT * FROM mystery_matches 
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
            """, (match_id, user_id, user_id))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            # Get messages
            cursor.execute("""
                SELECT 
                    id,
                    sender_id,
                    message_text,
                    created_at,
                    is_secret_chat
                FROM match_messages
                WHERE match_id = %s
                ORDER BY created_at ASC
            """, (match_id,))
            
            messages = cursor.fetchall()
            
            # Get current unlock level
            unlock_level = get_unlock_level(match["message_count"])
            is_premium = is_premium_user(user_id)
            
            # Get partner profile
            partner_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
            partner_profile = get_unlocked_profile_data(partner_id, unlock_level, is_premium)
            
            conn.close()
            
            return {
                "success": True,
                "match_id": match_id,
                "partner": partner_profile,
                "messages": [
                    {
                        "id": msg["id"],
                        "sender_id": msg["sender_id"],
                        "is_me": msg["sender_id"] == user_id,
                        "message": msg["message_text"],
                        "timestamp": msg["created_at"].isoformat()
                    }
                    for msg in messages
                ],
                "message_count": match["message_count"],
                "unlock_level": unlock_level,
                "expires_at": match["expires_at"].isoformat(),
                "secret_chat_active": match["secret_chat_active"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_chat_messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.post("/unmatch")
async def unmatch(request: UnmatchRequest):
    """End a mystery match"""
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            # Verify user is part of this match
            cursor.execute("""
                UPDATE mystery_matches 
                SET is_active = FALSE
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
            """, (request.match_id, request.user_id, request.user_id))
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Match ended successfully"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in unmatch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.post("/request-secret-chat")
async def request_secret_chat(request: SecretChatRequest):
    """Request to start a secret chat with timer"""
    try:
        conn = get_db_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify match exists
            cursor.execute("""
                SELECT * FROM mystery_matches 
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
            """, (request.match_id, request.requester_id, request.requester_id))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            # Create secret chat request notification
            partner_id = match["user2_id"] if match["user1_id"] == request.requester_id else match["user1_id"]
            
            # Store request (you can add a secret_chat_requests table)
            # For now, just return success
            
            conn.close()
            
            return {
                "success": True,
                "message": "Secret chat request sent",
                "partner_id": partner_id,
                "duration_minutes": request.duration_minutes
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in request_secret_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.post("/accept-secret-chat/{match_id}")
async def accept_secret_chat(match_id: int, user_id: int, duration_minutes: int = 30):
    """Accept secret chat request and activate timer"""
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            # Activate secret chat
            cursor.execute("""
                UPDATE mystery_matches 
                SET secret_chat_active = TRUE
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
            """, (match_id, user_id, user_id))
            
            if cursor.rowcount == 0:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Secret chat activated",
                "duration_minutes": duration_minutes,
                "self_destruct_at": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in accept_secret_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@mystery_router.get("/stats/{user_id}")
async def get_user_stats(user_id: int):
    """Get user's mystery match statistics"""
    try:
        conn = get_db_connection()
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get total matches
            cursor.execute("""
                SELECT COUNT(*) as total_matches
                FROM mystery_matches
                WHERE user1_id = %s OR user2_id = %s
            """, (user_id, user_id))
            total_matches = cursor.fetchone()["total_matches"]
            
            # Get active matches
            cursor.execute("""
                SELECT COUNT(*) as active_matches
                FROM mystery_matches
                WHERE (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
            """, (user_id, user_id))
            active_matches = cursor.fetchone()["active_matches"]
            
            # Get today's matches
            today_matches = get_daily_match_count(user_id)
            
            # Get total messages sent
            cursor.execute("""
                SELECT COUNT(*) as messages_sent
                FROM match_messages
                WHERE sender_id = %s
            """, (user_id,))
            messages_sent = cursor.fetchone()["messages_sent"]
            
            is_premium = is_premium_user(user_id)
            
            conn.close()
            
            return {
                "success": True,
                "user_id": user_id,
                "is_premium": is_premium,
                "total_matches": total_matches,
                "active_matches": active_matches,
                "today_matches": today_matches,
                "daily_limit": None if is_premium else 3,
                "messages_sent": messages_sent
            }
            
    except Exception as e:
        logger.error(f"Error in get_user_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
