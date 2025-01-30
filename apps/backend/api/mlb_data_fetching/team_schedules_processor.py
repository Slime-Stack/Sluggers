from flask import jsonify
import requests
from datetime import datetime, timedelta, timezone
from apps.backend.api.database.sluggers_client import db
from apps.backend.utils.constants import ISO_FORMAT, MLB_SCHEDULE_API_BASE_URL, MLB_LOGOS_URL
from apps.backend.utils.pubsub_utils import publish_game_status_event

# Function to process past finalized games
def process_past_games(team_id, season):
    """Processes finalized past games and stores them in Firestore"""
    try:
        data = _fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            print(f"No data fetched for team {team_id}, season {season}.")
            return []

        current_date = _get_current_date()
        highlights = []

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = _get_game_date(game)

                # Only process games that are Final
                if game["status"].get("abstractGameState") == "Final":
                    game_pk_str = str(game["gamePk"])  # Convert gamePk to string
                    highlight = {
                        "gamePk": game_pk_str,
                        "gameDate": game_date,
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
                        "updatedAt": current_date,
                        "createdAt": current_date,
                    }

                    # Save to Firestore
                    db.collection("highlights").document(game_pk_str).set(highlight)
                    highlights.append(highlight)

        print(f"Processed {len(highlights)} highlights for team {team_id}.")
        return highlights

    except Exception as e:
        print(f"Error processing past games: {e}")
        return []

# Checks for upcoming games & sends pubsub message
def check_next_game(team_id, season):
    """Finds the next upcoming game within the next 7 days and stores it in the 'highlights' collection."""
    try:
        data = _fetch_schedule(team_id, season)
        if not data or "dates" not in data:
            print(f"No schedule data found for team {team_id}, season {season}.")
            return None

        current_date = _get_current_date()
        next_game = None

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = _get_game_date(game)

                if current_date < game_date <= current_date + timedelta(days=7):
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
                            "updatedAt": current_date,
                            "createdAt": current_date
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

def _get_teams_from_api():
    teams_endpoint_url = "https://statsapi.mlb.com/api/v1/teams?sportId=1"
    try:
        response = requests.get(teams_endpoint_url)
        response.raise_for_status()
        data = response.json()

        teams = []
        for team in data["teams"]:
            team_data = {
                "teamId": team['id'],
                "name": team['name'],
                "shortName": team['teamName'],
                "logoUrl": _get_team_logo_url(team['id'])
            }
            teams.append(team_data)

        teams_sorted = sorted(teams, key = lambda x: x['name'])
        return jsonify(teams_sorted)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}, 500)

# Function to construct the team logo URL
def _get_team_logo_url(team_id):
    return f"{MLB_LOGOS_URL}{team_id}.svg"

def _fetch_schedule(team_id, season):
    """Fetches schedule data from MLB Stats API"""
    url = f"{MLB_SCHEDULE_API_BASE_URL}?sportId=1&season={season}&teamId={team_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching schedule: {response.text}")
        return None
    return response.json()

def _get_current_date():
    return datetime.now().replace(tzinfo=timezone.utc)

def _get_game_date(game):
    return datetime.fromisoformat(game["gameDate"].replace("Z", ISO_FORMAT)).astimezone(timezone.utc)
