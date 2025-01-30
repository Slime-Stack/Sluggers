import json
import time

from google.cloud import pubsub_v1

# Initialize Pub/Sub Publisher
publisher = pubsub_v1.PublisherClient()
game_status_topic_path = publisher.topic_path("slimeify", "sluggers-process-game-status")
ai_processing_topic = publisher.topic_path("slimeify", "sluggers-ai-processing")

# Function to publish message to Pub/Sub to kick off Gem/Imagen processing
def trigger_ai_processing(game_pk):
    """Publishes a message to Pub/Sub to start AI processing."""
    message = json.dumps({"gamePk": game_pk}).encode("utf-8")
    future = publisher.publish(game_status_topic_path, message)
    print(f"AI Processing triggered for game {game_pk}, ID: {future.result()}")

# Publishes a message when an upcoming game is detected
def publish_game_status_event(game_pk, game_date, max_retries=3):
    """Publishes a message to Pub/Sub with retry logic."""
    message = json.dumps({"gamePk": game_pk, "gameDate": game_date}).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            future = publisher.publish(game_status_topic_path, message)
            message_id = future.result(timeout=10)  # Wait for a result
            print(f"Successfully published game {game_pk} to Pub/Sub (Message ID: {message_id})")
            return
        except Exception as e:
            print(f"Attempt {attempt}: Failed to publish Pub/Sub message for game {game_pk}. Error: {e}")
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Exponential backoff (2s, 4s, 8s)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed to publish Pub/Sub message after {max_retries} attempts. Giving up.")
