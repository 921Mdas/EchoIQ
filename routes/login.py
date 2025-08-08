
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr
from database.database import get_db_cursor
from auth.auth_helper import hash_password, create_token, verify_password
import psycopg2
import json

router = APIRouter()
logger = None  # Initialize logger if needed, or import from your logging setup


@router.post("/login")
async def login_user(request: Request):
    conn = None
    cur = None
    try:
        # Parse and validate input
        data = await request.json()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")

        # Get database connection
        conn = get_db_cursor()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Create cursor
        cur = conn.cursor()

        # Query database
        try:
            cur.execute(
                "SELECT id, full_name, password_hash FROM users WHERE email = %s", 
                (email,))
            user = cur.fetchone()
        except psycopg2.Error as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail="Database operation failed")

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id, full_name, password_hash = user

        # Verify password
        if not verify_password(password, password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate token
        token = create_token(user_id)
        return {"token": token, "full_name": full_name}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        # Cleanup resources
        try:
            if cur:
                cur.close()
        except Exception as e:
            logger.error(f"Error closing cursor: {str(e)}")
        
        try:
            if conn:
                conn.close()
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")