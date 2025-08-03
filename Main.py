# === Standard Library ===
import os
import logging

# === Third-Party Libraries ===
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from playwright.sync_api import sync_playwright

# === Local Imports ===
from database.database import get_db_cursor
from routes.data import router as data_router
from scrape.scrape_engine.ScrapSources import Scrap_SourceBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# CORS Configuration - Updated to allow POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://echoiq921.netlify.app",
        "https://*.netlify.app",
        "https://deploy-preview-*.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],  # Added POST here
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers (uncomment if needed)
# app.include_router(data_router)

# ===== API Endpoints =====
@app.get("/api")
def read_root():
    return {"message": "Welcome to the Python Backend API!"}

@app.options("/api")
async def options_root():
    return {"message": "CORS preflight approved"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.options("/api/health")
async def options_health():
    return {"message": "CORS preflight approved"}

@app.get("/api/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.options("/api/greet/{name}")
async def options_greet(name: str):
    return {"message": "CORS preflight approved"}

@app.get("/api/db-status")
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

@app.options("/api/db-status")
async def options_db_status():
    return {"message": "CORS preflight approved"}

# Correct endpoint definition (POST method)
@app.post("/api/scrape")
async def trigger_scraping(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(main_scraper)
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
    
@app.options("/api/scrape")
async def options_scrape():
    return {"message": "CORS preflight approved"}


# ===== Scraping Endpoint =====
def main_scraper():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            Scrap_SourceBase(page)
            browser.close()
        logger.info("✅ Scraping completed successfully")
    except Exception as e:
        logger.error(f"❌ Scraping failed: {str(e)}")
        raise


# ===== Startup Events =====
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    if os.getenv("MODE") == "production":
        from migrations.migrate import run_migrations
        run_migrations()
    # Print all registered routes
    for route in app.routes:
        logger.info(f"Registered route: {route.path} - {route.methods}")

# ===== Main Application =====
if __name__ == "__main__":
    uvicorn.run(
        "Main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        reload_includes=["*.py"],
        log_level="info"
    )