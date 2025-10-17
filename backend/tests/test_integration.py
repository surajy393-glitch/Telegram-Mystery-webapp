"""
Integration Tests for All Improvements
Tests moderation, inclusivity, reporting, and security
"""
import pytest
import asyncio
import sys
import os

sys.path.insert(0, '/app/backend')

from utils.moderation import moderate_content, check_profanity, check_spam
from utils.file_security import generate_secure_filename, validate_image_file, sanitize_path
from utils.inclusivity import calculate_compatibility_score, Gender, get_compatible_genders


class TestModerationIntegration:
    """Test content moderation is working"""
    
    def test_profanity_blocked(self):
        """Profanity should be detected"""
        result = moderate_content("fuck you")
        assert not result.is_safe
        assert "profanity" in result.reason.lower()
    
    def test_spam_urls_blocked(self):
        """URLs should be flagged"""
        result = moderate_content("Check out https://spam.com")
        assert not result.is_safe
        assert "url" in result.reason.lower()
    
    def test_phone_numbers_blocked(self):
        """Phone numbers should be flagged"""
        result = moderate_content("Call me at 9876543210")
        assert not result.is_safe
    
    def test_clean_message_passes(self):
        """Clean messages should pass"""
        result = moderate_content("Hello, how are you today?")
        assert result.is_safe
    
    def test_harassment_detection(self):
        """Harassment patterns detected"""
        result = moderate_content("I hate you so much")
        assert not result.is_safe


class TestFileSecurityIntegration:
    """Test file upload security"""
    
    def test_filename_randomization(self):
        """Filenames must be randomized"""
        fn1 = generate_secure_filename("photo.jpg", "user123")
        fn2 = generate_secure_filename("photo.jpg", "user123")
        
        assert fn1 != fn2
        assert "user123" in fn1
        assert fn1.endswith('.jpg')
    
    def test_malicious_extensions_rejected(self):
        """Malicious files rejected"""
        with pytest.raises(ValueError):
            generate_secure_filename("virus.exe", "user123")
        
        with pytest.raises(ValueError):
            generate_secure_filename("script.php", "user123")
    
    def test_directory_traversal_blocked(self):
        """Path traversal attacks blocked"""
        with pytest.raises(ValueError):
            sanitize_path("../../etc/passwd", "/app/uploads")
    
    def test_jpeg_validation(self):
        """Valid JPEG accepted"""
        jpeg_magic = b'\xff\xd8\xff\xe0' + b'\x00' * 500
        is_valid, error = validate_image_file(jpeg_magic, "test.jpg")
        assert is_valid
        assert error is None
    
    def test_fake_image_rejected(self):
        """Fake images rejected"""
        fake_data = b'This is not an image'
        is_valid, error = validate_image_file(fake_data, "fake.jpg")
        assert not is_valid
        assert error is not None


class TestInclusivityIntegration:
    """Test inclusive matching"""
    
    def test_binary_match_compatibility(self):
        """Binary gender matching works"""
        score = calculate_compatibility_score(
            "male", "straight", "women", 25, ["sports", "movies"],
            "female", "straight", "men", 26, ["movies", "travel"],
        )
        assert score > 0.5
    
    def test_non_binary_compatibility(self):
        """Non-binary matching works"""
        score = calculate_compatibility_score(
            "non_binary", "pansexual", "everyone", 24, ["art", "music"],
            "genderfluid", "queer", "everyone", 25, ["art", "music"],
        )
        assert score > 0.6
    
    def test_compatible_genders_everyone(self):
        """Everyone preference includes all"""
        compatible = get_compatible_genders("male", "bi", "everyone")
        assert len(compatible) >= 7
    
    def test_compatible_genders_specific(self):
        """Specific preferences work"""
        compatible = get_compatible_genders("male", "straight", "women")
        assert Gender.FEMALE in compatible
        assert len(compatible) == 1


class TestFantasyInclusivity:
    """Test fantasy match inclusivity"""
    
    def test_normalize_gender_male(self):
        """Male normalization"""
        sys.path.insert(0, '/app/telegram_bot/handlers')
        from fantasy_match import normalize_gender
        
        assert normalize_gender("male") == "male"
        assert normalize_gender("m") == "male"
        assert normalize_gender("boy") == "male"
    
    def test_normalize_gender_non_binary(self):
        """Non-binary normalization"""
        sys.path.insert(0, '/app/telegram_bot/handlers')
        from fantasy_match import normalize_gender
        
        assert normalize_gender("non-binary") == "non_binary"
        assert normalize_gender("nb") == "non_binary"
        assert normalize_gender("enby") == "non_binary"
    
    def test_normalize_gender_genderqueer(self):
        """Other identities normalized"""
        sys.path.insert(0, '/app/telegram_bot/handlers')
        from fantasy_match import normalize_gender
        
        assert normalize_gender("genderqueer") == "genderqueer"
        assert normalize_gender("genderfluid") == "genderfluid"
        assert normalize_gender("agender") == "agender"


class TestEndpointIntegration:
    """Test API endpoints work"""
    
    def test_report_endpoint_exists(self):
        """Report endpoint exists"""
        from mystery_match import mystery_router
        routes = [r.path for r in mystery_router.routes]
        assert any('/report' in r for r in routes)
    
    def test_send_message_has_moderation(self):
        """Send message uses moderation"""
        import inspect
        from mystery_match import send_message
        
        source = inspect.getsource(send_message)
        assert 'moderate_content' in source
        assert 'moderation_result' in source


# Summary test
def test_all_improvements_present():
    """Verify all improvement files exist"""
    required_files = [
        '/app/backend/utils/moderation.py',
        '/app/backend/utils/file_security.py',
        '/app/backend/utils/inclusivity.py',
        '/app/backend/utils/feature_flags.py',
        '/app/backend/database/async_db.py',
        '/app/backend/alembic.ini',
        '/app/backend/migrations/versions/001_initial_schema.py',
        '/app/backend/migrations/versions/002_fantasy_tables.py',
    ]
    
    for file_path in required_files:
        assert os.path.exists(file_path), f"Missing: {file_path}"
    
    print("✅ All improvement files present!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
