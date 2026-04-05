"""Profile the ZOMBOO game loop and report hotspots.

Run: python profile_game.py
Plays for ~10 seconds then dumps cProfile stats.
"""
import cProfile
import pstats
import io
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "gameLib"))

import pygame
import dataFiles
import main as game_main

# Monkey-patch the main loop to auto-quit after N frames
_PROFILE_FRAMES = 300  # ~10 seconds at 30 FPS

_orig_init = game_main.game.__init__

def _profiled_init(self):
    self.screen = pygame.display.set_mode((dataFiles.SCREEN_WIDTH, dataFiles.SCREEN_HEIGHT))
    pygame.display.set_caption("ZOMBOO - PROFILING")
    import random
    self.spawnRate = random.randrange(10, 31)
    import sGroups
    sGroups.empty_all()
    self.make_sprites()
    sGroups.staticSprites.draw(self.screen)
    _profiled_main_loop(self)

def _profiled_main_loop(self):
    import random, sGroups, zombieSpawn
    self.background = pygame.image.load(dataFiles.gamefieldBG).convert()
    timer = 0
    timerSpawn = 0
    timerPickup = 0
    zombieLvl = 0
    zombieSMin = 60
    zombieSMax = 90
    clock = pygame.time.Clock()
    frame_count = 0

    while frame_count < _PROFILE_FRAMES:
        ms = clock.tick(dataFiles.FPS)
        dt = ms / (1000.0 / dataFiles.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        if self.player1.dead:
            break

        timerPickup += 1
        if timerPickup >= 150:
            self.pickups()
            timerPickup = 0

        timer += 1
        if timer >= self.spawnRate:
            self.spawn_zombie(self.zombie_spawner.rect.center)
            timer = 0
            self.spawnRate = random.randrange(zombieSMin, zombieSMax)

        timerSpawn += 1
        if timerSpawn >= (random.randrange(10 * dataFiles.FPS, 15 * dataFiles.FPS)):
            self.zombie_spawner = zombieSpawn.ZombieSpawner(30)
            sGroups.UISprites.add(self.zombie_spawner)
            timerSpawn = 0
            zombieLvl += 1
            zombieSMin = max(zombieSMin - 6, 5)
            zombieSMax = max(zombieSMax - 6, 10)

        self.update_groups(dt)
        self.draw_groups()
        pygame.display.flip()
        frame_count += 1

    pygame.mouse.set_visible(True)

# P2-012: This monkey-patch replaces game.__init__ without restoring the original.
# That is acceptable here because profiling is a short-lived dev-only run; no restore
# is needed since the process exits immediately after profiling completes.
game_main.game.__init__ = _profiled_init

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    # Skip menu, go straight to game
    game_main.game()
    profiler.disable()

    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(40)
    print(s.getvalue())

    s2 = io.StringIO()
    ps2 = pstats.Stats(profiler, stream=s2)
    ps2.sort_stats("tottime")
    ps2.print_stats(40)
    print("\n=== BY TOTAL TIME ===")
    print(s2.getvalue())
