"""
Centralized Feature Flags System
Manage feature toggles from database
"""
from typing import Optional, Dict
import asyncpg
from database.async_db import get_pool
import logging

logger = logging.getLogger(__name__)

# In-memory cache for performance
_flag_cache: Dict[str, bool] = {}


async def init_feature_flags():
    """Initialize feature flags table with default flags"""
    pool = await get_pool()
    
    default_flags = [
        ('fantasy_notifications', False, 'Enable fantasy match notifications'),
        ('confession_roulette', True, 'Enable confession roulette feature'),
        ('naughty_wyr', True, 'Enable naughty would-you-rather'),
        ('dare_challenges', True, 'Enable dare challenges'),
        ('vault_premium', False, 'Enable vault premium feature'),
        ('mystery_match', True, 'Enable mystery match dating'),
        ('gender_filtering', True, 'Allow premium users to filter by gender'),
        ('ai_moderation', False, 'Enable AI-powered content moderation'),
        ('multi_language', False, 'Enable multi-language support'),
    ]
    
    async with pool.acquire() as conn:
        for flag_name, enabled, description in default_flags:
            try:
                await conn.execute("""
                    INSERT INTO feature_flags (flag_name, enabled, description)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (flag_name) DO NOTHING
                """, flag_name, enabled, description)
            except Exception as e:
                logger.error(f"Failed to init flag {flag_name}: {e}")
    
    logger.info("✅ Feature flags initialized")


async def is_feature_enabled(flag_name: str, use_cache: bool = True) -> bool:
    """
    Check if a feature is enabled
    
    Args:
        flag_name: Name of the feature flag
        use_cache: Use in-memory cache for performance
        
    Returns:
        True if enabled, False otherwise
    """
    # Check cache first
    if use_cache and flag_name in _flag_cache:
        return _flag_cache[flag_name]
    
    # Query database
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.fetchrow("""
            SELECT enabled FROM feature_flags
            WHERE flag_name = $1
        """, flag_name)
        
        enabled = result['enabled'] if result else False
        
        # Update cache
        _flag_cache[flag_name] = enabled
        
        return enabled


async def set_feature_flag(flag_name: str, enabled: bool, updated_by: str = "admin"):
    """
    Enable or disable a feature flag
    
    Args:
        flag_name: Name of the feature flag
        enabled: New state
        updated_by: Who made the change
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE feature_flags
            SET enabled = $1, updated_at = NOW(), updated_by = $2
            WHERE flag_name = $3
        """, enabled, updated_by, flag_name)
    
    # Update cache
    _flag_cache[flag_name] = enabled
    
    logger.info(f"Feature flag '{flag_name}' set to {enabled} by {updated_by}")


async def get_all_flags() -> Dict[str, bool]:
    """Get all feature flags"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT flag_name, enabled, description
            FROM feature_flags
            ORDER BY flag_name
        """)
        
        return {
            row['flag_name']: {
                'enabled': row['enabled'],
                'description': row['description']
            }
            for row in rows
        }


def clear_flag_cache():
    """Clear feature flag cache"""
    global _flag_cache
    _flag_cache = {}
    logger.info("Feature flag cache cleared")


# Convenience decorators
def feature_required(flag_name: str):
    """Decorator to require a feature flag"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not await is_feature_enabled(flag_name):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403, 
                    detail=f"Feature '{flag_name}' is not enabled"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
