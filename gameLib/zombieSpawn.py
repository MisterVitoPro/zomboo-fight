'''
Created on 27.05.2011

@author: Anthony D'Alessandro
'''

import pygame, random, dataFiles

class zombieSpawner (pygame.sprite.Sprite):
    def __init__ (self, time):
        pygame.sprite.Sprite.__init__(self)
        self.spawn = random.randrange(1, 5)
        self.timer = 0
        self.timerEnd = random.randrange ((10*30), (time*30))
        self.image = pygame.image.load(dataFiles.zombieSpawnIm).convert()
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor)
        self.rect = self.image.get_rect()
        
    def update (self):
        self.timer += 1
        if self.timer >= self.timerEnd:
            self.kill()
            self.timer = 0
            
        
        if self.spawn == 1:
            self.centerRects(40, 30)
        elif self.spawn == 2:
            self.centerRects(760, 560)
        elif self.spawn == 3:
            self.centerRects(30, 560)
        elif self.spawn == 4:
            self.centerRects(760, 40)
            
    def centerRects (self, x, y):
        rangex = (x - 10)
        rangey = (y - 10)
        self.rect.centerx = random.randrange(rangex, x)
        self.rect.centery = random.randrange(rangey, y)
            