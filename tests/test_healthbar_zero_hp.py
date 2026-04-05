"""
P1-006: HealthBar.update() passes player.hp directly as a pixel dimension.

Bug: In UI_HUD.HealthBar.update() (UI_HUD.py line 32):
    self.image = pygame.transform.scale(self.imageMaster, (self.player.hp, 16))

pygame.transform.scale() raises pygame.error when either dimension is < 1.
When player.hp == 0 (player dead), the call becomes scale(..., (0, 16))
which raises an error.

Fix: Clamp the width to at least 1 before passing to transform.scale, e.g.:
    width = max(1, self.player.hp)
    self.image = pygame.transform.scale(self.imageMaster, (width, 16))
"""
import pytest
import pygame
import unittest.mock as mock


def _make_health_bar(hp=100):
    """
    Build a HealthBar without loading real image files.
    """
    import UI_HUD

    fake_master = pygame.Surface((100, 16))
    fake_master.fill((255, 0, 0))

    player = mock.MagicMock()
    player.hp = hp

    bar = object.__new__(UI_HUD.HealthBar)
    bar.player = player
    bar.imageMaster = fake_master
    bar.image = fake_master.copy()
    bar.rect = bar.image.get_rect()
    bar.rect.center = (90, 8)
    return bar


class TestHealthBarZeroHp:
    """P1-006: HealthBar must handle hp=0 without pygame error."""

    def test_healthbar_update_at_zero_hp_raises_error(self):
        """
        BUG REPRODUCTION (P1-006): When player.hp == 0, HealthBar.update()
        calls pygame.transform.scale(master, (0, 16)).  pygame raises an
        error for a zero-width surface.

        This test FAILS on the current code (the error IS raised).
        After the fix (clamping width to >= 1), this test passes.
        """
        bar = _make_health_bar(hp=0)
        try:
            bar.update()
        except (pygame.error, ValueError) as exc:
            pytest.fail(
                "HealthBar.update() raised %s when player.hp=0: %s  "
                "Width must be clamped to >= 1 (P1-006 bug)"
                % (type(exc).__name__, exc)
            )

    def test_healthbar_update_produces_valid_surface_at_zero_hp(self):
        """
        After the fix, HealthBar.update() with hp=0 should produce an image
        with width >= 1 (not width == 0).
        """
        bar = _make_health_bar(hp=0)
        try:
            bar.update()
        except Exception:
            pass  # Let the previous test catch the crash

        # If update() succeeded, the resulting image must have valid dimensions
        assert bar.image.get_width() >= 1, (
            "HealthBar image width is %d after hp=0 update; must be >= 1 "
            "(P1-006 bug)" % bar.image.get_width()
        )

    def test_healthbar_update_works_normally_at_full_hp(self):
        """
        Sanity check: HealthBar.update() with hp=100 should work fine on
        both fixed and unfixed code.
        """
        bar = _make_health_bar(hp=100)
        bar.update()
        assert bar.image.get_width() == 100
