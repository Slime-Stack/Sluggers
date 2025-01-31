import base64
import json
import os

import functions_framework
import requests
from google.auth import default
from google.cloud import firestore

db = firestore.Client(
    project = "slimeify",  # Your Google Cloud project ID
    database = "mlb-sluggers"
)

API_BASE_URL = os.getenv("SLIME_API_BASE_URL")
# Automatically retrieves the best available credentials
credentials, project = default()

@functions_framework.cloud_event
def ai_processing_service(cloud_event):
    """Triggered by a Pub/Sub message to process AI-generated highlights."""
    try:
        # Decode and parse the Pub/Sub message safely
        message_data = cloud_event.data.get("message", {}).get("data", "")
        if not message_data:
            raise ValueError("Received empty message data")

        decoded_message = json.loads(base64.b64decode(message_data).decode("utf-8"))

        game_pk = decoded_message.get("gamePk")
        if not game_pk:
            raise ValueError("Missing 'gamePk' in Pub/Sub message")

        print(f"Starting AI processing for game {game_pk}...")

        # Firestore update with retry logic
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                # Call the Flask API endpoint
                response = requests.get(f"{API_BASE_URL}/highlights/generate/{game_pk}")
                
                if response.status_code != 200:
                    raise Exception(f"API call failed with status {response.status_code}: {response.text}")

                print(f"AI processing complete for game {game_pk}. API call successful.")
                return {"message": f"AI processing complete for game {game_pk}"}

            except Exception as e:
                print(f"Attempt {attempt}: Failed to process game {game_pk}. Error: {e}")
                if attempt < max_retries:
                    continue  # Retry
                else:
                    print(f"Processing failed after {max_retries} attempts. Logging error.")
                    db.collection("failed_ai_updates").document(str(game_pk)).set({
                        "gamePk": str(game_pk),
                        "error": str(e),
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    return {"error": f"Failed to process game {game_pk}"}

    except Exception as e:
        print(f"Error processing AI assets: {e}")
        return {"error": str(e)}, 500
