
-- Ensure superuser exists
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'postgres') THEN
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  END IF;
END $$;

-- Create application user
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'vongaimusvaire') THEN
    CREATE ROLE vongaimusvaire WITH LOGIN PASSWORD 'MySushi32';
  END IF;
  ALTER ROLE vongaimusvaire WITH PASSWORD 'MySushi32';
END $$;

-- Create database
CREATE DATABASE echo_db OWNER vongaimusvaire;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE echo_db TO vongaimusvaire;
