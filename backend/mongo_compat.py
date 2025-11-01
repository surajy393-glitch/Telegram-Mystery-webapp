"""
MongoDB Compatibility Layer for PostgreSQL
This module provides MongoDB-like syntax for PostgreSQL operations
to minimize changes to existing server.py code
"""
import asyncpg
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from db_postgres import get_pool

class Collection:
    """Simulates MongoDB collection with PostgreSQL backend"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    async def find_one(self, filter_dict: Dict[str, Any], projection: Dict[str, Any] = None) -> Optional[Dict]:
        """Find single document matching filter (projection parameter ignored for now)"""
        pool = await get_pool()
        
        # Use the same advanced query building logic as Cursor class
        where_clause, values = self._build_where_clause(filter_dict)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause} LIMIT 1"
        
        try:
            row = await pool.fetchrow(query, *values)
            if row:
                result = dict(row)
                # Convert snake_case back to camelCase for compatibility
                return self._snake_to_camel(result)
            return None
        except Exception as e:
            print(f"Error in find_one: {e}")
            print(f"Query: {query}")
            print(f"Values: {values}")
            raise
    
    def _build_where_clause(self, filter_dict: Dict[str, Any], param_num_start: int = 1):
        """Build WHERE clause from MongoDB-style filter (shared with Cursor class)"""
        where_parts = []
        values = []
        param_num = param_num_start
        
        for key, value in filter_dict.items():
            # Handle special MongoDB operators
            if key == '$and':
                # Handle $and operator
                and_parts = []
                for sub_filter in value:
                    sub_where, sub_values = self._build_where_clause(sub_filter, param_num)
                    and_parts.append(f"({sub_where})")
                    values.extend(sub_values)
                    param_num += len(sub_values)
                where_parts.append(f"({' AND '.join(and_parts)})")
            elif key == '$or':
                # Handle $or operator
                or_parts = []
                for sub_filter in value:
                    sub_where, sub_values = self._build_where_clause(sub_filter, param_num)
                    or_parts.append(f"({sub_where})")
                    values.extend(sub_values)
                    param_num += len(sub_values)
                where_parts.append(f"({' OR '.join(or_parts)})")
            else:
                # Regular field
                db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
                
                # Special handling for ID fields - convert string to int for PostgreSQL
                if db_key in ['id', 'user_id'] and isinstance(value, str):
                    try:
                        value = int(value)
                    except (ValueError, TypeError):
                        pass
                
                # Handle special operators
                if isinstance(value, dict):
                    for op, op_value in value.items():
                        if op == '$ne':
                            # Also convert string to int for $ne operator
                            if db_key in ['id', 'user_id'] and isinstance(op_value, str):
                                try:
                                    op_value = int(op_value)
                                except (ValueError, TypeError):
                                    pass
                            where_parts.append(f"{db_key} != ${param_num}")
                            values.append(op_value)
                            param_num += 1
                        elif op == '$nin':
                            if op_value:  # Only add if list is not empty
                                # Convert string IDs to integers for user_id/id fields
                                if db_key in ['id', 'user_id']:
                                    converted_values = []
                                    for val in op_value:
                                        try:
                                            converted_values.append(int(val) if isinstance(val, str) else val)
                                        except (ValueError, TypeError):
                                            converted_values.append(val)
                                    op_value = converted_values
                                
                                placeholders = ','.join([f'${i}' for i in range(param_num, param_num + len(op_value))])
                                where_parts.append(f"{db_key} NOT IN ({placeholders})")
                                values.extend(op_value)
                                param_num += len(op_value)
                        elif op == '$in':
                            if op_value:  # Only add if list is not empty
                                # Convert string IDs to integers for user_id/id fields
                                if db_key in ['id', 'user_id']:
                                    converted_values = []
                                    for val in op_value:
                                        try:
                                            converted_values.append(int(val) if isinstance(val, str) else val)
                                        except (ValueError, TypeError):
                                            converted_values.append(val)
                                    op_value = converted_values
                                
                                placeholders = ','.join([f'${i}' for i in range(param_num, param_num + len(op_value))])
                                where_parts.append(f"{db_key} IN ({placeholders})")
                                values.extend(op_value)
                                param_num += len(op_value)
                        elif op == '$regex':
                            where_parts.append(f"{db_key} ~* ${param_num}")
                            values.append(op_value)
                            param_num += 1
                else:
                    where_parts.append(f"{db_key} = ${param_num}")
                    values.append(value)
                    param_num += 1
        
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        return where_clause, values
    
    def find(self, filter_dict: Dict[str, Any] = None):
        """Find multiple documents - returns a cursor-like object"""
        if filter_dict is None:
            filter_dict = {}
        return Cursor(self.table_name, filter_dict)
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None):
        """Count documents matching filter"""
        pool = await get_pool()
        
        if filter_dict is None or not filter_dict:
            # Simple count all
            query = f"SELECT COUNT(*) FROM {self.table_name}"
            row = await pool.fetchrow(query)
            return row[0]
        
        # Build WHERE clause for count with filter
        cursor = Cursor(self.table_name, filter_dict)
        where_clause, values = cursor._build_where_clause(filter_dict)
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
        
        try:
            row = await pool.fetchrow(query, *values)
            return row[0]
        except Exception as e:
            print(f"Error in count_documents: {e}")
            print(f"Query: {query}")
            return 0
    
    async def insert_one(self, document: Dict[str, Any]):
        """Insert single document"""
        pool = await get_pool()
        
        # Define valid columns for each table
        table_columns = {
            'webapp_users': {
                'id', 'full_name', 'username', 'email', 'mobile_number', 'password',
                'age', 'gender', 'city', 'interests', 'email_verified', 'mobile_verified',
                'profile_photo_url', 'profile_photo_file_id', 'bio',
                'is_private', 'is_verified', 'verify_status', 'verify_method',
                'verified_name', 'verify_code', 'verify_code_expires_at',
                'verify_code_photo_url', 'verify_photo_file',
                'followers_count', 'following_count',
                'created_at', 'updated_at', 'username_changed_at',
                'telegram_id', 'is_premium', 'is_founder', 'violations_count',
                'auth_method', 'verification_pathway', 'verified_at',
                'country', 'is_online', 'last_seen',
                'telegram_username', 'telegram_first_name', 'telegram_last_name',
                'telegram_photo_url', 'appear_in_search', 'allow_direct_messages',
                'show_online_status', 'allow_tagging', 'allow_story_replies',
                'show_vibe_score', 'push_notifications', 'email_notifications',
                'personality_answers', 'last_username_change'
            },
            'webapp_posts': {
                'id', 'user_id', 'username', 'user_profile_image', 'media_type',
                'media_url', 'caption', 'likes', 'comments', 'is_archived',
                'likes_hidden', 'comments_disabled', 'is_pinned', 'created_at',
                'telegram_file_id', 'telegram_file_path', 'likes_count', 'comments_count'
            },
            'webapp_stories': {
                'id', 'user_id', 'username', 'user_profile_image', 'media_type',
                'media_url', 'caption', 'likes', 'viewers', 'is_archived',
                'created_at', 'expires_at', 'telegram_file_id', 'telegram_file_path',
                'views_count'
            },
            'webapp_notifications': {
                'id', 'user_id', 'type', 'actor_id', 'post_id', 'comment_id',
                'is_read', 'created_at'
            }
        }
        
        # Get valid columns for this table
        valid_columns = table_columns.get(self.table_name, set())
        
        # Field mappings from MongoDB/App names to PostgreSQL column names
        field_mappings = {
            # User fields
            'password_hash': 'password',
            'profileImage': 'profile_photo_url',
            'profile_image': 'profile_photo_url',
            'phoneVerified': 'mobile_verified',
            'phone_verified': 'mobile_verified',
            'fullName': 'full_name',
            'mobileNumber': 'mobile_number',
            'authMethod': 'auth_method',
            'emailVerified': 'email_verified',
            'violationsCount': 'violations_count',
            'isPrivate': 'is_private',
            'isVerified': 'is_verified',
            'isPremium': 'is_premium',
            'isOnline': 'is_online',
            'lastSeen': 'last_seen',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'telegramId': 'telegram_id',
            'telegramUsername': 'telegram_username',
            'telegramFirstName': 'telegram_first_name',
            'telegramLastName': 'telegram_last_name',
            'telegramPhotoUrl': 'telegram_photo_url',
            'appearInSearch': 'appear_in_search',
            'allowDirectMessages': 'allow_direct_messages',
            'showOnlineStatus': 'show_online_status',
            'allowTagging': 'allow_tagging',
            'allowStoryReplies': 'allow_story_replies',
            'showVibeScore': 'show_vibe_score',
            'pushNotifications': 'push_notifications',
            'emailNotifications': 'email_notifications',
            'lastUsernameChange': 'last_username_change',
            'personalityAnswers': 'personality_answers',
            'verifiedAt': 'verified_at',
            'verificationPathway': 'verification_pathway',
            'isFounder': 'is_founder',
            # Post/Story fields
            'userId': 'user_id',
            'userProfileImage': 'user_profile_image',
            'mediaType': 'media_type',
            'mediaUrl': 'media_url',
            'isArchived': 'is_archived',
            'likesHidden': 'likes_hidden',
            'commentsDisabled': 'comments_disabled',
            'isPinned': 'is_pinned',
            'telegramFileId': 'telegram_file_id',
            'telegramFilePath': 'telegram_file_path',
            'likesCount': 'likes_count',
            'commentsCount': 'comments_count',
            'expiresAt': 'expires_at',
            'viewsCount': 'views_count'
        }
        
        # Convert camelCase keys to snake_case
        db_document = {}
        
        for key, value in document.items():
            # First check if there's a specific mapping
            if key in field_mappings:
                db_key = field_mappings[key]
            else:
                # Convert camelCase to snake_case
                db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Skip id - PostgreSQL auto-generates it
            if db_key == 'id':
                continue
            
            # Skip fields that don't exist in PostgreSQL
            if db_key not in valid_columns:
                continue
            
            # Special handling for ID fields - convert string to int for PostgreSQL
            if db_key in ['id', 'user_id'] and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass  # Keep as string if conversion fails
            
            # Convert lists/dicts to JSON (datetime objects are handled directly by asyncpg)
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            
            db_document[db_key] = value
        
        # Build INSERT query
        columns = list(db_document.keys())
        placeholders = [f'${i+1}' for i in range(len(columns))]
        values = [db_document[col] for col in columns]
        
        query = f"""
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        """
        
        try:
            inserted_id = await pool.fetchval(query, *values)
            return {'inserted_id': inserted_id}
        except Exception as e:
            print(f"Error in insert_one: {e}")
            print(f"Query: {query}")
            print(f"Values: {values}")
            raise
    
    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """Update single document"""
        pool = await get_pool()
        
        # Field mappings from MongoDB/App names to PostgreSQL column names
        field_mappings = {
            'password_hash': 'password',
            'profileImage': 'profile_photo_url',
            'profile_image': 'profile_photo_url',
            'phoneVerified': 'mobile_verified',
            'phone_verified': 'mobile_verified',
            'fullName': 'full_name',
            'mobileNumber': 'mobile_number',
            'authMethod': 'auth_method',
            'emailVerified': 'email_verified',
            'violationsCount': 'violations_count',
            'isPrivate': 'is_private',
            'isVerified': 'is_verified',
            'isPremium': 'is_premium',
            'isOnline': 'is_online',
            'lastSeen': 'last_seen',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'telegramId': 'telegram_id',
            'telegramUsername': 'telegram_username',
            'telegramFirstName': 'telegram_first_name',
            'telegramLastName': 'telegram_last_name',
            'telegramPhotoUrl': 'telegram_photo_url',
            'appearInSearch': 'appear_in_search',
            'allowDirectMessages': 'allow_direct_messages',
            'showOnlineStatus': 'show_online_status',
            'allowTagging': 'allow_tagging',
            'allowStoryReplies': 'allow_story_replies',
            'showVibeScore': 'show_vibe_score',
            'pushNotifications': 'push_notifications',
            'emailNotifications': 'email_notifications',
            'lastUsernameChange': 'last_username_change',
            'personalityAnswers': 'personality_answers',
            'verifiedAt': 'verified_at',
            'verificationPathway': 'verification_pathway',
            'isFounder': 'is_founder',
            'city': 'city'  # Added city field mapping
        }
        
        # Extract $set operator if present
        if '$set' in update_dict:
            update_fields = update_dict['$set']
        else:
            update_fields = update_dict
        
        # Build SET clause
        set_parts = []
        values = []
        param_num = 1
        
        for key, value in update_fields.items():
            # First check if there's a specific mapping
            if key in field_mappings:
                db_key = field_mappings[key]
            else:
                # Convert camelCase to snake_case
                db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Convert lists/dicts to JSON
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            
            set_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1
        
        # Build WHERE clause
        where_parts = []
        for key, value in filter_dict.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Special handling for ID fields - convert string to int for PostgreSQL
            if db_key in ['id', 'user_id'] and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
                    
            where_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1
        
        set_clause = ", ".join(set_parts)
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"
        
        try:
            await pool.execute(query, *values)
            return {'modified_count': 1}
        except Exception as e:
            print(f"Error in update_one: {e}")
            print(f"Query: {query}")
            print(f"Values: {values}")
            raise
    
    async def delete_one(self, filter_dict: Dict[str, Any]):
        """Delete single document"""
        pool = await get_pool()
        
        # Build WHERE clause
        where_parts = []
        values = []
        param_num = 1
        
        for key, value in filter_dict.items():
            # Convert camelCase keys into snake_case to match DB columns
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')

            # Convert string IDs into integers for numeric primary keys.
            # Without this conversion PostgreSQL will not match the row and deletion will fail.
            # Similar logic is used in update_one() for id/user_id fields.
            if db_key in ['id', 'user_id'] and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    # If conversion fails, leave the value unchanged
                    pass

            where_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1
        
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        query = f"DELETE FROM {self.table_name} WHERE {where_clause}"
        
        try:
            await pool.execute(query, *values)
            return {'deleted_count': 1}
        except Exception as e:
            print(f"Error in delete_one: {e}")
            raise
    
    async def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]):
        """
        Update multiple rows matching filter_dict.
        Currently supports only '$set' updates. Unsupported operators are ignored.
        """
        pool = await get_pool()

        # Determine the fields to update
        if '$set' in update_dict:
            updates = update_dict['$set']
        else:
            updates = update_dict

        # Build SET clause
        set_parts = []
        values = []
        param_num = 1

        # Use same field_mappings as update_one
        field_mappings = {
            'password_hash': 'password',
            'profileImage': 'profile_photo_url',
            'profile_image': 'profile_photo_url',
            'phoneVerified': 'mobile_verified',
            'phone_verified': 'mobile_verified',
            'fullName': 'full_name',
            'mobileNumber': 'mobile_number',
            'authMethod': 'auth_method',
            'emailVerified': 'email_verified',
            'violationsCount': 'violations_count',
            'isPrivate': 'is_private',
            'isVerified': 'is_verified',
            'isPremium': 'is_premium',
            'isOnline': 'is_online',
            'lastSeen': 'last_seen',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
            'telegramId': 'telegram_id',
            'telegramUsername': 'telegram_username',
            'telegramFirstName': 'telegram_first_name',
            'telegramLastName': 'telegram_last_name',
            'telegramPhotoUrl': 'telegram_photo_url',
            'appearInSearch': 'appear_in_search',
            'allowDirectMessages': 'allow_direct_messages',
            'showOnlineStatus': 'show_online_status',
            'allowTagging': 'allow_tagging',
            'allowStoryReplies': 'allow_story_replies',
            'showVibeScore': 'show_vibe_score',
            'pushNotifications': 'push_notifications',
            'emailNotifications': 'email_notifications',
            'lastUsernameChange': 'last_username_change',
            'personalityAnswers': 'personality_answers',
            'verifiedAt': 'verified_at',
            'verificationPathway': 'verification_pathway',
            'isFounder': 'is_founder',
            'city': 'city'  # Added city field mapping
        }

        for key, value in updates.items():
            if key in field_mappings:
                db_key = field_mappings[key]
            else:
                db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            # Convert lists/dicts to JSON
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            set_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1

        if not set_parts:
            return {'modified_count': 0}

        # Build WHERE clause
        where_parts = []
        for key, value in filter_dict.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            # Special handling for ID - convert string to int
            if db_key == 'id' and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
            where_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1

        set_clause = ", ".join(set_parts)
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {where_clause}"

        try:
            await pool.execute(query, *values)
            return {'modified_count': 'unknown'}
        except Exception as e:
            print(f"Error in update_many: {e}")
            print(f"Query: {query}")
            print(f"Values: {values}")
            raise

    async def delete_many(self, filter_dict: Dict[str, Any]):
        """
        Delete multiple rows matching filter_dict.
        """
        pool = await get_pool()

        where_parts = []
        values = []
        param_num = 1
        for key, value in filter_dict.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            # Special handling for ID - convert string to int
            if db_key == 'id' and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
            where_parts.append(f"{db_key} = ${param_num}")
            values.append(value)
            param_num += 1

        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        query = f"DELETE FROM {self.table_name} WHERE {where_clause}"

        try:
            await pool.execute(query, *values)
            return {'deleted_count': 'unknown'}
        except Exception as e:
            print(f"Error in delete_many: {e}")
            raise
    
    async def count_documents(self, filter_dict: Dict[str, Any] = None):
        """Count documents matching filter"""
        if filter_dict is None:
            filter_dict = {}
        
        pool = await get_pool()
        
        # Build WHERE clause
        where_parts = []
        values = []
        param_num = 1
        
        for key, value in filter_dict.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Special handling for ID fields - convert string to int for PostgreSQL
            if db_key in ['id', 'user_id'] and isinstance(value, str):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    pass
            
            # Handle special operators
            if isinstance(value, dict):
                for op, op_value in value.items():
                    if op == '$ne':
                        where_parts.append(f"{db_key} != ${param_num}")
                        values.append(op_value)
                        param_num += 1
            else:
                where_parts.append(f"{db_key} = ${param_num}")
                values.append(value)
                param_num += 1
        
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_clause}"
        
        try:
            count = await pool.fetchval(query, *values)
            return count
        except Exception as e:
            print(f"Error in count_documents: {e}")
            raise
    
    def _snake_to_camel(self, data: Dict) -> Dict:
        """Convert snake_case keys to camelCase with special mappings"""
        # Special field mappings for compatibility
        field_mappings = {
            'password': 'password_hash',  # PostgreSQL uses 'password', MongoDB used 'password_hash'
            'full_name': 'fullName',
            'profile_photo_url': 'profileImage',
            'telegram_id': 'telegramId',
            'telegram_username': 'telegramUsername',
            'telegram_first_name': 'telegramFirstName',
            'telegram_last_name': 'telegramLastName',
            'telegram_photo_url': 'telegramPhotoUrl',
            'auth_method': 'authMethod',
            'is_premium': 'isPremium',
            'is_private': 'isPrivate',
            'is_verified': 'isVerified',
            'verified_at': 'verifiedAt',
            'verification_pathway': 'verificationPathway',
            'is_founder': 'isFounder',
            'email_verified': 'emailVerified',
            'mobile_verified': 'phoneVerified',
            'violations_count': 'violationsCount',
            'mobile_number': 'mobileNumber',
            'appear_in_search': 'appearInSearch',
            'allow_direct_messages': 'allowDirectMessages',
            'show_online_status': 'showOnlineStatus',
            'allow_tagging': 'allowTagging',
            'allow_story_replies': 'allowStoryReplies',
            'show_vibe_score': 'showVibeScore',
            'push_notifications': 'pushNotifications',
            'email_notifications': 'emailNotifications',
            'last_username_change': 'lastUsernameChange',
            'is_online': 'isOnline',
            'last_seen': 'lastSeen',
            'created_at': 'createdAt',
            'updated_at': 'updatedAt'
        }
        
        result = {}
        for key, value in data.items():
            # Use special mapping if available
            if key in field_mappings:
                camel_key = field_mappings[key]
            else:
                # Convert snake_case to camelCase
                parts = key.split('_')
                camel_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            result[camel_key] = value
        return result


class Cursor:
    """Simulates MongoDB cursor for find() operations"""
    
    def __init__(self, table_name: str, filter_dict: Dict[str, Any]):
        self.table_name = table_name
        self.filter_dict = filter_dict
        self._sort_field = None
        self._sort_order = None
        self._limit_value = None
        self._skip_value = 0
    
    def sort(self, field: str, order: int = 1):
        """Sort results (1 = ascending, -1 = descending)"""
        self._sort_field = field
        self._sort_order = "ASC" if order == 1 else "DESC"
        return self
    
    def limit(self, count: int):
        """Limit number of results"""
        self._limit_value = count
        return self
    
    def skip(self, count: int):
        """Skip number of results (for pagination)"""
        self._skip_value = count
        return self
    
    async def to_list(self, length: int = None):
        """Convert cursor to list"""
        pool = await get_pool()
        
        # Build WHERE clause with support for complex queries
        where_clause, values = self._build_where_clause(self.filter_dict)
        
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        # Add sorting
        if self._sort_field:
            db_field = ''.join(['_' + c.lower() if c.isupper() else c for c in self._sort_field]).lstrip('_')
            query += f" ORDER BY {db_field} {self._sort_order}"
        
        # Add limit and offset
        limit = self._limit_value or length
        if limit:
            query += f" LIMIT {limit}"
        if self._skip_value:
            query += f" OFFSET {self._skip_value}"
        
        try:
            rows = await pool.fetch(query, *values)
            results = []
            for row in rows:
                result = dict(row)
                # Convert snake_case back to camelCase
                results.append(self._snake_to_camel(result))
            return results
        except Exception as e:
            print(f"Error in to_list: {e}")
            print(f"Query: {query}")
            print(f"Values: {values}")
            raise
    
    def _build_where_clause(self, filter_dict: Dict[str, Any], param_num_start: int = 1):
        """Build WHERE clause from MongoDB-style filter"""
        # Create a temporary Collection instance to use its _build_where_clause method
        temp_collection = Collection(self.table_name)
        return temp_collection._build_where_clause(filter_dict, param_num_start)
    
    def _snake_to_camel(self, data: Dict) -> Dict:
        """Convert snake_case keys to camelCase with special mappings"""
        # Special field mappings for compatibility
        field_mappings = {
            'password': 'password_hash',  # PostgreSQL uses 'password', MongoDB used 'password_hash'
            'full_name': 'fullName',
            'profile_photo_url': 'profileImage',
            'telegram_id': 'telegramId',
            'telegram_username': 'telegramUsername',
            'telegram_first_name': 'telegramFirstName',
            'telegram_last_name': 'telegramLastName',
            'telegram_photo_url': 'telegramPhotoUrl',
            'auth_method': 'authMethod',
            'is_premium': 'isPremium',
            'is_private': 'isPrivate',
            'is_verified': 'isVerified',
            'verified_at': 'verifiedAt',
            'verification_pathway': 'verificationPathway',
            'is_founder': 'isFounder',
            'email_verified': 'emailVerified',
            'mobile_verified': 'phoneVerified',
            'violations_count': 'violationsCount',
            'mobile_number': 'mobileNumber',
            'appear_in_search': 'appearInSearch',
            'allow_direct_messages': 'allowDirectMessages',
            'show_online_status': 'showOnlineStatus',
            'allow_tagging': 'allowTagging',
            'allow_story_replies': 'allowStoryReplies',
            'show_vibe_score': 'showVibeScore',
            'push_notifications': 'pushNotifications',
            'email_notifications': 'emailNotifications',
            'last_username_change': 'lastUsernameChange',
            'is_online': 'isOnline',
            'last_seen': 'lastSeen',
            'created_at': 'createdAt',
            'updated_at': 'updatedAt'
        }
        
        result = {}
        for key, value in data.items():
            # Use special mapping if available
            if key in field_mappings:
                camel_key = field_mappings[key]
            else:
                # Convert snake_case to camelCase
                parts = key.split('_')
                camel_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            result[camel_key] = value
        return result


class Database:
    """Simulates MongoDB database with collections"""
    
    def __init__(self):
        self.users = Collection("webapp_users")
        self.posts = Collection("webapp_posts")
        self.stories = Collection("webapp_stories")
        self.notifications = Collection("webapp_notifications")
        self.verification_codes = Collection("webapp_verification_codes")
        self.violations = Collection("webapp_violations")  # Add violations collection
        # Add more collections as needed
    
    async def create_user(self, user_data: Dict[str, Any]):
        """Insert a new user via the users collection."""
        result = await self.users.insert_one(user_data)
        # insert_one returns {'inserted_id': <int>}
        return result["inserted_id"]


# Create single database instance
db = Database()
