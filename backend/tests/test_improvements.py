"""
Comprehensive Test Suite for Mystery Match
Tests for API endpoints, WebSocket, security utilities
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from server import app
from database.async_db import init_db_pool, close_db_pool
from utils.file_security import (
    generate_secure_filename,
    validate_image_file,
    sanitize_path
)
from utils.moderation import moderate_content, check_profanity
from utils.inclusivity import calculate_compatibility_score, Gender, Orientation


# Fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    """Create async HTTP client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Setup database pool"""
    await init_db_pool()
    yield
    await close_db_pool()


# Security Tests
class TestFileSecurity:
    """Test file upload security"""
    
    def test_secure_filename_generation(self):
        """Test secure filename is randomized"""
        filename1 = generate_secure_filename("malicious..\\..\\file.jpg", "user123")
        filename2 = generate_secure_filename("malicious..\\..\\file.jpg", "user123")
        
        # Should be different each time
        assert filename1 != filename2
        
        # Should preserve extension
        assert filename1.endswith('.jpg')
        
        # Should include user ID
        assert 'user123' in filename1
    
    def test_invalid_extension_rejected(self):
        """Test invalid extensions are rejected"""
        with pytest.raises(ValueError):
            generate_secure_filename("malicious.exe", "user123")
        
        with pytest.raises(ValueError):
            generate_secure_filename("script.php", "user123")
    
    def test_image_validation(self):
        """Test image file validation"""
        # Valid JPEG magic bytes
        jpeg_bytes = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        is_valid, error = validate_image_file(jpeg_bytes, "test.jpg")
        assert is_valid
        assert error is None
        
        # Invalid magic bytes
        fake_bytes = b'fake image data'
        is_valid, error = validate_image_file(fake_bytes, "test.jpg")
        assert not is_valid
        assert error is not None
    
    def test_directory_traversal_prevention(self):
        """Test path traversal attacks are blocked"""
        with pytest.raises(ValueError):
            sanitize_path("../../etc/passwd", "/app/uploads")
        
        with pytest.raises(ValueError):
            sanitize_path("..\\..\\windows\\system32", "/app/uploads")


# Moderation Tests
class TestModeration:
    """Test content moderation"""
    
    def test_profanity_detection(self):
        """Test profanity is detected"""
        result = check_profanity("This is a damn test")
        assert not result.is_safe
        
        result = check_profanity("This is a clean message")
        assert result.is_safe
    
    def test_spam_detection(self):
        """Test spam patterns are detected"""
        result = moderate_content("CLICK HERE NOW!!!! 9876543210")
        assert not result.is_safe
        
        result = moderate_content("Normal message")
        assert result.is_safe
    
    def test_url_detection(self):
        """Test URLs are flagged"""
        result = moderate_content("Visit https://scam.com now")
        assert not result.is_safe


# Inclusivity Tests
class TestInclusivity:
    """Test inclusive matching"""
    
    def test_compatibility_calculation(self):
        """Test compatibility score calculation"""
        score = calculate_compatibility_score(
            user1_gender="male",
            user1_orientation="straight",
            user1_preferences="women",
            user1_age=25,
            user1_interests=["music", "movies", "travel"],
            user2_gender="female",
            user2_orientation="straight",
            user2_preferences="men",
            user2_age=26,
            user2_interests=["music", "travel", "reading"]
        )
        
        # Should have high compatibility
        assert score > 0.6
    
    def test_non_binary_compatibility(self):
        """Test non-binary matching works"""
        score = calculate_compatibility_score(
            user1_gender="non_binary",
            user1_orientation="pansexual",
            user1_preferences="everyone",
            user1_age=24,
            user1_interests=["art", "music"],
            user2_gender="genderfluid",
            user2_orientation="queer",
            user2_preferences="everyone",
            user2_age=25,
            user2_interests=["art", "poetry"]
        )
        
        # Should have compatibility
        assert score > 0.4


# API Tests
class TestMysteryMatchAPI:
    """Test Mystery Match endpoints"""
    
    @pytest.mark.asyncio
    async def test_find_match_requires_auth(self, async_client):
        """Test find-match requires authentication"""
        response = await async_client.post("/api/mystery/find-match", json={
            "user_id": 123456
        })
        
        # Should fail without proper auth
        assert response.status_code in [401, 403, 404]
    
    @pytest.mark.asyncio
    async def test_send_message_validation(self, async_client):
        """Test message sending validates input"""
        response = await async_client.post("/api/mystery/send-message", json={
            "match_id": 999,
            "sender_id": 123,
            "message_text": ""  # Empty message
        })
        
        # Should reject empty messages
        assert response.status_code >= 400


# WebSocket Tests
class TestWebSocket:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection endpoint exists"""
        from server import app
        
        # Check route exists
        routes = [route.path for route in app.routes]
        assert any('/ws/chat' in route for route in routes)


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
