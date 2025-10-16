-- ============================================
-- MYSTERY MATCH DATABASE SCHEMA
-- ============================================
-- Tables for progressive profile unlock dating system

-- Mystery Matches Table
CREATE TABLE IF NOT EXISTS mystery_matches (
    id BIGSERIAL PRIMARY KEY,
    user1_id BIGINT NOT NULL REFERENCES users(tg_user_id),
    user2_id BIGINT NOT NULL REFERENCES users(tg_user_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '48 hours'),
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    user1_unlock_level INTEGER DEFAULT 0 CHECK (user1_unlock_level BETWEEN 0 AND 4),
    user2_unlock_level INTEGER DEFAULT 0 CHECK (user2_unlock_level BETWEEN 0 AND 4),
    secret_chat_active BOOLEAN DEFAULT FALSE,
    secret_chat_expires_at TIMESTAMPTZ,
    UNIQUE(user1_id, user2_id)
);

-- Match Messages Table
CREATE TABLE IF NOT EXISTS match_messages (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES mystery_matches(id) ON DELETE CASCADE,
    sender_id BIGINT NOT NULL,
    message_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_secret_chat BOOLEAN DEFAULT FALSE,
    self_destruct_at TIMESTAMPTZ,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Daily Match Tracking (for free user limits)
CREATE TABLE IF NOT EXISTS daily_match_limits (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    match_date DATE DEFAULT CURRENT_DATE,
    matches_used INTEGER DEFAULT 0,
    UNIQUE(user_id, match_date)
);

-- Secret Chat Requests
CREATE TABLE IF NOT EXISTS secret_chat_requests (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES mystery_matches(id) ON DELETE CASCADE,
    requester_id BIGINT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ
);

-- Match Reports (for safety)
CREATE TABLE IF NOT EXISTS match_reports (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES mystery_matches(id),
    reporter_id BIGINT NOT NULL,
    reported_user_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- Profile Unlocks Log (analytics)
CREATE TABLE IF NOT EXISTS profile_unlock_log (
    id BIGSERIAL PRIMARY KEY,
    match_id BIGINT NOT NULL REFERENCES mystery_matches(id),
    user_id BIGINT NOT NULL,
    unlock_level INTEGER NOT NULL,
    unlock_type VARCHAR(50), -- 'age_city', 'photo_blur', 'interests', 'photo_full'
    unlocked_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Indexes on mystery_matches
CREATE INDEX IF NOT EXISTS idx_mystery_matches_user1 ON mystery_matches(user1_id);
CREATE INDEX IF NOT EXISTS idx_mystery_matches_user2 ON mystery_matches(user2_id);
CREATE INDEX IF NOT EXISTS idx_mystery_matches_active ON mystery_matches(is_active);
CREATE INDEX IF NOT EXISTS idx_mystery_matches_expires ON mystery_matches(expires_at);
CREATE INDEX IF NOT EXISTS idx_mystery_matches_created ON mystery_matches(created_at DESC);

-- Indexes on match_messages
CREATE INDEX IF NOT EXISTS idx_match_messages_match ON match_messages(match_id);
CREATE INDEX IF NOT EXISTS idx_match_messages_sender ON match_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_match_messages_created ON match_messages(created_at DESC);

-- Indexes on daily_match_limits
CREATE INDEX IF NOT EXISTS idx_daily_limits_user ON daily_match_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_limits_date ON daily_match_limits(match_date);

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to auto-expire matches
CREATE OR REPLACE FUNCTION expire_mystery_matches()
RETURNS void AS $$
BEGIN
    UPDATE mystery_matches
    SET is_active = FALSE
    WHERE is_active = TRUE
    AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old expired matches (run daily)
CREATE OR REPLACE FUNCTION cleanup_old_matches()
RETURNS void AS $$
BEGIN
    -- Delete messages from matches expired > 30 days ago
    DELETE FROM match_messages
    WHERE match_id IN (
        SELECT id FROM mystery_matches
        WHERE is_active = FALSE
        AND expires_at < NOW() - INTERVAL '30 days'
    );
    
    -- Delete expired matches > 30 days old
    DELETE FROM mystery_matches
    WHERE is_active = FALSE
    AND expires_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- View for active matches summary
CREATE OR REPLACE VIEW active_matches_summary AS
SELECT 
    DATE(created_at) as match_date,
    COUNT(*) as total_matches,
    COUNT(CASE WHEN secret_chat_active THEN 1 END) as secret_chats,
    AVG(message_count) as avg_messages,
    COUNT(CASE WHEN message_count >= 100 THEN 1 END) as fully_unlocked
FROM mystery_matches
WHERE is_active = TRUE
GROUP BY DATE(created_at)
ORDER BY match_date DESC;

-- View for user engagement
CREATE OR REPLACE VIEW user_engagement_stats AS
SELECT 
    user_id,
    COUNT(DISTINCT match_id) as total_matches,
    SUM(message_count) as total_messages,
    AVG(message_count) as avg_messages_per_match,
    COUNT(CASE WHEN unlock_level >= 4 THEN 1 END) as fully_unlocked_matches
FROM (
    SELECT user1_id as user_id, id as match_id, message_count, user1_unlock_level as unlock_level
    FROM mystery_matches
    UNION ALL
    SELECT user2_id as user_id, id as match_id, message_count, user2_unlock_level as unlock_level
    FROM mystery_matches
) as user_matches
GROUP BY user_id;

-- ============================================
-- SAMPLE QUERIES
-- ============================================

-- Get daily active users
-- SELECT COUNT(DISTINCT user_id) FROM (
--     SELECT user1_id as user_id FROM mystery_matches WHERE DATE(created_at) = CURRENT_DATE
--     UNION
--     SELECT user2_id FROM mystery_matches WHERE DATE(created_at) = CURRENT_DATE
-- ) as daily_users;

-- Get conversion funnel
-- SELECT 
--     COUNT(*) as total_matches,
--     COUNT(CASE WHEN message_count >= 10 THEN 1 END) as reached_10_msgs,
--     COUNT(CASE WHEN message_count >= 30 THEN 1 END) as reached_30_msgs,
--     COUNT(CASE WHEN message_count >= 50 THEN 1 END) as reached_50_msgs,
--     COUNT(CASE WHEN message_count >= 100 THEN 1 END) as reached_100_msgs
-- FROM mystery_matches;
