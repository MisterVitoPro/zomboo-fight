"""Tests for remaining P1 fixes: P1-002, P1-008, P1-010, P1-011, P1-014, P1-016."""
import inspect
import math
import os
import sys
import pytest
import pygame
import unittest.mock as mock


class TestJoystickMixerInitSafe:
    """P1-002: Module-level joystick/mixer init should be wrapped in try/except."""

    def test_joystick_init_wrapped_in_try(self):
        import sprites
        src = inspect.getsource(sys.modules[sprites.__name__])
        # The joystick.init() call should be inside a try block
        idx_joy = src.index("pygame.joystick.init()")
        # Find the nearest 'try' before it
        before = src[:idx_joy]
        assert "try:" in before[before.rfind("\n\n"):], (
            "pygame.joystick.init() is not wrapped in try/except (P1-002)"
        )

    def test_mixer_init_wrapped_in_try(self):
        import sprites
        src = inspect.getsource(sys.modules[sprites.__name__])
        idx_mix = src.index("pygame.mixer.init()")
        before = src[:idx_mix]
        assert "try:" in before[before.rfind("\n\n"):], (
            "pygame.mixer.init() is not wrapped in try/except (P1-002)"
        )

    def test_j_and_j2_have_defaults(self):
        """j and j2 should be initialized to None so code doesn't crash on NameError."""
        import sprites
        src = inspect.getsource(sys.modules[sprites.__name__])
        assert "j = None" in src or "j=None" in src, (
            "sprites.j is not initialized to None as a default (P1-002)"
        )
        assert "j2 = None" in src or "j2=None" in src, (
            "sprites.j2 is not initialized to None as a default (P1-002)"
        )


class TestShotgunSpread:
    """P1-008: Shotgun spread should work in all 8 directions using angle-based math."""

    def test_shotgun_produces_three_distinct_bullets(self):
        """Shotgun must fire 3 bullets with distinct directions."""
        import sprites
        import sGroups

        fake_surface = pygame.Surface((8, 8))

        p = object.__new__(pygame.sprite.Sprite)
        # Build a minimal player-like object for fire()
        import player as player_module
        p = object.__new__(player_module.Player)
        pygame.sprite.Sprite.__init__(p)
        p.image = fake_surface
        p.rect = fake_surface.get_rect()
        p.rect.center = (400, 300)
        p.gun = "Shotgun"
        p.damage = 30
        p.bulletLife = 35
        p.bulletStr = 4
        p.fireState = False
        p.fireSnd = mock.MagicMock()
        p.ammo = 5
        p.bulletSprites = pygame.sprite.Group()

        with mock.patch("pygame.image.load", return_value=fake_surface):
            p.fire((1, 0))

        bullets = list(p.bulletSprites)
        assert len(bullets) == 3, "Shotgun should create 3 bullets, got %d" % len(bullets)

        dirs = [b.dir for b in bullets]
        # All 3 should be distinct
        assert len(set(dirs)) == 3, (
            "Shotgun bullets should have 3 distinct directions, got %s" % dirs
        )

    def test_shotgun_spread_works_diagonally(self):
        """Shotgun spread must work for diagonal directions too (P1-008 bug)."""
        import player as player_module

        fake_surface = pygame.Surface((8, 8))
        p = object.__new__(player_module.Player)
        pygame.sprite.Sprite.__init__(p)
        p.image = fake_surface
        p.rect = fake_surface.get_rect()
        p.rect.center = (400, 300)
        p.gun = "Shotgun"
        p.damage = 30
        p.bulletLife = 35
        p.bulletStr = 4
        p.fireState = False
        p.fireSnd = mock.MagicMock()
        p.ammo = 5
        p.bulletSprites = pygame.sprite.Group()

        diagonal = (0.707, 0.707)  # ~45 degrees
        with mock.patch("pygame.image.load", return_value=fake_surface):
            p.fire(diagonal)

        bullets = list(p.bulletSprites)
        assert len(bullets) == 3, "Shotgun diagonal should create 3 bullets"
        dirs = [b.dir for b in bullets]
        assert len(set(dirs)) == 3, (
            "Shotgun diagonal bullets should have 3 distinct dirs, got %s" % dirs
        )

    def test_shotgun_uses_angle_math(self):
        """The fix should use math.atan2/cos/sin for spread, not manual axis offsets."""
        import player as player_module
        src = inspect.getsource(player_module.Player.fire)
        assert "math.atan2" in src or "math.cos" in src, (
            "Shotgun spread should use angle-based math (math.atan2/cos/sin)"
        )


class TestPickupOnCollideSignature:
    """P1-010: Base Pickup.on_collide should accept a player parameter."""

    def test_base_pickup_on_collide_accepts_player(self):
        import pickups
        sig = inspect.signature(pickups.Pickup.on_collide)
        params = list(sig.parameters.keys())
        assert len(params) >= 2, (
            "Pickup.on_collide should accept (self, player) but has params: %s "
            "(P1-010 bug)" % params
        )


class TestWallCollisionNoDamage:
    """P1-011: Wall collision should not run on_collide damage logic."""

    def test_wall_collision_calls_wallcollide_not_oncollide(self):
        """Player source should call wall_collide for staticSprites, not on_collide."""
        import player as player_module
        src = inspect.getsource(player_module.Player.update)
        # After the fix, wall collision uses wall_collide, not on_collide
        assert "wall_collide" in src or "wall_collide" in src, (
            "Player.update() should call wall_collide for wall collisions, "
            "not on_collide which applies damage (P1-011)"
        )

    def test_wall_collide_method_exists(self):
        """Player should have a wall_collide method for wall-only collision."""
        import player as player_module
        assert hasattr(player_module.Player, "wall_collide"), (
            "Player class should have a wall_collide method (P1-011)"
        )

    def test_wall_collide_does_not_subtract_hp(self):
        """wall_collide should not modify player.hp."""
        import player as player_module

        fake_surface = pygame.Surface((24, 32))
        p = object.__new__(player_module.Player)
        pygame.sprite.Sprite.__init__(p)
        p.image = fake_surface
        p.rect = fake_surface.get_rect()
        p.rect.center = (400, 300)
        p.hp = 100
        p.collideX = False
        p.collideY = False

        wall = mock.MagicMock()
        wall.rect = pygame.Rect(380, 280, 16, 16)
        wall.damage = 0

        p.wall_collide(wall)
        assert p.hp == 100, (
            "wall_collide reduced player hp from 100 to %d (P1-011)" % p.hp
        )


class TestGrenadeTimeIndependent:
    """P1-014: Grenade deceleration should accept dt parameter."""

    def test_grenade_update_accepts_dt(self):
        import sprites
        sig = inspect.signature(sprites.Grenade.update)
        params = list(sig.parameters.keys())
        assert "dt" in params, (
            "Grenade.update() should accept a dt parameter for time-independent "
            "deceleration (P1-014). Params: %s" % params
        )

    def test_grenade_deceleration_scales_with_dt(self):
        """At half dt, the grenade should decelerate half as much."""
        import sprites

        fake_surface = pygame.Surface((8, 8))

        def make_grenade():
            g = object.__new__(sprites.Grenade)
            pygame.sprite.Sprite.__init__(g)
            g.image = fake_surface
            g.rect = fake_surface.get_rect()
            g.rect.center = (400, 300)
            g.dir = (1, 0)
            g.speedX = 4.0
            g.speedY = 4.0
            g.timer = 0
            g.grenadeCook = 3
            g.damage = 100
            g.grenade = 1
            g.oldx = 400
            g.oldy = 300
            g.dx = 0
            g.dy = 0
            g.speedX_orig = 4.0
            return g

        empty_fire = pygame.sprite.Group()

        g1 = make_grenade()
        g1.update(empty_fire, dt=1.0)
        speed_normal = g1.speedX

        g2 = make_grenade()
        g2.update(empty_fire, dt=0.5)
        speed_half_dt = g2.speedX

        # With half dt, speed should decrease less
        assert speed_half_dt > speed_normal, (
            "Grenade at dt=0.5 (%.4f) should decelerate less than dt=1.0 (%.4f) "
            "(P1-014)" % (speed_half_dt, speed_normal)
        )


class TestLevelsImportRemoved:
    """P1-016: Levels import should be removed from main.py."""

    def test_no_levels_import_in_main(self):
        main_path = os.path.join(
            os.path.dirname(__file__), "..", "gameLib", "main.py"
        )
        with open(main_path) as f:
            source = f.read()

        # Check the import lines
        for line in source.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert "Levels" not in stripped, (
                    "main.py still imports Levels: '%s' (P1-016)" % stripped
                )
