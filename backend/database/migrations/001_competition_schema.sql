-- Competition Backend Schema - Minimal & Focused
-- Chrome Built-in AI Challenge 2025

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Character profiles table
CREATE TABLE IF NOT EXISTS character_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    character_name VARCHAR(100) NOT NULL,
    dialogue_samples JSONB DEFAULT '[]'::jsonb,
    voice_traits JSONB DEFAULT '{}'::jsonb,
    sample_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, character_name)
);

-- Documents table (optional - for storing writing)
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_character_profiles_user_id ON character_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);

-- Demo user (optional - for quick testing)
-- Password: demo1234 (hashed with bcrypt)
INSERT INTO users (email, password_hash) VALUES
('demo@owen.ai', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5uFy.r0WRpMDG')
ON CONFLICT (email) DO NOTHING;
