
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr
from database.database import get_db_cursor
from auth.auth_helper import hash_password, create_token, verify_password
import psycopg2


router = APIRouter()


@router.post("/login")
async def login_user(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    conn = get_db_cursor()
    cur = conn.cursor()

    if not conn or not cur:
        conn.rollback()
        cur.close()
        raise HTTPException(status_code=500, detail="Database connection error")
    if not isinstance(email, str) or not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Invalid input format")
    email = email.strip()
    password = password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    try:
        cur.execute("SELECT id, full_name, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Database error")

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user_id, full_name, password_hash = user

    if not verify_password(password, password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_token(user_id)
    return {"token": token, "full_name": full_name}
