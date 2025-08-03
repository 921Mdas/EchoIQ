from fastapi import APIRouter, Request, Query, HTTPException
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "message": "Welcome to the Python Backend API!"}