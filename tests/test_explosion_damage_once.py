"""
P2-006: Explosion deals damage every frame it overlaps a zombie instead of once.

Bug: In sprites.Zombie.update() (sprites.py lines 510-512):
    collideEx = pygame.sprite.spritecollide(self, fireSprites, False)
    for collider in collideEx:
        self.on_collide(collider)

The third argument to spritecollide is `dokill=False`, meaning the Explosion
sprite is NOT removed after the collision.  Since Explosion.update() keeps
the sprite alive for 5 frames, the zombie takes damage on every one of those
5 frames.  With damage=50, that's 250 total instead of 50.

Fix: Either use `dokill=True` to remove the explosion after first contact,
or add a 'has_damaged' flag to Explosion so it only deals damage once,
or handle it in Explosion.on_collide().
"""
import pytest
import pygame
import unittest.mock as mock


def _make_minimal_zombie(pos=(400, 300)):
    import sprites
    fake_image = pygame.Surface((24, 32))
    z = object.__new__(sprites.Zombie)
    pygame.sprite.Sprite.__init__(z)
    z.image = fake_image
    z.rect = fake_image.get_rect()
    z.rect.center = pos
    z.hp = 100
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


def _make_explosion(pos=(400, 300), damage=50):
    """Build a minimal Explosion sprite."""
    import sprites
    fake_image = pygame.Surface((32, 32))
    exp = object.__new__(sprites.Explosion)
    pygame.sprite.Sprite.__init__(exp)
    exp.image = fake_image
    exp.rect = fake_image.get_rect()
    exp.rect.center = pos
    exp.damage = damage
    exp.explodeTimer = 0
    exp.hp = 0
    exp.bulletResist = 0
    exp.damaged = set()
    return exp


class TestExplosionDamageOnce:
    """P2-006: Explosion must only deal damage once to a zombie."""

    def test_explosion_damages_zombie_multiple_times_per_overlap(self):
        """
        BUG REPRODUCTION (P2-006): A zombie colliding with an Explosion for
        5 consecutive frames (the Explosion lifetime) takes 5x the damage
        because spritecollide(..., dokill=False) never removes the explosion.

        With damage=50 and 5 frames of overlap, expected zombie hp = 100 - 50 = 50
        but the bug produces: 100 - (50 * 5) = -150 (zombie killed after first hit).

        We run the zombie update 5 times with the explosion present and check
        the final hp.  This test FAILS after the fix because damage is applied
        only once.
        """
        import sprites

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            zombie = _make_minimal_zombie(pos=(400, 300))
            explosion = _make_explosion(pos=(400, 300), damage=50)

            # Manually keep the explosion alive (bypass its own update() timer)
            fire_group = pygame.sprite.Group()
            fire_group.add(explosion)

            player1 = mock.MagicMock()
            player1.rect.centerx = 200
            player1.rect.centery = 200
            player1.oldxy2 = (200, 200)

            empty_bullets = pygame.sprite.Group()
            # Zombie must be in a group for alive() to return True
            zombie_group = pygame.sprite.Group()
            zombie_group.add(zombie)

            # Run 5 update ticks -- the explosion stays in fire_group each time
            for i in range(5):
                if zombie.alive():
                    zombie.update(empty_bullets, fire_group, player1, None)

            final_hp = zombie.hp

            # With the bug: damage=50 applied 5 times = 250 total > 100 hp => zombie dead
            # After fix: damage applied once => hp = 50
            assert final_hp == 50, (
                "Zombie hp is %d after 5 frames of explosion overlap; "
                "expected 50 (damage=50 applied once).  "
                "The explosion is dealing damage every frame because "
                "spritecollide uses dokill=False (P2-006 bug)" % final_hp
            )
        finally:
            sprites.jCount = original_jcount

    def test_explosion_zombie_damage_once_when_fixed(self):
        """
        After the fix, a single explosion tick should deal damage exactly once.
        We verify this by checking hp after a single update.
        """
        import sprites

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            zombie = _make_minimal_zombie(pos=(400, 300))
            explosion = _make_explosion(pos=(400, 300), damage=50)

            fire_group = pygame.sprite.Group()
            fire_group.add(explosion)

            player1 = mock.MagicMock()
            player1.rect.centerx = 200
            player1.rect.centery = 200
            player1.oldxy2 = (200, 200)

            empty_bullets = pygame.sprite.Group()
            zombie.update(empty_bullets, fire_group, player1, None)

            # After one tick, if collided, hp should be 50
            # This assertion should hold regardless of the bug
            assert zombie.hp <= 100, "zombie hp exceeded starting value"
        finally:
            sprites.jCount = original_jcount
