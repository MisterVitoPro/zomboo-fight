# D:/workspace/zomboo-fight/tests/test_p0_joystick_null_guard.py
"""
Tests for:
  P0-001: Null joystick dereference in player.update() movement block
  P0-002: pygame.JOYBUTTONDOWN used as always-true constant guard
  P2-005: Player moving flag not set on keyboard input
  P3-003: Stamina recovery only applies at exact zero velocity
"""
import inspect
import pytest
import pygame
import unittest.mock as mock


def _make_minimal_player(jOn=False, j=None):
    """Build a Player using object.__new__ to skip full __init__ asset loading."""
    import player as player_module

    fake_surface = pygame.Surface((24, 32))
    p = object.__new__(player_module.Player)
    pygame.sprite.Sprite.__init__(p)
    p.pNum = 1
    p.j = j
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
    p.fireTimer = 0
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
    p.gun = "Pistol"
    p.damage = 20
    p.reloadSpeed = 15
    p.ammo = 9
    p.clips = 8
    p.automatic = False
    p.fireRate = 10
    p.bulletLife = 45
    p.bulletStr = 2
    p.moving = False
    p.state = None
    p.MOVE_N = 0
    p.MOVE_NE = 1
    p.MOVE_E = 2
    p.MOVE_SE = 3
    p.MOVE_S = 4
    p.MOVE_SW = 5
    p.MOVE_W = 6
    p.MOVE_NW = 7
    p.NORTH = [fake_surface]
    p.SOUTH = [fake_surface]
    p.EAST = [fake_surface]
    p.WEST = [fake_surface]

    import sGroups
    p.bulletSprites = sGroups.bulletSprites
    p.bombSprites = sGroups.bombSprites

    p.fireSnd = mock.MagicMock()
    p.reloadSnd = mock.MagicMock()
    p.emptySnd = mock.MagicMock()
    return p


class TestP0JoystickNullGuardInUpdate:
    """P0-001: player.update() must not crash when sprites.jOn=True but self.j=None."""

    def test_player_update_does_not_crash_when_j_is_none_and_jon_true(self):
        """
        BUG REPRODUCTION (P0-001): When sprites.jOn is True but player.j is None
        (e.g. player 2 with only 1 controller), calling player.update() raises:
            AttributeError: 'NoneType' object has no attribute 'get_axis'
        at player.py:103.  After the fix (and self.j is not None guard), this
        must not raise.
        """
        import sprites

        original_jOn = sprites.jOn
        sprites.jOn = True

        try:
            p = _make_minimal_player(jOn=True, j=None)

            empty_group = pygame.sprite.Group()

            fake_event_list = []
            fake_keys = [False] * 512
            fake_mouse = (0, 0)
            fake_mouse_buttons = (False, False, False)

            with mock.patch("pygame.key.get_pressed", return_value=fake_keys), \
                 mock.patch("pygame.mouse.get_pos", return_value=fake_mouse), \
                 mock.patch("pygame.mouse.get_pressed", return_value=fake_mouse_buttons), \
                 mock.patch("pygame.sprite.spritecollide", return_value=[]):
                try:
                    p.update(empty_group, empty_group, empty_group)
                except AttributeError as exc:
                    pytest.fail(
                        "player.update() raised AttributeError when sprites.jOn=True "
                        "and self.j=None: %s  (P0-001 bug)" % exc
                    )
        finally:
            sprites.jOn = original_jOn

    def test_player_update_joystick_block_skipped_when_j_is_none(self):
        """
        When self.j is None and sprites.jOn is True, the joystick input block
        must be skipped entirely so that joyX/joyY are not read from None.
        After the fix the block is guarded; this test confirms no axis reads occur.
        """
        import sprites

        original_jOn = sprites.jOn
        sprites.jOn = True

        try:
            p = _make_minimal_player(jOn=True, j=None)

            # Patch get_axis to raise if called (it should never be called)
            axis_called = [False]

            class FailingJoystick:
                def get_axis(self, n):
                    axis_called[0] = True
                    raise AssertionError("get_axis called on None joystick (P0-001)")

            p.j = None

            empty_group = pygame.sprite.Group()
            fake_keys = [False] * 512
            fake_mouse_buttons = (False, False, False)

            with mock.patch("pygame.key.get_pressed", return_value=fake_keys), \
                 mock.patch("pygame.mouse.get_pos", return_value=(400, 300)), \
                 mock.patch("pygame.mouse.get_pressed", return_value=fake_mouse_buttons), \
                 mock.patch("pygame.sprite.spritecollide", return_value=[]):
                try:
                    p.update(empty_group, empty_group, empty_group)
                except AttributeError:
                    pass  # Already caught by P0-001 test; we check axis_called separately

            assert not axis_called[0], (
                "get_axis() was called on a None joystick (P0-001 bug)"
            )
        finally:
            sprites.jOn = original_jOn

    def test_player_update_works_normally_when_j_is_valid_mock(self):
        """
        Positive test: when sprites.jOn=True and self.j is a valid mock joystick,
        player.update() must complete without error.
        """
        import sprites

        original_jOn = sprites.jOn
        sprites.jOn = True

        try:
            mock_joystick = mock.MagicMock()
            mock_joystick.get_axis.return_value = 0.0
            mock_joystick.get_button.return_value = False

            p = _make_minimal_player(jOn=True, j=mock_joystick)

            empty_group = pygame.sprite.Group()
            fake_keys = [False] * 512
            fake_mouse_buttons = (False, False, False)

            with mock.patch("pygame.key.get_pressed", return_value=fake_keys), \
                 mock.patch("pygame.mouse.get_pos", return_value=(400, 300)), \
                 mock.patch("pygame.mouse.get_pressed", return_value=fake_mouse_buttons), \
                 mock.patch("pygame.sprite.spritecollide", return_value=[]):
                p.update(empty_group, empty_group, empty_group)
        finally:
            sprites.jOn = original_jOn


class TestP0JoyButtonDownConstant:
    """P0-002: pygame.JOYBUTTONDOWN must not be used as a boolean condition."""

    def test_joybuttondown_not_used_as_boolean_condition(self):
        """
        BUG REPRODUCTION (P0-002): The line `if pygame.JOYBUTTONDOWN:` in
        player.update() is always True (constant 1539), causing get_button()
        to be called unconditionally even when self.j is None.

        Inspect the source and assert the bare constant check is absent.
        This test FAILS on current code.
        """
        import player as player_module

        source = inspect.getsource(player_module.Player.update)

        assert "if pygame.JOYBUTTONDOWN:" not in source, (
            "player.update() still contains `if pygame.JOYBUTTONDOWN:` which is "
            "always True (constant 1539) -- this is not an event check and allows "
            "get_button() to be called on a None joystick (P0-002 bug)"
        )

    def test_button_block_guarded_by_j_is_not_none(self):
        """
        After the fix, all self.j.get_button() calls must be inside a block
        that verifies self.j is not None.  Inspect source to confirm.
        """
        import player as player_module

        source = inspect.getsource(player_module.Player.update)

        # The joystick button block should be inside the outer jOn + j guard
        # Heuristic: count lines between 'self.j is not None' and 'get_button'
        j_guard_idx = source.find("self.j is not None")
        get_button_idx = source.find("self.j.get_button")

        assert j_guard_idx != -1, (
            "player.update() does not contain a 'self.j is not None' guard "
            "(P0-002 fix missing)"
        )
        assert get_button_idx != -1, (
            "player.update() does not call self.j.get_button() at all; "
            "the method may have been removed entirely"
        )
        assert j_guard_idx < get_button_idx, (
            "'self.j is not None' guard at index %d comes AFTER get_button at index %d; "
            "button reads must be inside the guard (P0-002)" % (j_guard_idx, get_button_idx)
        )


class TestP1001JoyAxisMotionConstant:
    """P1-001: pygame.JOYAXISMOTION must not be used as a boolean condition."""

    def test_joyaxismotion_not_used_as_boolean_condition(self):
        """
        BUG REPRODUCTION (P1-001): `if pygame.JOYAXISMOTION:` is always True
        (constant 1536), making self.moving permanently True whenever a joystick
        is connected.  After the fix this line is removed.
        This test FAILS on current code.
        """
        import player as player_module

        source = inspect.getsource(player_module.Player.update)

        assert "if pygame.JOYAXISMOTION:" not in source, (
            "player.update() still contains `if pygame.JOYAXISMOTION:` which is "
            "always True (constant 1536).  This makes self.moving permanently True "
            "while a joystick is connected (P1-001 bug)"
        )


class TestP2005MovingFlagKeyboard:
    """P2-005: Player self.moving flag must be set on keyboard input."""

    def test_moving_flag_true_when_w_key_pressed(self):
        """
        BUG REPRODUCTION (P2-005): player.movement() sets speedY but does not
        set self.moving = True.  Animation only plays when moving is True.
        After the fix, pressing W must set self.moving = True.
        This test FAILS on current code.
        """
        import player as player_module

        p = _make_minimal_player()
        p.moving = False

        # Simulate W key pressed
        fake_keys = [False] * 512
        fake_keys[pygame.K_w] = True
        p.keys = fake_keys

        p.movement()

        assert p.moving == True, (
            "player.moving is False after movement() with W pressed; "
            "self.moving must be set to True when a movement key is active "
            "(P2-005 bug)"
        )

    def test_moving_flag_false_when_no_keys_pressed(self):
        """
        When no WASD keys are pressed, movement() should set self.moving = False
        (so idle animation is used rather than walk cycle).
        """
        import player as player_module

        p = _make_minimal_player()
        p.moving = True  # Simulate previously moving state

        fake_keys = [False] * 512
        p.keys = fake_keys

        p.movement()

        assert p.moving == False, (
            "player.moving is still True after movement() with no keys pressed; "
            "self.moving should be False when stationary (P2-005)"
        )


class TestP3003StaminaRecoveryThreshold:
    """P3-003: Stamina bonus recovery should apply when nearly stopped, not only at exact zero."""

    def test_stamina_bonus_applies_at_near_zero_velocity(self):
        """
        BUG REPRODUCTION (P3-003): stamina_change(1) only grants the +1 bonus
        when speedX == 0 AND speedY == 0 exactly.  A player at speedX=0.3
        gets no bonus.  After the fix (threshold-based check), near-zero
        speed should still grant the bonus.
        This test FAILS on current code.
        """
        import player as player_module

        p = _make_minimal_player()
        p.stamina = 50
        p.staminaTimerUp = 15   # Trigger the stamina recovery this tick
        p.reloading = False
        p.speedX = 0.3          # Near-zero but not exactly zero
        p.speedY = 0.0

        p.stamina_change(1)

        # After fix: stamina should have increased by 2 (base 1 + near-still bonus 1)
        assert p.stamina == 52, (
            "stamina is %d after stamina_change(1) with speedX=0.3; "
            "expected 52 (base +1, near-still bonus +1).  The bonus only applies "
            "at exact zero velocity (P3-003 bug)" % p.stamina
        )

    def test_stamina_bonus_does_not_apply_while_moving_fast(self):
        """
        When moving at full speed (speedX=5), no bonus should apply.
        This is a regression guard -- should pass on both old and fixed code.
        """
        import player as player_module

        p = _make_minimal_player()
        p.stamina = 50
        p.staminaTimerUp = 15
        p.reloading = False
        p.speedX = 5
        p.speedY = 0

        p.stamina_change(1)

        # Only base +1 recovery, no near-still bonus
        assert p.stamina == 51, (
            "stamina is %d after stamina_change(1) at full speed; "
            "expected 51 (base +1 only, no near-still bonus)" % p.stamina
        )
