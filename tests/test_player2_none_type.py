"""
P0-001: player2 is initialised as the string "none" instead of Python None.

Bug: In game.make_sprites() (main.py line 126):
    self.player2 = "none"

This means downstream checks like `if self.player2 is None` evaluate to False
even in single-player mode, and any code that tries to access attributes on
the string "none" (e.g. player2.rect) will raise AttributeError.

Additionally Zombie.update() (sprites.py line 392) does:
    Dist1 = (self.rect.centerx - player2.rect.centerx, ...)
when jCount == 2, but with a single joystick (jCount == 1) it takes the else
branch and only references player1.  In single-player mode player2="none"
is passed in from main.update_groups(), so the string "none" is used as a
player object.  If jCount were forced to 2 this would immediately crash.
"""
import os
import sys
import types
import pytest
import pygame
import unittest.mock as mock


class TestPlayer2IsNoneNotString:
    """P0-001: self.player2 should be None, not the string 'none'."""

    def test_player2_is_none_not_string_in_single_player(self):
        """
        BUG REPRODUCTION: game.make_sprites() assigns self.player2 = "none"
        (a string).  In single-player mode (jCount != 2), player2 should be
        Python None so that callers can safely test `if player2 is None`.
        """
        import main as game_main
        import sprites

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            # Patch main_loop so it returns immediately, but let make_sprites run
            with mock.patch.object(game_main.game, "main_loop", return_value=None):
                fake_image = pygame.Surface((24, 32))
                with mock.patch("pygame.image.load", return_value=fake_image), \
                     mock.patch("pygame.mixer.Sound", return_value=mock.MagicMock()):
                    g = game_main.game()

            assert g.player2 is None, (
                "game.player2 was %r (type %s) instead of None; "
                "make_sprites() assigns the string 'none' rather than Python None "
                "(P0-001 bug)" % (g.player2, type(g.player2).__name__)
            )
        finally:
            sprites.jCount = original_jcount

    def test_zombie_update_with_none_player2_no_attribute_error(self):
        """
        When player2 is None (correct) and jCount == 1 (single player),
        Zombie.update() should run without AttributeError.

        With the current 'none' string bug: if code accidentally evaluates
        jCount==2 and then calls player2.rect, it raises AttributeError on
        the string "none".  We test the safer invariant: calling
        Zombie.update() with player2=None must not raise.
        """
        import sprites
        import sGroups

        # Temporarily override jCount so the single-player branch is taken
        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            # Build minimal mocks so we can construct a Zombie
            fake_image = pygame.Surface((24, 32))
            pos = (400, 300)

            # Patch pygame.image.load for GameObject.__init__
            with mock.patch("pygame.image.load", return_value=fake_image):
                with mock.patch("pygame.mixer.Sound"):
                    zombie = sprites.Zombie.__new__(sprites.Zombie)
                    # Manually set required attrs to avoid full __init__ chain
                    zombie.image = fake_image
                    zombie.rect = fake_image.get_rect()
                    zombie.rect.center = pos
                    zombie.hp = 60
                    zombie.damage = 25
                    zombie.dx = 0
                    zombie.dy = 0
                    zombie.dxPlayer = 0
                    zombie.dyPlayer = 0
                    zombie.speedX = 2
                    zombie.speedY = 2
                    zombie.delay = 0
                    zombie.timer = 0
                    zombie.pause = 0
                    zombie.dir = "none"
                    zombie.animDelay = 10
                    zombie.wander_offset = 0.0
                    zombie.wander_speed = 2.0
                    zombie.wander_strength = 0.0
                    zombie.steer_speed = 0.08
                    zombie.moving = False
                    zombie.state = None
                    zombie.oldx = pos[0]
                    zombie.oldy = pos[1]
                    zombie.oldxy = pos
                    zombie.oldxy2 = pos
                    zombie.frame = 0
                    zombie.MOVE_N = 0
                    zombie.MOVE_NE = 1
                    zombie.MOVE_E = 2
                    zombie.MOVE_SE = 3
                    zombie.MOVE_S = 4
                    zombie.MOVE_SW = 5
                    zombie.MOVE_W = 6
                    zombie.MOVE_NW = 7
                    zombie.NORTH = [fake_image]
                    zombie.SOUTH = [fake_image]
                    zombie.EAST = [fake_image]
                    zombie.WEST = [fake_image]

                    # Build a minimal player1 mock
                    player1 = mock.MagicMock()
                    player1.rect.centerx = 200
                    player1.rect.centery = 200
                    player1.oldxy2 = (200, 200)

                    empty_group = pygame.sprite.Group()

                    # player2 = None is the CORRECT value after the fix;
                    # passing None must not crash in single-player mode.
                    try:
                        zombie.update(empty_group, empty_group, player1, None)
                    except AttributeError as exc:
                        pytest.fail(
                            "Zombie.update() raised AttributeError when "
                            "player2=None: %s  (P0-001 bug)" % exc
                        )
        finally:
            sprites.jCount = original_jcount
