-- Complete PostgreSQL Schema for LuvHive WebApp
-- This creates all necessary tables to replace MongoDB

-- 1. webapp_posts table
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

CREATE INDEX idx_posts_user_id ON webapp_posts(user_id);
CREATE INDEX idx_posts_created_at ON webapp_posts(created_at DESC);

-- 2. webapp_stories table
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

CREATE INDEX idx_stories_user_id ON webapp_stories(user_id);
CREATE INDEX idx_stories_expires_at ON webapp_stories(expires_at);

-- 3. webapp_notifications table
CREATE TABLE IF NOT EXISTS webapp_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    from_user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    from_username VARCHAR(100),
    message TEXT,
    post_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_id ON webapp_notifications(user_id);
CREATE INDEX idx_notifications_created_at ON webapp_notifications(created_at DESC);

-- 4. webapp_follows table
CREATE TABLE IF NOT EXISTS webapp_follows (
    follower_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    following_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'accepted',
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id)
);

CREATE INDEX idx_follows_follower ON webapp_follows(follower_id);
CREATE INDEX idx_follows_following ON webapp_follows(following_id);

-- 5. webapp_likes table
CREATE TABLE IF NOT EXISTS webapp_likes (
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

CREATE INDEX idx_likes_post_id ON webapp_likes(post_id);

-- 6. webapp_comments table
CREATE TABLE IF NOT EXISTS webapp_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    username VARCHAR(100),
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_comments_post_id ON webapp_comments(post_id);
CREATE INDEX idx_comments_created_at ON webapp_comments(created_at DESC);

-- 7. webapp_saved_posts table
CREATE TABLE IF NOT EXISTS webapp_saved_posts (
    user_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

-- 8. webapp_blocked_users table
CREATE TABLE IF NOT EXISTS webapp_blocked_users (
    blocker_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    blocked_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    blocked_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (blocker_id, blocked_id)
);

-- 9. webapp_muted_users table
CREATE TABLE IF NOT EXISTS webapp_muted_users (
    muter_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    muted_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    muted_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (muter_id, muted_id)
);

-- 10. webapp_post_reports table
CREATE TABLE IF NOT EXISTS webapp_post_reports (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES webapp_posts(id) ON DELETE CASCADE,
    reporter_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 11. webapp_verification_codes table
CREATE TABLE IF NOT EXISTS webapp_verification_codes (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    mobile VARCHAR(20),
    code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT NOW() + INTERVAL '10 minutes'
);

CREATE INDEX idx_verification_email ON webapp_verification_codes(email);
CREATE INDEX idx_verification_mobile ON webapp_verification_codes(mobile);

-- 12. Add missing columns to webapp_users if needed
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS is_premium BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS is_founder BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS violations_count INTEGER DEFAULT 0;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS auth_method VARCHAR(50) DEFAULT 'password';
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS verification_pathway VARCHAR(100);
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS country VARCHAR(100);
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP DEFAULT NOW();

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON webapp_users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON webapp_users(email);
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON webapp_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_is_premium ON webapp_users(is_premium);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON webapp_users(is_verified);
