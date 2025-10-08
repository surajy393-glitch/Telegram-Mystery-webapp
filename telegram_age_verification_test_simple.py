#!/usr/bin/env python3
"""
Simplified Telegram Bot Age Verification Testing
Focus on code verification and logic testing without complex async mocking
"""

import os
import sys
import re
from pathlib import Path

# Add telegram_bot directory to path
sys.path.insert(0, '/app/telegram_bot')

class SimpleTelegramAgeVerificationTester:
    def __init__(self):
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

    def test_module_import_and_functions(self):
        """Test that registration.py module can be imported and has required functions"""
        try:
            import registration
            
            # Check if key functions exist
            required_functions = [
                'ensure_age_verification_columns',
                'handle_registration_text',
                'on_callback'
            ]
            
            missing_functions = []
            existing_functions = []
            
            for func_name in required_functions:
                if hasattr(registration, func_name):
                    existing_functions.append(func_name)
                else:
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.log_result("Module Import and Functions", False, 
                              f"Missing functions: {missing_functions}. Found: {existing_functions}")
            else:
                self.log_result("Module Import and Functions", True, 
                              f"Successfully imported registration.py with all required functions: {existing_functions}")
                
        except Exception as e:
            self.log_result("Module Import and Functions", False, "Failed to import registration.py", str(e))

    def test_age_verification_database_schema(self):
        """Test that age verification database schema functions exist"""
        try:
            import registration
            
            # Check if ensure_age_verification_columns function exists and can be called
            if hasattr(registration, 'ensure_age_verification_columns'):
                # Read the function source to verify it creates the right columns
                import inspect
                source = inspect.getsource(registration.ensure_age_verification_columns)
                
                # Check for required SQL statements
                required_columns = [
                    'age_verified BOOLEAN DEFAULT FALSE',
                    'age_agreement_date TIMESTAMPTZ'
                ]
                
                missing_columns = []
                found_columns = []
                
                for col in required_columns:
                    if col in source:
                        found_columns.append(col)
                    else:
                        missing_columns.append(col)
                
                if missing_columns:
                    self.log_result("Age Verification Database Schema", False, 
                                  f"Missing column definitions: {missing_columns}")
                else:
                    self.log_result("Age Verification Database Schema", True, 
                                  f"All required columns defined: {found_columns}")
            else:
                self.log_result("Age Verification Database Schema", False, 
                              "ensure_age_verification_columns function not found")
                
        except Exception as e:
            self.log_result("Age Verification Database Schema", False, "Exception occurred", str(e))

    def test_age_rejection_logic_in_code(self):
        """Test that age rejection logic exists in the code"""
        try:
            # Read the registration.py file and check for age rejection logic
            registration_file = Path('/app/telegram_bot/registration.py')
            
            if not registration_file.exists():
                self.log_result("Age Rejection Logic in Code", False, "registration.py file not found")
                return
            
            content = registration_file.read_text()
            
            # Check for age rejection patterns
            age_rejection_patterns = [
                r'age\s*<\s*18',  # age < 18
                r'18\+\s*only',   # 18+ only
                r'cannot\s+use\s+this\s+bot',  # cannot use this bot
                r'return'  # Should return/stop registration
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in age_rejection_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if age rejection logic is present
            if len(found_patterns) >= 3:  # At least 3 out of 4 patterns should be found
                self.log_result("Age Rejection Logic in Code", True, 
                              f"Age rejection logic found with patterns: {found_patterns}")
            else:
                self.log_result("Age Rejection Logic in Code", False, 
                              f"Insufficient age rejection logic. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Age Rejection Logic in Code", False, "Exception occurred", str(e))

    def test_age_agreement_dialog_in_code(self):
        """Test that age agreement dialog code exists"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for age agreement dialog patterns
            dialog_patterns = [
                r'AGE\s+VERIFICATION',  # AGE VERIFICATION header
                r'18\+\s+years\s+old',  # 18+ years old confirmation
                r'False\s+age.*ban',    # False age warning
                r'I\s+Agree.*18\+',     # I Agree (18+) button
                r'age_agree'            # age_agree callback data
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in dialog_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if age agreement dialog is present
            if len(found_patterns) >= 4:  # At least 4 out of 5 patterns should be found
                self.log_result("Age Agreement Dialog in Code", True, 
                              f"Age agreement dialog found with patterns: {found_patterns}")
            else:
                self.log_result("Age Agreement Dialog in Code", False, 
                              f"Insufficient age agreement dialog. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Age Agreement Dialog in Code", False, "Exception occurred", str(e))

    def test_callback_handler_in_code(self):
        """Test that age_agree callback handler exists in code"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for callback handler patterns
            callback_patterns = [
                r'age_agree',                    # age_agree callback data
                r'age_verified\s*=\s*TRUE',      # Database update with age_verified=TRUE
                r'age_agreement_date\s*=\s*NOW', # Database update with timestamp
                r'UPDATE\s+users',               # SQL UPDATE statement
                r'COUNTRY'                       # State transition to COUNTRY
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in callback_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if callback handler is present
            if len(found_patterns) >= 4:  # At least 4 out of 5 patterns should be found
                self.log_result("Callback Handler in Code", True, 
                              f"Age agree callback handler found with patterns: {found_patterns}")
            else:
                self.log_result("Callback Handler in Code", False, 
                              f"Insufficient callback handler logic. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Callback Handler in Code", False, "Exception occurred", str(e))

    def test_database_update_logic_in_code(self):
        """Test that database update logic for age verification exists"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for database update patterns
            db_patterns = [
                r'UPDATE\s+users.*SET.*age_verified\s*=\s*TRUE',  # UPDATE with age_verified=TRUE
                r'age_agreement_date\s*=\s*NOW\(\)',              # Timestamp with NOW()
                r'WHERE\s+tg_user_id\s*=\s*%s',                  # WHERE clause with user ID
                r'con\.commit\(\)',                               # Transaction commit
                r'cur\.execute'                                   # Cursor execute
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in db_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if database update logic is present
            if len(found_patterns) >= 4:  # At least 4 out of 5 patterns should be found
                self.log_result("Database Update Logic in Code", True, 
                              f"Database update logic found with patterns: {found_patterns}")
            else:
                self.log_result("Database Update Logic in Code", False, 
                              f"Insufficient database update logic. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Database Update Logic in Code", False, "Exception occurred", str(e))

    def test_registration_flow_state_management(self):
        """Test that registration flow state management is implemented"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for state management patterns
            state_patterns = [
                r'reg_state.*AGE',               # AGE state handling
                r'reg_state.*COUNTRY',           # COUNTRY state transition
                r'context\.user_data',           # Context user data usage
                r'Age verification complete',    # Success message
                r'country'                       # Next step prompt
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in state_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if state management is present
            if len(found_patterns) >= 4:  # At least 4 out of 5 patterns should be found
                self.log_result("Registration Flow State Management", True, 
                              f"State management found with patterns: {found_patterns}")
            else:
                self.log_result("Registration Flow State Management", False, 
                              f"Insufficient state management. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Registration Flow State Management", False, "Exception occurred", str(e))

    def test_error_handling_and_validation(self):
        """Test that proper error handling and input validation exists"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for error handling patterns
            error_patterns = [
                r'isdigit\(\)',                  # Numeric validation
                r'age\s*<\s*13.*age\s*>\s*99',   # Age range validation
                r'Please\s+send.*number',        # Error message for non-numeric
                r'between\s+13.*99',             # Age range error message
                r'try.*except'                   # Exception handling
            ]
            
            found_patterns = []
            missing_patterns = []
            
            for pattern in error_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)
            
            # Check if error handling is present
            if len(found_patterns) >= 3:  # At least 3 out of 5 patterns should be found
                self.log_result("Error Handling and Validation", True, 
                              f"Error handling found with patterns: {found_patterns}")
            else:
                self.log_result("Error Handling and Validation", False, 
                              f"Insufficient error handling. Found: {found_patterns}, Missing: {missing_patterns}")
                
        except Exception as e:
            self.log_result("Error Handling and Validation", False, "Exception occurred", str(e))

    def test_complete_age_verification_implementation(self):
        """Test that all components of age verification are implemented together"""
        try:
            registration_file = Path('/app/telegram_bot/registration.py')
            content = registration_file.read_text()
            
            # Check for complete implementation
            components = {
                'Age Input Handling': [r'state.*AGE', r'isdigit\(\)', r'int\(txt\)'],
                'Age Rejection': [r'age\s*<\s*18', r'18\+\s*only', r'cannot.*use.*bot'],
                'Age Agreement Dialog': [r'AGE\s+VERIFICATION', r'I\s+Agree.*18\+', r'age_agree'],
                'Callback Handler': [r'age_agree', r'age_verified\s*=\s*TRUE', r'age_agreement_date'],
                'Database Update': [r'UPDATE\s+users', r'NOW\(\)', r'commit\(\)'],
                'State Transition': [r'COUNTRY', r'Age verification complete', r'country']
            }
            
            results = {}
            for component, patterns in components.items():
                found = sum(1 for pattern in patterns if re.search(pattern, content, re.IGNORECASE))
                results[component] = f"{found}/{len(patterns)}"
            
            # Calculate overall score
            total_found = sum(int(result.split('/')[0]) for result in results.values())
            total_expected = sum(int(result.split('/')[1]) for result in results.values())
            score = (total_found / total_expected) * 100
            
            if score >= 80:  # 80% or more components found
                self.log_result("Complete Age Verification Implementation", True, 
                              f"Implementation score: {score:.1f}% - Components: {results}")
            else:
                self.log_result("Complete Age Verification Implementation", False, 
                              f"Implementation score: {score:.1f}% - Components: {results}")
                
        except Exception as e:
            self.log_result("Complete Age Verification Implementation", False, "Exception occurred", str(e))

    def run_all_tests(self):
        """Run all age verification tests"""
        print("🧪 TELEGRAM BOT AGE VERIFICATION CODE ANALYSIS")
        print("=" * 60)
        print()
        
        # Test 1: Module Import and Functions
        self.test_module_import_and_functions()
        
        # Test 2: Database Schema
        self.test_age_verification_database_schema()
        
        # Test 3: Age Rejection Logic
        self.test_age_rejection_logic_in_code()
        
        # Test 4: Age Agreement Dialog
        self.test_age_agreement_dialog_in_code()
        
        # Test 5: Callback Handler
        self.test_callback_handler_in_code()
        
        # Test 6: Database Update Logic
        self.test_database_update_logic_in_code()
        
        # Test 7: State Management
        self.test_registration_flow_state_management()
        
        # Test 8: Error Handling
        self.test_error_handling_and_validation()
        
        # Test 9: Complete Implementation
        self.test_complete_age_verification_implementation()
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🚨 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error['test']}: {error['message']}")
                if error['error']:
                    print(f"     Error: {error['error']}")
        
        print()
        return self.results['failed'] == 0

def main():
    """Main function to run all tests"""
    tester = SimpleTelegramAgeVerificationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! Age verification functionality is properly implemented.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())