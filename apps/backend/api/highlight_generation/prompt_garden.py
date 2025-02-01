def provide_story_prompt(text) -> str:
    return f"""
        Given this JSON of a completed baseball game {text}, tell the story of the game 
        in a structured three-act format that is captivating for children. Focus only on information directly relevant to 
        the plays described, without inventing or inferring events not explicitly represented in the data. Assume the 
        reader has a basic knowledge of the game and its rules. Incorporate the following: Three-Act Structure: Opening 
        Shot (Act 1, Scene 0): establish the story being told Act 1 (Setup): Introduce the teams, key players, 
        and the opening moments of the game. Build anticipation for the action to come. Act 2 (Conflict): Highlight the 
        tension and turning points in the game, focusing on suspenseful and strategic plays. Show the rise and fall of 
        momentum between the teams. Act 3 (Resolution): Conclude with the final dramatic moments of the game, 
        including any climactic plays and the outcome. End with a sense of closure or excitement about the game's 
        conclusion. Closing Shot (Act 3 final scene): wrap up the story for the viewer Each act should consist of 3-5 
        scenes depending on the {text}
        The final story should be 11-17 scenes with opening and closing shots
        Language Requirements:The story should be provided in English, Spanish, and Japanese. Each scene must include captions and audio URLs for all three languages.
        Output the story in JSON format as an object of scenes following this schema:
        Storyboard:
        storyTitle: A child-friendly title introducing the game.
        teaserSummary: A short, engaging preview of the game story and matchup.
        storyImageUrl: Empty string as a placeholder
        storyImagenPrompt: Empty string as a placeholder
        for each scene, include the following:
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
        Output in JSON format, ensuring the structure of the JSON object remains consistent with the schema provided, is in valid JSON format, and ensuring that both key and string values use double quotes for all entries.
    """


def provide_imagen_model_prompt(story, game_overview) -> str:
    return f"""
        Given the JSON object {story} containing scenes from a baseball game and its game overview {game_overview}, 
        create a concise and visually engaging imagenPrompt for each scene optimized for generative AI (Imagen 3). 
        Formatting Instructions: Use the visualDescription field as the primary inspiration for the imagenPrompt. Use 
        the description and caption_en fields to inform to team details, jersey numbers, and key visual elements. 
        Replace only the storyImagenPrompt and imagenPrompt fields in the JSON object while ensuring all other fields 
        remain unedited. Ensure the final output is in JSON format with the exact structure provided. Context 
        Instructions: For each scene: Create a concise, vivid description of the visual focus. Ensure that 
        imagenPrompt aligns with the style and structure described above. For the overall storyImage, 
        create a stylized and visually engaging prompt representing game matchup utilizing the teams logos and 
        selected animal pairing. Output the updated JSON object with all keys and string values using double quotes.
"""
