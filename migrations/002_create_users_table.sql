-- ==============================
-- 002_create_auth_users_table.sql
-- ==============================

-- ------------------------------
-- 1️⃣ Ensure trigger function exists
-- ------------------------------
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------
-- 2️⃣ Create auth_users table
-- ------------------------------
CREATE TABLE IF NOT EXISTS auth_users (
    id SERIAL PRIMARY KEY,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    provider TEXT DEFAULT 'local',
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------
-- 3️⃣ Trigger to auto-update updated_at
-- ------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_trigger 
        WHERE tgname = 'update_auth_users_modtime'
    ) THEN
        CREATE TRIGGER update_auth_users_modtime
        BEFORE UPDATE ON auth_users
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    END IF;
END;
$$;

-- ------------------------------
-- 4️⃣ Index for email lookup
-- ------------------------------
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_users(email);

-- ------------------------------
-- 5️⃣ Record this migration safely
-- ------------------------------
INSERT INTO _migrations (filename)
VALUES ('002_create_auth_users_table.sql')
ON CONFLICT DO NOTHING;
