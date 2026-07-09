"""Shanhai Spirit - 基于计算机视觉的实时体感交互艺术作品。

《山海灵识》是一款以中国上古神话《山海经》为文化载体的实时体感交互艺术装置。
"""

__version__ = "1.0.0"
__author__ = "ShanhaiSpirit Team"
__all__ = [
    "CreatureManager",
    "CreatureRenderer",
    "CombinedTracker",
    "FaceTracker",
    "HandTracker",
]

from .creature import CreatureManager, CreatureRenderer
from .tracker import CombinedTracker, FaceTracker, HandTracker
