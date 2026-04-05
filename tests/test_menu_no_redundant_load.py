"""
P0-004: menu() reloads the background image on every frame inside the loop.

Bug: `background = pygame.image.load(dataFiles.mainMenuIm)` appears both
BEFORE the loop (line 203) and INSIDE the loop (line 210).  This means
the file is read from disk every 1/30 second while the menu is open, which
is wasteful and the in-loop reload is entirely redundant.

The test patches pygame.image.load to count calls and runs menu() with
a single immediate QUIT event (so the loop executes exactly one iteration).
With the bug present, load() is called at least 2 times (once before loop,
once inside loop body).  After the fix it should be called exactly once
(the pre-loop initialisation only).
"""
import os
import sys
import pytest
import pygame


def test_menu_loads_background_once():
    """
    BUG REPRODUCTION (P0-004): menu() calls pygame.image.load for the
    background inside the event loop on every frame.  After exactly one loop
    iteration (driven by a single QUIT event), the load call count should be
    1 (setup only).  Currently it is >= 2, so this test FAILS on unfixed code.
    """
    import main as game_main

    load_call_count = [0]
    original_load = pygame.image.load

    def counting_load(path):
        load_call_count[0] += 1
        surf = pygame.Surface((800, 600))
        return surf

    first_call = [True]
    original_event_get = pygame.event.get

    def one_shot_events():
        if first_call[0]:
            first_call[0] = False
            return [pygame.event.Event(pygame.QUIT)]
        raise SystemExit("done")

    pygame.image.load = counting_load
    pygame.event.get = one_shot_events
    try:
        game_main.menu()
    except SystemExit:
        pass
    finally:
        pygame.image.load = original_load
        pygame.event.get = original_event_get

    # With the bug: count >= 2 (once before loop, once inside loop).
    # After fix  : count == 1 (the in-loop reload is removed).
    assert load_call_count[0] <= 1, (
        "pygame.image.load was called %d time(s) during menu(); "
        "the background is being reloaded every frame inside the loop "
        "(P0-004 bug)" % load_call_count[0]
    )
