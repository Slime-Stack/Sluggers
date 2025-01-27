from flask import Flask, jsonify, request
import requests
from google.cloud import firestore
from datetime import datetime

# Initialize Firestore client
db = firestore.Client(
    project="slimeify",  # Your Google Cloud project ID
    database="mlb-sluggers"  # Replace with your database name if it's not "(default)"
)
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


# Endpoint to fetch highlights for a specific team
@app.route("/highlights/<int:teamId>", methods=["GET"])
def get_highlights(teamId):
    highlights_ref = db.collection("highlights")
    query = highlights_ref.where("teams", "array_contains", teamId).stream()

    results = []
    for doc in query:
        results.append(doc.to_dict())

    # Sort by date in descending order
    results.sort(key=lambda h: h["gameDate"], reverse=True)

    # Return results or 404 if none found
    if not results:
        return jsonify({"error": "No highlights found for the specified team"}), 404
    return jsonify(results)

# Endpoint to fetch push new game highlights
@app.route("/highlights", methods=["POST"])
def add_highlight():
    try:
        # Parse the incoming JSON payload
        data = request.get_json()

        # Validate required fields
        required_fields = ["gamePk", "teams", "gameDate", "scenes"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Validate 'teams' array
        if not isinstance(data["teams"], list) or len(data["teams"]) != 2:
            return jsonify({"error": "Invalid 'teams' field. Must be an array with exactly two team IDs."}), 400

        # Validate 'scenes' array
        if not isinstance(data["scenes"], list):
            return jsonify({"error": "Invalid 'scenes' field. Must be an array of scenes."}), 400

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
        return jsonify({"error": f"An internal error occurred - Error adding highlight: {e}"}), 500


# Main entry point
if __name__ == "__main__":
    # Run the Flask app on port 8080
    app.run(host="0.0.0.0", port=8080)
