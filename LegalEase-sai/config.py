import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the LegalEase Project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")

# FastAPI Server Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
GENERATE_ENDPOINT = f"{API_BASE_URL}/generate"

# Asset Paths
IMAGE_DIR = BASE_DIR / "Image" if (BASE_DIR / "Image").exists() else BASE_DIR / "image"
LOGO_PATH = IMAGE_DIR / "Logo.png"
INVERSE_LOGO_PATH = IMAGE_DIR / "inverseLogo.png"
