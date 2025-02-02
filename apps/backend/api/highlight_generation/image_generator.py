import logging

from google.cloud import aiplatform, storage
from vertexai.vision_models import Image, ImageGenerationModel

from apps.backend.config import PROJECT_ID, REGION, BUCKET_URI

aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
imagen3_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
storage_client = storage.Client()
bucket_name = BUCKET_URI.replace('gs://', '')
logger = logging.getLogger(__name__)

def generate_image(prompt: str, aspect_ratio) -> Image:
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
            
        bucket = storage_client.bucket(bucket_name)
        image_name = f"game_{game_pk}_{'story' if is_story_image else f'scene_{scene_number}'}.png"
        blob = bucket.blob(image_name)

        # Convert image to byte stream
        image_bytes = io.BytesIO()
        scene_image.save(image_bytes, format="PNG")  # Explicitly save as PNG
        image_bytes.seek(0)  # Ensure the file pointer is at the start

        # Upload the image
        blob.upload_from_file(image_bytes, content_type="image/png")

    logger.info(f"Successfully uploaded image: {image_name}")
        return f"gs://{bucket_name}/{image_name}"
        
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
        return upload_image_to_gcs(prompt=first_scene.imagenPrompt, game_pk=game_pk, scene_number=0,
                                   is_story_image=True)
        
    except Exception as e:
        logger.error(f"Failed to upload story list image: {str(e)}", exc_info=True)
        return get_placeholder_image_url()
