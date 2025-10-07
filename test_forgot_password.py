#!/usr/bin/env python3
"""
Test script for forgot password functionality
"""
import asyncio
import sys
import os
sys.path.append('/app/backend')

# Set environment variables for testing
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'luvhive_test'
os.environ['JWT_SECRET'] = 'test-secret-key'

async def test_forgot_password():
    """Test the forgot password models and functions"""
    try:
        # Import after setting env vars
        from server import ForgotPasswordRequest, ResetPasswordRequest, create_access_token, get_password_hash
        from datetime import timedelta
        import jwt
        
        print("✅ Successfully imported forgot password models")
        
        # Test ForgotPasswordRequest model
        forgot_request = ForgotPasswordRequest(email="test@example.com")
        print(f"✅ ForgotPasswordRequest created: {forgot_request.email}")
        
        # Test ResetPasswordRequest model
        reset_request = ResetPasswordRequest(token="test-token", new_password="newpassword123")
        print(f"✅ ResetPasswordRequest created with password length: {len(reset_request.new_password)}")
        
        # Test create_access_token with custom expiry
        test_token = create_access_token(
            data={"sub": "test-user-id", "type": "password_reset"},
            expires_delta=timedelta(hours=24)
        )
        print(f"✅ Password reset token created: {test_token[:20]}...")
        
        # Test password hashing
        hashed = get_password_hash("testpassword123")
        print(f"✅ Password hashed successfully: {hashed[:20]}...")
        
        # Test token decoding
        SECRET_KEY = "test-secret-key"
        ALGORITHM = "HS256"
        payload = jwt.decode(test_token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully: {payload}")
        
        print("\n🎉 All forgot password functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_forgot_password())
    sys.exit(0 if result else 1)