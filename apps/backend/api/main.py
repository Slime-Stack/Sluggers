from flask import Flask, jsonify, request
import requests
import json 
from google.cloud import firestore, pubsub_v1
from datetime import datetime, timedelta, timezone

# Initialize Firestore client
db = firestore.Client(
    project="slimeify",  # Google Cloud project ID
    database="mlb-sluggers"  # Must be declared if it's not "(default)"
)

# Initialize Pub/Sub Publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("slimeify", "sluggers-process-game-status")

app = Flask(__name__)

# Function to construct the team logo URL
def get_team_logoUrl(teamId):
    return f'https://www.mlbstatic.com/team-logos/{teamId}.svg'

# Endpoint to fetch all MLB teams
@app.route("/teams", methods=["GET"])
def get_teams():
    teams = [
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/109.svg",
                    "name": "Arizona Diamondbacks",
                    "shortName": "D-backs",
                    "teamId": 109
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/133.svg",
                    "name": "Athletics",
                    "shortName": "Athletics",
                    "teamId": 133
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/144.svg",
                    "name": "Atlanta Braves",
                    "shortName": "Braves",
                    "teamId": 144
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/110.svg",
                    "name": "Baltimore Orioles",
                    "shortName": "Orioles",
                    "teamId": 110
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/111.svg",
                    "name": "Boston Red Sox",
                    "shortName": "Red Sox",
                    "teamId": 111
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/112.svg",
                    "name": "Chicago Cubs",
                    "shortName": "Cubs",
                    "teamId": 112
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/145.svg",
                    "name": "Chicago White Sox",
                    "shortName": "White Sox",
                    "teamId": 145
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/113.svg",
                    "name": "Cincinnati Reds",
                    "shortName": "Reds",
                    "teamId": 113
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/114.svg",
                    "name": "Cleveland Guardians",
                    "shortName": "Guardians",
                    "teamId": 114
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/115.svg",
                    "name": "Colorado Rockies",
                    "shortName": "Rockies",
                    "teamId": 115
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/116.svg",
                    "name": "Detroit Tigers",
                    "shortName": "Tigers",
                    "teamId": 116
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/117.svg",
                    "name": "Houston Astros",
                    "shortName": "Astros",
                    "teamId": 117
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/118.svg",
                    "name": "Kansas City Royals",
                    "shortName": "Royals",
                    "teamId": 118
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/108.svg",
                    "name": "Los Angeles Angels",
                    "shortName": "Angels",
                    "teamId": 108
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/119.svg",
                    "name": "Los Angeles Dodgers",
                    "shortName": "Dodgers",
                    "teamId": 119
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/146.svg",
                    "name": "Miami Marlins",
                    "shortName": "Marlins",
                    "teamId": 146
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/158.svg",
                    "name": "Milwaukee Brewers",
                    "shortName": "Brewers",
                    "teamId": 158
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/142.svg",
                    "name": "Minnesota Twins",
                    "shortName": "Twins",
                    "teamId": 142
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/121.svg",
                    "name": "New York Mets",
                    "shortName": "Mets",
                    "teamId": 121
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/147.svg",
                    "name": "New York Yankees",
                    "shortName": "Yankees",
                    "teamId": 147
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/143.svg",
                    "name": "Philadelphia Phillies",
                    "shortName": "Phillies",
                    "teamId": 143
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/134.svg",
                    "name": "Pittsburgh Pirates",
                    "shortName": "Pirates",
                    "teamId": 134
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/135.svg",
                    "name": "San Diego Padres",
                    "shortName": "Padres",
                    "teamId": 135
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/137.svg",
                    "name": "San Francisco Giants",
                    "shortName": "Giants",
                    "teamId": 137
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/136.svg",
                    "name": "Seattle Mariners",
                    "shortName": "Mariners",
                    "teamId": 136
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/138.svg",
                    "name": "St. Louis Cardinals",
                    "shortName": "Cardinals",
                    "teamId": 138
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/139.svg",
                    "name": "Tampa Bay Rays",
                    "shortName": "Rays",
                    "teamId": 139
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/140.svg",
                    "name": "Texas Rangers",
                    "shortName": "Rangers",
                    "teamId": 140
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/141.svg",
                    "name": "Toronto Blue Jays",
                    "shortName": "Blue Jays",
                    "teamId": 141
                },
                {
                    "logoUrl": "https://www.mlbstatic.com/team-logos/120.svg",
                    "name": "Washington Nationals",
                    "shortName": "Nationals",
                    "teamId": 120
                }
            ]
    return jsonify(teams), 200

    # URL for the MLB API
    # teams_endpoint_url = 'https://statsapi.mlb.com/api/v1/teams?sportId=1'

    # try:
        # Fetch data from the MLB API
        # response = requests.get(teams_endpoint_url)
        # response.raise_for_status()  # Raise exception for HTTP errors
        # data = response.json()

        # Parse and format team data
        # teams = []
        # for team in data['teams']:
          #  team_data = {
          #      'teamId': team['id'],
          #      'name': team['name'],
          #      'shortName': team['teamName'],
          #      'logoUrl': get_team_logoUrl(team['id'])
          #  }
          #  teams.append(team_data)

        # Sort teams alphabetically by name
        #teams_sorted = sorted(teams, key=lambda x: x['name'])
        #return jsonify(teams_sorted)

    #except requests.exceptions.RequestException as e:
        #return jsonify({"error": str(e)}), 500


# Endpoint to fetch highlights for a specific team
@app.route("/highlights/<int:teamId>", methods=["GET"])
def get_highlights(teamId):
    try:
        highlights_ref = db.collection("highlights")
        query = highlights_ref.where("homeTeam.team_id", "==", teamId).stream()
        query_away = highlights_ref.where("awayTeam.team_id", "==", teamId).stream()

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
        print(f"Error fetching highlights for team {teamId}: {e}")
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
        data["gameDate"] = datetime.fromisoformat(data["gameDate"].replace("Z", "+00:00"))
        data["updatedAt"] = datetime.utcnow()
        data["createdAt"] = datetime.utcnow()

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
def process_highlights(teamId, season):
    """API endpoint to process past games and find next upcoming game"""
    try:
        current_year = datetime.utcnow().year

        if season < current_year:
            return jsonify({"error": f"Invalid season: {season}. The season must be {current_year} or later."}), 400

        past_highlights = process_past_games(teamId, season)
        next_game = check_next_game(teamId, season)

        return jsonify({
            "processedHighlights": past_highlights,
            "nextGame": next_game if next_game else "No upcoming games within 7 days."
        }), 200

    except Exception as e:
        print(f"Error processing highlights: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Endpoint for updating highlights
@app.route("/highlights/<string:gamePk>", methods=["PATCH"])
def update_highlight(gamePk):
    """Update specific fields of an existing highlight without overwriting other fields."""
    try:
        # Parse incoming JSON payload
        update_data = request.get_json()

        # Reference the document in Firestore
        doc_ref = db.collection("highlights").document(gamePk)
        doc = doc_ref.get()

        # Check if document exists
        if not doc.exists:
            return jsonify({"error": f"Highlight with gamePk {gamePk} not found"}), 404

        # Update Firestore document
        update_data["updatedAt"] = datetime.utcnow().replace(tzinfo=timezone.utc)
        doc_ref.update(update_data)

        return jsonify({"message": f"Highlight {gamePk} updated successfully"}), 200

    except Exception as e:
        print(f"Error updating highlight {gamePk}: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
