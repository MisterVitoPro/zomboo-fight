"""ZOMBOO - Pickup items (weapons, health, ammo, grenades).

Created 2011 by Anthony D'Alessandro.
"""
import pygame, random
import sprites, dataFiles, level_LOC, sGroups


class Pickup (sprites.GameObject):
    """Base class for all spinning pickup items on the map."""

    _rotation_cache = {}

    def __init__(self, image):
        sprites.GameObject.__init__(self, image)
        self.addHp = 0
        self.weapon = "none"
        self.speed = 0
        self.clips = 0
        self.angle = 0
        self._build_rotation_cache()

    def _build_rotation_cache(self):
        cache_key = id(self.imageC)
        if cache_key not in Pickup._rotation_cache:
            frames = {}
            for angle in range(0, 362, 2):
                frames[angle] = pygame.transform.rotate(self.imageC, angle)
            Pickup._rotation_cache[cache_key] = frames
        self._frames = Pickup._rotation_cache[cache_key]

    def update(self):
        oldCenter = self.rect.center
        self.angle += 2
        if self.angle > 360:
            self.angle = 0
        self.image = self._frames[self.angle]
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
            
    def on_collide(self, player):
        self.kill()
        
    def gun_pickup(self, player):
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
    """Ammo clip pickup that replenishes the player's magazine count."""

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
    """Health restoration pickup that heals the player."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.addHp = 40
        self.rect.center = ((random.randrange(100, 700)), (random.randrange(100, 600)))
        
    def on_collide (self, player):
        self.kill()
        player.hp += self.addHp
        
class ShotgunPickup (Pickup):
    """Shotgun weapon pickup that arms the player with a shotgun."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Shotgun"
        self.clips = 25
        self.ammo = 5
        self.reloadSpeed = 10
        self.fireSnd = dataFiles.load_sound(dataFiles.shotgunFireSnd)
        self.reloadSnd = dataFiles.load_sound(dataFiles.shotgunReloadingSnd)
        self.damage = 30
        self.rect.center = level_LOC.topWeaponSpawn
        self.bulletLife = 35
        self.bulletStr = 4
        self.automatic = False
        self.fireRate = 15
        
    def on_collide(self, player):
        self.kill()
        Pickup.gun_pickup(self, player)
        
class Mp5Pickup (Pickup):
    """MP5 submachine gun pickup that arms the player with an automatic weapon."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "MP5"
        self.clips = 3
        self.ammo = 32
        self.reloadSpeed = 18
        self.fireSnd = dataFiles.load_sound(dataFiles.fireSnd)
        self.reloadSnd = dataFiles.load_sound(dataFiles.reloadSnd)
        self.damage = 20
        self.rect.center = level_LOC.rightWeaponSpawn
        self.bulletLife = 50
        self.bulletStr = 4
        self.automatic = True
        self.fireRate = 3
        
    def on_collide(self, player):
        self.kill()
        Pickup.gun_pickup(self, player)
        
class GrenadePickup (Pickup):
    """Grenade pickup that adds a grenade to the player's inventory."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.grenade = 1
        
    def on_collide(self, player):
        self.kill()
        player.grenade += self.grenade
        
class FoodPickup(Pickup):
    """Food pickup that restores the player's stamina."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.stamina = 60
        self.rect.center = (random.randrange(10, dataFiles.SCREEN_WIDTH - 10),
                            random.randrange(10, dataFiles.SCREEN_HEIGHT - 10))
        
    def on_collide(self, player):
        self.kill()
        player.stamina += self.stamina
        
class FlameThrower (Pickup):
    """Flamethrower weapon pickup that arms the player with a continuous-fire weapon."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Flamethrower"
        self.clips = 0
        self.ammo = 100
        self.reloadSpeed = 25
        self.fireSnd = dataFiles.load_sound(dataFiles.flamethrowerSnd)
        self.reloadSnd = dataFiles.load_sound(dataFiles.reloadSnd)
        self.damage = 10
        self.rect.center = level_LOC.bottomWeaponSpawn
        self.bulletLife = 25
        self.bulletStr = 8
        self.automatic = True
        self.fireRate = 2
        
    def on_collide(self, player):
        self.kill()
        Pickup.gun_pickup(self, player)
        
class RocketLauncher(Pickup):
    """Rocket launcher pickup that arms the player with a high-damage bazooka."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.gun = "Bazooka"
        self.clips = 5
        self.ammo = 1
        self.reloadSpeed = 25
        self.fireSnd = dataFiles.load_sound(dataFiles.fireSnd)
        self.reloadSnd = dataFiles.load_sound(dataFiles.reloadSnd)
        self.damage = 100
        self.rect.center = level_LOC.leftWeaponSpawn
        self.bulletLife = 100
        self.bulletStr = 2
        self.automatic = False
        self.fireRate = 5
        
    def on_collide(self, player):
        self.kill()
        Pickup.gun_pickup(self, player)
        
class TurretPickup (Pickup):
    """Turret pickup that places a defensive turret sprite on collection."""

    def __init__(self, image):
        Pickup.__init__(self, image)
        self.rect.center = (level_LOC.entiremapLOC)
        
    def on_collide(self, player):
        self.kill()
        turret = sprites.Turret(dataFiles.turretIm, self.rect.center)
        sGroups.turretSprites.add(turret)
        
        return sGroups.turretSprites
    
        