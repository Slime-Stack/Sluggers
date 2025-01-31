import os
from dotenv import load_dotenv

from apps.backend.utils.constants import PROJECT_ID, BUCKET_URI

load_dotenv()  # Load environment variables from .env if present

PROJECT_ID = PROJECT_ID
REGION = os.getenv("REGION", "us-central1")
BUCKET_URI = BUCKET_URI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLIME_API_BASE_URL = os.getenv("SLIME_API_BASE_URL")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID environment variable is not set.")

if not BUCKET_URI:
    raise ValueError("BUCKET_URI environment variable is not set.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")
