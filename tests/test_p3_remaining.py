"""Tests for P3 fixes: P3-001, P3-005, P3-006."""
import os
import pytest


class TestNoPython2PrintSyntax:
    """P3-001: No Python 2 print statements (even in comments)."""

    def test_no_py2_print_in_sprites(self):
        path = os.path.join(os.path.dirname(__file__), "..", "gameLib", "sprites.py")
        with open(path) as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    # Check for Python 2 print syntax in comments
                    comment = stripped.lstrip("#").strip()
                    if comment.startswith("print ") and "(" not in comment[:20]:
                        pytest.fail(
                            "Python 2 print syntax at sprites.py:%d: %s (P3-001)"
                            % (i, stripped)
                        )

    def test_no_py2_print_in_player(self):
        path = os.path.join(os.path.dirname(__file__), "..", "gameLib", "player.py")
        with open(path) as f:
            for i, line in enumerate(f, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    comment = stripped.lstrip("#").strip()
                    if comment.startswith("print ") and "(" not in comment[:20]:
                        pytest.fail(
                            "Python 2 print syntax at player.py:%d: %s (P3-001)"
                            % (i, stripped)
                        )


class TestNoDirBuiltinShadowing:
    """P3-006: Local variables should not shadow the 'dir' built-in."""

    def test_no_dir_variable_in_loadimage(self):
        """GameObject.load_image should not use 'dir' as a local variable name."""
        import sprites
        import inspect
        src = inspect.getsource(sprites.GameObject.load_image)
        # Check that `dir = ` assignments don't exist (should use `direction = `)
        lines = src.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("dir =") or stripped.startswith("dir="):
                pytest.fail(
                    "load_image uses 'dir' as a variable name on line %d: '%s'. "
                    "Should use 'direction' to avoid shadowing built-in (P3-006)"
                    % (i + 1, stripped)
                )
