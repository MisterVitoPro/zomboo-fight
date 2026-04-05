"""
P2-007: LaserSight.__init__() uses a hardcoded path instead of dataFiles constant.

Bug: In sprites.LaserSight.__init__() (sprites.py line 314):
    self.imageMaster = pygame.image.load("../data/Laser_Pointer.tga")

This is a hardcoded relative path.  The rest of the codebase uses
dataFiles.laserSightIm for this asset.  The hardcoded path will break
when the working directory is not gameLib/ (same root cause as P2-002).

Fix: Replace the hardcoded string with dataFiles.laserSightIm:
    self.imageMaster = pygame.image.load(dataFiles.laserSightIm)
"""
import inspect
import pytest


class TestLaserSightUsesDataFiles:
    """P2-007: LaserSight must not hardcode asset paths."""

    def test_lasersight_init_has_no_hardcoded_data_path(self):
        """
        BUG REPRODUCTION (P2-007): LaserSight.__init__() contains the
        hardcoded string '../data/Laser_Pointer.tga' instead of using
        the dataFiles.laserSightIm constant.

        We read the source of __init__ and assert the hardcoded path is absent.
        This test FAILS on the current code.
        """
        import sprites
        source = inspect.getsource(sprites.LaserSight.__init__)

        assert "../data/" not in source, (
            "LaserSight.__init__() contains hardcoded path '../data/'; "
            "it should use dataFiles.laserSightIm instead (P2-007 bug).  "
            "Found in source:\n%s" % source
        )

    def test_lasersight_init_references_datafiles_constant(self):
        """
        BUG REPRODUCTION (P2-007): The source of LaserSight.__init__ should
        reference dataFiles.laserSightIm (or at minimum the `dataFiles` module).

        This test FAILS on the current code because the path is hardcoded.
        """
        import sprites
        source = inspect.getsource(sprites.LaserSight.__init__)

        assert "dataFiles" in source, (
            "LaserSight.__init__() does not reference dataFiles at all; "
            "the laser sight image path is hardcoded to '../data/Laser_Pointer.tga' "
            "instead of using dataFiles.laserSightIm (P2-007 bug)"
        )

    def test_lasersight_path_matches_datafiles_constant(self):
        """
        The constant dataFiles.laserSightIm must point to the same file
        as whatever LaserSight loads, so that fixing the hardcoded path
        with the constant actually works.
        """
        import dataFiles
        import os

        expected_filename = "Laser_Pointer.bmp"
        actual_path = dataFiles.laserSightIm

        assert expected_filename in actual_path or "Laser_Pointer" in actual_path, (
            "dataFiles.laserSightIm ('%s') does not appear to reference the "
            "Laser_Pointer file; the constant may also be wrong" % actual_path
        )
