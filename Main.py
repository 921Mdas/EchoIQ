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
from routes.data import router as data_router
from routes.health import router as health_router
from routes.dbHealth import router as db_health_router
from routes.login import router as login_router
from routes.signup import router as signup_router
from routes.scrape import create_scrape_router
from MainScraper import main_scraper
# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

#routes
app.include_router(data_router)
app.include_router(health_router)
app.include_router(db_health_router)
app.include_router(login_router)
app.include_router(signup_router)
scraper_router = create_scrape_router(main_scraper)
app.include_router(scraper_router)

# CORS Configuration - Updated to allow POST requests
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "https://echoiq921.netlify.app",
#         "https://*.netlify.app",
#         "https://deploy-preview-*.netlify.app"
#     ],
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],  # Added POST here
#     allow_headers=["*"],
#     expose_headers=["*"],
    
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Exact URL (Vite default)
        "http://127.0.0.1:5173",  # Alternative
        "https://echoiq921.netlify.app",
        "https://*.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (simpler)
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"]  # Expose all headers
)


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