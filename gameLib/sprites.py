"""ZOMBOO - Game object sprites (zombies, bullets, grenades, turrets, etc).

Created 2011 by Anthony D'Alessandro.
"""


import pygame, dataFiles, sGroups, animate
import random, math

_image_cache = {}
_frame_cache = {}


def _cached_image_load(path):
    """Load and convert an image, returning a cached copy on subsequent calls.

    .copy() is intentional: pygame surfaces are mutable, and callers frequently
    call set_colorkey() or blit onto the surface they receive. Returning a copy
    prevents those mutations from corrupting the shared cached master surface.
    """
    if path not in _image_cache:
        img = pygame.image.load(path).convert()
        _image_cache[path] = img
    return _image_cache[path].copy()


def _cached_frames(path, imageC):
    """Slice a sprite sheet into directional animation frames, cached per path."""
    if path in _frame_cache:
        return _frame_cache[path]

    directions = {}
    for dir_name, mirror_of, flip in (
        ("north", "north", False),
        ("northEast", "northWest", True),
        ("east", "west", True),
        ("southEast", "southWest", True),
        ("south", "south", False),
        ("southWest", "southWest", False),
        ("west", "west", False),
        ("northWest", "northWest", False),
    ):
        frames = []
        size = animate.Animate.imageSizes[mirror_of]
        offsets = animate.Animate.offsets[mirror_of]
        sample_color = None
        for offset in offsets:
            surf = pygame.Surface(size)
            surf.blit(imageC, (0, 0), (offset, size))
            if sample_color is None:
                sample_color = surf.get_at((1, 1))
            surf.set_colorkey(sample_color)
            if flip:
                surf = pygame.transform.flip(surf, True, False)
            frames.append(surf)
        directions[dir_name] = frames

    _frame_cache[path] = directions
    return directions

try:
    pygame.joystick.init()
except pygame.error:
    pass

try:
    pygame.mixer.init()
except pygame.error:
    pass

# NOTE: Joystick state (jCount, jOn, j, j2) is initialized once when this module is
# first imported. If joysticks are connected or disconnected after import, or if the
# game is restarted within the same process, these globals will not reflect the new
# hardware state. A full process restart is required to pick up joystick changes.
jCount = pygame.joystick.get_count()
jOn = False
j = None
j2 = None
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

class GameObject(pygame.sprite.Sprite):
    """Base sprite class providing directional animation frames and screen-boundary enforcement."""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = _cached_image_load(image)
        self.imageC = self.image
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor)
        self.rect = self.image.get_rect()
        self.rect.center = ((dataFiles.SCREEN_WIDTH // 2), (dataFiles.SCREEN_HEIGHT // 2))
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

        self.load_image(image)

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
        if self.rect.right > dataFiles.SCREEN_WIDTH:
            self.speedX = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.bottom > dataFiles.SCREEN_HEIGHT:
            self.speedY = 0
            self.rect.center = (self.oldx, self.oldy)
        if self.rect.left < 0:
            self.speedX = 0
            self.rect.center = (self.oldx, self.oldy)

    def on_collide(self):
        """Handle collision events; override in subclasses."""
        pass

    def load_image (self, image):
        """Slice the sprite sheet into directional animation frame lists (cached per image)."""
        dirs = _cached_frames(image, self.imageC)
        self.NORTH = dirs["north"]
        self.NORTHEAST = dirs["northEast"]
        self.EAST = dirs["east"]
        self.SOUTHEAST = dirs["southEast"]
        self.SOUTH = dirs["south"]
        self.SOUTHWEST = dirs["southWest"]
        self.WEST = dirs["west"]
        self.NORTHWEST = dirs["northWest"]            
    
    def animation (self):
        """Advance the directional walk-cycle frame based on current movement state."""
        # P2-006: guard against uninitialized state
        if self.state is None:
            return
        if self.moving == True:
            if self.state == self.MOVE_N:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                # P2-001: display the last frame before wrapping back to 0
                self.image = self.NORTH[self.frame] if self.frame < len(self.NORTH) else self.NORTH[-1]
                if self.frame >= len(self.NORTH):
                    self.frame = 0

            elif self.state == self.MOVE_E:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                self.image = self.EAST[self.frame] if self.frame < len(self.EAST) else self.EAST[-1]
                if self.frame >= len(self.EAST):
                    self.frame = 0

            elif self.state == self.MOVE_W:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                self.image = self.WEST[self.frame] if self.frame < len(self.WEST) else self.WEST[-1]
                if self.frame >= len(self.WEST):
                    self.frame = 0

            elif self.state == self.MOVE_S:
                self.pause += 1
                if self.pause > self.animDelay:
                    self.pause = 0
                    self.frame += 1
                self.image = self.SOUTH[self.frame] if self.frame < len(self.SOUTH) else self.SOUTH[-1]
                if self.frame >= len(self.SOUTH):
                    self.frame = 0
        
class Bullet (GameObject):
    """Projectile fired by a weapon that travels in a fixed direction and expires after a set lifetime."""
    def __init__(self, image, pos, dir, damage, bulletLife, bulletStr, gun):
        GameObject.__init__(self, image)
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
        
    def update (self, splatSprites, fireSprites, dt=1.0):
        self.splatSprites = splatSprites
        self.fireSprites = fireSprites
        self.timer += 1
        self.rect.centerx += self.dir[0] * self.speed * dt
        self.rect.centery += self.dir[1] * self.speed * dt
        
        if self.timer >= self.bulletLife:
            self.die()
            
        collideWall = pygame.sprite.spritecollide (self, sGroups.staticSprites, False)
        for collider in collideWall:
            self.on_collide(collider)
            
    def on_collide (self, collider):
        """Spawn a hit splat and reduce bullet penetration strength on impact."""
        hit = HitSplat(dataFiles.hitIm, self.rect.center)
        self.splatSprites.add(hit)
        self.bulletStr -= collider.bulletResist
        if self.bulletStr <= 0:
            self.die()

        return self.splatSprites
    def die (self):
        self.kill()
        if self.gun == "Bazooka":
            explosion = Explosion(self.damage, self.rect.center)
            self.fireSprites.add(explosion)
        # P2-010: release fireSprites reference to avoid retaining group after death
        self.fireSprites = None
        
        
        
class HitSplat (GameObject):
    """Brief visual flash sprite displayed at a bullet impact point."""
    def __init__ (self, image, pos):
        GameObject.__init__ (self, image)
        self.rect.center = pos
        self.timer = 0

    def update (self):
        self.timer += 1
        if self.timer >= 5:
            self.kill()
            
class LaserSight (GameObject):
    """Rotating aim indicator that follows the player's fire direction or joystick right-stick input."""

    _rotation_cache = {}

    def __init__(self, image, player):
        GameObject.__init__(self, image)
        self.player = player
        if jOn == True:
            if self.player.pNum == 1:
                self.j = j
            elif self.player.pNum == 2:
                self.j = j2
        else:
            self.j = "none"
        self.angle = 0
        self.imageMaster = _cached_image_load(dataFiles.laserSightIm)
        self.image = self.imageMaster
        self.transColor = self.image.get_at((0, 0))
        self.image.set_colorkey(self.transColor)
        self.rect = self.image.get_rect()
        self.rect.center = self.player.rect.center
        self.dir = 0
        self._prev_angle = None
        self._build_rotation_cache()

    def _build_rotation_cache(self):
        cache_key = dataFiles.laserSightIm
        if cache_key not in LaserSight._rotation_cache:
            frames = {}
            for angle in range(360):
                frames[angle] = pygame.transform.rotate(self.imageMaster, angle)
            LaserSight._rotation_cache[cache_key] = frames
        self._frames = LaserSight._rotation_cache[cache_key]

    def update (self):
        if jOn == True and self.j != "none":
            self.joyRX = float(self.j.get_axis(4))
            self.joyRY = float(self.j.get_axis(3))
            self.dir = (self.joyRX, self.joyRY)
        else:
            mx, my = pygame.mouse.get_pos()
            aim_dx = mx - self.player.rect.centerx
            aim_dy = my - self.player.rect.centery
            dist = math.sqrt(aim_dx * aim_dx + aim_dy * aim_dy)
            if dist > 0:
                self.dir = (aim_dx / dist, aim_dy / dist)
            else:
                self.dir = self.player.dir
        self.calc_angle(self.dir)
        int_angle = int(self.angle) % 360
        if int_angle != self._prev_angle:
            self._prev_angle = int_angle
            self.image = self._frames[int_angle]
            self.rect = self.image.get_rect()
        self.rect.center = self.player.rect.center

    def calc_angle (self, dir):
        """Convert a direction vector to a rotation angle in degrees for the laser sprite."""
        dirx = dir[0]
        diry = dir[1]

        radians = math.atan2 (diry, dirx)
        self.angle = radians * -180 / math.pi
        self.angle += 270

class Explosion (GameObject):
    """Short-lived area-of-effect blast sprite that deals damage to overlapping entities once."""
    def __init__ (self, damage, pos):
        image = (dataFiles.explosionIm)
        GameObject.__init__(self, image)
        self.explodeTimer = 0
        self.damage = damage
        self.rect.center = pos
        self.damaged = set()
        
    def update (self):
        self.explodeTimer += 1
        if self.explodeTimer >= 5:
            self.kill()
        
    def on_collide(self):
        pass
        
        
                 
            
class Zombie(GameObject):
    """Enemy that pursues the nearest player and takes damage from bullets and explosions."""
    def __init__(self, image, pos):
        GameObject.__init__(self, image)
        self.image = self.NORTH[0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hp = 60
        self.damage = 25
        self.dx = 0.0
        self.dy = 0.0
        self.dxPlayer = 0
        self.dyPlayer = 0
        base_speed = 2 + random.uniform(-0.4, 0.4)
        self.speedX = base_speed
        self.speedY = base_speed
        self.delay = 0
        self.timer = 0
        self.pause = 0
        self.dir = "none"
        self.animDelay = 10
        self.wander_offset = random.uniform(0, math.pi * 2)
        self.wander_speed = random.uniform(1.5, 3.0)
        self.wander_strength = random.uniform(0.3, 0.6)
        self.steer_speed = 0.08
    
    def _get_target_pos(self, player1, player2):
        """Return the position of the nearest living player to track."""
        if player2 is not None and not player2.dead and jCount == 2:
            dist1_sq = (self.rect.centerx - player2.rect.centerx) ** 2 + (self.rect.centery - player2.rect.centery) ** 2
            dist2_sq = (self.rect.centerx - player1.rect.centerx) ** 2 + (self.rect.centery - player1.rect.centery) ** 2
            if dist2_sq <= dist1_sq:
                return player1.oldxy2
            else:
                return player2.oldxy2
        return player1.oldxy2

    def update(self, bulletSprites, fireSprites, player1, player2, dt=1.0):
        self.moving = True
        self.oldxy = self.rect.center
        self.timer += 1

        target = self._get_target_pos(player1, player2)
        diff_x = target[0] - self.rect.centerx
        diff_y = target[1] - self.rect.centery
        dist = math.sqrt(diff_x * diff_x + diff_y * diff_y)

        if dist > 1.0:
            goal_dx = diff_x / dist
            goal_dy = diff_y / dist
        else:
            goal_dx = 0.0
            goal_dy = 0.0

        self.wander_offset += self.wander_speed * 0.02
        # P2-002: wrap wander_offset to [0, 2*pi) to prevent unbounded accumulation
        self.wander_offset = self.wander_offset % (math.pi * 2)
        wander_x = math.cos(self.wander_offset) * self.wander_strength
        wander_y = math.sin(self.wander_offset) * self.wander_strength

        goal_dx += wander_x
        goal_dy += wander_y

        self.dx += (goal_dx - self.dx) * self.steer_speed
        self.dy += (goal_dy - self.dy) * self.steer_speed

        if self.rect.top < 0:
            self.dy = max(self.dy, 0)
            self.rect.centery = self.oldy
        if self.rect.right > dataFiles.SCREEN_WIDTH:
            self.dx = min(self.dx, 0)
            self.rect.centerx = self.oldx
        if self.rect.bottom > dataFiles.SCREEN_HEIGHT:
            self.dy = min(self.dy, 0)
            self.rect.centery = self.oldy
        if self.rect.left < 0:
            self.dx = max(self.dx, 0)
            self.rect.centerx = self.oldx

        if self.timer >= self.delay:
            self.moveDirX = self.dx * self.speedX
            self.moveDirY = self.dy * self.speedY

            self.rect.centerx += self.moveDirX * dt
            self.rect.centery += self.moveDirY * dt

            if abs(self.moveDirX) > abs(self.moveDirY):
                if self.moveDirX > 0:
                    self.state = self.MOVE_E
                else:
                    self.state = self.MOVE_W
            else:
                if self.moveDirY > 0:
                    self.state = self.MOVE_S
                elif self.moveDirY < 0:
                    self.state = self.MOVE_N

            GameObject.animation(self)
            self.timer = 0
                
        collideBul = pygame.sprite.spritecollide(self, bulletSprites, False)
        for collider in collideBul:
            self.on_collide(collider)
            collider.on_collide(self)
        
        collideEx = pygame.sprite.spritecollide(self, fireSprites, False)
        for collider in collideEx:
            # P2-011: use sprite object directly instead of id() so the set tracks
            # live references rather than potentially reused memory addresses
            if self not in collider.damaged:
                collider.damaged.add(self)
                self.on_collide(collider)

        collideZom = pygame.sprite.spritecollide(self, sGroups.zombieSprites, False)
        for other in collideZom:
            if other is not self:
                dx = self.rect.centerx - other.rect.centerx
                dy = self.rect.centery - other.rect.centery
                if dx == 0 and dy == 0:
                    dx = random.choice([-1, 1])
                self.rect.centerx += (1 if dx > 0 else -1)
                self.rect.centery += (1 if dy > 0 else -1)

#    def change_image (self, facing):
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
        """Subtract collider damage from HP and kill the zombie if HP reaches zero."""
        self.hp -= collider.damage
        if self.hp <= 0:
            self.kill()
                              
class BigZombie (Zombie):
    """Tougher zombie variant with increased HP and damage."""
    def __init__(self, image, pos):
        Zombie.__init__(self, image, pos)
        self.rect.center = pos
        self.hp = 200
        self.damage = 30
        
    def update (self, bulletSprites, bombSprites, player1, player2, dt=1.0):
        Zombie.update(self, bulletSprites, bombSprites, player1, player2, dt)
        
    def change_image (self, dir):
        pass
                             
class Grenade(GameObject):
    """Thrown projectile that decelerates over time and detonates into an Explosion after a cook timer."""
    def __init__(self, image, pos, dir, pSpeedX, pSpeedY):
        GameObject.__init__(self, image)
        self.grenade = 1
        self.damage = 100
        self.rect.center = pos
        self.dir = dir
        self.speed = 4.00
        self.speed = float(self.speed)
        self.timer = 0
        self.grenadeCook = 3
        # P2-007: clamp grenade speed to a maximum of 8.0 to prevent out-of-bounds travel
        self.speedX = min(abs(pSpeedX) + self.speed, 8.0)
        self.speedY = min(abs(pSpeedY) + self.speed, 8.0)
        
    def update (self, fireSprites, dt=1.0):
        GameObject.update(self)
        self.fireSprites = fireSprites

        self.timer += 1

        decel = 0.1 * dt
        self.speedX -= decel
        if self.speedX <= 0.00:
            self.speedX = 0.00

        self.speedY -= decel
        if self.speedY <= 0.00:
            self.speedY = 0.00

        self.rect.centerx += self.dir[0] * self.speedX * dt
        self.rect.centery += self.dir[1] * self.speedY * dt

        if self.timer >= (self.grenadeCook * dataFiles.FPS):
            self.die()
        
    def die(self):
        """Remove the grenade sprite and spawn an Explosion at the current position."""
        self.rect.center = (self.rect.centerx, self.rect.centery)
        self.kill()
        explosion = Explosion(self.damage, self.rect.center)
        self.fireSprites.add(explosion)
        return self.fireSprites

class UI(pygame.sprite.Sprite):
    """Heads-up display sprite that renders a player's HP, stamina, ammo, and game-over countdown."""

    _font_small = None
    _font_large = None
    _game_over_image = None

    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        if UI._font_small is None:
            UI._font_small = pygame.font.SysFont("None", 23)
            UI._font_large = pygame.font.SysFont("None", 40)
            UI._game_over_image = UI._font_large.render("GAME OVER", 10, (255, 255, 255))
        self.font = UI._font_small
        self.time = 9
        self.timer = self.time * dataFiles.FPS
        self._prev_text = None

    def update(self):
        prev = getattr(self, '_prev_text', None)
        if self.player.dead == False:
            text = "HP:                             STM: %d %s: %d/%d Nades: %d" % (self.player.stamina, self.player.gun, self.player.ammo, self.player.clips, self.player.grenade)
            if text != prev:
                self._prev_text = text
                self.image = self.font.render(text, 10, (255, 255, 255))
                self.rect = self.image.get_rect()
            self.rect.left = 5
            if self.player.pNum == 2:
                self.rect.left = 400
        elif self.player.dead == True:
            if self.timer <= 0:
                if UI._game_over_image is not None:
                    self.image = UI._game_over_image
                else:
                    self.image = self.font.render("GAME OVER", 10, (255, 255, 255))
                self.rect = self.image.get_rect()
                self.rect.center = (400, 300)
            else:
                self.timer -= 1
                self.time = self.timer // 30
                text = "Continue? %d" % self.time
                if text != prev:
                    self._prev_text = text
                    self.image = self.font.render(text, 10, (255, 255, 255))
                    self.rect = self.image.get_rect()
                self.rect.left = 100
                if self.player.pNum == 2:
                    self.rect.left = 500
                    
class Turret (GameObject):
    """Stationary auto-firing turret that aims via joystick input and self-destructs after a fixed duration."""
    def __init__(self, image, pos):
        GameObject.__init__(self, image)
        self.dir = (0, -1)
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
        
        if jOn == True:
            self.joyRX = float(j.get_axis(4))
            self.joyRY = float(j.get_axis(3))
            self.dir = (self.joyRX, self.joyRY)
        
        self.calc_vector(self.dir)
        
        oldCenter = self.rect.center 
#        self.dir += 1
#        if self.dir > 360:
#            self.dir = 0
        self.image = pygame.transform.rotate(self.imageC, self.angle) 
        self.rect = self.image.get_rect() 
        self.rect.center = oldCenter 
        
    def calc_vector (self, dir):
        """Convert a direction vector to a rotation angle in degrees for the turret sprite."""
        dirx = dir[0]
        diry = dir[1]

        radians = math.atan2 (diry, dirx)
        self.angle = radians * -180 / math.pi
        self.angle += 270

    def fire (self):
        """Spawn a bullet at the turret's position traveling in the current aim direction."""
        bullet = Bullet((dataFiles.bulletIm), self.rect.center, self.dir, self.damage, 60, 4, "MP5")
        sGroups.bulletSprites.add(bullet)
        
        return sGroups.bulletSprites
    
class Wall (pygame.sprite.Sprite):
    """Static impassable obstacle that absorbs bullets and blocks movement."""
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.imageMaster = _cached_image_load(image)
        self.image = self.imageMaster
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hp = 0
        self.damage = 0
        self.bulletResist = 5