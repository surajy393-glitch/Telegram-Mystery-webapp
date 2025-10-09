--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (165f042)
-- Dumped by pg_dump version 16.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


--
-- Name: cleanup_expired_saves(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.cleanup_expired_saves() RETURNS void
    LANGUAGE plpgsql
    AS $$
                BEGIN
                    DELETE FROM miniapp_saves WHERE expires_at <= NOW();
                END;
                $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ad_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ad_messages (
    id bigint NOT NULL,
    session_id bigint,
    user_id bigint,
    anon_name text,
    msg_type text NOT NULL,
    content text,
    meta jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: ad_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ad_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ad_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ad_messages_id_seq OWNED BY public.ad_messages.id;


--
-- Name: ad_participants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ad_participants (
    id bigint NOT NULL,
    session_id bigint,
    user_id bigint NOT NULL,
    anon_name text NOT NULL,
    joined_at timestamp with time zone DEFAULT now(),
    left_at timestamp with time zone
);


--
-- Name: ad_participants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ad_participants_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ad_participants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ad_participants_id_seq OWNED BY public.ad_participants.id;


--
-- Name: ad_prompts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ad_prompts (
    id bigint NOT NULL,
    session_id bigint,
    kind text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: ad_prompts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ad_prompts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ad_prompts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ad_prompts_id_seq OWNED BY public.ad_prompts.id;


--
-- Name: ad_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ad_sessions (
    id bigint NOT NULL,
    started_at timestamp with time zone DEFAULT now(),
    ends_at timestamp with time zone NOT NULL,
    vibe text,
    status text DEFAULT 'live'::text
);


--
-- Name: ad_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ad_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ad_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ad_sessions_id_seq OWNED BY public.ad_sessions.id;


--
-- Name: blocked_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.blocked_users (
    user_id bigint NOT NULL,
    blocked_uid bigint NOT NULL,
    added_at timestamp with time zone DEFAULT now()
);


--
-- Name: chat_extensions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_extensions (
    id integer NOT NULL,
    match_id bigint NOT NULL,
    extended_by bigint NOT NULL,
    stars_paid integer DEFAULT 50,
    minutes_added integer DEFAULT 30,
    extended_at timestamp with time zone DEFAULT now()
);


--
-- Name: chat_extensions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_extensions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_extensions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_extensions_id_seq OWNED BY public.chat_extensions.id;


--
-- Name: chat_ratings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_ratings (
    id integer NOT NULL,
    rater_id bigint NOT NULL,
    ratee_id bigint NOT NULL,
    value smallint NOT NULL,
    reason text,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: chat_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_ratings_id_seq OWNED BY public.chat_ratings.id;


--
-- Name: chat_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_reports (
    id bigint NOT NULL,
    reporter_tg_id bigint NOT NULL,
    reported_tg_id bigint NOT NULL,
    in_secret boolean DEFAULT false NOT NULL,
    text text,
    media_file_id text,
    media_type text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: chat_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_reports_id_seq OWNED BY public.chat_reports.id;


--
-- Name: comment_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment_likes (
    comment_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    post_id integer,
    user_id bigint,
    text text,
    created_at timestamp without time zone,
    pinned boolean DEFAULT false NOT NULL,
    pinned_at timestamp with time zone,
    pinned_by_user_id integer,
    profile_id bigint
);


--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: confession_deliveries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_deliveries (
    id bigint NOT NULL,
    confession_id bigint NOT NULL,
    user_id bigint NOT NULL,
    delivered_at timestamp with time zone DEFAULT now()
);


--
-- Name: confession_deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.confession_deliveries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: confession_deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.confession_deliveries_id_seq OWNED BY public.confession_deliveries.id;


--
-- Name: confession_leaderboard; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_leaderboard (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    period character varying(20) NOT NULL,
    confession_count integer DEFAULT 0,
    total_reactions_received integer DEFAULT 0,
    replies_received integer DEFAULT 0,
    rank_type character varying(30) NOT NULL,
    rank_position integer DEFAULT 0,
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: confession_leaderboard_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.confession_leaderboard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: confession_leaderboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.confession_leaderboard_id_seq OWNED BY public.confession_leaderboard.id;


--
-- Name: confession_mutes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_mutes (
    user_id bigint NOT NULL,
    confession_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: confession_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_reactions (
    id bigint NOT NULL,
    confession_id bigint NOT NULL,
    user_id bigint NOT NULL,
    reaction_type character varying(10) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    approved boolean DEFAULT false,
    approved_at timestamp with time zone
);


--
-- Name: confession_reactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.confession_reactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: confession_reactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.confession_reactions_id_seq OWNED BY public.confession_reactions.id;


--
-- Name: confession_replies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_replies (
    id bigint NOT NULL,
    original_confession_id bigint NOT NULL,
    replier_user_id bigint NOT NULL,
    reply_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    reply_reactions integer DEFAULT 0,
    is_anonymous boolean DEFAULT true,
    approved boolean DEFAULT false,
    approved_at timestamp with time zone
);


--
-- Name: confession_replies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.confession_replies_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: confession_replies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.confession_replies_id_seq OWNED BY public.confession_replies.id;


--
-- Name: confession_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confession_stats (
    user_id bigint NOT NULL,
    total_confessions integer DEFAULT 0,
    weekly_confessions integer DEFAULT 0,
    current_streak integer DEFAULT 0,
    longest_streak integer DEFAULT 0,
    total_reactions_received integer DEFAULT 0,
    total_replies_received integer DEFAULT 0,
    best_confessor_score integer DEFAULT 0,
    last_confession_date date,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: confessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.confessions (
    id integer NOT NULL,
    author_id bigint NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    delivered boolean DEFAULT false,
    delivered_at timestamp with time zone,
    delivered_to bigint,
    system_seed boolean DEFAULT false,
    deleted_at timestamp with time zone
);


--
-- Name: confessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.confessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: confessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.confessions_id_seq OWNED BY public.confessions.id;


--
-- Name: crush_leaderboard; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.crush_leaderboard (
    user_id bigint NOT NULL,
    crush_count integer DEFAULT 0,
    week_start date DEFAULT CURRENT_DATE,
    last_updated timestamp with time zone DEFAULT now()
);


--
-- Name: daily_dare_selection; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.daily_dare_selection (
    dare_date date NOT NULL,
    dare_text text NOT NULL,
    dare_source character varying(20) DEFAULT 'community'::character varying,
    source_id integer,
    created_at timestamp with time zone DEFAULT now(),
    submitter_id bigint,
    category character varying(20) DEFAULT 'general'::character varying,
    difficulty character varying(10) DEFAULT 'medium'::character varying,
    creator_notified boolean DEFAULT false
);


--
-- Name: dare_feedback; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dare_feedback (
    id integer NOT NULL,
    submission_id integer,
    event_type character varying(20),
    user_id bigint,
    dare_date date,
    notified boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT dare_feedback_event_type_check CHECK (((event_type)::text = ANY (ARRAY[('selected'::character varying)::text, ('accepted'::character varying)::text, ('completed'::character varying)::text])))
);


--
-- Name: dare_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dare_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dare_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dare_feedback_id_seq OWNED BY public.dare_feedback.id;


--
-- Name: dare_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dare_responses (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    dare_date date NOT NULL,
    response character varying(10),
    response_time timestamp with time zone DEFAULT now(),
    completion_claimed boolean DEFAULT false,
    difficulty_selected character varying(10) DEFAULT 'medium'::character varying,
    dare_text text,
    CONSTRAINT dare_responses_response_check CHECK (((response)::text = ANY (ARRAY[('accepted'::character varying)::text, ('declined'::character varying)::text, ('expired'::character varying)::text])))
);


--
-- Name: dare_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dare_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dare_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dare_responses_id_seq OWNED BY public.dare_responses.id;


--
-- Name: dare_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dare_stats (
    user_id bigint NOT NULL,
    current_streak integer DEFAULT 0,
    longest_streak integer DEFAULT 0,
    total_accepted integer DEFAULT 0,
    total_declined integer DEFAULT 0,
    total_expired integer DEFAULT 0,
    last_dare_date date,
    badges text[] DEFAULT '{}'::text[],
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: dare_submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dare_submissions (
    id integer NOT NULL,
    submitter_id bigint NOT NULL,
    dare_text text NOT NULL,
    category character varying(20) DEFAULT 'general'::character varying,
    difficulty character varying(10) DEFAULT 'medium'::character varying,
    approved boolean DEFAULT false,
    admin_approved_by bigint,
    submission_date date DEFAULT CURRENT_DATE,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: dare_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dare_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dare_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dare_submissions_id_seq OWNED BY public.dare_submissions.id;


--
-- Name: fantasy_board_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_board_reactions (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    fantasy_id bigint NOT NULL,
    reaction_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: fantasy_board_reactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_board_reactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_board_reactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_board_reactions_id_seq OWNED BY public.fantasy_board_reactions.id;


--
-- Name: fantasy_chat_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_chat_sessions (
    id bigint NOT NULL,
    a_id bigint NOT NULL,
    b_id bigint NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    ended_at timestamp with time zone,
    status text DEFAULT 'active'::text NOT NULL
);


--
-- Name: fantasy_chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_chat_sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_chat_sessions_id_seq OWNED BY public.fantasy_chat_sessions.id;


--
-- Name: fantasy_chats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_chats (
    id integer NOT NULL,
    match_id integer,
    chat_room_id text NOT NULL,
    started_at timestamp without time zone DEFAULT now(),
    expires_at timestamp without time zone DEFAULT (now() + '00:15:00'::interval),
    boy_joined boolean DEFAULT false,
    girl_joined boolean DEFAULT false,
    message_count integer DEFAULT 0
);


--
-- Name: fantasy_chats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_chats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_chats_id_seq OWNED BY public.fantasy_chats.id;


--
-- Name: fantasy_match_notifs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_match_notifs (
    id integer NOT NULL,
    match_id integer,
    user_id bigint NOT NULL,
    sent_at timestamp without time zone DEFAULT now()
);


--
-- Name: fantasy_match_notifs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_match_notifs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_match_notifs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_match_notifs_id_seq OWNED BY public.fantasy_match_notifs.id;


--
-- Name: fantasy_match_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_match_requests (
    id integer NOT NULL,
    requester_id bigint NOT NULL,
    fantasy_id bigint NOT NULL,
    fantasy_owner_id bigint NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    responded_at timestamp with time zone,
    expires_at timestamp with time zone NOT NULL,
    cancelled_by_user_id bigint,
    cancelled_at timestamp with time zone,
    cancel_reason text,
    version integer DEFAULT 1
);


--
-- Name: fantasy_match_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_match_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_match_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_match_requests_id_seq OWNED BY public.fantasy_match_requests.id;


--
-- Name: fantasy_matches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_matches (
    id integer NOT NULL,
    boy_id bigint NOT NULL,
    girl_id bigint NOT NULL,
    fantasy_key text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    expires_at timestamp without time zone DEFAULT (now() + '24:00:00'::interval),
    boy_ready boolean DEFAULT false,
    girl_ready boolean DEFAULT false,
    boy_is_premium boolean DEFAULT false,
    connected_at timestamp without time zone,
    status character varying(20) DEFAULT 'pending'::character varying,
    chat_id text,
    vibe text,
    shared_keywords text[]
);


--
-- Name: fantasy_matches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_matches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_matches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_matches_id_seq OWNED BY public.fantasy_matches.id;


--
-- Name: fantasy_stats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_stats (
    fantasy_id bigint NOT NULL,
    views_count integer DEFAULT 0,
    reactions_count integer DEFAULT 0,
    matches_count integer DEFAULT 0,
    success_rate numeric(5,2) DEFAULT 0.0,
    last_updated timestamp with time zone DEFAULT now()
);


--
-- Name: fantasy_submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fantasy_submissions (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    gender text NOT NULL,
    fantasy_text text NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    is_active boolean DEFAULT true,
    fantasy_key text,
    submitted_count integer DEFAULT 1,
    vibe text,
    keywords text[],
    active boolean DEFAULT true
);


--
-- Name: fantasy_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fantasy_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fantasy_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fantasy_submissions_id_seq OWNED BY public.fantasy_submissions.id;


--
-- Name: feed_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_comments (
    id bigint NOT NULL,
    post_id bigint,
    author_id bigint NOT NULL,
    author_name text NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: feed_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feed_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feed_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feed_comments_id_seq OWNED BY public.feed_comments.id;


--
-- Name: feed_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_likes (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: feed_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_posts (
    id bigint NOT NULL,
    author_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    content_type text,
    file_id text,
    text text,
    reaction_count integer DEFAULT 0,
    comment_count integer DEFAULT 0,
    profile_id bigint
);


--
-- Name: feed_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.feed_posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: feed_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.feed_posts_id_seq OWNED BY public.feed_posts.id;


--
-- Name: feed_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_profiles (
    uid bigint NOT NULL,
    username text,
    bio text,
    is_public boolean DEFAULT true,
    photo text
);


--
-- Name: feed_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_reactions (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    emoji text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: feed_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.feed_views (
    post_id bigint NOT NULL,
    viewer_id bigint NOT NULL,
    viewed_at timestamp with time zone DEFAULT now()
);


--
-- Name: friend_chats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.friend_chats (
    id bigint NOT NULL,
    a bigint,
    b bigint,
    opened_at timestamp with time zone DEFAULT now(),
    closed_at timestamp with time zone
);


--
-- Name: friend_chats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.friend_chats_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: friend_chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.friend_chats_id_seq OWNED BY public.friend_chats.id;


--
-- Name: friend_msg_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.friend_msg_requests (
    id bigint NOT NULL,
    sender bigint,
    receiver bigint,
    text text,
    created_at timestamp with time zone DEFAULT now(),
    status text DEFAULT 'pending'::text
);


--
-- Name: friend_msg_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.friend_msg_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: friend_msg_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.friend_msg_requests_id_seq OWNED BY public.friend_msg_requests.id;


--
-- Name: friend_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.friend_requests (
    requester_id bigint NOT NULL,
    target_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: friends; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.friends (
    user_id bigint NOT NULL,
    friend_id bigint NOT NULL,
    added_at timestamp with time zone DEFAULT now()
);


--
-- Name: friendship_levels; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.friendship_levels (
    user1_id bigint NOT NULL,
    user2_id bigint NOT NULL,
    interaction_count integer DEFAULT 0,
    level integer DEFAULT 1,
    last_interaction timestamp with time zone DEFAULT now(),
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: game_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.game_questions (
    game text,
    question text,
    added_by bigint,
    added_at timestamp with time zone DEFAULT now()
);


--
-- Name: idempotency_keys; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.idempotency_keys (
    key text NOT NULL,
    operation text NOT NULL,
    result jsonb,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.likes (
    id integer NOT NULL,
    post_id integer,
    user_id bigint,
    created_at timestamp without time zone
);


--
-- Name: likes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.likes_id_seq OWNED BY public.likes.id;


--
-- Name: maintenance_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.maintenance_log (
    id bigint NOT NULL,
    operation text NOT NULL,
    status text NOT NULL,
    details jsonb,
    duration_seconds real,
    executed_at timestamp with time zone DEFAULT now()
);


--
-- Name: maintenance_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.maintenance_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: maintenance_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.maintenance_log_id_seq OWNED BY public.maintenance_log.id;


--
-- Name: miniapp_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_comments (
    id bigint NOT NULL,
    post_id bigint NOT NULL,
    author_id bigint NOT NULL,
    text text NOT NULL,
    parent_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT miniapp_comments_text_check CHECK (((length(text) >= 1) AND (length(text) <= 500)))
);


--
-- Name: miniapp_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.miniapp_comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: miniapp_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.miniapp_comments_id_seq OWNED BY public.miniapp_comments.id;


--
-- Name: miniapp_follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_follows (
    follower_id bigint NOT NULL,
    followee_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    status text DEFAULT 'approved'::text NOT NULL,
    CONSTRAINT miniapp_follows_check CHECK ((follower_id <> followee_id)),
    CONSTRAINT miniapp_follows_status_check CHECK ((status = ANY (ARRAY['approved'::text, 'pending'::text])))
);


--
-- Name: miniapp_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_likes (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: miniapp_post_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_post_views (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    viewed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: miniapp_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_posts (
    id bigint NOT NULL,
    author_id bigint NOT NULL,
    type text DEFAULT 'text'::text NOT NULL,
    caption text,
    media_url text,
    media_type text,
    visibility text DEFAULT 'public'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT miniapp_posts_caption_check CHECK ((length(caption) <= 2000)),
    CONSTRAINT miniapp_posts_type_check CHECK ((type = ANY (ARRAY['text'::text, 'photo'::text, 'video'::text]))),
    CONSTRAINT miniapp_posts_visibility_check CHECK ((visibility = ANY (ARRAY['public'::text, 'followers'::text, 'private'::text]))),
    CONSTRAINT valid_media CHECK ((((type = 'text'::text) AND (media_url IS NULL)) OR ((type = ANY (ARRAY['photo'::text, 'video'::text])) AND (media_url IS NOT NULL))))
);


--
-- Name: miniapp_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.miniapp_posts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: miniapp_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.miniapp_posts_id_seq OWNED BY public.miniapp_posts.id;


--
-- Name: miniapp_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_profiles (
    user_id bigint NOT NULL,
    username text,
    display_name text,
    bio text,
    avatar_url text,
    is_private boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT miniapp_profiles_bio_check CHECK (((bio IS NULL) OR (length(bio) <= 500))),
    CONSTRAINT miniapp_profiles_display_name_check CHECK (((display_name IS NULL) OR (length(display_name) <= 100))),
    CONSTRAINT miniapp_profiles_username_check CHECK (((username IS NULL) OR ((length(username) >= 3) AND (length(username) <= 30))))
);


--
-- Name: miniapp_saves; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.miniapp_saves (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone DEFAULT (now() + '72:00:00'::interval) NOT NULL,
    CONSTRAINT miniapp_saves_check CHECK ((expires_at > created_at))
);


--
-- Name: moderation_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moderation_events (
    id bigint NOT NULL,
    tg_user_id bigint,
    kind text NOT NULL,
    token text NOT NULL,
    sample text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: moderation_events_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.moderation_events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: moderation_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.moderation_events_id_seq OWNED BY public.moderation_events.id;


--
-- Name: muc_char_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_char_options (
    id integer NOT NULL,
    question_id integer NOT NULL,
    opt_key text NOT NULL,
    text text NOT NULL
);


--
-- Name: muc_char_options_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_char_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_char_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_char_options_id_seq OWNED BY public.muc_char_options.id;


--
-- Name: muc_char_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_char_questions (
    id integer NOT NULL,
    series_id integer NOT NULL,
    prompt text NOT NULL,
    question_key text NOT NULL,
    active_from_episode_id integer
);


--
-- Name: muc_char_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_char_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_char_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_char_questions_id_seq OWNED BY public.muc_char_questions.id;


--
-- Name: muc_char_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_char_votes (
    id integer NOT NULL,
    question_id integer NOT NULL,
    option_id integer NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: muc_char_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_char_votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_char_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_char_votes_id_seq OWNED BY public.muc_char_votes.id;


--
-- Name: muc_characters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_characters (
    id integer NOT NULL,
    series_id integer NOT NULL,
    name text NOT NULL,
    role text NOT NULL,
    bio_md text,
    attributes jsonb DEFAULT '{}'::jsonb,
    secrets jsonb DEFAULT '{}'::jsonb
);


--
-- Name: muc_characters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_characters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_characters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_characters_id_seq OWNED BY public.muc_characters.id;


--
-- Name: muc_episodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_episodes (
    id integer NOT NULL,
    series_id integer NOT NULL,
    idx integer NOT NULL,
    title text NOT NULL,
    teaser_md text,
    body_md text,
    cliff_md text,
    publish_at timestamp with time zone,
    close_at timestamp with time zone,
    status text DEFAULT 'draft'::text NOT NULL,
    CONSTRAINT muc_episodes_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'published'::text, 'voting'::text, 'closed'::text])))
);


--
-- Name: muc_episodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_episodes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_episodes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_episodes_id_seq OWNED BY public.muc_episodes.id;


--
-- Name: muc_poll_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_poll_options (
    id integer NOT NULL,
    poll_id integer NOT NULL,
    opt_key text,
    text text NOT NULL,
    next_hint text,
    idx integer DEFAULT 0
);


--
-- Name: muc_poll_options_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_poll_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_poll_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_poll_options_id_seq OWNED BY public.muc_poll_options.id;


--
-- Name: muc_polls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_polls (
    id integer NOT NULL,
    episode_id integer NOT NULL,
    prompt text NOT NULL,
    layer text DEFAULT 'surface'::text NOT NULL,
    allow_multi boolean DEFAULT false,
    CONSTRAINT muc_polls_layer_check CHECK ((layer = ANY (ARRAY['surface'::text, 'deeper'::text, 'deepest'::text])))
);


--
-- Name: muc_polls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_polls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_polls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_polls_id_seq OWNED BY public.muc_polls.id;


--
-- Name: muc_series; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_series (
    id integer NOT NULL,
    slug text NOT NULL,
    title text NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: muc_series_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_series_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_series_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_series_id_seq OWNED BY public.muc_series.id;


--
-- Name: muc_theories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_theories (
    id integer NOT NULL,
    episode_id integer NOT NULL,
    user_id bigint NOT NULL,
    text text NOT NULL,
    likes integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: muc_theories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_theories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_theories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_theories_id_seq OWNED BY public.muc_theories.id;


--
-- Name: muc_theory_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_theory_likes (
    id integer NOT NULL,
    theory_id integer NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: muc_theory_likes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_theory_likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_theory_likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_theory_likes_id_seq OWNED BY public.muc_theory_likes.id;


--
-- Name: muc_user_engagement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_user_engagement (
    user_id bigint NOT NULL,
    streak_days integer DEFAULT 0,
    detective_score integer DEFAULT 0,
    last_seen_episode_id integer
);


--
-- Name: muc_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.muc_votes (
    id integer NOT NULL,
    poll_id integer NOT NULL,
    option_id integer NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: muc_votes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.muc_votes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: muc_votes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.muc_votes_id_seq OWNED BY public.muc_votes.id;


--
-- Name: naughty_wyr_deliveries; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.naughty_wyr_deliveries (
    question_id bigint NOT NULL,
    user_id bigint NOT NULL,
    delivered_at timestamp with time zone DEFAULT now()
);


--
-- Name: naughty_wyr_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.naughty_wyr_questions (
    id bigint NOT NULL,
    question text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    system_seed boolean DEFAULT true
);


--
-- Name: naughty_wyr_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.naughty_wyr_questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: naughty_wyr_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.naughty_wyr_questions_id_seq OWNED BY public.naughty_wyr_questions.id;


--
-- Name: naughty_wyr_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.naughty_wyr_votes (
    question_id bigint NOT NULL,
    user_id bigint NOT NULL,
    choice text NOT NULL,
    voted_at timestamp with time zone DEFAULT now()
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id bigint,
    ntype character varying(24),
    actor bigint,
    post_id integer,
    created_at timestamp without time zone,
    read boolean
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: pending_confession_replies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pending_confession_replies (
    id integer NOT NULL,
    original_confession_id bigint NOT NULL,
    replier_user_id bigint NOT NULL,
    reply_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    admin_notified boolean DEFAULT false,
    is_voice boolean DEFAULT false,
    voice_file_id text,
    voice_duration integer
);


--
-- Name: pending_confession_replies_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pending_confession_replies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pending_confession_replies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pending_confession_replies_id_seq OWNED BY public.pending_confession_replies.id;


--
-- Name: pending_confessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pending_confessions (
    id bigint NOT NULL,
    author_id bigint NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    admin_notified boolean DEFAULT false,
    is_voice boolean DEFAULT false,
    voice_file_id text,
    voice_duration integer
);


--
-- Name: pending_confessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pending_confessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pending_confessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pending_confessions_id_seq OWNED BY public.pending_confessions.id;


--
-- Name: poll_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.poll_options (
    id bigint NOT NULL,
    poll_id bigint NOT NULL,
    text text NOT NULL
);


--
-- Name: poll_options_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.poll_options_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: poll_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.poll_options_id_seq OWNED BY public.poll_options.id;


--
-- Name: poll_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.poll_votes (
    poll_id bigint NOT NULL,
    voter_id bigint NOT NULL,
    option_idx integer NOT NULL,
    voted_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: polls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.polls (
    id bigint NOT NULL,
    author_id bigint NOT NULL,
    question text NOT NULL,
    options text[] NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: polls_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.polls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: polls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.polls_id_seq OWNED BY public.polls.id;


--
-- Name: post_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_likes (
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: post_reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.post_reports (
    id bigint NOT NULL,
    post_id bigint NOT NULL,
    user_id bigint NOT NULL,
    reason text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: post_reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.post_reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: post_reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.post_reports_id_seq OWNED BY public.post_reports.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    author bigint,
    text text,
    media_url text,
    is_public boolean,
    created_at timestamp without time zone
);


--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profiles (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    profile_name text NOT NULL,
    username text NOT NULL,
    bio text,
    avatar_url text,
    is_active boolean DEFAULT false
);


--
-- Name: profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.profiles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.profiles_id_seq OWNED BY public.profiles.id;


--
-- Name: qa_answers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.qa_answers (
    id bigint NOT NULL,
    question_id bigint NOT NULL,
    author_id bigint NOT NULL,
    text text NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: qa_answers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.qa_answers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: qa_answers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.qa_answers_id_seq OWNED BY public.qa_answers.id;


--
-- Name: qa_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.qa_questions (
    id bigint NOT NULL,
    author_id bigint,
    text text NOT NULL,
    scope text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    deleted_at timestamp with time zone
);


--
-- Name: qa_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.qa_questions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: qa_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.qa_questions_id_seq OWNED BY public.qa_questions.id;


--
-- Name: referrals; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.referrals (
    inviter_id bigint NOT NULL,
    invitee_id bigint NOT NULL,
    rewarded boolean DEFAULT false,
    added_at timestamp with time zone DEFAULT now()
);


--
-- Name: reports; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reports (
    id bigint NOT NULL,
    reporter bigint NOT NULL,
    target bigint NOT NULL,
    reason text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.reports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: secret_chats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.secret_chats (
    id bigint NOT NULL,
    a bigint NOT NULL,
    b bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    closed_at timestamp with time zone
);


--
-- Name: secret_chats_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.secret_chats_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: secret_chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.secret_chats_id_seq OWNED BY public.secret_chats.id;


--
-- Name: secret_crush; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.secret_crush (
    user_id bigint NOT NULL,
    target_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: sensual_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensual_reactions (
    id bigint NOT NULL,
    story_id bigint,
    user_id bigint NOT NULL,
    reaction text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: sensual_reactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sensual_reactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sensual_reactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sensual_reactions_id_seq OWNED BY public.sensual_reactions.id;


--
-- Name: sensual_stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sensual_stories (
    id bigint NOT NULL,
    title text NOT NULL,
    content text NOT NULL,
    category text DEFAULT 'general'::text,
    created_at timestamp with time zone DEFAULT now(),
    is_featured boolean DEFAULT false
);


--
-- Name: sensual_stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sensual_stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sensual_stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sensual_stories_id_seq OWNED BY public.sensual_stories.id;


--
-- Name: social_comments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_comments (
    id integer NOT NULL,
    post_id integer,
    user_tg_id bigint NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_comments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_comments_id_seq OWNED BY public.social_comments.id;


--
-- Name: social_friend_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_friend_requests (
    id integer NOT NULL,
    requester_tg_id bigint NOT NULL,
    target_tg_id bigint NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_friend_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_friend_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_friend_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_friend_requests_id_seq OWNED BY public.social_friend_requests.id;


--
-- Name: social_friends; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_friends (
    id integer NOT NULL,
    user_tg_id bigint NOT NULL,
    friend_tg_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_friends_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_friends_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_friends_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_friends_id_seq OWNED BY public.social_friends.id;


--
-- Name: social_likes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_likes (
    id integer NOT NULL,
    post_id integer,
    user_tg_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_likes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_likes_id_seq OWNED BY public.social_likes.id;


--
-- Name: social_posts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_posts (
    id integer NOT NULL,
    author_tg_id bigint NOT NULL,
    text text DEFAULT ''::text,
    media character varying(255),
    is_public boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_posts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_posts_id_seq OWNED BY public.social_posts.id;


--
-- Name: social_profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.social_profiles (
    id integer NOT NULL,
    tg_user_id bigint NOT NULL,
    username character varying(50),
    bio text DEFAULT ''::text,
    photo character varying(255),
    privacy character varying(20) DEFAULT 'public'::character varying,
    show_fields text DEFAULT 'username,bio,photo'::text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: social_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.social_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: social_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.social_profiles_id_seq OWNED BY public.social_profiles.id;


--
-- Name: stories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stories (
    id bigint NOT NULL,
    author_id bigint NOT NULL,
    kind text NOT NULL,
    text text,
    media_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL
);


--
-- Name: stories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stories_id_seq OWNED BY public.stories.id;


--
-- Name: story_segments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_segments (
    id integer NOT NULL,
    story_id bigint NOT NULL,
    segment_type text NOT NULL,
    content_type text NOT NULL,
    file_id text,
    text text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id bigint,
    profile_id bigint
);


--
-- Name: story_segments_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.story_segments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: story_segments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.story_segments_id_seq OWNED BY public.story_segments.id;


--
-- Name: story_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.story_views (
    story_id bigint NOT NULL,
    viewer_id bigint NOT NULL,
    viewed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: user_badges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_badges (
    user_id bigint NOT NULL,
    badge_id text NOT NULL,
    earned_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_blocks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_blocks (
    blocker_id bigint NOT NULL,
    blocked_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_follows; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_follows (
    follower_id bigint NOT NULL,
    followee_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: user_interests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_interests (
    user_id integer,
    interest_key text NOT NULL
);


--
-- Name: user_mutes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_mutes (
    muter_id bigint NOT NULL,
    muted_id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    tg_user_id bigint NOT NULL,
    gender text,
    age integer,
    country text,
    city text,
    is_premium boolean DEFAULT false,
    search_pref text DEFAULT 'any'::text,
    created_at timestamp without time zone DEFAULT now(),
    last_dialog_date date,
    dialogs_total integer DEFAULT 0,
    dialogs_today integer DEFAULT 0,
    messages_sent integer DEFAULT 0,
    messages_recv integer DEFAULT 0,
    rating_up integer DEFAULT 0,
    rating_down integer DEFAULT 0,
    report_count integer DEFAULT 0,
    is_verified boolean DEFAULT false,
    verify_status text DEFAULT 'none'::text,
    verify_method text,
    verify_audio_file text,
    verify_photo_file text,
    verify_phrase text,
    verify_at timestamp without time zone,
    verify_src_chat bigint,
    verify_src_msg bigint,
    premium_until timestamp without time zone,
    language text,
    last_gender_change_at timestamp with time zone,
    last_age_change_at timestamp with time zone,
    banned_until timestamp with time zone,
    banned_reason text,
    banned_by bigint,
    match_verified_only boolean DEFAULT false,
    incognito boolean DEFAULT false,
    coins integer DEFAULT 0,
    last_daily timestamp with time zone,
    strikes integer DEFAULT 0,
    last_strike timestamp with time zone,
    spin_last timestamp with time zone,
    spins integer DEFAULT 0,
    games_played integer DEFAULT 0,
    bio text,
    photo_file_id text,
    feed_username text,
    feed_is_public boolean DEFAULT true,
    feed_photo text,
    feed_notify boolean DEFAULT true,
    date_of_birth date,
    shadow_banned boolean DEFAULT false,
    shadow_banned_at timestamp with time zone,
    min_age_pref integer DEFAULT 18,
    max_age_pref integer DEFAULT 99,
    allow_forward boolean DEFAULT false,
    last_seen timestamp with time zone,
    wyr_streak integer DEFAULT 0,
    wyr_last_voted date,
    dare_streak integer DEFAULT 0,
    dare_last_date date,
    vault_tokens integer DEFAULT 10,
    vault_tokens_last_reset date DEFAULT CURRENT_DATE,
    vault_storage_used bigint DEFAULT 0,
    vault_coins integer DEFAULT 0,
    display_name text,
    username text,
    avatar_url text,
    is_onboarded boolean DEFAULT false NOT NULL,
    tg_id bigint,
    active_profile_id bigint,
    privacy_consent boolean DEFAULT false,
    privacy_consent_date timestamp with time zone,
    age_verified boolean DEFAULT false,
    age_agreement_date timestamp with time zone,
    CONSTRAINT chk_users_age_range CHECK (((age IS NULL) OR ((age >= 13) AND (age <= 120))))
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vault_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_categories (
    id integer NOT NULL,
    name text NOT NULL,
    description text,
    emoji text DEFAULT '📝'::text,
    blur_intensity integer DEFAULT 70,
    premium_only boolean DEFAULT true,
    active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: vault_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vault_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vault_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vault_categories_id_seq OWNED BY public.vault_categories.id;


--
-- Name: vault_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_content (
    id bigint NOT NULL,
    submitter_id bigint NOT NULL,
    category_id integer,
    content_text text,
    blurred_text text,
    blur_level integer DEFAULT 70,
    reveal_cost integer DEFAULT 2,
    status text DEFAULT 'pending'::text,
    approval_status text DEFAULT 'pending'::text,
    approved_by bigint,
    approved_at timestamp with time zone,
    view_count integer DEFAULT 0,
    reveal_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    media_type text DEFAULT 'text'::text,
    file_url text,
    thumbnail_url text,
    blurred_thumbnail_url text,
    file_id text,
    CONSTRAINT chk_approval_status CHECK ((approval_status = ANY (ARRAY['pending'::text, 'approved'::text, 'rejected'::text]))),
    CONSTRAINT chk_media_type CHECK ((media_type = ANY (ARRAY['text'::text, 'image'::text, 'video'::text]))),
    CONSTRAINT chk_vault_status CHECK ((status = ANY (ARRAY['pending'::text, 'approved'::text, 'rejected'::text, 'archived'::text])))
);


--
-- Name: vault_content_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vault_content_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vault_content_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vault_content_id_seq OWNED BY public.vault_content.id;


--
-- Name: vault_daily_category_views; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_daily_category_views (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    category_id integer,
    views_today integer DEFAULT 0,
    view_date date DEFAULT CURRENT_DATE,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vault_daily_category_views_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vault_daily_category_views_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vault_daily_category_views_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vault_daily_category_views_id_seq OWNED BY public.vault_daily_category_views.id;


--
-- Name: vault_daily_limits; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_daily_limits (
    user_id bigint NOT NULL,
    reveals_used integer DEFAULT 0,
    media_reveals_used integer DEFAULT 0,
    limit_date date DEFAULT CURRENT_DATE,
    premium_status boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


--
-- Name: vault_interactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_interactions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    content_id bigint,
    action text NOT NULL,
    tokens_spent integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chk_vault_action CHECK ((action = ANY (ARRAY['viewed'::text, 'revealed'::text, 'liked'::text, 'reported'::text])))
);


--
-- Name: vault_interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vault_interactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vault_interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vault_interactions_id_seq OWNED BY public.vault_interactions.id;


--
-- Name: vault_user_states; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vault_user_states (
    user_id bigint NOT NULL,
    category_id integer,
    state text NOT NULL,
    data text,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: wyr_anonymous_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_anonymous_users (
    id bigint NOT NULL,
    vote_date date NOT NULL,
    tg_user_id bigint NOT NULL,
    anonymous_name text NOT NULL,
    assigned_at timestamp with time zone DEFAULT now()
);


--
-- Name: wyr_anonymous_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wyr_anonymous_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wyr_anonymous_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wyr_anonymous_users_id_seq OWNED BY public.wyr_anonymous_users.id;


--
-- Name: wyr_group_chats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_group_chats (
    vote_date date NOT NULL,
    total_voters integer DEFAULT 0,
    total_messages integer DEFAULT 0,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone DEFAULT (now() + '1 day'::interval)
);


--
-- Name: wyr_group_messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_group_messages (
    id bigint NOT NULL,
    vote_date date NOT NULL,
    anonymous_user_id bigint,
    message_type text DEFAULT 'comment'::text,
    content text NOT NULL,
    reply_to_message_id bigint,
    created_at timestamp with time zone DEFAULT now(),
    is_deleted boolean DEFAULT false,
    deleted_by_admin bigint,
    deleted_at timestamp with time zone,
    CONSTRAINT wyr_group_messages_message_type_check CHECK ((message_type = ANY (ARRAY['comment'::text, 'reaction'::text, 'reply'::text])))
);


--
-- Name: wyr_group_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wyr_group_messages_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wyr_group_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wyr_group_messages_id_seq OWNED BY public.wyr_group_messages.id;


--
-- Name: wyr_message_reactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_message_reactions (
    id bigint NOT NULL,
    message_id bigint,
    tg_user_id bigint NOT NULL,
    reaction_type text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT wyr_message_reactions_reaction_type_check CHECK ((reaction_type = ANY (ARRAY['like'::text, 'heart'::text, 'laugh'::text])))
);


--
-- Name: wyr_message_reactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.wyr_message_reactions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: wyr_message_reactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.wyr_message_reactions_id_seq OWNED BY public.wyr_message_reactions.id;


--
-- Name: wyr_permanent_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_permanent_users (
    tg_user_id bigint NOT NULL,
    permanent_username text NOT NULL,
    assigned_at timestamp with time zone DEFAULT now(),
    total_comments integer DEFAULT 0,
    total_likes integer DEFAULT 0,
    weekly_comments integer DEFAULT 0,
    weekly_likes integer DEFAULT 0,
    last_reset timestamp with time zone DEFAULT now()
);


--
-- Name: wyr_question_of_day; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_question_of_day (
    vote_date date NOT NULL,
    a_text text NOT NULL,
    b_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


--
-- Name: wyr_votes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.wyr_votes (
    tg_user_id bigint NOT NULL,
    vote_date date NOT NULL,
    side character(1) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT wyr_votes_side_check CHECK ((side = ANY (ARRAY['A'::bpchar, 'B'::bpchar])))
);


--
-- Name: ad_messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ad_messages ALTER COLUMN id SET DEFAULT nextval('public.ad_messages_id_seq'::regclass);


--
-- Name: ad_participants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ad_participants ALTER COLUMN id SET DEFAULT nextval('public.ad_participants_id_seq'::regclass);


--
-- Name: ad_prompts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ad_prompts ALTER COLUMN id SET DEFAULT nextval('public.ad_prompts_id_seq'::regclass);


--
-- Name: ad_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ad_sessions ALTER COLUMN id SET DEFAULT nextval('public.ad_sessions_id_seq'::regclass);


--
-- Name: chat_extensions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_extensions ALTER COLUMN id SET DEFAULT nextval('public.chat_extensions_id_seq'::regclass);


--
-- Name: chat_ratings id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_ratings ALTER COLUMN id SET DEFAULT nextval('public.chat_ratings_id_seq'::regclass);


--
-- Name: chat_reports id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_reports ALTER COLUMN id SET DEFAULT nextval('public.chat_reports_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: confession_deliveries id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confession_deliveries ALTER COLUMN id SET DEFAULT nextval('public.confession_deliveries_id_seq'::regclass);


--
-- Name: confession_leaderboard id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confession_leaderboard ALTER COLUMN id SET DEFAULT nextval('public.confession_leaderboard_id_seq'::regclass);


--
-- Name: confession_reactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confession_reactions ALTER COLUMN id SET DEFAULT nextval('public.confession_reactions_id_seq'::regclass);


--
-- Name: confession_replies id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confession_replies ALTER COLUMN id SET DEFAULT nextval('public.confession_replies_id_seq'::regclass);


--
-- Name: confessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.confessions ALTER COLUMN id SET DEFAULT nextval('public.confessions_id_seq'::regclass);


--
-- Name: dare_feedback id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dare_feedback ALTER COLUMN id SET DEFAULT nextval('public.dare_feedback_id_seq'::regclass);


--
-- Name: dare_responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dare_responses ALTER COLUMN id SET DEFAULT nextval('public.dare_responses_id_seq'::regclass);


--
-- Name: dare_submissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dare_submissions ALTER COLUMN id SET DEFAULT nextval('public.dare_submissions_id_seq'::regclass);


--
-- Name: fantasy_board_reactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fantasy_board_reactions ALTER COLUMN id SET DEFAULT nextval('public.fantasy_board_reactions_id_seq'::regclass);


--
-- Name: fantasy_chat_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fantasy_chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.fantasy_chat_sessions_id_seq'::regclass);


--
-- Name: post_reports id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_reports ALTER COLUMN id SET DEFAULT nextval('public.post_reports_id_seq'::regclass);


--
-- Name: story_segments id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_segments ALTER COLUMN id SET DEFAULT nextval('public.story_segments_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vault_categories id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vault_categories ALTER COLUMN id SET DEFAULT nextval('public.vault_categories_id_seq'::regclass);


--
-- Data for Name: ad_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ad_messages (id, session_id, user_id, anon_name, msg_type, content, meta, created_at) FROM stdin;
\.


--
-- Data for Name: ad_participants; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ad_participants (id, session_id, user_id, anon_name, joined_at, left_at) FROM stdin;
\.


--
-- Data for Name: ad_prompts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ad_prompts (id, session_id, kind, payload, created_at) FROM stdin;
\.


--
-- Data for Name: ad_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ad_sessions (id, started_at, ends_at, vibe, status) FROM stdin;
\.


--
-- Data for Name: blocked_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.blocked_users (user_id, blocked_uid, added_at) FROM stdin;
\.


--
-- Data for Name: chat_extensions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_extensions (id, match_id, extended_by, stars_paid, minutes_added, extended_at) FROM stdin;
\.


--
-- Data for Name: chat_ratings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_ratings (id, rater_id, ratee_id, value, reason, created_at) FROM stdin;
\.


--
-- Data for Name: chat_reports; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.chat_reports (id, reporter_tg_id, reported_tg_id, in_secret, text, media_file_id, media_type, created_at) FROM stdin;
\.


--
-- Data for Name: comment_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comment_likes (comment_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comments (id, post_id, user_id, text, created_at, pinned, pinned_at, pinned_by_user_id, profile_id) FROM stdin;
\.


--
-- Data for Name: confession_deliveries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_deliveries (id, confession_id, user_id, delivered_at) FROM stdin;
\.


--
-- Data for Name: confession_leaderboard; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_leaderboard (id, user_id, period, confession_count, total_reactions_received, replies_received, rank_type, rank_position, updated_at) FROM stdin;
\.


--
-- Data for Name: confession_mutes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_mutes (user_id, confession_id, created_at) FROM stdin;
\.


--
-- Data for Name: confession_reactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_reactions (id, confession_id, user_id, reaction_type, created_at, approved, approved_at) FROM stdin;
\.


--
-- Data for Name: confession_replies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_replies (id, original_confession_id, replier_user_id, reply_text, created_at, reply_reactions, is_anonymous, approved, approved_at) FROM stdin;
\.


--
-- Data for Name: confession_stats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confession_stats (user_id, total_confessions, weekly_confessions, current_streak, longest_streak, total_reactions_received, total_replies_received, best_confessor_score, last_confession_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: confessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.confessions (id, author_id, text, created_at, delivered, delivered_at, delivered_to, system_seed, deleted_at) FROM stdin;
1	8482725798	Kabhi kabhi sochti hoon koi mujhe bas ek baar pyaar se gale lagaye aur bole "main hoon na"… shayad mujhe bas itna hi chahiye life me ❤️	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
2	647778438	Rain me bheegna mujhe hamesha pasand tha, but jab ek baar kisi ne deliberately umbrella close karke bola "let's get wet together", tab laga filmy romance real hai 🌧️🔥	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
3	1437934486	Main tough dikhne ki koshish karta hoon, par ek soft touch aur ek warm hug mujhe turant tod deta hai… bas koi ho jo mujhe bina judge kiye samajh le 🤗	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
4	8482725798	Ek baar truth or dare me dare mila kiss karne ka, aur wo life ka best moment tha… kyunki secretly maine hamesha usi ka wait kiya tha 😈💋	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
5	647778438	Log mujhe innocent kehte hain, par sach ye hai ki meri mind me bohot naughty thoughts hote hain… bas ek partner chahiye jo unhe explore kar sake 😉🔥	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
6	1437934486	Kya tumhe kabhi kisi ki aankhon me dekh ke lagta hai ki time ruk gaya? Mujhe wo feel ek baar hua tha aur abhi tak us nazar ko bhool nahi paya 👀💞	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
7	8482725798	Mera dil ek hi cheez pe weak ho jata hai — public me secretly hand hold karna… wo single touch pura din yaad rehta hai 🫦	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
8	647778438	Mujhe secretly pasand hai jab koi possessive style me bole "you're mine"… wo line mujhe safe aur desired feel karati hai 😳❤️	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
9	1437934486	Raat ke 2 baje ka ek "you up?" message hi sabse bada trap hai… us time pe sabse asli secrets nikalte hain 🌌😏	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
10	8482725798	Koi accept kare ya na kare, mujhe neck kisses aur ear whispers pe control hi nahi rehta… bas guard down ho jata hai 🫠🔥	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
11	647778438	Kabhi kabhi sochta hoon ki agar koi bas mere forehead pe ek gentle kiss kare, to shayad main uske saath forever ho jaun 💫	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
12	1437934486	Public me affection dekhna logon ko ajeeb lagta hai, but mujhe usme hi thrill hai… ek baar kisi ne crowd me haath pakda tha aur wo feel unforgettable hai 👀	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
13	8482725798	Maine ek baar kisi ko bas aankhon se "I like you" bola tha… aur usne samajh bhi liya. Us din realize hua ki feelings words ke bina bhi express ho sakti hain 👀💌	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
14	647778438	Maine ek baar kisi ko bas aankhon se "I like you" bola tha… aur usne samajh bhi liya. Us din realize hua ki feelings words ke bina bhi express ho sakti hain 👀💌	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
15	1437934486	Maine ek baar kisi ko bas aankhon se "I like you" bola tha… aur usne samajh bhi liya. Us din realize hua ki feelings words ke bina bhi express ho sakti hain 👀💌	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
16	8482725798	Mera sapna hai kisi ke sath rooftop pe baith kar city lights dekhna aur bas chup rehna… silence bhi kabhi kabhi sabse loud hota hai 🌃	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
17	647778438	Ek baar kisi ne mujhe tease kiya aur main blush se control hi nahi kar paayi… us din samjha blush bhi addiction ban sakta hai 😳	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
18	1437934486	Mujhe genuinely pasand hai jab koi mujhe care karta hai little things me… jaise "khana khaya?" ya "pani piya?" 🥺	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
19	8482725798	Maine ek baar kisi ko apna crush bolne hi wala tha, aur tabhi usne bola "tum mere best dost ho"… tab se confess karne me darr lagta hai 💔	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
20	647778438	Kabhi kabhi ek random stranger ki smile dil chura leti hai… aur main pura din usi ke bare me sochta/ti rehta hoon 🙂	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
21	1437934486	Sometimes I just want to disappear with someone for a weekend… no phones, no social media, sirf hum aur vibes 🌌🔥	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
22	8482725798	Mujhe confess karna hai ki kabhi kabhi main apne crush ki insta story 20 baar dekh leti hoon, bas ek glimpse ke liye 😅	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
23	647778438	Ek baar kisi ne mujhe tease kiya aur main blush se control hi nahi kar paayi… us din samjha blush bhi addiction ban sakta hai 😳	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
24	1437934486	Sometimes I just want someone to sit with me in silence and hold my hand… aur bas wohi enough hai ❤️	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
25	8482725798	Mujhe confess karna hai ki kabhi kabhi main apne crush ki insta story 20 baar dekh leti hoon, bas ek glimpse ke liye 😅	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
26	647778438	Ek baar kisi ne mujhe tease kiya aur main blush se control hi nahi kar paayi… us din samjha blush bhi addiction ban sakta hai 😳	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
27	1437934486	Sometimes I just want someone to sit with me in silence and hold my hand… aur bas wohi enough hai ❤️	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
28	8482725798	Mujhe confess karna hai ki kabhi kabhi main apne crush ki insta story 20 baar dekh leti hoon, bas ek glimpse ke liye 😅	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
29	647778438	Ek baar kisi ne mujhe tease kiya aur main blush se control hi nahi kar paayi… us din samjha blush bhi addiction ban sakta hai 😳	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
30	1437934486	Sometimes I just want someone to sit with me in silence and hold my hand… aur bas wohi enough hai ❤️	2025-10-09 04:50:43.340455+00	f	\N	\N	t	\N
\.


--
-- Data for Name: crush_leaderboard; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.crush_leaderboard (user_id, crush_count, week_start, last_updated) FROM stdin;
\.


--
-- Data for Name: daily_dare_selection; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.daily_dare_selection (dare_date, dare_text, dare_source, source_id, created_at, submitter_id, category, difficulty, creator_notified) FROM stdin;
\.


--
-- Data for Name: dare_feedback; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dare_feedback (id, submission_id, event_type, user_id, dare_date, notified, created_at) FROM stdin;
\.


--
-- Data for Name: dare_responses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dare_responses (id, user_id, dare_date, response, response_time, completion_claimed, difficulty_selected, dare_text) FROM stdin;
\.


--
-- Data for Name: dare_stats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dare_stats (user_id, current_streak, longest_streak, total_accepted, total_declined, total_expired, last_dare_date, badges, updated_at) FROM stdin;
\.


--
-- Data for Name: dare_submissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dare_submissions (id, submitter_id, dare_text, category, difficulty, approved, admin_approved_by, submission_date, created_at) FROM stdin;
\.


--
-- Data for Name: fantasy_board_reactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_board_reactions (id, user_id, fantasy_id, reaction_type, created_at) FROM stdin;
\.


--
-- Data for Name: fantasy_chat_sessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_chat_sessions (id, a_id, b_id, started_at, ended_at, status) FROM stdin;
\.


--
-- Data for Name: fantasy_chats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_chats (id, match_id, chat_room_id, started_at, expires_at, boy_joined, girl_joined, message_count) FROM stdin;
\.


--
-- Data for Name: fantasy_match_notifs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_match_notifs (id, match_id, user_id, sent_at) FROM stdin;
\.


--
-- Data for Name: fantasy_match_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_match_requests (id, requester_id, fantasy_id, fantasy_owner_id, status, created_at, responded_at, expires_at, cancelled_by_user_id, cancelled_at, cancel_reason, version) FROM stdin;
\.


--
-- Data for Name: fantasy_matches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_matches (id, boy_id, girl_id, fantasy_key, created_at, expires_at, boy_ready, girl_ready, boy_is_premium, connected_at, status, chat_id, vibe, shared_keywords) FROM stdin;
\.


--
-- Data for Name: fantasy_stats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_stats (fantasy_id, views_count, reactions_count, matches_count, success_rate, last_updated) FROM stdin;
\.


--
-- Data for Name: fantasy_submissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fantasy_submissions (id, user_id, gender, fantasy_text, created_at, is_active, fantasy_key, submitted_count, vibe, keywords, active) FROM stdin;
\.


--
-- Data for Name: feed_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_comments (id, post_id, author_id, author_name, text, created_at) FROM stdin;
\.


--
-- Data for Name: feed_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_likes (post_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: feed_posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_posts (id, author_id, created_at, content_type, file_id, text, reaction_count, comment_count, profile_id) FROM stdin;
\.


--
-- Data for Name: feed_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_profiles (uid, username, bio, is_public, photo) FROM stdin;
\.


--
-- Data for Name: feed_reactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_reactions (post_id, user_id, emoji, created_at) FROM stdin;
\.


--
-- Data for Name: feed_views; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.feed_views (post_id, viewer_id, viewed_at) FROM stdin;
\.


--
-- Data for Name: friend_chats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.friend_chats (id, a, b, opened_at, closed_at) FROM stdin;
\.


--
-- Data for Name: friend_msg_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.friend_msg_requests (id, sender, receiver, text, created_at, status) FROM stdin;
\.


--
-- Data for Name: friend_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.friend_requests (requester_id, target_id, created_at) FROM stdin;
\.


--
-- Data for Name: friends; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.friends (user_id, friend_id, added_at) FROM stdin;
\.


--
-- Data for Name: friendship_levels; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.friendship_levels (user1_id, user2_id, interaction_count, level, last_interaction, created_at) FROM stdin;
\.


--
-- Data for Name: game_questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.game_questions (game, question, added_by, added_at) FROM stdin;
\.


--
-- Data for Name: idempotency_keys; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.idempotency_keys (key, operation, result, created_at) FROM stdin;
\.


--
-- Data for Name: likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.likes (id, post_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: maintenance_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.maintenance_log (id, operation, status, details, duration_seconds, executed_at) FROM stdin;
\.


--
-- Data for Name: miniapp_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_comments (id, post_id, author_id, text, parent_id, created_at) FROM stdin;
\.


--
-- Data for Name: miniapp_follows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_follows (follower_id, followee_id, created_at, status) FROM stdin;
\.


--
-- Data for Name: miniapp_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_likes (post_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: miniapp_post_views; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_post_views (post_id, user_id, viewed_at) FROM stdin;
\.


--
-- Data for Name: miniapp_posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_posts (id, author_id, type, caption, media_url, media_type, visibility, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: miniapp_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_profiles (user_id, username, display_name, bio, avatar_url, is_private, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: miniapp_saves; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.miniapp_saves (post_id, user_id, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: moderation_events; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.moderation_events (id, tg_user_id, kind, token, sample, created_at) FROM stdin;
\.


--
-- Data for Name: muc_char_options; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_char_options (id, question_id, opt_key, text) FROM stdin;
\.


--
-- Data for Name: muc_char_questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_char_questions (id, series_id, prompt, question_key, active_from_episode_id) FROM stdin;
\.


--
-- Data for Name: muc_char_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_char_votes (id, question_id, option_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: muc_characters; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_characters (id, series_id, name, role, bio_md, attributes, secrets) FROM stdin;
\.


--
-- Data for Name: muc_episodes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_episodes (id, series_id, idx, title, teaser_md, body_md, cliff_md, publish_at, close_at, status) FROM stdin;
\.


--
-- Data for Name: muc_poll_options; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_poll_options (id, poll_id, opt_key, text, next_hint, idx) FROM stdin;
\.


--
-- Data for Name: muc_polls; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_polls (id, episode_id, prompt, layer, allow_multi) FROM stdin;
\.


--
-- Data for Name: muc_series; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_series (id, slug, title, status, created_at) FROM stdin;
\.


--
-- Data for Name: muc_theories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_theories (id, episode_id, user_id, text, likes, created_at) FROM stdin;
\.


--
-- Data for Name: muc_theory_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_theory_likes (id, theory_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: muc_user_engagement; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_user_engagement (user_id, streak_days, detective_score, last_seen_episode_id) FROM stdin;
\.


--
-- Data for Name: muc_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.muc_votes (id, poll_id, option_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: naughty_wyr_deliveries; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.naughty_wyr_deliveries (question_id, user_id, delivered_at) FROM stdin;
\.


--
-- Data for Name: naughty_wyr_questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.naughty_wyr_questions (id, question, created_at, system_seed) FROM stdin;
\.


--
-- Data for Name: naughty_wyr_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.naughty_wyr_votes (question_id, user_id, choice, voted_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, user_id, ntype, actor, post_id, created_at, read) FROM stdin;
\.


--
-- Data for Name: pending_confession_replies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pending_confession_replies (id, original_confession_id, replier_user_id, reply_text, created_at, admin_notified, is_voice, voice_file_id, voice_duration) FROM stdin;
\.


--
-- Data for Name: pending_confessions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pending_confessions (id, author_id, text, created_at, admin_notified, is_voice, voice_file_id, voice_duration) FROM stdin;
\.


--
-- Data for Name: poll_options; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.poll_options (id, poll_id, text) FROM stdin;
\.


--
-- Data for Name: poll_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.poll_votes (poll_id, voter_id, option_idx, voted_at) FROM stdin;
\.


--
-- Data for Name: polls; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.polls (id, author_id, question, options, created_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: post_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.post_likes (post_id, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: post_reports; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.post_reports (id, post_id, user_id, reason, created_at) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.posts (id, author, text, media_url, is_public, created_at) FROM stdin;
\.


--
-- Data for Name: profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.profiles (id, user_id, profile_name, username, bio, avatar_url, is_active) FROM stdin;
\.


--
-- Data for Name: qa_answers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.qa_answers (id, question_id, author_id, text, is_admin, created_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: qa_questions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.qa_questions (id, author_id, text, scope, created_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: referrals; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.referrals (inviter_id, invitee_id, rewarded, added_at) FROM stdin;
\.


--
-- Data for Name: reports; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reports (id, reporter, target, reason, created_at) FROM stdin;
\.


--
-- Data for Name: secret_chats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.secret_chats (id, a, b, created_at, expires_at, closed_at) FROM stdin;
\.


--
-- Data for Name: secret_crush; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.secret_crush (user_id, target_id, created_at) FROM stdin;
\.


--
-- Data for Name: sensual_reactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sensual_reactions (id, story_id, user_id, reaction, created_at) FROM stdin;
\.


--
-- Data for Name: sensual_stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sensual_stories (id, title, content, category, created_at, is_featured) FROM stdin;
\.


--
-- Data for Name: social_comments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_comments (id, post_id, user_tg_id, text, created_at) FROM stdin;
\.


--
-- Data for Name: social_friend_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_friend_requests (id, requester_tg_id, target_tg_id, status, created_at) FROM stdin;
\.


--
-- Data for Name: social_friends; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_friends (id, user_tg_id, friend_tg_id, created_at) FROM stdin;
\.


--
-- Data for Name: social_likes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_likes (id, post_id, user_tg_id, created_at) FROM stdin;
\.


--
-- Data for Name: social_posts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_posts (id, author_tg_id, text, media, is_public, created_at) FROM stdin;
\.


--
-- Data for Name: social_profiles; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.social_profiles (id, tg_user_id, username, bio, photo, privacy, show_fields, created_at) FROM stdin;
\.


--
-- Data for Name: stories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stories (id, author_id, kind, text, media_id, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: story_segments; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_segments (id, story_id, segment_type, content_type, file_id, text, created_at, user_id, profile_id) FROM stdin;
\.


--
-- Data for Name: story_views; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.story_views (story_id, viewer_id, viewed_at) FROM stdin;
\.


--
-- Data for Name: user_badges; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_badges (user_id, badge_id, earned_at) FROM stdin;
\.


--
-- Data for Name: user_blocks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_blocks (blocker_id, blocked_id, created_at) FROM stdin;
\.


--
-- Data for Name: user_follows; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_follows (follower_id, followee_id, created_at) FROM stdin;
\.


--
-- Data for Name: user_interests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_interests (user_id, interest_key) FROM stdin;
1	love
1	chatting
1	relationship
1	games
1	anime
1	friends
\.


--
-- Data for Name: user_mutes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_mutes (muter_id, muted_id, created_at) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, tg_user_id, gender, age, country, city, is_premium, search_pref, created_at, last_dialog_date, dialogs_total, dialogs_today, messages_sent, messages_recv, rating_up, rating_down, report_count, is_verified, verify_status, verify_method, verify_audio_file, verify_photo_file, verify_phrase, verify_at, verify_src_chat, verify_src_msg, premium_until, language, last_gender_change_at, last_age_change_at, banned_until, banned_reason, banned_by, match_verified_only, incognito, coins, last_daily, strikes, last_strike, spin_last, spins, games_played, bio, photo_file_id, feed_username, feed_is_public, feed_photo, feed_notify, date_of_birth, shadow_banned, shadow_banned_at, min_age_pref, max_age_pref, allow_forward, last_seen, wyr_streak, wyr_last_voted, dare_streak, dare_last_date, vault_tokens, vault_tokens_last_reset, vault_storage_used, vault_coins, display_name, username, avatar_url, is_onboarded, tg_id, active_profile_id, privacy_consent, privacy_consent_date, age_verified, age_agreement_date) FROM stdin;
1	647778438	male	30	India	Mumbai	f	any	2025-10-09 05:12:03.495449	\N	0	0	0	0	0	0	0	f	none	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	f	f	0	\N	0	\N	\N	0	0	\N	\N	\N	t	\N	t	\N	f	\N	18	99	f	2025-10-09 05:23:33.794189+00	0	\N	0	\N	10	2025-10-09	0	0	\N	\N	\N	f	\N	\N	t	2025-10-09 05:12:03.495449+00	t	2025-10-09 05:12:25.18526+00
\.


--
-- Data for Name: vault_categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_categories (id, name, description, emoji, blur_intensity, premium_only, active, created_at) FROM stdin;
1	Romantic Confessions	Love stories and romantic secrets	💖	75	t	t	2025-10-09 05:23:45.673815+00
2	Dark Secrets	Deep confessions and hidden truths	🖤	85	t	t	2025-10-09 05:23:45.673815+00
3	Midnight Thoughts	Late night revelations	🌙	60	t	t	2025-10-09 05:23:45.673815+00
4	Forbidden Dreams	Fantasies and desires	🔥	90	t	t	2025-10-09 05:23:45.673815+00
5	Funny Confessions	Embarrassing and funny moments	😂	50	t	t	2025-10-09 05:23:45.673815+00
6	Life Lessons	Wisdom and experiences	💡	40	t	t	2025-10-09 05:23:45.673815+00
7	Blur Pictures	Hidden photos and private moments	📸	95	t	t	2025-10-09 05:23:45.673815+00
8	Blur Videos	Secret videos and clips	🎥	95	t	t	2025-10-09 05:23:45.673815+00
\.


--
-- Data for Name: vault_content; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_content (id, submitter_id, category_id, content_text, blurred_text, blur_level, reveal_cost, status, approval_status, approved_by, approved_at, view_count, reveal_count, created_at, updated_at, media_type, file_url, thumbnail_url, blurred_thumbnail_url, file_id) FROM stdin;
\.


--
-- Data for Name: vault_daily_category_views; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_daily_category_views (id, user_id, category_id, views_today, view_date, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vault_daily_limits; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_daily_limits (user_id, reveals_used, media_reveals_used, limit_date, premium_status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: vault_interactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_interactions (id, user_id, content_id, action, tokens_spent, created_at) FROM stdin;
\.


--
-- Data for Name: vault_user_states; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vault_user_states (user_id, category_id, state, data, created_at) FROM stdin;
\.


--
-- Data for Name: wyr_anonymous_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_anonymous_users (id, vote_date, tg_user_id, anonymous_name, assigned_at) FROM stdin;
\.


--
-- Data for Name: wyr_group_chats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_group_chats (vote_date, total_voters, total_messages, is_active, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: wyr_group_messages; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_group_messages (id, vote_date, anonymous_user_id, message_type, content, reply_to_message_id, created_at, is_deleted, deleted_by_admin, deleted_at) FROM stdin;
\.


--
-- Data for Name: wyr_message_reactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_message_reactions (id, message_id, tg_user_id, reaction_type, created_at) FROM stdin;
\.


--
-- Data for Name: wyr_permanent_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_permanent_users (tg_user_id, permanent_username, assigned_at, total_comments, total_likes, weekly_comments, weekly_likes, last_reset) FROM stdin;
\.


--
-- Data for Name: wyr_question_of_day; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_question_of_day (vote_date, a_text, b_text, created_at) FROM stdin;
\.


--
-- Data for Name: wyr_votes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.wyr_votes (tg_user_id, vote_date, side, created_at) FROM stdin;
\.


--
-- Name: ad_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ad_messages_id_seq', 1, false);


--
-- Name: ad_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ad_participants_id_seq', 1, false);


--
-- Name: ad_prompts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ad_prompts_id_seq', 1, false);


--
-- Name: ad_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ad_sessions_id_seq', 1, false);


--
-- Name: chat_extensions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_extensions_id_seq', 1, false);


--
-- Name: chat_ratings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_ratings_id_seq', 1, false);


--
-- Name: chat_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.chat_reports_id_seq', 1, false);


--
-- Name: comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comments_id_seq', 1, false);


--
-- Name: confession_deliveries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.confession_deliveries_id_seq', 1, false);


--
-- Name: confession_leaderboard_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.confession_leaderboard_id_seq', 1, false);


--
-- Name: confession_reactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.confession_reactions_id_seq', 1, false);


--
-- Name: confession_replies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.confession_replies_id_seq', 1, false);


--
-- Name: confessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.confessions_id_seq', 30, true);


--
-- Name: dare_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dare_feedback_id_seq', 1, false);


--
-- Name: dare_responses_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dare_responses_id_seq', 1, false);


--
-- Name: dare_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dare_submissions_id_seq', 1, false);


--
-- Name: fantasy_board_reactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_board_reactions_id_seq', 1, false);


--
-- Name: fantasy_chat_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_chat_sessions_id_seq', 1, false);


--
-- Name: fantasy_chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_chats_id_seq', 1, false);


--
-- Name: fantasy_match_notifs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_match_notifs_id_seq', 1, false);


--
-- Name: fantasy_match_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_match_requests_id_seq', 1, false);


--
-- Name: fantasy_matches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_matches_id_seq', 1, false);


--
-- Name: fantasy_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fantasy_submissions_id_seq', 1, false);


--
-- Name: feed_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.feed_comments_id_seq', 1, false);


--
-- Name: feed_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.feed_posts_id_seq', 1, false);


--
-- Name: friend_chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.friend_chats_id_seq', 1, false);


--
-- Name: friend_msg_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.friend_msg_requests_id_seq', 1, false);


--
-- Name: likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.likes_id_seq', 1, false);


--
-- Name: maintenance_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.maintenance_log_id_seq', 1, false);


--
-- Name: miniapp_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.miniapp_comments_id_seq', 1, false);


--
-- Name: miniapp_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.miniapp_posts_id_seq', 1, false);


--
-- Name: moderation_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.moderation_events_id_seq', 1, false);


--
-- Name: muc_char_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_char_options_id_seq', 1, false);


--
-- Name: muc_char_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_char_questions_id_seq', 1, false);


--
-- Name: muc_char_votes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_char_votes_id_seq', 1, false);


--
-- Name: muc_characters_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_characters_id_seq', 1, false);


--
-- Name: muc_episodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_episodes_id_seq', 1, false);


--
-- Name: muc_poll_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_poll_options_id_seq', 1, false);


--
-- Name: muc_polls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_polls_id_seq', 1, false);


--
-- Name: muc_series_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_series_id_seq', 1, false);


--
-- Name: muc_theories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_theories_id_seq', 1, false);


--
-- Name: muc_theory_likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_theory_likes_id_seq', 1, false);


--
-- Name: muc_votes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.muc_votes_id_seq', 1, false);


--
-- Name: naughty_wyr_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.naughty_wyr_questions_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: pending_confession_replies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pending_confession_replies_id_seq', 1, false);


--
-- Name: pending_confessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pending_confessions_id_seq', 1, false);


--
-- Name: poll_options_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.poll_options_id_seq', 1, false);


--
-- Name: polls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.polls_id_seq', 1, false);


--
-- Name: post_reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.post_reports_id_seq', 1, false);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.profiles_id_seq', 1, false);


--
-- Name: qa_answers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.qa_answers_id_seq', 1, false);


--
-- Name: qa_questions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.qa_questions_id_seq', 1, false);


--
-- Name: reports_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reports_id_seq', 1, false);


--
-- Name: secret_chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.secret_chats_id_seq', 1, false);


--
-- Name: sensual_reactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sensual_reactions_id_seq', 1, false);


--
-- Name: sensual_stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sensual_stories_id_seq', 1, false);


--
-- Name: social_comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_comments_id_seq', 1, false);


--
-- Name: social_friend_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_friend_requests_id_seq', 1, false);


--
-- Name: social_friends_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_friends_id_seq', 1, false);


--
-- Name: social_likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_likes_id_seq', 1, false);


--
-- Name: social_posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_posts_id_seq', 1, false);


--
-- Name: social_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.social_profiles_id_seq', 1, false);


--
-- Name: stories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.stories_id_seq', 1, false);


--
-- Name: story_segments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.story_segments_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: vault_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vault_categories_id_seq', 8, true);


--
-- Name: vault_content_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vault_content_id_seq', 1, false);


--
-- Name: vault_daily_category_views_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vault_daily_category_views_id_seq', 1, false);


--
-- Name: vault_interactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vault_interactions_id_seq', 1, false);


--
-- Name: wyr_anonymous_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.wyr_anonymous_users_id_seq', 1, false);


--
-- Name: wyr_group_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.wyr_group_messages_id_seq', 1, false);


--
-- Name: wyr_message_reactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.wyr_message_reactions_id_seq', 1, false);


--
-- Name: post_reports post_reports_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.post_reports
    ADD CONSTRAINT post_reports_pkey PRIMARY KEY (id);


--
-- Name: story_segments story_segments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.story_segments
    ADD CONSTRAINT story_segments_pkey PRIMARY KEY (id);


--
-- Name: user_blocks user_blocks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_blocks
    ADD CONSTRAINT user_blocks_pkey PRIMARY KEY (blocker_id, blocked_id);


--
-- Name: user_mutes user_mutes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_mutes
    ADD CONSTRAINT user_mutes_pkey PRIMARY KEY (muter_id, muted_id);


--
-- Name: users users_tg_user_id_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tg_user_id_unique UNIQUE (tg_user_id);


--
-- Name: vault_categories vault_categories_name_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vault_categories
    ADD CONSTRAINT vault_categories_name_unique UNIQUE (name);


--
-- Name: vault_categories vault_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vault_categories
    ADD CONSTRAINT vault_categories_pkey PRIMARY KEY (id);


--
-- Name: feed_reactions_post_user_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX feed_reactions_post_user_idx ON public.feed_reactions USING btree (post_id, user_id);


--
-- Name: feed_reactions_user_post_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX feed_reactions_user_post_idx ON public.feed_reactions USING btree (user_id, post_id);


--
-- Name: fmr_exp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fmr_exp ON public.fantasy_match_requests USING btree (expires_at);


--
-- Name: fmr_owner_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fmr_owner_status ON public.fantasy_match_requests USING btree (fantasy_owner_id, status);


--
-- Name: fmr_requester_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX fmr_requester_status ON public.fantasy_match_requests USING btree (requester_id, status);


--
-- Name: idx_qa_a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qa_a ON public.qa_answers USING btree (question_id, created_at);


--
-- Name: idx_qa_q; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qa_q ON public.qa_questions USING btree (created_at);


--
-- Name: feed_comments fk_feed_comments_author; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feed_comments
    ADD CONSTRAINT fk_feed_comments_author FOREIGN KEY (author_id) REFERENCES public.users(tg_user_id) ON DELETE CASCADE;


--
-- Name: feed_posts fk_feed_posts_author; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.feed_posts
    ADD CONSTRAINT fk_feed_posts_author FOREIGN KEY (author_id) REFERENCES public.users(tg_user_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

