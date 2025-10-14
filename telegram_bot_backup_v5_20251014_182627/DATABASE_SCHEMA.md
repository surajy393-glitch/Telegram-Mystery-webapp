# LuvHive Database Schema - Complete Table Reference

## ✅ TOTAL TABLES: 119

### 1. Users & Authentication (10 tables)
- **users** - Main user accounts and profiles
- **user_interests** - User interest tags
- **user_badges** - Achievement badges
- **user_blocks** - Blocked users list
- **user_follows** - User following relationships
- **user_mutes** - Muted users
- **profiles** - Extended user profile data
- **feed_profiles** - Social feed profile settings
- **miniapp_profiles** - Mini-app specific profiles
- **social_profiles** - Social network profiles

### 2. Chat & Messaging (8 tables)
- **secret_chats** - Anonymous chat sessions
- **friend_chats** - Friend-to-friend messaging
- **friend_msg_requests** - Friend message requests
- **chat_ratings** - Chat session ratings
- **chat_reports** - User reports from chats
- **chat_extensions** - Paid chat time extensions
- **blocked_users** - User blocking relationships
- **notifications** - User notifications

### 3. Fantasy Match System (12 tables) 🆕
- **fantasy_submissions** - User fantasy submissions (with moderation status)
- **fantasy_matches** - Matched fantasy pairs
- **fantasy_match_requests** - Connection requests between users
- **fantasy_match_notifs** - Match notifications sent
- **fantasy_chats** - Active fantasy chat rooms
- **fantasy_chat_sessions** - Fantasy chat session records
- **fantasy_stats** - Fantasy engagement statistics
- **fantasy_board_reactions** - Reactions to fantasy posts
- **fantasy_achievements** - User achievement tracking 🆕
- **fantasy_leaderboard** - Weekly leaderboard rankings 🆕
- **fantasy_events** - Special event management 🆕
- **fantasy_treasure_hunt** - Treasure hunt progress 🆕

### 4. Social Features (21 tables)
- **posts** - User posts
- **social_posts** - Social network posts
- **miniapp_posts** - Mini-app posts
- **feed_posts** - Public feed posts
- **comments** - Post comments
- **social_comments** - Social network comments
- **feed_comments** - Feed post comments
- **miniapp_comments** - Mini-app comments
- **likes** - Post likes
- **social_likes** - Social network likes
- **feed_likes** - Feed post likes
- **miniapp_likes** - Mini-app likes
- **post_likes** - Post like tracking
- **comment_likes** - Comment likes
- **feed_reactions** - Emoji reactions on feed
- **feed_views** - Post view tracking
- **miniapp_post_views** - Mini-app post views
- **miniapp_saves** - Saved mini-app content
- **miniapp_follows** - Mini-app user follows
- **post_reports** - Post-specific reports
- **reports** - General user reports

### 5. Friends System (6 tables)
- **friends** - Friend relationships
- **social_friends** - Social network friends
- **friend_requests** - Pending friend requests
- **social_friend_requests** - Social network friend requests
- **friendship_levels** - Friendship engagement levels
- **secret_crush** - Secret crush feature

### 6. Confession Roulette (10 tables)
- **confessions** - Anonymous confessions
- **confession_deliveries** - Confession delivery records
- **confession_reactions** - Reactions to confessions
- **confession_replies** - Replies to confessions
- **confession_stats** - User confession statistics
- **confession_leaderboard** - Top confessors leaderboard
- **confession_mutes** - Muted confessions
- **pending_confessions** - Confessions awaiting delivery
- **pending_confession_replies** - Pending confession replies
- **crush_leaderboard** - Weekly crush leaderboard

### 7. Games & Interactive Features (13 tables)
- **naughty_wyr_questions** - Would You Rather questions
- **naughty_wyr_votes** - WYR vote records
- **naughty_wyr_deliveries** - WYR delivery tracking
- **wyr_question_of_day** - Daily WYR question
- **wyr_votes** - WYR voting history
- **wyr_anonymous_users** - Anonymous WYR participants
- **wyr_permanent_users** - Registered WYR users
- **wyr_group_chats** - WYR group chat sessions
- **wyr_group_messages** - WYR group messages
- **wyr_message_reactions** - WYR message reactions
- **game_questions** - General game questions
- **poll_options** - Poll answer options
- **poll_votes** - Poll voting records

### 8. Dare System (5 tables)
- **daily_dare_selection** - Selected daily dares
- **dare_submissions** - User-submitted dares
- **dare_responses** - User dare responses
- **dare_stats** - User dare statistics
- **dare_feedback** - Dare completion feedback

### 9. Polls (1 table)
- **polls** - User-created polls

### 10. Blur Vault - Premium Content (6 tables)
- **vault_content** - Locked premium content
- **vault_categories** - Content categories
- **vault_interactions** - User interactions with content
- **vault_user_states** - User vault states
- **vault_daily_limits** - Daily usage limits
- **vault_daily_category_views** - Category view tracking

### 11. Stories & Content (5 tables)
- **stories** - User stories
- **sensual_stories** - Adult-themed stories
- **sensual_reactions** - Story reactions
- **story_segments** - Story parts/chapters
- **story_views** - Story view tracking

### 12. After Dark Sessions (4 tables)
- **ad_sessions** - After Dark chat sessions
- **ad_participants** - Session participants
- **ad_messages** - Session messages
- **ad_prompts** - Session prompts/scenarios

### 13. Midnight University Chronicles (13 tables)
- **muc_series** - Midnight University series
- **muc_episodes** - Episode records
- **muc_characters** - Character database
- **muc_char_questions** - Character questions
- **muc_char_options** - Character quiz options
- **muc_char_votes** - Character quiz votes
- **muc_polls** - MUC polls
- **muc_poll_options** - MUC poll options
- **muc_votes** - MUC voting records
- **muc_theories** - User theories
- **muc_theory_likes** - Theory likes
- **muc_user_engagement** - User engagement tracking
- **muc_user_votes** - User voting records

### 14. Q&A System (2 tables)
- **qa_questions** - User questions
- **qa_answers** - User answers

### 15. Premium & Payments (2 tables)
- **referrals** - User referral tracking
- **idempotency_keys** - Payment deduplication

### 16. Moderation & Safety (2 tables)
- **moderation_events** - Moderation action log
- **maintenance_log** - System maintenance records

---

## 📋 Complete Table List (All 119 Tables)

1. ad_messages
2. ad_participants
3. ad_prompts
4. ad_sessions
5. blocked_users
6. chat_extensions
7. chat_ratings
8. chat_reports
9. comment_likes
10. comments
11. confession_deliveries
12. confession_leaderboard
13. confession_mutes
14. confession_reactions
15. confession_replies
16. confession_stats
17. confessions
18. crush_leaderboard
19. daily_dare_selection
20. dare_feedback
21. dare_responses
22. dare_stats
23. dare_submissions
24. fantasy_achievements 🆕
25. fantasy_board_reactions
26. fantasy_chat_sessions
27. fantasy_chats
28. fantasy_events 🆕
29. fantasy_leaderboard 🆕
30. fantasy_match_notifs
31. fantasy_match_requests
32. fantasy_matches
33. fantasy_stats
34. fantasy_submissions
35. fantasy_treasure_hunt 🆕
36. feed_comments
37. feed_likes
38. feed_posts
39. feed_profiles
40. feed_reactions
41. feed_views
42. friend_chats
43. friend_msg_requests
44. friend_requests
45. friends
46. friendship_levels
47. game_questions
48. idempotency_keys
49. likes
50. maintenance_log
51. miniapp_comments
52. miniapp_follows
53. miniapp_likes
54. miniapp_post_views
55. miniapp_posts
56. miniapp_profiles
57. miniapp_saves
58. moderation_events
59. muc_char_options
60. muc_char_questions
61. muc_char_votes
62. muc_characters
63. muc_episodes
64. muc_poll_options
65. muc_polls
66. muc_series
67. muc_theories
68. muc_theory_likes
69. muc_user_engagement
70. muc_votes
71. naughty_wyr_deliveries
72. naughty_wyr_questions
73. naughty_wyr_votes
74. notifications
75. pending_confession_replies
76. pending_confessions
77. poll_options
78. poll_votes
79. polls
80. post_likes
81. post_reports
82. posts
83. profiles
84. qa_answers
85. qa_questions
86. referrals
87. reports
88. secret_chats
89. secret_crush
90. sensual_reactions
91. sensual_stories
92. social_comments
93. social_friend_requests
94. social_friends
95. social_likes
96. social_posts
97. social_profiles
98. stories
99. story_segments
100. story_views
101. user_badges
102. user_blocks
103. user_follows
104. user_interests
105. user_mutes
106. users
107. vault_categories
108. vault_content
109. vault_daily_category_views
110. vault_daily_limits
111. vault_interactions
112. vault_user_states
113. wyr_anonymous_users
114. wyr_group_chats
115. wyr_group_messages
116. wyr_message_reactions
117. wyr_permanent_users
118. wyr_question_of_day
119. wyr_votes

---

## 🔑 Key Schema Details

### 🆕 Fantasy Achievements (NEW)
```sql
CREATE TABLE fantasy_achievements (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    achievement_key TEXT NOT NULL,
    earned_at TIMESTAMPTZ DEFAULT NOW(),
    stars_earned INTEGER DEFAULT 0,
    UNIQUE(user_id, achievement_key)
);
```

### 🆕 Fantasy Leaderboard (NEW)
```sql
CREATE TABLE fantasy_leaderboard (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    week_start DATE NOT NULL,
    total_reactions INTEGER DEFAULT 0,
    total_matches INTEGER DEFAULT 0,
    total_chats INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2) DEFAULT 0.0,
    rank_position INTEGER DEFAULT 999,
    UNIQUE(user_id, week_start)
);
```

### 🆕 Fantasy Events (NEW)
```sql
CREATE TABLE fantasy_events (
    id SERIAL PRIMARY KEY,
    event_key TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    participants_count INTEGER DEFAULT 0
);
```

### 🆕 Fantasy Treasure Hunt (NEW)
```sql
CREATE TABLE fantasy_treasure_hunt (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    clue_index INTEGER NOT NULL,
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    stars_earned INTEGER DEFAULT 0,
    UNIQUE(user_id, clue_index)
);
```

### Fantasy Submissions (with Moderation)
```sql
CREATE TABLE fantasy_submissions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    gender TEXT NOT NULL,
    fantasy_text TEXT NOT NULL,
    vibe TEXT NOT NULL,
    keywords TEXT[] NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    active BOOLEAN DEFAULT TRUE,
    status TEXT DEFAULT 'pending'  -- pending/approved/rejected
);
```

### Users Table
```sql
CREATE TABLE users (
    tg_user_id BIGINT PRIMARY KEY,
    username TEXT,
    display_name TEXT,
    age INTEGER,
    gender TEXT,
    city TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    premium_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 📊 Database Statistics

- **Total Tables:** 119 ✅
- **Core Feature Categories:** 16
- **NEW Tables Added Today:** 4 (fantasy powerup features)
- **Moderation-Ready:** Yes (Fantasy, Confessions, Dares, Stories)
- **Premium Features:** Integrated (Vault, Extensions, Referrals, Achievements)
- **Safety Features:** Full reporting, blocking, and moderation system
- **Analytics:** Comprehensive stats tracking across all features
- **Social Features:** 21 tables for multi-platform social networking
- **Gaming Features:** 13+ tables for interactive games
- **Content Delivery:** Scheduled confession/dare/WYR systems
- **Engagement Systems:** Achievements, leaderboards, events, treasure hunts

---

## 🎯 Recent Updates (October 14, 2025)

### Fantasy Match Powerup Features Added:
1. **Achievements System** - 6 achievement types with star rewards
2. **Weekly Leaderboards** - Competitive rankings with success metrics
3. **Fantasy Events** - Special timed events (Full Moon, Valentine's, etc.)
4. **Treasure Hunt** - Gamified discovery challenges

All fantasy submissions now require admin approval before appearing on Fantasy Board for safety compliance.
