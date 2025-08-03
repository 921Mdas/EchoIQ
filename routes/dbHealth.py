from fastapi import APIRouter
import os
from database.database import get_db_cursor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/db-status")
async def check_db_status():
    try:
        conn, cursor = get_db_cursor()
        if conn and cursor:
            db_params = conn.get_dsn_parameters()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            return {
                "status": "healthy",
                "message": "Database connection successful",
                "details": {
                    "mode": os.getenv("MODE", "development"),
                    "dbname": db_params.get('dbname', 'unknown')
                }
            }
        return {"status": "unhealthy", "message": "Database connection failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}