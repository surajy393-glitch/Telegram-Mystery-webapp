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
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict]:
        """Find single document matching filter"""
        pool = await get_pool()
        
        # Build WHERE clause
        where_parts = []
        values = []
        param_num = 1
        
        for key, value in filter_dict.items():
            # Convert camelCase to snake_case
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Handle special operators
            if isinstance(value, dict):
                for op, op_value in value.items():
                    if op == '$ne':
                        where_parts.append(f"{db_key} != ${param_num}")
                        values.append(op_value)
                        param_num += 1
                    elif op == '$in':
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
    
    async def find(self, filter_dict: Dict[str, Any] = None):
        """Find multiple documents - returns a cursor-like object"""
        if filter_dict is None:
            filter_dict = {}
        return Cursor(self.table_name, filter_dict)
    
    async def insert_one(self, document: Dict[str, Any]):
        """Insert single document"""
        pool = await get_pool()
        
        # Convert camelCase keys to snake_case
        db_document = {}
        has_custom_id = 'id' in document
        
        for key, value in document.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Special case: password_hash -> password (PostgreSQL uses 'password')
            if db_key == 'password_hash':
                db_key = 'password'
            
            # Convert lists/dicts to JSON
            if isinstance(value, (list, dict)):
                value = json.dumps(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            
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
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
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
    
    def sort(self, field: str, order: int = 1):
        """Sort results (1 = ascending, -1 = descending)"""
        self._sort_field = field
        self._sort_order = "ASC" if order == 1 else "DESC"
        return self
    
    def limit(self, count: int):
        """Limit number of results"""
        self._limit_value = count
        return self
    
    async def to_list(self, length: int = None):
        """Convert cursor to list"""
        pool = await get_pool()
        
        # Build WHERE clause
        where_parts = []
        values = []
        param_num = 1
        
        for key, value in self.filter_dict.items():
            db_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
            
            # Handle special operators
            if isinstance(value, dict):
                for op, op_value in value.items():
                    if op == '$ne':
                        where_parts.append(f"{db_key} != ${param_num}")
                        values.append(op_value)
                        param_num += 1
                    elif op == '$in':
                        placeholders = ','.join([f'${i}' for i in range(param_num, param_num + len(op_value))])
                        where_parts.append(f"{db_key} IN ({placeholders})")
                        values.extend(op_value)
                        param_num += len(op_value)
            else:
                where_parts.append(f"{db_key} = ${param_num}")
                values.append(value)
                param_num += 1
        
        where_clause = " AND ".join(where_parts) if where_parts else "TRUE"
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        
        # Add sorting
        if self._sort_field:
            db_field = ''.join(['_' + c.lower() if c.isupper() else c for c in self._sort_field]).lstrip('_')
            query += f" ORDER BY {db_field} {self._sort_order}"
        
        # Add limit
        limit = self._limit_value or length
        if limit:
            query += f" LIMIT {limit}"
        
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


class Database:
    """Simulates MongoDB database with collections"""
    
    def __init__(self):
        self.users = Collection("webapp_users")
        self.posts = Collection("webapp_posts")
        self.stories = Collection("webapp_stories")
        self.notifications = Collection("webapp_notifications")
        self.verification_codes = Collection("webapp_verification_codes")
        # Add more collections as needed


# Create single database instance
db = Database()
