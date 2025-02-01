from dataclasses import dataclass

from typing_extensions import TypedDict

@dataclass
class Scene:
    actNumber: int
    audioUrl_en: str
    audioUrl_es: str
    audioUrl_ja: str
    caption_en: str
    caption_es: str
    caption_ja: str
    description: str
    imageUrl: str
    imagenPrompt: str
    sceneNumber: int
    visualDescription: str
