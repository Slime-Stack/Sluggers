from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# Function to construct the team logo URL
def get_team_logo_url(team_id):
    return f'https://www.mlbstatic.com/team-logos/{team_id}.svg'

# Endpoint to fetch all MLB teams
@app.route("/teams", methods=["GET"])
def get_teams():
    # URL for the MLB API
    teams_endpoint_url = 'https://statsapi.mlb.com/api/v1/teams?sportId=1'

    try:
        # Fetch data from the MLB API
        response = requests.get(teams_endpoint_url)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()

        # Parse and format team data
        teams = []
        for team in data['teams']:
            team_data = {
                'team_id': team['id'],
                'name': team['name'],
                'shortName': team['teamName'],
                'logo_url': get_team_logo_url(team['id'])
            }
            teams.append(team_data)

        # Sort teams alphabetically by name
        teams_sorted = sorted(teams, key=lambda x: x['name'])
        return jsonify(teams_sorted)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Mock data for highlights
highlights = [
    {"teamId": 121, "gameId": 123456, "description": "Dodgers win with a walk-off home run!", "videoUrl": "https://example.com/highlight1.mp4", "date": "2025-01-20"},
    {"teamId": 147, "gameId": 123457, "description": "Yankees dominate with a grand slam!", "videoUrl": "https://example.com/highlight2.mp4", "date": "2025-01-21"},
    {"teamId": 111, "gameId": 123458, "description": "Red Sox rally late for an epic win!", "videoUrl": "https://example.com/highlight3.mp4", "date": "2025-01-22"},
]

# Endpoint to fetch highlights for a specific team
@app.route("/highlights/<int:teamId>", methods=["GET"])
def get_highlights(teamId):
    # Filter highlights by teamId
    team_highlights = [h for h in highlights if h["teamId"] == teamId]

    # Return highlights or a 404 if no highlights exist
    if not team_highlights:
        return jsonify({"error": "No highlights found for the specified team"}), 404
    return jsonify(team_highlights)

# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
