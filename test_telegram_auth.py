#!/usr/bin/env python3
"""
Test script for Telegram authentication hash verification
"""
import hashlib
import hmac

def verify_telegram_hash(auth_data: dict, bot_token: str) -> bool:
    """
    Verify Telegram Login Widget hash for security
    https://core.telegram.org/widgets/login#checking-authorization
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
    """Test the Telegram hash verification function"""
    
    # Test bot token (example)
    bot_token = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
    
    # Sample Telegram auth data (this would come from Telegram Login Widget)
    auth_data = {
        "id": "12345678",
        "first_name": "John",
        "last_name": "Doe", 
        "username": "johndoe",
        "photo_url": "https://t.me/i/userpic/320/johndoe.jpg",
        "auth_date": "1633024800"
    }
    
    # Create the expected hash manually for testing
    data_check_arr = []
    for key, value in sorted(auth_data.items()):
        data_check_arr.append(f"{key}={value}")
    
    data_check_string = '\n'.join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    expected_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Add the hash to auth_data
    auth_data_with_hash = auth_data.copy()
    auth_data_with_hash['hash'] = expected_hash
    
    # Test verification
    result = verify_telegram_hash(auth_data_with_hash.copy(), bot_token)
    
    print(f"✅ Telegram hash verification test: {'PASSED' if result else 'FAILED'}")
    print(f"   Expected hash: {expected_hash}")
    print(f"   Verification result: {result}")
    
    # Test with invalid hash
    invalid_auth_data = auth_data.copy()
    invalid_auth_data['hash'] = "invalid_hash"
    
    invalid_result = verify_telegram_hash(invalid_auth_data, bot_token)
    print(f"✅ Invalid hash test: {'PASSED' if not invalid_result else 'FAILED'}")
    print(f"   Invalid hash verification result: {invalid_result}")
    
    return result and not invalid_result

if __name__ == "__main__":
    success = test_telegram_hash_verification()
    print(f"\n🔐 Telegram Authentication Security: {'IMPLEMENTED' if success else 'FAILED'}")