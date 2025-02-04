import logging

from google.cloud import aiplatform, storage

from apps.backend.api.genai.generative_model_config import GenerativeModelConfig
from apps.backend.config import PROJECT_ID, REGION, BUCKET_URI

aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
imagen3_model = GenerativeModelConfig().imagen3_model
storage_client = storage.Client()
bucket_name = BUCKET_URI.replace('gs://', '')
logger = logging.getLogger(__name__)
storage_client_uri_prefix = "https://storage.googleapis.com/"


def generate_image(prompt: str, aspect_ratio):
    """Generate an image using Vertex AI's Imagen model."""
    logger.debug(f"Generating image with prompt: {prompt[:100]}...")  # Log first 100 chars of prompt

    try:
        response = imagen3_model.generate_images(
            prompt=prompt,
            number_of_images=4,
            aspect_ratio=aspect_ratio,
            language="en",
            safety_filter_level="block_some",
            person_generation="dont_allow",
            output_gcs_uri=BUCKET_URI
        )

        if not response or not response.images:
            logger.error("Image generation failed - no images returned")
            return None

        logger.debug("Successfully generated image")
        return response.images[0]

    except Exception as e:
        logger.error(f"Failed to generate image: {str(e)}", exc_info=True)
        return None


def upload_image_to_gcs(prompt: str, game_pk: str, scene_number: int, is_story_image: bool = False) -> str:
    """Generate and upload an image to GCS."""
    try:
        scene_image = generate_image(prompt, "3:4" if not is_story_image else "4:3")

        if not scene_image:
            logger.warning("No image generated, using placeholder")
            return get_placeholder_image_url()

        # image_name = f"/tmp/game_{game_pk}_{'story' if is_story_image else f'scene_{scene_number}'}.png"
        # image_bytes = scene_image.show
        # bucket = storage_client.bucket(bucket_name)
        # blob = bucket.blob(image_name)

        # Convert image to byte stream
        # image_bytes = io.BytesIO()
        # image_bytes.write(scene_image.save(image_name))

        logger.debug("scene_image._gcs_uri is: %s", f"{scene_image._gcs_uri}")

        # scene_image.save(image_name, False)

        # logger.debug("scene_image._gcs_uri is: %s", f"{scene_image._gcs_uri}")
        # logger.debug("scene_image._image_bytes is: %s", f"{scene_image._image_bytes[:300]}")
        # blob_url = upload_blob_from_stream(
        #     bucket_name=bucket_name,
        #     destination_blob_name=image_name,
        #     content=image_bytes
        # )

        # Upload the image
        # blob.upload_from_file(scene_image_file, content_type="image/png")
        scene_image_gcs_url = scene_image._gcs_uri.replace('gs://', '')

        storage_client_url = f"{storage_client_uri_prefix}{scene_image_gcs_url}"
        logger.info("Successfully uploaded image: %s", storage_client_url)
        return storage_client_url

    except Exception as e:
        logger.error(f"Failed to upload image: {str(e)}", exc_info=True)
        return get_placeholder_image_url()


def get_placeholder_image_url() -> str:
    """Return a placeholder image URL when generation fails."""
    return f"{BUCKET_URI}/placeholder_image.png"  # Update with your actual placeholder image


def upload_story_list_image_to_gcs(storyboard, game_pk: str) -> str:
    """Upload the story list image to GCS."""
    try:
        # Get the first scene's prompt for the story image
        if not storyboard or not storyboard.scenes:
            logger.error("No scenes found in storyboard")
            return get_placeholder_image_url()

        first_scene = storyboard.scenes[0]
        return upload_image_to_gcs(
            prompt=first_scene.imagenPrompt,
            game_pk=game_pk,
            scene_number=0,
            is_story_image=True
        )

    except Exception as e:
        logger.error(f"Failed to upload story list image: {str(e)}", exc_info=True)
        return get_placeholder_image_url()
