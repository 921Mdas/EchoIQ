# database/db_dependency.py
from contextlib import asynccontextmanager
from fastapi import HTTPException
from psycopg2.extensions import connection, cursor
from database.database import get_db_cursor

@asynccontextmanager
async def get_db():
    """
    Async context manager for database connections
    """
    db = get_db_cursor()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    conn, cur = db
    try:
        yield conn, cur
    finally:
        cur.close()
        conn.close()