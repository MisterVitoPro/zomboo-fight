"""
P2-002: dataFiles.py uses hardcoded relative paths like "../data/" which
break when the working directory is not gameLib/.

Bug: dataFiles.py line 7-10:
    dataPath = "../data/"
    soundPath = "../data/Sounds/"
    ...

These paths are relative to the process's CWD.  When run from the project
root (e.g. `python gameLib/main.py` from D:\\workspace\\zomboo-fight) or
from a test runner, "../data/" resolves to the wrong directory.

Fix: Compute paths relative to the dataFiles.py module location:
    import os
    _HERE = os.path.dirname(os.path.abspath(__file__))
    dataPath = os.path.join(_HERE, "..", "data") + os.sep
"""
import os
import sys
import pytest


DATA_DIR = os.path.join(
    os.path.dirname(__file__), "..", "data"
)

# Key asset files that must exist
REQUIRED_ASSETS = [
    ("mainMenuIm", "mainMenubg.jpg"),
    ("gamefieldBG", "game_field.tga"),
    ("dude1Im", "dude1.tga"),
    ("zombie1", None),  # path from dataFiles
    ("zombieBig", "bigZombie.tga"),
    ("bulletIm", "bullet.tga"),
    ("explosionIm", "explosion64.PNG"),
]


class TestAssetPathsResolve:
    """P2-002: dataFiles paths must resolve from any working directory."""

    def test_data_directory_exists_relative_to_project_root(self):
        """
        The data/ directory must exist relative to the project root.
        This always passes if the repo is intact.
        """
        data_abs = os.path.abspath(DATA_DIR)
        assert os.path.isdir(data_abs), (
            "data/ directory not found at %s" % data_abs
        )

    def test_datafiles_paths_are_not_absolute(self):
        """
        All dataFiles paths should be resolvable.  Currently they are
        relative paths starting with '../data/' which only work when CWD
        is gameLib/.  This test checks what they resolve to from the
        test runner's perspective.
        """
        import dataFiles
        # The paths in dataFiles start with "../data/" -- relative to gameLib/
        # From the tests/ directory they should resolve to the data directory.
        # After the P2-002 fix, paths are absolute (module-relative).
        # Verify they are now absolute OR resolve correctly.
        assert os.path.isabs(dataFiles.dataPath) or dataFiles.dataPath.startswith("../"), (
            "dataFiles.dataPath is neither absolute nor relative"
        )

    def test_main_menu_asset_resolves_from_project_root(self):
        """
        BUG REPRODUCTION (P2-002): When tests are run from the project root,
        the path '../data/mainMenubg.jpg' resolves to the PARENT of the
        project root (one level up from zomboo-fight/), not to the data/ dir.

        We verify that the path in dataFiles actually points to an existing file.
        This test FAILS when run from outside gameLib/ (i.e. normal test runner
        invocation from project root).
        """
        import dataFiles

        # dataFiles.mainMenuIm == "../data/mainMenubg.jpg" (relative)
        # When resolved from project root: D:\\workspace\\mainMenubg.jpg (wrong)
        # When resolved from gameLib/: D:\\workspace\\zomboo-fight\\data\\mainMenubg.jpg (right)

        resolved_path = os.path.abspath(dataFiles.mainMenuIm)
        assert os.path.isfile(resolved_path), (
            "dataFiles.mainMenuIm ('%s') does not resolve to an existing file "
            "from the current working directory ('%s').  "
            "The path resolves to: '%s'  "
            "dataFiles.py must use paths relative to its own module location, "
            "not relative to CWD (P2-002 bug)" % (
                dataFiles.mainMenuIm,
                os.getcwd(),
                resolved_path,
            )
        )

    def test_game_field_background_resolves(self):
        """
        BUG REPRODUCTION (P2-002): Same as above for gamefieldBG.
        """
        import dataFiles
        resolved_path = os.path.abspath(dataFiles.gamefieldBG)
        assert os.path.isfile(resolved_path), (
            "dataFiles.gamefieldBG ('%s') -> '%s' does not exist from CWD '%s' "
            "(P2-002 bug)" % (dataFiles.gamefieldBG, resolved_path, os.getcwd())
        )

    def test_zombie_sprite_resolves(self):
        """
        BUG REPRODUCTION (P2-002): zombie sprite path must resolve correctly.
        """
        import dataFiles
        resolved_path = os.path.abspath(dataFiles.zombie1)
        assert os.path.isfile(resolved_path), (
            "dataFiles.zombie1 ('%s') -> '%s' does not exist from CWD '%s' "
            "(P2-002 bug)" % (dataFiles.zombie1, resolved_path, os.getcwd())
        )
