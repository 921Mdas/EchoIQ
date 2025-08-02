import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_migrations():
    print("🔄 Checking database migrations...")
    conn = None
    try:
        mode = os.getenv("MODE", "development").lower()
        
        if mode == "production":
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL is required in production mode")
            conn = psycopg2.connect(db_url)
            print("🔧 Using production database")
        else:
            conn = psycopg2.connect(
                dbname=os.getenv("POSTGRES_DB", "echo_db"),
                user=os.getenv("POSTGRES_USER", "vongaimusvaire"),
                password=os.getenv("POSTGRES_PASSWORD", "MySushi32"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )
            print("🔧 Using development database")

        # Get the directory where THIS script lives
        migration_dir = os.path.dirname(__file__)
        
        with conn.cursor() as cur:
            # Create migrations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS _migrations (
                    id SERIAL PRIMARY KEY,
                    filename VARCHAR(255) UNIQUE NOT NULL,
                    executed_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Get completed migrations
            cur.execute("SELECT filename FROM _migrations")
            completed = {row[0] for row in cur.fetchall()}
            
            # Apply new migrations
            for filename in sorted(os.listdir(migration_dir)):
                if filename.endswith(".sql") and filename not in completed:
                    with open(os.path.join(migration_dir, filename), 'r') as f:
                        sql = f.read()
                    cur.execute(sql)
                    print(f"✅ Applied {filename}")
        
        conn.commit()
        print("✔️ Database is up-to-date")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if conn: conn.rollback()
        raise
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    run_migrations()