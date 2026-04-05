"""
P1-015: ZombieSpawner drifts on every update() call because center_rects()
uses random.randrange to set position every frame.

Bug: In zombieSpawn.ZombieSpawner.update() (zombieSpawn.py lines 27-34),
the spawner's rect is repositioned by center_rects() on every frame:
    def center_rects(self, x, y):
        rangex = (x - 10)
        rangey = (y - 10)
        self.rect.centerx = random.randrange(rangex, x)
        self.rect.centery = random.randrange(rangey, y)

This means the spawner icon jitters by up to 10 pixels every frame (30fps).
The position should be fixed at the assigned corner for the spawner's lifetime.

Fix: Call center_rects() only once (in __init__), not on every update().
"""
import pytest
import pygame
import unittest.mock as mock


def _make_spawner(spawn_quadrant=1):
    """
    Build a ZombieSpawner without loading real image files.
    """
    import zombieSpawn

    fake_surface = pygame.Surface((16, 16))

    spawner = object.__new__(zombieSpawn.ZombieSpawner)
    spawner.image = fake_surface
    spawner.rect = fake_surface.get_rect()
    spawner.spawn = spawn_quadrant
    spawner.timer = 0
    spawner.timerEnd = 10 * 30  # 10 seconds
    spawner.transColor = (0, 0, 0, 255)

    # Set initial position as center_rects would for quadrant 1
    spawner.rect.centerx = 35
    spawner.rect.centery = 25
    return spawner


class TestSpawnerStablePosition:
    """P1-015: ZombieSpawner position must not change on every update()."""

    def test_spawner_position_changes_every_frame(self):
        """
        BUG REPRODUCTION (P1-015): The spawner calls center_rects() on every
        update(), which calls random.randrange() to set a new position.

        We run update() 10 times and collect positions.  With the bug, the
        position is different on (most) frames.  After the fix, it stays
        constant.

        This test FAILS after the fix (the position becomes stable).
        As a RED test it confirms the bug by asserting position CHANGES.

        We invert this: assert the position is STABLE, which FAILS on current
        buggy code.
        """
        spawner = _make_spawner(spawn_quadrant=1)

        positions = []
        for _ in range(10):
            spawner.update()
            positions.append((spawner.rect.centerx, spawner.rect.centery))

        unique_positions = set(positions)
        # With the bug: multiple distinct positions (randrange jitter)
        # After fix: exactly one position (set once in __init__)
        assert len(unique_positions) == 1, (
            "Spawner position changed across 10 update() calls: %s  "
            "center_rects() is being called every frame instead of only once "
            "during initialisation (P1-015 bug)" % unique_positions
        )

    def test_spawner_stays_in_assigned_corner_quadrant1(self):
        """
        For spawn==1 (top-left, x=40, y=30), the spawner must stay near (40, 30).
        With the bug the position drifts randomly within [30-40] x [20-30].
        After the fix the position is determined once and stays there.

        This is a weaker stability test -- it passes if position stays in range.
        """
        spawner = _make_spawner(spawn_quadrant=1)

        for _ in range(10):
            spawner.update()

        # Quadrant 1: center_rects(40, 30) -> x in [30, 40), y in [20, 30)
        assert 25 <= spawner.rect.centerx <= 45, (
            "Spawner x=%d out of expected range [25, 45] for quadrant 1" % spawner.rect.centerx
        )
        assert 15 <= spawner.rect.centery <= 35, (
            "Spawner y=%d out of expected range [15, 35] for quadrant 1" % spawner.rect.centery
        )

    def test_spawner_initial_position_is_set_in_init(self):
        """
        BUG REPRODUCTION (P1-015): The spawner's position should be set
        once in __init__ via center_rects().  Currently __init__ does NOT
        call center_rects() -- position is only set in update().  This means
        on frame 0 the spawner has no position (left at (0, 0) from get_rect()).

        This test FAILS on the current code because __init__ never calls
        center_rects().
        """
        import zombieSpawn

        fake_surface = pygame.Surface((16, 16))

        with mock.patch("pygame.image.load", return_value=fake_surface):
            spawner = zombieSpawn.ZombieSpawner(21)

        # After __init__, the position should already be in the assigned corner
        # Quadrant 1 (spawn=1): x near 40, y near 30
        # Quadrant 2 (spawn=2): x near 760, y near 560
        # Quadrant 3 (spawn=3): x near 30, y near 560
        # Quadrant 4 (spawn=4): x near 760, y near 40

        # The spawner should NOT be at the default rect origin (0, 0)
        # because center_rects() should have been called during __init__
        at_origin = (spawner.rect.centerx == 0 and spawner.rect.centery == 0)
        assert not at_origin, (
            "Spawner position is still at (0, 0) after __init__.  "
            "center_rects() is not being called in __init__, only in update().  "
            "The spawner has no position on the first frame (P1-015 bug)."
        )
