"""
P1-003: Levels.Level.get_at() swallows ALL exceptions with a bare `except:`.

Bug: In Levels.py line 36-38:
    def get_at(self, dx, dy):
        try:
            return self.image.get_at((dx, dy))
        except:
            pass

A bare `except:` catches everything including KeyboardInterrupt, SystemExit,
and MemoryError.  It should only catch IndexError (out-of-bounds pixel access)
or the equivalent pygame error.

Fix: Change `except:` to `except (IndexError, Exception)` or more precisely
to the actual exception type raised by pygame on out-of-bounds access.
"""
import pytest
import pygame
import unittest.mock as mock


def _make_level_with_mock_image(width=10, height=10):
    """
    Create a Level object without calling Layout() (which would try to
    parse a real image and create Wall sprites).  We inject a mock image
    surface so we can control get_at() behaviour.
    """
    import Levels

    level = object.__new__(Levels.Level)
    # Create a real pygame Surface to use as the level image
    level.image = pygame.Surface((width, height))
    level.image.fill((0, 0, 0))
    # Paint one blue pixel at (0, 0) to test the WALL colour path
    level.image.set_at((0, 0), (0, 0, 255, 255))
    level.x = 0
    level.y = 0
    level.WALL = (0, 0, 255, 0)
    return level


class TestGetAtExceptionHandling:
    """P1-003: get_at should catch only IndexError, not all exceptions."""

    def test_get_at_returns_color_for_valid_coords(self):
        """
        get_at() with valid coordinates must return the pixel colour.
        This is the happy path -- should pass even on unfixed code.
        """
        level = _make_level_with_mock_image(10, 10)
        color = level.get_at(5, 5)
        assert color is not None, "get_at with valid coords returned None"

    def test_get_at_returns_none_for_out_of_bounds(self):
        """
        get_at() with coordinates outside the image bounds must return None
        (the exception is silenced correctly for IndexError/pygame error).
        This should pass on both fixed and unfixed code.
        """
        level = _make_level_with_mock_image(10, 10)
        result = level.get_at(9999, 9999)
        assert result is None, (
            "get_at with out-of-bounds coords should return None, got %r" % result
        )

    def test_get_at_does_not_swallow_keyboard_interrupt(self):
        """
        BUG REPRODUCTION (P1-003): The bare `except:` in get_at() swallows
        KeyboardInterrupt.  This means Ctrl-C cannot interrupt the game's
        level layout loop.

        We inject a KeyboardInterrupt into the image's get_at() call and
        verify it propagates out.  On the current code it is SWALLOWED
        (this test FAILS because the exception is caught and suppressed).
        After the fix (e.g. `except IndexError:`) it propagates correctly.
        """
        import Levels

        level = _make_level_with_mock_image(10, 10)

        def raise_keyboard_interrupt(coord):
            raise KeyboardInterrupt("simulated Ctrl-C")

        # Replace the surface's get_at with one that raises KeyboardInterrupt
        level.image = mock.MagicMock()
        level.image.get_at = raise_keyboard_interrupt

        with pytest.raises(KeyboardInterrupt):
            level.get_at(0, 0)
        # If this pytest.raises does NOT catch a KeyboardInterrupt, it means
        # Level.get_at() swallowed it -- confirming the P1-003 bug.

    def test_get_at_does_not_swallow_system_exit(self):
        """
        BUG REPRODUCTION (P1-003): SystemExit should also propagate.
        Same root cause as KeyboardInterrupt -- bare `except:` swallows it.
        """
        import Levels

        level = _make_level_with_mock_image(10, 10)

        def raise_system_exit(coord):
            raise SystemExit("simulated exit")

        level.image = mock.MagicMock()
        level.image.get_at = raise_system_exit

        with pytest.raises(SystemExit):
            level.get_at(0, 0)
