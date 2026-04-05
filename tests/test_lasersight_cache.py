# D:/workspace/zomboo-fight/tests/test_lasersight_cache.py
"""
Tests for:
  P1-006: LaserSight rotation cache uses id() as key causing unbounded growth
  P2-004: Pickup rotation cache uses id() as key risking stale cache hits
  P2-003 (edge): Zombie-zombie collision when dy==0 but dx!=0
"""
import inspect
import pytest
import pygame
import unittest.mock as mock


class TestLaserSightCacheKey:
    """P1-006: LaserSight rotation cache must use file path, not id()."""

    def test_lasersight_cache_does_not_use_id(self):
        """
        BUG REPRODUCTION (P1-006): LaserSight._build_rotation_cache() uses
        `cache_key = id(self.imageMaster)` which creates a new 360-surface cache
        per instance since _cached_image_load() returns .copy() each time.
        After the fix, id() must not be used as the cache key.
        This test FAILS on current code.
        """
        import sprites

        source = inspect.getsource(sprites.LaserSight._build_rotation_cache)

        assert "id(self.imageMaster)" not in source and "id(self.image" not in source, (
            "LaserSight._build_rotation_cache() uses id() as cache key; "
            "each instance creates a new 360-surface cache entry because "
            "_cached_image_load() returns .copy() each time, making id() unique. "
            "Use the file path string as the key instead (P1-006 bug)"
        )

    def test_lasersight_two_instances_share_one_cache_entry(self):
        """
        After the fix, two LaserSight instances loading the same image path
        should result in exactly one entry in _rotation_cache, not two.
        This test FAILS on current code.
        """
        import sprites
        import dataFiles

        # Clear the cache to get a clean count
        sprites.LaserSight._rotation_cache.clear()

        fake_surface = pygame.Surface((32, 32))
        fake_player = mock.MagicMock()
        fake_player.pNum = 1
        fake_player.rect.center = (400, 300)
        fake_player.dir = (1, 0)

        original_jOn = sprites.jOn
        sprites.jOn = False

        try:
            with mock.patch("pygame.image.load", return_value=fake_surface), \
                 mock.patch("pygame.transform.rotate", return_value=fake_surface):
                ls1 = object.__new__(sprites.LaserSight)
                ls1.player = fake_player
                ls1.j = "none"
                ls1.angle = 0
                ls1._prev_angle = None
                ls1.imageMaster = fake_surface.copy()
                ls1._build_rotation_cache()

                ls2 = object.__new__(sprites.LaserSight)
                ls2.player = fake_player
                ls2.j = "none"
                ls2.angle = 0
                ls2._prev_angle = None
                ls2.imageMaster = fake_surface.copy()
                ls2._build_rotation_cache()

            cache_size = len(sprites.LaserSight._rotation_cache)

            assert cache_size == 1, (
                "LaserSight._rotation_cache has %d entries after creating 2 instances "
                "with the same image path; expected 1 shared entry. "
                "The id() cache key creates a new entry per instance (P1-006 bug)"
                % cache_size
            )
        finally:
            sprites.jOn = original_jOn
            sprites.LaserSight._rotation_cache.clear()


class TestPickupCacheKey:
    """P2-004: Pickup rotation cache must use file path, not id()."""

    def test_pickup_cache_does_not_use_id(self):
        """
        BUG REPRODUCTION (P2-004): Pickup._build_rotation_cache() uses
        `id(self.imageC)` as cache key.  Python reuses ids of garbage-collected
        objects, so a new pickup could accidentally get stale cached frames.
        After the fix, id() must not be used.
        This test FAILS on current code.
        """
        import pickups

        source = inspect.getsource(pickups.Pickup._build_rotation_cache)

        assert "id(self.imageC)" not in source and "id(self.image" not in source, (
            "Pickup._build_rotation_cache() uses id() as cache key; "
            "Python id reuse can cause a new pickup to get stale cached rotations "
            "from a previously GC'd pickup with the same id (P2-004 bug)"
        )


class TestZombieZombieCollisionDyZero:
    """P2-003 edge case: collision nudge when dy==0 but dx!=0."""

    def test_zombie_collision_nudges_y_when_dy_is_zero(self):
        """
        P2-003: When two zombies overlap and dy==0 (same y, different x),
        the current collision code increments centerx correctly but does NOT
        increment centery because the centery increment uses `dy > 0` / `dy < 0`
        logic which is False when dy==0.

        After the fix (add a random nudge when dy==0), the zombie should
        move in y as well to break the overlap.
        This test FAILS on current code.
        """
        import sprites
        import sGroups

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            fake_image = pygame.Surface((24, 32))

            def make_zombie(pos):
                z = object.__new__(sprites.Zombie)
                pygame.sprite.Sprite.__init__(z)
                z.image = fake_image
                z.rect = fake_image.get_rect()
                z.rect.center = pos
                z.hp = 60
                z.damage = 25
                z.dx = 0.0
                z.dy = 0.0
                z.speedX = 2
                z.speedY = 2
                z.delay = 0
                z.timer = 0
                z.pause = 0
                z.animDelay = 10
                z.wander_offset = 0.0
                z.wander_speed = 2.0
                z.wander_strength = 0.0   # disable wander so position is predictable
                z.steer_speed = 0.08
                z.moving = False
                z.state = None
                z.oldx = pos[0]
                z.oldy = pos[1]
                z.oldxy = pos
                z.oldxy2 = pos
                z.frame = 0
                z.dxPlayer = 0
                z.dyPlayer = 0
                z.MOVE_N = 0
                z.MOVE_NE = 1
                z.MOVE_E = 2
                z.MOVE_SE = 3
                z.MOVE_S = 4
                z.MOVE_SW = 5
                z.MOVE_W = 6
                z.MOVE_NW = 7
                z.NORTH = [fake_image]
                z.SOUTH = [fake_image]
                z.EAST = [fake_image]
                z.WEST = [fake_image]
                return z

            sGroups.zombieSprites.empty()

            # z1 at (400, 300), z2 at (401, 300) -- same y, adjacent x
            # After rect collision detection their rects overlap; dy=0, dx=-1
            z1 = make_zombie((400, 300))
            z2 = make_zombie((401, 300))  # 1 pixel to the right, rects overlap

            sGroups.zombieSprites.add(z1)
            sGroups.zombieSprites.add(z2)

            player1 = mock.MagicMock()
            player1.rect.centerx = 400
            player1.rect.centery = 300
            player1.oldxy2 = (400, 300)

            empty = pygame.sprite.Group()

            z1_start_y = z1.rect.centery

            z1.update(empty, empty, player1, None)

            # After fix: centery should change (nudge applied when dy==0)
            assert z1.rect.centery != z1_start_y, (
                "Zombie centery did not change during collision when dy==0; "
                "the collision resolution does not nudge y when dy==0, leaving "
                "zombies stuck in a horizontal line formation (P2-003 edge case)"
            )
        finally:
            sprites.jCount = original_jcount
            sGroups.zombieSprites.empty()
