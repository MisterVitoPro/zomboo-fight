'''
Created on 31.05.2011

@author: Anthony D'Alessandro
'''

import pygame, dataFiles

class LowerHud (pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = pygame.image.load(dataFiles.bottomBarIm)
        self.image = self.imageMaster.convert()
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor)
        self.image = pygame.transform.rotate(self.imageMaster, 180)
        self.rect = self.image.get_rect()
        self.rect.top = 0
        
class healthBar (pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.imageMaster = pygame.image.load(dataFiles.healthBarIm)
        self.image = self.imageMaster.convert()
        pygame.transform.scale(self.imageMaster, (self.player.hp, 16))
        self.rect = self.image.get_rect()
        self.rect.center = (90, 8)
        
    def update (self):
        oldcenter = self.rect.center
        self.image = pygame.transform.scale(self.imageMaster, (self.player.hp, 16))
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter
        