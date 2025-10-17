"""
Mystery Match Backend API - Fully Async Version
Progressive profile unlock system for anonymous dating
100% async operations for 100k+ concurrent users
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random
import logging

# Async DB helpers
from database.async_db import (
    fetch_one,
    fetch_all,
    execute,
    async_get_daily_match_count,
    async_is_premium_user,
    async_create_match,
    async_get_user_matches,
    async_send_message,        # नया helper
)
from utils.feature_flags import feature_required
from utils.moderation import create_report, check_auto_ban_threshold
from websocket_manager import manager, handle_websocket_message

logger = logging.getLogger(__name__)

mystery_router = APIRouter(prefix="/api/mystery", tags=["Mystery Match"])

# --------- Pydantic models ----------
class MysteryMatchRequest(BaseModel):
    user_id: int
    preferred_gender: Optional[str] = None
    preferred_age_min: int = 18
    preferred_age_max: int = 100
    preferred_city: Optional[str] = None

class MessageRequest(BaseModel):
    match_id: int
    sender_id: int
    message_text: str

class SecretChatRequest(BaseModel):
    match_id: int
    requester_id: int
    duration_minutes: int

class UnmatchRequest(BaseModel):
    match_id: int
    user_id: int
    reason: Optional[str] = None

class BlockRequest(BaseModel):
    user_id: int
    block_user_id: int
    reason: Optional[str] = None

class ExtendMatchRequest(BaseModel):
    match_id: int
    user_id: int

class ReportRequest(BaseModel):
    reporter_id: int
    reported_user_id: int
    content_type: str
    content_id: str
    reason: str

# --------- Helper functions ----------
def get_unlock_level(msg_count: int) -> int:
    if msg_count >= 150:
        return 4
    if msg_count >= 100:
        return 3
    if msg_count >= 60:
        return 2
    if msg_count >= 20:
        return 1
    return 0

async def async_get_unlocked_profile_data(user_id: int, unlock_level: int, is_premium: bool) -> Optional[Dict[str, Any]]:
    row = await fetch_one(
        """
        SELECT tg_user_id, gender, age, city, bio, interests, profile_photo_url
        FROM users WHERE tg_user_id=$1
        """,
        user_id,
    )
    if not row:
        return None
    # Full profile if premium or fully unlocked
    if is_premium or unlock_level >= 4:
        return {
            "user_id": row["tg_user_id"],
            "age": row["age"],
            "gender": row["gender"],
            "city": row["city"],
            "bio": row["bio"],
            "interests": row["interests"],
            "photo_url": row["profile_photo_url"],
            "photo_blur": 0,
            "unlock_level": 4,
        }
    # Partial profile based on unlock level
    profile: Dict[str, Any] = {"user_id": "Mystery User", "unlock_level": unlock_level}
    if unlock_level >= 1:
        profile["age"] = row["age"]
        profile["city"] = row["city"]
    if unlock_level >= 2:
        profile["photo_url"] = row["profile_photo_url"]
        profile["photo_blur"] = 50
    if unlock_level >= 3:
        profile["interests"] = row["interests"]
        profile["bio"] = row["bio"]
        profile["photo_blur"] = 25
    return profile

# --------- API endpoints ----------

@mystery_router.post("/find-match")
async def find_mystery_match(request: MysteryMatchRequest):
    user_id = request.user_id
    user = await fetch_one("SELECT * FROM users WHERE tg_user_id=$1", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    is_premium = await async_is_premium_user(user_id)
    if not is_premium and await async_get_daily_match_count(user_id) >= 3:
        return {
            "success": False,
            "error": "daily_limit_reached",
            "message": "You've reached your daily limit of 3 matches. Upgrade to Premium!",
        }

    clauses = ["tg_user_id != $1"]
    params: List[Any] = [user_id]
    idx = 2
    if is_premium and request.preferred_gender:
        clauses.append(f"gender = ${idx}")
        params.append(request.preferred_gender)
        idx += 1
    if is_premium and request.preferred_city:
        clauses.append(f"city ILIKE ${idx}")
        params.append(f"%{request.preferred_city}%")
        idx += 1
    clauses.append(f"age BETWEEN ${idx} AND ${idx+1}")
    params += [request.preferred_age_min, request.preferred_age_max]

    sql = f"""
        SELECT tg_user_id, age, gender, city FROM users
        WHERE {' AND '.join(clauses)}
          AND tg_user_id NOT IN (
              SELECT CASE WHEN user1_id=$1 THEN user2_id ELSE user1_id END
              FROM mystery_matches
              WHERE (user1_id=$1 OR user2_id=$1) AND is_active=TRUE
          )
    """
    candidates = await fetch_all(sql, *params)
    if not candidates:
        return {"success": False, "error": "no_matches_found", "message": "No matches found right now. Try again later!"}
    chosen = random.choice(candidates)
    match_id = await async_create_match(user_id, chosen["tg_user_id"])
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
    matches = await async_get_user_matches(user_id)
    is_premium = await async_is_premium_user(user_id)
    result = []
    for m in matches:
        msg_count = m.get("message_count", 0)
        result.append({
            "match_id": m["match_id"],
            "partner_id": m["partner_id"],
            "message_count": msg_count,
            "unlock_level": get_unlock_level(msg_count),
            "expires_at": m.get("expires_at").isoformat() if m.get("expires_at") else None,
            "secret_chat_active": m.get("secret_chat_active"),
        })
    return {"success": True, "matches": result, "is_premium": is_premium}

@mystery_router.post("/send-message")
async def send_message(request: MessageRequest):
    """Send a chat message via async helper (see async_send_message below)."""
    res = await async_send_message(request.match_id, request.sender_id, request.message_text)
    return {"success": True, "message_id": res["message_id"]}

@mystery_router.get("/chat/{match_id}")
async def get_chat_messages(match_id: int, user_id: int):
    match = await fetch_one(
        "SELECT id, user1_id, user2_id, message_count, expires_at, secret_chat_active FROM mystery_matches WHERE id=$1 AND (user1_id=$2 OR user2_id=$2)",
        match_id, user_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    messages = await fetch_all(
        "SELECT id, sender_id, message_text, created_at, is_secret_chat FROM match_messages WHERE match_id=$1 ORDER BY created_at ASC",
        match_id
    )
    unlock_level = get_unlock_level(match["message_count"])
    is_premium = await async_is_premium_user(user_id)
    partner_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
    partner_profile = await async_get_unlocked_profile_data(partner_id, unlock_level, is_premium)
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
                "timestamp": m["created_at"].isoformat(),
            }
            for m in messages
        ],
        "message_count": match["message_count"],
        "unlock_level": unlock_level,
        "expires_at": match["expires_at"].isoformat() if match["expires_at"] else None,
        "secret_chat_active": match["secret_chat_active"],
    }

@mystery_router.post("/unmatch")
async def unmatch(request: UnmatchRequest):
    match = await fetch_one(
        "SELECT id FROM mystery_matches WHERE id=$1 AND (user1_id=$2 OR user2_id=$2)",
        request.match_id, request.user_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    await execute(
        "UPDATE mystery_matches SET is_active=FALSE, unmatch_reason=$3, unmatch_by_user=$2 WHERE id=$1",
        request.match_id, request.user_id, request.reason
    )
    return {"success": True, "message": "Match ended successfully"}

@mystery_router.post("/block")
async def block_user(request: BlockRequest):
    """Block a user and deactivate any active matches."""
    await execute(
        """
        INSERT INTO blocked_users (user_id, blocked_user_id, reason, created_at)
        VALUES ($1,$2,$3,NOW())
        ON CONFLICT (user_id,blocked_user_id) DO NOTHING
        """,
        request.user_id, request.block_user_id, request.reason
    )
    await execute(
        """
        UPDATE mystery_matches
        SET is_active=FALSE, unmatch_reason='User blocked'
        WHERE ((user1_id=$1 AND user2_id=$2) OR (user1_id=$2 AND user2_id=$1))
          AND is_active=TRUE
        """,
        request.user_id, request.block_user_id
    )
    return {"success": True, "message": "User blocked successfully"}

@mystery_router.post("/unblock")
async def unblock_user(request: BlockRequest):
    await execute(
        "DELETE FROM blocked_users WHERE user_id=$1 AND blocked_user_id=$2",
        request.user_id, request.block_user_id
    )
    return {"success": True, "message": "User unblocked successfully"}

@mystery_router.post("/extend-match")
async def extend_match(request: ExtendMatchRequest):
    match = await fetch_one(
        "SELECT expires_at FROM mystery_matches WHERE id=$1 AND (user1_id=$2 OR user2_id=$2) AND is_active=TRUE",
        request.match_id, request.user_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    is_premium = await async_is_premium_user(request.user_id)
    new_expiry = await fetch_one(
        "UPDATE mystery_matches SET expires_at=expires_at + INTERVAL '24 hours' WHERE id=$1 RETURNING expires_at",
        request.match_id
    )
    return {
        "success": True,
        "message": "Match extended by 24 hours",
        "new_expiry": new_expiry["expires_at"].isoformat() if new_expiry else None,
        "cost": 0 if is_premium else 50,
    }

@mystery_router.post("/request-secret-chat")
async def request_secret_chat(request: SecretChatRequest):
    match = await fetch_one(
        "SELECT user1_id,user2_id FROM mystery_matches WHERE id=$1 AND is_active=TRUE AND (user1_id=$2 OR user2_id=$2)",
        request.match_id, request.requester_id
    )
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    partner_id = match["user2_id"] if match["user1_id"] == request.requester_id else match["user1_id"]
    return {
        "success": True,
        "message": "Secret chat request sent",
        "partner_id": partner_id,
        "duration_minutes": request.duration_minutes,
    }

@mystery_router.post("/accept-secret-chat/{match_id}")
async def accept_secret_chat(match_id: int, user_id: int, duration_minutes: int = 30):
    result = await execute(
        "UPDATE mystery_matches SET secret_chat_active=TRUE WHERE id=$1 AND (user1_id=$2 OR user2_id=$2)",
        match_id, user_id
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Match not found")
    return {
        "success": True,
        "message": "Secret chat activated",
        "duration_minutes": duration_minutes,
        "self_destruct_at": (datetime.utcnow() + timedelta(minutes=duration_minutes)).isoformat(),
    }

@mystery_router.get("/stats/{user_id}")
async def get_user_stats(user_id: int):
    total_row = await fetch_one(
        "SELECT COUNT(*) AS total_matches FROM mystery_matches WHERE user1_id=$1 OR user2_id=$1",
        user_id
    )
    active_row = await fetch_one(
        "SELECT COUNT(*) AS active_matches FROM mystery_matches WHERE (user1_id=$1 OR user2_id=$1) AND is_active=TRUE",
        user_id
    )
    today_count = await async_get_daily_match_count(user_id)
    messages_row = await fetch_one(
        "SELECT COUNT(*) AS messages_sent FROM match_messages WHERE sender_id=$1",
        user_id
    )
    is_premium = await async_is_premium_user(user_id)
    return {
        "success": True,
        "user_id": user_id,
        "is_premium": is_premium,
        "total_matches": total_row.get("total_matches") if total_row else 0,
        "active_matches": active_row.get("active_matches") if active_row else 0,
        "today_matches": today_count,
        "daily_limit": None if is_premium else 3,
        "messages_sent": messages_row.get("messages_sent") if messages_row else 0,
    }

@mystery_router.get("/chat/online-status/{match_id}/{user_id}")
async def check_online_status(match_id: int, user_id: int):
    match = await fetch_one("SELECT user1_id,user2_id FROM mystery_matches WHERE id=$1", match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    other_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
    return {"success": True, "user_id": other_id, "is_online": manager.is_user_online(match_id, other_id)}

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

@mystery_router.websocket("/ws/chat/{match_id}/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, match_id: int, user_id: int):
    await manager.connect(websocket, match_id, user_id)
    try:
        await websocket.send_json({
            "type": "connected",
            "match_id": match_id,
            "user_id": user_id,
            "message": "Connected to Mystery Match chat",
        })
        while True:
            data = await websocket.receive_json()
            await handle_websocket_message(websocket, match_id, user_id, data)
    except WebSocketDisconnect:
        manager.disconnect(match_id, user_id)
        await manager.broadcast_to_match(match_id, {"type": "user_offline", "user_id": user_id})
    except Exception:
        manager.disconnect(match_id, user_id)
        raise
