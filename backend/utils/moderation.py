"""
Content Moderation & Safety Tools
Profanity detection, content filtering, and reporting
"""
from typing import Optional, Tuple
import re
from better_profanity import profanity
import logging

logger = logging.getLogger(__name__)

# Initialize profanity filter
profanity.load_censor_words()

# Custom bad words for Indian context
CUSTOM_BAD_WORDS = [
    # Add context-specific words
]

for word in CUSTOM_BAD_WORDS:
    profanity.add_censor_words([word])


class ContentModerationResult:
    """Result of content moderation check"""
    def __init__(self, is_safe: bool, reason: Optional[str] = None, confidence: float = 1.0):
        self.is_safe = is_safe
        self.reason = reason
        self.confidence = confidence


def check_profanity(text: str) -> ContentModerationResult:
    """
    Check text for profanity
    
    Args:
        text: Text to check
        
    Returns:
        ContentModerationResult
    """
    if profanity.contains_profanity(text):
        censored = profanity.censor(text)
        return ContentModerationResult(
            is_safe=False,
            reason=f"Contains profanity: {censored}",
            confidence=0.9
        )
    
    return ContentModerationResult(is_safe=True)


def check_spam(text: str) -> ContentModerationResult:
    """
    Check for spam patterns
    
    Args:
        text: Text to check
        
    Returns:
        ContentModerationResult
    """
    # Check for excessive caps
    if text.isupper() and len(text) > 20:
        return ContentModerationResult(
            is_safe=False,
            reason="Excessive caps (potential spam)",
            confidence=0.7
        )
    
    # Check for repeated characters
    if re.search(r'(.)\1{5,}', text):
        return ContentModerationResult(
            is_safe=False,
            reason="Excessive character repetition",
            confidence=0.8
        )
    
    # Check for phone numbers
    if re.search(r'\b\d{10}\b', text):
        return ContentModerationResult(
            is_safe=False,
            reason="Contains phone number",
            confidence=0.9
        )
    
    # Check for URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.search(url_pattern, text, re.IGNORECASE):
        return ContentModerationResult(
            is_safe=False,
            reason="Contains URL",
            confidence=0.9
        )
    
    return ContentModerationResult(is_safe=True)


def check_harassment(text: str) -> ContentModerationResult:
    """
    Check for harassment patterns
    
    Args:
        text: Text to check
        
    Returns:
        ContentModerationResult
    """
    harassment_patterns = [
        r'\bkill\s+yourself\b',
        r'\bdie\b',
        r'\bhate\s+you\b',
        r'\bugly\b',
        r'\bfat\b.*\bloser\b',
    ]
    
    text_lower = text.lower()
    for pattern in harassment_patterns:
        if re.search(pattern, text_lower):
            return ContentModerationResult(
                is_safe=False,
                reason="Potential harassment detected",
                confidence=0.85
            )
    
    return ContentModerationResult(is_safe=True)


def moderate_content(text: str) -> ContentModerationResult:
    """
    Run all moderation checks
    
    Args:
        text: Text to moderate
        
    Returns:
        ContentModerationResult
    """
    # Run all checks
    checks = [
        check_profanity(text),
        check_spam(text),
        check_harassment(text),
    ]
    
    # Return first failure
    for result in checks:
        if not result.is_safe:
            return result
    
    return ContentModerationResult(is_safe=True)


# Reporting utilities
from database.async_db import execute, fetch_one

async def create_report(
    reporter_id: int,
    reported_user_id: int,
    content_type: str,
    content_id: str,
    reason: str
) -> int:
    """
    Create a content report
    
    Args:
        reporter_id: User filing the report
        reported_user_id: User being reported
        content_type: Type of content ('message', 'profile', 'photo')
        content_id: ID of the content
        reason: Reason for report
        
    Returns:
        Report ID
    """
    result = await fetch_one("""
        INSERT INTO content_reports 
        (reporter_id, reported_user_id, content_type, content_id, reason, status, created_at)
        VALUES ($1, $2, $3, $4, $5, 'pending', NOW())
        RETURNING id
    """, reporter_id, reported_user_id, content_type, content_id, reason)
    
    logger.info(f"Report created: {result['id']} by user {reporter_id}")
    return result['id']


async def auto_ban_user(user_id: int, reason: str, duration_hours: int = 24):
    """
    Automatically ban a user
    
    Args:
        user_id: User to ban
        reason: Reason for ban
        duration_hours: Ban duration in hours
    """
    await execute("""
        UPDATE users
        SET is_banned = TRUE,
            ban_reason = $2,
            ban_until = NOW() + INTERVAL '%s hours',
            updated_at = NOW()
        WHERE tg_user_id = $1
    """ % duration_hours, user_id, reason)
    
    logger.warning(f"User {user_id} auto-banned for {duration_hours}h: {reason}")


async def get_user_report_count(user_id: int, days: int = 7) -> int:
    """Get number of reports against a user in recent days"""
    result = await fetch_one("""
        SELECT COUNT(*) as count FROM content_reports
        WHERE reported_user_id = $1
        AND created_at > NOW() - INTERVAL '%s days'
    """ % days, user_id)
    
    return result['count'] if result else 0


async def check_auto_ban_threshold(user_id: int):
    """
    Check if user should be auto-banned based on reports
    Auto-ban if 3+ reports in last 7 days
    """
    report_count = await get_user_report_count(user_id)
    
    if report_count >= 3:
        await auto_ban_user(
            user_id,
            f"Automatic ban: {report_count} reports in 7 days",
            duration_hours=48
        )
        return True
    
    return False
