"""ZOMBOO - Zombie spawner sprite (corner-based spawn points).

Created 2011 by Anthony D'Alessandro.
"""

import pygame, random, dataFiles

_spawner_image = None


class ZombieSpawner (pygame.sprite.Sprite):
    """Timed spawn-point sprite that marks a corner location for zombie generation."""

    def __init__ (self, time):
        global _spawner_image
        pygame.sprite.Sprite.__init__(self)
        self.spawn = random.randrange(1, 5)
        self.timer = 0
        self.timerEnd = random.randrange((10 * dataFiles.FPS), (time * dataFiles.FPS))
        if _spawner_image is None:
            _spawner_image = pygame.image.load(dataFiles.zombieSpawnIm).convert()
            trans = _spawner_image.get_at((0, 0))
            _spawner_image.set_colorkey(trans)
        self.image = _spawner_image.copy()
        self.rect = self.image.get_rect()

        if self.spawn == 1:
            self.center_rects(40, 30)
        elif self.spawn == 2:
            self.center_rects(760, 560)
        elif self.spawn == 3:
            self.center_rects(30, 560)
        elif self.spawn == 4:
            self.center_rects(760, 40)

    def update (self):
        self.timer += 1
        if self.timer >= self.timerEnd:
            self.kill()
            self.timer = 0
            
    def center_rects (self, x, y):
        rangex = (x - 10)
        rangey = (y - 10)
        self.rect.centerx = random.randrange(rangex, x)
        self.rect.centery = random.randrange(rangey, y)
            