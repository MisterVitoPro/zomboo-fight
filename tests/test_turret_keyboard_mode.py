"""
P1-005: Turret.update() crashes with TypeError when no joystick is connected.

Fix: Initialise self.dir as a tuple, e.g. self.dir = (0, -1).
"""
import pytest
import unittest.mock as mock
import pygame
import inspect
import re


class TestTurretKeyboardMode:
    """P1-005: Turret must not crash when no joystick is connected."""

    def _get_turret_init_dir(self):
        """Read the actual self.dir value from Turret.__init__ source."""
        import sprites
        src = inspect.getsource(sprites.Turret.__init__)
        m = re.search(r'self\.dir\s*=\s*(.+)', src)
        if m:
            return eval(m.group(1).strip())
        return 0

    def test_turret_update_no_joystick_no_type_error(self):
        """With jOn=False, Turret.update() must not crash."""
        import sprites

        original_jOn = sprites.jOn
        sprites.jOn = False

        try:
            fake_surface = pygame.Surface((32, 32))
            with mock.patch("pygame.image.load", return_value=fake_surface):
                turret = sprites.Turret.__new__(sprites.Turret)
                pygame.sprite.Sprite.__init__(turret)
                turret.image = fake_surface
                turret.imageC = fake_surface
                turret.rect = fake_surface.get_rect()
                turret.rect.center = (400, 300)
                turret.dir = self._get_turret_init_dir()
                turret.fireTimer = 0
                turret.fireSet = 100
                turret.damage = 60
                turret.angle = 0
                turret.timer = 0

            try:
                turret.update()
            except TypeError as exc:
                pytest.fail(
                    "Turret.update() raised TypeError when jOn=False: %s  "
                    "self.dir is initialised as integer 0 instead of a tuple "
                    "(P1-005 bug)" % exc
                )
        finally:
            sprites.jOn = original_jOn

    def test_turret_dir_initial_value_is_tuple(self):
        """Turret.__init__ must set self.dir to a tuple."""
        dir_val = self._get_turret_init_dir()

        assert isinstance(dir_val, tuple), (
            "Turret.dir is %r (type %s) after __init__; expected a tuple "
            "so calc_vector() can do dir[0] and dir[1] without TypeError "
            "(P1-005 bug)" % (dir_val, type(dir_val).__name__)
        )

    def test_calcrector_works_with_tuple_dir(self):
        """calc_vector must work with a tuple dir."""
        import sprites

        fake_surface = pygame.Surface((32, 32))
        with mock.patch("pygame.image.load", return_value=fake_surface):
            turret = sprites.Turret.__new__(sprites.Turret)
            turret.dir = (1, 0)
            turret.angle = 0

        turret.calc_vector((1, 0))
        assert turret.angle == pytest.approx(270.0, abs=0.1)
