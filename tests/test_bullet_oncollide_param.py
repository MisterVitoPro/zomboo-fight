"""
P1-009: Zombie.update() calls collider.on_collide(collider) -- passing the
bullet to ITSELF instead of passing the zombie.

Bug: In sprites.Zombie.update() (sprites.py lines 506-508):
    collideBul = pygame.sprite.spritecollide(self, bulletSprites, False)
    for collider in collideBul:
        self.on_collide(collider)       # correct: zombie takes damage from bullet
        collider.on_collide(collider)   # BUG: bullet.on_collide receives itself

Bullet.on_collide(collider) expects `collider` to be the object the bullet
hit (e.g. a wall with bulletResist), not the bullet itself.  When the bullet
is passed itself, it subtracts its own bulletResist from bulletStr multiple
times and otherwise applies wrong logic.

Fix: Change `collider.on_collide(collider)` to `collider.on_collide(self)`
so the bullet receives the zombie as the collider.
"""
import pytest
import pygame
import unittest.mock as mock


def _make_minimal_zombie(pos=(400, 300)):
    import sprites
    fake_image = pygame.Surface((24, 32))
    z = object.__new__(sprites.Zombie)
    z.image = fake_image
    z.rect = fake_image.get_rect()
    z.rect.center = pos
    z.hp = 60
    z.damage = 25
    z.dx = 0
    z.dy = 0
    z.dxPlayer = 0
    z.dyPlayer = 0
    z.speedX = 2
    z.speedY = 2
    z.delay = 0
    z.timer = 0
    z.pause = 0
    z.animDelay = 10
    z.wander_offset = 0.0
    z.wander_speed = 2.0
    z.wander_strength = 0.0
    z.steer_speed = 0.08
    z.moving = False
    z.state = None
    z.oldx = pos[0]
    z.oldy = pos[1]
    z.oldxy = pos
    z.oldxy2 = pos
    z.frame = 0
    z.MOVE_N = 0
    z.MOVE_E = 2
    z.MOVE_S = 4
    z.MOVE_W = 6
    z.MOVE_NE = 1
    z.MOVE_SE = 3
    z.MOVE_SW = 5
    z.MOVE_NW = 7
    z.NORTH = [fake_image]
    z.SOUTH = [fake_image]
    z.EAST = [fake_image]
    z.WEST = [fake_image]
    return z


class TestBulletOnCollideParam:
    """P1-009: bullet.on_collide must receive the zombie, not itself."""

    def test_bullet_on_collide_receives_zombie_not_itself(self):
        """
        BUG REPRODUCTION (P1-009): In Zombie.update(), when a bullet hits a
        zombie, the code calls `collider.on_collide(collider)` -- passing the
        bullet itself as the argument.  It should call `collider.on_collide(self)`
        -- passing the zombie.

        We record what argument bullet.on_collide() receives and assert it is
        the zombie, not the bullet.  This test FAILS on the current code.
        """
        import sprites

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            zombie = _make_minimal_zombie(pos=(400, 300))
            fake_surface = pygame.Surface((8, 8))

            received_args = []

            # Create a real Bullet but override on_collide to record the arg
            bullet = object.__new__(sprites.Bullet)
            pygame.sprite.Sprite.__init__(bullet)
            bullet.image = fake_surface
            bullet.rect = fake_surface.get_rect()
            bullet.rect.center = (400, 300)  # Same position as zombie
            bullet.damage = 20
            bullet.bulletStr = 2
            bullet.bulletResist = 0
            bullet.speed = 10
            bullet.dir = (1, 0)
            bullet.timer = 0
            bullet.bulletLife = 45
            bullet.gun = "Pistol"
            bullet.splatSprites = pygame.sprite.Group()
            bullet.fireSprites = pygame.sprite.Group()

            def recording_on_collide(collider):
                received_args.append(collider)

            bullet.on_collide = recording_on_collide

            bullet_group = pygame.sprite.Group()
            bullet_group.add(bullet)

            # Build a minimal player mock
            player1 = mock.MagicMock()
            player1.rect.centerx = 200
            player1.rect.centery = 200
            player1.oldxy2 = (200, 200)

            # Ensure collision is detected: bullet is at same position as zombie
            empty_group = pygame.sprite.Group()
            zombie.update(bullet_group, empty_group, player1, None)

            assert len(received_args) > 0, (
                "bullet.on_collide was never called during zombie.update() "
                "even though bullet overlaps zombie.  Check collision detection."
            )

            received = received_args[0]
            assert received is zombie, (
                "bullet.on_collide received %r (type %s) instead of the zombie.  "
                "Zombie.update() calls collider.on_collide(collider) but should "
                "call collider.on_collide(self) to pass the zombie (P1-009 bug)"
                % (received, type(received).__name__)
            )
        finally:
            sprites.jCount = original_jcount
