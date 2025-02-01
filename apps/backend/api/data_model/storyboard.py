from typing import List, Optional

from pydantic.dataclasses import dataclass

from apps.backend.api.data_model.scene import Scene


@dataclass
class Storyboard:
    storyImageUrl: str = ""
    storyImagenPrompt: str = ""
    storyTitle: str = ""
    teaserSummary: str = ""
    scenes: Optional[List[Scene]] = None
