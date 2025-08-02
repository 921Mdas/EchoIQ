from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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