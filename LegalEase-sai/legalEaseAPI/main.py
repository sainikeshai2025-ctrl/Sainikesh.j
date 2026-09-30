import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import config
from legalEaseAPI.routes import router as legal_router

# 1. Initialize FastAPI application
app = FastAPI(
    title="LegalEase API",
    description="Backend API powering the LegalEase AI Legal Document Generator",
    version="1.0.0"
)

# 2. Configure CORS middleware for Streamlit and external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include modular routes from routes.py
app.include_router(legal_router)

# 4. Define Root Healthcheck Endpoint
@app.get("/")
def home():
    """
    Root endpoint to verify the LegalEase API service is running.
    """
    return {
        "status": "online",
        "service": "LegalEase: AI-Powered Legal Document Generator API BY LILY",
        "version": "1.0.0",
        "docs_url": "/docs",
        "endpoints": {
            "root": "/",
            "generate": "/generate (POST)",
            "status": "/status (GET)"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "legalEaseAPI.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )
