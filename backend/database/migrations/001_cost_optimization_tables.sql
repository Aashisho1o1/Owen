-- Cost Optimization Tables Migration
-- This migration adds PostgreSQL-based rate limiting, caching, and usage analytics
-- Compatible with existing schema and Railway PostgreSQL

-- 1. Rate Limiting Table (UNLOGGED for performance)
-- Uses Token Bucket + Sliding Window algorithm
CREATE UNLOGGED TABLE IF NOT EXISTS rate_limit (
    user_id INTEGER NOT NULL,
    endpoint TEXT NOT NULL,
    window_start INTEGER NOT NULL,  -- epoch seconds of current bucket
    tokens_left INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, endpoint, window_start)
);

-- Index for cleanup queries
CREATE INDEX IF NOT EXISTS idx_rate_limit_window ON rate_limit (window_start);

-- 2. LLM Response Cache (UNLOGGED for performance)
-- Stores expensive LLM API responses with TTL
CREATE UNLOGGED TABLE IF NOT EXISTS llm_cache (
    key TEXT PRIMARY KEY,
    response JSONB NOT NULL,
    inserted_at TIMESTAMPTZ DEFAULT NOW(),
    ttl_seconds INTEGER NOT NULL DEFAULT 3600,  -- 1 hour default
    cache_type TEXT NOT NULL DEFAULT 'chat',    -- chat, voice_analysis, etc.
    token_count INTEGER DEFAULT 0,              -- for cost tracking
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for efficient queries and cleanup
CREATE INDEX IF NOT EXISTS idx_llm_cache_ttl ON llm_cache (inserted_at, ttl_seconds);
CREATE INDEX IF NOT EXISTS idx_llm_cache_type ON llm_cache (cache_type);
CREATE INDEX IF NOT EXISTS idx_llm_cache_user ON llm_cache (user_id);

-- 3. API Usage Analytics (Standard table for long-term tracking)
-- Tracks API costs and usage patterns for optimization
CREATE TABLE IF NOT EXISTS api_usage_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    llm_provider TEXT,
    tokens_used INTEGER DEFAULT 0,
    estimated_cost_cents INTEGER DEFAULT 0,  -- cost in cents for precision
    cache_hit BOOLEAN DEFAULT FALSE,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    date_bucket DATE GENERATED ALWAYS AS (DATE(created_at)) STORED  -- for daily rollups
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_usage_user_date ON api_usage_analytics (user_id, date_bucket);
CREATE INDEX IF NOT EXISTS idx_usage_endpoint_date ON api_usage_analytics (endpoint, date_bucket);
CREATE INDEX IF NOT EXISTS idx_usage_date ON api_usage_analytics (date_bucket);

-- 4. Rate Limit Configuration (Standard table)
-- Flexible tier-based rate limiting configuration
CREATE TABLE IF NOT EXISTS rate_limit_config (
    tier TEXT PRIMARY KEY,
    endpoint TEXT NOT NULL,
    requests_per_minute INTEGER NOT NULL,
    requests_per_hour INTEGER,
    requests_per_day INTEGER,
    burst_allowance INTEGER DEFAULT 10,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(tier, endpoint)
);

-- Insert default rate limit configurations
INSERT INTO rate_limit_config (tier, endpoint, requests_per_minute, requests_per_hour, requests_per_day, burst_allowance)
VALUES 
    ('free', 'chat', 10, 300, 1000, 5),
    ('free', 'voice_analysis', 3, 50, 200, 2),
    ('free', 'grammar', 20, 500, 2000, 10),
    ('free', 'auth', 5, 20, 100, 3),
    ('premium', 'chat', 50, 1500, 10000, 20),
    ('premium', 'voice_analysis', 15, 300, 2000, 10),
    ('premium', 'grammar', 100, 2000, 20000, 50),
    ('premium', 'auth', 20, 100, 500, 10)
ON CONFLICT (tier, endpoint) DO NOTHING;

-- 5. Create PL/pgSQL function for atomic rate limiting
-- This implements the Token Bucket algorithm with atomic operations
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id INTEGER,
    p_endpoint TEXT,
    p_tier TEXT DEFAULT 'free'
) RETURNS TABLE(allowed BOOLEAN, tokens_remaining INTEGER, reset_time INTEGER) AS $$
DECLARE
    config_row RECORD;
    current_window INTEGER;
    current_time INTEGER;
BEGIN
    -- Get current time as epoch seconds
    current_time := EXTRACT(EPOCH FROM NOW())::INTEGER;
    
    -- Get rate limit configuration for this tier and endpoint
    SELECT requests_per_minute, burst_allowance 
    INTO config_row
    FROM rate_limit_config 
    WHERE tier = p_tier AND endpoint = p_endpoint;
    
    -- If no config found, use default free tier limits
    IF NOT FOUND THEN
        config_row.requests_per_minute := 10;
        config_row.burst_allowance := 5;
    END IF;
    
    -- Calculate current window (60-second buckets)
    current_window := current_time / 60;
    
    -- Atomic upsert with rate limit check
    WITH rate_check AS (
        INSERT INTO rate_limit (user_id, endpoint, window_start, tokens_left)
        VALUES (p_user_id, p_endpoint, current_window, config_row.requests_per_minute - 1)
        ON CONFLICT (user_id, endpoint, window_start)
        DO UPDATE SET 
            tokens_left = GREATEST(rate_limit.tokens_left - 1, -1)
        RETURNING tokens_left
    )
    SELECT 
        CASE WHEN tokens_left >= 0 THEN TRUE ELSE FALSE END as allowed,
        GREATEST(tokens_left, 0) as tokens_remaining,
        (current_window + 1) * 60 as reset_time
    FROM rate_check
    INTO allowed, tokens_remaining, reset_time;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- 6. Cleanup functions for maintenance
CREATE OR REPLACE FUNCTION cleanup_expired_cache() RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM llm_cache 
    WHERE inserted_at < NOW() - (ttl_seconds || ' seconds')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_rate_limits() RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Remove rate limit entries older than 2 hours
    DELETE FROM rate_limit 
    WHERE window_start < (EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours'))::INTEGER / 60;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 7. Usage analytics helper function
CREATE OR REPLACE FUNCTION record_api_usage(
    p_user_id INTEGER,
    p_endpoint TEXT,
    p_llm_provider TEXT DEFAULT NULL,
    p_tokens_used INTEGER DEFAULT 0,
    p_estimated_cost_cents INTEGER DEFAULT 0,
    p_cache_hit BOOLEAN DEFAULT FALSE,
    p_processing_time_ms INTEGER DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    INSERT INTO api_usage_analytics (
        user_id, endpoint, llm_provider, tokens_used, 
        estimated_cost_cents, cache_hit, processing_time_ms
    ) VALUES (
        p_user_id, p_endpoint, p_llm_provider, p_tokens_used,
        p_estimated_cost_cents, p_cache_hit, p_processing_time_ms
    );
END;
$$ LANGUAGE plpgsql;

-- 8. Daily usage summary view
CREATE OR REPLACE VIEW daily_usage_summary AS
SELECT 
    date_bucket,
    user_id,
    endpoint,
    COUNT(*) as total_requests,
    SUM(tokens_used) as total_tokens,
    SUM(estimated_cost_cents) as total_cost_cents,
    AVG(processing_time_ms) as avg_processing_time_ms,
    SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) as cache_hits,
    ROUND(100.0 * SUM(CASE WHEN cache_hit THEN 1 ELSE 0 END) / COUNT(*), 2) as cache_hit_rate
FROM api_usage_analytics
GROUP BY date_bucket, user_id, endpoint
ORDER BY date_bucket DESC, total_cost_cents DESC;

-- Migration complete
SELECT 'Cost optimization tables created successfully' as status; 