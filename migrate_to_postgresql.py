#!/usr/bin/env python3
"""
Complete MongoDB to PostgreSQL Migration Script
Migrates ONLY Luvhive user and related data
"""
import psycopg2
from pymongo import MongoClient
import os
import json
from datetime import datetime

# Database connections
PG_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_oVJba7TZXiW3@ep-lingering-sun-afnijqh1.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require")
MONGO_URL = "mongodb://localhost:27017"

def migrate_luvhive_user():
    """Migrate Luvhive user to PostgreSQL webapp_users table"""
    print("\n🔄 Step 1: Migrating Luvhive user...")
    
    pg_conn = psycopg2.connect(PG_URL)
    pg_cur = pg_conn.cursor()
    mongo_client = MongoClient(MONGO_URL)
    mongo_db = mongo_client.luvhive_database
    
    # Get Luvhive user from MongoDB
    luvhive = mongo_db.users.find_one({"username": "Luvhive"})
    
    if not luvhive:
        print("❌ Luvhive user not found!")
        return False
    
    # Delete all existing webapp_users
    pg_cur.execute("DELETE FROM webapp_users")
    print(f"   Deleted all existing webapp_users")
    
    # Insert Luvhive user
    pg_cur.execute("""
        INSERT INTO webapp_users (
            id, full_name, username, email, mobile_number, password,
            age, gender, city, interests, bio, profile_image,
            country, is_premium, is_verified, is_founder,
            email_verified, phone_verified, telegram_id,
            violations_count, auth_method, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s
        )
    """, (
        1,  # Auto-increment ID
        luvhive.get('fullName', 'LuvHive'),
        luvhive.get('username'),
        luvhive.get('email'),
        luvhive.get('mobileNumber'),
        luvhive.get('password_hash'),
        luvhive.get('age'),
        luvhive.get('gender'),
        luvhive.get('city'),
        json.dumps(luvhive.get('interests', [])),
        luvhive.get('bio', ''),
        luvhive.get('profileImage'),
        luvhive.get('country', 'India'),
        luvhive.get('isPremium', False),
        luvhive.get('isVerified', False),
        luvhive.get('isFounder', False),
        luvhive.get('emailVerified', True),
        luvhive.get('phoneVerified', False),
        luvhive.get('telegramId'),
        luvhive.get('violationsCount', 0),
        luvhive.get('authMethod', 'password'),
        luvhive.get('createdAt', datetime.now())
    ))
    
    pg_conn.commit()
    print(f"   ✅ Migrated Luvhive user to PostgreSQL")
    
    pg_cur.close()
    pg_conn.close()
    mongo_client.close()
    
    return True

def migrate_posts():
    """Migrate Luvhive's posts to PostgreSQL"""
    print("\n🔄 Step 2: Migrating posts...")
    
    pg_conn = psycopg2.connect(PG_URL)
    pg_cur = pg_conn.cursor()
    mongo_client = MongoClient(MONGO_URL)
    mongo_db = mongo_client.luvhive_database
    
    # Get Luvhive user ID from MongoDB
    luvhive = mongo_db.users.find_one({"username": "Luvhive"})
    luvhive_mongo_id = luvhive.get('id')
    
    # Get posts
    posts = mongo_db.posts.find({"userId": luvhive_mongo_id})
    
    # Delete all existing webapp_posts
    pg_cur.execute("DELETE FROM webapp_posts")
    
    post_count = 0
    for post in posts:
        pg_cur.execute("""
            INSERT INTO webapp_posts (
                user_id, caption, media, created_at, likes_count, comments_count
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            1,  # Luvhive's PG ID
            post.get('caption', ''),
            json.dumps(post.get('media', [])),
            post.get('createdAt', datetime.now()),
            post.get('likesCount', 0),
            post.get('commentsCount', 0)
        ))
        post_count += 1
    
    pg_conn.commit()
    print(f"   ✅ Migrated {post_count} posts")
    
    pg_cur.close()
    pg_conn.close()
    mongo_client.close()

def update_bot_user():
    """Update bot's users table to link with webapp_users"""
    print("\n🔄 Step 3: Linking bot user with webapp...")
    
    pg_conn = psycopg2.connect(PG_URL)
    pg_cur = pg_conn.cursor()
    
    # Update or insert in bot's users table
    pg_cur.execute("""
        INSERT INTO users (tg_user_id, username, is_premium, premium_until)
        VALUES (1437934486, 'Luvhive', true, NOW() + INTERVAL '365 days')
        ON CONFLICT (tg_user_id) DO UPDATE 
        SET is_premium = true, premium_until = NOW() + INTERVAL '365 days'
    """)
    
    pg_conn.commit()
    print(f"   ✅ Bot user linked with webapp")
    
    pg_cur.close()
    pg_conn.close()

if __name__ == "__main__":
    print("🚀 STARTING MONGODB → POSTGRESQL MIGRATION")
    print("=" * 80)
    print("⚠️  This will:")
    print("   1. Delete ALL webapp_users except Luvhive")
    print("   2. Migrate Luvhive user data")
    print("   3. Migrate Luvhive's posts")
    print("   4. Link with bot's users table")
    print("=" * 80)
    
    try:
        if migrate_luvhive_user():
            migrate_posts()
            update_bot_user()
            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 80)
        else:
            print("\n❌ Migration failed")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
