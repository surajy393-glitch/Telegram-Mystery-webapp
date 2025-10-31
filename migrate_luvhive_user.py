"""
Migrate only Luvhive user from MongoDB to PostgreSQL
Clean slate - no followers, following, posts, stories, or notifications
"""
import asyncio
import asyncpg
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def migrate_luvhive_user():
    """Migrate Luvhive user to PostgreSQL"""
    
    # Load user data
    with open('/app/luvhive_user_data.json', 'r') as f:
        user_data = json.load(f)
    
    print("=" * 70)
    print("POSTGRESQL MIGRATION - LUVHIVE USER ONLY")
    print("=" * 70)
    
    # Connect to PostgreSQL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment")
        return
    
    print(f"\n📡 Connecting to PostgreSQL...")
    
    try:
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to PostgreSQL")
        
        # Check if user already exists
        existing_user = await conn.fetchrow(
            "SELECT id, username FROM webapp_users WHERE username = $1",
            user_data['username']
        )
        
        if existing_user:
            print(f"\n⚠️  User '{user_data['username']}' already exists (ID: {existing_user['id']})")
            print("   Updating existing user...")
            
            # Update existing user
            await conn.execute("""
                UPDATE webapp_users SET
                    email = $1,
                    full_name = $2,
                    age = $3,
                    gender = $4,
                    bio = $5,
                    profile_photo_url = $6,
                    is_premium = $7,
                    is_verified = $8,
                    is_private = $9,
                    country = $10,
                    telegram_id = $11,
                    auth_method = $12,
                    password = $13,
                    email_verified = $14,
                    mobile_verified = $15,
                    violations_count = $16,
                    mobile_number = $17,
                    updated_at = NOW()
                WHERE username = $18
            """,
                user_data.get('email'),
                user_data.get('fullName'),
                user_data.get('age'),
                user_data.get('gender'),
                user_data.get('bio', ''),
                user_data.get('profileImage'),
                user_data.get('isPremium', False),
                user_data.get('isVerified', False),
                user_data.get('isPrivate', False),
                user_data.get('country'),
                user_data.get('telegramId'),
                user_data.get('authMethod', 'password'),
                user_data.get('password_hash'),
                user_data.get('emailVerified', True),
                user_data.get('phoneVerified', False),
                user_data.get('violationsCount', 0),
                user_data.get('mobileNumber'),
                user_data['username']
            )
            
            user_id = existing_user['id']
            print(f"✅ Updated user '{user_data['username']}' (ID: {user_id})")
            
        else:
            # Insert new user
            print(f"\n📝 Creating new user '{user_data['username']}'...")
            
            user_id = await conn.fetchval("""
                INSERT INTO webapp_users (
                    username, email, full_name, age, gender, bio,
                    profile_photo_url, is_premium, is_verified, is_private,
                    country, telegram_id, auth_method, password,
                    email_verified, mobile_verified, violations_count,
                    mobile_number, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
                RETURNING id
            """,
                user_data['username'],
                user_data.get('email'),
                user_data['fullName'],
                user_data['age'],
                user_data['gender'],
                user_data.get('bio', ''),
                user_data.get('profileImage'),
                user_data.get('isPremium', False),
                user_data.get('isVerified', False),
                user_data.get('isPrivate', False),
                user_data.get('country'),
                user_data.get('telegramId'),
                user_data.get('authMethod', 'password'),
                user_data.get('password_hash'),
                user_data.get('emailVerified', True),
                user_data.get('phoneVerified', False),
                user_data.get('violationsCount', 0),
                user_data.get('mobileNumber'),
                user_data.get('createdAt', datetime.now().isoformat())
            )
            
            print(f"✅ Created user '{user_data['username']}' (ID: {user_id})")
        
        # Verify the user data
        print("\n" + "=" * 70)
        print("VERIFICATION - USER DATA IN POSTGRESQL")
        print("=" * 70)
        
        migrated_user = await conn.fetchrow(
            "SELECT * FROM webapp_users WHERE id = $1", user_id
        )
        
        if migrated_user:
            print(f"✅ Username: {migrated_user['username']}")
            print(f"✅ Email: {migrated_user['email']}")
            print(f"✅ Full Name: {migrated_user['full_name']}")
            print(f"✅ Profile Photo: {'Yes' if migrated_user['profile_photo_url'] else 'No'}")
            print(f"✅ Is Premium: {migrated_user['is_premium']}")
            print(f"✅ Is Verified: {migrated_user['is_verified']}")
            print(f"✅ Telegram ID: {migrated_user['telegram_id']}")
            print(f"✅ Country: {migrated_user['country']}")
            print(f"✅ Bio: {migrated_user['bio'][:50]}..." if migrated_user['bio'] else "✅ Bio: None")
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE - LUVHIVE USER MIGRATED SUCCESSFULLY")
        print("=" * 70)
        print("\nNOTE: Clean slate - no followers, following, posts, stories, or notifications")
        print("      MongoDB remains untouched as backup")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(migrate_luvhive_user())
