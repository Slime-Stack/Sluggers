from datetime import datetime, timedelta, timezone

import requests
from flask import jsonify
from google.cloud import firestore

from apps.backend.config import PROJECT_ID, DATABASE_ID
from apps.backend.utils.constants import ISO_FORMAT, MLB_SCHEDULE_API_BASE_URL, MLB_LOGOS_URL, MLB_STATS_API_BASE_URL
from apps.backend.utils.pubsub_utils import publish_game_status_event, trigger_ai_processing
from apps.backend.utils.log_util import logger

db = firestore.Client(
    project=PROJECT_ID,  # Your Google Cloud project ID
    database=DATABASE_ID
)


def process_past_games(season, team_id, date):
    """Processes finalized past games, updates status in Firestore, and triggers AI processing."""
    try:
        data = _fetch_schedule(season, team_id, date)
        if not data or "dates" not in data:
            logger.error(f"No data fetched for season {season}, date {date}, team {team_id}.")
            return []

        current_date = get_current_datetime()
        highlights = []

        _loop_over_game_dates(data, current_date, highlights)

        logger.info(f"Processed {len(highlights)} finalized highlights for team {team_id}.")
        return highlights

    except Exception as e:
        logger.error(f"Error processing past games: {e}")
        return []


# Checks for upcoming games & sends pubsub message
def check_next_game(season, team_id, date):
    """Finds the next upcoming game within the next 7 days and stores it in the 'highlights' collection."""
    try:
        data = _fetch_schedule(season, team_id, date)
        if not data or "dates" not in data:
            logger.error(f"No schedule data found for team {team_id}, season {season}.")
            return None

        current_date = get_current_datetime()
        next_game = None

        for date_entry in data["dates"]:
            for game in date_entry["games"]:
                game_date = get_game_datetime(game)

                if current_date < game_date <= current_date + timedelta(days=7):
                    game_pk = str(game["gamePk"])
                    doc_ref = db.collection("highlights").document(game_pk)

                    # Check if game already exists in Firestore
                    if not doc_ref.get().exists:
                        next_game = {
                            "gamePk": game_pk,
                            "gameDate": game["gameDate"],
                            "homeTeam": game["teams"]["home"]["team"]["id"],
                            "awayTeam": game["teams"]["away"]["team"]["id"],
                            "status": game["status"]["detailedState"],
                            "updatedAt": current_date,
                            "createdAt": current_date
                        }

                        doc_ref.set(next_game)
                        logger.info(f"Stored upcoming game {game_pk} in 'highlights' collection.")

                        # Publish event to Pub/Sub for game status tracking
                        publish_game_status_event(game_pk, game["gameDate"])

                    return next_game

        return None

    except Exception as e:
        logger.error(f"Error checking next game: {e}")
        return None


def _loop_over_game_dates(data, current_date, highlights):
    """Process each game in the schedule data."""
    for date_entry in data["dates"]:
        for game in date_entry["games"]:
            if _is_final_game(game):
                game_pk_str = str(game["gamePk"])
                _process_game(game, game_pk_str, current_date, highlights)


def _is_final_game(game):
    """Check if a game is in Final state."""
    return game["status"].get("abstractGameState", "") == "Final"


def _process_game(game, game_pk_str, current_date, highlights):
    """Process a single game and update Firestore."""
    doc_ref = db.collection("highlights").document(game_pk_str)
    doc_snapshot = doc_ref.get()

    if doc_snapshot.exists:
        _update_existing_game(doc_ref, doc_snapshot, game_pk_str, current_date)
    else:
        _create_new_game(doc_ref, game, game_pk_str, current_date)

    highlights.append(game_pk_str)


def _update_existing_game(doc_ref, doc_snapshot, game_pk_str, current_date):
    """Update an existing game if its status has changed to Final."""
    stored_data = doc_snapshot.to_dict()
    if stored_data.get("status") != "Final":
        doc_ref.update({"status": "Final", "updatedAt": current_date})
        logger.info(f"Updated game {game_pk_str} to Final in Firestore.")
        trigger_ai_processing(game_pk_str)
    else:
        logger.info(f"Game {game_pk_str} already marked Final, skipping update.")


def _create_new_game(doc_ref, game, game_pk_str, current_date):
    """Create a new game record in Firestore."""
    game_date = get_game_datetime(game)
    highlight = _create_new_highlight_record(game_pk_str, game_date, game, current_date)
    doc_ref.set(highlight)
    logger.info(f"Inserted new game {game_pk_str} in Firestore.")
    trigger_ai_processing(game_pk_str)


def _create_new_highlight_record(game_pk_str=None, game_date=None, game=None, current_date=None):
    return {
        "gamePk": game_pk_str,
        "gameDate": game_date,
        "homeTeam": game["teams"]["home"]["team"]["id"],
        "awayTeam": game["teams"]["away"]["team"]["id"],
        "status": game["status"]["detailedState"],
        "updatedAt": current_date,
        "createdAt": current_date,
    }


def _get_team_logo_url(team_id):
    return f"{MLB_LOGOS_URL}{team_id}.svg"


# Function to construct the team logo URL
def _fetch_schedule(season, team_id, date):
    """Fetches schedule data from MLB Stats API, filtering by required date and optional team."""
    url = f"{MLB_SCHEDULE_API_BASE_URL}?sportId=1&season={season}&teamId={team_id}&date={date}"

    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Error fetching schedule: {response.text}")
        return None
    return response.json()


def get_current_datetime():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def get_game_datetime(game):
    return datetime.fromisoformat(game["gameDate"].replace("Z", ISO_FORMAT)).astimezone(timezone.utc)


def _get_teams_from_api():
    teams_endpoint_url = f"{MLB_STATS_API_BASE_URL}v1/teams?sportId=1"
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

        teams_sorted = sorted(teams, key=lambda x: x['name'])
        return jsonify(teams_sorted)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}, 500)
