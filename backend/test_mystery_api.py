"""
Test script for Mystery Match API
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_api():
    print("🧪 Testing Mystery Match API\n")
    print("="*50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✅ Health check passed")
        print(f"   Database: {response.json().get('database')}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test 2: Find mystery match (free user)
    print("\n2️⃣ Testing Find Mystery Match (Free User)...")
    test_user_id = 99999999  # Test user
    
    payload = {
        "user_id": test_user_id,
        "preferred_age_min": 18,
        "preferred_age_max": 35
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/mystery/find-match",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Find match endpoint working")
            print(f"   Success: {data.get('success')}")
            if data.get('success'):
                print(f"   Match ID: {data.get('match_id')}")
                print(f"   Mystery User: {data.get('mystery_user')}")
                match_id = data.get('match_id')
            else:
                print(f"   Message: {data.get('message')}")
        else:
            print(f"❌ Find match failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get my matches
    print("\n3️⃣ Testing Get My Matches...")
    try:
        response = requests.get(f"{BASE_URL}/api/mystery/my-matches/{test_user_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Get matches endpoint working")
            print(f"   Total matches: {data.get('total')}")
            print(f"   Is premium: {data.get('is_premium')}")
            print(f"   Daily limit: {data.get('daily_limit')}")
        else:
            print(f"❌ Get matches failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get user stats
    print("\n4️⃣ Testing Get User Stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/mystery/stats/{test_user_id}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats endpoint working")
            print(f"   Total matches: {data.get('total_matches')}")
            print(f"   Active matches: {data.get('active_matches')}")
            print(f"   Today's matches: {data.get('today_matches')}")
            print(f"   Messages sent: {data.get('messages_sent')}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("🎉 API Tests Complete!\n")

if __name__ == "__main__":
    test_api()
