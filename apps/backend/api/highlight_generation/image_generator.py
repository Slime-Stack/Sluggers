from google.cloud import aiplatform

from apps.backend.api.genai.generative_model_config import GenerativeModelConfig
from apps.backend.config import PROJECT_ID, REGION, BUCKET_URI

class ImageGenerator:
    """
    A class to generate images using the Imagen model.
    """

    def __init__(self):
        aiplatform.init(project=PROJECT_ID, location=REGION, staging_bucket=BUCKET_URI)
        self.model = GenerativeModelConfig().imagen3_model

    def generate_image_from_prompt(self, prompt: str):
        """
        Generates an image from a given text prompt.

        Args:
            prompt (str): The text prompt used to generate an image.

        Returns:
           Image: A generated Image object.
        """
        response = self.model.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="block_few",
            person_generation="allow_adult",
        )
        if response and response.images:
            return response.images[0]
        else:
            print("Error with Image Generation API, no image returned.")
            return None
