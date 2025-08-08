
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database.database import get_db_cursor
from auth.auth_helper import hash_password, create_token
import json
import psycopg2

    
class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# auth/signup.py
router = APIRouter()

logger = None  # Initialize logger if needed, or import from your logging setup

@router.post("/signup")
async def signup(user: SignupRequest):
    conn = None
    cur = None
    try:
        # Validate input
        if not all([isinstance(user.full_name, str), 
                   isinstance(user.email, str),
                   isinstance(user.password, str)]):
            raise HTTPException(status_code=400, detail="All fields must be strings")

        user.full_name = user.full_name.strip()
        user.email = user.email.strip().lower()  # Normalize email
        user.password = user.password.strip()

        if not user.full_name or not user.email or not user.password:
            raise HTTPException(status_code=400, 
                              detail="Full name, email, and password are required")

        if len(user.password) < 8:
            raise HTTPException(status_code=400,
                              detail="Password must be at least 8 characters")

        # Get database connection
        conn = get_db_cursor()
        if conn is None:
            raise HTTPException(status_code=500, 
                              detail="Database connection failed")
        
        cur = conn.cursor()

        # Check if email exists first
        cur.execute("SELECT id FROM users WHERE email = %s", (user.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, 
                              detail="Email already registered")

        # Hash password
        hashed_pw = hash_password(user.password)

        # Create user
        try:
            cur.execute(
                """INSERT INTO users (full_name, email, password_hash) 
                   VALUES (%s, %s, %s) RETURNING id""",
                (user.full_name, user.email, hashed_pw)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Database error during signup: {str(e)}")
            raise HTTPException(status_code=500, 
                              detail="Failed to create user")

        # Generate token
        token = create_token(user_id)
        return {
            "token": token, 
            "full_name": user.full_name,
            "email": user.email
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(status_code=500, 
                          detail="Internal server error")
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