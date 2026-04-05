"""ZOMBOO - Sprite animation offsets and frame sizes.

Created 2011 by Anthony D'Alessandro.
"""
from types import MappingProxyType


class Animate():
    """Stores directional sprite sheet offsets and frame sizes for character animation."""

    def __init__(self):
        self.info = None

    offsets = MappingProxyType({
        "north": ((0, 0), (24, 0), (51, 0)),
        "northWest": ((0, 35), (26, 35), (51, 35)),
        "west": ((0, 69), (25, 69), (52, 69)),
        "southWest": ((0, 102), (24, 102), (47, 102)),
        "south": ((0, 136), (24, 136), (49, 136), (75, 136)),
    })

    imageSizes = MappingProxyType({
        "north": (24, 32),
        "northWest": (24, 32),
        "west": (26, 32),
        "southWest": (23, 32),
        "south": (24, 32),
    })
