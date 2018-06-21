'''
Created on Mar 9, 2011

@author: student
'''


import pygame
import animation
import sprites


#player1 sprite class    
class PLAYER1(pygame.sprite.Sprite):
    def __init__(self, charName, pri, jmpH, mov, dir, startX, LA, HA):
        pygame.sprite.Sprite.__init__(self)
        #health bar class
        
        #character name
        self.name = charName
        
        #Character state layout
        self.STANDING = 1
        self.STANDINGF = 7
        self.WALKING = 0
        self.WALKINGF = 5
        self.JUMPING = 2
        self.JUMPINGF = 8
        self.LIGHTATTACK = 3
        self.LIGHTATTACKF = 9
        self.HEAVYATTACK = 4
        self.HEAVYATTACKF = 10
        
        #Which direction does the player face at start
        self.dir = dir
        
        #start position on screen
        self.startPos = (startX)
        
        #Character attributes
        self.priority = pri
        self.jumpHeight = jmpH
        self.movement = mov
        self.health = 100
        self.LA = LA
        self.HA = HA
        
        #loads all images
        self.loadImages()
    
        #Image control, placement and ground plane setup
        self.dx = 0
        self.dy = 0
        self.loadImages()
        self.image = self.imageJumping
        self.x, self.y = self.image.get_size()
        
        self.feet = self.y/2
        self.rect = self.image.get_rect()
        self.rect.center = (256, (660 - self.feet))
        
        #Gravity modifier
        self.gravity = 8
        
        #animation controls
        self.frame = 0
        self.delay = 2
        self.ladelay = 3
        self.hadelay = 2
        self.pause = 0
        self.repeat = 0
        self.p1health = P1HEALTH(self.dx, self.dy, self.health, self.dir)
        #initial state
        self.state = self.STANDING
         
         
    def p1HDamage(self, p1, p2):
        if pygame.sprite.collide_circle(p1, p2) == 1:
            if p2.state != p2.LIGHTATTACK and p2.HEAVYATTACK and p2.LIGHTATTACKF and p2.HEAVYATTACKF:
                p2.health = p2.health - p1.HA
                
            elif p1.dir == p2.dir:
                b4Bonus = p1.priority
                p1.priority = + 50
                p2.health = p2.health - p1.HA
                p1.priority = b4Bonus
                
            elif p1.priority > p2.priority:
                p2.health = p2.health - p1.HA
                
                if p1.priority < p2.priority:
                    p1.health = p1.health - p2.LA
             
                                  
    def checkKeys1(self):
        keys = pygame.key.get_pressed()
                
        if self.state != self.JUMPING and self.state != self.JUMPINGF:
            if keys[pygame.K_w]:
                if self.dir == "left":
                    self.state = self.JUMPING
                    self.dy = -self.jumpHeight
                if self.dir == "right":
                    self.state = self.JUMPINGF
                    self.dy = -self.jumpHeight
        
        else: # We Are Jumping// I have to mod this so I can still have movement in air 
            if keys[pygame.K_d]:
                if self.dir == "right":
                    self.rect.centerx += self.movement
            elif keys[pygame.K_a]:
                if self.dir == "left":
                    self.rect.centerx -= self.movement
                
        if self.state != self.HEAVYATTACK and self.state != self.HEAVYATTACKF and self.state != self.LIGHTATTACK and self.state != self.LIGHTATTACKF:

                          
            if self.state != self.JUMPING and self.state != self.JUMPINGF:
                
                if keys[pygame.K_d]:
                    self.rect.centerx += self.movement
#                            if self.state != self.JUMPING:
#                                if self.state != self.JUMPINGF:
                    self.dir = "right"
                    self.state = self.WALKINGF               
                    print "going right"
                    
                elif keys[pygame.K_a]:
                    self.rect.centerx -= self.movement
#                                if self.state != self.JUMPING:
                    self.dir = "left"
                    self.state = self.WALKING
                    print "going left"
                    
                if keys[pygame.K_SPACE]:
                    if self.dir == "left": 
                        self.state = self.LIGHTATTACK
                        self.dx = -self.LA
                    if self.dir == "right":
                        self.state = self.LIGHTATTACKF
                        self.dx = +self.LA
#                        if pygame.sprite.collide_circle(fatguy, testdumdum)== 1:
#                            testdumdum.health = testdumdum.health - self.damage
        
                if keys[pygame.K_LALT]:
                    if self.dir == "left":
                        self.state = self.HEAVYATTACK
                        self.dx = -self.HA
                    if self.dir == "right":
                        self.state = self.HEAVYATTACKF
                        self.dx = +self.HA

    #loads all images  
    def loadImages(self):
        self.imageWalking = pygame.image.load(("images/" + self.name + ".bmp"))
        self.imageWalkingF = pygame.image.load(("images/" + self.name + "F.bmp"))
        self.imageStand = pygame.image.load(("images/" + self.name + "Standing.bmp"))
        self.imageStandF = pygame.image.load(("images/" + self.name + "StandingF.bmp"))
        self.imageJumping = pygame.image.load(("images/" + self.name + "J.bmp"))
        self.imageJumpingF = pygame.image.load(("images/" + self.name + "JF.bmp"))
        self.imageLattack = pygame.image.load(("images/" + self.name + "LightAttack.bmp"))
        self.imageLattackF = pygame.image.load(("images/" + self.name + "LightAttackF.bmp"))
        self.imageHattack = pygame.image.load(("images/" + self.name + "HeavyAttack.bmp"))
        self.imageHattackF = pygame.image.load(("images/" + self.name + "HeavyAttackF.bmp"))
#coverts all images
        self.imageStand = self.imageStand.convert()
        self.imageStandF = self.imageStandF.convert()
        self.imageWalking = self.imageWalking.convert()
        self.imageWalkingF = self.imageWalkingF.convert()
        self.imageJumping = self.imageJumping.convert()
        self.imageJumping = self.imageJumpingF.convert()
        self.imageLattack = self.imageLattack.convert()
        self.imageHattack = self.imageHattack.convert()
              
        
#JUMP
        imgSizeJ = animation.AnimationInfo.imageSizes[self.name + "Jumping"]
        offsetJ = animation.AnimationInfo.offsets[self.name + "Jumping"]
        
        tmpImageJ = pygame.Surface(imgSizeJ)
        tmpImageJ.blit (self.imageJumping, (0,0), (offsetJ, imgSizeJ))
        transColor = tmpImageJ.get_at((1, 1))
        tmpImageJ.set_colorkey(transColor)
        tmpImageJS = pygame.transform.scale2x(tmpImageJ)
        self.imageJumping = tmpImageJS
  
#Flipped JUMP
        imgSizeJF = animation.AnimationInfo.imageSizes[self.name + "Jumping"]
        offsetJF = animation.AnimationInfo.offsets[self.name + "Jumping"]
        
        tmpImageJF = pygame.Surface(imgSizeJF)
        tmpImageJF.blit (self.imageJumpingF, (0,0), (offsetJF, imgSizeJF))
        transColor = tmpImageJF.get_at((1, 1))
        tmpImageJF.set_colorkey(transColor)
        tmpImageJF = (pygame.transform.flip(tmpImageJF, 1, 0))
        tmpImageJFS = pygame.transform.scale2x(tmpImageJF)
        self.imageJumpingF = tmpImageJFS      
        
 
#IDLE   
        self.Stand = []
        imgSizeS = animation.AnimationInfo.imageSizes[self.name + "Standing"]
        offsetS = animation.AnimationInfo.offsets[self.name + "Standing"]
        
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "Standing"])
        for i in range(frameCount):
            tmpImageS = pygame.Surface(imgSizeS)
            tmpImageS.blit (self.imageStand, (0,0), (offsetS[i], imgSizeS))
            transColor = tmpImageS.get_at((1, 1))
            tmpImageS.set_colorkey(transColor)
            tmpImageSS = pygame.transform.scale2x(tmpImageS)
            self.Stand.append(tmpImageSS)
            
#Flipped IDLE     
        self.StandF = []
        imgSizeWF = animation.AnimationInfo.imageSizes[self.name + "Standing"]
        offsetWF = animation.AnimationInfo.offsets[self.name + "Standing"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "Standing"])
        for i in range(frameCount):
            tmpImageSF = pygame.Surface(imgSizeWF)
            tmpImageSF.blit (self.imageStandF, (0,0), (offsetWF[i], imgSizeWF))
            transColor = tmpImageSF.get_at((1, 1))
            tmpImageSF.set_colorkey(transColor)
            tmpImageSF = (pygame.transform.flip(tmpImageSF, 1, 0))
            tmpImageSSF = pygame.transform.scale2x(tmpImageSF)
            self.StandF.append(tmpImageSSF)
            
#animates the walk cycle
        self.walking = []
        imgSizeW = animation.AnimationInfo.imageSizes[self.name + "Walking"]
        offsetW = animation.AnimationInfo.offsets[self.name + "Walking"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "Walking"])
        for i in range(frameCount):
            tmpImageW = pygame.Surface(imgSizeW)
            tmpImageW.blit (self.imageWalking, (0,0), (offsetW[i], imgSizeW))
            transColor = tmpImageW.get_at((1, 1))
            tmpImageW.set_colorkey(transColor)
            tmpImageWS = pygame.transform.scale2x(tmpImageW)
            self.walking.append(tmpImageWS)

#flips the walk cycle for walking right
        self.walkingF = []
        
        imgSizeWF = animation.AnimationInfo.imageSizes[self.name + "Walking"]
        offsetWF = animation.AnimationInfo.offsets[self.name + "Walking"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "Walking"])
        for i in range(frameCount):
            tmpImageWF = pygame.Surface(imgSizeW)
            tmpImageWF.blit (self.imageWalkingF, (0,0), (offsetWF[i], imgSizeWF))
            transColor = tmpImageWF.get_at((1, 1))
            tmpImageWF.set_colorkey(transColor)
            tmpImageWF = (pygame.transform.flip(tmpImageWF, 1, 0))
            tmpImageWFS = pygame.transform.scale2x(tmpImageWF)
            self.walkingF.append(tmpImageWFS)
            
#animates the light attack  
        self.lattack = []
        imgSizela = animation.AnimationInfo.imageSizes[self.name + "LightAttack"]
        offsetla = animation.AnimationInfo.offsets[self.name + "LightAttack"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "LightAttack"])
        for i in range(frameCount):
            tmpImagela = pygame.Surface(imgSizela)
            tmpImagela.blit (self.imageLattack, (0,0), (offsetla[i], imgSizela))
            transColor = tmpImagela.get_at((1, 1))
            tmpImagela.set_colorkey(transColor)
            tmpImagela = pygame.transform.scale2x(tmpImagela)
            self.lattack.append(tmpImagela)
            
#flips the light attack for attacking the right side
        self.lattackF = []
        imgSizelaF = animation.AnimationInfo.imageSizes[self.name + "LightAttack"]
        offsetlaF = animation.AnimationInfo.offsets[self.name + "LightAttack"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "LightAttack"])
        for i in range(frameCount):
            tmpImagelaF = pygame.Surface(imgSizelaF)
            tmpImagelaF.blit (self.imageLattackF, (0,0), (offsetlaF[i], imgSizelaF))
            transColor = tmpImagelaF.get_at((1, 1))
            tmpImagelaF.set_colorkey(transColor)
            tmpImagelaF = (pygame.transform.flip(tmpImagelaF, 1, 0))
            tmpImagelaFS = pygame.transform.scale2x(tmpImagelaF)
            self.lattackF.append(tmpImagelaFS)
            
#animates the heavy attack  
        self.hattack = []
        imgSizeH = animation.AnimationInfo.imageSizes[self.name + "HeavyAttack"]
        offsetH = animation.AnimationInfo.offsets[self.name + "HeavyAttack"]
        
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "HeavyAttack"])
        for i in range(frameCount):
            tmpImageH = pygame.Surface(imgSizeH)
            tmpImageH.blit (self.imageHattack, (0,0), (offsetH[i], imgSizeH))
            transColor = tmpImageH.get_at((1, 1))
            tmpImageH.set_colorkey(transColor)
            tmpImageH = pygame.transform.scale2x(tmpImageH)
            self.hattack.append(tmpImageH)
            
#flips the heavy attack for attacking the right side   
        self.hattackF = []
        imgSizeHF = animation.AnimationInfo.imageSizes[self.name + "HeavyAttack"]
        offsetHF = animation.AnimationInfo.offsets[self.name + "HeavyAttack"]
        
        frameCount = len(animation.AnimationInfo.offsets[self.name + "HeavyAttack"])
        for i in range(frameCount):
            tmpImageHF = pygame.Surface(imgSizeHF)
            tmpImageHF.blit (self.imageHattackF, (0,0), (offsetHF[i], imgSizeHF))
            transColor = tmpImageHF.get_at((1, 1))
            tmpImageHF.set_colorkey(transColor)
            tmpImageHF = (pygame.transform.flip(tmpImageHF, 1, 0))
            tmpImageHFS = pygame.transform.scale2x(tmpImageHF)
            self.hattackF.append(tmpImageHFS)

    #sets gravity and the ground plane
    def grav(self):   
        
        if self.state == self.JUMPING:
            
                self.dy += self.gravity
                
                if self.dy > 30:
                    self.dy = 30
                           
                if self.rect.centery >= 660 - self.feet:
                    self.rect.centery = 660 - self.feet
                    self.dy = 0
                    self.state = self.STANDING
        if self.state == self.JUMPINGF:
            
                self.dy += self.gravity
                
                if self.dy > 30:
                    self.dy = 30
                           
                if self.rect.centery >= 660 - self.feet:
                    self.rect.centery = 660 - self.feet
                    self.dy = 0
                    self.state = self.STANDINGF
             
    def getHud(self):
        return self.p1health
    
    def update(self):
        self.grav()
        self.p1health.setCenter(self.rect.centerx + self.dx, self.rect.centery + self.dy, self.health, self.dir)
        if self.state == self.STANDING:
            self.pause += 1
            if self.pause > self.delay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.Stand):
                self.frame = 0
                self.state = self.STANDING
#                self.image = self.Stand[self.frame]
            else:
                self.image = self.Stand[self.frame]
            
        elif self.state == self.STANDINGF:
            self.pause += 1
            if self.pause > self.delay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.StandF):
                self.frame = 0
                self.state = self.STANDINGF
#                self.image = self.StandF[self.frame]
            else:
                self.image = self.StandF[self.frame]
                
        if self.state == self.LIGHTATTACK:
            self.image = self.lattack
            self.pause += 1                    
            if self.pause > self.ladelay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.lattack):
                self.frame = 0
                self.state = self.STANDING
                self.image = self.lattack[self.frame]
            else:
                self.image = self.lattack[self.frame]
        
        elif self.state == self.LIGHTATTACKF:
            self.image = self.lattackF
            self.pause += 1
            
            
            if self.pause > self.ladelay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.lattackF):
                self.frame = 0
                self.state = self.STANDINGF
                self.image = self.lattackF[self.frame]
            else:
                self.image = self.lattackF[self.frame]
                
        if self.state == self.HEAVYATTACK:
            self.image = self.hattack
            self.pause += 1
            
#            self.p1HDamage(sprites.player1, sprites.player2)
            
            if self.pause > self.ladelay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.hattack):
                self.frame = 0
                self.state = self.STANDING
                self.image = self.hattack[self.frame]
            else:
                self.image = self.hattack[self.frame]
                
        elif self.state == self.HEAVYATTACKF:
            self.image = self.hattackF
            self.pause += 1
            
#            self.p1HDamage(sprites.player1, sprites.player2)
            
            if self.pause > self.ladelay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.hattackF):
                self.frame = 0
                self.state = self.STANDINGF
                self.image = self.hattackF[self.frame]
            else:
                self.image = self.hattackF[self.frame]
                
        if self.state == self.WALKING:
            self.dir = "left"
            self.image = self.walking
            self.pause += 1
            if self.pause > self.delay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.walking):
                self.frame = 0
                self.state = self.STANDING
                self.image = self.walking[self.frame]
            else:
                self.image = self.walking[self.frame]
                    
        elif self.state == self.WALKINGF:
            self.dir = "right"
            self.image = self.walkingF
            self.pause += 1
            if self.pause > self.delay:
#reset pause and advance animation
                self.pause = 0
                self.frame += 1
            if self.frame >= len(self.walkingF):
                self.frame = 0
                self.state = self.STANDINGF
                self.image = self.walkingF[self.frame]
            else:
                self.image = self.walkingF[self.frame]
                
        if self.state == self.STANDING:
            self.dx = 0
        if self.state == self.STANDINGF:
            self.dx = 0 
                              
        elif self.state == self.JUMPING:
                self.image = self.imageJumping
        elif self.state == self.JUMPINGF:
                self.image = self.imageJumpingF
                
        self.checkKeys1()
        self.rect.center = (self.rect.centerx + self.dx, self.rect.centery + self.dy)
        
