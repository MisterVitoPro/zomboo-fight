'''
Created on May 24, 2011

@author: student
'''


import pygame, dataFiles, sGroups, animate
import random, math

pygame.joystick.init()
pygame.mixer.init()

jCount = pygame.joystick.get_count()
jOn = False
if jCount == 1:
    jOn = True
    j = pygame.joystick.Joystick(0)
    j.init()
if jCount == 2:
    jOn = True
    j = pygame.joystick.Joystick(0)
    j2 = pygame.joystick.Joystick(1)
    j.init()
    j2.init()  


    if j.get_init() == 1: 
        print "Joystick is initialized"

class gameObject(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.image = self.image.convert()
        self.imageC = self.image
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor)
        self.rect = self.image.get_rect()
        self.rect.center = ((800/2), (600/2))
        self.damage = 0
        self.hp = 0
        self.dx = 0
        self.dy = 0
        self.oldx = self.rect.centerx
        self.oldy = self.rect.centery
        self.oldxy = (self.oldx, self.oldy)
        self.oldxy2 = (self.oldxy)
        self.speed = (self.dx, self.dy)
        self.speedX = 0
        self.speedY = 0
        self.state = None
        self.frame = 0
        self.pause = 0
        self.animDelay = 5
        self.moving = False
        
        self.loadImage(image)
        
        self.MOVE_N = 0
        self.MOVE_NE = 1
        self.MOVE_E = 2
        self.MOVE_SE = 3
        self.MOVE_S = 4
        self.MOVE_SW = 5
        self.MOVE_W = 6
        self.MOVE_NW = 7
        
    def update (self):
        self.oldx = self.rect.centerx
        self.oldy = self.rect.centery
        
        if self.rect.top < 0:
            self.speedY = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.right > 800:
            self.speedX = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.bottom > 600:
            self.speedY = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.left < 0:
            self.speedX = 0
            self.rect.center = (self.oldx, self.oldy)
    
    def on_collide(self):
        pass
    
    def loadImage (self, image):
#NORTH MOVEMENT
        self.NORTH = []
        imgSizeN = animate.Animate.imageSizes["north"]
        offsetsN = animate.Animate.offsets["north"]
        
        
        frameCount = len(animate.Animate.offsets["north"])
        for i in range(frameCount):
            tmpImageN = pygame.Surface(imgSizeN)
            tmpImageN.blit (self.imageC, (0,0), (offsetsN[i], imgSizeN))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageN.set_colorkey(transColor)
            self.NORTH.append(tmpImageN)
#NORTH EAST MOVEMENT
        self.NORTHEAST = []
        imgSizeNE = animate.Animate.imageSizes["northWest"]
        offsetsNE = animate.Animate.offsets["northWest"]
        
        
        frameCount = len(animate.Animate.offsets["northWest"])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            tmpImageNE = (pygame.transform.flip(tmpImageNE, 1, 0))
            self.NORTHEAST.append(tmpImageNE)  
#EAST MOVEMENT
        self.EAST = []
        dir = "west"
        imgSizeNE = animate.Animate.imageSizes[dir]
        offsetsNE = animate.Animate.offsets[dir]
        
        frameCount = len(animate.Animate.offsets[dir])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            tmpImageNE = (pygame.transform.flip(tmpImageNE, 1, 0))
            self.EAST.append(tmpImageNE)
#SOUTH EAST MOVEMENT
        self.SOUTHEAST = []
        dir = "southWest"
        imgSizeNE = animate.Animate.imageSizes[dir]
        offsetsNE = animate.Animate.offsets[dir]
        
        frameCount = len(animate.Animate.offsets[dir])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            tmpImageNE = (pygame.transform.flip(tmpImageNE, 1, 0))
            self.SOUTHEAST.append(tmpImageNE)   
#SOUTH MOVEMENT          
        self.SOUTH = []
        imgSizeN = animate.Animate.imageSizes["south"]
        offsetsN = animate.Animate.offsets["south"]
          
        frameCount = len(animate.Animate.offsets["south"])
        for i in range(frameCount):
            tmpImageN = pygame.Surface(imgSizeN)
            tmpImageN.blit (self.imageC, (0,0), (offsetsN[i], imgSizeN))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageN.set_colorkey(transColor)
            self.SOUTH.append(tmpImageN) 
#SOUTH WEST MOVEMENT
        self.SOUTHWEST = []
        dir = "southWest"
        imgSizeNE = animate.Animate.imageSizes[dir]
        offsetsNE = animate.Animate.offsets[dir]
        
        frameCount = len(animate.Animate.offsets[dir])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            self.SOUTHWEST.append(tmpImageNE)
#WEST MOVEMENT
        self.WEST = []
        dir = "west"
        imgSizeNE = animate.Animate.imageSizes[dir]
        offsetsNE = animate.Animate.offsets[dir]
        
        frameCount = len(animate.Animate.offsets[dir])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            self.WEST.append(tmpImageNE)                                                                  
#NORTH WEST MOVEMENT
        self.NORTHWEST = []
        dir = "northWest"
        imgSizeNE = animate.Animate.imageSizes[dir]
        offsetsNE = animate.Animate.offsets[dir]
        
        frameCount = len(animate.Animate.offsets[dir])
        for i in range(frameCount):
            tmpImageNE = pygame.Surface(imgSizeNE)
            tmpImageNE.blit (self.imageC, (0,0), (offsetsNE[i], imgSizeNE))
            transColor = tmpImageN.get_at((1, 1))
            tmpImageNE.set_colorkey(transColor)
            self.NORTHWEST.append(tmpImageNE)            
    
    def animation (self):
        
        if self.moving == True:
            if self.state == self.MOVE_N:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                if self.frame >= len(self.NORTH):
                    self.frame = 0
                    self.state = self.MOVE_N
                else:
                    self.image = self.NORTH[self.frame]
                    
            elif self.state == self.MOVE_E:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                if self.frame >= len(self.EAST):
                    self.frame = 0
                    self.state = self.MOVE_E
                else:
                    self.image = self.EAST[self.frame]
                    
            elif self.state == self.MOVE_W:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                if self.frame >= len(self.WEST):
                    self.frame = 0
                    self.state = self.MOVE_W
                else:
                    self.image = self.WEST[self.frame]        
                    
            elif self.state == self.MOVE_S:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                if self.frame >= len(self.SOUTH):
                    self.frame = 0
                    self.state = self.MOVE_S
                else:
                    self.image = self.SOUTH[self.frame]
        
class Bullet (gameObject):
    def __init__(self, image, pos, dir, damage, bulletLife, bulletStr, gun):
        gameObject.__init__(self, image)
        self.gun = gun
        self.damage = damage
        self.pos = pos
        self.rect.center = self.pos
        self.dir = dir
        self.speed = 10
        self.timer = 0
        self.bulletLife = bulletLife
        self.bulletStr = random.randrange(0, bulletStr)
        self.splatSprites = pygame.sprite.Group()
        self.bulletResist = 0
        
    def update (self, splatSprites, fireSprites):
        self.splatSprites = splatSprites
        self.fireSprites = fireSprites
        self.timer += 1
        self.rect.centerx += self.dir[0] * self.speed
        self.rect.centery += self.dir[1] * self.speed
        
        if self.timer >= self.bulletLife:
            self.die()
            
        collideWall = pygame.sprite.spritecollide (self, sGroups.staticSprites, False)
        for collider in collideWall:
            self.on_collide(collider)
            
    def on_collide (self, collider):
        hit = HitSplat(dataFiles.hitIm, self.rect.center)
        self.splatSprites.add(hit)
        self.bulletStr -= 1
        if self.bulletStr <= 0:
            self.die()
        
        self.bulletStr -= collider.bulletResist
       
        return self.splatSprites
    def die (self):
        self.kill()
        if self.gun == "Bazooka":
            explosion = Explosion(self.damage, self.rect.center)
            self.fireSprites.add(explosion)
        
        
        
class HitSplat (gameObject):
    def __init__ (self, image, pos):
        gameObject.__init__ (self, image)
        self.rect.center = pos
        self.timer = 0
        print "HitSplat Initiated"
        
    def update (self):
        self.timer += 1
        print self.timer
        if self.timer >= 5:
            self.kill()
            
class LaserSight (gameObject):
    def __init__(self, image, player):
        gameObject.__init__(self, image)
        self.player = player
        if jOn == True:
            if self.player.pNum == 1:
                self.j = j
            elif self.player.pNum == 2:
                self.j = j2
        else:
            self.j = "none"
        self.angle = 0
        self.imageMaster = pygame.image.load("../data/Laser_Pointer.tga") 
        self.imageMaster = self.imageMaster.convert() 
        self.image = self.imageMaster
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor) 
        self.rect = self.image.get_rect() 
        self.rect.center = self.player.rect.center 
        self.dir = 0
        
    def update (self):
        self.joyRX = float(self.j.get_axis(4))
        self.joyRY = float(self.j.get_axis(3))
        self.dir = (self.joyRX, self.joyRY)
        self.oldxy = self.rect.center
        self.calcAngle(self.dir)
        self.image = pygame.transform.rotate(self.imageMaster, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = self.oldxy
        self.rect.center = self.player.rect.center
        
    def calcAngle (self, dir):
        dirx = dir[0]
        diry = dir[1]
        
        radians = math.atan2 (diry, dirx)
        self.angle = radians * -180 / math.pi
        self.angle += 270
        
class Explosion (gameObject):
    def __init__ (self, damage, pos):
        image = (dataFiles.explosionIm)
        gameObject.__init__(self, image)
        self.explodeTimer = 0
        self.damage = damage
        self.rect.center = pos
        
    def update (self):
        self.explodeTimer += 1
        if self.explodeTimer >= 5:
            self.kill()
        
    def on_collide(self):
        pass
        
        
                 
            
class Zombie(gameObject):
    def __init__(self, image, pos):
        gameObject.__init__(self, image)
        self.image = self.NORTH[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hp = 60
        self.damage = 25
        self.dx = 0
        self.dy = 0
        self.dxPlayer = 0
        self.dyPlayer = 0
        self.speedX = 2
        self.speedY = 2
        self.delay = 0
        self.timer = 0
        self.pause = 0
        self.dir = "none"
        self.animDelay = 10
    
    def update(self, bulletSprites, fireSprites, player1, player2):       
        self.moving = True
        
        self.oldxy = self.rect.center
        self.timer += 1
        
        if jCount == 2:
# Distance from the player2        
            Dist1 = ((self.rect.centerx - player2.rect.centerx), (self.rect.centery - player2.rect.centery))
            DistRaw1 = ((Dist1[0] * Dist1[0]) + (Dist1[1] * Dist1[1]))
            DistMag1 = math.sqrt(DistRaw1)
            
            Dist2 = ((self.rect.centerx - player1.rect.centerx), (self.rect.centery - player1.rect.centery))
            DistRaw2 = ((Dist2[0] * Dist2[0]) + (Dist2[1] * Dist2[1]))
            DistMag2 = math.sqrt(DistRaw2)
            
            if DistMag1 > DistMag2:
                if self.rect.centerx < player1.oldxy2[0]:
                    self.dx = 1
                elif self.rect.centerx > player1.oldxy2[0]:
                    self.dx = -1
            elif DistMag1 < DistMag2:
                if self.rect.centerx < player2.oldxy2[0]:
                    self.dx = 1
                elif self.rect.centerx > player2.oldxy2[0]:
                    self.dx = -1
            if DistMag1 > DistMag2:
                if self.rect.centery < player1.oldxy2[1]:
                    self.dy = 1
                elif self.rect.centery > player1.oldxy2[1]:
                    self.dy = -1
            elif DistMag1 < DistMag2:
                if self.rect.centery < player2.oldxy2[1]:
                    self.dy = 1
                elif self.rect.centery > player2.oldxy2[1]:
                    self.dy = -1
        else:
# Distance from the player1   
            self.dxplayer = self.rect.centerx - player1.rect.centerx
            self.dyplayer = self.rect.centery - player1.rect.centery
            
            Dist2 = (self.dxplayer, self.dyplayer)
            DistRaw2 = ((Dist2[0] * Dist2[0]) + (Dist2[1] * Dist2[1]))
            DistMag2 = math.sqrt(DistRaw2)
            
            print DistMag2
            
            if self.rect.centery < player1.oldxy2[1]:
                self.dy = 1
            elif self.rect.centery > player1.oldxy2[1]:
                self.dy = -1
            if self.rect.centerx < player1.oldxy2[0]:
                self.dx = 1
            elif self.rect.centerx > player1.oldxy2[0]:
                self.dx = -1
            
#            self.dx = (self.dxplayer/DistMag2)
#            self.dy = (self.dyplayer/DistMag2)
#            dxNeg = self.dx * -1
#            dyNeg = self.dy * -1
            
#            print self.dx, self.dy, "THIS IS THE DX DY"     
#            if self.rect.centerx < player1.oldxy2[0]:
#                self.dx = self.dx
#            elif self.rect.centerx > player1.oldxy2[0]:
#                self.dx = dxNeg
#            if self.rect.centery < player1.oldxy2[1]:
#                self.dy = dyNeg
#            elif self.rect.centery > player1.oldxy2[1]:
#                self.dy = self.dy
            if self.rect.centerx == player1.oldxy2[0] and self.rect.centery != player1.oldxy2[1]:
                self.dx = 0
            elif self.rect.centery == player1.oldxy2[1] and self.rect.centerx != player1.oldxy2[0]:
                self.dy = 0 
            
        if self.rect.top < 0:
            self.dy = 0
            self.rect.centery = self.oldy
        if self.rect.right > 800:
            self.dx = 0
            self.rect.centerx = self.oldx
        if self.rect.bottom > 600:
            self.dy = 0
            self.rect.centery = self.oldy
        if self.rect.left < 0:
            self.dx = 0
            self.rect.centerx = self.oldx
        
        if self.timer >= self.delay:
            self.pause += 1
            self.moveDirX = (self.dx * self.speedX)
            self.moveDirY = (self.dy * self.speedY)
              
            self.rect.centerx += self.moveDirX
            self.rect.centery += self.moveDirY
            
            delay2 = random.randrange(5, 15)
            if self.pause >= delay2:
                self.dx = random.randrange(-1, 2)
                self.dy = random.randrange(-1, 2)
            
            if self.moveDirX > 0 and self.moveDirX > self.moveDirY:
                self.state = self.MOVE_E
            elif self.moveDirX < 0 and self.moveDirX < self.moveDirY:
                self.state = self.MOVE_W
            elif self.moveDirY > 0 and self.moveDirY > self.moveDirX:
                self.state = self.MOVE_S
            elif self.moveDirY < 0 and self.moveDirY < self.moveDirX:
                self.state = self.MOVE_N
#            
#            elif self.moveDirX > 0 and self.moveDirY > 0 and self.moveDirX >= self.moveDirY:
#                self.state = self.MOVE_SE
#            elif self.moveDirX < 0 and self.moveDirY > 0 and self.moveDirX <= self.moveDirY:
#                self.state = self.MOVE_SW
#            elif self.moveDirY < 0 and self.moveDirX > 0 and self.moveDirY >= self.moveDirX:
#                self.state = self.MOVE_NE
#            elif self.moveDirY < 0 and self.moveDirX < 0 and self.moveDirY <= self.moveDirX:
#                self.state = self.MOVE_NW
                
            print self.state
            
            gameObject.animation(self)

            self.timer = 0
                
        collideBul = pygame.sprite.spritecollide(self, bulletSprites, False)
        for collider in collideBul:
            self.on_collide(collider)
            collider.on_collide(collider)
        
        collideEx = pygame.sprite.spritecollide(self, fireSprites, False)
        for collider in collideEx:
            self.on_collide(collider)
          
#    def changeImage (self, facing):
#        if facing == "right":
#            self.image = pygame.image.load(dataFiles.zombieRightIm).convert()
#        elif facing == "left":
#            self.image = pygame.image.load(dataFiles.zombieLeftIm).convert()
#        elif facing == "down":
#            self.image = pygame.image.load(dataFiles.zombieTopIm).convert()
#        elif facing == "up":
#            self.state = self.NORTH
#        self.transColor = self.image.get_at((0, 0))
#        self.image.set_colorkey(self.transColor)
#    
    def on_collide(self, collider):        
        self.hp -= collider.damage
        if self.hp <= 0:
            self.kill()
                              
class BigZombie (Zombie):
    def __init__(self, image, pos):
        Zombie.__init__(self, image, pos)
        self.rect.center = pos
        self.hp = 200
        self.damage = 30
        
    def update (self, bulletSprites, bombSprites, player1, player2):
        Zombie.update(self, bulletSprites, bombSprites, player1, player2)
        
    def changeImage (self, dir):
        pass
                             
class Grenade(gameObject):
    def __init__(self, image, pos, dir, pSpeedX, pSpeedY):
        gameObject.__init__(self, image)
        self.grenade = 1
        self.damage = 100
        self.rect.center = pos
        self.dir = dir
        self.speed = 4.00
        self.speed = float(self.speed)
        self.timer = 0
        self.grenadeCook = 3
        self.speedX = abs(pSpeedX) + self.speed
        self.speedY = abs(pSpeedY) + self.speed
        
    def update (self, fireSprites):
        gameObject.update(self)
        self.fireSprites = fireSprites
        
        self.timer += 1
        
        self.speedX -= 0.1
        if self.speedX <= 0.00:
            self.speedX = 0.00
            
        self.speedY -= 0.1
        if self.speedY <= 0.00:
            self.speedY = 0.00
             
        self.rect.centerx += self.dir[0] * self.speedX
        self.rect.centery += self.dir[1] * self.speedY
        
        if self.timer >= (self.grenadeCook*30):
            self.die()
        
    def die(self):
        self.rect.center = (self.rect.centerx, self.rect.centery)
        self.kill()
        explosion = Explosion(self.damage, self.rect.center)
        self.fireSprites.add(explosion)
        return self.fireSprites

class UI(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.font = pygame.font.SysFont("None", 23)
        self.time = 9
        self.timer = self.time*30
        
    def update(self):
        if self.player.dead == False:
            self.text = "HP:                             STM: %d %s: %d/%d Nades: %d" % (self.player.stamina, self.player.gun, self.player.ammo, self.player.clips, self.player.grenade)
            self.image = self.font.render(self.text, 10, (255, 255, 255))
            self.rect = self.image.get_rect()
            self.rect.left = 5
            if self.player.pNum == 2:
                self.rect.left = 400
        elif self.player.dead == True:
            if self.timer <= 0:
                self.font = pygame.font.SysFont("None", 40)
                self.text = "GAME OVER"
                self.image = self.font.render(self.text, 10, (255, 255, 255))
                self.rect.center = (400, 300)
            else:
                self.rect = self.image.get_rect()
                self.timer -= 1
                self.time = self.timer/30
                self.text = "Continue? %d" % self.time 
                self.image = self.font.render(self.text, 10, (255, 255, 255))
                self.rect = self.image.get_rect()
                self.rect.left = 100
                if self.player.pNum == 2:
                    self.rect.left = 500 
                    
class Turret (gameObject):
    def __init__(self, image, pos):
        gameObject.__init__(self, image)
        self.dir = 0
        self.rect.center = pos
        self.fireTimer = 0
        self.fireSet = 2
        self.damage = 60
        self.angle = 0
        self.timer = 0
        
    def update(self):
        self.fireTimer += 1
        if self.fireTimer == self.fireSet:
            self.fire()
            self.fireTimer = 0
            
        self.timer += 1
        if self.timer >= 300:
            self.kill()
        
        self.joyRX = float(j.get_axis(4))
        self.joyRY = float(j.get_axis(3))    
        self.dir = (self.joyRX, self.joyRY)
        
        self.calcVector(self.dir)
        
        oldCenter = self.rect.center 
#        self.dir += 1
#        if self.dir > 360:
#            self.dir = 0
        self.image = pygame.transform.rotate(self.imageC, self.angle) 
        self.rect = self.image.get_rect() 
        self.rect.center = oldCenter 
        
    def calcVector (self, dir):
        dirx = dir[0]
        diry = dir[1]
        
        radians = math.atan2 (diry, dirx)
        self.angle = radians * -180 / math.pi
        self.angle += 270
        
    def fire (self):
        bullet = Bullet((dataFiles.bulletIm), self.rect.center, self.dir, self.damage, 60, 4, "MP5")
        sGroups.bulletSprites.add(bullet)
        
        return sGroups.bulletSprites
    
class Wall (pygame.sprite.Sprite):
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = pygame.image.load(image)
        self.image = self.imageMaster.convert()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hp = 0
        self.damage = 0
        self.bulletResist = 5