#!/usr/bin/env python3
"""
Test forgot password endpoints via HTTP
"""
import requests
import json

def test_forgot_password_endpoint():
    """Test the forgot password endpoint"""
    base_url = "http://localhost:8000/api"
    
    # Test 1: Empty email
    print("🧪 Testing forgot password with empty email...")
    response = requests.post(f"{base_url}/auth/forgot-password", 
                           json={"email": ""})
    
    if response.status_code == 400:
        print("✅ Correctly rejected empty email")
    else:
        print(f"❌ Expected 400, got {response.status_code}")
    
    # Test 2: Valid email format (non-existent user)
    print("🧪 Testing forgot password with non-existent email...")
    response = requests.post(f"{base_url}/auth/forgot-password", 
                           json={"email": "test@example.com"})
    
    if response.status_code == 200:
        data = response.json()
        if "reset link has been sent" in data.get("message", ""):
            print("✅ Correctly handled non-existent email")
        else:
            print(f"❌ Unexpected response: {data}")
    else:
        print(f"❌ Expected 200, got {response.status_code}: {response.text}")
    
    # Test 3: Reset password with invalid token
    print("🧪 Testing reset password with invalid token...")
    response = requests.post(f"{base_url}/auth/reset-password", 
                           json={"token": "invalid-token", "new_password": "newpass123"})
    
    if response.status_code == 400:
        print("✅ Correctly rejected invalid token")
    else:
        print(f"❌ Expected 400, got {response.status_code}")

if __name__ == "__main__":
    try:
        test_forgot_password_endpoint()
        print("\n🎉 HTTP endpoint tests completed!")
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running - skipping HTTP tests")
    except Exception as e:
        print(f"❌ Test failed: {e}")