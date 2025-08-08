
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database.database import get_db_cursor
from auth.auth_helper import hash_password, create_token

class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# auth/signup.py
router = APIRouter()

@router.post("/signup")
def signup(user: SignupRequest):
    try:
        hashed_pw = hash_password(user.password)
        conn = get_db_cursor()
        cur = conn.cursor()
        if not conn or not cur:
            conn.rollback()
            cur.close()
            raise HTTPException(status_code=500, detail="Database connection error")
        if not isinstance(user.full_name, str) or not isinstance(user.email, str) or not isinstance(user.password, str):
            raise HTTPException(status_code=400, detail="Invalid input format")
        user.full_name = user.full_name.strip()
        user.email = user.email.strip()
        user.password = user.password.strip()
        # Validate required fields
        # Ensure full_name, email, and password are provided
        if not user.full_name or not user.email or not user.password:
            raise HTTPException(status_code=400, detail="Full name, email, and password are required")
        # Check if email already exists
        cur.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (user.full_name, user.email, hashed_pw)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        token = create_token(user_id)
        return {"token": token, "full_name": user.full_name}
    except Exception:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Email already exists or invalid data.")