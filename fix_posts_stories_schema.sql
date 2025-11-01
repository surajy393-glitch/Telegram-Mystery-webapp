-- Fix webapp_posts table schema to match application requirements

-- Add missing columns to webapp_posts
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS username VARCHAR(100);
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS user_profile_image TEXT;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS media_type VARCHAR(20);
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS caption TEXT;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS likes JSONB DEFAULT '[]';
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS comments JSONB DEFAULT '[]';
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS likes_hidden BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS comments_disabled BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS is_pinned BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS telegram_file_id TEXT;
ALTER TABLE webapp_posts ADD COLUMN IF NOT EXISTS telegram_file_path TEXT;

-- Add missing columns to webapp_stories  
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS username VARCHAR(100);
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS user_profile_image TEXT;
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS media_type VARCHAR(20) DEFAULT 'image';
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS caption TEXT;
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS likes JSONB DEFAULT '[]';
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS viewers JSONB DEFAULT '[]';
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS telegram_file_id TEXT;
ALTER TABLE webapp_stories ADD COLUMN IF NOT EXISTS telegram_file_path TEXT;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_posts_username ON webapp_posts(username);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON webapp_posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_user_id_created_at ON webapp_posts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_stories_username ON webapp_stories(username);
CREATE INDEX IF NOT EXISTS idx_stories_expires_at ON webapp_stories(expires_at);
CREATE INDEX IF NOT EXISTS idx_stories_user_id ON webapp_stories(user_id);
