def provide_imagen_prompt_gen_instructions() -> str:
    return """
        Your job is to create a concise and visually engaging imagenPrompt for each story and scene optimized 
        for generative AI (Imagen 3) Style: Use a 3D Pixar animated film style for all prompts. Focus on vibrant, 
        engaging visuals with a clear, child-friendly aesthetic. Subject Focus: Focus on a single key subject or action 
        in each scene (e.g., one batter, one pitcher, or a celebration). Avoid overloading scenes with too many actions 
        or characters. Characters: Replace all humans with animal characters, always referring to them as "animals" and 
        never as "creatures." Maintain consistent animal representations for players throughout the JSON object (e.g., 
        if a raccoon represents #99 for the Yankees, this must remain consistent in all scenes). Team and Player Details: 
        always include the appropriate team and jersey or player numbers, and player roles (e.g., batter, pitcher) in the 
        prompts. If relevant, use stylized team logos (e.g., Dodgers, Yankees) as part of the environment or scene. 
        Background and Setting: Include concise descriptions of the setting (e.g., "a baseball stadium" or "a baseball 
        field"). Minimize background elements unless critical to the scene. Visual Simplicity: Avoid cluttered prompts or 
        unnecessary actions. Prioritize clarity and directness to optimize for Imagen 3. Team Animal Pairings: Choose 
        randomly from any of the following pairings when depicting players as animals: Raccoons and Squirrels, 
        Foxes and Rabbits, Bears and Moose, Cats and Dogs. For a given story, depict the away team as one species from 
        the selected pairing and the away team as the other. (ie. home team is animal1 and away team is animal2) 
        Examples: Example 0 (Scene): A professional 3D animated film render, action shot of a Angel stadium with a blue 
        sky overhead. A starting lineup of 3 fox characters dressed as the Toronto Bluejays and a starting lineup of 3 
        rabbit characters dressed as the Los Angeles Angels warm up on the field Example 1 (Scene): 3D rendered pixar 
        animated film style, a medium shot of a baseball field with a fox pitcher with jersey #22 wearing the official 
        Los Angeles Dodgers team uniform Example 2 (Scene): 3D rendered pixar animation style, a close up of a Raccoon 
        with a #99 jersey from the New York Yankees hitting a home run to right-center field. A single baseball is flying 
        off the bat Example 3 (Story): A professional 3D animated film render of a painted cinderblock wall, 
        split in half. On one side, a single stylized Arizona Diamondbacks logo and on the other, a single stylized New 
        York Mets logo. A 3D rendered pixar film style squirrel baseball player with Diamondbacks baseball uniform on and 
        a 3d rendered pixar film style raccoon baseball player wearing an official Mets team uniform are posed on either 
        side, facing each other and ready for a friendly baseball match. Example 4 (Story): 3D rendered pixar animated 
        film style, a wide shot of a baseball field at night with two characters standing on the mound: a fox wearing 
        Chicago Cubs uniforms on one side of the pitcher's mound, and a rabbit wearing Chicago White Sox uniforms on the 
        other. Chicago city skyline in the distance Example 5: (Story): A 3D render of a baseball stadium's wall, 
        split diagonally. On one side, a bright red square displays a large white stylized letter 'B' and on the other, 
        a dark green square with a yellow and green stylized 'A'. A cute 3d pixar style fox character with Athletics 
        baseball uniform on and a cute pixar style rabbit wearing boston red sox uniform are posed on either side of the 
        diagonal. Example 6 (Scene): 3D rendered pixar animation style, a medium shot of a baseball field with a rabbit 
        player wearing #5 for the Colorado Rockies waiting on first base of a baseball diamond, ready to run to the next 
        base. A fox wearing a Seattle Mariners uniform stands next to him as the first base player
    """
