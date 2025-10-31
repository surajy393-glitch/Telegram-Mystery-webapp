-- Complete PostgreSQL Schema for LuvHive WebApp
-- This creates the webapp_users table and all related tables

-- Main webapp_users table
CREATE TABLE IF NOT EXISTS webapp_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    mobile_number VARCHAR(20),
    password VARCHAR(255),
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    bio TEXT DEFAULT '',
    profile_photo_url TEXT,
    
    -- Telegram Integration
    telegram_id BIGINT UNIQUE,
    telegram_username VARCHAR(100),
    telegram_first_name VARCHAR(255),
    telegram_last_name VARCHAR(255),
    telegram_photo_url TEXT,
    auth_method VARCHAR(50) DEFAULT 'password',
    
    -- Premium & Verification
    is_premium BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verification_pathway VARCHAR(100),
    is_founder BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    mobile_verified BOOLEAN DEFAULT FALSE,
    violations_count INTEGER DEFAULT 0,
    
    -- Privacy Settings
    appear_in_search BOOLEAN DEFAULT TRUE,
    allow_direct_messages BOOLEAN DEFAULT TRUE,
    show_online_status BOOLEAN DEFAULT TRUE,
    
    -- Interaction Preferences
    allow_tagging BOOLEAN DEFAULT TRUE,
    allow_story_replies BOOLEAN DEFAULT TRUE,
    show_vibe_score BOOLEAN DEFAULT TRUE,
    
    -- Notifications
    push_notifications BOOLEAN DEFAULT TRUE,
    email_notifications BOOLEAN DEFAULT TRUE,
    
    -- Additional Info
    country VARCHAR(100),
    city VARCHAR(100),
    interests JSONB DEFAULT '[]',
    personality_answers JSONB DEFAULT '{}',
    last_username_change TIMESTAMP,
    is_online BOOLEAN DEFAULT TRUE,
    last_seen TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for webapp_users
CREATE INDEX IF NOT EXISTS idx_users_username ON webapp_users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON webapp_users(email);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON webapp_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_is_premium ON webapp_users(is_premium);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON webapp_users(is_verified);

-- Posts table
CREATE TABLE IF NOT EXISTS webapp_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    caption TEXT,
    media JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    is_deleted BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_posts_user_id ON webapp_posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON webapp_posts(created_at DESC);

-- Stories table
CREATE TABLE IF NOT EXISTS webapp_stories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    media_url TEXT NOT NULL,
    media_type VARCHAR(20) DEFAULT 'image',
    caption TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '24 hours',
    viewers JSONB DEFAULT '[]',
    views_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_stories_user_id ON webapp_stories(user_id);
CREATE INDEX IF NOT EXISTS idx_stories_expires_at ON webapp_stories(expires_at);

-- Notifications table
CREATE TABLE IF NOT EXISTS webapp_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    from_user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    from_username VARCHAR(100),
    from_user_image TEXT,
    message TEXT,
    post_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON webapp_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON webapp_notifications(created_at DESC);

-- Follows table
CREATE TABLE IF NOT EXISTS webapp_follows (
    follower_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    following_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'accepted',
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id)
);

CREATE INDEX IF NOT EXISTS idx_follows_follower ON webapp_follows(follower_id);
CREATE INDEX IF NOT EXISTS idx_follows_following ON webapp_follows(following_id);

-- Likes table
CREATE TABLE IF NOT EXISTS webapp_likes (
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_post_id ON webapp_likes(post_id);

-- Comments table
CREATE TABLE IF NOT EXISTS webapp_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    username VARCHAR(100),
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_post_id ON webapp_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON webapp_comments(created_at DESC);

-- Saved posts table
CREATE TABLE IF NOT EXISTS webapp_saved_posts (
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

-- Blocked users table
CREATE TABLE IF NOT EXISTS webapp_blocked_users (
    blocker_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    blocked_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    blocked_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (blocker_id, blocked_id)
);

-- Muted users table
CREATE TABLE IF NOT EXISTS webapp_muted_users (
    muter_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    muted_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    muted_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (muter_id, muted_id)
);

-- Post reports table
CREATE TABLE IF NOT EXISTS webapp_post_reports (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    reporter_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Verification codes table (for OTP)
CREATE TABLE IF NOT EXISTS webapp_verification_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    mobile VARCHAR(20),
    telegram_id BIGINT,
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '10 minutes',
    attempts INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_verification_email ON webapp_verification_codes(email);
CREATE INDEX IF NOT EXISTS idx_verification_mobile ON webapp_verification_codes(mobile);
CREATE INDEX IF NOT EXISTS idx_verification_telegram ON webapp_verification_codes(telegram_id);

-- Hidden story users table
CREATE TABLE IF NOT EXISTS webapp_hidden_story_users (
    hider_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    hidden_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    hidden_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (hider_id, hidden_id)
);

-- Follow requests table (for private accounts)
CREATE TABLE IF NOT EXISTS webapp_follow_requests (
    requester_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    requested_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (requester_id, requested_id)
);
