import google.generativeai as genai
from vertexai.preview.vision_models import ImageGenerationModel

from apps.backend.api.highlight_generation.instructions_garden import provide_imagen_prompt_gen_instructions
from apps.backend.config import GEMINI_API_KEY


class GenerativeModelConfig:

    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)

    story_gen_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        ),
    )

    imagen_prompt_gen_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        ),
        system_instruction=provide_imagen_prompt_gen_instructions()
    )

    imagen3_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")
