"""
Pytest configuration and shared fixtures for ZOMBOO game tests.

Sets up pygame with dummy drivers so tests can run headlessly without a
real display or audio device.
"""
import os
import sys

# Must be set BEFORE pygame is imported anywhere in this process.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

# Add the gameLib package to the import path so tests can do
# `import sprites`, `import player`, etc. exactly as the game does.
GAME_LIB = os.path.join(os.path.dirname(__file__), "..", "gameLib")
if GAME_LIB not in sys.path:
    sys.path.insert(0, os.path.abspath(GAME_LIB))

import pygame
import pytest


@pytest.fixture(scope="session", autouse=True)
def pygame_session():
    """Initialise pygame once for the entire test session."""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def clear_sprite_groups():
    """
    Empty all global sprite groups before every test so that group state
    from one test cannot leak into the next.
    """
    import sGroups
    yield
    for group in (
        sGroups.turretSprites,
        sGroups.UISprites,
        sGroups.UIBarSprites,
        sGroups.textSprites,
        sGroups.allySprites,
        sGroups.zombieSprites,
        sGroups.bulletSprites,
        sGroups.bombSprites,
        sGroups.fireSprites,
        sGroups.splatSprites,
        sGroups.laserSprites,
        sGroups.powerupSprites,
        sGroups.staticSprites,
    ):
        group.empty()
