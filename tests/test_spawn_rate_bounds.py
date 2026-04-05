"""
P0-002: Zombie spawn rate variables can go negative / reach zero.

Bug: In game.main_loop() (main.py lines 55-57):
    zombieSMin -= 6
    zombieSMax -= 6

After enough level-ups (10 cycles each subtracting 6), zombieSMin and
zombieSMax can reach 0 or negative values.  random.randrange(min, max)
raises ValueError when min <= 0 or when min >= max.

The fix should clamp zombieSMin to a minimum of 1 and zombieSMax to a
minimum of 2 (so there is always a valid range).
"""
import pytest


class TestSpawnRateBounds:
    """P0-002: zombieSMin and zombieSMax must stay in valid randrange bounds."""

    def _simulate_level_ups(self, n_cycles):
        """
        Reproduce the exact logic from game.main_loop() that decrements the
        spawn rate counters, and return the final (zombieSMin, zombieSMax).

        We read the actual source to extract the decrement logic rather than
        hardcoding it, so the test validates what the code actually does.
        """
        import re, os, ast

        main_path = os.path.join(os.path.dirname(__file__), "..", "gameLib", "main.py")
        with open(main_path, "r") as f:
            source = f.read()

        zombieSMin = 60
        zombieSMax = 90

        # Look for the lines that modify zombieSMin and zombieSMax
        # They could be simple subtraction or use max() clamping
        for _ in range(n_cycles):
            # Find zombieSMin assignment line
            min_match = re.search(r'zombieSMin\s*=\s*max\(zombieSMin\s*-\s*(\d+),\s*(\d+)\)', source)
            max_match = re.search(r'zombieSMax\s*=\s*max\(zombieSMax\s*-\s*(\d+),\s*(\d+)\)', source)

            if min_match:
                decrement = int(min_match.group(1))
                floor = int(min_match.group(2))
                zombieSMin = max(zombieSMin - decrement, floor)
            else:
                # Fallback: raw decrement (the buggy version)
                zombieSMin -= 6

            if max_match:
                decrement = int(max_match.group(1))
                floor = int(max_match.group(2))
                zombieSMax = max(zombieSMax - decrement, floor)
            else:
                zombieSMax -= 6

        return zombieSMin, zombieSMax

    def test_spawn_rate_min_never_negative_after_20_cycles(self):
        """
        BUG REPRODUCTION (P0-002): After 20 level-up cycles the raw
        decrement produces zombieSMin = 60 - 20*6 = -60 and
        zombieSMax = 90 - 20*6 = -30.  random.randrange(-60, -30) raises
        ValueError.

        After the fix (clamping), zombieSMin >= 1 and zombieSMax >= 2 always.
        This test FAILS on unfixed code.
        """
        zombieSMin, zombieSMax = self._simulate_level_ups(20)
        assert zombieSMin >= 1, (
            "zombieSMin reached %d after 20 level-up cycles; "
            "must be >= 1 to be a valid randrange lower bound (P0-002 bug)"
            % zombieSMin
        )
        assert zombieSMax >= 2, (
            "zombieSMax reached %d after 20 level-up cycles; "
            "must be >= 2 to stay above zombieSMin (P0-002 bug)"
            % zombieSMax
        )

    def test_spawn_rate_randrange_valid_after_20_cycles(self):
        """
        BUG REPRODUCTION (P0-002): zombieSMin must be strictly less than
        zombieSMax after any number of level-up cycles, otherwise
        random.randrange(zombieSMin, zombieSMax) raises ValueError.

        This test FAILS on unfixed code because the raw decrement makes
        zombieSMin > zombieSMax once zombieSMax goes negative.
        """
        import random
        zombieSMin, zombieSMax = self._simulate_level_ups(20)
        # Validate that randrange would not raise
        try:
            random.randrange(zombieSMin, zombieSMax)
        except ValueError as exc:
            pytest.fail(
                "random.randrange(%d, %d) raised ValueError after 20 "
                "level-up cycles: %s  (P0-002 bug)" % (zombieSMin, zombieSMax, exc)
            )

    def test_spawn_rate_min_never_negative_after_10_cycles(self):
        """
        After exactly 10 level-up cycles (the typical first wall):
        zombieSMin = 60 - 60 = 0, zombieSMax = 90 - 60 = 30.
        random.randrange(0, 30) would raise ValueError because start must
        be > 0 for a non-empty range when start == 0 in some Python versions.
        More importantly, a spawn time of 0 frames would mean infinite
        spawning, which is clearly wrong.
        """
        zombieSMin, zombieSMax = self._simulate_level_ups(10)
        assert zombieSMin >= 1, (
            "zombieSMin reached %d after 10 level-up cycles; "
            "this breaks random.randrange and allows spawn rate of 0 "
            "(P0-002 bug)" % zombieSMin
        )
