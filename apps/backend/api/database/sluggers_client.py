from google.cloud import firestore

from apps.backend.utils.constants import PROJECT_ID, DATABASE_ID

db = firestore.Client(
    project = PROJECT_ID,  # Your Google Cloud project ID
    database = DATABASE_ID
)
