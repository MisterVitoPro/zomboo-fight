# D:/workspace/zomboo-fight/tests/test_bullet_double_decrement.py
"""
Tests for:
  P1-003: Bullet strength decremented twice on collision (once fixed + once by bulletResist)
"""
import pytest
import pygame
import unittest.mock as mock


def _make_minimal_bullet(bulletStr=3, gun="Pistol"):
    """Build a Bullet via object.__new__ without asset loading."""
    import sprites

    fake_surface = pygame.Surface((8, 8))
    b = object.__new__(sprites.Bullet)
    pygame.sprite.Sprite.__init__(b)
    b.image = fake_surface
    b.rect = fake_surface.get_rect()
    b.rect.center = (400, 300)
    b.gun = gun
    b.damage = 20
    b.pos = (400, 300)
    b.dir = (1, 0)
    b.speed = 10
    b.timer = 0
    b.bulletLife = 45
    b.bulletStr = bulletStr
    b.bulletResist = 0
    b.splatSprites = pygame.sprite.Group()
    b.fireSprites = pygame.sprite.Group()
    return b


def _make_zombie_collider(bulletResist=1):
    """Build a minimal zombie-like collider with the given bulletResist."""
    collider = mock.MagicMock()
    collider.bulletResist = bulletResist
    collider.damage = 0
    return collider


class TestBulletDoubleDecrement:
    """P1-003: Bullet.on_collide must only decrement by collider.bulletResist, not by 1 extra."""

    def test_bullet_loses_only_bulletresist_per_hit(self):
        """
        BUG REPRODUCTION (P1-003): Bullet.on_collide() does:
            self.bulletStr -= 1               # first decrement
            ...
            self.bulletStr -= collider.bulletResist  # second decrement

        With bulletStr=3 and bulletResist=1, expected result is 3-1=2, but
        current code produces 3-1-1=1.
        This test FAILS on current code.
        """
        import sprites

        fake_surface = pygame.Surface((8, 8))
        bullet = _make_minimal_bullet(bulletStr=3)
        zombie = _make_zombie_collider(bulletResist=1)

        with mock.patch("pygame.image.load", return_value=fake_surface):
            bullet.on_collide(zombie)

        assert bullet.bulletStr == 2, (
            "bullet.bulletStr is %d after one collision with bulletResist=1; "
            "expected 2 (3 - 1 = 2).  Current code decrements twice: "
            "once fixed (-1) then once by bulletResist (-1) = 3-1-1=1 (P1-003 bug)"
            % bullet.bulletStr
        )

    def test_bullet_survives_one_hit_with_strength_two(self):
        """
        BUG REPRODUCTION (P1-003): A bullet with bulletStr=2 hitting a zombie
        with bulletResist=1 should survive with bulletStr=1.
        Current code: 2-1-1=0 kills the bullet.  After fix: 2-1=1, bullet lives.
        This test FAILS on current code.
        """
        import sprites

        fake_surface = pygame.Surface((8, 8))
        bullet = _make_minimal_bullet(bulletStr=2)
        zombie = _make_zombie_collider(bulletResist=1)

        bullet_group = pygame.sprite.Group()
        bullet_group.add(bullet)

        with mock.patch("pygame.image.load", return_value=fake_surface):
            bullet.on_collide(zombie)

        assert bullet.alive(), (
            "Bullet with bulletStr=2 was killed by one hit from bulletResist=1 zombie; "
            "2-1=1 should survive, but current code does 2-1-1=0 (P1-003 bug)"
        )

    def test_bullet_dies_when_bulletstr_exactly_zero(self):
        """
        After the fix: a bullet with bulletStr=1 hitting bulletResist=1 should die.
        1 - 1 = 0 -> die().  This should pass on both old and fixed code
        (old code: 1-1-1=-1 also calls die()).
        """
        import sprites

        fake_surface = pygame.Surface((8, 8))
        bullet = _make_minimal_bullet(bulletStr=1)
        zombie = _make_zombie_collider(bulletResist=1)

        bullet_group = pygame.sprite.Group()
        bullet_group.add(bullet)

        with mock.patch("pygame.image.load", return_value=fake_surface):
            bullet.on_collide(zombie)

        assert not bullet.alive(), (
            "Bullet with bulletStr=1 should die after one hit from bulletResist=1 "
            "(1 - 1 = 0 -> die())"
        )

    def test_on_collide_source_has_single_decrement(self):
        """
        Inspect source to confirm the double-decrement has been removed.
        Asserts that `self.bulletStr -= 1` appears at most once in on_collide,
        and is always the combined `collider.bulletResist` form.
        This test FAILS on current code.
        """
        import inspect
        import sprites

        source = inspect.getsource(sprites.Bullet.on_collide)

        # After fix: `self.bulletStr -= 1` (bare) should not appear as a
        # standalone line separate from the bulletResist decrement
        lines = [l.strip() for l in source.split("\n")]
        bare_decrements = [l for l in lines if l == "self.bulletStr -= 1"]

        assert len(bare_decrements) == 0, (
            "Bullet.on_collide() still contains `self.bulletStr -= 1` as a bare "
            "decrement separate from `self.bulletStr -= collider.bulletResist`. "
            "Found %d occurrence(s). Remove the bare decrement (P1-003 bug)" % len(bare_decrements)
        )
