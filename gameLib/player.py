"""ZOMBOO - Player class and input handling.

Created 2011 by Anthony D'Alessandro.
"""
import pygame, sprites, math, sGroups, animate
import dataFiles


class Player (sprites.GameObject):
    """Controllable player character with health, stamina, weapons, and collision handling."""

    def __init__(self, image, pNum):
        sprites.GameObject.__init__(self, image)
        self.pNum = pNum
        self.j = None
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
        self.sprintSpeed = 1
        self.dir = (0, -1)
        self.facing = "none"
        self.fireTimer = 0
        self.emptySnd = dataFiles.load_sound(dataFiles.emptySnd)
        self.reloadSnd = dataFiles.load_sound(dataFiles.reloadSnd)
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
        """Equip the pistol and set its stats as the current weapon."""
        self.gun = "Pistol"
        self.damage = 20
        self.reloadSpeed = 15
        self.ammo = 9
        self.clips = 8
        self.fireSnd = dataFiles.load_sound(dataFiles.fireSnd)
        self.automatic = False
        self.fireRate = 10
        self.bulletLife = 45
        self.bulletStr = 2
    
    def update (self, zombieSprites, powerupSprites, bombSprites, dt=1.0):
        """Process input, movement, stamina, firing, reloading, and all collisions each frame."""

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
        self.oldxy2 = self.oldxy
        
        if sprites.jOn == True and self.j is not None:
            self.joyX = int(self.j.get_axis(0)*(self.dx- self.staminaLow))
            self.joyY = int(self.j.get_axis(1)*(self.dy- self.staminaLow))
            self.joyRX = float(self.j.get_axis(4))
            self.joyRY = float(self.j.get_axis(3))
            self.trigR = float(self.j.get_axis(2))

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
                            self.pre_reload()
                                    
            sprites.GameObject.animation(self)
            
            self.dir = (self.joyRX, self.joyRY)
            if self.j.get_button(5):
                if self.grenade > 0:
                    if self.gTimer >= self.gTime:
                        self.throw_grenade(self.dir)
                        self.gTimer = 0
            elif self.j.get_button(4):
                if self.reloading == False:
                    if self.trigR > -.01:
                        if self.gun == "Pistol":
                            if self.ammo < 9:
                                if self.clips > 0:
                                    self.pre_reload()
                        elif self.gun == "Shotgun":
                            if self.ammo < 5:
                                if self.clips > 0:
                                    self.pre_reload()
                        elif self.gun == "MP5":
                            if self.ammo < 32:
                                if self.clips > 0:
                                    self.pre_reload()
                        elif self.gun == "Flamethrower":
                            if self.ammo < 100:
                                if self.clips > 0:
                                    self.pre_reload()
                        elif self.gun == "Bazooka":
                            if self.ammo < 1:
                                if self.clips > 0:
                                    self.pre_reload()
            
#Stamina effects
        self.stamina_change(1)
#Sprinting (controller only - keyboard sprint handled below)
        if sprites.jOn == True and self.j is not None:
            if self.trigR > 0:
                if self.stamina > 0:
                    self.sprintSpeed = abs(self.trigR * 2)
                    self.animDelay = 2
                    self.stamina_change(0)
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
            self.rect.centerx = self.rect.centerx + self.speedX * self.sprintSpeed * dt
            self.rect.centery = self.rect.centery + self.speedY * self.sprintSpeed * dt
       
        """ FIRING GUN AND RELOADING USING KEYBOARD """
        self.keys = pygame.key.get_pressed()
        if sprites.jOn == False:
            if self.keys:
                self.movement()

            # Aim toward the mouse cursor
            mx, my = pygame.mouse.get_pos()
            aim_dx = mx - self.rect.centerx
            aim_dy = my - self.rect.centery
            aim_dist = math.sqrt(aim_dx * aim_dx + aim_dy * aim_dy)
            if aim_dist > 0:
                self.dir = (aim_dx / aim_dist, aim_dy / aim_dist)

            # Pick animation facing from mouse angle
            if abs(aim_dx) > abs(aim_dy):
                if aim_dx > 0:
                    self.state = self.MOVE_E
                else:
                    self.state = self.MOVE_W
            else:
                if aim_dy > 0:
                    self.state = self.MOVE_S
                else:
                    self.state = self.MOVE_N

            # Sprint with left shift
            if self.keys[pygame.K_LSHIFT]:
                if self.stamina > 0:
                    self.sprintSpeed = 2
                    self.animDelay = 2
                    self.stamina_change(0)
            else:
                self.sprintSpeed = 1
                self.animDelay = 5

            # P2-005: moving is now set by movement() based on WASD state; do not override here
            sprites.GameObject.animation(self)

        mouseButtons = pygame.mouse.get_pressed()
        firePressed = self.keys[pygame.K_SPACE] or mouseButtons[0]
        if firePressed:
            if self.fireTimer >= self.fireRate:
                if self.reloading == False:
                    if self.ammo > 0:
                        self.fire(self.dir)
                        self.fireTimer = 0
                    elif self.ammo <= 0:
                        self.fireSnd.stop()
                        self.emptySnd.play()
                        self.pre_reload()

        if self.keys[pygame.K_t] == True:
            if self.reloading == False:
                if self.gun == "Pistol":
                    if self.ammo < 9:
                        if self.clips > 0:
                            self.pre_reload()
                elif self.gun == "Shotgun":
                    if self.ammo < 5:
                        if self.clips > 0:
                            self.pre_reload()
                elif self.gun == "MP5":
                    if self.ammo < 32:
                        if self.clips > 0:
                            self.pre_reload()
                elif self.gun == "Flamethrower":
                    if self.ammo < 100:
                        if self.clips > 0:
                            self.pre_reload()
                elif self.gun == "Bazooka":
                    if self.ammo < 1:
                        if self.clips > 0:
                            self.pre_reload()

        # Throw grenade with G key
        if self.keys[pygame.K_g] == True:
            if self.grenade > 0:
                if self.gTimer >= self.gTime:
                    self.throw_grenade(self.dir)
                    self.gTimer = 0
        
        """ REALODING TIMER """                   
        if self.reloading == True:
            self.reloadTime += 1
            if self.reloadTime >= self.reloadSpeed:
                self.reload(self.gun)
                
        
        if self.rect.top < 0:
            self.speedY = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.right > dataFiles.SCREEN_WIDTH:
            self.speedX = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.bottom > dataFiles.SCREEN_HEIGHT:
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
            if self.godMode == False:
                self.on_collide(collider)
                
        collideWall = pygame.sprite.spritecollide(self, sGroups.staticSprites, False)
        for collider in collideWall:
            self.wall_collide(collider)
            
        collidePowerup = pygame.sprite.spritecollide(self, powerupSprites, False)
        for collider in collidePowerup:
            if sprites.jOn == True and self.j is not None:
                if self.j.get_button(0):
                    collider.on_collide(self)
            else:
                if self.keys[pygame.K_e] == True:
                    collider.on_collide(self)
            
            
    def movement (self):
        """Set speedX and speedY from WASD keyboard state."""
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
        # P2-005: set moving flag based on whether any WASD key is pressed
        self.moving = (self.speedX != 0 or self.speedY != 0)
            
    def image_change (self, facing):
        """Update the animation state to match a cardinal facing direction string."""
        if facing == "right":
            self.state = self.MOVE_E
        elif facing == "left":
            self.state = self.MOVE_W
        elif facing == "down":
            self.state = self.MOVE_S
        elif facing == "up":
            self.state = self.MOVE_N
            
    def on_collide(self, collider):
        """Apply damage from a zombie collider and push the player out of overlap."""

        hp = self.hp
        self.hp -= collider.damage
        if self.hp < hp:
            self.godMode = True
        if self.hp <= 0:
            self.hp = 0
            self.die()
            
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.bottom - self.rect.top
            self.apply_offset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.bottom - self.rect.top
            self.apply_offset(offsetX, offsetY)
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.top - self.rect.bottom
            self.apply_offset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.top - self.rect.bottom
            self.apply_offset(offsetX, offsetY)
                                     
    def wall_collide(self, collider):
        """Push the player out of overlap with a static wall collider."""
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.bottom - self.rect.top
            self.apply_offset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.top < collider.rect.bottom and self.rect.top > collider.rect.top:
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.bottom - self.rect.top
            self.apply_offset(offsetX, offsetY)
        if self.rect.right > collider.rect.left and self.rect.right < collider.rect.right and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
            offsetX = collider.rect.left - self.rect.right
            offsetY = collider.rect.top - self.rect.bottom
            self.apply_offset(offsetX, offsetY)
        if self.rect.left < collider.rect.right and self.rect.left > collider.rect.left and self.rect.bottom > collider.rect.top and self.rect.bottom < collider.rect.bottom:
            offsetX = collider.rect.right - self.rect.left
            offsetY = collider.rect.top - self.rect.bottom
            self.apply_offset(offsetX, offsetY)

    def apply_offset (self, offsetX, offsetY):
        """Resolve overlap by nudging the player along the axis of least penetration."""
        if abs(offsetX) > abs(offsetY) and self.collideY == False:
            self.collideY = True              
            self.rect.centery += offsetY
        elif self.collideX == False:
            self.collideX = True
            self.rect.centerx += offsetX
        
    def die (self):
        """Mark the player as dead and remove it from all sprite groups."""
        self.dead = True
        self.kill()
    
    def stamina_change (self, delta):
        """Drain stamina when delta is 0 (sprinting) or regenerate it when delta is 1 (resting)."""
        if delta == 0:
            self.staminaTimer += 1
            if self.staminaTimer >= 2:
                    self.stamina -= 2
                    self.staminaTimer = 0
        
        if delta == 1: 
            if self.reloading == False:   
                self.staminaTimerUp += 1
                if self.staminaTimerUp >= 15:
                    self.stamina += 1
                    if abs(self.speedX) < 0.5 and abs(self.speedY) < 0.5:
                        self.stamina += 1
                    self.staminaTimerUp = 0
    
    def fire (self, dir):
        """Spawn a bullet (or spread/projectile) in dir for the current weapon and decrement ammo."""
        if dir == (0, 0):
            return self.bulletSprites
        self.fireState = True
        if self.gun == "Flamethrower":
            fire = sprites.Bullet(dataFiles.explosionSIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(fire)
        elif self.gun == "Shotgun":
            spread = 0.15
            radians = math.atan2(dir[1], dir[0])
            dir1 = (math.cos(radians + spread), math.sin(radians + spread))
            dir2 = (math.cos(radians - spread), math.sin(radians - spread))

            bullet = sprites.Bullet(dataFiles.bulletIm, self.rect.center, dir, self.damage, self.bulletLife, self.bulletStr, self.gun)
            self.bulletSprites.add(bullet)
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

    def pre_reload (self):
        """Play the reload sound and flag the player as currently reloading."""
        self.reloadSnd.play()
        self.reloading = True    
    
    def reload (self, gun):
        """Complete a reload by spending a clip and restoring full ammo for the given gun."""
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
            
    def throw_grenade(self, dir):
        """Spawn a grenade in dir, inheriting the player's current velocity, and decrement the count."""
        self.grenade -= 1
        grenade = sprites.Grenade(dataFiles.grenadeIm, self.rect.center, dir, self.speedX, self.speedY)
        self.bombSprites.add(grenade)
        return self.bombSprites
        