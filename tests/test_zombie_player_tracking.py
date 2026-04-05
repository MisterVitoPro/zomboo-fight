"""
P1-004: Zombie tracks player's OLD position (oldxy2) instead of current position.

Bug: In sprites.Zombie.update() the zombie steers toward player1.oldxy2 --
a position that is only updated every 180 frames (player.py line 99):
    if self.timerPos >= 180:
        self.oldxy2 = self.oldxy

This means the zombie chases a 6-second-old ghost position, not the actual
player.  A zombie spawned when timerPos < 180 is tracking (0, 0) because
oldxy2 is never initialised (the Player.__init__ at line 34 sets
`self.dir = (0, 0)` but oldxy2 is only assigned inside the timerPos block).

Fix: Use player1.rect.center for steering (the real-time position) rather
than player1.oldxy2.
"""
import pytest
import unittest.mock as mock
import pygame


def _make_minimal_zombie(pos=(400, 300)):
    """
    Build a Zombie with the minimum attributes required to call update()
    without hitting asset-loading code.
    """
    import sprites

    fake_image = pygame.Surface((24, 32))
    z = object.__new__(sprites.Zombie)
    z.image = fake_image
    z.rect = fake_image.get_rect()
    z.rect.center = pos
    z.hp = 60
    z.damage = 25
    z.dx = 0
    z.dy = 0
    z.dxPlayer = 0
    z.dyPlayer = 0
    z.speedX = 2
    z.speedY = 2
    z.delay = 0
    z.timer = 0
    z.pause = 0
    z.animDelay = 10
    z.moving = False
    z.state = None
    z.oldx = pos[0]
    z.oldy = pos[1]
    z.oldxy = pos
    z.oldxy2 = pos
    z.frame = 0
    z.MOVE_N = 0
    z.MOVE_NE = 1
    z.MOVE_E = 2
    z.MOVE_SE = 3
    z.MOVE_S = 4
    z.MOVE_SW = 5
    z.MOVE_W = 6
    z.MOVE_NW = 7
    z.NORTH = [fake_image]
    z.SOUTH = [fake_image]
    z.EAST = [fake_image]
    z.WEST = [fake_image]
    return z


def _make_minimal_player(center=(100, 100)):
    """Build a minimal player-like mock for zombie tracking tests."""
    p = mock.MagicMock()
    p.rect.centerx = center[0]
    p.rect.centery = center[1]
    # oldxy2 starts at (0, 0) -- not yet updated (timerPos < 180 on fresh spawn)
    p.oldxy2 = (0, 0)
    return p


class TestZombiePlayerTracking:
    """P1-004: Zombie must track the player's real-time position."""

    def test_zombie_moves_toward_player_current_position_not_old(self):
        """
        P1-004: After the fix, oldxy2 is updated every frame to match
        the player's current position. This means zombies should track
        the player immediately, not wait 6 seconds.

        We verify by checking that the player's oldxy2 matches their
        current position (via the Player.update code) and that the zombie
        moves toward it.
        """
        import sprites
        import inspect

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            # Verify the fix: Player.update should set oldxy2 every frame
            # (not gated by timerPos >= 180)
            import player as player_module
            src = inspect.getsource(player_module.Player.update)
            has_conditional_oldxy2 = "timerPos >= 180" in src and "oldxy2" in src[src.index("timerPos >= 180"):]
            assert not has_conditional_oldxy2, (
                "Player.update() still gates oldxy2 behind timerPos >= 180; "
                "zombies won't track the player for the first 6 seconds (P1-004 bug)"
            )

            # Also verify zombie tracks correctly when oldxy2 matches player pos
            zombie = _make_minimal_zombie(pos=(400, 300))
            player1 = _make_minimal_player(center=(600, 400))
            player1.oldxy2 = (600, 400)  # After fix, this matches rect.center

            empty_group = pygame.sprite.Group()
            zombie.update(empty_group, empty_group, player1, None)

            assert zombie.dx > 0, (
                "Zombie should have dx > 0 to approach player at x=600, "
                "but got dx=%d" % zombie.dx
            )
        finally:
            sprites.jCount = original_jcount

    def test_zombie_eventually_reaches_player_area(self):
        """
        After several update ticks, a zombie that starts to the bottom-right
        of the player should converge on the player's position, not diverge.
        This is a weaker test that should pass even with the old-position bug
        once timerPos >= 180 -- but it confirms the tracking logic works at all.
        """
        import sprites

        original_jcount = sprites.jCount
        sprites.jCount = 1

        try:
            zombie = _make_minimal_zombie(pos=(600, 500))
            player1 = _make_minimal_player(center=(100, 100))
            player1.oldxy2 = (100, 100)  # updated position matches real position

            start_x = zombie.rect.centerx
            start_y = zombie.rect.centery
            target_x, target_y = 100, 100

            empty_group = pygame.sprite.Group()
            for _ in range(10):
                zombie.update(empty_group, empty_group, player1, None)

            end_x = zombie.rect.centerx
            end_y = zombie.rect.centery

            dist_start = ((start_x - target_x) ** 2 + (start_y - target_y) ** 2) ** 0.5
            dist_end = ((end_x - target_x) ** 2 + (end_y - target_y) ** 2) ** 0.5

            assert dist_end < dist_start, (
                "Zombie moved AWAY from player after 10 ticks "
                "(start dist=%.1f, end dist=%.1f).  Tracking is broken." % (
                    dist_start, dist_end
                )
            )
        finally:
            sprites.jCount = original_jcount
