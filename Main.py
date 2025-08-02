# === Standard Library ===
import os
import logging

# === Third-Party Libraries ===
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

#==== Local Imports ===
from database.database import get_db_cursor
# database.py contains the get_db_cursor function to connect to the database
# migrations.migrate contains the run_migrations function to handle database migrations
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set up the FastAPI application    
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://echoiq921.netlify.app",
        "https://*.netlify.app",
        "https://deploy-preview-*.netlify.app"
    ],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Root endpoint
@app.get("/api")
def read_root():
    return {"message": "Welcome to the Python Backend API!"}

@app.options("/api")
async def options_root():
    return {"message": "CORS preflight approved"}

# Health check endpoint
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.options("/api/health")
async def options_health():
    return {"message": "CORS preflight approved"}

# Greeting endpoint
@app.get("/api/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.options("/api/greet/{name}")
async def options_greet(name: str):
    return {"message": "CORS preflight approved"}

#db status endpoint
@app.get("/api/db-status")
async def check_db_status():
    try:
        # Test database connection
        conn, cursor = get_db_cursor()
        if conn and cursor:
            # Get connection details BEFORE closing
            db_params = conn.get_dsn_parameters()
            cursor.execute("SELECT 1")  # Simple test query
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

if __name__ == "__main__":
    if os.getenv("MODE") == "production":
        from migrations.migrate import run_migrations
        run_migrations()
    uvicorn.run(
        "Main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
        reload_includes=["Main.py"],  # Only watch this specific file
        reload_excludes=["*"]         # Ignore everything else
    )