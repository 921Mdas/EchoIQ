-- ==============================
-- 001_initial_schema.sql
-- ==============================

-- ------------------------------
-- 1️⃣ Create function for triggers
-- ------------------------------
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------
-- 2️⃣ Create articles table
-- ------------------------------
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL DEFAULT 'unknown',
    url VARCHAR(255) UNIQUE NOT NULL,
    date TIMESTAMP WITH TIME ZONE,
    source_name VARCHAR(255) NOT NULL DEFAULT 'unknown',
    source_logo VARCHAR(255) NOT NULL DEFAULT 'unknown',
    author VARCHAR(255) DEFAULT 'unknown',
    category VARCHAR(100) DEFAULT 'unknown',
    body_intro TEXT DEFAULT 'unknown',
    named_entities JSONB,
    first_comment TEXT DEFAULT 'unknown',
    ad_slots JSONB,
    country VARCHAR(100) DEFAULT 'unknown',
    reach INTEGER DEFAULT 0,
    sentiment VARCHAR(50) DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_name);

-- Trigger to auto-update updated_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'update_articles_modtime'
    ) THEN
        CREATE TRIGGER update_articles_modtime
        BEFORE UPDATE ON articles
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    END IF;
END;
$$;

-- ------------------------------
-- 3️⃣ Create users table
-- ------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    provider TEXT DEFAULT 'local',
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for email lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Trigger to auto-update updated_at
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'update_users_modtime'
    ) THEN
        CREATE TRIGGER update_users_modtime
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    END IF;
END;
$$;

-- ------------------------------
-- 4️⃣ Migration tracking
-- ------------------------------
-- Make sure you have a _migrations table first:
-- CREATE TABLE _migrations (id SERIAL PRIMARY KEY, filename TEXT, applied_at TIMESTAMP DEFAULT NOW());

INSERT INTO _migrations (filename)
VALUES ('001_create_tables.sql')
ON CONFLICT DO NOTHING;
