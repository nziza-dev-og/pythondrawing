from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class AnimationConfig:
    duration: float
    delay: float
    effects: List[str]

@dataclass
class ImageData:
    file_path: str
    position: Tuple[int, int]
    size: Tuple[int, int]