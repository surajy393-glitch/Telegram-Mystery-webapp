"""
PostgreSQL Database Helper for LuvHive Backend
Replaces MongoDB with PostgreSQL
"""
import asyncpg
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# Database connection pool
_pool: Optional[asyncpg.Pool] = None

async def get_pool() -> asyncpg.Pool:
    """Get or create database connection pool"""
    global _pool
    if _pool is None:
        database_url = os.getenv("DATABASE_URL")
        _pool = await asyncpg.create_pool(database_url, min_size=10, max_size=20)
    return _pool

async def close_pool():
    """Close database connection pool"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

# User queries
async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM webapp_users WHERE id = $1", user_id)
    return dict(row) if row else None

async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username (case-insensitive)"""
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM webapp_users WHERE LOWER(username) = LOWER($1)", username)
    return dict(row) if row else None

async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM webapp_users WHERE email = $1", email)
    return dict(row) if row else None

async def get_user_by_telegram_id(telegram_id: int) -> Optional[Dict[str, Any]]:
    """Get user by Telegram ID"""
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM webapp_users WHERE telegram_id = $1", telegram_id)
    return dict(row) if row else None

async def create_user(user_data: Dict[str, Any]) -> int:
    """Create new user and return ID"""
    pool = await get_pool()
    
    # Convert lists/dicts to JSON strings
    if 'interests' in user_data and isinstance(user_data['interests'], list):
        user_data['interests'] = json.dumps(user_data['interests'])
    
    query = """
        INSERT INTO webapp_users (
            full_name, username, email, mobile_number, password,
            age, gender, city, interests, bio, profile_photo_url,
            is_private, is_verified, email_verified, mobile_verified,
            telegram_id, country, auth_method, violations_count
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
        RETURNING id
    """
    
    user_id = await pool.fetchval(
        query,
        user_data.get('fullName'),
        user_data.get('username'),
        user_data.get('email'),
        user_data.get('mobileNumber'),
        user_data.get('password_hash'),
        user_data.get('age'),
        user_data.get('gender'),
        user_data.get('city'),
        user_data.get('interests', '[]'),
        user_data.get('bio', ''),
        user_data.get('profileImage'),
        user_data.get('isPrivate', False),
        user_data.get('isVerified', False),
        user_data.get('emailVerified', True),
        user_data.get('phoneVerified', False),
        user_data.get('telegramId'),
        user_data.get('country'),
        user_data.get('authMethod', 'password'),
        user_data.get('violationsCount', 0)
    )
    
    return user_id

async def update_user(user_id: int, updates: Dict[str, Any]):
    """Update user fields"""
    pool = await get_pool()
    
    # Build dynamic UPDATE query
    set_clauses = []
    values = []
    param_num = 1
    
    for key, value in updates.items():
        # Convert camelCase to snake_case
        db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
        set_clauses.append(f"{db_key} = ${param_num}")
        
        # Convert lists/dicts to JSON
        if isinstance(value, (list, dict)):
            value = json.dumps(value)
        
        values.append(value)
        param_num += 1
    
    values.append(user_id)
    query = f"UPDATE webapp_users SET {', '.join(set_clauses)} WHERE id = ${param_num}"
    
    await pool.execute(query, *values)

# Post queries
async def create_post(user_id: int, caption: str, media: List) -> int:
    """Create new post"""
    pool = await get_pool()
    post_id = await pool.fetchval(
        """INSERT INTO webapp_posts (user_id, caption, media) 
           VALUES ($1, $2, $3) RETURNING id""",
        user_id, caption, json.dumps(media)
    )
    return post_id

async def get_post_by_id(post_id: int) -> Optional[Dict]:
    """Get post by ID"""
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM webapp_posts WHERE id = $1 AND is_deleted = FALSE", post_id)
    return dict(row) if row else None

async def get_user_posts(user_id: int, limit: int = 50) -> List[Dict]:
    """Get user's posts"""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT * FROM webapp_posts 
           WHERE user_id = $1 AND is_deleted = FALSE 
           ORDER BY created_at DESC LIMIT $2""",
        user_id, limit
    )
    return [dict(row) for row in rows]

async def delete_post(post_id: int):
    """Soft delete post"""
    pool = await get_pool()
    await pool.execute("UPDATE webapp_posts SET is_deleted = TRUE WHERE id = $1", post_id)

# Follow queries
async def follow_user(follower_id: int, following_id: int, status: str = 'accepted'):
    """Create follow relationship"""
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO webapp_follows (follower_id, following_id, status)
           VALUES ($1, $2, $3)
           ON CONFLICT (follower_id, following_id) DO UPDATE SET status = $3""",
        follower_id, following_id, status
    )

async def unfollow_user(follower_id: int, following_id: int):
    """Remove follow relationship"""
    pool = await get_pool()
    await pool.execute(
        "DELETE FROM webapp_follows WHERE follower_id = $1 AND following_id = $2",
        follower_id, following_id
    )

async def is_following(follower_id: int, following_id: int) -> bool:
    """Check if user is following another user"""
    pool = await get_pool()
    result = await pool.fetchval(
        "SELECT 1 FROM webapp_follows WHERE follower_id = $1 AND following_id = $2 AND status = 'accepted'",
        follower_id, following_id
    )
    return result is not None

async def get_followers(user_id: int) -> List[int]:
    """Get list of follower IDs"""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT follower_id FROM webapp_follows WHERE following_id = $1 AND status = 'accepted'",
        user_id
    )
    return [row['follower_id'] for row in rows]

async def get_following(user_id: int) -> List[int]:
    """Get list of following IDs"""
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT following_id FROM webapp_follows WHERE follower_id = $1 AND status = 'accepted'",
        user_id
    )
    return [row['following_id'] for row in rows]

# Notification queries
async def create_notification(user_id: int, notif_type: str, from_user_id: int, 
                              from_username: str, message: str, post_id: Optional[int] = None):
    """Create notification"""
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO webapp_notifications 
           (user_id, type, from_user_id, from_username, message, post_id)
           VALUES ($1, $2, $3, $4, $5, $6)""",
        user_id, notif_type, from_user_id, from_username, message, post_id
    )

async def get_user_notifications(user_id: int, limit: int = 50) -> List[Dict]:
    """Get user notifications"""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT * FROM webapp_notifications 
           WHERE user_id = $1 
           ORDER BY created_at DESC LIMIT $2""",
        user_id, limit
    )
    return [dict(row) for row in rows]
