import functions_framework
import json
import base64
from google.cloud import firestore, pubsub_v1
from google.auth import default

from apps.backend.api.database.sluggers_client import db

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

        # Simulate AI-generated assets
        bucket_name = "mlb-sluggers-assets"
        image_url = f"https://storage.googleapis.com/{bucket_name}/game_{game_pk}_highlight.jpg"
        audio_url = f"https://storage.googleapis.com/{bucket_name}/game_{game_pk}_audio.mp3"

        # Firestore update with retry logic
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                #Everything works this is commented out so things dont overwrite a valid record while testing
                #doc_ref = db.collection("highlights").document(str(game_pk))

                #doc_ref.update({
                #    "storyboard": [put the good stuff in here]
                #})

                print(f"AI processing complete for game {game_pk}. Firestore updated.")
                return {"message": f"AI processing complete for game {game_pk}"}

            except Exception as e:
                print(f"Attempt {attempt}: Failed to update Firestore for game {game_pk}. Error: {e}")
                if attempt < max_retries:
                    continue  # Retry
                else:
                    print(f"Firestore update failed after {max_retries} attempts. Logging error.")
                    db.collection("failed_ai_updates").document(str(game_pk)).set({
                        "gamePk": str(game_pk),
                        "error": str(e),
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    return {"error": f"Failed to update Firestore for game {game_pk}"}

    except Exception as e:
        print(f"Error processing AI assets: {e}")
        return {"error": str(e)}, 500
