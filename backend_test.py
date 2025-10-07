#!/usr/bin/env python3
"""
Backend API Testing for LuvHive Enhanced Features
Tests the newly implemented endpoints for user profiles, AI compatibility, blocking, and story hiding
"""

import requests
import json
import sys
import os
from datetime import datetime

# Load environment variables
sys.path.append('/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/frontend/.env')

# Get backend URL from frontend env
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://social-connect-264.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class LuvHiveAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.current_user_id = None
        self.test_user_id = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message="", error_details=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if error_details:
            print(f"   Error: {error_details}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append({
                'test': test_name,
                'message': message,
                'error': error_details
            })
        print()
    
    def register_test_user(self):
        """Register a test user for authentication"""
        try:
            user_data = {
                "fullName": "Emma Rodriguez",
                "username": f"emma_test_{datetime.now().strftime('%H%M%S')}",
                "age": 25,
                "gender": "female",
                "password": "SecurePass123!"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data['access_token']
                self.current_user_id = data['user']['id']
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                self.log_result("User Registration", True, f"Registered user: {user_data['username']}")
                return True
            else:
                self.log_result("User Registration", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("User Registration", False, "Exception occurred", str(e))
            return False
    
    def register_second_user(self):
        """Register a second user for testing interactions"""
        try:
            user_data = {
                "fullName": "Alex Johnson",
                "username": f"alex_test_{datetime.now().strftime('%H%M%S')}",
                "age": 28,
                "gender": "male",
                "password": "SecurePass456!"
            }
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                self.test_user_id = data['user']['id']
                self.log_result("Second User Registration", True, f"Registered user: {user_data['username']}")
                return True
            else:
                self.log_result("Second User Registration", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_result("Second User Registration", False, "Exception occurred", str(e))
            return False
    
    def test_get_user_profile(self):
        """Test GET /api/users/{userId}/profile endpoint"""
        if not self.test_user_id:
            self.log_result("Get User Profile", False, "No test user ID available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.test_user_id}/profile")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'username', 'fullName', 'age', 'gender', 'followersCount', 'followingCount']
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_result("Get User Profile", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Get User Profile", True, f"Retrieved profile for user: {data['username']}")
            else:
                self.log_result("Get User Profile", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get User Profile", False, "Exception occurred", str(e))
    
    def test_get_user_profile_invalid_id(self):
        """Test GET /api/users/{userId}/profile with invalid user ID"""
        try:
            invalid_id = "invalid-user-id-12345"
            response = self.session.get(f"{API_BASE}/users/{invalid_id}/profile")
            
            if response.status_code == 404:
                self.log_result("Get User Profile (Invalid ID)", True, "Correctly returned 404 for invalid user ID")
            else:
                self.log_result("Get User Profile (Invalid ID)", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Get User Profile (Invalid ID)", False, "Exception occurred", str(e))
    
    def test_get_user_posts(self):
        """Test GET /api/users/{userId}/posts endpoint"""
        if not self.test_user_id:
            self.log_result("Get User Posts", False, "No test user ID available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/users/{self.test_user_id}/posts")
            
            if response.status_code == 200:
                data = response.json()
                if 'posts' in data and isinstance(data['posts'], list):
                    self.log_result("Get User Posts", True, f"Retrieved {len(data['posts'])} posts")
                else:
                    self.log_result("Get User Posts", False, "Response missing 'posts' array")
            else:
                self.log_result("Get User Posts", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get User Posts", False, "Exception occurred", str(e))
    
    def test_ai_vibe_compatibility(self):
        """Test POST /api/ai/vibe-compatibility endpoint"""
        if not self.test_user_id:
            self.log_result("AI Vibe Compatibility", False, "No test user ID available")
            return
        
        try:
            request_data = {
                "targetUserId": self.test_user_id
            }
            
            response = self.session.post(f"{API_BASE}/ai/vibe-compatibility", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'compatibility' in data and 'analysis' in data:
                    compatibility_score = data['compatibility']
                    if isinstance(compatibility_score, int) and 0 <= compatibility_score <= 100:
                        self.log_result("AI Vibe Compatibility", True, 
                                      f"Compatibility: {compatibility_score}%, Analysis: {data['analysis'][:50]}...")
                    else:
                        self.log_result("AI Vibe Compatibility", False, 
                                      f"Invalid compatibility score: {compatibility_score}")
                else:
                    self.log_result("AI Vibe Compatibility", False, "Missing compatibility or analysis fields")
            else:
                self.log_result("AI Vibe Compatibility", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("AI Vibe Compatibility", False, "Exception occurred", str(e))
    
    def test_ai_vibe_compatibility_missing_target(self):
        """Test POST /api/ai/vibe-compatibility without target user ID"""
        try:
            request_data = {}  # Missing targetUserId
            
            response = self.session.post(f"{API_BASE}/ai/vibe-compatibility", json=request_data)
            
            if response.status_code == 400:
                self.log_result("AI Vibe Compatibility (Missing Target)", True, 
                              "Correctly returned 400 for missing target user ID")
            else:
                self.log_result("AI Vibe Compatibility (Missing Target)", False, 
                              f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("AI Vibe Compatibility (Missing Target)", False, "Exception occurred", str(e))
    
    def test_block_user(self):
        """Test POST /api/users/{userId}/block endpoint"""
        if not self.test_user_id:
            self.log_result("Block User", False, "No test user ID available")
            return
        
        try:
            response = self.session.post(f"{API_BASE}/users/{self.test_user_id}/block")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'blocked' in data['message'].lower():
                    self.log_result("Block User", True, f"Successfully blocked user: {data['message']}")
                else:
                    self.log_result("Block User", False, f"Unexpected response: {data}")
            else:
                self.log_result("Block User", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Block User", False, "Exception occurred", str(e))
    
    def test_block_self(self):
        """Test POST /api/users/{userId}/block with own user ID"""
        try:
            response = self.session.post(f"{API_BASE}/users/{self.current_user_id}/block")
            
            if response.status_code == 400:
                self.log_result("Block Self", True, "Correctly prevented self-blocking")
            else:
                self.log_result("Block Self", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Block Self", False, "Exception occurred", str(e))
    
    def test_hide_user_story(self):
        """Test POST /api/users/{userId}/hide-story endpoint"""
        if not self.test_user_id:
            self.log_result("Hide User Story", False, "No test user ID available")
            return
        
        try:
            response = self.session.post(f"{API_BASE}/users/{self.test_user_id}/hide-story")
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'hidden' in data['message'].lower():
                    self.log_result("Hide User Story", True, f"Successfully hid stories: {data['message']}")
                else:
                    self.log_result("Hide User Story", False, f"Unexpected response: {data}")
            else:
                self.log_result("Hide User Story", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Hide User Story", False, "Exception occurred", str(e))
    
    def test_hide_own_story(self):
        """Test POST /api/users/{userId}/hide-story with own user ID"""
        try:
            response = self.session.post(f"{API_BASE}/users/{self.current_user_id}/hide-story")
            
            if response.status_code == 400:
                self.log_result("Hide Own Story", True, "Correctly prevented hiding own stories")
            else:
                self.log_result("Hide Own Story", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Hide Own Story", False, "Exception occurred", str(e))
    
    def test_authentication_required(self):
        """Test that endpoints require authentication"""
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            
            response = unauth_session.get(f"{API_BASE}/users/test-id/profile")
            
            if response.status_code == 401:
                self.log_result("Authentication Required", True, "Correctly requires authentication")
            else:
                self.log_result("Authentication Required", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Authentication Required", False, "Exception occurred", str(e))
    
    def test_get_user_profile_with_settings(self):
        """Test GET /api/auth/me endpoint - should NOT include publicProfile, should include blockedUsers"""
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that publicProfile is NOT included (removed setting)
                if 'publicProfile' in data:
                    self.log_result("Get User Profile with Settings", False, "publicProfile should be removed but is still present")
                    return
                
                # Check that blockedUsers array is included
                if 'blockedUsers' not in data:
                    self.log_result("Get User Profile with Settings", False, "blockedUsers array is missing")
                    return
                
                if not isinstance(data['blockedUsers'], list):
                    self.log_result("Get User Profile with Settings", False, f"blockedUsers should be array, got {type(data['blockedUsers'])}")
                    return
                
                # Check for remaining 9 required setting fields (excluding publicProfile)
                privacy_fields = ['appearInSearch', 'allowDirectMessages', 'showOnlineStatus']
                interaction_fields = ['allowTagging', 'allowStoryReplies', 'showVibeScore']
                notification_fields = ['pushNotifications', 'emailNotifications']
                
                all_setting_fields = privacy_fields + interaction_fields + notification_fields + ['isPrivate']
                missing_fields = [field for field in all_setting_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Get User Profile with Settings", False, f"Missing setting fields: {missing_fields}")
                else:
                    # Verify field types are boolean
                    invalid_types = []
                    for field in all_setting_fields:
                        if not isinstance(data[field], bool):
                            invalid_types.append(f"{field}: {type(data[field])}")
                    
                    if invalid_types:
                        self.log_result("Get User Profile with Settings", False, f"Invalid field types: {invalid_types}")
                    else:
                        self.log_result("Get User Profile with Settings", True, 
                                      f"✅ publicProfile removed, blockedUsers present, 9 remaining settings valid. Privacy: {len(privacy_fields)}, Interaction: {len(interaction_fields)}, Notification: {len(notification_fields)}")
            else:
                self.log_result("Get User Profile with Settings", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get User Profile with Settings", False, "Exception occurred", str(e))
    
    def test_update_individual_settings(self):
        """Test PUT /api/auth/settings endpoint for updating individual settings (excluding publicProfile)"""
        try:
            # Test updating valid privacy settings (excluding publicProfile)
            privacy_update = {
                "appearInSearch": False,
                "allowDirectMessages": False
            }
            
            response = self.session.put(f"{API_BASE}/auth/settings", json=privacy_update)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'updated' in data:
                    # Verify the settings were updated
                    me_response = self.session.get(f"{API_BASE}/auth/me")
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        if me_data['appearInSearch'] == False and me_data['allowDirectMessages'] == False:
                            self.log_result("Update Individual Settings", True, 
                                          f"Successfully updated privacy settings: {data['updated']}")
                        else:
                            self.log_result("Update Individual Settings", False, 
                                          f"Settings not persisted correctly. Expected: {privacy_update}, Got: appearInSearch={me_data['appearInSearch']}, allowDirectMessages={me_data['allowDirectMessages']}")
                    else:
                        self.log_result("Update Individual Settings", False, "Could not verify settings persistence")
                else:
                    self.log_result("Update Individual Settings", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Update Individual Settings", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Update Individual Settings", False, "Exception occurred", str(e))
    
    def test_update_bulk_settings(self):
        """Test PUT /api/auth/settings endpoint for bulk settings updates"""
        try:
            # Test updating multiple settings at once
            bulk_update = {
                "allowDirectMessages": False,
                "showOnlineStatus": False,
                "allowTagging": False,
                "allowStoryReplies": False,
                "pushNotifications": False,
                "emailNotifications": False
            }
            
            response = self.session.put(f"{API_BASE}/auth/settings", json=bulk_update)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'updated' in data:
                    # Verify all settings were updated
                    me_response = self.session.get(f"{API_BASE}/auth/me")
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        all_correct = all(me_data[key] == value for key, value in bulk_update.items())
                        
                        if all_correct:
                            self.log_result("Update Bulk Settings", True, 
                                          f"Successfully updated {len(bulk_update)} settings: {list(bulk_update.keys())}")
                        else:
                            mismatches = {k: f"expected {v}, got {me_data[k]}" for k, v in bulk_update.items() if me_data[k] != v}
                            self.log_result("Update Bulk Settings", False, 
                                          f"Settings not persisted correctly: {mismatches}")
                    else:
                        self.log_result("Update Bulk Settings", False, "Could not verify settings persistence")
                else:
                    self.log_result("Update Bulk Settings", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Update Bulk Settings", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Update Bulk Settings", False, "Exception occurred", str(e))
    
    def test_invalid_settings_validation(self):
        """Test PUT /api/auth/settings endpoint rejects publicProfile and other invalid settings"""
        try:
            # Test with publicProfile (should be rejected) and other invalid settings
            invalid_update = {
                "publicProfile": True,  # This should be rejected as it's removed
                "invalidSetting": True,
                "anotherInvalidSetting": 123
            }
            
            response = self.session.put(f"{API_BASE}/auth/settings", json=invalid_update)
            
            if response.status_code == 400:
                self.log_result("Invalid Settings Validation", True, "✅ Correctly rejected publicProfile and invalid settings")
            elif response.status_code == 200:
                # Check if only valid settings were updated
                data = response.json()
                if 'updated' in data and len(data['updated']) == 0:
                    self.log_result("Invalid Settings Validation", True, "✅ No invalid settings were processed (including publicProfile)")
                else:
                    # Check if publicProfile was processed (it shouldn't be)
                    if 'publicProfile' in data.get('updated', {}):
                        self.log_result("Invalid Settings Validation", False, "❌ publicProfile was processed but should be rejected")
                    else:
                        self.log_result("Invalid Settings Validation", True, f"✅ publicProfile rejected, other invalid settings ignored: {data.get('updated', {})}")
            else:
                self.log_result("Invalid Settings Validation", False, f"Unexpected status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Invalid Settings Validation", False, "Exception occurred", str(e))
    
    def test_empty_settings_update(self):
        """Test PUT /api/auth/settings endpoint with empty request"""
        try:
            response = self.session.put(f"{API_BASE}/auth/settings", json={})
            
            if response.status_code == 400:
                self.log_result("Empty Settings Update", True, "Correctly rejected empty settings update")
            else:
                self.log_result("Empty Settings Update", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Empty Settings Update", False, "Exception occurred", str(e))
    
    def test_data_download(self):
        """Test GET /api/auth/download-data endpoint for exporting user data"""
        try:
            response = self.session.get(f"{API_BASE}/auth/download-data")
            
            if response.status_code == 200:
                # Check if response is JSON
                try:
                    data = response.json()
                    
                    # Check for required sections in export
                    required_sections = ['profile', 'posts', 'stories', 'notifications', 'exportedAt', 'totalPosts', 'totalStories', 'totalNotifications']
                    missing_sections = [section for section in required_sections if section not in data]
                    
                    if missing_sections:
                        self.log_result("Data Download", False, f"Missing sections in export: {missing_sections}")
                    else:
                        # Check profile section has required fields
                        profile = data['profile']
                        profile_fields = ['id', 'fullName', 'username', 'age', 'gender', 'createdAt', 'followers', 'following']
                        missing_profile_fields = [field for field in profile_fields if field not in profile]
                        
                        if missing_profile_fields:
                            self.log_result("Data Download", False, f"Missing profile fields: {missing_profile_fields}")
                        else:
                            # Check Content-Disposition header for filename
                            content_disposition = response.headers.get('Content-Disposition', '')
                            has_filename = 'filename=' in content_disposition and 'luvhive-data-' in content_disposition
                            
                            if has_filename:
                                self.log_result("Data Download", True, 
                                              f"Successfully exported data with {data['totalPosts']} posts, {data['totalStories']} stories, {data['totalNotifications']} notifications")
                            else:
                                self.log_result("Data Download", False, "Missing or incorrect Content-Disposition header")
                        
                except json.JSONDecodeError:
                    self.log_result("Data Download", False, "Response is not valid JSON")
            else:
                self.log_result("Data Download", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Data Download", False, "Exception occurred", str(e))
    
    def test_settings_authentication_required(self):
        """Test that settings endpoints require authentication"""
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            
            # Test settings update without auth
            response = unauth_session.put(f"{API_BASE}/auth/settings", json={"appearInSearch": False})
            
            if response.status_code == 401:
                # Test data download without auth
                response2 = unauth_session.get(f"{API_BASE}/auth/download-data")
                
                if response2.status_code == 401:
                    self.log_result("Settings Authentication Required", True, "Both settings endpoints correctly require authentication")
                else:
                    self.log_result("Settings Authentication Required", False, f"Data download endpoint: expected 401, got {response2.status_code}")
            else:
                self.log_result("Settings Authentication Required", False, f"Settings update endpoint: expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Settings Authentication Required", False, "Exception occurred", str(e))
    
    def test_get_blocked_users(self):
        """Test GET /api/users/blocked endpoint returns list of blocked users"""
        try:
            response = self.session.get(f"{API_BASE}/users/blocked")
            
            if response.status_code == 200:
                data = response.json()
                if 'blockedUsers' in data and isinstance(data['blockedUsers'], list):
                    self.log_result("Get Blocked Users", True, 
                                  f"Successfully retrieved blocked users list with {len(data['blockedUsers'])} users")
                else:
                    self.log_result("Get Blocked Users", False, "Response missing 'blockedUsers' array")
            else:
                self.log_result("Get Blocked Users", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get Blocked Users", False, "Exception occurred", str(e))
    
    def test_unblock_user(self):
        """Test POST /api/users/{userId}/unblock endpoint"""
        if not self.test_user_id:
            self.log_result("Unblock User", False, "No test user ID available")
            return
        
        try:
            # First ensure the user is blocked
            block_response = self.session.post(f"{API_BASE}/users/{self.test_user_id}/block")
            
            if block_response.status_code == 200:
                # Now test unblocking
                response = self.session.post(f"{API_BASE}/users/{self.test_user_id}/unblock")
                
                if response.status_code == 200:
                    data = response.json()
                    if 'message' in data and 'unblock' in data['message'].lower():
                        # Verify user is removed from blocked list
                        me_response = self.session.get(f"{API_BASE}/auth/me")
                        if me_response.status_code == 200:
                            me_data = me_response.json()
                            if self.test_user_id not in me_data.get('blockedUsers', []):
                                self.log_result("Unblock User", True, f"Successfully unblocked user: {data['message']}")
                            else:
                                self.log_result("Unblock User", False, "User still in blocked list after unblocking")
                        else:
                            self.log_result("Unblock User", False, "Could not verify unblock operation")
                    else:
                        self.log_result("Unblock User", False, f"Unexpected response: {data}")
                else:
                    self.log_result("Unblock User", False, f"Status: {response.status_code}", response.text)
            else:
                self.log_result("Unblock User", False, "Could not block user first for testing")
                
        except Exception as e:
            self.log_result("Unblock User", False, "Exception occurred", str(e))
    
    def test_unblock_self(self):
        """Test POST /api/users/{userId}/unblock with own user ID"""
        try:
            response = self.session.post(f"{API_BASE}/users/{self.current_user_id}/unblock")
            
            if response.status_code == 400:
                self.log_result("Unblock Self", True, "Correctly prevented self-unblocking")
            else:
                self.log_result("Unblock Self", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Unblock Self", False, "Exception occurred", str(e))
    
    def test_remaining_9_settings_persistence(self):
        """Test that all 9 remaining settings (excluding publicProfile) work correctly"""
        try:
            # Test all 9 remaining settings
            all_settings = {
                "isPrivate": True,
                "appearInSearch": False,
                "allowDirectMessages": True,
                "showOnlineStatus": False,
                "allowTagging": True,
                "allowStoryReplies": False,
                "showVibeScore": True,
                "pushNotifications": False,
                "emailNotifications": True
            }
            
            response = self.session.put(f"{API_BASE}/auth/settings", json=all_settings)
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'updated' in data:
                    # Verify all 9 settings were updated and persisted
                    me_response = self.session.get(f"{API_BASE}/auth/me")
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        
                        # Check each setting
                        mismatches = []
                        for key, expected_value in all_settings.items():
                            if key not in me_data:
                                mismatches.append(f"{key}: missing")
                            elif me_data[key] != expected_value:
                                mismatches.append(f"{key}: expected {expected_value}, got {me_data[key]}")
                        
                        if mismatches:
                            self.log_result("Remaining 9 Settings Persistence", False, 
                                          f"Settings not persisted correctly: {mismatches}")
                        else:
                            self.log_result("Remaining 9 Settings Persistence", True, 
                                          f"✅ All 9 remaining settings work correctly: {list(all_settings.keys())}")
                    else:
                        self.log_result("Remaining 9 Settings Persistence", False, "Could not verify settings persistence")
                else:
                    self.log_result("Remaining 9 Settings Persistence", False, f"Unexpected response format: {data}")
            else:
                self.log_result("Remaining 9 Settings Persistence", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Remaining 9 Settings Persistence", False, "Exception occurred", str(e))
    
    # ========== SEARCH FUNCTIONALITY TESTS ==========
    
    def create_test_posts(self):
        """Create test posts with hashtags for search testing"""
        try:
            # Create posts with different content for search testing
            test_posts = [
                {
                    "mediaType": "image",
                    "mediaUrl": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                    "caption": "Beautiful sunset at the beach! #sunset #beach #nature #photography"
                },
                {
                    "mediaType": "image", 
                    "mediaUrl": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                    "caption": "Coffee time! ☕ #coffee #morning #lifestyle #cafe"
                },
                {
                    "mediaType": "image",
                    "mediaUrl": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k=",
                    "caption": "Working out at the gym 💪 #fitness #gym #workout #health"
                }
            ]
            
            created_posts = []
            for post_data in test_posts:
                response = self.session.post(f"{API_BASE}/posts/create", json=post_data)
                if response.status_code == 200:
                    created_posts.append(response.json())
            
            self.log_result("Create Test Posts", len(created_posts) == len(test_posts), 
                          f"Created {len(created_posts)}/{len(test_posts)} test posts")
            return len(created_posts) > 0
            
        except Exception as e:
            self.log_result("Create Test Posts", False, "Exception occurred", str(e))
            return False
    
    def test_search_all_content(self):
        """Test POST /api/search endpoint with type 'all'"""
        try:
            search_request = {
                "query": "beach",
                "type": "all"
            }
            
            response = self.session.post(f"{API_BASE}/search", json=search_request)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['users', 'posts', 'hashtags', 'query']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Search All Content", False, f"Missing fields: {missing_fields}")
                else:
                    # Verify data structure
                    if (isinstance(data['users'], list) and 
                        isinstance(data['posts'], list) and 
                        isinstance(data['hashtags'], list) and
                        data['query'] == search_request['query']):
                        
                        self.log_result("Search All Content", True, 
                                      f"Found {len(data['users'])} users, {len(data['posts'])} posts, {len(data['hashtags'])} hashtags")
                    else:
                        self.log_result("Search All Content", False, "Invalid data structure in response")
            else:
                self.log_result("Search All Content", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Search All Content", False, "Exception occurred", str(e))
    
    def test_search_users_only(self):
        """Test POST /api/search endpoint with type 'users'"""
        try:
            search_request = {
                "query": "alex",
                "type": "users"
            }
            
            response = self.session.post(f"{API_BASE}/search", json=search_request)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'users' in data and isinstance(data['users'], list):
                    # Check if users have required fields
                    if data['users']:
                        user = data['users'][0]
                        required_user_fields = ['id', 'fullName', 'username', 'followersCount', 'isFollowing']
                        missing_user_fields = [field for field in required_user_fields if field not in user]
                        
                        if missing_user_fields:
                            self.log_result("Search Users Only", False, f"Missing user fields: {missing_user_fields}")
                        else:
                            self.log_result("Search Users Only", True, f"Found {len(data['users'])} users matching 'alex'")
                    else:
                        self.log_result("Search Users Only", True, "No users found matching 'alex' (expected)")
                else:
                    self.log_result("Search Users Only", False, "Response missing 'users' array")
            else:
                self.log_result("Search Users Only", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Search Users Only", False, "Exception occurred", str(e))
    
    def test_search_posts_only(self):
        """Test POST /api/search endpoint with type 'posts'"""
        try:
            search_request = {
                "query": "coffee",
                "type": "posts"
            }
            
            response = self.session.post(f"{API_BASE}/search", json=search_request)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'posts' in data and isinstance(data['posts'], list):
                    # Check if posts have required fields
                    if data['posts']:
                        post = data['posts'][0]
                        required_post_fields = ['id', 'userId', 'username', 'mediaType', 'caption', 'likes', 'comments']
                        missing_post_fields = [field for field in required_post_fields if field not in post]
                        
                        if missing_post_fields:
                            self.log_result("Search Posts Only", False, f"Missing post fields: {missing_post_fields}")
                        else:
                            self.log_result("Search Posts Only", True, f"Found {len(data['posts'])} posts matching 'coffee'")
                    else:
                        self.log_result("Search Posts Only", True, "No posts found matching 'coffee' (may be expected)")
                else:
                    self.log_result("Search Posts Only", False, "Response missing 'posts' array")
            else:
                self.log_result("Search Posts Only", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Search Posts Only", False, "Exception occurred", str(e))
    
    def test_search_hashtags_only(self):
        """Test POST /api/search endpoint with type 'hashtags'"""
        try:
            search_request = {
                "query": "#beach",
                "type": "hashtags"
            }
            
            response = self.session.post(f"{API_BASE}/search", json=search_request)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'hashtags' in data and isinstance(data['hashtags'], list):
                    self.log_result("Search Hashtags Only", True, f"Found {len(data['hashtags'])} hashtags matching '#beach'")
                else:
                    self.log_result("Search Hashtags Only", False, "Response missing 'hashtags' array")
            else:
                self.log_result("Search Hashtags Only", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Search Hashtags Only", False, "Exception occurred", str(e))
    
    def test_search_empty_query(self):
        """Test POST /api/search endpoint with empty query"""
        try:
            search_request = {
                "query": "",
                "type": "all"
            }
            
            response = self.session.post(f"{API_BASE}/search", json=search_request)
            
            if response.status_code == 400:
                self.log_result("Search Empty Query", True, "Correctly rejected empty search query")
            else:
                self.log_result("Search Empty Query", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_result("Search Empty Query", False, "Exception occurred", str(e))
    
    def test_search_blocked_users_excluded(self):
        """Test that blocked users are excluded from search results"""
        try:
            # First block the test user
            if self.test_user_id:
                block_response = self.session.post(f"{API_BASE}/users/{self.test_user_id}/block")
                
                if block_response.status_code == 200:
                    # Now search for the blocked user
                    search_request = {
                        "query": "alex",
                        "type": "users"
                    }
                    
                    response = self.session.post(f"{API_BASE}/search", json=search_request)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Check if blocked user is excluded
                        blocked_user_found = any(user['id'] == self.test_user_id for user in data.get('users', []))
                        
                        if not blocked_user_found:
                            self.log_result("Search Blocked Users Excluded", True, "Blocked users correctly excluded from search")
                        else:
                            self.log_result("Search Blocked Users Excluded", False, "Blocked user found in search results")
                    else:
                        self.log_result("Search Blocked Users Excluded", False, f"Search failed: {response.status_code}")
                else:
                    self.log_result("Search Blocked Users Excluded", False, "Could not block user for testing")
            else:
                self.log_result("Search Blocked Users Excluded", False, "No test user ID available")
                
        except Exception as e:
            self.log_result("Search Blocked Users Excluded", False, "Exception occurred", str(e))
    
    def test_get_trending_content(self):
        """Test GET /api/search/trending endpoint"""
        try:
            response = self.session.get(f"{API_BASE}/search/trending")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['trending_users', 'trending_hashtags']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_result("Get Trending Content", False, f"Missing fields: {missing_fields}")
                else:
                    # Verify data structure
                    if (isinstance(data['trending_users'], list) and 
                        isinstance(data['trending_hashtags'], list)):
                        
                        # Check trending users structure
                        if data['trending_users']:
                            user = data['trending_users'][0]
                            required_user_fields = ['id', 'fullName', 'username', 'followersCount', 'isFollowing']
                            missing_user_fields = [field for field in required_user_fields if field not in user]
                            
                            if missing_user_fields:
                                self.log_result("Get Trending Content", False, f"Missing trending user fields: {missing_user_fields}")
                                return
                        
                        # Check trending hashtags structure
                        if data['trending_hashtags']:
                            hashtag = data['trending_hashtags'][0]
                            required_hashtag_fields = ['hashtag', 'count']
                            missing_hashtag_fields = [field for field in required_hashtag_fields if field not in hashtag]
                            
                            if missing_hashtag_fields:
                                self.log_result("Get Trending Content", False, f"Missing trending hashtag fields: {missing_hashtag_fields}")
                                return
                        
                        self.log_result("Get Trending Content", True, 
                                      f"Retrieved {len(data['trending_users'])} trending users, {len(data['trending_hashtags'])} trending hashtags")
                    else:
                        self.log_result("Get Trending Content", False, "Invalid data structure in response")
            else:
                self.log_result("Get Trending Content", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get Trending Content", False, "Exception occurred", str(e))
    
    def test_get_search_suggestions(self):
        """Test GET /api/search/suggestions endpoint"""
        try:
            # Test with user query
            response = self.session.get(f"{API_BASE}/search/suggestions?q=em")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'suggestions' in data and isinstance(data['suggestions'], list):
                    # Check suggestions structure
                    if data['suggestions']:
                        suggestion = data['suggestions'][0]
                        required_fields = ['type', 'text', 'value']
                        missing_fields = [field for field in required_fields if field not in suggestion]
                        
                        if missing_fields:
                            self.log_result("Get Search Suggestions", False, f"Missing suggestion fields: {missing_fields}")
                        else:
                            self.log_result("Get Search Suggestions", True, 
                                          f"Retrieved {len(data['suggestions'])} suggestions for 'em'")
                    else:
                        self.log_result("Get Search Suggestions", True, "No suggestions found for 'em' (may be expected)")
                else:
                    self.log_result("Get Search Suggestions", False, "Response missing 'suggestions' array")
            else:
                self.log_result("Get Search Suggestions", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get Search Suggestions", False, "Exception occurred", str(e))
    
    def test_get_search_suggestions_hashtag(self):
        """Test GET /api/search/suggestions endpoint with hashtag query"""
        try:
            # Test with hashtag query
            response = self.session.get(f"{API_BASE}/search/suggestions?q=%23beach")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'suggestions' in data and isinstance(data['suggestions'], list):
                    # Check if hashtag suggestions are returned
                    hashtag_suggestions = [s for s in data['suggestions'] if s.get('type') == 'hashtag']
                    self.log_result("Get Search Suggestions Hashtag", True, 
                                  f"Retrieved {len(hashtag_suggestions)} hashtag suggestions for '#beach'")
                else:
                    self.log_result("Get Search Suggestions Hashtag", False, "Response missing 'suggestions' array")
            else:
                self.log_result("Get Search Suggestions Hashtag", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get Search Suggestions Hashtag", False, "Exception occurred", str(e))
    
    def test_get_search_suggestions_min_length(self):
        """Test GET /api/search/suggestions endpoint with query less than 2 characters"""
        try:
            # Test with single character (should return empty)
            response = self.session.get(f"{API_BASE}/search/suggestions?q=a")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'suggestions' in data and isinstance(data['suggestions'], list):
                    if len(data['suggestions']) == 0:
                        self.log_result("Get Search Suggestions Min Length", True, 
                                      "Correctly returned empty suggestions for query < 2 characters")
                    else:
                        self.log_result("Get Search Suggestions Min Length", False, 
                                      f"Expected empty suggestions, got {len(data['suggestions'])}")
                else:
                    self.log_result("Get Search Suggestions Min Length", False, "Response missing 'suggestions' array")
            else:
                self.log_result("Get Search Suggestions Min Length", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_result("Get Search Suggestions Min Length", False, "Exception occurred", str(e))
    
    def test_search_authentication_required(self):
        """Test that search endpoints require authentication"""
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            
            # Test search endpoint
            search_response = unauth_session.post(f"{API_BASE}/search", json={"query": "test", "type": "all"})
            
            if search_response.status_code == 401:
                # Test trending endpoint
                trending_response = unauth_session.get(f"{API_BASE}/search/trending")
                
                if trending_response.status_code == 401:
                    # Test suggestions endpoint
                    suggestions_response = unauth_session.get(f"{API_BASE}/search/suggestions?q=test")
                    
                    if suggestions_response.status_code == 401:
                        self.log_result("Search Authentication Required", True, 
                                      "All search endpoints correctly require authentication")
                    else:
                        self.log_result("Search Authentication Required", False, 
                                      f"Suggestions endpoint: expected 401, got {suggestions_response.status_code}")
                else:
                    self.log_result("Search Authentication Required", False, 
                                  f"Trending endpoint: expected 401, got {trending_response.status_code}")
            else:
                self.log_result("Search Authentication Required", False, 
                              f"Search endpoint: expected 401, got {search_response.status_code}")
                
        except Exception as e:
            self.log_result("Search Authentication Required", False, "Exception occurred", str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("LUVHIVE BACKEND API TESTING")
        print("=" * 60)
        print(f"Testing against: {API_BASE}")
        print()
        
        # Setup phase
        if not self.register_test_user():
            print("❌ Cannot proceed without authenticated user")
            return
        
        if not self.register_second_user():
            print("❌ Cannot proceed without second test user")
            return
        
        # Test all endpoints
        print("Testing User Profile Endpoints...")
        self.test_get_user_profile()
        self.test_get_user_profile_invalid_id()
        self.test_get_user_posts()
        
        print("Testing AI Vibe Compatibility...")
        self.test_ai_vibe_compatibility()
        self.test_ai_vibe_compatibility_missing_target()
        
        print("Testing User Blocking...")
        self.test_block_user()
        self.test_block_self()
        
        print("Testing Story Hiding...")
        self.test_hide_user_story()
        self.test_hide_own_story()
        
        print("Testing Authentication...")
        self.test_authentication_required()
        
        print("Testing Updated Settings Functionality...")
        self.test_get_user_profile_with_settings()
        self.test_update_individual_settings()
        self.test_update_bulk_settings()
        self.test_invalid_settings_validation()
        self.test_empty_settings_update()
        self.test_data_download()
        self.test_settings_authentication_required()
        self.test_remaining_9_settings_persistence()
        
        print("Testing Blocked Users Management...")
        self.test_get_blocked_users()
        self.test_unblock_user()
        self.test_unblock_self()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Total Tests: {self.results['passed'] + self.results['failed']}")
        
        if self.results['errors']:
            print("\nFAILED TESTS:")
            for error in self.results['errors']:
                print(f"- {error['test']}: {error['message']}")
                if error['error']:
                    print(f"  Error: {error['error']}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = LuvHiveAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)