from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production!
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