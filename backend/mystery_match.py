"""
Mystery Match Backend API
Progressive profile unlock system for anonymous dating
"""
from fastapi import APIRouter, HTTPException, Depends, Header, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import random
import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Async DB imports
from database.async_db import (
    fetch_one,
    fetch_all,
    execute,
    async_get_daily_match_count,
    async_is_premium_user,
    async_create_match,
    async_get_user_matches,
)
from utils.feature_flags import feature_required
from utils.moderation import create_report, check_auto_ban_threshold

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Create router
mystery_router = APIRouter(prefix="/api/mystery", tags=["Mystery Match"])

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
    - 20 msgs: Level 1 (Gender + Age)
    - 60 msgs: Level 2 (Blurred Photo)
    - 100 msgs: Level 3 (Interests + Bio + Clearer Photo)
    - 150 msgs: Level 4 (Full Profile - Clear Photo + Real Name)
    """
    if message_count >= 150:
        return 4  # Full profile unlocked
    elif message_count >= 100:
        return 3  # Interests + Bio + Clearer photo
    elif message_count >= 60:
        return 2  # Blurred photo
    elif message_count >= 20:
        return 1  # Gender + Age
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
    user_id = request.user_id

    # 1. verify user exists
    user = await fetch_one("SELECT * FROM users WHERE tg_user_id=$1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    # 2. check premium
    is_premium = await async_is_premium_user(user_id)

    # 3. daily limit for free users
    if not is_premium and await async_get_daily_match_count(user_id) >= 3:
        return {
            "success": False,
            "error": "daily_limit_reached",
            "message": "You've reached your daily limit of 3 matches. Upgrade to Premium!",
            "matches_today": 3,
            "limit": 3,
        }

    # 4. build WHERE clause and parameter list
    where_clauses = ["tg_user_id != $1"]
    params = [user_id]
    idx = 2

    if is_premium and request.preferred_gender:
        where_clauses.append(f"gender = ${idx}")
        params.append(request.preferred_gender)
        idx += 1

    if is_premium and request.preferred_city:
        where_clauses.append(f"city ILIKE ${idx}")
        params.append(f"%{request.preferred_city}%")
        idx += 1

    # age filter always applied
    where_clauses.append(f"age BETWEEN ${idx} AND ${idx+1}")
    params += [request.preferred_age_min, request.preferred_age_max]

    sql = f"""
        SELECT tg_user_id, age, gender, city
        FROM users
        WHERE {' AND '.join(where_clauses)}
          AND tg_user_id NOT IN (
            SELECT CASE WHEN user1_id = $1 THEN user2_id ELSE user1_id END
            FROM mystery_matches
            WHERE (user1_id = $1 OR user2_id = $1) AND is_active = TRUE
        )
    """

    potential_matches = await fetch_all(sql, *params)
    if not potential_matches:
        return {
            "success": False,
            "error": "no_matches_found",
            "message": "No matches found right now. Try again later!",
        }

    selected = random.choice(potential_matches)
    match_id = await async_create_match(user_id, selected["tg_user_id"])

    return {
        "success": True,
        "match_id": match_id,
        "expires_at": (datetime.utcnow() + timedelta(hours=48)).isoformat(),
        "is_premium": is_premium,
        "message_count": 0,
        "next_unlock_at": 20,
    }

@mystery_router.get("/my-matches/{user_id}")
async def get_my_matches(user_id: int):
    is_premium = await async_is_premium_user(user_id)
    matches = await async_get_user_matches(user_id)
    result = []
    for m in matches:
        msg_count = m.get("message_count", 0)
        # unlock level calculation
        if msg_count >= 150:
            unlock_level = 4
        elif msg_count >= 100:
            unlock_level = 3
        elif msg_count >= 60:
            unlock_level = 2
        elif msg_count >= 20:
            unlock_level = 1
        else:
            unlock_level = 0

        result.append({
            "match_id": m["match_id"],
            "partner_id": m["partner_id"],
            "message_count": msg_count,
            "unlock_level": unlock_level,
            "expires_at": m.get("expires_at").isoformat() if m.get("expires_at") else None,
            "secret_chat_active": m.get("secret_chat_active"),
        })
    return {"success": True, "matches": result, "is_premium": is_premium}

@mystery_router.post("/send-message")
async def send_message(request: MessageRequest):
    # Using async helper from database/async_db.py  
    from database.async_db import async_send_message as send_msg_helper
    res = await send_msg_helper(request.match_id, request.sender_id, request.message_text)
    return {"success": True, "message_id": res.get("message_id", -1)}

@mystery_router.get("/chat/{match_id}")
async def get_chat_messages(match_id: int, user_id: int):
    # Verify match and user via async helpers
    match = await fetch_one(
        """SELECT * FROM mystery_matches WHERE id=$1
           AND (user1_id=$2 OR user2_id=$2)""",
        match_id, user_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    messages = await fetch_all(
        """SELECT id, sender_id, message_text, created_at, is_secret_chat
           FROM match_messages WHERE match_id=$1 ORDER BY created_at ASC""",
        match_id
    )
    unlock_level = get_unlock_level(match["message_count"])
    is_premium = await async_is_premium_user(user_id)
    partner_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
    partner_profile = get_unlocked_profile_data(partner_id, unlock_level, is_premium)

    return {
        "success": True,
        "match_id": match_id,
        "partner": partner_profile,
        "messages": [
            {
                "id": m["id"],
                "sender_id": m["sender_id"],
                "is_me": m["sender_id"] == user_id,
                "message": m["message_text"],
                "timestamp": m["created_at"].isoformat()
            } for m in messages
        ],
        "message_count": match["message_count"],
        "unlock_level": unlock_level,
        "expires_at": match["expires_at"].isoformat(),
        "secret_chat_active": match["secret_chat_active"],
    }

@mystery_router.post("/unmatch")
async def unmatch(request: UnmatchRequest):
    match = await fetch_one(
        """SELECT * FROM mystery_matches WHERE id=$1 AND (user1_id=$2 OR user2_id=$2)""",
        request.match_id, request.user_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    await execute(
        """UPDATE mystery_matches SET is_active=FALSE, unmatch_reason=$3, unmatch_by_user=$2 WHERE id=$1""",
        request.match_id, request.user_id, request.reason
    )
    return {"success": True, "message": "Match ended successfully"}

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


# ==========================================
# UNMATCH & BLOCK ENDPOINTS
# ==========================================

class UnmatchRequest(BaseModel):
    match_id: int
    user_id: int
    reason: Optional[str] = None

@mystery_router.post("/unmatch")
async def unmatch(request: UnmatchRequest):
    """End a mystery match"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify user is part of this match
            cursor.execute("""
                SELECT * FROM mystery_matches 
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
            """, (request.match_id, request.user_id, request.user_id))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            # Deactivate match
            cursor.execute("""
                UPDATE mystery_matches 
                SET is_active = FALSE,
                    unmatch_reason = %s,
                    unmatch_by_user = %s
                WHERE id = %s
            """, (request.reason, request.user_id, request.match_id))
            
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

class BlockRequest(BaseModel):
    user_id: int
    block_user_id: int
    reason: Optional[str] = None

@mystery_router.post("/block")
async def block_user(request: BlockRequest):
    # Insert into blocked_users
    await execute(
        """INSERT INTO blocked_users (user_id, blocked_user_id, reason, created_at)
           VALUES ($1, $2, $3, NOW())
           ON CONFLICT (user_id, blocked_user_id) DO NOTHING""",
        request.user_id, request.block_user_id, request.reason
    )
    # Deactivate active matches
    await execute(
        """UPDATE mystery_matches SET is_active=FALSE, unmatch_reason='User blocked'
           WHERE ((user1_id=$1 AND user2_id=$2) OR (user1_id=$2 AND user2_id=$1))
             AND is_active=TRUE""",
        request.user_id, request.block_user_id
    )
    return {"success": True, "message": "User blocked successfully"}

@mystery_router.post("/unblock")
async def unblock_user(request: BlockRequest):
    await execute(
        """DELETE FROM blocked_users WHERE user_id=$1 AND blocked_user_id=$2""",
        request.user_id, request.block_user_id
    )
    return {"success": True, "message": "User unblocked successfully"}

# ==========================================
# EXTEND MATCH ENDPOINT (PREMIUM FEATURE)
# ==========================================

class ExtendMatchRequest(BaseModel):
    match_id: int
    user_id: int

@mystery_router.post("/extend-match")
async def extend_match(request: ExtendMatchRequest):
    """Extend match expiry by 24 hours (costs 50 Telegram Stars)"""
    try:
        # Check if user is premium (premium gets unlimited extensions)
        is_premium = is_premium_user(request.user_id)
        
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Verify match exists and user is part of it
            cursor.execute("""
                SELECT * FROM mystery_matches 
                WHERE id = %s 
                AND (user1_id = %s OR user2_id = %s)
                AND is_active = TRUE
            """, (request.match_id, request.user_id, request.user_id))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            # Premium users get free extensions
            if not is_premium:
                # TODO: Implement Telegram Stars payment verification here
                # For now, we'll just charge coins or require payment link
                pass
            
            # Extend expiry by 24 hours
            cursor.execute("""
                UPDATE mystery_matches 
                SET expires_at = expires_at + INTERVAL '24 hours'
                WHERE id = %s
                RETURNING expires_at
            """, (request.match_id,))
            
            new_expiry = cursor.fetchone()["expires_at"]
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "Match extended by 24 hours",
                "new_expiry": new_expiry.isoformat(),
                "cost": 0 if is_premium else 50  # 50 Stars for non-premium
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in extend_match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# MODERATION & REPORTING ENDPOINTS
# ==========================================

class ReportRequest(BaseModel):
    reporter_id: int
    reported_user_id: int
    content_type: str  # 'message', 'profile', 'photo'
    content_id: str
    reason: str

@mystery_router.post("/report")
async def report_content(request: ReportRequest):
    report_id = await create_report(
        request.reporter_id,
        request.reported_user_id,
        request.content_type,
        request.content_id,
        request.reason,
    )
    await check_auto_ban_threshold(request.reported_user_id)
    return {"success": True, "report_id": report_id}


# ==========================================
# WEBSOCKET REAL-TIME CHAT
# ==========================================

from websocket_manager import manager, handle_websocket_message

@mystery_router.websocket("/ws/chat/{match_id}/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, match_id: int, user_id: int):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, match_id, user_id)
    
    try:
        # Send initial connection success
        await websocket.send_json({
            "type": "connected",
            "match_id": match_id,
            "user_id": user_id,
            "message": "Connected to Mystery Match chat"
        })
        
        # Listen for messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle the message
            await handle_websocket_message(websocket, match_id, user_id, data)
            
    except WebSocketDisconnect:
        manager.disconnect(match_id, user_id)
        logger.info(f"User {user_id} disconnected from match {match_id}")
        
        # Notify other user
        await manager.broadcast_to_match(match_id, {
            "type": "user_offline",
            "user_id": user_id
        })
    
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id} in match {match_id}: {e}")
        manager.disconnect(match_id, user_id)

@mystery_router.get("/chat/online-status/{match_id}/{user_id}")
async def check_online_status(match_id: int, user_id: int):
    """Check if the other user in match is online"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get the other user's ID
            cursor.execute("""
                SELECT user1_id, user2_id 
                FROM mystery_matches 
                WHERE id = %s
            """, (match_id,))
            
            match = cursor.fetchone()
            
            if not match:
                conn.close()
                raise HTTPException(status_code=404, detail="Match not found")
            
            # Determine the other user
            other_user_id = match['user2_id'] if match['user1_id'] == user_id else match['user1_id']
            
            conn.close()
            
            # Check if online via WebSocket manager
            is_online = manager.is_user_online(match_id, other_user_id)
            
            return {
                "success": True,
                "user_id": other_user_id,
                "is_online": is_online
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking online status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

