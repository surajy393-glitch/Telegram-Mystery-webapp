#!/usr/bin/env python3
"""
Telegram Bot Age Verification Testing
Tests the age verification functionality implemented in /app/telegram_bot/registration.py
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import importlib.util
from datetime import datetime, timezone
import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

# Add telegram_bot directory to path
sys.path.insert(0, '/app/telegram_bot')

class TelegramBotAgeVerificationTester:
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.db_url = os.environ.get("DATABASE_URL")
        
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

    def test_module_import(self):
        """Test that registration.py module can be imported without errors"""
        try:
            import registration
            
            # Check if key functions exist
            required_functions = [
                'ensure_age_verification_columns',
                'handle_registration_text',
                'on_callback'
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not hasattr(registration, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                self.log_result("Module Import", False, f"Missing functions: {missing_functions}")
            else:
                self.log_result("Module Import", True, "Successfully imported registration.py with all required functions")
                
        except Exception as e:
            self.log_result("Module Import", False, "Failed to import registration.py", str(e))

    def test_age_verification_columns_exist(self):
        """Test that age verification database columns exist"""
        if not self.db_url:
            self.log_result("Age Verification Columns", False, "No DATABASE_URL configured")
            return
            
        try:
            # Import registration module to use its connection functions
            import registration
            
            # Ensure columns exist
            registration.ensure_age_verification_columns()
            
            # Check if columns exist in database
            with registration._conn() as conn, conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('age_verified', 'age_agreement_date')
                    ORDER BY column_name
                """)
                columns = cur.fetchall()
                
                if len(columns) == 2:
                    age_verified_col = next((col for col in columns if col[0] == 'age_verified'), None)
                    age_agreement_col = next((col for col in columns if col[0] == 'age_agreement_date'), None)
                    
                    if age_verified_col and age_agreement_col:
                        # Verify column types
                        if age_verified_col[1] == 'boolean' and 'timestamp' in age_agreement_col[1].lower():
                            self.log_result("Age Verification Columns", True, 
                                          f"Both columns exist with correct types: age_verified ({age_verified_col[1]}), age_agreement_date ({age_agreement_col[1]})")
                        else:
                            self.log_result("Age Verification Columns", False, 
                                          f"Incorrect column types: age_verified ({age_verified_col[1]}), age_agreement_date ({age_agreement_col[1]})")
                    else:
                        self.log_result("Age Verification Columns", False, "Columns exist but could not verify details")
                else:
                    self.log_result("Age Verification Columns", False, f"Expected 2 columns, found {len(columns)}")
                    
        except Exception as e:
            self.log_result("Age Verification Columns", False, "Database connection or query failed", str(e))

    def test_age_rejection_logic(self):
        """Test age rejection logic for users under 18"""
        try:
            import registration
            from telegram import Update, Message, User, Chat
            from telegram.ext import ContextTypes
            
            # Create mock objects
            mock_update = Mock(spec=Update)
            mock_message = Mock(spec=Message)
            mock_user = Mock(spec=User)
            mock_chat = Mock(spec=Chat)
            mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Setup mock structure
            mock_user.id = 12345
            mock_chat.id = 12345
            mock_message.from_user = mock_user
            mock_message.chat = mock_chat
            mock_message.text = "17"  # Under 18
            mock_message.reply_text = Mock()
            mock_update.message = mock_message
            
            # Setup context user_data
            mock_context.user_data = {
                "reg_state": "AGE",
                "reg_data": {}
            }
            
            # Test age rejection
            async def run_test():
                result = await registration.handle_registration_text(mock_update, mock_context)
                
                # Check if reply_text was called with rejection message
                mock_message.reply_text.assert_called_once()
                call_args = mock_message.reply_text.call_args[0][0]
                
                if "18+ only" in call_args and "cannot use this bot" in call_args:
                    return True, "Age rejection message sent correctly"
                else:
                    return False, f"Unexpected rejection message: {call_args}"
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, message = loop.run_until_complete(run_test())
                self.log_result("Age Rejection Logic", success, message)
            finally:
                loop.close()
                
        except Exception as e:
            self.log_result("Age Rejection Logic", False, "Exception occurred", str(e))

    def test_age_agreement_dialog(self):
        """Test age agreement dialog appears for users 18+"""
        try:
            import registration
            from telegram import Update, Message, User, Chat, InlineKeyboardMarkup
            from telegram.ext import ContextTypes
            
            # Create mock objects
            mock_update = Mock(spec=Update)
            mock_message = Mock(spec=Message)
            mock_user = Mock(spec=User)
            mock_chat = Mock(spec=Chat)
            mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Setup mock structure
            mock_user.id = 12345
            mock_chat.id = 12345
            mock_message.from_user = mock_user
            mock_message.chat = mock_chat
            mock_message.text = "25"  # 18+
            mock_message.reply_text = Mock()
            mock_update.message = mock_message
            
            # Setup context user_data
            mock_context.user_data = {
                "reg_state": "AGE",
                "reg_data": {}
            }
            
            # Test age agreement dialog
            async def run_test():
                result = await registration.handle_registration_text(mock_update, mock_context)
                
                # Check if reply_text was called with age verification dialog
                mock_message.reply_text.assert_called_once()
                call_args = mock_message.reply_text.call_args
                message_text = call_args[0][0]
                kwargs = call_args[1] if len(call_args) > 1 else {}
                
                # Check message content
                if ("AGE VERIFICATION" in message_text and 
                    "18+ years old" in message_text and 
                    "False age = Permanent ban" in message_text):
                    
                    # Check if inline keyboard is present
                    if 'reply_markup' in kwargs:
                        reply_markup = kwargs['reply_markup']
                        if isinstance(reply_markup, InlineKeyboardMarkup):
                            # Check if "I Agree (18+)" button exists
                            buttons = reply_markup.inline_keyboard
                            if buttons and len(buttons) > 0 and len(buttons[0]) > 0:
                                button = buttons[0][0]
                                if button.text == "I Agree (18+)" and button.callback_data == "age_agree":
                                    return True, "Age agreement dialog with correct button displayed"
                                else:
                                    return False, f"Incorrect button: text='{button.text}', callback='{button.callback_data}'"
                            else:
                                return False, "No buttons found in reply markup"
                        else:
                            return False, f"Reply markup is not InlineKeyboardMarkup: {type(reply_markup)}"
                    else:
                        return False, "No reply_markup found in response"
                else:
                    return False, f"Age verification dialog content incorrect: {message_text}"
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, message = loop.run_until_complete(run_test())
                self.log_result("Age Agreement Dialog", success, message)
            finally:
                loop.close()
                
        except Exception as e:
            self.log_result("Age Agreement Dialog", False, "Exception occurred", str(e))

    def test_age_agree_callback_handler(self):
        """Test callback handler for 'age_agree' button click"""
        try:
            import registration
            from telegram import Update, CallbackQuery, User, Chat, Message
            from telegram.ext import ContextTypes
            
            # Create mock objects
            mock_update = Mock(spec=Update)
            mock_callback_query = Mock(spec=CallbackQuery)
            mock_user = Mock(spec=User)
            mock_chat = Mock(spec=Chat)
            mock_message = Mock(spec=Message)
            mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            # Setup mock structure
            mock_user.id = 12345
            mock_chat.id = 12345
            mock_message.chat = mock_chat
            mock_callback_query.from_user = mock_user
            mock_callback_query.message = mock_message
            mock_callback_query.data = "age_agree"
            mock_callback_query.answer = Mock()
            mock_callback_query.edit_message_text = Mock()
            mock_update.callback_query = mock_callback_query
            
            # Setup context user_data
            mock_context.user_data = {
                "reg_state": "AGE",
                "reg_data": {"age": 25}
            }
            
            # Mock database connection
            with patch.object(registration, '_conn') as mock_conn:
                mock_connection = Mock()
                mock_cursor = Mock()
                mock_conn.return_value.__enter__.return_value = mock_connection
                mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                
                # Test callback handler
                async def run_test():
                    result = await registration.on_callback(mock_update, mock_context)
                    
                    # Check if answer was called
                    mock_callback_query.answer.assert_called_once()
                    
                    # Check if database update was called
                    mock_cursor.execute.assert_called_once()
                    execute_call = mock_cursor.execute.call_args[0]
                    sql_query = execute_call[0]
                    sql_params = execute_call[1]
                    
                    if ("UPDATE users" in sql_query and 
                        "age_verified=TRUE" in sql_query and 
                        "age_agreement_date=NOW()" in sql_query and
                        sql_params == (12345,)):
                        
                        # Check if edit_message_text was called with success message
                        mock_callback_query.edit_message_text.assert_called_once()
                        edit_call = mock_callback_query.edit_message_text.call_args[0][0]
                        
                        if "Age verification complete" in edit_call and "country" in edit_call:
                            # Check if context state was updated
                            if mock_context.user_data.get("reg_state") == "COUNTRY":
                                return True, "Age agreement callback handled correctly with database update and state transition"
                            else:
                                return False, f"Context state not updated correctly: {mock_context.user_data.get('reg_state')}"
                        else:
                            return False, f"Incorrect success message: {edit_call}"
                    else:
                        return False, f"Database update query incorrect: {sql_query} with params {sql_params}"
                
                # Run async test
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    success, message = loop.run_until_complete(run_test())
                    self.log_result("Age Agree Callback Handler", success, message)
                finally:
                    loop.close()
                    
        except Exception as e:
            self.log_result("Age Agree Callback Handler", False, "Exception occurred", str(e))

    def test_database_update_with_timestamp(self):
        """Test that database is updated with age_verified=TRUE and timestamp"""
        if not self.db_url:
            self.log_result("Database Update with Timestamp", False, "No DATABASE_URL configured")
            return
            
        try:
            import registration
            
            # Create a test user first
            test_user_id = 999999  # Use a unique test ID
            
            with registration._conn() as conn, conn.cursor() as cur:
                # Insert test user
                cur.execute("""
                    INSERT INTO users (tg_user_id, gender, age, country, city) 
                    VALUES (%s, 'test', 25, 'TestCountry', 'TestCity')
                    ON CONFLICT (tg_user_id) DO UPDATE SET 
                        age_verified = FALSE, 
                        age_agreement_date = NULL
                """, (test_user_id,))
                conn.commit()
                
                # Simulate the age agreement update
                cur.execute("""
                    UPDATE users 
                    SET age_verified=TRUE, 
                        age_agreement_date=NOW() 
                    WHERE tg_user_id=%s
                """, (test_user_id,))
                conn.commit()
                
                # Verify the update
                cur.execute("""
                    SELECT age_verified, age_agreement_date 
                    FROM users 
                    WHERE tg_user_id=%s
                """, (test_user_id,))
                result = cur.fetchone()
                
                if result:
                    age_verified, age_agreement_date = result
                    
                    if age_verified is True and age_agreement_date is not None:
                        # Check if timestamp is recent (within last minute)
                        now = datetime.now(timezone.utc)
                        time_diff = now - age_agreement_date.replace(tzinfo=timezone.utc)
                        
                        if time_diff.total_seconds() < 60:
                            self.log_result("Database Update with Timestamp", True, 
                                          f"Database updated correctly: age_verified={age_verified}, timestamp={age_agreement_date}")
                        else:
                            self.log_result("Database Update with Timestamp", False, 
                                          f"Timestamp too old: {time_diff.total_seconds()} seconds")
                    else:
                        self.log_result("Database Update with Timestamp", False, 
                                      f"Incorrect values: age_verified={age_verified}, age_agreement_date={age_agreement_date}")
                else:
                    self.log_result("Database Update with Timestamp", False, "No result returned from database query")
                
                # Clean up test user
                cur.execute("DELETE FROM users WHERE tg_user_id=%s", (test_user_id,))
                conn.commit()
                
        except Exception as e:
            self.log_result("Database Update with Timestamp", False, "Database operation failed", str(e))

    def test_registration_flow_integration(self):
        """Test complete registration flow with age verification"""
        try:
            import registration
            from telegram import Update, Message, User, Chat, CallbackQuery, InlineKeyboardMarkup
            from telegram.ext import ContextTypes
            
            # Test the complete flow: AGE input -> Age agreement -> Country
            test_user_id = 888888
            
            # Step 1: Test age input (18+)
            mock_update1 = Mock(spec=Update)
            mock_message1 = Mock(spec=Message)
            mock_user1 = Mock(spec=User)
            mock_chat1 = Mock(spec=Chat)
            mock_context1 = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            mock_user1.id = test_user_id
            mock_chat1.id = test_user_id
            mock_message1.from_user = mock_user1
            mock_message1.chat = mock_chat1
            mock_message1.text = "22"
            mock_message1.reply_text = Mock()
            mock_update1.message = mock_message1
            
            mock_context1.user_data = {
                "reg_state": "AGE",
                "reg_data": {}
            }
            
            # Step 2: Test age agreement callback
            mock_update2 = Mock(spec=Update)
            mock_callback_query2 = Mock(spec=CallbackQuery)
            mock_user2 = Mock(spec=User)
            mock_chat2 = Mock(spec=Chat)
            mock_message2 = Mock(spec=Message)
            mock_context2 = Mock(spec=ContextTypes.DEFAULT_TYPE)
            
            mock_user2.id = test_user_id
            mock_chat2.id = test_user_id
            mock_message2.chat = mock_chat2
            mock_callback_query2.from_user = mock_user2
            mock_callback_query2.message = mock_message2
            mock_callback_query2.data = "age_agree"
            mock_callback_query2.answer = Mock()
            mock_callback_query2.edit_message_text = Mock()
            mock_update2.callback_query = mock_callback_query2
            
            mock_context2.user_data = {
                "reg_state": "AGE",
                "reg_data": {"age": 22}
            }
            
            async def run_integration_test():
                # Step 1: Handle age input
                await registration.handle_registration_text(mock_update1, mock_context1)
                
                # Verify age agreement dialog was shown
                mock_message1.reply_text.assert_called_once()
                call_args = mock_message1.reply_text.call_args
                message_text = call_args[0][0]
                
                if "AGE VERIFICATION" not in message_text:
                    return False, "Age verification dialog not shown"
                
                # Step 2: Handle age agreement callback
                with patch.object(registration, '_conn') as mock_conn:
                    mock_connection = Mock()
                    mock_cursor = Mock()
                    mock_conn.return_value.__enter__.return_value = mock_connection
                    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
                    
                    await registration.on_callback(mock_update2, mock_context2)
                    
                    # Verify database update
                    mock_cursor.execute.assert_called_once()
                    execute_call = mock_cursor.execute.call_args[0]
                    sql_query = execute_call[0]
                    
                    if "age_verified=TRUE" not in sql_query:
                        return False, "Database not updated with age verification"
                    
                    # Verify state transition to COUNTRY
                    if mock_context2.user_data.get("reg_state") != "COUNTRY":
                        return False, f"State not transitioned to COUNTRY: {mock_context2.user_data.get('reg_state')}"
                    
                    # Verify success message
                    mock_callback_query2.edit_message_text.assert_called_once()
                    edit_call = mock_callback_query2.edit_message_text.call_args[0][0]
                    
                    if "Age verification complete" not in edit_call or "country" not in edit_call:
                        return False, f"Incorrect success message: {edit_call}"
                    
                    return True, "Complete registration flow with age verification working correctly"
            
            # Run async test
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                success, message = loop.run_until_complete(run_integration_test())
                self.log_result("Registration Flow Integration", success, message)
            finally:
                loop.close()
                
        except Exception as e:
            self.log_result("Registration Flow Integration", False, "Exception occurred", str(e))

    def test_edge_cases(self):
        """Test edge cases like invalid age input, boundary values, etc."""
        try:
            import registration
            from telegram import Update, Message, User, Chat
            from telegram.ext import ContextTypes
            
            test_cases = [
                ("abc", "non-numeric input"),
                ("12", "age below minimum (13)"),
                ("100", "age above maximum (99)"),
                ("18", "boundary case - exactly 18"),
                ("17", "boundary case - just under 18")
            ]
            
            results = []
            
            for age_input, description in test_cases:
                # Create mock objects for each test
                mock_update = Mock(spec=Update)
                mock_message = Mock(spec=Message)
                mock_user = Mock(spec=User)
                mock_chat = Mock(spec=Chat)
                mock_context = Mock(spec=ContextTypes.DEFAULT_TYPE)
                
                mock_user.id = 12345
                mock_chat.id = 12345
                mock_message.from_user = mock_user
                mock_message.chat = mock_chat
                mock_message.text = age_input
                mock_message.reply_text = Mock()
                mock_update.message = mock_message
                
                mock_context.user_data = {
                    "reg_state": "AGE",
                    "reg_data": {}
                }
                
                async def run_edge_case_test():
                    try:
                        result = await registration.handle_registration_text(mock_update, mock_context)
                        
                        # Check response based on input
                        mock_message.reply_text.assert_called()
                        call_args = mock_message.reply_text.call_args[0][0]
                        
                        if age_input == "abc":
                            # Should ask for numeric input
                            return "number" in call_args.lower()
                        elif age_input in ["12", "100"]:
                            # Should ask for valid range
                            return "between" in call_args.lower() or "13" in call_args
                        elif age_input == "17":
                            # Should reject with 18+ message
                            return "18+ only" in call_args
                        elif age_input == "18":
                            # Should show age verification dialog
                            return "AGE VERIFICATION" in call_args
                        
                        return False
                        
                    except Exception as e:
                        return f"Exception: {str(e)}"
                
                # Run async test
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(run_edge_case_test())
                    results.append(f"{description}: {'✅' if result is True else '❌' if result is False else result}")
                finally:
                    loop.close()
            
            # Check if all edge cases passed
            failed_cases = [r for r in results if '❌' in r or 'Exception' in r]
            
            if not failed_cases:
                self.log_result("Edge Cases", True, f"All edge cases handled correctly: {', '.join(results)}")
            else:
                self.log_result("Edge Cases", False, f"Some edge cases failed: {', '.join(failed_cases)}")
                
        except Exception as e:
            self.log_result("Edge Cases", False, "Exception occurred", str(e))

    def run_all_tests(self):
        """Run all age verification tests"""
        print("🧪 TELEGRAM BOT AGE VERIFICATION TESTING")
        print("=" * 60)
        print()
        
        # Test 1: Module Import
        self.test_module_import()
        
        # Test 2: Database Schema
        self.test_age_verification_columns_exist()
        
        # Test 3: Age Rejection Logic
        self.test_age_rejection_logic()
        
        # Test 4: Age Agreement Dialog
        self.test_age_agreement_dialog()
        
        # Test 5: Callback Handler
        self.test_age_agree_callback_handler()
        
        # Test 6: Database Update
        self.test_database_update_with_timestamp()
        
        # Test 7: Integration Test
        self.test_registration_flow_integration()
        
        # Test 8: Edge Cases
        self.test_edge_cases()
        
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
    tester = TelegramBotAgeVerificationTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 ALL TESTS PASSED! Age verification functionality is working correctly.")
    else:
        print("⚠️  SOME TESTS FAILED. Please review the implementation.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())