import functions_framework
import json
import requests
from google.cloud import storage, firestore
from google.auth import default
from google.cloud import pubsub_v1

# Automatically retrieves the best available credentials
credentials, project = default()

# Initialize Firestore and Cloud Storage
db = firestore.Client(project="slimeify")
storage_client = storage.Client()
bucket_name = "mlb-sluggers-assets"

@functions_framework.cloud_event
def ai_processing_service(cloud_event):
    """Triggered by a Pub/Sub message to process AI-generated highlights."""
    try:
        # Decode the Pub/Sub message
        message_data = cloud_event.data["message"]["data"]
        decoded_message = json.loads(message_data)

        game_pk = decoded_message["gamePk"]
        print(f"Starting AI processing for game {game_pk}...")

        # Simulate AI-generated assets
        image_url = f"https://storage.googleapis.com/{bucket_name}/game_{game_pk}_highlight.jpg"
        audio_url = f"https://storage.googleapis.com/{bucket_name}/game_{game_pk}_audio.mp3"

        # Firestore update with retry logic
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                db.collection("highlights").document(game_pk).update({
                    "storyboard": [{"imageUrl": image_url, "audioUrl_en": audio_url}],
                    "status": "Processed"
                })
                print(f"AI processing complete for game {game_pk}. Firestore updated.")
                return {"message": f"AI processing complete for game {game_pk}"}, 200
            except Exception as e:
                print(f"Attempt {attempt}: Failed to update Firestore for game {game_pk}. Error: {e}")
                if attempt < max_retries:
                    continue
                else:
                    print(f"Firestore update failed after {max_retries} attempts. Logging error.")
                    db.collection("failed_ai_updates").document(game_pk).set({
                        "gamePk": game_pk,
                        "error": str(e),
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    return {"error": f"Failed to update Firestore for game {game_pk}"}, 500

    except Exception as e:
        print(f"Error processing AI assets: {e}")
        return {"error": str(e)}, 500