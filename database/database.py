import psycopg2
import os
from typing import Optional, Tuple
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def get_db_cursor() -> Optional[psycopg2.extensions.connection]:
    """
    Returns a database connection.
    Production: Uses DATABASE_URL
    Development: Uses explicit credentials with defaults
    """
    try:
        mode = os.getenv("MODE", "development").lower()

        # Production
        if mode == "production":
            if not os.getenv("DATABASE_URL"):
                raise ValueError("DATABASE_URL required in production mode")
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("DATABASE_URL required in production")
            conn = psycopg2.connect(database_url)
            print(f"✅ Connected to PRODUCTION DB {conn.get_dsn_parameters()['dbname']} at {conn.get_dsn_parameters()['host']}:{conn.get_dsn_parameters()['port']}")
            return conn

        # Development
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "echo_db"),
            user=os.getenv("POSTGRES_USER", "vongaimusvaire"),
            password=os.getenv("POSTGRES_PASSWORD", "MySushi32"),
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432")
        )
        print(f"✅ Connected to DEVELOPMENT DB {conn.get_dsn_parameters()['dbname']} at {conn.get_dsn_parameters()['host']}:{conn.get_dsn_parameters()['port']}")
        return conn

    except psycopg2.OperationalError as e:
        print(f"🚨 Connection failed to connect to {mode} see database.py: {e}")
        return None
    except Exception as e:
        print(f"🚨 Unexpected error in {mode} see database.py: {e}")
        return None


def insertInDB(data: List[Dict]) -> Dict:
    """
    Processes article data with full field handling.
    Returns: {
        'new_articles': int,
        'updated_articles': int,
        'mode': str,
        'success': bool
    }
    """
    # Get database connection and cursor
    conn = get_db_cursor()
    if not conn:
        return {"error": "Connection failed", "success": False}

    cursor = conn.cursor()  # ← PROPER WAY TO GET CURSOR

    new_article_count = 0
    updated_article_count = 0

    try:
        for article in data:
            # Required fields with defaults
            title = article.get('title', 'unknown')
            url = article.get('url')
            date_value = article.get('date', 'unknown')
            source_name = article.get('source_name', 'unknown')
            source_logo = article.get('source_logo', 'unknown')

            # Optional fields with defaults
            author = article.get('author', 'unknown')
            category = article.get('category', 'unknown')
            body_intro = article.get('body_intro', 'unknown')
            named_entities = article.get('named_entities', [])[:5] or None
            first_comment = article.get('first_comment', 'unknown')
            ad_slots = article.get('ad_slots', [])[:5] or None
            country = article.get('country', 'unknown')
            reach = article.get('reach', 0)
            sentiment = article.get('sentiment', 'unknown')

            # Skip if missing required fields
            if not all([title, url, date_value, source_name, source_logo]):
                continue

            # Check for existing article
            cursor.execute("""
                SELECT source_name, source_logo 
                FROM articles 
                WHERE url = %s 
                LIMIT 1;
            """, (url,))
            existing = cursor.fetchone()

            if existing:
                existing_name, existing_logo = existing
                # Update if source info is missing
                if (not existing_name or not existing_logo) and (source_name and source_logo):
                    cursor.execute("""
                        UPDATE articles
                        SET source_name = %s,
                            source_logo = %s
                        WHERE url = %s;
                    """, (source_name, source_logo, url))
                    updated_article_count += 1
                    print(f"🔄 Updated source info for: {title[:50]}...")
                continue

            # Insert new article
            cursor.execute("""
                INSERT INTO articles (
                    title, date, url, source_name, source_logo,
                    author, category, body_intro, named_entities,
                    first_comment, ad_slots, country, reach, sentiment
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                );
            """, (
                title, date_value, url, source_name, source_logo,
                author, category, body_intro, named_entities,
                first_comment, ad_slots, country, reach, sentiment
            ))
            new_article_count += 1
            print(f"✅ Inserted: {title[:50]}...")

        conn.commit()
        print(f"\n📊 Results:")
        print(f"- New articles: {new_article_count}")
        print(f"- Updated articles: {updated_article_count}")
        return {
            "new_articles": new_article_count,
            "updated_articles": updated_article_count,
            "mode": os.getenv("MODE", "development"),
            "success": True
        }

    except psycopg2.Error as e:
        conn.rollback()
        print(f"❌ Database operation failed: {e}")
        return {
            "error": str(e),
            "success": False
        }
    except Exception as e:
        conn.rollback()
        print(f"❌ Unexpected error: {e}")
        return {
            "error": str(e),
            "success": False
        }
    finally:
        cursor.close()
        conn.close()
        print("🔌 Database connection closed")