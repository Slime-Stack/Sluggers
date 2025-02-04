import requests

from apps.backend.utils.constants import MLB_STATS_API_BASE_URL

MIDDLE_URL_SEGMENT = "v1.1/game/"
GAME_FEED_ENDPOINT = "/feed/live"

def fetch_single_game_data(game_pk):
    url = _game_url_builder(game_pk)
    response = requests.get(url)
    return response.json()

# Extract play-by-play details
def extract_play_by_play(game_data):
    plays = game_data["liveData"]["plays"]["allPlays"]
    play_details = []
    for play in plays:
        result = play["result"]
        about = play["about"]
        match_up = play["matchup"]
        play_info = {
            "description": result["description"],
            "inning": about["inning"],
            "half": "Top" if about["isTopInning"] else "Bottom",
            "event": result["event"],
            "away_score": result["awayScore"],
            "home_score": result["homeScore"],
            "batter": match_up["batter"]["fullName"],
            "pitcher": match_up["pitcher"]["fullName"],
            "captivating_index": about["captivatingIndex"]
        }
        play_details.append(play_info)
    return play_details

# Extract game overview
def extract_game_overview(data):
    game_info = data["gameData"]
    overview = {
        "away_team": game_info["teams"]["away"]["name"],
        "home_team": game_info["teams"]["home"]["name"],
        "venue": game_info["venue"]["name"],
        "date": game_info["datetime"]["officialDate"],
        "attendance": game_info["gameInfo"].get("attendance", "Unknown"),
        "duration_minutes": game_info["gameInfo"].get("gameDurationMinutes", "Unknown"),
        "weather": game_info["weather"],
    }
    return overview

def _game_url_builder(game_pk):
    return f"{MLB_STATS_API_BASE_URL}{MIDDLE_URL_SEGMENT}{game_pk}{GAME_FEED_ENDPOINT}"
