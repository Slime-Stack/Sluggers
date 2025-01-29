from flask import Flask, jsonify, request
import requests
from google.cloud import firestore
from datetime import datetime, timedelta, timezone

# Initialize Firestore client
db = firestore.Client(
    project="slimeify",  # Your Google Cloud project ID
    database="mlb-sluggers"  # Replace with your database name if it's not "(default)"
)
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
            results.append(doc.to_dict())
        for doc in query_away:
            results.append(doc.to_dict())

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

        # Add timestamps to the record
        data["gameDate"] = datetime.fromisoformat(data["gameDate"].replace("Z", "+00:00"))
        data["updatedAt"] = datetime.utcnow()
        data["createdAt"] = datetime.utcnow()

        # Insert into Firestore (use gamePk as the document ID)
        doc_ref = db.collection("highlights").document(str(data["gamePk"]))
        doc_ref.set(data)

        return jsonify({"message": "Highlight added successfully", "gamePk": data["gamePk"]}), 201

    except Exception as e:
        # Log and return the error
        print(f"Error adding highlight: {e}")
        return jsonify({"error": f"An internal error occurred - Error adding highlight: {str(e)}"}), 500

MLB_API_BASE_URL = "https://statsapi.mlb.com/api/v1/schedule"

def fetch_schedule(team_id, season):
    """Fetches schedule data from MLB Stats API"""
    url = f"{MLB_API_BASE_URL}?sportId=1&season={season}&teamId={team_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching schedule: {response.text}")
        return None
    return response.json()

# Function to process past finalized games
def process_past_games(team_id, season):
    """Processes finalized past games and stores them in Firestore"""
    try:
        data = fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            print(f"No data fetched for team {team_id}, season {season}.")
            return []

        current_date = datetime.utcnow().replace(tzinfo=timezone.utc) 
        highlights = []

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00")).astimezone(timezone.utc)

                # Only process games that are Final
                if game["status"].get("abstractGameState") == "Final":
                    game_pk_str = str(game["gamePk"])  # Convert gamePk to string
                    highlight = {
                        "gamePk": game_pk_str,
                        "gameDate": game["gameDate"],
                        "homeTeam": {
                            "team_id": game["teams"]["home"]["team"]["id"],
                            "name": game["teams"]["home"]["team"]["name"],
                            "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),  # Safe access
                            "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
                        },
                        "awayTeam": {
                            "team_id": game["teams"]["away"]["team"]["id"],
                            "name": game["teams"]["away"]["team"]["name"],
                            "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),  # Safe access
                            "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
                        },
                        "status": game["status"]["detailedState"],
                        "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc),
                        "createdAt": datetime.utcnow().replace(tzinfo=timezone.utc),
                    }

                    # Save to Firestore
                    db.collection("highlights").document(game_pk_str).set(highlight)
                    highlights.append(highlight)

        print(f"Processed {len(highlights)} highlights for team {team_id}.")
        return highlights

    except Exception as e:
        print(f"Error processing past games: {e}")
        return []

def check_next_game(team_id, season):
    """Finds the next upcoming game within the next 7 days"""
    try:
        data = fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            return None

        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)  #  Make UTC-aware
        next_game = None

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = datetime.fromisoformat(game["gameDate"].replace("Z", "+00:00")).astimezone(timezone.utc)  # Convert to UTC

                if game_date > current_date and game_date <= current_date + timedelta(days=7):
                    next_game = {
                        "gamePk": str(game["gamePk"]),
                        "gameDate": game["gameDate"],
                        "homeTeam": {
                            "team_id": game["teams"]["home"]["team"]["id"],
                            "name": game["teams"]["home"]["team"]["name"],
                            "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),  # Safe access
                            "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
                        },
                        "awayTeam": {
                            "team_id": game["teams"]["away"]["team"]["id"],
                            "name": game["teams"]["away"]["team"]["name"],
                            "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),  # Safe access
                            "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
                        },
                        "status": game["status"]["detailedState"],
                        "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc)
                    }

                    # Save/update in Firestore
                    db.collection("next_games").document(str(game["gamePk"])).set(next_game)
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
        # Get the current year
        current_year = datetime.utcnow().year

        # Validate the season
        if season < current_year:
            return jsonify({
                "error": f"Invalid season: {season}. The season must be the current year or later."
            }), 400

        # Process past games
        past_highlights = process_past_games(teamId, season)

        # Check for the next game
        next_game = check_next_game(teamId, season)

        response = {
            "processedHighlights": past_highlights,
            "nextGame": next_game if next_game else "No upcoming games within 7 days."
        }

        return jsonify(response), 200

    except Exception as e:
        print(f"Error processing highlights: {e}")
        return jsonify({"error": f"An internal error occurred - {str(e)}"}), 500

# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
