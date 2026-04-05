"""ZOMBOO - HUD elements (health bar, lower bar).

Created 2011 by Anthony D'Alessandro.
"""

import pygame, dataFiles

_hud_image = None
_healthbar_master = None


class LowerHud (pygame.sprite.Sprite):
    """Bottom bar overlay sprite displayed at the top of the screen."""

    def __init__(self):
        global _hud_image
        pygame.sprite.Sprite.__init__(self)
        if _hud_image is None:
            master = pygame.image.load(dataFiles.bottomBarIm).convert()
            trans = master.get_at((0, 0))
            master.set_colorkey(trans)
            _hud_image = pygame.transform.rotate(master, 180)
        self.image = _hud_image
        self.rect = self.image.get_rect()
        self.rect.top = 0


class HealthBar (pygame.sprite.Sprite):
    """Dynamically scaled sprite that displays the player's current health."""

    def __init__(self, player):
        global _healthbar_master
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        if _healthbar_master is None:
            _healthbar_master = pygame.image.load(dataFiles.healthBarIm).convert()
        self.imageMaster = _healthbar_master
        self.image = pygame.transform.scale(self.imageMaster, (self.player.hp, 16))
        self.rect = self.image.get_rect()
        self.rect.center = (90, 8)
        self._prev_width = self.player.hp

    def update (self):
        width = max(self.player.hp, 1)
        if width != getattr(self, '_prev_width', None):
            self._prev_width = width
            oldcenter = self.rect.center
            self.image = pygame.transform.scale(self.imageMaster, (width, 16))
            self.rect = self.image.get_rect()
            self.rect.center = oldcenter
        