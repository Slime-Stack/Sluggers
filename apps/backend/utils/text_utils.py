def combine_captions(storyboard: dict) -> str:
    """Combines all English captions from a storyboard into a single narrative string.

    Args:
        storyboard: A dictionary containing scenes with caption_en fields

    Returns:
        A string combining all English captions with proper spacing and flow
    """
    if not storyboard or 'scenes' not in storyboard:
        return ""

    # Extract all English captions and filter out None/empty values
    captions = [scene.get('caption_en', '') for scene in storyboard['scenes']
                if scene.get('caption_en')]

    # Join the captions with spaces between them
    return ' '.join(captions)
