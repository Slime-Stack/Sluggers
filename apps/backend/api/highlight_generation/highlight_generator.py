import json

from google.cloud import firestore

from apps.backend.api.highlight_generation.image_generator import ImageGenerator
from apps.backend.api.highlight_generation.speech_generator import SpeechGenerator
from apps.backend.api.highlight_generation.storyboard_generator import tell_the_plays_as_a_story, \
    generate_storyboard_prompts
from apps.backend.api.mlb_data_fetching.gumbo_processor import fetch_single_game_data, extract_play_by_play, \
    extract_game_overview
from apps.backend.api.mlb_data_fetching.team_schedules_processor import get_current_datetime
from apps.backend.utils.constants import BUCKET_URI, PROJECT_ID, DATABASE_ID

db = firestore.Client(
    project = PROJECT_ID,  # Your Google Cloud project ID
    database = DATABASE_ID
)

def generate_game_highlights(game_pk_str):
    """Generate highlights for a finalized game."""
    try:
        # Fetch detailed game data
        game_data = fetch_single_game_data(game_pk_str)
        play_by_play = extract_play_by_play(game_data)
        game_overview = extract_game_overview(game_data)

        # Generate story and prompts
        # tell_the_plays_as_a_story returns a JSON string
        story_json_str = tell_the_plays_as_a_story(play_by_play)
        if not story_json_str:
            raise Exception("Failed to generate story from play data")

        # generate_storyboard_prompts expects and returns a JSON string
        storyboard_json_str = generate_storyboard_prompts(story_json_str)
        if not storyboard_json_str:
            raise Exception("Failed to generate storyboard prompts")

        # Parse the JSON string into a Python dict
        try:
            storyboard = json.loads(storyboard_json_str)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse storyboard JSON: {e}")

        # Initialize generators
        image_gen = ImageGenerator()
        speech_gen = SpeechGenerator()

        # Process each scene
        processed_scenes = []
        for scene in storyboard.get('scenes', []):
            # Generate image
            if scene.get('imagenPrompt'):
                image = image_gen.generate_image_from_prompt(scene['imagenPrompt'])
                if image:
                    scene['imageUrl'] = image.url

            # Generate audio for each language
            for lang in ['en', 'es', 'ja']:
                caption_key = f'caption_{lang}'
                audio_key = f'audioUrl_{lang}'
                if scene.get(caption_key):
                    speech_gen.scene_id = f"{game_pk_str}_{scene['sceneNumber']}_{lang}"
                    speech_gen.build_output_file_name(speech_gen.scene_id)  # Initialize the output filename
                    speech_gen.synthesize_highlight_from_ssml(scene[caption_key])
                    scene[audio_key] = f"{BUCKET_URI}/{speech_gen.OUTPUT_FILE_NAME}"

            processed_scenes.append(scene)

        # Update Firestore with processed storyboard
        print(f"this is the first processed scene {processed_scenes[0]}")
        doc_ref = db.collection("highlights").document(game_pk_str)
        doc_ref.update({
            "storyboard": processed_scenes,
            "gameOverview": game_overview,
            "updatedAt": get_current_datetime()
        })

        print(f"Successfully generated highlights for game {game_pk_str}")
        return processed_scenes

    except Exception as e:
        print(f"Error generating highlights for game {game_pk_str}: {e}")
        # You might want to add error handling or retry logic here