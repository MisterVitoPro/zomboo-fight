'''
Created on 26.05.2011

@author: Anthony D'Alessandro
'''
import pygame, random
import sprites, dataFiles, level_LOC, sGroups


class Pickup (sprites.gameObject):
    def __init__(self, image):
        sprites.gameObject.__init__(self, image)
        self.addHp = 0
        self.weapon = "none"
        self.speed = 0
        self.clips = 0
        self.angle = 0
        
    def update(self):
        oldCenter = self.rect.center 
        self.angle += 2
        if self.angle > 360:
            self.angle = 0
        self.image = pygame.transform.rotate(self.imageC, self.angle) 
        self.rect = self.image.get_rect() 
        self.rect.center = oldCenter 
            
    def on_collide(self):
        self.kill()
        
    def gunPickup(self, player):
        player.gun = self.gun
        player.clips = self.clips
        player.ammo = self.ammo
        player.reloadSpeed = self.reloadSpeed
        player.fireSnd = self.fireSnd
        player.damage = self.damage
        player.bulletLife = self.bulletLife
        player.automatic = self.automatic
        player.fireRate = self.fireRate
        player.bulletStr = self.bulletStr
        player.reloadSnd = self.reloadSnd
        
class ClipPickup (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.clips = 1
        self.rect.center = ((random.randrange(400, 700)), (random.randrange(100, 200)))
        
    def on_collide(self, player):
        if player.gun == "Shotgun":
            self.clips = 5
        self.kill()
        player.clips += self.clips
        
class Medkit (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.addHp = 40
        self.rect.center = ((random.randrange(100, 700)), (random.randrange(100, 600)))
        
    def on_collide (self, player):
        self.kill()
        player.hp += self.addHp
        
class shotgunPickup (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Shotgun"
        self.clips = 25
        self.ammo = 5
        self.reloadSpeed = 10
        self.fireSnd = pygame.mixer.Sound(dataFiles.shotgunFireSnd)
        self.reloadSnd = pygame.mixer.Sound(dataFiles.shotgunReloadingSnd)
        self.damage = 30
        self.rect.center = level_LOC.topWeaponSpawn
        self.bulletLife = 35
        self.bulletStr = 4
        self.automatic = False
        self.fireRate = 15
        
    def on_collide(self, player):
        self.kill()
        Pickup.gunPickup(self, player)
        
class mp5Pickup (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "MP5"
        self.clips = 3
        self.ammo = 32
        self.reloadSpeed = 18
        self.fireSnd = pygame.mixer.Sound(dataFiles.fireSnd)
        self.reloadSnd = pygame.mixer.Sound(dataFiles.reloadSnd)
        self.damage = 20
        self.rect.center = level_LOC.rightWeaponSpawn
        self.bulletLife = 50
        self.bulletStr = 4
        self.automatic = True
        self.fireRate = 3
        
    def on_collide(self, player):
        self.kill()
        Pickup.gunPickup(self, player)
        
class grenadePickup (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.grenade = 1
        
    def on_collide(self, player):
        self.kill()
        player.grenade += self.grenade
        print player.grenade, "PLUS ONE IN GRENADE INVENTORY FOR", player
        
class foodPickup(Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.stamina = 60
        self.rect.center = (random.randrange(10, 790), random.randrange(10, 590))
        
    def on_collide(self, player):
        self.kill()
        player.stamina += self.stamina
        
class flameThrower (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Flamethrower"
        self.clips = 0
        self.ammo = 100
        self.reloadSpeed = 25
        self.fireSnd = pygame.mixer.Sound(dataFiles.flamethrowerSnd)
        self.reloadSnd = pygame.mixer.Sound(dataFiles.reloadSnd)
        self.damage = 10
        self.rect.center = level_LOC.bottomWeaponSpawn
        self.bulletLife = 25
        self.bulletStr = 8
        self.automatic = True
        self.fireRate = 2
        
    def on_collide(self, player):
        self.kill()
        Pickup.gunPickup(self, player)
        
class RocketLauncher(Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Bazooka"
        self.clips = 5
        self.ammo = 1
        self.reloadSpeed = 25
        self.fireSnd = pygame.mixer.Sound(dataFiles.fireSnd)
        self.reloadSnd = pygame.mixer.Sound(dataFiles.reloadSnd)
        self.damage = 100
        self.rect.center = level_LOC.leftWeaponSpawn
        self.bulletLife = 100
        self.bulletStr = 2
        self.automatic = False
        self.fireRate = 5
        
    def on_collide(self, player):
        self.kill()
        Pickup.gunPickup(self, player)
        
class TurretPickup (Pickup):
    def __init__(self, image):
        Pickup.__init__(self, image)
        self.rect.center = (level_LOC.entiremapLOC)
        
    def on_collide(self, player):
        self.kill()
        turret = sprites.Turret(dataFiles.turretIm, self.rect.center)
        sGroups.turretSprites.add(turret)
        
        return sGroups.turretSprites
    
        