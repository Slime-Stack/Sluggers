from datetime import datetime, timedelta, timezone

import requests
from flask import jsonify
from google.cloud import firestore

from apps.backend.utils.constants import ISO_FORMAT, MLB_SCHEDULE_API_BASE_URL, MLB_LOGOS_URL, MLB_STATS_API_BASE_URL
from apps.backend.utils.pubsub_utils import publish_game_status_event, trigger_ai_processing

db = firestore.Client(
    project = "slimeify",  # Your Google Cloud project ID
    database = "mlb-sluggers"
)

# Function to process past finalized games
# def process_past_games(season, date, team_id=None):
#     """Processes finalized past games, filtered by required date and optional team."""
#     try:
#         data = _fetch_schedule(season, date, team_id)
#         if not data or "dates" not in data:
#             print(f"No data fetched for season {season}, date {date}, team {team_id}.")
#             return []
#
#         highlights = []
#         for date_entry in data["dates"]:
#             for game in date_entry["games"]:
#                 game_status = game["status"].get("abstractGameState")
#                 game_pk_str = str(game["gamePk"])  # Convert gamePk to string
#
#                 if game_status == "Final":
#                     highlight = {
#                         "gamePk": game_pk_str,
#                         "gameDate": game["gameDate"],
#                         "homeTeam": {
#                             "team_id": game["teams"]["home"]["team"]["id"],
#                             "name": game["teams"]["home"]["team"]["name"],
#                             "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),
#                             "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
#                         },
#                         "awayTeam": {
#                             "team_id": game["teams"]["away"]["team"]["id"],
#                             "name": game["teams"]["away"]["team"]["name"],
#                             "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),
#                             "logo_url": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
#                         },
#                         "status": game["status"]["detailedState"],
#                         "updatedAt": datetime.utcnow().replace(tzinfo=timezone.utc),
#                         "createdAt": datetime.utcnow().replace(tzinfo=timezone.utc),
#                     }
#
#                     # Save to Firestore (if gamePk already exists, only update status)
#                     doc_ref = db.collection("highlights").document(game_pk_str)
#                     if doc_ref.get().exists:
#                         doc_ref.update({"status": "Final"})
#                     else:
#                         doc_ref.set(highlight)
#
#                     highlights.append(highlight)
#
#         print(f"Processed {len(highlights)} highlights for season {season}, date {date}, team {team_id}.")
#         return highlights
#
#     except Exception as e:
#         print(f"Error processing past games: {e}")
#         return []

def process_past_games(season, team_id, date):
    """Processes finalized past games, updates status in Firestore, and triggers AI processing."""
    try:
        data = _fetch_schedule(season, team_id, date)
        if not data or "dates" not in data:
            print(f"No data fetched for season {season}, date {date}, team {team_id}.")
            return []

        current_date = get_current_datetime()
        highlights = []

        _loop_over_game_dates(data, current_date, highlights)

        print(f"Processed {len(highlights)} finalized highlights for team {team_id}.")
        return highlights

    except Exception as e:
        print(f"Error processing past games: {e}")
        return []

# Checks for upcoming games & sends pubsub message
def check_next_game(season, team_id, date):
    """Finds the next upcoming game within the next 7 days and stores it in the 'highlights' collection."""
    try:
        data = _fetch_schedule(season,team_id, date)
        if not data or "dates" not in data:
            print(f"No schedule data found for team {team_id}, season {season}.")
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
                            "homeTeam": {
                                "teamId": game["teams"]["home"]["team"]["id"],
                                "name": game["teams"]["home"]["team"]["name"],
                                "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),
                                "logoUrl": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
                            },
                            "awayTeam": {
                                "teamId": game["teams"]["away"]["team"]["id"],
                                "name": game["teams"]["away"]["team"]["name"],
                                "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),
                                "logoUrl": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
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
        print(f"Updated game {game_pk_str} to Final in Firestore.")
        trigger_ai_processing(game_pk_str)
    else:
        print(f"Game {game_pk_str} already marked Final, skipping update.")

def _create_new_game(doc_ref, game, game_pk_str, current_date):
    """Create a new game record in Firestore."""
    game_date = get_game_datetime(game)
    highlight = _create_new_highlight_record(game_pk_str, game_date, game, current_date)
    doc_ref.set(highlight)
    print(f"Inserted new game {game_pk_str} in Firestore.")
    trigger_ai_processing(game_pk_str)

def _create_new_highlight_record(game_pk_str=None, game_date=None, game=None, current_date=None):
    return {
        "gamePk": game_pk_str,
        "gameDate": game_date,
        "homeTeam": {
            "teamId": game["teams"]["home"]["team"]["id"],
            "name": game["teams"]["home"]["team"]["name"],
            "shortName": game["teams"]["home"]["team"].get("abbreviation", ""),
            "logoUrl": f"https://www.mlbstatic.com/team-logos/{game['teams']['home']['team']['id']}.svg"
        },
        "awayTeam": {
            "teamId": game["teams"]["away"]["team"]["id"],
            "name": game["teams"]["away"]["team"]["name"],
            "shortName": game["teams"]["away"]["team"].get("abbreviation", ""),
            "logoUrl": f"https://www.mlbstatic.com/team-logos/{game['teams']['away']['team']['id']}.svg"
        },
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
        print(f"Error fetching schedule: {response.text}")
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

        teams_sorted = sorted(teams, key = lambda x: x['name'])
        return jsonify(teams_sorted)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}, 500)

# def _generate_game_highlights(game_pk_str):
#     """Generate highlights for a finalized game."""
#     try:
#         # Fetch detailed game data
#         game_data = fetch_single_game_data(game_pk_str)
#         play_by_play = extract_play_by_play(game_data)
#         game_overview = extract_game_overview(game_data)
#
#         # Generate story and prompts
#         # tell_the_plays_as_a_story returns a JSON string
#         story_json_str = tell_the_plays_as_a_story(play_by_play)
#         if not story_json_str:
#             raise Exception("Failed to generate story from play data")
#
#         # generate_storyboard_prompts expects and returns a JSON string
#         storyboard_json_str = generate_storyboard_prompts(story_json_str)
#         if not storyboard_json_str:
#             raise Exception("Failed to generate storyboard prompts")
#
#         # Parse the JSON string into a Python dict
#         try:
#             storyboard = json.loads(storyboard_json_str)
#         except json.JSONDecodeError as e:
#             raise Exception(f"Failed to parse storyboard JSON: {e}")
#
#         # Initialize generators
#         image_gen = ImageGenerator()
#         speech_gen = SpeechGenerator()
#
#         # Process each scene
#         processed_scenes = []
#         for scene in storyboard.get('scenes', []):
#             # Generate image
#             if scene.get('imagenPrompt'):
#                 image = image_gen.generate_image_from_prompt(scene['imagenPrompt'])
#                 if image:
#                     scene['imageUrl'] = image.url
#
#             # Generate audio for each language
#             for lang in ['en', 'es', 'ja']:
#                 caption_key = f'caption_{lang}'
#                 audio_key = f'audioUrl_{lang}'
#                 if scene.get(caption_key):
#                     speech_gen.scene_id = f"{game_pk_str}_{scene['sceneNumber']}_{lang}"
#                     speech_gen.build_output_file_name(speech_gen.scene_id)  # Initialize the output filename
#                     speech_gen.synthesize_highlight_from_ssml(scene[caption_key])
#                     scene[audio_key] = f"{BUCKET_URI}/{speech_gen.OUTPUT_FILE_NAME}"
#
#             processed_scenes.append(scene)
#
#         # Update Firestore with processed storyboard
#         print(f"this is the first processed scene {processed_scenes[0]}")
#         doc_ref = db.collection("highlights").document(game_pk_str)
#         doc_ref.update({
#             "storyboard": processed_scenes,
#             "gameOverview": game_overview,
#             "updatedAt": get_current_datetime()
#         })
#
#         print(f"Successfully generated highlights for game {game_pk_str}")
#
#     except Exception as e:
#         print(f"Error generating highlights for game {game_pk_str}: {e}")
#         # You might want to add error handling or retry logic here
