from typing import TypedDict
from apps.backend.api.data_model.scene import Scene


class Storyboard(TypedDict):
    scenes: list[Scene]         # List of scenes within the story
