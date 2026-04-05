# D:/workspace/zomboo-fight/tests/test_flamethrower_clips.py
"""
Tests for:
  P1-004: FlameThrower pickup has clips=0 making reload impossible
  P1-005: Pistol infinite ammo (clips restored on reload -- documents intentional design)
  P3-002: Medkit overheals without immediate cap
"""
import pytest
import pygame
import unittest.mock as mock


class TestFlameThrowerClips:
    """P1-004: FlameThrower must ship with a non-zero clip count."""

    def test_flamethrower_pickup_clips_is_nonzero(self):
        """
        BUG REPRODUCTION (P1-004): FlameThrower.__init__() sets self.clips = 0.
        This means a player who picks up the flamethrower can never reload it
        (all reload paths require `self.clips > 0`).
        This test FAILS on current code where clips=0.
        """
        import pickups

        fake_surface = pygame.Surface((24, 32))

        with mock.patch("pygame.image.load", return_value=fake_surface), \
             mock.patch("pygame.mixer.Sound", return_value=mock.MagicMock()):
            ft = pickups.FlameThrower.__new__(pickups.FlameThrower)
            ft.clips = 0   # simulate current bug state
            # Now call the actual assignment from __init__ inline to test
            # We test the attribute directly after full init
            ft2 = object.__new__(pickups.FlameThrower)
            ft2.clips = 0   # default before init

        # Re-instantiate using proper mocks
        with mock.patch("pygame.image.load", return_value=fake_surface), \
             mock.patch("pygame.mixer.Sound", return_value=mock.MagicMock()), \
             mock.patch("pygame.transform.rotate", return_value=fake_surface), \
             mock.patch("gameLib.pickups.level_LOC") if False else mock.patch("level_LOC.bottomWeaponSpawn", (400, 500)):
            pass

        # Direct attribute inspection of the class default
        import inspect
        import pickups as pickups_module

        source = inspect.getsource(pickups_module.FlameThrower.__init__)

        assert "self.clips = 0" not in source, (
            "FlameThrower.__init__() sets self.clips = 0; "
            "the flamethrower can never be reloaded because all reload paths "
            "require self.clips > 0 (P1-004 bug)"
        )

    def test_flamethrower_reload_possible_after_pickup(self):
        """
        After the fix (clips > 0), a player holding a FlameThrower with ammo < 100
        and clips > 0 must be able to call pre_reload() via the reload condition.
        """
        import inspect
        import pickups as pickups_module

        source = inspect.getsource(pickups_module.FlameThrower.__init__)

        # Find what clips is set to
        import re
        match = re.search(r"self\.clips\s*=\s*(\d+)", source)
        assert match is not None, "Could not find self.clips assignment in FlameThrower.__init__"

        clips_value = int(match.group(1))
        assert clips_value > 0, (
            "FlameThrower sets clips=%d; must be > 0 for reload to be possible "
            "(P1-004 bug)" % clips_value
        )

    def test_flamethrower_ammo_is_100(self):
        """Regression: FlameThrower must start with 100 ammo (should always pass)."""
        import inspect
        import pickups as pickups_module
        import re

        source = inspect.getsource(pickups_module.FlameThrower.__init__)
        match = re.search(r"self\.ammo\s*=\s*(\d+)", source)
        assert match is not None, "No self.ammo assignment found in FlameThrower.__init__"
        ammo_value = int(match.group(1))
        assert ammo_value == 100, (
            "FlameThrower ammo is %d; expected 100" % ammo_value
        )


class TestPistolInfiniteAmmo:
    """P1-005: Documents that pistol clips are restored on reload (intentional infinite fallback)."""

    def test_pistol_reload_restores_clips(self):
        """
        DESIGN DOCUMENTATION TEST (P1-005): player.reload("Pistol") increments
        self.clips back up after spending one, effectively giving infinite pistol
        ammo.  This test documents the CURRENT intended behaviour.
        If the design changes to finite pistol clips, update this test.
        """
        import player as player_module

        p = object.__new__(player_module.Player)
        p.reloadTime = 0
        p.clips = 3
        p.reloading = True

        p.reload("Pistol")

        # clips was decremented by 1 then incremented by 1 = net 0 change
        assert p.clips == 3, (
            "After pistol reload, clips should be unchanged (decremented then "
            "restored = net 0).  Got clips=%d.  This documents the intentional "
            "infinite pistol design (P1-005)" % p.clips
        )

    def test_pistol_ammo_set_to_9_after_reload(self):
        """Pistol reload must restore ammo to 9."""
        import player as player_module

        p = object.__new__(player_module.Player)
        p.reloadTime = 0
        p.clips = 3
        p.reloading = True
        p.ammo = 0

        p.reload("Pistol")

        assert p.ammo == 9, (
            "Pistol reload should set ammo to 9, got %d" % p.ammo
        )


class TestMedkitOverheal:
    """P3-002: Medkit should not push HP above the game's overheal maximum."""

    def test_medkit_does_not_push_hp_above_150(self):
        """
        P3-002: Medkit.on_collide() does `player.hp += 40` with no cap.
        A player at hp=140 would reach hp=180, exceeding the 150 cap that
        player.update() enforces lazily.  The pickup itself should cap hp.
        This test FAILS on current code where no cap exists in on_collide.
        """
        import pickups

        player = mock.MagicMock()
        player.hp = 140

        # Build a minimal Medkit without image loading
        medkit = object.__new__(pickups.Medkit)
        medkit.addHp = 40

        # Patch kill() so the sprite removal doesn't fail
        medkit.kill = mock.MagicMock()

        medkit.on_collide(player)

        # After fix: hp capped at 150
        assert player.hp <= 150, (
            "player.hp is %d after medkit pickup from 140 hp; "
            "should be capped at 150 (P3-002 bug: no cap in Medkit.on_collide)" % player.hp
        )

    def test_medkit_normal_heal_unaffected(self):
        """
        Regression: a player at hp=60 picking up a medkit (addHp=40) should
        reach hp=100 without any cap interference.
        """
        import pickups

        player = mock.MagicMock()
        player.hp = 60

        medkit = object.__new__(pickups.Medkit)
        medkit.addHp = 40
        medkit.kill = mock.MagicMock()

        medkit.on_collide(player)

        assert player.hp == 100, (
            "player.hp is %d after medkit from hp=60; expected 100" % player.hp
        )
