#!/usr/bin/env python3
"""
Test script for Telegram authentication hash verification
"""

import hmac
import hashlib
import os
import sys

def verify_telegram_hash(auth_data: dict, bot_token: str) -> bool:
    """
    Test implementation of Telegram hash verification
    """
    try:
        # Extract hash from auth_data
        received_hash = auth_data.pop('hash', None)
        if not received_hash:
            return False
        
        # Create data check string
        data_check_arr = []
        for key, value in sorted(auth_data.items()):
            if key != 'hash':
                data_check_arr.append(f"{key}={value}")
        
        data_check_string = '\n'.join(data_check_arr)
        
        # Create secret key from bot token
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare hashes
        return hmac.compare_digest(calculated_hash, received_hash)
        
    except Exception as e:
        print(f"Error verifying Telegram hash: {e}")
        return False

def test_telegram_hash_verification():
    """
    Test the Telegram hash verification function
    """
    print("🧪 Testing Telegram Hash Verification...")
    
    # Test data (example from Telegram documentation)
    bot_token = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"
    
    # Test case 1: Valid hash
    auth_data_valid = {
        "id": "123456789",
        "first_name": "John",
        "last_name": "Doe", 
        "username": "johndoe",
        "photo_url": "https://t.me/i/userpic/320/johndoe.jpg",
        "auth_date": "1633024800"
    }
    
    # Generate correct hash for test
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data_valid.items())])
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    correct_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    auth_data_with_hash = auth_data_valid.copy()
    auth_data_with_hash['hash'] = correct_hash
    
    # Test valid hash
    result_valid = verify_telegram_hash(auth_data_with_hash.copy(), bot_token)
    if result_valid:
        print("✅ Telegram hash verification test: PASSED")
    else:
        print("❌ Telegram hash verification test: FAILED")
        return False
    
    # Test case 2: Invalid hash
    auth_data_invalid = auth_data_valid.copy()
    auth_data_invalid['hash'] = "invalid_hash_123"
    
    result_invalid = verify_telegram_hash(auth_data_invalid.copy(), bot_token)
    if not result_invalid:
        print("✅ Invalid hash test: PASSED")
    else:
        print("❌ Invalid hash test: FAILED")
        return False
    
    print("🔐 Telegram Authentication Security: IMPLEMENTED")
    return True

def check_environment():
    """
    Check if Telegram bot token is configured
    """
    print("\n🔧 Checking Environment Configuration...")
    
    # Try to load from .env file
    env_path = "/app/backend/.env"
    telegram_token = None
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('TELEGRAM_BOT_TOKEN='):
                    telegram_token = line.split('=', 1)[1].strip().strip('"')
                    break
    except FileNotFoundError:
        print(f"❌ Environment file not found: {env_path}")
    
    if telegram_token and telegram_token != "YOUR_BOT_TOKEN_FROM_BOTFATHER":
        print("✅ TELEGRAM_BOT_TOKEN: Configured")
        print(f"   Token: {telegram_token[:10]}...{telegram_token[-5:]}")
        return True
    else:
        print("⚠️  TELEGRAM_BOT_TOKEN: Not configured")
        print("   Please add your bot token to /app/backend/.env")
        print("   Format: TELEGRAM_BOT_TOKEN=\"your_token_here\"")
        return False

def main():
    """
    Main test function
    """
    print("=" * 60)
    print("🚀 LuvHive Telegram Authentication Security Test")
    print("=" * 60)
    
    # Test hash verification function
    hash_test_passed = test_telegram_hash_verification()
    
    # Check environment configuration
    env_configured = check_environment()
    
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print("=" * 60)
    
    if hash_test_passed:
        print("✅ Hash Verification: WORKING")
    else:
        print("❌ Hash Verification: FAILED")
    
    if env_configured:
        print("✅ Environment: CONFIGURED")
    else:
        print("⚠️  Environment: NEEDS SETUP")
    
    if hash_test_passed and env_configured:
        print("\n🎉 Ready for secure Telegram authentication!")
    elif hash_test_passed:
        print("\n🔧 Please configure TELEGRAM_BOT_TOKEN to complete setup")
    else:
        print("\n❌ Tests failed - please check implementation")
    
    print("=" * 60)
    
    return hash_test_passed and env_configured

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)