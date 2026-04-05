"""
P1-013: After the player dies, the game loop does not exit -- keepGoing stays
True indefinitely because the UI timer for 'GAME OVER' is never checked
against keepGoing in game.main_loop().

Bug: game.main_loop() has no logic to set keepGoing=False when the player
is dead and the UI timer has expired.  The `UI.update()` sprite changes its
text to "GAME OVER" but never signals the main loop to stop.

Fix: Check `if self.player1.dead:` in the main loop and exit when the UI
timer (or a separate death timer) reaches zero.
"""
import pytest
import pygame
import unittest.mock as mock


class TestGameOverReturnsToMenu:
    """P1-013: Player death must eventually cause the game loop to exit."""

    def test_player_death_flag_is_set_by_die(self):
        """
        Sanity check: Player.die() must set player.dead = True.
        """
        import player as player_module

        fake_surface = pygame.Surface((24, 32))
        p = object.__new__(player_module.Player)
        pygame.sprite.Sprite.__init__(p)
        p.image = fake_surface
        p.rect = fake_surface.get_rect()
        p.dead = False
        p.hp = 0

        p.die()

        assert p.dead is True, "Player.die() did not set player.dead = True"

    def test_game_loop_exits_when_player_is_dead(self):
        """
        BUG REPRODUCTION (P1-013): main_loop() source must contain a check
        for player1.dead that sets keepGoing = False.
        """
        import inspect
        import main as game_main

        source = inspect.getsource(game_main.game.main_loop)

        has_dead_check = "player1.dead" in source or "self.player1.dead" in source
        has_keepgoing_false = "keepGoing = False" in source or "keepGoing=False" in source

        assert has_dead_check and has_keepgoing_false, (
            "Game loop does not check player1.dead and set keepGoing=False.  "
            "main_loop() must exit after the death timer expires (P1-013 bug)"
        )

    def test_ui_timer_counts_down_when_player_dead(self):
        """
        The UI sprite's timer must count down when the player is dead.
        This is a prerequisite for the game knowing when to exit.
        Should pass on both fixed and unfixed code (the UI does count down).
        """
        import sprites

        fake_surface = pygame.Surface((24, 32))

        player = mock.MagicMock()
        player.dead = True
        player.pNum = 1
        player.stamina = 100
        player.gun = "Pistol"
        player.ammo = 9
        player.clips = 8
        player.grenade = 10

        ui = object.__new__(sprites.UI)
        ui.player = player
        ui.font = pygame.font.SysFont(None, 23)
        ui.time = 9
        ui.timer = 9 * 30  # 9 seconds * 30 fps
        ui.image = fake_surface
        ui.rect = fake_surface.get_rect()

        initial_timer = ui.timer
        ui.update()

        assert ui.timer < initial_timer, (
            "UI.timer did not decrease after player death; "
            "countdown must tick down each frame"
        )
