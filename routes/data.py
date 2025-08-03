# Root endpoint
from fastapi import APIRouter, Request, Query, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api")
def read_root():
    return {"message": "Welcome to the Python Backend API!"}

@router.options("/api")
async def options_root():
    return {"message": "CORS preflight approved"}