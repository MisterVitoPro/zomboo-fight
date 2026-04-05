"""
P0-005: menu() references `donePlaying` before it is guaranteed to be assigned.

Bug: if the event loop exits without any matching event (e.g. all events are
MOUSEMOTION), `donePlaying` is never set, and `return donePlaying` raises
UnboundLocalError.

Additionally the SPACE key path must set donePlaying=False so callers know
to start a new game.
"""
import os
import sys
import types

import pytest

# conftest.py already inserted gameLib into sys.path and set dummy drivers.
import pygame


def _run_menu_with_events(event_list):
    """
    Patch pygame.event.get to return `event_list` on the first call, then
    an empty list on every subsequent call so the loop can drain.  Also patch
    pygame.image.load to avoid file-system access, and clock.tick to avoid
    real timing.
    """
    import main as game_main
    import dataFiles

    call_count = [0]
    original_load = pygame.image.load

    def fake_load(path):
        # Return a minimal surface so blit() works
        surf = pygame.Surface((800, 600))
        return surf

    def fake_event_get():
        call_count[0] += 1
        if call_count[0] == 1:
            return event_list
        # On the second call, send a QUIT event so the loop exits naturally.
        # This lets us observe the return value of menu() rather than
        # breaking out via SystemExit.
        return [pygame.event.Event(pygame.QUIT)]

    monkeypatches = [
        ("pygame.event", "get", fake_event_get),
        ("pygame.image", "load", fake_load),
    ]

    original_event_get = pygame.event.get
    original_image_load = pygame.image.load
    pygame.event.get = fake_event_get
    pygame.image.load = fake_load

    try:
        result = game_main.menu()
    except SystemExit:
        # This means the loop ran out of events without setting donePlaying --
        # which is the exact bug we're testing for (UnboundLocalError would
        # also surface here as the result).
        result = "UNBOUND"
    except UnboundLocalError:
        result = "UNBOUND"
    finally:
        pygame.event.get = original_event_get
        pygame.image.load = original_image_load

    return result


def _make_event(event_type, **kwargs):
    return pygame.event.Event(event_type, **kwargs)


class TestMenuDonePlayingInitialized:
    """
    P0-005: donePlaying is not initialised before the event loop so a QUIT
    event that arrives but causes loop exit before setting donePlaying
    triggers UnboundLocalError on `return donePlaying`.
    """

    def test_menu_returns_without_unboundlocal_on_quit(self):
        """
        A QUIT event must cause menu() to return True without raising
        UnboundLocalError.  Currently menu() only sets donePlaying inside
        the `if event.type == pygame.QUIT` branch so the variable IS set for
        QUIT -- this test confirms that path works.
        """
        quit_event = _make_event(pygame.QUIT)
        result = _run_menu_with_events([quit_event])
        # Should be True (donePlaying=True) not "UNBOUND"
        assert result is True, (
            "menu() should return True on QUIT but got %r -- "
            "possibly UnboundLocalError was raised" % result
        )

    def test_menu_returns_false_on_space(self):
        """
        Pressing SPACE must cause menu() to return False (start a new game).
        """
        space_event = _make_event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0, unicode=" ")
        result = _run_menu_with_events([space_event])
        assert result is False, (
            "menu() should return False when SPACE is pressed, got %r" % result
        )

    def test_menu_raises_unboundlocal_with_no_matching_events(self):
        """
        BUG REPRODUCTION: When the event loop drains without any of QUIT /
        K_ESCAPE / K_SPACE events being processed, `donePlaying` is never
        assigned.  The function should still return a defined value, but
        currently it raises UnboundLocalError.

        This test FAILS on the current code (red phase) because the bug exists.
        After the fix (initialising donePlaying before the loop) this test
        should PASS.
        """
        # Send only a MOUSEMOTION event -- none of the three handled branches
        mousemove = _make_event(pygame.MOUSEMOTION, pos=(10, 10), rel=(1, 1), buttons=(0, 0, 0))
        result = _run_menu_with_events([mousemove])
        # After a fix, result should be a bool (e.g. True = quit by default)
        assert result != "UNBOUND", (
            "menu() raised UnboundLocalError because donePlaying was never "
            "initialised before use in `return donePlaying`"
        )
