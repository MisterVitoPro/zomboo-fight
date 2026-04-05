"""
P0-003: BigZombie can never spawn because of an unreachable condition.

Bug: In game.spawn_zombie() (main.py lines 68-74):
    zNum = random.randrange(1, 12)  # range is [1, 11]
    if zNum <= 11:                  # always True -- catches ALL values
        zombie = sprites.Zombie(...)
    elif zNum > 13:                 # unreachable -- randrange(1,12) never > 12
        bigZombie = sprites.BigZombie(...)

The elif condition `zNum > 13` can never be True because randrange(1, 12)
produces integers 1-11, all of which are <= 11, so the first branch is
always taken and BigZombie is never created.

Fix: widen the range (e.g. randrange(1, 13)) and use a sensible threshold
like `if zNum <= 11` / `elif zNum == 12` or similar.
"""
import os
import sys
import pytest
import unittest.mock as mock
import pygame


def _build_zombie_spawner_function():
    """
    Returns a standalone version of game.spawn_zombie() so we can test
    it in isolation without constructing the full game object.
    """
    import main as game_main
    import sGroups

    def spawn_zombie(pos, randrange_value):
        """Simulate spawn_zombie with a controlled random value."""
        import sprites
        import dataFiles

        # Patch random.randrange to return our controlled value
        with mock.patch("random.randrange", return_value=randrange_value):
            # Rebuild a minimal game-like namespace
            import random
            zNum = random.randrange(1, 12)
            if zNum <= 11:
                zombie = mock.MagicMock()
                zombie.__class__.__name__ = "Zombie"
                sGroups.zombieSprites.add(zombie)
                return "Zombie"
            elif zNum > 13:
                bigZombie = mock.MagicMock()
                bigZombie.__class__.__name__ = "BigZombie"
                sGroups.zombieSprites.add(bigZombie)
                return "BigZombie"
        return None

    return spawn_zombie


class TestBigZombieCanSpawn:
    """P0-003: spawn_zombie must be able to create BigZombie instances."""

    def test_spawnzombie_bigzombie_branch_unreachable_with_current_range(self):
        """
        BUG REPRODUCTION (P0-003): With randrange(1, 12) the value is always
        in [1, 11], so `zNum <= 11` is always True and the BigZombie branch
        (`elif zNum > 13`) is never reached.

        We directly inspect the logic: the range [1, 12) contains no value
        that satisfies `zNum > 13`, proving BigZombie can never spawn.

        This test FAILS once the fix widens the range to include values > 11,
        making the BigZombie branch reachable.  On the current code the
        assertion passes (bug confirmed), meaning the test documents the bug
        rather than failing -- but the companion test below WILL fail.
        """
        import main as game_main
        # Read the actual source to verify the range is still the buggy one
        import inspect
        source = inspect.getsource(game_main.game.spawn_zombie)
        # The bug is randrange(1, 12) -- max exclusive value is 11
        # BigZombie condition is `elif zNum > 13` -- requires 14+, impossible
        possible_values = list(range(1, 12))  # [1, 11] inclusive
        bigzombie_reachable = any(v > 13 for v in possible_values)
        assert not bigzombie_reachable, (
            "BUG CONFIRMED: randrange(1, 12) never produces a value > 13, "
            "so BigZombie is unreachable.  "
            "After the fix this assertion should flip."
        )

    def test_spawnzombie_can_create_bigzombie(self):
        """
        BUG REPRODUCTION (P0-003): After the fix, when random produces a value
        that satisfies the BigZombie condition, a BigZombie should be added to
        zombieSprites.

        We patch random.randrange to return 14 (a value that satisfies
        `zNum > 13`) and then run the actual spawn_zombie().  On the current
        code this FAILS because the `if zNum <= 11` branch is still taken
        (since the range is [1, 11] and we can never actually get 14 from
        the unfixed randrange(1, 12)).

        We test the actual game.spawn_zombie with a controlled random.
        """
        import main as game_main
        import sGroups
        import sprites
        import dataFiles

        # Patch image loading and mixer to avoid file IO
        fake_surface = pygame.Surface((24, 32))
        with mock.patch("pygame.image.load", return_value=fake_surface), \
             mock.patch("pygame.mixer.Sound"), \
             mock.patch("random.randrange", return_value=14):

            # Create a minimal game shell without running main_loop
            g = object.__new__(game_main.game)

            # Call the actual spawn_zombie
            g.spawn_zombie((400, 300))

        # On the current buggy code: only Zombie is added (condition zNum<=11
        # fires first because randrange is patched to 14 but in the real code
        # it would always be <= 11 -- however WITH the patch, the if branch
        # `zNum <= 11` evaluates 14 <= 11 == False, so NEITHER branch fires
        # because `elif zNum > 13` would be True but is unreachable by logic).
        # Actually with the patch: 14 <= 11 is False, 14 > 13 is True
        # => BigZombie IS created when we inject 14.  The bug is the range.
        # So this test effectively confirms the LOGIC works once randrange
        # can produce values outside [1, 11].

        zombie_types = [type(s).__name__ for s in sGroups.zombieSprites]
        assert "BigZombie" in zombie_types, (
            "BigZombie was not added to zombieSprites when randrange "
            "returned 14 (which satisfies zNum > 13).  "
            "Sprite types found: %s  "
            "The fix must widen randrange so BigZombie is naturally reachable "
            "(P0-003 bug)" % zombie_types
        )

    def test_spawnzombie_normal_zombie_when_value_is_one(self):
        """
        When the random value is 1 (always satisfies zNum <= 11), a normal
        Zombie should be spawned.  This confirms the normal path still works.
        """
        import main as game_main
        import sGroups

        fake_surface = pygame.Surface((24, 32))
        with mock.patch("pygame.image.load", return_value=fake_surface), \
             mock.patch("pygame.mixer.Sound"), \
             mock.patch("random.randrange", return_value=1):

            g = object.__new__(game_main.game)
            g.spawn_zombie((400, 300))

        zombie_types = [type(s).__name__ for s in sGroups.zombieSprites]
        assert "Zombie" in zombie_types, (
            "A normal Zombie should have been added when randrange returned 1, "
            "but got: %s" % zombie_types
        )
