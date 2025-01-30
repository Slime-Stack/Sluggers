import google.generativeai as genai
from typing import List
from apps.backend.api.genai.generative_model_config import GenerativeModelConfig


def tell_the_plays_as_a_story(text: List[dict]) -> str:
    """
    Generates a story from play data.

    Args:
       text (list): A list of dictionaries containing play-by-play information.

    Returns:
       str: A string of the story, in json format.
    """
    prompt = f"""Given this JSON of a completed baseball game: {text}, tell the story of the game in a structured three-act format that is captivating for children. Focus only on information directly relevant to the plays described, without inventing or inferring events not explicitly represented in the data. Assume the reader has a basic knowledge of the game and its rules. Incorporate the following:
        Three-Act Structure:
        Opening Shot (Act 1, Scene 0): establish the story being told
        Act 1 (Setup): Introduce the teams, key players, and the opening moments of the game. Build anticipation for the action to come.
        Act 2 (Conflict): Highlight the tension and turning points in the game, focusing on suspenseful and strategic plays. Show the rise and fall of momentum between the teams.
        Act 3 (Resolution): Conclude with the final dramatic moments of the game, including any climactic plays and the outcome. End with a sense of closure or excitement about the game's conclusion.
        Closing Shot (Act 3 final scene): wrap up the story for the viewer
        Each act should consist of 3-5 scenes depending on the {text} content.
        The final story should be 11-17 scenes with opening and closing shots
        Language Requirements:The story should be provided in English, Spanish, and Japanese. Each scene must include captions and audio URLs for all three languages.
        Output the story in JSON format as an object of scenes following this schema:
        For each scene, include the following:
        actNumber: The act number for a given scene
        sceneNumber: The sequential number of the scene in the entire story.
        description: A brief description of what happens in the scene, emphasizing strategic or tactical elements.
        imageUrl: Empty string as a placeholder
        audioUrl_en: Empty string as a placeholder
        audioUrl_es: Empty string as a placeholder
        audioUrl_ja: Empty string as a placeholder
        caption_en: A chunk of text in english derived from a larger text body called story.
        caption_es: A chunk of text in spanish derived from a larger text body called story.
        caption_ja: A chunk of text in japanese derived from a larger text body called story.
        visualDescription: Brief Visual description of what happens in the scene, considering what a single still image would depict
        imagenPrompt: Empty string as a placeholderUse clear and concise language that is easy for children to understand while incorporating elements like suspense, humor, and excitement to make the story captivating.
        Output in JSON format, ensuring the structure of the JSON object remains consistent with the schema provided, is in valid JSON format, and ensuring that both key and string values use double quotes for all entries."""

    model = GenerativeModelConfig.story_gen_model
    response = model.generate_content(prompt)
    if response and response.text:
        return response.text.strip()
    else:
        print(f"Error with Gemini API: {response.status_code}, {response.text if response else 'No response'}")
        return ""


def generate_storyboard_prompts(story: str) -> str:
    """
    Generates storyboard prompts for each scene from a given story.

    Args:
        story (str): A string of the story

    Returns:
        str: A JSON string of the storyboard prompts.
    """
    prompt = f"""Given the JSON object {story} containing scenes from a baseball game, create an advanced prompt for generative AI using animal characters as the main subject for each scene. No humans should output from the generated prompt and any background people should be replaced with woodland animal characters. Please use any identified MLB teams in the prompt as appropriate. Consider the following in your response:
        - 3D rendered woodland animal characters with a pixar animated kids film style look. Always refer to them as 'woodland animals' and never use the word 'creatures'
        - Visual appeal: Focus on creating a visually engaging and exciting experience.
        - Player-Specific Details: Include accurate details about players' positions, teams, and jersey numbers in the prompts. Do not use player names in the prompts. Ensure consistency in animal representation for specific players across all scenes (e.g., if a player is represented as a lion with jersey number 22, this representation must remain consistent throughout the story).
        For each scene:
        - Use the visualDescription, description and caption_en fields from the JSON object to inform the AI prompt, considering what a single still image of the scene would depict.
        - describe the player's team, position and jersey number accurately without specifying their name.
        - Incorporate relevant environmental details (e.g., stadium, field, crowd reactions) and tactical actions described in the scene.
        -  create prompts that are optimized for generative ai image creation
        - Populate the imagenPrompt field in the corresponding JSON object with the generated prompt. All other fields should remain unedited from the {story} object and populate the values from {story} to their corresponding
        Output the updated JSON object, ensuring the structure of the JSON object remains consistent with the original schema provided, is in JSON format, and ensuring all keys and string values use double quotes."""

    model = GenerativeModelConfig.imagen_prompt_gen_model
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        ),
    )
    if response and response.text:
        return response.text.strip()
    else:
        print(f"Error with Gemini API: {response.status_code}, {response.text if response else 'No response'}")
        return story
