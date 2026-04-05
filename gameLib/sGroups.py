"""ZOMBOO - Sprite group containers.

Created 2011 by Anthony D'Alessandro.
"""

import pygame


class SpriteGroups:
    """Central container for all sprite groups used in the game."""

    GROUP_NAMES = (
        "turretSprites", "UISprites", "UIBarSprites", "textSprites",
        "allySprites", "zombieSprites", "bulletSprites", "bombSprites",
        "fireSprites", "splatSprites", "laserSprites", "powerupSprites",
        "staticSprites",
    )

    def __init__(self):
        for name in self.GROUP_NAMES:
            setattr(self, name, pygame.sprite.Group())

    def empty_all(self):
        for name in self.GROUP_NAMES:
            getattr(self, name).empty()


_instance = SpriteGroups()

turretSprites = _instance.turretSprites
UISprites = _instance.UISprites
UIBarSprites = _instance.UIBarSprites
textSprites = _instance.textSprites
allySprites = _instance.allySprites
zombieSprites = _instance.zombieSprites
bulletSprites = _instance.bulletSprites
bombSprites = _instance.bombSprites
fireSprites = _instance.fireSprites
splatSprites = _instance.splatSprites
laserSprites = _instance.laserSprites
powerupSprites = _instance.powerupSprites
staticSprites = _instance.staticSprites

empty_all = _instance.empty_all
