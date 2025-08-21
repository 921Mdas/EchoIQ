import os
import psycopg2
import time
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    print("🔄 Checking database migrations...")
    conn = None
    max_retries = 5
    retry_delay = 3  # seconds
    
    for attempt in range(max_retries):
        try:
            # In production, we'll only use DATABASE_URL
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable is required")
            
            print(f"🔧 Attempting database connection (try {attempt + 1}/{max_retries})...")
            conn = psycopg2.connect(db_url)
            print("✅ Database connection established")
            
            # Get the directory where THIS script lives
            migration_dir = os.path.dirname(__file__)
            
            with conn.cursor() as cur:
                # Explicitly create migrations table in public schema
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS public._migrations (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) UNIQUE NOT NULL,
                        executed_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Get completed migrations
                cur.execute("SELECT filename FROM public._migrations")
                completed = {row[0] for row in cur.fetchall()}
                
                # Apply new migrations
                for filename in sorted(os.listdir(migration_dir)):
                    if filename.endswith(".sql"):
                        with open(os.path.join(migration_dir, filename), 'r') as f:
                            sql = f.read()
                        
                        try:
                            if filename not in completed:
                                print(f"⚙️ Applying {filename}...")
                                cur.execute(sql)
                                
                                # Skip inserting if it's the initial schema (since it inserts itself)
                                if "001_initial_schema.sql" not in filename:
                                    cur.execute(
                                        "INSERT INTO public._migrations (filename) VALUES (%s)", 
                                        (filename,)
                                    )
                                print(f"✅ Successfully applied {filename}")
                            else:
                                print(f"⏩ Already applied: {filename}")
                                
                        except psycopg2.errors.UniqueViolation:
                            print(f"⚠️ Migration {filename} already recorded (continuing)")
                            conn.rollback()
                            continue
                        except psycopg2.Error as e:
                            print(f"❌ SQL error in {filename}: {e}")
                            conn.rollback()
                            raise
            
            conn.commit()
            print("✔️ Database migrations complete")
            return  # Success - exit the retry loop

        except psycopg2.OperationalError as e:
            print(f"⚠️ Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise  # Re-raise on final attempt
            time.sleep(retry_delay)
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if conn: conn.rollback()
            raise
            
        finally:
            if conn: conn.close()

if __name__ == "__main__":
    run_migrations()
