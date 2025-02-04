import json
import logging
import time

from google.cloud import firestore

from apps.backend.api.highlight_generation.storyboard_generator import build_story_board
from apps.backend.api.mlb_data_fetching.gumbo_processor import fetch_single_game_data, extract_play_by_play, \
    extract_game_overview
from apps.backend.api.mlb_data_fetching.team_schedules_processor import get_current_datetime

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

db = firestore.Client(
    project="slimeify",  # Your Google Cloud project ID
    database="mlb-sluggers"
)


def generate_game_highlights(game_pk_str):
    """Generate highlights for a finalized game with rate limit handling."""
    logger.info(f"Starting highlight generation for game {game_pk_str}")
    try:
        # Fetch game data with detailed logging
        game_data = fetch_single_game_data(game_pk_str)
        logger.info("Successfully fetched game data")

        logger.info("Extracting play-by-play data...")
        play_by_play = extract_play_by_play(game_data)
        logger.info(f"Extracted {len(play_by_play)} plays")
        logger.info("Extracting game overview...")
        game_overview = extract_game_overview(game_data)
        # Build storyboard with rate limit handling
        logger.info("Building storyboard...")
        try:
            storyboard = build_story_board(play_by_play, game_overview, game_pk_str)
            logger.info("Successfully built storyboard")
            # logger.debug("First scene: %s", storyboard.scenes[0] if storyboard.scenes else 'No scenes')
        except Exception as e:
            if "429" in str(e):
                logger.error("Rate limit hit during storyboard generation. Waiting before retry...")
                time.sleep(60)  # Wait 60 seconds before retry
                storyboard = build_story_board(play_by_play, game_overview, game_pk_str)
            else:
                raise

        # Update Firestore with the serialized storyboard
        logger.debug("Updating Firestore...")
        doc_ref = db.collection("highlights").document(game_pk_str)
        doc_ref.update({
            "storyboard": json.dumps(storyboard, indent=4),  # Convert to dict before storing
            "updatedAt": get_current_datetime()
        })
        logger.info("Successfully updated Firestore")

        return storyboard

    except Exception as e:
        logger.error(f"Error generating highlights for game {game_pk_str}: {str(e)}", exc_info=True)
        if "429" in str(e):
            logger.error("Rate limit exceeded. Consider implementing backoff strategy.")
        raise


if __name__ == "__main__":
    logging.info("Starting highlight generation test...")
    try:
        pks = ["775300", "775294", "775298", "775297", "775296"]
        for pk in pks:
            generate_game_highlights(pk)
        logging.info("Highlight generation completed successfully")
        # logging.debug("Generated storyboard: %s", f"{test_storyboard}")
    except Exception as e:
        logging.error("Highlight generation test failed", exc_info=True)
