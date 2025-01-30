from typing import TypedDict, Optional


class Scene(TypedDict):
    actNumber: int                     # The act number of the scene
    sceneNumber: int                   # The scene number within the act
    description: str                   # A description of the scene
    imageUrl: Optional[str]            # URL to the scene's image (if available)
    audioUrl_en: Optional[str]         # URL to the English audio file (if available)
    audioUrl_es: Optional[str]         # URL to the Spanish audio file (if available)
    audioUrl_ja: Optional[str]         # URL to the Japanese audio file (if available)
    caption_en: Optional[str]          # English caption text for the scene
    caption_es: Optional[str]          # Spanish caption text for the scene
    caption_ja: Optional[str]          # Japanese caption text for the scene
    visualDescription: Optional[str]   # Brief text description of the scene
    imagenPrompt: Optional[str]        # Description used to generate an image (e.g., for AI rendering)
