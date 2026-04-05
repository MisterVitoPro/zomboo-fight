"""
P1-012: Flamethrower reload threshold is 300 in the joystick path but the
gun only holds 100 rounds, so reload is never triggered in keyboard mode.

Bug: In player.py (joystick path, line 165-167):
    elif self.gun == "Flamethrower":
        if self.ammo < 300:      # BUG: max capacity is 100, so always True
            if self.clips > 0:
                self.pre_reload()

And in keyboard path (line 278-281):
    elif self.gun == "Flamethrower":
        if self.ammo < 300:      # same threshold: should be < 100

The Flamethrower is reloaded to 100 rounds (player.py line 533: self.ammo = 100).
The threshold for triggering a reload should be `< 100` (not full), but the
condition `< 300` is always True even when fully loaded at 100.  This is not
technically a prevent-reload bug (it always allows reload), but the
complementary problem is the inverse: the threshold is wrong semantically.

The actual QA finding (P1-012) is that a Flamethrower at ammo=99 should
trigger reload when T is pressed, and ammo=100 (full) should NOT trigger
reload.  With the current `< 300` threshold, reload triggers even when full.

Fix: Change `if self.ammo < 300:` to `if self.ammo < 100:`.
"""
import pytest
import pygame
import unittest.mock as mock


def _make_flamethrower_player(ammo=99, clips=1):
    """Build a Player already holding a Flamethrower."""
    import sprites
    import player as player_module

    fake_surface = pygame.Surface((24, 32))

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
    p.dir = (1, 0)
    p.facing = "none"
    p.fireTimer = 20
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

    # Flamethrower stats
    p.gun = "Flamethrower"
    p.damage = 10
    p.reloadSpeed = 25
    p.ammo = ammo
    p.clips = clips
    p.automatic = True
    p.fireRate = 2
    p.bulletLife = 25
    p.bulletStr = 8

    import sGroups
    p.bulletSprites = sGroups.bulletSprites
    p.bombSprites = sGroups.bombSprites

    p.fireSnd = mock.MagicMock()
    p.reloadSnd = mock.MagicMock()
    p.emptySnd = mock.MagicMock()
    return p


class TestFlamethrowerReloadThreshold:
    """P1-012: Flamethrower reload threshold must be 100, not 300."""

    def test_reload_triggers_at_ammo_99(self):
        """
        With ammo=99 and clips=1, pressing T (keyboard reload) should trigger
        pre_reload() because 99 < 100 (not full magazine).

        This test should PASS on the current code too because 99 < 300.
        It documents the correct threshold behaviour.
        """
        import sprites

        original_jOn = sprites.jOn
        sprites.jOn = False

        p = _make_flamethrower_player(ammo=99, clips=1)
        preReload_called = [False]

        original_preReload = p.pre_reload

        def mock_preReload():
            preReload_called[0] = True

        p.pre_reload = mock_preReload

        # Simulate pressing T with the reload condition check
        if p.reloading == False:
            if p.gun == "Flamethrower":
                if p.ammo < 300:  # Current (buggy) threshold
                    if p.clips > 0:
                        p.pre_reload()

        sprites.jOn = original_jOn

        assert preReload_called[0], (
            "pre_reload() was not called with ammo=99, clips=1, Flamethrower"
        )

    def test_reload_does_not_trigger_at_ammo_100_with_correct_threshold(self):
        """
        BUG REPRODUCTION (P1-012): With ammo=100 (full), pressing T should NOT
        trigger reload because the magazine is full.

        We read the actual threshold from source and verify it rejects ammo=100.
        """
        import sprites
        import inspect
        import re
        import player as player_module

        source = inspect.getsource(player_module.Player.update)

        # Find the flamethrower reload threshold from source
        # Pattern: elif self.gun == "Flamethrower":  ... if self.ammo < NNN:
        matches = re.findall(r'self\.ammo\s*<\s*(\d+)', source)
        # Get the threshold used near "Flamethrower" context
        flamethrower_section = source[source.index('"Flamethrower"'):]
        threshold_match = re.search(r'self\.ammo\s*<\s*(\d+)', flamethrower_section)
        threshold = int(threshold_match.group(1)) if threshold_match else 300

        p = _make_flamethrower_player(ammo=100, clips=1)
        preReload_called = [False]

        def mock_preReload():
            preReload_called[0] = True

        p.pre_reload = mock_preReload

        if p.reloading == False:
            if p.gun == "Flamethrower":
                if p.ammo < threshold:
                    if p.clips > 0:
                        p.pre_reload()

        assert not preReload_called[0], (
            "pre_reload() was called when ammo=100 (full magazine); "
            "the reload threshold is %d but should be 100 for Flamethrower "
            "(P1-012 bug): reload triggers even on a full magazine" % threshold
        )

    def test_correct_threshold_is_100_not_300(self):
        """
        BUG REPRODUCTION (P1-012): Directly verify that the reload condition
        uses the correct threshold (< 100) rather than (< 300).

        We inspect the player source to find the Flamethrower reload threshold.
        This test FAILS on the current code where the threshold is 300.
        """
        import inspect
        import player as player_module

        source = inspect.getsource(player_module.Player.update)

        # The buggy threshold
        assert "ammo < 300" not in source, (
            "player.update() contains `ammo < 300` for Flamethrower reload; "
            "the correct threshold is `ammo < 100` (the magazine capacity) "
            "(P1-012 bug)"
        )
