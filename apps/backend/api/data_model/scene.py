from pydantic.dataclasses import dataclass

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
