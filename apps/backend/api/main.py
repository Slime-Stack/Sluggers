import logging
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from google.cloud import firestore, pubsub_v1

from apps.backend.api.highlight_generation.highlight_generator import generate_game_highlights
from apps.backend.api.mlb_data_fetching.team_schedules_processor import process_past_games, check_next_game
from apps.backend.config import PROJECT_ID, DATABASE_ID
from apps.backend.utils.constants import TEAMS, ISO_FORMAT

# Initialize Firestore client
db = firestore.Client(
    project=PROJECT_ID,  # Your Google Cloud project ID
    database=DATABASE_ID
)
# Initialize Pub/Sub Publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("slimeify", "sluggers-process-game-status")

app = Flask(__name__)


# Endpoint to fetch all MLB teams
@app.route("/teams", methods=["GET"])
def get_teams():
    return jsonify(TEAMS), 200


# Endpoint to fetch highlights for a specific team
@app.route("/highlights/<int:team_id>", methods=["GET"])
def get_highlights(team_id):
    try:
        highlights_ref = db.collection("highlights")
        query_home = highlights_ref.where("homeTeam", "==", team_id).stream()
        query_away = highlights_ref.where("awayTeam", "==", team_id).stream()

        results = {}

        def process_query(query, label):
            print(f"Processing {label} query for team ID {team_id}...")

            for doc in query:
                highlight = doc.to_dict()
                game_pk = highlight.get("gamePk")

                # Validate storyboard existence (now a dict, not a list)
                if game_pk and isinstance(highlight.get("storyboard"), dict):
                    results[game_pk] = highlight  # Store highlight by gamePk

        # Process both queries
        process_query(query_home, "home")
        process_query(query_away, "away")

        # If no results, return 404
        if not results:
            print(f"No highlights found for team {team_id}.")
            return jsonify({"error": f"No highlights found for team {team_id}"}), 404

        # Ensure sorting by gameDate in descending order
        sorted_highlights = sorted(results.values(), key=lambda h: h["gameDate"], reverse=True)

        return jsonify({"highlights": sorted_highlights}), 200

    except Exception as e:
        print(f"Error fetching highlights for team {team_id}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Endpoint to create a new highlight
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
        if not isinstance(data["homeTeam"], int) or not isinstance(data["awayTeam"], int):
            return jsonify({"error": "'homeTeam' and 'awayTeam' must be objects."}), 400

        # Validate 'storyboard' - it must be a dictionary
        if not isinstance(data.get("storyboard"), dict):
            return jsonify({"error": "'storyboard' must be an object, not an array."}), 400

        # Validate required storyboard fields
        required_storyboard_fields = ["storyTitle", "teaserSummary", "scenes"]
        missing_storyboard_fields = [field for field in required_storyboard_fields if field not in data["storyboard"]]

        if missing_storyboard_fields:
            return jsonify(
                {"error": f"Missing required storyboard fields: {', '.join(missing_storyboard_fields)}"}), 400

        # Validate 'scenes' inside storyboard - it must be a list of objects
        if not isinstance(data["storyboard"]["scenes"], list) or not all(
                isinstance(scene, dict) for scene in data["storyboard"]["scenes"]):
            return jsonify({"error": "'scenes' inside 'storyboard' must be an array of objects."}), 400
        # Convert gamePk to string for consistency
        game_pk_str = str(data["gamePk"])

        # Check if gamePk already exists
        doc_ref = db.collection("highlights").document(game_pk_str)
        if doc_ref.get().exists:
            return jsonify({"error": f"Highlight with gamePk {game_pk_str} already exists."}), 409  # 409 Conflict

        # Add timestamps to the record
        data["gameDate"] = datetime.fromisoformat(data["gameDate"].replace("Z", ISO_FORMAT))
        data["updatedAt"] = datetime.utcnow()
        data["createdAt"] = datetime.utcnow()

        # Insert into Firestore
        doc_ref.set(data)

        return jsonify({"message": "Highlight added successfully", "gamePk": game_pk_str}), 201

    except Exception as e:
        # Log and return the error
        logging.error(f"Error adding highlight: {e}")
        return jsonify({"error": f"An internal error occurred - Error adding highlight: {str(e)}"}), 500


# Endpoint to process final game data and queue upcoming games
@app.route("/highlights/process/<int:season>/", methods=["GET"])
def process_highlights(season):
    """API endpoint to process past games for a specific season, requiring a date and optionally filtering by team."""
    try:
        # Get required date param
        date_param = request.args.get("date")
        if not date_param:
            return jsonify({"error": "Missing required parameter: date (YYYY-MM-DD)"}), 400

        # Validate date format
        try:
            datetime.strptime(date_param, "%Y-%m-%d")  # Validate format
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

        # Get optional team filter
        team_param = request.args.get("teamId")
        team_id = int(team_param) if team_param else None

        # Process past games for the specific date (team filter is optional)
        past_highlights = process_past_games(season, team_id, date_param)
        next_game = check_next_game(season, team_id, date_param)

        response = {
            "processedHighlights": past_highlights,
            "nextGame": next_game if next_game else "No upcoming games within 7 days.",
            "message": f"Highlights processed for {date_param} {f'and team {team_id}' if team_id else ''}"
        }

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error processing highlights: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500


@app.route("/highlights/generate/<string:game_pk>", methods=["GET"])
def generate_highlights(game_pk):
    try:
        generated_highlights = generate_game_highlights(game_pk)
        return jsonify(generated_highlights), 200
    except Exception as e:
        # Log and return the error
        logging.error(f"Error generating highlights for game_pk: {game_pk}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500


# Endpoint for updating highlights

@app.route("/highlights/<string:game_pk>", methods=["PATCH"])
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
        update_data["updatedAt"] = datetime.utcnow().replace(tzinfo=timezone.utc)
        doc_ref.update(update_data)

        return jsonify({"message": f"Highlight {game_pk} updated successfully"}), 200

    except Exception as e:
        logging.error(f"Error updating highlight {game_pk}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500


# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
