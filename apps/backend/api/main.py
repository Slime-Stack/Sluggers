from datetime import datetime, timezone

from flask import Flask, jsonify, request

from apps.backend.api.database.sluggers_client import db
from apps.backend.api.mlb_data_fetching.team_schedules_processor import process_past_games, check_next_game
from apps.backend.utils.constants import ISO_FORMAT, TEAMS

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
