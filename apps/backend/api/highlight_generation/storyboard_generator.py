import json
import logging
from typing import List

import google.generativeai as genai
import vertexai
from google.cloud import firestore, storage, texttospeech

from apps.backend.api.data_model.scene import Scene
from apps.backend.api.data_model.storyboard import Storyboard
from apps.backend.api.genai.generative_model_config import GenerativeModelConfig
from apps.backend.api.highlight_generation.image_generator import upload_story_list_image_to_gcs, upload_image_to_gcs
from apps.backend.api.highlight_generation.prompt_garden import provide_story_prompt, provide_imagen_model_prompt
from apps.backend.api.highlight_generation.speech_generator import synthesize_highlight_from_ssml
from apps.backend.utils.constants import BUCKET_URI, DATABASE_ID, PROJECT_ID

# Initialize Firestore and Cloud Storage
db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)
storage_client = storage.Client()

# Initialize Text-to-Speech client
tts_client = texttospeech.TextToSpeechClient()

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location="us-central1", staging_bucket=BUCKET_URI)
logger = logging.getLogger(__name__)


def _get_imagen_prompts(base_story_json_str, game_overview):
    storyboard = add_imagen_prompts_to_storyboard(base_story_json_str, game_overview)
    if not storyboard:
        logger.error("Failed to add imagen prompts to storyboard - received bad response")
        raise ValueError("Bad response from imagen prompt generation")
    else:
        logger.debug(f"Added imagen prompts to base storyboard: {base_story_json_str[:200]}...")
        return storyboard


def build_story_board(play_by_play, game_overview, game_pk) -> Storyboard:
    """Combine the output from each model into a storyboard"""

    try:
        logger.info(f"Starting storyboard generation for game {game_pk}")

        # Generate a storyboard json string without Imagen prompts
        base_story_json_str = _generate_base_storyboard(play_by_play)

        # Generate storyboard with imagen prompts from base json str
        logger.debug("Adding imagen prompts to storyboard...")
        storyboard = _get_imagen_prompts(base_story_json_str, game_overview)
        # Generate, upload and set the game list item image
        logger.debug("Generating and uploading story list image...")
        try:
            storyboard.storyImageUrl = upload_story_list_image_to_gcs(storyboard, game_pk)
            logger.info(f"Successfully uploaded story image: {storyboard.storyImageUrl}")
        except Exception as e:
            logger.error(f"Failed to upload story list image: {str(e)}", exc_info=True)
            raise

        # Iterate over all the scenes, generate image and add the url to each Scene in place
        logger.info(f"Processing {len(storyboard.scenes)} scenes...")
        for idx, scene in enumerate(storyboard.scenes, 1):
            logger.debug(f"Processing scene {idx}/{len(storyboard.scenes)}")

            # Generate and upload scene image
            try:
                logger.debug(f"Generating image for scene {scene.sceneNumber}...")
                scene.image_url = add_image_url(scene, game_pk)
                logger.debug(f"Successfully added image URL: {scene.image_url}")
            except Exception as e:
                logger.error(f"Failed to generate/upload image for scene {scene.sceneNumber}: {str(e)}", exc_info=True)
                raise

            # Generate and upload audio for each language
            for lang in ["en", "es", "ja"]:
                try:
                    logger.debug(f"Generating {lang} audio for scene {scene.sceneNumber}...")
                    caption = getattr(scene, f"caption_{lang}")
                    if caption:
                        audio_url = synthesize_highlight_from_ssml(
                            caption=caption,
                            language_code=lang,
                            act_number=scene.actNumber,
                            scene_number=scene.sceneNumber
                        )
                        setattr(scene, f"audioUrl_{lang}", audio_url)
                        logger.debug(f"Successfully added {lang} audio URL: {audio_url}")
                except Exception as e:
                    logger.error(f"Failed to generate {lang} audio for scene {scene.sceneNumber}: {str(e)}",
                                 exc_info=True)
                    raise

            logger.info(f"Completed processing scene {idx}/{len(storyboard.scenes)}")

        logger.info(f"Successfully completed storyboard generation for game {game_pk}")
        return storyboard

    except Exception as e:
        logger.error(f"Error building storyboard for game {game_pk}: {str(e)}", exc_info=True)
        if "429" in str(e):
            logger.error("Rate limit hit during storyboard generation")
        raise


def tell_the_plays_as_a_story(text: List[dict]) -> str:
    """
    Generates a story from play data.

    Args:
       :param text: A list of dictionaries containing play-by-play information.
    Returns:
       str: A string of the story, in json format.
    """
    prompt = provide_story_prompt(text)

    model = GenerativeModelConfig.story_gen_model
    response = model.generate_content(prompt)
    if response and response.text:
        return response.text.strip()
    else:
        print(f"Error with Gemini API: {response.status_code}, {response.text if response else 'No response'}")
        return ""


def add_imagen_prompts_to_storyboard(story: str, overview: str) -> Storyboard:
    """
    Generates imagen prompts for each scene from a given story.

    Args:
        :param story: A string of the story
        :param overview: A string of the overall game information
    Returns:
        str: A JSON string of the storyboard prompts.
    """
    imagen_model_prompt = provide_imagen_model_prompt(story, overview)

    model = GenerativeModelConfig.imagen_prompt_gen_model
    response_incl_imagen = model.generate_content(
        imagen_model_prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        ),
    )
    if response_incl_imagen and response_incl_imagen.text:
        data = json.loads(response_incl_imagen.text)
        return Storyboard(**data)
    else:
        print(
            f"Error with Gemini API: {response_incl_imagen.status_code}, {response_incl_imagen.text if response_incl_imagen else 'No response'}")
        return Storyboard()


def add_image_url(scene: Scene, game_pk) -> str:
    """
        Runs image generation: saves them to gcs and then returns the url to the stored image for each scene from a given story.
        model.generateImage()
        Args:
            :param scene: A Scene data class with the prompt to generate the desired image
            :param game_pk: the game key

        Returns:
            str: A url string of the image's storage location.
        """
    image_url = upload_image_to_gcs(prompt=scene.imagenPrompt, game_pk=game_pk, scene_number=scene.sceneNumber)
    return image_url


def provide_audio_url_for_scene():
    return ""


def _generate_base_storyboard(play_by_play):
    logger.debug("Generating base story from play-by-play data...")
    base_story_json_str = tell_the_plays_as_a_story(play_by_play)
    if not base_story_json_str:
        logger.error("Failed to generate base story - received empty response")
        raise ValueError("Empty response from story generation")
    else:
        logger.debug(f"Generated base story: {base_story_json_str[:200]}...")
        return base_story_json_str
