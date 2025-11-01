-- Fix PostgreSQL schema - Add all missing columns to webapp_users

-- Add missing columns to webapp_users table
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS telegram_username VARCHAR(100);
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS telegram_first_name VARCHAR(255);
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS telegram_last_name VARCHAR(255);
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS telegram_photo_url TEXT;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS appear_in_search BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS allow_direct_messages BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS show_online_status BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS allow_tagging BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS allow_story_replies BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS show_vibe_score BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS push_notifications BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS email_notifications BOOLEAN DEFAULT TRUE;
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS personality_answers JSONB DEFAULT '{}';
ALTER TABLE webapp_users ADD COLUMN IF NOT EXISTS last_username_change TIMESTAMP;

-- Update existing users to have proper default values
UPDATE webapp_users SET appear_in_search = TRUE WHERE appear_in_search IS NULL;
UPDATE webapp_users SET allow_direct_messages = TRUE WHERE allow_direct_messages IS NULL;
UPDATE webapp_users SET show_online_status = TRUE WHERE show_online_status IS NULL;
UPDATE webapp_users SET allow_tagging = TRUE WHERE allow_tagging IS NULL;
UPDATE webapp_users SET allow_story_replies = TRUE WHERE allow_story_replies IS NULL;
UPDATE webapp_users SET show_vibe_score = TRUE WHERE show_vibe_score IS NULL;
UPDATE webapp_users SET push_notifications = TRUE WHERE push_notifications IS NULL;
UPDATE webapp_users SET email_notifications = TRUE WHERE email_notifications IS NULL;
UPDATE webapp_users SET personality_answers = '{}' WHERE personality_answers IS NULL;

-- Create missing tables
CREATE TABLE IF NOT EXISTS webapp_hidden_story_users (
    hider_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    hidden_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    hidden_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (hider_id, hidden_id)
);

CREATE TABLE IF NOT EXISTS webapp_follow_requests (
    requester_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    requested_id INTEGER REFERENCES webapp_users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (requester_id, requested_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_hidden_story_users_hider ON webapp_hidden_story_users(hider_id);
CREATE INDEX IF NOT EXISTS idx_hidden_story_users_hidden ON webapp_hidden_story_users(hidden_id);
CREATE INDEX IF NOT EXISTS idx_follow_requests_requester ON webapp_follow_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_follow_requests_requested ON webapp_follow_requests(requested_id);
