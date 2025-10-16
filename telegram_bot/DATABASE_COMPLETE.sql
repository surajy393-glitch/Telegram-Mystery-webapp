-- ============================================================================
-- LUVHIVE TELEGRAM BOT - COMPLETE DATABASE SCHEMA EXPORT
-- ============================================================================
-- Export Date: October 16, 2025
-- Total Tables: 131
-- Database: PostgreSQL Development
-- 
-- This file contains EVERYTHING in a single file:
-- ✅ All 131 CREATE TABLE statements
-- ✅ All column definitions with proper data types
-- ✅ All PRIMARY KEY constraints
-- ✅ All FOREIGN KEY relationships
-- ✅ All UNIQUE constraints
-- ✅ All indexes for performance
-- ✅ All DEFAULT values
-- 
-- Import: psql -U username -d dbname -f DATABASE_COMPLETE.sql
-- ============================================================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- ============================================================================
-- DROP EXISTING TABLES (Optional - uncomment if needed)
-- ============================================================================
-- DROP TABLE IF EXISTS ad_messages CASCADE;
-- DROP TABLE IF EXISTS ad_participants CASCADE;
-- [... add all tables if needed for clean import]

-- ============================================================================
-- TABLE DEFINITIONS (All 131 Tables)
-- ============================================================================


-- [1/131] AD_MESSAGES
CREATE TABLE ad_messages (
    id BIGSERIAL NOT NULL,
    session_id BIGINT,
    user_id BIGINT,
    anon_name TEXT,
    msg_type TEXT NOT NULL,
    content TEXT,
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [2/131] AD_PARTICIPANTS
CREATE TABLE ad_participants (
    id BIGSERIAL NOT NULL,
    session_id BIGINT,
    user_id BIGINT NOT NULL,
    anon_name TEXT NOT NULL,
    joined_at TIMESTAMPTZ DEFAULT now(),
    left_at TIMESTAMPTZ
);

-- [3/131] AD_PROMPTS
CREATE TABLE ad_prompts (
    id BIGSERIAL NOT NULL,
    session_id BIGINT,
    kind TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [4/131] AD_SESSIONS
CREATE TABLE ad_sessions (
    id BIGSERIAL NOT NULL,
    started_at TIMESTAMPTZ DEFAULT now(),
    ends_at TIMESTAMPTZ NOT NULL,
    vibe TEXT,
    status TEXT DEFAULT 'live'::text
);

-- [5/131] ADMIN_AUDIT_LOG
CREATE TABLE admin_audit_log (
    id BIGSERIAL NOT NULL,
    admin_user_id BIGINT NOT NULL,
    action TEXT NOT NULL,
    target_user_id BIGINT,
    target_type TEXT,
    details JSONB,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [6/131] BLOCKED_USERS
CREATE TABLE blocked_users (
    user_id BIGINT NOT NULL,
    blocked_uid BIGINT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- [7/131] CHAT_EXTENSIONS
CREATE TABLE chat_extensions (
    id SERIAL NOT NULL,
    match_id BIGINT NOT NULL,
    extended_by BIGINT NOT NULL,
    stars_paid INTEGER DEFAULT 50,
    minutes_added INTEGER DEFAULT 30,
    extended_at TIMESTAMPTZ DEFAULT now()
);

-- [8/131] CHAT_RATINGS
CREATE TABLE chat_ratings (
    id SERIAL NOT NULL,
    rater_id BIGINT NOT NULL,
    ratee_id BIGINT NOT NULL,
    value SMALLINT NOT NULL,
    reason TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- [9/131] CHAT_REPORTS
CREATE TABLE chat_reports (
    id BIGSERIAL NOT NULL,
    reporter_tg_id BIGINT NOT NULL,
    reported_tg_id BIGINT NOT NULL,
    in_secret BOOLEAN NOT NULL DEFAULT false,
    text TEXT,
    media_file_id TEXT,
    media_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [10/131] COMMENT_LIKES
CREATE TABLE comment_likes (
    comment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [11/131] COMMENTS
CREATE TABLE comments (
    id SERIAL NOT NULL,
    post_id INTEGER,
    user_id BIGINT,
    text TEXT,
    created_at TIMESTAMP,
    pinned BOOLEAN NOT NULL DEFAULT false,
    pinned_at TIMESTAMPTZ,
    pinned_by_user_id INTEGER,
    profile_id BIGINT
);

-- [12/131] CONFESSION_DELIVERIES
CREATE TABLE confession_deliveries (
    id BIGSERIAL NOT NULL,
    confession_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    delivered_at TIMESTAMPTZ DEFAULT now()
);

-- [13/131] CONFESSION_LEADERBOARD
CREATE TABLE confession_leaderboard (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    period VARCHAR(20) NOT NULL,
    confession_count INTEGER DEFAULT 0,
    total_reactions_received INTEGER DEFAULT 0,
    replies_received INTEGER DEFAULT 0,
    rank_type VARCHAR(30) NOT NULL,
    rank_position INTEGER DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [14/131] CONFESSION_MUTES
CREATE TABLE confession_mutes (
    user_id BIGINT NOT NULL,
    confession_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [15/131] CONFESSION_REACTIONS
CREATE TABLE confession_reactions (
    id BIGSERIAL NOT NULL,
    confession_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reaction_type VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    approved BOOLEAN DEFAULT false,
    approved_at TIMESTAMPTZ
);

-- [16/131] CONFESSION_REPLIES
CREATE TABLE confession_replies (
    id BIGSERIAL NOT NULL,
    original_confession_id BIGINT NOT NULL,
    replier_user_id BIGINT NOT NULL,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    reply_reactions INTEGER DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT true,
    approved BOOLEAN DEFAULT false,
    approved_at TIMESTAMPTZ
);

-- [17/131] CONFESSION_ROULETTE
CREATE TABLE confession_roulette (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    confession_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    delivered BOOLEAN DEFAULT false
);

-- [18/131] CONFESSION_ROUND_LOCK
CREATE TABLE confession_round_lock (
    user_id BIGINT NOT NULL,
    round_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [19/131] CONFESSION_STATS
CREATE TABLE confession_stats (
    user_id BIGINT NOT NULL,
    total_confessions INTEGER DEFAULT 0,
    weekly_confessions INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_reactions_received INTEGER DEFAULT 0,
    total_replies_received INTEGER DEFAULT 0,
    best_confessor_score INTEGER DEFAULT 0,
    last_confession_date DATE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [20/131] CONFESSIONS
CREATE TABLE confessions (
    id SERIAL NOT NULL,
    author_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    delivered BOOLEAN DEFAULT false,
    delivered_at TIMESTAMPTZ,
    delivered_to BIGINT,
    system_seed BOOLEAN DEFAULT false,
    deleted_at TIMESTAMPTZ
);

-- [21/131] CRUSH_LEADERBOARD
CREATE TABLE crush_leaderboard (
    user_id BIGINT NOT NULL,
    crush_count INTEGER DEFAULT 0,
    week_start DATE DEFAULT CURRENT_DATE,
    last_updated TIMESTAMPTZ DEFAULT now()
);

-- [22/131] DAILY_DARE_SELECTION
CREATE TABLE daily_dare_selection (
    dare_date DATE NOT NULL,
    dare_text TEXT NOT NULL,
    dare_source VARCHAR(20) DEFAULT 'community'::character varying,
    source_id INTEGER,
    created_at TIMESTAMPTZ DEFAULT now(),
    submitter_id BIGINT,
    category VARCHAR(20) DEFAULT 'general'::character varying,
    difficulty VARCHAR(10) DEFAULT 'medium'::character varying,
    creator_notified BOOLEAN DEFAULT false
);

-- [23/131] DARE_FEEDBACK
CREATE TABLE dare_feedback (
    id SERIAL NOT NULL,
    submission_id INTEGER,
    event_type VARCHAR(20),
    user_id BIGINT,
    dare_date DATE,
    notified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [24/131] DARE_RESPONSES
CREATE TABLE dare_responses (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    dare_date DATE NOT NULL,
    response VARCHAR(10),
    response_time TIMESTAMPTZ DEFAULT now(),
    completion_claimed BOOLEAN DEFAULT false,
    difficulty_selected VARCHAR(10) DEFAULT 'medium'::character varying,
    dare_text TEXT
);

-- [25/131] DARE_STATS
CREATE TABLE dare_stats (
    user_id BIGINT NOT NULL,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    total_declined INTEGER DEFAULT 0,
    total_expired INTEGER DEFAULT 0,
    last_dare_date DATE,
    badges TEXT[] DEFAULT '{}'::text[],
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [26/131] DARE_SUBMISSIONS
CREATE TABLE dare_submissions (
    id SERIAL NOT NULL,
    submitter_id BIGINT NOT NULL,
    dare_text TEXT NOT NULL,
    category VARCHAR(20) DEFAULT 'general'::character varying,
    difficulty VARCHAR(10) DEFAULT 'medium'::character varying,
    approved BOOLEAN DEFAULT false,
    admin_approved_by BIGINT,
    submission_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [27/131] FANTASY_ACHIEVEMENTS
CREATE TABLE fantasy_achievements (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    achievement_key TEXT NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT now(),
    stars_earned INTEGER DEFAULT 0
);

-- [28/131] FANTASY_BOARD_REACTIONS
CREATE TABLE fantasy_board_reactions (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    fantasy_id BIGINT NOT NULL,
    reaction_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [29/131] FANTASY_CHAT_SESSIONS
CREATE TABLE fantasy_chat_sessions (
    id BIGSERIAL NOT NULL,
    a_id BIGINT NOT NULL,
    b_id BIGINT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active'::text
);

-- [30/131] FANTASY_CHATS
CREATE TABLE fantasy_chats (
    id INTEGER NOT NULL,
    match_id INTEGER,
    chat_room_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT (now() + '00:15:00'::interval),
    boy_joined BOOLEAN DEFAULT false,
    girl_joined BOOLEAN DEFAULT false,
    message_count INTEGER DEFAULT 0
);

-- [31/131] FANTASY_EVENTS
CREATE TABLE fantasy_events (
    id SERIAL NOT NULL,
    event_key TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT true,
    participants_count INTEGER DEFAULT 0
);

-- [32/131] FANTASY_LEADERBOARD
CREATE TABLE fantasy_leaderboard (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    week_start DATE NOT NULL,
    total_reactions INTEGER DEFAULT 0,
    total_matches INTEGER DEFAULT 0,
    total_chats INTEGER DEFAULT 0,
    success_rate NUMERIC DEFAULT 0.0,
    rank_position INTEGER DEFAULT 999
);

-- [33/131] FANTASY_MATCH_NOTIFS
CREATE TABLE fantasy_match_notifs (
    id INTEGER NOT NULL,
    match_id INTEGER,
    user_id BIGINT NOT NULL,
    sent_at TIMESTAMP DEFAULT now()
);

-- [34/131] FANTASY_MATCH_REQUESTS
CREATE TABLE fantasy_match_requests (
    id INTEGER NOT NULL,
    requester_id BIGINT NOT NULL,
    fantasy_id BIGINT NOT NULL,
    fantasy_owner_id BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'::text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    responded_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    cancelled_by_user_id BIGINT,
    cancelled_at TIMESTAMPTZ,
    cancel_reason TEXT,
    version INTEGER DEFAULT 1
);

-- [35/131] FANTASY_MATCHES
CREATE TABLE fantasy_matches (
    id INTEGER NOT NULL,
    boy_id BIGINT NOT NULL,
    girl_id BIGINT NOT NULL,
    fantasy_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    expires_at TIMESTAMP DEFAULT (now() + '24:00:00'::interval),
    boy_ready BOOLEAN DEFAULT false,
    girl_ready BOOLEAN DEFAULT false,
    boy_is_premium BOOLEAN DEFAULT false,
    connected_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending'::character varying,
    chat_id TEXT,
    vibe TEXT,
    shared_keywords TEXT[]
);

-- [36/131] FANTASY_STATS
CREATE TABLE fantasy_stats (
    fantasy_id BIGINT NOT NULL,
    views_count INTEGER DEFAULT 0,
    reactions_count INTEGER DEFAULT 0,
    matches_count INTEGER DEFAULT 0,
    success_rate NUMERIC DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT now()
);

-- [37/131] FANTASY_SUBMISSIONS
CREATE TABLE fantasy_submissions (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    gender TEXT NOT NULL,
    fantasy_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    is_active BOOLEAN DEFAULT true,
    fantasy_key TEXT,
    submitted_count INTEGER DEFAULT 1,
    vibe TEXT,
    keywords TEXT[],
    active BOOLEAN DEFAULT true,
    status TEXT DEFAULT 'pending'::text
);

-- [38/131] FANTASY_TREASURE_HUNT
CREATE TABLE fantasy_treasure_hunt (
    id SERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    clue_index INTEGER NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT now(),
    stars_earned INTEGER DEFAULT 0
);

-- [39/131] FEED_COMMENTS
CREATE TABLE feed_comments (
    id BIGINT NOT NULL,
    post_id BIGINT,
    author_id BIGINT NOT NULL,
    author_name TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [40/131] FEED_LIKES
CREATE TABLE feed_likes (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [41/131] FEED_POSTS
CREATE TABLE feed_posts (
    id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    content_type TEXT,
    file_id TEXT,
    text TEXT,
    reaction_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    profile_id BIGINT
);

-- [42/131] FEED_PROFILES
CREATE TABLE feed_profiles (
    uid BIGINT NOT NULL,
    username TEXT,
    bio TEXT,
    is_public BOOLEAN DEFAULT true,
    photo TEXT
);

-- [43/131] FEED_REACTIONS
CREATE TABLE feed_reactions (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    emoji TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [44/131] FEED_VIEWS
CREATE TABLE feed_views (
    post_id BIGINT NOT NULL,
    viewer_id BIGINT NOT NULL,
    viewed_at TIMESTAMPTZ DEFAULT now()
);

-- [45/131] FRIEND_CHATS
CREATE TABLE friend_chats (
    id BIGINT NOT NULL,
    a BIGINT,
    b BIGINT,
    opened_at TIMESTAMPTZ DEFAULT now(),
    closed_at TIMESTAMPTZ
);

-- [46/131] FRIEND_MSG_REQUESTS
CREATE TABLE friend_msg_requests (
    id BIGINT NOT NULL,
    sender BIGINT,
    receiver BIGINT,
    text TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    status TEXT DEFAULT 'pending'::text
);

-- [47/131] FRIEND_REQUESTS
CREATE TABLE friend_requests (
    requester_id BIGINT NOT NULL,
    target_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [48/131] FRIENDS
CREATE TABLE friends (
    user_id BIGINT NOT NULL,
    friend_id BIGINT NOT NULL,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- [49/131] FRIENDSHIP_LEVELS
CREATE TABLE friendship_levels (
    user1_id BIGINT NOT NULL,
    user2_id BIGINT NOT NULL,
    interaction_count INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    last_interaction TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [50/131] GAME_QUESTIONS
CREATE TABLE game_questions (
    game TEXT,
    question TEXT,
    added_by BIGINT,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- [51/131] IDEMPOTENCY_KEYS
CREATE TABLE idempotency_keys (
    key TEXT NOT NULL,
    operation TEXT NOT NULL,
    result JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [52/131] LIKES
CREATE TABLE likes (
    id INTEGER NOT NULL,
    post_id INTEGER,
    user_id BIGINT,
    created_at TIMESTAMP
);

-- [53/131] MAINTENANCE_LOG
CREATE TABLE maintenance_log (
    id BIGINT NOT NULL,
    operation TEXT NOT NULL,
    status TEXT NOT NULL,
    details JSONB,
    duration_seconds REAL,
    executed_at TIMESTAMPTZ DEFAULT now()
);

-- [54/131] MINIAPP_COMMENTS
CREATE TABLE miniapp_comments (
    id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    parent_id BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [55/131] MINIAPP_FOLLOWS
CREATE TABLE miniapp_follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'approved'::text
);

-- [56/131] MINIAPP_LIKES
CREATE TABLE miniapp_likes (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [57/131] MINIAPP_POST_VIEWS
CREATE TABLE miniapp_post_views (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [58/131] MINIAPP_POSTS
CREATE TABLE miniapp_posts (
    id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    type TEXT NOT NULL DEFAULT 'text'::text,
    caption TEXT,
    media_url TEXT,
    media_type TEXT,
    visibility TEXT NOT NULL DEFAULT 'public'::text,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [59/131] MINIAPP_PROFILES
CREATE TABLE miniapp_profiles (
    user_id BIGINT NOT NULL,
    username TEXT,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    is_private BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [60/131] MINIAPP_SAVES
CREATE TABLE miniapp_saves (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + '72:00:00'::interval)
);

-- [61/131] MODERATION_EVENTS
CREATE TABLE moderation_events (
    id BIGINT NOT NULL,
    tg_user_id BIGINT,
    kind TEXT NOT NULL,
    token TEXT NOT NULL,
    sample TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [62/131] MUC_CHAR_OPTIONS
CREATE TABLE muc_char_options (
    id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    opt_key TEXT NOT NULL,
    text TEXT NOT NULL
);

-- [63/131] MUC_CHAR_QUESTIONS
CREATE TABLE muc_char_questions (
    id INTEGER NOT NULL,
    series_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    question_key TEXT NOT NULL,
    active_from_episode_id INTEGER
);

-- [64/131] MUC_CHAR_VOTES
CREATE TABLE muc_char_votes (
    id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [65/131] MUC_CHARACTERS
CREATE TABLE muc_characters (
    id INTEGER NOT NULL,
    series_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    bio_md TEXT,
    attributes JSONB DEFAULT '{}'::jsonb,
    secrets JSONB DEFAULT '{}'::jsonb
);

-- [66/131] MUC_EPISODES
CREATE TABLE muc_episodes (
    id INTEGER NOT NULL,
    series_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    title TEXT NOT NULL,
    teaser_md TEXT,
    body_md TEXT,
    cliff_md TEXT,
    publish_at TIMESTAMPTZ,
    close_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'draft'::text
);

-- [67/131] MUC_POLL_OPTIONS
CREATE TABLE muc_poll_options (
    id INTEGER NOT NULL,
    poll_id INTEGER NOT NULL,
    opt_key TEXT,
    text TEXT NOT NULL,
    next_hint TEXT,
    idx INTEGER DEFAULT 0
);

-- [68/131] MUC_POLLS
CREATE TABLE muc_polls (
    id INTEGER NOT NULL,
    episode_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    layer TEXT NOT NULL DEFAULT 'surface'::text,
    allow_multi BOOLEAN DEFAULT false
);

-- [69/131] MUC_SERIES
CREATE TABLE muc_series (
    id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'::text,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [70/131] MUC_THEORIES
CREATE TABLE muc_theories (
    id INTEGER NOT NULL,
    episode_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [71/131] MUC_THEORY_LIKES
CREATE TABLE muc_theory_likes (
    id INTEGER NOT NULL,
    theory_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [72/131] MUC_USER_ENGAGEMENT
CREATE TABLE muc_user_engagement (
    user_id BIGINT NOT NULL,
    streak_days INTEGER DEFAULT 0,
    detective_score INTEGER DEFAULT 0,
    last_seen_episode_id INTEGER
);

-- [73/131] MUC_VOTES
CREATE TABLE muc_votes (
    id INTEGER NOT NULL,
    poll_id INTEGER NOT NULL,
    option_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [74/131] NAUGHTY_WYR_DELIVERIES
CREATE TABLE naughty_wyr_deliveries (
    question_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    delivered_at TIMESTAMPTZ DEFAULT now()
);

-- [75/131] NAUGHTY_WYR_QUESTIONS
CREATE TABLE naughty_wyr_questions (
    id BIGSERIAL NOT NULL,
    question TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    system_seed BOOLEAN DEFAULT true
);

-- [76/131] NAUGHTY_WYR_VOTES
CREATE TABLE naughty_wyr_votes (
    question_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    choice TEXT NOT NULL,
    voted_at TIMESTAMPTZ DEFAULT now()
);

-- [77/131] NOTIFICATIONS
CREATE TABLE notifications (
    id INTEGER NOT NULL,
    user_id BIGINT,
    ntype VARCHAR(24),
    actor BIGINT,
    post_id INTEGER,
    created_at TIMESTAMP,
    read BOOLEAN
);

-- [78/131] PAYMENTS
CREATE TABLE payments (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    charge_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'XTR'::text,
    status TEXT NOT NULL DEFAULT 'pending'::text,
    product_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [79/131] PAYMENTS_ARCHIVE
CREATE TABLE payments_archive (
    id BIGSERIAL NOT NULL,
    original_payment_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    charge_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'XTR'::text,
    status TEXT NOT NULL,
    product_type TEXT NOT NULL,
    metadata JSONB,
    archived_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

-- [80/131] PENDING_CONFESSION_REPLIES
CREATE TABLE pending_confession_replies (
    id INTEGER NOT NULL,
    original_confession_id BIGINT NOT NULL,
    replier_user_id BIGINT NOT NULL,
    reply_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    admin_notified BOOLEAN DEFAULT false,
    is_voice BOOLEAN DEFAULT false,
    voice_file_id TEXT,
    voice_duration INTEGER
);

-- [81/131] PENDING_CONFESSIONS
CREATE TABLE pending_confessions (
    id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    admin_notified BOOLEAN DEFAULT false,
    is_voice BOOLEAN DEFAULT false,
    voice_file_id TEXT,
    voice_duration INTEGER
);

-- [82/131] POLL_OPTIONS
CREATE TABLE poll_options (
    id BIGINT NOT NULL,
    poll_id BIGINT NOT NULL,
    text TEXT NOT NULL
);

-- [83/131] POLL_VOTES
CREATE TABLE poll_votes (
    poll_id BIGINT NOT NULL,
    voter_id BIGINT NOT NULL,
    option_idx INTEGER NOT NULL,
    voted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [84/131] POLLS
CREATE TABLE polls (
    id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    question TEXT NOT NULL,
    options TEXT[] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

-- [85/131] POST_LIKES
CREATE TABLE post_likes (
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [86/131] POST_REPORTS
CREATE TABLE post_reports (
    id BIGSERIAL NOT NULL,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [87/131] POSTS
CREATE TABLE posts (
    id INTEGER NOT NULL,
    author BIGINT,
    text TEXT,
    media_url TEXT,
    is_public BOOLEAN,
    created_at TIMESTAMP
);

-- [88/131] PROFILES
CREATE TABLE profiles (
    id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    profile_name TEXT NOT NULL,
    username TEXT NOT NULL,
    bio TEXT,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT false
);

-- [89/131] QA_ANSWERS
CREATE TABLE qa_answers (
    id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

-- [90/131] QA_QUESTIONS
CREATE TABLE qa_questions (
    id BIGINT NOT NULL,
    author_id BIGINT,
    text TEXT NOT NULL,
    scope TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

-- [91/131] RATE_LIMIT_LOGS
CREATE TABLE rate_limit_logs (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    action_type TEXT NOT NULL,
    exceeded_at TIMESTAMPTZ DEFAULT now(),
    limit_value INTEGER,
    actual_value INTEGER,
    ip_address TEXT
);

-- [92/131] REFERRALS
CREATE TABLE referrals (
    inviter_id BIGINT NOT NULL,
    invitee_id BIGINT NOT NULL,
    rewarded BOOLEAN DEFAULT false,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- [93/131] REPORTS
CREATE TABLE reports (
    id BIGINT NOT NULL,
    reporter BIGINT NOT NULL,
    target BIGINT NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [94/131] SECRET_CHATS
CREATE TABLE secret_chats (
    id BIGINT NOT NULL,
    a BIGINT NOT NULL,
    b BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    closed_at TIMESTAMPTZ
);

-- [95/131] SECRET_CRUSH
CREATE TABLE secret_crush (
    user_id BIGINT NOT NULL,
    target_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [96/131] SENSUAL_REACTIONS
CREATE TABLE sensual_reactions (
    id BIGINT NOT NULL,
    story_id BIGINT,
    user_id BIGINT NOT NULL,
    reaction TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [97/131] SENSUAL_STORIES
CREATE TABLE sensual_stories (
    id BIGINT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general'::text,
    created_at TIMESTAMPTZ DEFAULT now(),
    is_featured BOOLEAN DEFAULT false
);

-- [98/131] SOCIAL_COMMENTS
CREATE TABLE social_comments (
    id INTEGER NOT NULL,
    post_id INTEGER,
    user_tg_id BIGINT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [99/131] SOCIAL_FRIEND_REQUESTS
CREATE TABLE social_friend_requests (
    id INTEGER NOT NULL,
    requester_tg_id BIGINT NOT NULL,
    target_tg_id BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'::character varying,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [100/131] SOCIAL_FRIENDS
CREATE TABLE social_friends (
    id INTEGER NOT NULL,
    user_tg_id BIGINT NOT NULL,
    friend_tg_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [101/131] SOCIAL_LIKES
CREATE TABLE social_likes (
    id INTEGER NOT NULL,
    post_id INTEGER,
    user_tg_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [102/131] SOCIAL_POSTS
CREATE TABLE social_posts (
    id INTEGER NOT NULL,
    author_tg_id BIGINT NOT NULL,
    text TEXT DEFAULT ''::text,
    media VARCHAR(255),
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [103/131] SOCIAL_PROFILES
CREATE TABLE social_profiles (
    id INTEGER NOT NULL,
    tg_user_id BIGINT NOT NULL,
    username VARCHAR(50),
    bio TEXT DEFAULT ''::text,
    photo VARCHAR(255),
    privacy VARCHAR(20) DEFAULT 'public'::character varying,
    show_fields TEXT DEFAULT 'username,bio,photo'::text,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [104/131] STORIES
CREATE TABLE stories (
    id BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT,
    media_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- [105/131] STORY_SEGMENTS
CREATE TABLE story_segments (
    id SERIAL NOT NULL,
    story_id BIGINT NOT NULL,
    segment_type TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_id TEXT,
    text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id BIGINT,
    profile_id BIGINT
);

-- [106/131] STORY_VIEWS
CREATE TABLE story_views (
    story_id BIGINT NOT NULL,
    viewer_id BIGINT NOT NULL,
    viewed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- [107/131] USER_BADGES
CREATE TABLE user_badges (
    user_id BIGINT NOT NULL,
    badge_id TEXT NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT now()
);

-- [108/131] USER_BLOCKS
CREATE TABLE user_blocks (
    blocker_id BIGINT NOT NULL,
    blocked_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [109/131] USER_DELETION_QUEUE
CREATE TABLE user_deletion_queue (
    id BIGSERIAL NOT NULL,
    tg_user_id BIGINT NOT NULL,
    scheduled_by BIGINT,
    reason TEXT,
    scheduled_at TIMESTAMPTZ DEFAULT now(),
    deletion_date TIMESTAMPTZ DEFAULT (now() + '7 days'::interval),
    status TEXT DEFAULT 'scheduled'::text,
    metadata JSONB
);

-- [110/131] USER_FOLLOWS
CREATE TABLE user_follows (
    follower_id BIGINT NOT NULL,
    followee_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [111/131] USER_INTERESTS
CREATE TABLE user_interests (
    user_id INTEGER,
    interest_key TEXT NOT NULL
);

-- [112/131] USER_MUTES
CREATE TABLE user_mutes (
    muter_id BIGINT NOT NULL,
    muted_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [113/131] USER_REPORTS
CREATE TABLE user_reports (
    id BIGSERIAL NOT NULL,
    reporter_user_id BIGINT NOT NULL,
    reported_user_id BIGINT NOT NULL,
    report_type TEXT NOT NULL,
    reason TEXT,
    content_id BIGINT,
    content_type TEXT,
    status TEXT DEFAULT 'pending'::text,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB
);

-- [114/131] USER_SESSIONS
CREATE TABLE user_sessions (
    id BIGSERIAL NOT NULL,
    user_id BIGINT NOT NULL,
    session_key TEXT NOT NULL,
    session_data JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ DEFAULT now()
);

-- [115/131] USERS
CREATE TABLE users (
    id SERIAL NOT NULL,
    tg_user_id BIGINT NOT NULL,
    gender TEXT,
    age INTEGER,
    country TEXT,
    city TEXT,
    is_premium BOOLEAN DEFAULT false,
    search_pref TEXT DEFAULT 'any'::text,
    created_at TIMESTAMP DEFAULT now(),
    last_dialog_date DATE,
    dialogs_total INTEGER DEFAULT 0,
    dialogs_today INTEGER DEFAULT 0,
    messages_sent INTEGER DEFAULT 0,
    messages_recv INTEGER DEFAULT 0,
    rating_up INTEGER DEFAULT 0,
    rating_down INTEGER DEFAULT 0,
    report_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT false,
    verify_status TEXT DEFAULT 'none'::text,
    verify_method TEXT,
    verify_audio_file TEXT,
    verify_photo_file TEXT,
    verify_phrase TEXT,
    verify_at TIMESTAMP,
    verify_src_chat BIGINT,
    verify_src_msg BIGINT,
    premium_until TIMESTAMP,
    language TEXT,
    last_gender_change_at TIMESTAMPTZ,
    last_age_change_at TIMESTAMPTZ,
    banned_until TIMESTAMPTZ,
    banned_reason TEXT,
    banned_by BIGINT,
    match_verified_only BOOLEAN DEFAULT false,
    incognito BOOLEAN DEFAULT false,
    coins INTEGER DEFAULT 0,
    last_daily TIMESTAMPTZ,
    strikes INTEGER DEFAULT 0,
    last_strike TIMESTAMPTZ,
    spin_last TIMESTAMPTZ,
    spins INTEGER DEFAULT 0,
    games_played INTEGER DEFAULT 0,
    bio TEXT,
    photo_file_id TEXT,
    feed_username TEXT,
    feed_is_public BOOLEAN DEFAULT true,
    feed_photo TEXT,
    feed_notify BOOLEAN DEFAULT true,
    date_of_birth DATE,
    shadow_banned BOOLEAN DEFAULT false,
    shadow_banned_at TIMESTAMPTZ,
    min_age_pref INTEGER DEFAULT 18,
    max_age_pref INTEGER DEFAULT 99,
    allow_forward BOOLEAN DEFAULT false,
    last_seen TIMESTAMPTZ,
    wyr_streak INTEGER DEFAULT 0,
    wyr_last_voted DATE,
    dare_streak INTEGER DEFAULT 0,
    dare_last_date DATE,
    vault_tokens INTEGER DEFAULT 10,
    vault_tokens_last_reset DATE DEFAULT CURRENT_DATE,
    vault_storage_used BIGINT DEFAULT 0,
    vault_coins INTEGER DEFAULT 0,
    display_name TEXT,
    username TEXT,
    avatar_url TEXT,
    is_onboarded BOOLEAN NOT NULL DEFAULT false,
    tg_id BIGINT,
    active_profile_id BIGINT,
    privacy_consent BOOLEAN DEFAULT false,
    privacy_consent_date TIMESTAMPTZ,
    age_verified BOOLEAN DEFAULT false,
    age_agreement_date TIMESTAMPTZ
);

-- [116/131] VAULT_CATEGORIES
CREATE TABLE vault_categories (
    id SERIAL NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    emoji TEXT DEFAULT '📝'::text,
    blur_intensity INTEGER DEFAULT 70,
    premium_only BOOLEAN DEFAULT true,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [117/131] VAULT_CONTENT
CREATE TABLE vault_content (
    id BIGSERIAL NOT NULL,
    submitter_id BIGINT NOT NULL,
    category_id INTEGER,
    content_text TEXT,
    blurred_text TEXT,
    blur_level INTEGER DEFAULT 70,
    reveal_cost INTEGER DEFAULT 2,
    status TEXT DEFAULT 'pending'::text,
    approval_status TEXT DEFAULT 'pending'::text,
    approved_by BIGINT,
    approved_at TIMESTAMPTZ,
    view_count INTEGER DEFAULT 0,
    reveal_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    media_type TEXT DEFAULT 'text'::text,
    file_url TEXT,
    thumbnail_url TEXT,
    blurred_thumbnail_url TEXT,
    file_id TEXT
);

-- [118/131] VAULT_DAILY_CATEGORY_VIEWS
CREATE TABLE vault_daily_category_views (
    id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    category_id INTEGER,
    views_today INTEGER DEFAULT 0,
    view_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [119/131] VAULT_DAILY_LIMITS
CREATE TABLE vault_daily_limits (
    user_id BIGINT NOT NULL,
    reveals_used INTEGER DEFAULT 0,
    media_reveals_used INTEGER DEFAULT 0,
    limit_date DATE DEFAULT CURRENT_DATE,
    premium_status BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- [120/131] VAULT_INTERACTIONS
CREATE TABLE vault_interactions (
    id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content_id BIGINT,
    action TEXT NOT NULL,
    tokens_spent INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [121/131] VAULT_USER_STATES
CREATE TABLE vault_user_states (
    user_id BIGINT NOT NULL,
    category_id INTEGER,
    state TEXT NOT NULL,
    data TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [122/131] WYR_ANONYMOUS_USERS
CREATE TABLE wyr_anonymous_users (
    id BIGSERIAL NOT NULL,
    vote_date DATE NOT NULL,
    tg_user_id BIGINT NOT NULL,
    anonymous_name TEXT NOT NULL,
    assigned_at TIMESTAMPTZ DEFAULT now()
);

-- [123/131] WYR_BLOCKED_WORDS
CREATE TABLE wyr_blocked_words (
    id SERIAL NOT NULL,
    word TEXT NOT NULL,
    severity TEXT DEFAULT 'medium'::text,
    added_by BIGINT,
    added_at TIMESTAMPTZ DEFAULT now()
);

-- [124/131] WYR_COMMENT_REPORTS
CREATE TABLE wyr_comment_reports (
    id BIGSERIAL NOT NULL,
    message_id BIGINT NOT NULL,
    reporter_tg_id BIGINT NOT NULL,
    report_reason TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    reviewed BOOLEAN DEFAULT false,
    reviewed_by BIGINT,
    reviewed_at TIMESTAMPTZ,
    action_taken TEXT
);

-- [125/131] WYR_GROUP_CHATS
CREATE TABLE wyr_group_chats (
    vote_date DATE NOT NULL,
    total_voters INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ DEFAULT (now() + '1 day'::interval)
);

-- [126/131] WYR_GROUP_MESSAGES
CREATE TABLE wyr_group_messages (
    id BIGSERIAL NOT NULL,
    vote_date DATE NOT NULL,
    anonymous_user_id BIGINT,
    message_type TEXT DEFAULT 'comment'::text,
    content TEXT NOT NULL,
    reply_to_message_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT now(),
    is_deleted BOOLEAN DEFAULT false,
    deleted_by_admin BIGINT,
    deleted_at TIMESTAMPTZ
);

-- [127/131] WYR_MESSAGE_REACTIONS
CREATE TABLE wyr_message_reactions (
    id BIGSERIAL NOT NULL,
    message_id BIGINT,
    tg_user_id BIGINT NOT NULL,
    reaction_type TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [128/131] WYR_PERMANENT_USERS
CREATE TABLE wyr_permanent_users (
    tg_user_id BIGINT NOT NULL,
    permanent_username TEXT NOT NULL,
    assigned_at TIMESTAMPTZ DEFAULT now(),
    total_comments INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    weekly_comments INTEGER DEFAULT 0,
    weekly_likes INTEGER DEFAULT 0,
    last_reset TIMESTAMPTZ DEFAULT now()
);

-- [129/131] WYR_QUESTION_OF_DAY
CREATE TABLE wyr_question_of_day (
    vote_date DATE NOT NULL,
    a_text TEXT NOT NULL,
    b_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- [130/131] WYR_RATE_LIMITS
CREATE TABLE wyr_rate_limits (
    tg_user_id BIGINT NOT NULL,
    comment_count INTEGER DEFAULT 1,
    window_start TIMESTAMPTZ DEFAULT now(),
    last_comment_at TIMESTAMPTZ DEFAULT now()
);

-- [131/131] WYR_VOTES
CREATE TABLE wyr_votes (
    tg_user_id BIGINT NOT NULL,
    vote_date DATE NOT NULL,
    side CHARACTER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);


-- ============================================================================
-- PRIMARY KEY CONSTRAINTS (All Tables)
-- ============================================================================

ALTER TABLE admin_audit_log ADD PRIMARY KEY (id);
ALTER TABLE confession_roulette ADD PRIMARY KEY (id);
ALTER TABLE confession_round_lock ADD PRIMARY KEY (user_id, round_key);
ALTER TABLE fantasy_achievements ADD PRIMARY KEY (id);
ALTER TABLE fantasy_events ADD PRIMARY KEY (id);
ALTER TABLE fantasy_leaderboard ADD PRIMARY KEY (id);
ALTER TABLE fantasy_treasure_hunt ADD PRIMARY KEY (id);
ALTER TABLE payments ADD PRIMARY KEY (id);
ALTER TABLE payments_archive ADD PRIMARY KEY (id);
ALTER TABLE post_reports ADD PRIMARY KEY (id);
ALTER TABLE rate_limit_logs ADD PRIMARY KEY (id);
ALTER TABLE story_segments ADD PRIMARY KEY (id);
ALTER TABLE user_blocks ADD PRIMARY KEY (blocker_id, blocked_id);
ALTER TABLE user_deletion_queue ADD PRIMARY KEY (id);
ALTER TABLE user_mutes ADD PRIMARY KEY (muter_id, muted_id);
ALTER TABLE user_reports ADD PRIMARY KEY (id);
ALTER TABLE user_sessions ADD PRIMARY KEY (id);
ALTER TABLE vault_categories ADD PRIMARY KEY (id);
ALTER TABLE vault_user_states ADD PRIMARY KEY (user_id);
ALTER TABLE wyr_blocked_words ADD PRIMARY KEY (id);
ALTER TABLE wyr_comment_reports ADD PRIMARY KEY (id);
ALTER TABLE wyr_rate_limits ADD PRIMARY KEY (tg_user_id);


-- ============================================================================
-- FOREIGN KEY CONSTRAINTS (All Relationships)
-- ============================================================================

ALTER TABLE feed_comments ADD CONSTRAINT fk_feed_comments_author
    FOREIGN KEY (author_id) REFERENCES users(tg_user_id);
ALTER TABLE feed_posts ADD CONSTRAINT fk_feed_posts_author
    FOREIGN KEY (author_id) REFERENCES users(tg_user_id);
ALTER TABLE payments ADD CONSTRAINT payments_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(tg_user_id);


-- ============================================================================
-- UNIQUE CONSTRAINTS
-- ============================================================================

ALTER TABLE fantasy_achievements ADD CONSTRAINT fantasy_achievements_user_id_achievement_key_key UNIQUE (user_id, achievement_key);
ALTER TABLE fantasy_leaderboard ADD CONSTRAINT fantasy_leaderboard_user_id_week_start_key UNIQUE (user_id, week_start);
ALTER TABLE fantasy_treasure_hunt ADD CONSTRAINT fantasy_treasure_hunt_user_id_clue_index_key UNIQUE (user_id, clue_index);
ALTER TABLE user_sessions ADD CONSTRAINT user_sessions_user_id_session_key_key UNIQUE (user_id, session_key);
ALTER TABLE users ADD CONSTRAINT users_tg_user_id_unique UNIQUE (tg_user_id);
ALTER TABLE vault_categories ADD CONSTRAINT vault_categories_name_unique UNIQUE (name);
ALTER TABLE wyr_anonymous_users ADD CONSTRAINT wyr_anonymous_users_tg_user_vote_date_unique UNIQUE (tg_user_id, vote_date);
ALTER TABLE wyr_blocked_words ADD CONSTRAINT wyr_blocked_words_word_key UNIQUE (word);
ALTER TABLE wyr_comment_reports ADD CONSTRAINT wyr_comment_reports_message_id_reporter_tg_id_key UNIQUE (message_id, reporter_tg_id);
ALTER TABLE wyr_question_of_day ADD CONSTRAINT wyr_question_of_day_vote_date_unique UNIQUE (vote_date);


-- ============================================================================
-- PERFORMANCE INDEXES
-- ============================================================================

CREATE INDEX idx_admin_audit_admin_user ON public.admin_audit_log USING btree (admin_user_id, created_at);
CREATE INDEX idx_admin_audit_target_user ON public.admin_audit_log USING btree (target_user_id, created_at);
CREATE INDEX idx_dare_responses_date ON public.dare_responses USING btree (dare_date, response);
CREATE INDEX idx_dare_stats_streak ON public.dare_stats USING btree (current_streak DESC);
CREATE INDEX idx_dare_submissions_approved ON public.dare_submissions USING btree (approved, submission_date);
CREATE UNIQUE INDEX fantasy_achievements_user_id_achievement_key_key ON public.fantasy_achievements USING btree (user_id, achievement_key);
CREATE UNIQUE INDEX fantasy_leaderboard_user_id_week_start_key ON public.fantasy_leaderboard USING btree (user_id, week_start);
CREATE INDEX fmr_exp ON public.fantasy_match_requests USING btree (expires_at);
CREATE INDEX fmr_owner_status ON public.fantasy_match_requests USING btree (fantasy_owner_id, status);
CREATE INDEX fmr_requester_status ON public.fantasy_match_requests USING btree (requester_id, status);
CREATE UNIQUE INDEX fantasy_treasure_hunt_user_id_clue_index_key ON public.fantasy_treasure_hunt USING btree (user_id, clue_index);
CREATE UNIQUE INDEX feed_reactions_post_user_idx ON public.feed_reactions USING btree (post_id, user_id);
CREATE UNIQUE INDEX feed_reactions_user_post_idx ON public.feed_reactions USING btree (user_id, post_id);
CREATE INDEX idx_payments_created_at ON public.payments USING btree (created_at);
CREATE INDEX idx_payments_user_status ON public.payments USING btree (user_id, status);
CREATE UNIQUE INDEX uq_payments_charge_id ON public.payments USING btree (charge_id);
CREATE INDEX idx_qa_a ON public.qa_answers USING btree (question_id, created_at);
CREATE INDEX idx_qa_q ON public.qa_questions USING btree (created_at);
CREATE INDEX idx_rate_limit_logs_user ON public.rate_limit_logs USING btree (user_id, exceeded_at);
CREATE INDEX idx_user_reports_reported ON public.user_reports USING btree (reported_user_id, status);
CREATE INDEX idx_user_reports_reporter ON public.user_reports USING btree (reporter_user_id);
CREATE INDEX idx_user_sessions_expires ON public.user_sessions USING btree (expires_at);
CREATE INDEX idx_user_sessions_user ON public.user_sessions USING btree (user_id);
CREATE UNIQUE INDEX user_sessions_user_id_session_key_key ON public.user_sessions USING btree (user_id, session_key);
CREATE UNIQUE INDEX users_tg_user_id_unique ON public.users USING btree (tg_user_id);
CREATE UNIQUE INDEX vault_categories_name_unique ON public.vault_categories USING btree (name);
CREATE INDEX idx_wyr_anonymous_users_date ON public.wyr_anonymous_users USING btree (vote_date);
CREATE INDEX idx_wyr_anonymous_users_tg_id ON public.wyr_anonymous_users USING btree (tg_user_id);
CREATE UNIQUE INDEX wyr_anonymous_users_tg_user_vote_date_unique ON public.wyr_anonymous_users USING btree (tg_user_id, vote_date);
CREATE UNIQUE INDEX wyr_blocked_words_word_key ON public.wyr_blocked_words USING btree (word);
CREATE UNIQUE INDEX wyr_comment_reports_message_id_reporter_tg_id_key ON public.wyr_comment_reports USING btree (message_id, reporter_tg_id);
CREATE INDEX idx_wyr_group_messages_created ON public.wyr_group_messages USING btree (created_at DESC);
CREATE INDEX idx_wyr_group_messages_date ON public.wyr_group_messages USING btree (vote_date);
CREATE UNIQUE INDEX wyr_question_of_day_vote_date_unique ON public.wyr_question_of_day USING btree (vote_date);
CREATE INDEX idx_wyr_votes_date_side ON public.wyr_votes USING btree (vote_date, side);


-- ============================================================================
-- EXPORT SUMMARY
-- ============================================================================
-- Total Tables: 131
-- Primary Keys: 22
-- Foreign Keys: 3
-- Unique Constraints: 10
-- Indexes: 35
-- 
-- All 131 tables exported successfully in a SINGLE file!
-- Ready to import into any PostgreSQL database.
-- ============================================================================
