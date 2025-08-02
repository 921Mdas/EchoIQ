-- Create articles table with all your fields
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    
    -- Required fields
    title VARCHAR(255) NOT NULL DEFAULT 'unknown',
    url VARCHAR(255) UNIQUE NOT NULL,
    date TIMESTAMP WITH TIME ZONE,
    source_name VARCHAR(255) NOT NULL DEFAULT 'unknown',
    source_logo VARCHAR(255) NOT NULL DEFAULT 'unknown',
    
    -- Optional fields
    author VARCHAR(255) DEFAULT 'unknown',
    category VARCHAR(100) DEFAULT 'unknown',
    body_intro TEXT DEFAULT 'unknown',
    named_entities JSONB,  -- Stores arrays/lists efficiently
    first_comment TEXT DEFAULT 'unknown',
    ad_slots JSONB,        -- Stores arrays/lists efficiently
    country VARCHAR(100) DEFAULT 'unknown',
    reach INTEGER DEFAULT 0,
    sentiment VARCHAR(50) DEFAULT 'unknown',
    
    -- Automatic timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_date ON articles(date);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source_name);

-- Add trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_articles_modtime
BEFORE UPDATE ON articles
FOR EACH ROW
EXECUTE FUNCTION update_modified_column();

-- Migration tracking (don't modify this part)
INSERT INTO _migrations (filename) VALUES ('001_initial_schema.sql');