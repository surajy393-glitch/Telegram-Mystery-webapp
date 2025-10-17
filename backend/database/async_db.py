"""
Async Database Connection Pool
High-performance async PostgreSQL operations using asyncpg
"""
import asyncpg
import os
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    """Initialize async database connection pool"""
    global _pool
    
    if _pool is not None:
        return _pool
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Build from individual env vars
        database_url = f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:" \
                      f"{os.getenv('POSTGRES_PASSWORD')}@" \
                      f"{os.getenv('POSTGRES_HOST', 'localhost')}:" \
                      f"{os.getenv('POSTGRES_PORT', '5432')}/" \
                      f"{os.getenv('POSTGRES_DB', 'luvhive_bot')}"
    
    try:
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            max_queries=50000,
            max_inactive_connection_lifetime=300
        )
        logger.info("✅ Async database pool initialized")
        return _pool
    except Exception as e:
        logger.error(f"❌ Failed to create database pool: {e}")
        raise


async def close_db_pool():
    """Close database connection pool"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")


async def get_pool() -> asyncpg.Pool:
    """Get database connection pool"""
    if _pool is None:
        await init_db_pool()
    return _pool


# High-level async database operations

async def fetch_one(query: str, *args) -> Optional[Dict[str, Any]]:
    """Execute query and fetch one result"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def fetch_all(query: str, *args) -> List[Dict[str, Any]]:
    """Execute query and fetch all results"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute(query: str, *args) -> str:
    """Execute query without returning results"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.execute(query, *args)


async def fetchval(query: str, *args):
    """Execute query and fetch single value"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchval(query, *args)


# Mystery Match specific async operations

async def async_get_daily_match_count(user_id: int) -> int:
    """Get match count for user today (async)"""
    result = await fetch_one("""
        SELECT COUNT(*) as count FROM mystery_matches
        WHERE (user1_id = $1 OR user2_id = $1)
        AND DATE(created_at) = CURRENT_DATE
    """, user_id)
    return result['count'] if result else 0


async def async_is_premium_user(user_id: int) -> bool:
    """Check if user has active premium (async)"""
    result = await fetch_one("""
        SELECT is_premium, premium_until
        FROM users 
        WHERE tg_user_id = $1
    """, user_id)
    
    if not result:
        return False
    
    if result['is_premium']:
        if result['premium_until']:
            from datetime import datetime
            if result['premium_until'] > datetime.now():
                return True
        else:
            return True
    
    # Fallback: check payments table
    payment = await fetch_one("""
        SELECT * FROM payments 
        WHERE user_id = $1 
        AND status = 'completed'
        AND expires_at > NOW()
        ORDER BY expires_at DESC
        LIMIT 1
    """, user_id)
    
    return payment is not None


async def async_create_match(user1_id: int, user2_id: int) -> int:
    """Create mystery match (async)"""
    match_id = await fetchval("""
        INSERT INTO mystery_matches 
        (user1_id, user2_id, created_at, expires_at, message_count, is_active, user1_unlock_level, user2_unlock_level)
        VALUES ($1, $2, NOW(), NOW() + INTERVAL '48 hours', 0, TRUE, 0, 0)
        RETURNING id
    """, user1_id, user2_id)
    
    return match_id


async def async_get_user_matches(user_id: int) -> List[Dict[str, Any]]:
    """Get all active matches for user (async)"""
    return await fetch_all("""
        SELECT 
            id as match_id,
            CASE 
                WHEN user1_id = $1 THEN user2_id 
                ELSE user1_id 
            END as partner_id,
            message_count,
            created_at,
            expires_at,
            secret_chat_active
        FROM mystery_matches
        WHERE (user1_id = $1 OR user2_id = $1)
        AND is_active = TRUE
        ORDER BY created_at DESC
    """, user_id)
