'''
Created on 26.05.2011

@author: Anthony D'Alessandro
'''
import pygame, sprites, math, sGroups, animate
import dataFiles


class Player (sprites.gameObject):
    def __init__(self, image, pNum):
        sprites.gameObject.__init__(self, image)
        self.pNum = pNum
        if sprites.jOn == True:
            if pNum == 1:
                self.j = sprites.j
            elif pNum == 2:
                self.j = sprites.j2
                self.rect.center = (400, 320)
        self.image = self.WEST[0]
        self.rect = self.image.get_rect()  
        self.rect.center = (400, 300)      
        self.dead = False
        self.hp = 100
        self.stamina = 100
        self.staminaLow = 0
        self.grenade = 10
        self.dx = 5
        self.dy = 5
        self.speedX = 0
        self.speedY = 0
        self.sprintSpeed = 0
        self.dir = (0, 0)
        self.facing = "none"
        self.fireTimer = 0
        self.emptySnd = pygame.mixer.Sound(dataFiles.emptySnd)
        self.reloadSnd = pygame.mixer.Sound(dataFiles.reloadSnd)
        self.godMode = False
        self.timerGodmode = 0
        self.timerHP = 0
        self.timerPos = 0
        self.gTimer = 0
        self.staminaTimer = 0
        self.staminaTimerUp = 0
        self.fireStateTimer = 0
        self.gTime = 15
        self.reloadTime = 0
        self.pistol()
        self.reloading = False
        self.fireState = False
        self.collideX = False
        self.collideY = False
        
        
    def pistol (self):
        self.gun = "Pistol"
        self.damage = 20
        self.reloadSpeed = 15
        self.ammo = 9
        self.clips = 8
        self.fireSnd = pygame.mixer.Sound(dataFiles.fireSnd)
        self.automatic = False
        self.fireRate = 10
        self.bulletLife = 45
        self.bulletStr = 2
    
    def update (self, zombieSprites, powerupSprites, bombSprites):
        
        
        self.collideX = False
        self.collideY = False
        
        self.fireTimer += 1

        self.gTimer += 1
            
        if self.fireState == True:
            self.fireStateTimer += 1
            if self.fireStateTimer >= 5:
                self.fireState = False
                self.fireStateTimer = 0
            
        if self.ammo <= 0:
            self.ammo = 0
            
        if self.gun != "Pistol":
            if self.ammo <= 0:
                if self.clips <= 0:
                    self.pistol()
                    
        self.bulletSprites = sGroups.bulletSprites
        self.bombSprites = bombSprites
        self.oldx = self.rect.centerx
        self.oldy = self.rect.centery
        self.oldxy = (self.oldx, self.oldy)
        self.timerPos += 1
        if self.timerPos >= 180:
            self.oldxy2 = self.oldxy
        
        if sprites.jOn == True:
            self.joyX = int(self.j.get_axis(0)*(self.dx- self.staminaLow))
            self.joyY = int(self.j.get_axis(1)*(self.dy- self.staminaLow))
            self.joyRX = float(self.j.get_axis(4))
            self.joyRY = float(self.j.get_axis(3))
            self.trigR = float(self.j.get_axis(2))
                
            if pygame.JOYAXISMOTION:
                self.moving = True
                if self.joyX < 0.1 and self.joyX > -0.1:
                    self.joyX = 0
                if self.joyY < 0.1 and self.joyY > -0.1:
                    self.joyY = 0
                self.speedX = self.joyX
                self.speedY = self.joyY
                
                if self.joyRX > 0 and self.joyRX > self.joyRY:
                    self.state = self.MOVE_E
                elif self.joyRX < 0 and self.joyRX < self.joyRY:
                    self.state = self.MOVE_W
                elif self.joyRY > 0 and self.joyRY > self.joyRX:
                    self.state = self.MOVE_S
                elif self.joyRY < 0 and self.joyRY < self.joyRX:
                    self.state = self.MOVE_N
                
                
                if self.trigR <= -0.7:
                    if self.fireTimer >= self.fireRate:
                            if self.reloading == False:
                                if self.ammo > 0:
                                    self.fire(self.dir)
                                    self.fireTimer = 0
                                    if self.automatic == True:
                                        self.fireTimer = 0
                                elif self.ammo <= 0:
                                    self.fireSnd.stop()
                                    self.emptySnd.play()
                                    self.preReload()
                                    
            sprites.gameObject.animation(self)
            
            if pygame.JOYBUTTONDOWN:
                self.dir = (self.joyRX, self.joyRY)
                if self.j.get_button(5):
                    if self.grenade > 0:
                        if self.gTimer >= self.gTime:
                            self.throwGrenade(self.dir)
                            self.gTimer = 0
                elif self.j.get_button(4):
                    if self.reloading == False:
                        if self.trigR > -.01:
                            if self.gun == "Pistol":
                                if self.ammo < 9:
                                    if self.clips > 0:
                                        self.preReload()
                            elif self.gun == "Shotgun":
                                if self.ammo < 5:
                                    if self.clips > 0:
                                        self.preReload()
                            elif self.gun == "MP5":
                                if self.ammo < 32:
                                    if self.clips > 0:
                                        self.preReload()
                            elif self.gun == "Flamethrower":
                                if self.ammo < 300:
                                    if self.clips > 0:
                                        self.preReload()
                            elif self.gun == "Bazooka":
                                if self.ammo < 1:
                                    if self.clips > 0:
                                        self.preReload()      
            
#Stamina effects    
        self.staminaChange(1)
#Sprinting
        if sprites.jOn == True:        
            if self.trigR > 0:
                if self.stamina > 0:
                    self.sprintSpeed = abs(self.trigR * 2)
                    self.animDelay = 2
                    self.staminaChange(0)
            elif self.trigR <= 0:
                self.sprintSpeed = 1
                self.animDelay = 5
            
        if self.stamina > 100:
            self.stamina -= 1
        if self.stamina <= 0:
            self.stamina = 0
            
        if self.stamina <= 15:
            self.staminaLow = 1
        elif self.stamina > 15:
            self.staminaLow = 0
        
        if self.staminaLow == 1:
            self.animDelay = 8
        else:
            self.animDelay = 5

#Moving the Player
        if self.moving == True:                    
            self.rect.centerx = self.rect.centerx + self.speedX * self.sprintSpeed
            self.rect.centery = self.rect.centery + self.speedY * self.sprintSpeed
       
        """ FIRING GUN AND RELOADING USING KEYBOARD """
        self.keys = pygame.key.get_pressed()
        if self.keys:
            self.movement()
        if self.keys[pygame.K_SPACE] == True:
            if self.fireTimer >= self.fireRate:
                if self.ammo > 0:
                    self.fire(self.dir)
                    self.fireTimer = 0
        elif self.keys[pygame.K_t] == True:
            if self.gun == "Pistol":
                if self.ammo < 9:
                    if self.clips > 0:
                        self.preReload()
                elif self.gun == "Shotgun":
                    if self.ammo < 5:
                        if self.clips > 0:
                            self.preReload()
                elif self.gun == "Flamethrower":
                    if self.ammo < 300:
                        if self.clips > 0:
                            self.preReload()
                elif self.gun == "Bazooka":
                    if self.ammo < 1:
                        if self.clips > 0:
                            self.preReload()
        
        """ REALODING TIMER """                   
        if self.reloading == True:
            self.reloadTime += 1
            print self.reloadTime
            if self.reloadTime >= self.reloadSpeed:
                self.reload(self.gun)
                
        
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
            
        if self.godMode == True:
                self.timerGodmode += 1
                if self.timerGodmode >= 15:
                    self.godMode = False
                    self.timerGodmode = 0
                    
        if self.hp > 100:
            self.timerHP += 1
            if self.timerHP >= 10:
                self.hp -= 1
                self.timerHP = 0
        if self.hp > 150:
            self.hp = 150
            
        collideZom = pygame.sprite.spritecollide(self, zombieSprites, False)
        for collider in collideZom:
            print "COLLIDED"
            if self.godMode == False:
                self.on_collide(collider)
                
        collideWall = pygame.sprite.spritecollide(self, sGroups.staticSprites, False)
        for collider in collideWall:
            self.on_collide(collider)
            
        collidePowerup = pygame.sprite.spritecollide(self, powerupSprites, False)
        for collider in collidePowerup:
            if pygame.JOYBUTTONDOWN:
                if self.j.get_button(0):
                        collider.on_collide(self)
            
            
    def movement (self):
        if self.keys[pygame.K_w] == True:
            self.speedY = (-1 * self.dy)
        #moves player down
        elif self.keys[pygame.K_s] == True:
            self.speedY = self.dy
        else:
            self.speedY = 0
        #moves player left
        if self.keys[pygame.K_a] == True:
            self.speedX = (-1 * self.dx)
        #moves player right
        elif self.keys[pygame.K_d] == True:
            self.speedX = self.dx
        else:
            self.speedX = 0
            
    def imageChange (self, facing):
        if self.pNum == 1:
            if facing == "right":
                self.state = self.MOVE_E
            elif facing == "left":
                self.state = self.MOVE_W
            elif facing == "down":
                self.state = self.MOVE_S
            elif facing == "up":
                self.state = self.MOVE_N
        if self.pNum == 2:
            if facing == "right":
                self.state = self.MOVE_E
            elif facing == "left":
                self.state = self.MOVE_W
            elif facing == "down":
                self.state = self.MOVE_S
            elif facing == "up":
                self.state = self.MOVE_N
            
    def on_collide(self, collider):       
        
        hp = self.hp
        self.hp -= collider.damage
        if self.hp < hp:
            self.godMode = True
        if self.hp <= 0:
            self.hp = 0
            self.die()
            
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
#            print "collision happened top right"
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.bottom - self.rect.top
            self.applyOffset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
#            print "collision happened top left"
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.bottom - self.rect.top
            self.applyOffset(offsetX, offsetY)
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
#            print "collision happened bottom left"
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.top - self.rect.bottom
            self.applyOffset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
#            print "collision happened bottom right"
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.top - self.rect.bottom
            self.applyOffset(offsetX, offsetY)
                                     
    def applyOffset (self, offsetX, offsetY):
        if abs(offsetX) > abs(offsetY) and self.collideY == False:
            self.collideY = True              
            self.rect.centery += offsetY
        elif self.collideX == False:
            self.collideX = True
            self.rect.centerx += offsetX
        
    def die (self):
        self.dead = True
        self.kill()
    
    def staminaChange (self, delta):
        if delta == 0:
            self.staminaTimer += 1
#            print self.staminaTimer, "STAMINA TIME"
            if self.staminaTimer >= 2:
                    self.stamina -= 2
                    self.staminaTimer = 0
        
        if delta == 1: 
            if self.reloading == False:   
                self.staminaTimerUp += 1
                if self.staminaTimerUp >= 15:
                    self.stamina += 1
                    if self.speedX == 0 and self.speedY == 0:
                        self.stamina += 1
                    self.staminaTimerUp = 0
    
    def fire (self, dir):        
        self.fireState = True
        if self.gun == "Flamethrower":
            fire = sprites.Bullet(dataFiles.explosionSIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(fire)
        elif self.gun == "Shotgun":
            dirx = dir[0]
            diry = dir[1]
            dir1x = dir[0]
            dir1y = dir[1]
            dir2x = dir[0]
            dir2y = dir[1]
            
            dir1x += .1
            dir1y += .1
             
            radians = math.atan2 (diry, dirx)
            angle = radians * 180 / math.pi
            angle += 180
            print angle, "ANGLE ORIGINAL"
            print dirx, diry, "ORIGINAL VECTOR"
            
            radians = math.atan2 (dir1y, dirx)
            angle2 = radians * 180 / math.pi
            angle2 += 180
            print angle2, "ANGLE 2"
            print dir1x, dir1y, "ORIGINAL VECTOR"
            
            

            
            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)
            
            if dir[1] > 0 and dir[1] > dir[0] and dir[0] > -.7:
                "up"
                dir1x -= .1
                dir2x += .1
            if dir[1] > 0 and dir[0] > 0 and dir[1] > dir [0]:
                "up right"
                dir1y -= .1
                dir2x += .1
            elif dir[0] > 0 and dir[0] > dir[1]:
                "right"
                dir1y += .1
                dir2y -= .1
            elif dir[0] < 0 and dir[0] < dir[1]:
                "left"
                dir1y -= .1
                dir2y += .1
            
            elif dir[1] < 0 and dir[1] < dir[0]:
                "down"
                dir1x += .1
                dir2x -= .1
                
            dir1 = (dir1x, dir1y)
            dir2 = (dir2x, dir2y)
            
            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir1, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)
            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir2, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)
        elif self.gun == "Pistol": 
            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)       
        elif self.gun == "MP5":
            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)
        elif self.gun == "Bazooka":
            rocket = sprites.Bullet(dataFiles.rocketIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(rocket)
        
        self.fireSnd.play()
        self.ammo -= 1
        return self.bulletSprites

    def preReload (self):
        self.reloadSnd.play()
        self.reloading = True    
    
    def reload (self, gun):
        self.reloadTime = 0   
        self.clips -= 1
        self.reloading = False
        if gun == "Pistol":
            self.ammo = 9
            self.clips += 1
        elif gun == "Shotgun":
            self.ammo = 5
        elif gun == "MP5":
            self.ammo = 32
        elif gun == "Flamethrower":
            self.ammo = 100
        elif gun == "Bazooka":
            self.ammo = 1
            
    def throwGrenade(self, dir):
            self.grenade -= 1
            print "GRENADES LEFT", self.grenade
            grenade = sprites.Grenade(dataFiles.grenadeIm, self.rect.center, dir, self.speedX, self.speedY)
            self.bombSprites.add(grenade)
            return self.bombSprites
        