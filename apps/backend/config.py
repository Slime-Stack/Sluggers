import os

from dotenv import load_dotenv
from google.cloud import secretmanager


def get_credentials_from_secret_manager(project_id, secret_name):
    """Retrieves credentials from Secret Manager.

    Args:
        project_id: The Google Cloud project ID.
        secret_name: The name of the secret in Secret Manager.

    Returns:
        A dictionary containing the credentials, or None if an error occurs.
    """

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

    try:
        response = client.access_secret_version(name=name)
        credentials_json = response.payload.data.decode("UTF-8") # Decode from bytes
        return credentials_json
    except Exception as e:
        print(f"Error accessing secret: {e}")
        return None


def use_credentials(credentials):
    """Uses the retrieved credentials to authenticate with a Google Cloud service.

    Args:
        credentials: The credentials dictionary.
    """
    from google.oauth2 import service_account  # For service account credentials

    try:
      creds = service_account.Credentials.from_service_account_info(credentials)
      # Now you can use 'creds' to access Google Cloud services
      # Example:
      from googleapiclient.discovery import build
      service = build('cloudresourcemanager', 'v1', credentials=creds)
      projects = service.projects().list().execute()
      print(projects)

    except Exception as e:
        print(f"Error using credentials: {e}")


load_dotenv()  # Load environment variables from .env if present

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
REGION = os.getenv("REGION", "us-central1")
BUCKET_URI = os.getenv("GCS_BUCKET")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SLIME_API_BASE_URL = os.getenv("SLIME_API_BASE_URL")
DATABASE_ID = os.getenv("DATABASE_ID")
if not PROJECT_ID:
    raise ValueError("PROJECT_ID environment variable is not set.")

if not BUCKET_URI:
    raise ValueError("BUCKET_URI environment variable is not set.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")


