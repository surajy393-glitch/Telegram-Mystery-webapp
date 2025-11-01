#!/usr/bin/env python3
"""
Debug the user posts endpoint issue
"""

import requests
import json
import sys
import os

# Load environment variables
sys.path.append('/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sql-transition-1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

def test_user_posts_endpoint():
    """Test the user posts endpoint with different approaches"""
    
    # First, login
    login_data = {
        "username": "testuser_2979",
        "password": "TestPass123!"
    }
    
    session = requests.Session()
    response = session.post(f"{API_BASE}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()['access_token']
    user_id = response.json()['user']['id']
    session.headers.update({'Authorization': f'Bearer {token}'})
    
    print(f"✅ Logged in as user ID: {user_id}")
    
    # Test 1: Try with user ID
    print(f"\n🔍 Testing GET /api/users/{user_id}/posts")
    response = session.get(f"{API_BASE}/users/{user_id}/posts")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Success: {len(data.get('posts', []))} posts returned")
    
    # Test 2: Try with username
    username = "testuser_2979"
    print(f"\n🔍 Testing GET /api/users/{username}/posts")
    response = session.get(f"{API_BASE}/users/{username}/posts")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        data = response.json()
        print(f"Success: {len(data.get('posts', []))} posts returned")
    
    # Test 3: Check if posts exist in regular feed
    print(f"\n🔍 Testing GET /api/posts/feed (should include user's posts)")
    response = session.get(f"{API_BASE}/posts/feed")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        posts = data.get('posts', [])
        user_posts = [p for p in posts if p.get('userId') == user_id]
        print(f"Total posts in feed: {len(posts)}")
        print(f"User's posts in feed: {len(user_posts)}")
        if user_posts:
            print(f"User's post IDs: {[p['id'] for p in user_posts]}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_user_posts_endpoint()