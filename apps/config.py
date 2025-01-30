import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env if present

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
BUCKET_URI = os.getenv("BUCKET_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not PROJECT_ID:
    raise ValueError("PROJECT_ID environment variable is not set.")

if not BUCKET_URI:
    raise ValueError("BUCKET_URI environment variable is not set.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")
