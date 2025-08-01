from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
# Update your CORS middleware to this exact configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
         "https://echoiq921.netlify.app"   # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/api")
def read_root():
    return {"message": "Welcome to the Python Backend API!"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}