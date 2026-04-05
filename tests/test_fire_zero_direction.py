"""
P1-007: Player.fire() is called with dir=(0, 0) in keyboard mode.

Bug: Player.__init__ sets self.dir = (0, 0).  In keyboard mode (jOn=False),
if the player has not pressed any direction key yet, self.dir remains (0, 0).
Player.fire() then creates a Bullet with dir=(0, 0), which means the bullet
never moves (speedX=0 * 10=0, speedY=0 * 10=0).  The bullet sits on top of
the player and damages whatever collides there.

Fix: Either guard fire() to prevent firing when dir==(0,0), or initialise
dir to a sensible default (e.g. (1, 0) = facing right).
"""
import pytest
import pygame
import unittest.mock as mock


def _make_player_keyboard_mode():
    """
    Build a minimal Player in keyboard/no-joystick mode without full init.
    """
    import sprites
    import player as player_module

    fake_surface = pygame.Surface((24, 32))

    original_jOn = sprites.jOn
    sprites.jOn = False

    p = object.__new__(player_module.Player)
    p.pNum = 1
    p.j = None
    p.image = fake_surface
    p.rect = fake_surface.get_rect()
    p.rect.center = (400, 300)
    p.dead = False
    p.hp = 100
    p.stamina = 100
    p.staminaLow = 0
    p.grenade = 10
    p.dx = 5
    p.dy = 5
    p.speedX = 0
    p.speedY = 0
    p.sprintSpeed = 1
    p.dir = (0, 0)  # The buggy initial value
    p.facing = "none"
    p.fireTimer = 20  # Ensure fireTimer >= fireRate so firing is allowed
    p.godMode = False
    p.timerGodmode = 0
    p.timerHP = 0
    p.timerPos = 0
    p.gTimer = 0
    p.staminaTimer = 0
    p.staminaTimerUp = 0
    p.fireStateTimer = 0
    p.gTime = 15
    p.reloadTime = 0
    p.reloading = False
    p.fireState = False
    p.collideX = False
    p.collideY = False
    p.gun = "Pistol"
    p.damage = 20
    p.reloadSpeed = 15
    p.ammo = 9
    p.clips = 8
    p.automatic = False
    p.fireRate = 10
    p.bulletLife = 45
    p.bulletStr = 2

    import sGroups
    p.bulletSprites = sGroups.bulletSprites
    p.bombSprites = sGroups.bombSprites

    # Mock sounds
    p.fireSnd = mock.MagicMock()
    p.reloadSnd = mock.MagicMock()
    p.emptySnd = mock.MagicMock()

    return p, original_jOn


class TestFireZeroDirection:
    """P1-007: Firing with dir=(0,0) should either be prevented or produce
    a moving bullet."""

    def test_fire_with_zero_direction_produces_stationary_bullet(self):
        """
        BUG REPRODUCTION (P1-007): When player.dir == (0, 0) and fire() is
        called, either no bullet should be created, or it should have non-zero
        velocity. The fix blocks fire with (0,0) direction.
        """
        import sprites
        import sGroups

        original_jOn = sprites.jOn
        sprites.jOn = False

        fake_surface = pygame.Surface((8, 8))
        p, _ = _make_player_keyboard_mode()

        initial_bullet_count = len(sGroups.bulletSprites)

        with mock.patch("pygame.image.load", return_value=fake_surface):
            p.fire((0, 0))

        bullets = list(sGroups.bulletSprites)
        new_bullets = bullets[initial_bullet_count:]

        # After fix: either no bullet created, or all bullets have non-zero dir
        for bullet in new_bullets:
            bullet_velocity = (bullet.dir[0] * bullet.speed, bullet.dir[1] * bullet.speed)
            is_stationary = bullet_velocity == (0, 0)
            assert not is_stationary, (
                "Bullet created with zero velocity (dir=%r) when player.dir=(0,0); "
                "fire() should be blocked or default direction should be non-zero "
                "(P1-007 bug)" % (bullet.dir,)
            )

        sprites.jOn = original_jOn

    def test_fire_is_blocked_or_has_nonzero_direction_in_keyboard_mode(self):
        """
        After the fix, calling fire((0, 0)) in keyboard mode should either:
        (a) not add any bullet to bulletSprites, OR
        (b) add a bullet with non-zero dir.

        This test FAILS on the current code because it adds a zero-dir bullet.
        """
        import sprites
        import sGroups

        original_jOn = sprites.jOn
        sprites.jOn = False

        fake_surface = pygame.Surface((8, 8))
        p, _ = _make_player_keyboard_mode()

        with mock.patch("pygame.image.load", return_value=fake_surface):
            p.fire((0, 0))

        bullets = list(sGroups.bulletSprites)

        if len(bullets) == 0:
            # Fire was correctly blocked -- test passes
            sprites.jOn = original_jOn
            return

        for bullet in bullets:
            assert bullet.dir != (0, 0), (
                "Bullet has zero direction %r; firing with dir=(0,0) must "
                "be blocked or redirected to a sensible default (P1-007 bug)"
                % (bullet.dir,)
            )

        sprites.jOn = original_jOn
