-- Guest Sessions Migration
-- This creates a separate table for guest sessions instead of polluting the users table
-- Engineering rationale: Separation of concerns and data hygiene

-- 1. Guest Sessions Table
CREATE TABLE guest_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint VARCHAR(32),
    data JSONB DEFAULT '{}',  -- Extensible data storage for guest-specific info
    converted_to_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Performance Indexes
-- Index on expires_at for cleanup queries (most common operation)
CREATE INDEX idx_guest_expires ON guest_sessions(expires_at) WHERE is_active = TRUE;

-- Index on IP + created_at for rate limiting by IP
CREATE INDEX idx_guest_ip_created ON guest_sessions(ip_address, created_at);

-- Index on device fingerprint for device binding
CREATE INDEX idx_guest_device ON guest_sessions(device_fingerprint) WHERE is_active = TRUE;

-- JSONB index for flexible querying of guest data
CREATE INDEX idx_guest_data ON guest_sessions USING GIN(data);

-- 3. Guest Analytics Table
-- Separate table for tracking guest behavior (conversion optimization)
CREATE TABLE guest_analytics (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES guest_sessions(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for analytics queries
CREATE INDEX idx_guest_analytics_session ON guest_analytics(session_id, created_at);
CREATE INDEX idx_guest_analytics_action ON guest_analytics(action, created_at);

-- 4. Update Rate Limit Configuration for Guest Tier
-- Add guest-specific rate limits that are more restrictive
INSERT INTO rate_limit_config (tier, endpoint, requests_per_minute, requests_per_hour, requests_per_day, burst_allowance)
VALUES 
    -- Very conservative limits for guests to prevent abuse
    ('guest', 'chat', 3, 50, 200, 2),                    -- 3 chats/min, 50/hour
    ('guest', 'voice_analysis', 1, 6, 30, 1),            -- 1 analysis/min, 6/hour  
    ('guest', 'grammar', 5, 100, 500, 3),                -- 5 grammar checks/min
    ('guest', 'auth', 10, 50, 100, 5),                   -- More auth attempts for conversions
    ('guest', 'general', 10, 200, 1000, 5);              -- General API limits

-- 5. Cleanup Function
-- Efficient batched cleanup to avoid long locks
CREATE OR REPLACE FUNCTION cleanup_expired_guests(batch_size INTEGER DEFAULT 100) 
RETURNS TABLE(deleted_sessions INTEGER, deleted_analytics INTEGER) AS $$
DECLARE
    deleted_sess INTEGER := 0;
    deleted_anal INTEGER := 0;
    batch_deleted INTEGER;
BEGIN
    -- Clean up expired guest sessions in batches
    LOOP
        WITH expired_batch AS (
            SELECT id FROM guest_sessions 
            WHERE expires_at < NOW() 
            AND converted_to_user_id IS NULL
            AND is_active = TRUE
            LIMIT batch_size
        )
        DELETE FROM guest_sessions 
        WHERE id IN (SELECT id FROM expired_batch);
        
        GET DIAGNOSTICS batch_deleted = ROW_COUNT;
        deleted_sess := deleted_sess + batch_deleted;
        
        -- Exit when no more rows to delete
        EXIT WHEN batch_deleted = 0;
        
        -- Small delay to prevent overwhelming the database
        PERFORM pg_sleep(0.1);
    END LOOP;
    
    -- Clean up orphaned analytics (should cascade, but defensive programming)
    DELETE FROM guest_analytics 
    WHERE session_id NOT IN (SELECT id FROM guest_sessions);
    
    GET DIAGNOSTICS deleted_anal = ROW_COUNT;
    
    RETURN QUERY SELECT deleted_sess, deleted_anal;
END;
$$ LANGUAGE plpgsql;

-- 6. Guest Conversion Function
-- Helper function for converting guest to user
CREATE OR REPLACE FUNCTION convert_guest_session(
    p_session_id UUID,
    p_user_id INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    -- Mark session as converted
    UPDATE guest_sessions 
    SET converted_to_user_id = p_user_id,
        is_active = FALSE
    WHERE id = p_session_id 
    AND expires_at > NOW()
    AND is_active = TRUE;
    
    -- Return true if session was found and updated
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
