# routers/scrape.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from typing import Callable
import logging

logger = logging.getLogger(__name__)

def create_scrape_router(scrape_function: Callable):
    router = APIRouter()
    
    @router.post("/scrape", tags=["scraping"])
    async def trigger_scraping(background_tasks: BackgroundTasks):
        try:
            background_tasks.add_task(scrape_function)
            return {
                "status": "success",
                "message": "Scraping started in background",
                "details": "Check server logs for progress"
            }
        except Exception as e:
            logger.error(f"Failed to start scraping: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Scraping initialization failed: {str(e)}"
            )
    
    return router