'''
Created on Jun 4, 2011

@author: anthony
'''

import pygame, dataFiles, sprites, sGroups

BLOCK_SIZE = 4

class Level:
    def __init__ (self, image):
        self.image = pygame.image.load(image)
        self.x = 0
        self.y = 0
        self.WALL = (0, 0, 255, 0)
        
        self.Layout()
    def Layout (self):
        
        x_offset = (BLOCK_SIZE/2)
        y_offset = (BLOCK_SIZE/2)
        
        for y in xrange(self.image.get_height()):
            self.y = y
            for x in xrange(self.image.get_width()):
                    self.x = x
                    """Get the center point for the rects"""
                    color = self.get_at(self.x, self.y)
                    pos = ((self.x*4 + x_offset), (self.y*4 + y_offset))
                    print self.x, self.y, color
                    if color == self.WALL: 
                        wall = sprites.Wall(dataFiles.wallIm, pos)
                        sGroups.staticSprites.add(wall)
                        print sGroups.staticSprites
    
    def get_at(self, dx, dy):
        try:
            return self.image.get_at((dx, dy))
        except:
            pass