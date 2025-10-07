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
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://dating-social.preview.emergentagent.com')
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
        """Test PUT /api/auth/settings endpoint with invalid settings"""
        try:
            # Test with invalid setting names and values
            invalid_update = {
                "invalidSetting": True,
                "publicProfile": "not_a_boolean",
                "anotherInvalidSetting": 123
            }
            
            response = self.session.put(f"{API_BASE}/auth/settings", json=invalid_update)
            
            if response.status_code == 400:
                self.log_result("Invalid Settings Validation", True, "Correctly rejected invalid settings")
            elif response.status_code == 200:
                # Check if only valid settings were updated
                data = response.json()
                if 'updated' in data and len(data['updated']) == 0:
                    self.log_result("Invalid Settings Validation", True, "No invalid settings were processed")
                else:
                    self.log_result("Invalid Settings Validation", False, f"Invalid settings were processed: {data.get('updated', {})}")
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
            response = unauth_session.put(f"{API_BASE}/auth/settings", json={"publicProfile": False})
            
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
        
        print("Testing Settings Functionality...")
        self.test_get_user_profile_with_settings()
        self.test_update_individual_settings()
        self.test_update_bulk_settings()
        self.test_invalid_settings_validation()
        self.test_empty_settings_update()
        self.test_data_download()
        self.test_settings_authentication_required()
        
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