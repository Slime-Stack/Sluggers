import base64
import json

import functions_framework
import requests
from google.auth import default

from apps.backend.api.database.sluggers_client import db
from apps.backend.utils.pubsub_utils import publisher, ai_processing_topic

# Automatically retrieves the best available credentials
credentials, project = default()

@functions_framework.cloud_event
def process_game_status_event(cloud_event):
    """Triggered by a Pub/Sub message to check game status from the MLB API."""
    try:
        # Decode and parse the Pub/Sub message safely
        message_data = cloud_event.data.get("message", {}).get("data", "")
        if not message_data:
            raise ValueError("Received empty message data")

        decoded_message = json.loads(base64.b64decode(message_data).decode("utf-8"))

        game_pk = decoded_message.get("gamePk")
        if not game_pk:
            raise ValueError("Missing 'gamePk' in Pub/Sub message")

        print(f"Checking status for game {game_pk}...")

        # Fetch game status from MLB API
        mlb_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
        response = requests.get(mlb_url)

        if response.status_code != 200:
            raise ValueError(f"MLB API request failed: {response.text}")

        game_data = response.json()
        game_status = game_data["gameData"]["status"]["abstractGameState"]

        if game_status == "Final":
            print(f"Game {game_pk} is Final. Updating Firestore and triggering AI processing.")

            # Update Firestore to mark the game as Final
            db.collection("highlights").document(str(game_pk)).update({"status": "Final"})

            # Publish message to AI Processing Pub/Sub topic
            ai_message = json.dumps({"gamePk": game_pk}).encode("utf-8")
            future = publisher.publish(ai_processing_topic, ai_message)
            print(f"AI Processing triggered for game {game_pk}, Message ID: {future.result()}")

            return {"message": f"Game {game_pk} is Final. AI processing started."}, 200
        else:
            print(f"Game {game_pk} is still {game_status}. Retrying later...")

    except Exception as e:
        print(f"Error processing game status: {e}")
        return {"error": str(e)}, 500
