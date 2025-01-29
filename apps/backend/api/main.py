from flask import Flask, jsonify, request
from datetime import datetime, timezone
from apps.backend.api.database.sluggers_client import db
from apps.backend.api.mlb_data_fetching.team_schedules_processor import process_past_games, check_next_game
from apps.backend.utils.constants import ISO_FORMAT, TEAMS
import requests
import json
from google.cloud import firestore, pubsub_v1
from datetime import datetime, timedelta, timezone

# Initialize Pub/Sub Publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("slimeify", "sluggers-process-game-status")

app = Flask(__name__)

# Endpoint to fetch all MLB teams
@app.route("/teams", methods=["GET"])
def get_teams():
    return jsonify(TEAMS), 200

# Endpoint to fetch highlights for a specific team
@app.route("/highlights/<int:teamId>", methods=["GET"])
def get_highlights(team_id):
    try:
        highlights_ref = db.collection("highlights")
        query = highlights_ref.where("homeTeam.team_id", "==", team_id).stream()
        query_away = highlights_ref.where("awayTeam.team_id", "==", team_id).stream()

        # Combine results from both queries
        results = []
        for doc in query:
            highlight = doc.to_dict()
            if "storyboard" in highlight and isinstance(highlight["storyboard"], list) and highlight["storyboard"]:
                results.append(highlight)

        for doc in query_away:
            highlight = doc.to_dict()
            if "storyboard" in highlight and isinstance(highlight["storyboard"], list) and highlight["storyboard"]:
                results.append(highlight)

        # Remove duplicates (if any) based on gamePk
        results = {item["gamePk"]: item for item in results}.values()

        # Sort by gameDate in descending order
        results = sorted(results, key=lambda h: h["gameDate"], reverse=True)

        # Return results or 404 if none found
        if not results:
            return jsonify({"error": "No highlights found for the specified team"}), 404
        return jsonify(results), 200

    except Exception as e:
        # Log and return the error
        print(f"Error fetching highlights for team {team_id}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

#Endpoint to create a new highlight
@app.route("/highlights", methods=["POST"])
def add_highlight():
    try:
        # Parse the incoming JSON payload
        data = request.get_json()

        # Validate required fields
        required_fields = ["gamePk", "homeTeam", "awayTeam", "gameDate", "storyboard"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validate 'homeTeam' and 'awayTeam' fields
        if not isinstance(data["homeTeam"], dict) or not isinstance(data["awayTeam"], dict):
            return jsonify({"error": "'homeTeam' and 'awayTeam' must be objects."}), 400

        # Validate 'storyboard' array
        if not isinstance(data["storyboard"], list) or not all(isinstance(item, dict) for item in data["storyboard"]):
            return jsonify({"error": "'storyboard' must be an array of objects."}), 400

        # Validate each storyboard item
        for item in data["storyboard"]:
            if "storyTitle" not in item or "teaserSummary" not in item or "scenes" not in item:
                return jsonify({"error": "Each storyboard must include 'storyTitle', 'teaserSummary', and 'scenes'."}), 400
            if not isinstance(item["scenes"], list):
                return jsonify({"error": "Each storyboard's 'scenes' must be an array."}), 400

        # Convert gamePk to string for consistency
        game_pk_str = str(data["gamePk"])

        # Check if gamePk already exists
        doc_ref = db.collection("highlights").document(game_pk_str)
        if doc_ref.get().exists:
            return jsonify({"error": f"Highlight with gamePk {game_pk_str} already exists."}), 409  # 409 Conflict

        # Add timestamps to the record
        data["gameDate"] = datetime.fromisoformat(data["gameDate"].replace("Z", ISO_FORMAT))
        data["updatedAt"] = datetime.now()
        data["createdAt"] = datetime.now()

        # Insert into Firestore
        doc_ref.set(data)

        return jsonify({"message": "Highlight added successfully", "gamePk": game_pk_str}), 201

    except Exception as e:
        # Log and return the error
        print(f"Error adding highlight: {e}")
        return jsonify({"error": f"An internal error occurred - Error adding highlight: {str(e)}"}), 500

# PROCESSING HIGHLIGHTS
# API edndpoint: /highlights/process/{teamId}
# Variables and functions for processing MLB schedule for final and upcoming games

MLB_API_BASE_URL = "https://statsapi.mlb.com/api/v1/schedule"

def fetch_schedule(team_id, season):
    """Fetches schedule data from MLB Stats API"""
    url = f"{MLB_API_BASE_URL}?sportId=1&season={season}&teamId={team_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching schedule: {response.text}")
        return None
    return response.json()

# Function to publish message to Pub/Sub to kick off Gem/Imagen processing
def trigger_ai_processing(game_pk):
    """Publishes a message to Pub/Sub to start AI processing."""
    message = json.dumps({"gamePk": game_pk}).encode("utf-8")
    future = publisher.publish(topic_path, message)
    print(f"AI Processing triggered for game {game_pk}, ID: {future.result()}")

# Function to process past finalized games
def process_past_games(team_id, season):
    """Processes finalized past games, updates status in Firestore, and triggers AI processing."""
    try:
        data = fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            print(f"No data fetched for team {team_id}, season {season}.")
            return []

        highlights = []
        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_pk_str = str(game["gamePk"])  # Convert gamePk to string
                game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00")).astimezone(timezone.utc)
                game_status = game["status"].get("abstractGameState", "")

                # Only process games that are Final
                if game_status == "Final":
                    doc_ref = db.collection("highlights").document(game_pk_str)
                    doc_snapshot = doc_ref.get()

                    if doc_snapshot.exists:
                        stored_data = doc_snapshot.to_dict()

                        # Update only if the status has changed
                        if stored_data.get("status") != "Final":
                            doc_ref.update({"status": "Final", "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc)})
                            print(f"Updated game {game_pk_str} to Final in Firestore.")

                            # Trigger AI Processing
                            trigger_ai_processing(game_pk_str)
                        else:
                            print(f"Game {game_pk_str} already marked Final, skipping update.")

                    else:
                        # Insert new record
                        highlight = {
                            "gamePk": game_pk_str,
                            "gameDate": game["gameDate"],
                            "homeTeam": {
                                "team_id": game["teams"]["home"]["team"]["id"],
                                "name": game["teams"]["home"]["team"]["name"],
                                "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),
                                "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
                            },
                            "awayTeam": {
                                "team_id": game["teams"]["away"]["team"]["id"],
                                "name": game["teams"]["away"]["team"]["name"],
                                "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),
                                "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
                            },
                            "status": game["status"]["detailedState"],
                            "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc),
                            "createdAt": datetime.utcnow().replace(tzinfo=timezone.utc),
                        }
                        doc_ref.set(highlight)
                        print(f"Inserted new game {game_pk_str} in Firestore.")

                        # Trigger AI Processing
                        trigger_ai_processing(game_pk_str)

                    highlights.append(game_pk_str)

        print(f"Processed {len(highlights)} finalized highlights for team {team_id}.")
        return highlights

    except Exception as e:
        print(f"Error processing past games: {e}")
        return []

# Publishes a message when an upcoming game is detected
def publish_game_status_event(game_pk, game_date, max_retries=3):
    """Publishes a message to Pub/Sub with retry logic."""
    message = json.dumps({"gamePk": game_pk, "gameDate": game_date}).encode("utf-8")

    for attempt in range(1, max_retries + 1):
        try:
            future = publisher.publish(topic_path, message)
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

# Checks for upcoming games & sends pubsub message
def check_next_game(team_id, season):
    """Finds the next upcoming game within the next 7 days and stores it in the 'highlights' collection."""
    try:
        data = fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            print(f"No schedule data found for team {team_id}, season {season}.")
            return None

        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        next_game = None

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00")).astimezone(timezone.utc)

                if game_date > current_date and game_date <= current_date + timedelta(days=7):
                    game_pk = str(game["gamePk"])
                    doc_ref = db.collection("highlights").document(game_pk)

                    # Check if game already exists in Firestore
                    if not doc_ref.get().exists:
                        next_game = {
                            "gamePk": game_pk,
                            "gameDate": game["gameDate"],
                            "homeTeam": {
                                "team_id": game["teams"]["home"]["team"]["id"],
                                "name": game["teams"]["home"]["team"]["name"],
                                "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),
                                "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
                            },
                            "awayTeam": {
                                "team_id": game["teams"]["away"]["team"]["id"],
                                "name": game["teams"]["away"]["team"]["name"],
                                "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),
                                "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
                            },
                            "status": game["status"]["detailedState"],
                            "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc),
                            "createdAt": datetime.utcnow().replace(tzinfo=timezone.utc)
                        }

                        doc_ref.set(next_game)
                        print(f"Stored upcoming game {game_pk} in 'highlights' collection.")

                        # Publish event to Pub/Sub for game status tracking
                        publish_game_status_event(game_pk, game["gameDate"])

                    return next_game

        return None

    except Exception as e:
        print(f"Error checking next game: {e}")
        return None


# Endpoint to process final game data and queue upcoming games
@app.route("/highlights/process/<int:teamId>/<int:season>", methods=["GET"])
def process_highlights(team_id, season):
    """API endpoint to process past games and find next upcoming game"""
    try:
        current_year = datetime.now().year

        if season < current_year:
            return jsonify({"error": f"Invalid season: {season}. The season must be {current_year} or later."}), 400

        past_highlights = process_past_games(team_id, season)
        next_game = check_next_game(team_id, season)

        return jsonify({
            "processedHighlights": past_highlights,
            "nextGame": next_game if next_game else "No upcoming games within 7 days."
        }), 200

    except Exception as e:
        print(f"Error processing highlights: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Endpoint for updating highlights
@app.route("/highlights/<string:gamePk>", methods=["PATCH"])
def update_highlight(game_pk):
    """Update specific fields of an existing highlight without overwriting other fields."""
    try:
        # Parse incoming JSON payload
        update_data = request.get_json()

        # Reference the document in Firestore
        doc_ref = db.collection("highlights").document(game_pk)
        doc = doc_ref.get()

        # Check if document exists
        if not doc.exists:
            return jsonify({"error": f"Highlight with gamePk {game_pk} not found"}), 404

        # Update Firestore document
        update_data["updatedAt"] = datetime.now().replace(tzinfo=timezone.utc)
        doc_ref.update(update_data)

        return jsonify({"message": f"Highlight {game_pk} updated successfully"}), 200

    except Exception as e:
        print(f"Error updating highlight {game_pk}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
