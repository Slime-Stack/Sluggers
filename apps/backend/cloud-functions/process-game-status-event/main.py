import functions_framework
import json
import requests
from google.cloud import firestore, pubsub_v1

# Initialize Firestore and Pub/Sub
db = firestore.Client(project="slimeify")
publisher = pubsub_v1.PublisherClient()

ai_processing_topic = publisher.topic_path("slimeify", "sluggers-ai-processing")

@functions_framework.cloud_event
def process_game_status_event(cloud_event):
    """Triggered by a Pub/Sub message to check game status from the MLB API."""
    try:
        # Decode the Pub/Sub message
        message_data = cloud_event.data["message"]["data"]
        decoded_message = json.loads(message_data)

        game_pk = decoded_message["gamePk"]
        mlb_url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/feed/live"

        # Fetch game status
        response = requests.get(mlb_url).json()
        game_status = response["gameData"]["status"]["abstractGameState"]

        if game_status == "Final":
            print(f"Game {game_pk} is Final. Updating Firestore and triggering AI processing.")

            # Update Firestore to mark the game as Final
            db.collection("highlights").document(game_pk).update({"status": "Final"})

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