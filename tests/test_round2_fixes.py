"""Tests for round 2 fixes: P2-003, P2-004, P2-008, P2-009, P2-013, P2-014,
P3-002, P3-003, P3-004."""
import inspect
import os
import sys
import re
import pytest
import pygame


class TestP3004CopyrightHeaders:
    """P3-004: Copyright headers should not reference 'student' as author."""

    def _read_header(self, filename):
        path = os.path.join(os.path.dirname(__file__), "..", "gameLib", filename)
        with open(path) as f:
            return f.read(500)

    def test_no_student_author(self):
        for filename in ["sprites.py", "dataFiles.py", "player.py", "main.py",
                         "pickups.py", "sGroups.py", "animate.py", "UI_HUD.py"]:
            header = self._read_header(filename)
            assert "@author: student" not in header, (
                "%s still has '@author: student' (P3-004)" % filename
            )

    def test_headers_use_docstring_format(self):
        for filename in ["sprites.py", "player.py", "main.py", "pickups.py"]:
            header = self._read_header(filename)
            assert header.startswith('"""'), (
                "%s should use triple-quote docstring header (P3-004)" % filename
            )


class TestP2003ImageChangeDeduplicated:
    """P2-003: imageChange should not have duplicate logic for pNum 1 and 2."""

    def test_no_pnum_check_in_image_change(self):
        import player as player_module
        src = inspect.getsource(player_module.Player.image_change)
        assert "pNum" not in src, (
            "image_change still checks pNum -- duplicate branches not collapsed (P2-003)"
        )


class TestP2004MagicNumbers:
    """P2-004: Screen dimensions and FPS should be centralized constants."""

    def test_datafiles_has_screen_constants(self):
        import dataFiles
        assert hasattr(dataFiles, "SCREEN_WIDTH"), "dataFiles missing SCREEN_WIDTH"
        assert hasattr(dataFiles, "SCREEN_HEIGHT"), "dataFiles missing SCREEN_HEIGHT"
        assert hasattr(dataFiles, "FPS"), "dataFiles missing FPS"
        assert dataFiles.SCREEN_WIDTH == 800
        assert dataFiles.SCREEN_HEIGHT == 600
        assert dataFiles.FPS == 30

    def test_main_uses_screen_constants(self):
        import main as game_main
        src = inspect.getsource(game_main.game.__init__)
        assert "dataFiles.SCREEN_WIDTH" in src or "SCREEN_WIDTH" in src, (
            "game.__init__ should use SCREEN_WIDTH constant (P2-004)"
        )

    def test_sprites_uses_screen_constants(self):
        import sprites
        src = inspect.getsource(sprites.GameObject.__init__)
        assert "800" not in src, (
            "GameObject.__init__ still has hardcoded 800 (P2-004)"
        )

    def test_main_uses_fps_constant(self):
        import main as game_main
        src = inspect.getsource(game_main.game.main_loop)
        assert "dataFiles.FPS" in src, (
            "main_loop should use dataFiles.FPS instead of hardcoded 30 (P2-004)"
        )


class TestP2008PickupRotationCache:
    """P2-008: Pickup rotation should use cached surfaces."""

    def test_pickup_has_rotation_cache(self):
        import pickups
        assert hasattr(pickups.Pickup, "_rotation_cache"), (
            "Pickup class should have a _rotation_cache for precomputed frames (P2-008)"
        )

    def test_pickup_update_does_not_call_transform_rotate(self):
        import pickups
        src = inspect.getsource(pickups.Pickup.update)
        assert "pygame.transform.rotate" not in src, (
            "Pickup.update() should use cached frames, not call "
            "pygame.transform.rotate every frame (P2-008)"
        )


class TestP2009FrameRateIndependence:
    """P2-009: Movement update methods should accept dt parameter."""

    def test_player_update_accepts_dt(self):
        import player as player_module
        sig = inspect.signature(player_module.Player.update)
        params = list(sig.parameters.keys())
        assert "dt" in params, (
            "Player.update() should accept dt parameter (P2-009). Params: %s" % params
        )

    def test_zombie_update_accepts_dt(self):
        import sprites
        sig = inspect.signature(sprites.Zombie.update)
        params = list(sig.parameters.keys())
        assert "dt" in params, (
            "Zombie.update() should accept dt parameter (P2-009). Params: %s" % params
        )

    def test_bullet_update_accepts_dt(self):
        import sprites
        sig = inspect.signature(sprites.Bullet.update)
        params = list(sig.parameters.keys())
        assert "dt" in params, (
            "Bullet.update() should accept dt parameter (P2-009). Params: %s" % params
        )

    def test_player_movement_scales_with_dt(self):
        import player as player_module
        src = inspect.getsource(player_module.Player.update)
        assert "* dt" in src, (
            "Player movement should multiply by dt for frame-rate independence (P2-009)"
        )

    def test_zombie_movement_scales_with_dt(self):
        import sprites
        src = inspect.getsource(sprites.Zombie.update)
        assert "* dt" in src, (
            "Zombie movement should multiply by dt for frame-rate independence (P2-009)"
        )


class TestP2013SGroupsEncapsulation:
    """P2-013: sGroups should have an encapsulated SpriteGroups class."""

    def test_sgroups_has_spritegroups_class(self):
        import sGroups
        assert hasattr(sGroups, "SpriteGroups"), (
            "sGroups should have a SpriteGroups class (P2-013)"
        )

    def test_sgroups_has_empty_all(self):
        import sGroups
        assert callable(getattr(sGroups, "empty_all", None)), (
            "sGroups should have an empty_all() function (P2-013)"
        )

    def test_empty_all_clears_groups(self):
        import sGroups
        sGroups.zombieSprites.add(pygame.sprite.Sprite())
        assert len(sGroups.zombieSprites) > 0
        sGroups.empty_all()
        assert len(sGroups.zombieSprites) == 0, (
            "empty_all() should clear all sprite groups (P2-013)"
        )

    def test_spritegroups_has_group_names(self):
        import sGroups
        assert hasattr(sGroups.SpriteGroups, "GROUP_NAMES"), (
            "SpriteGroups should define GROUP_NAMES tuple (P2-013)"
        )


class TestP2014AnimateImmutable:
    """P2-014: animate.py dicts should be immutable."""

    def test_animate_offsets_immutable(self):
        import animate
        with pytest.raises(TypeError):
            animate.Animate.offsets["north"] = "tampered"

    def test_animate_image_sizes_immutable(self):
        import animate
        with pytest.raises(TypeError):
            animate.Animate.imageSizes["north"] = "tampered"


class TestP3002NamingConventions:
    """P3-002: Methods should use snake_case, classes PascalCase."""

    def test_gameobject_is_pascal_case(self):
        import sprites
        assert hasattr(sprites, "GameObject"), (
            "sprites.gameObject should be renamed to sprites.GameObject (P3-002)"
        )

    def test_player_methods_are_snake_case(self):
        import player as player_module
        p = player_module.Player
        snake_methods = [
            "image_change", "wall_collide", "apply_offset",
            "stamina_change", "pre_reload", "throw_grenade",
        ]
        for method_name in snake_methods:
            assert hasattr(p, method_name), (
                "Player.%s not found -- should be snake_case (P3-002)" % method_name
            )

    def test_pickup_classes_are_pascal_case(self):
        import pickups
        pascal_classes = [
            "ShotgunPickup", "Mp5Pickup", "GrenadePickup",
            "FoodPickup", "FlameThrower", "HealthBar",
        ]
        for cls_name in pascal_classes[:-1]:
            assert hasattr(pickups, cls_name), (
                "pickups.%s not found -- should be PascalCase (P3-002)" % cls_name
            )


class TestP3003Docstrings:
    """P3-003: Classes should have docstrings."""

    def test_gameobject_has_docstring(self):
        import sprites
        assert sprites.GameObject.__doc__, "GameObject should have a docstring (P3-003)"

    def test_zombie_has_docstring(self):
        import sprites
        assert sprites.Zombie.__doc__, "Zombie should have a docstring (P3-003)"

    def test_player_has_docstring(self):
        import player as player_module
        assert player_module.Player.__doc__, "Player should have a docstring (P3-003)"

    def test_pickup_has_docstring(self):
        import pickups
        assert pickups.Pickup.__doc__, "Pickup should have a docstring (P3-003)"

    def test_bullet_has_docstring(self):
        import sprites
        assert sprites.Bullet.__doc__, "Bullet should have a docstring (P3-003)"

    def test_grenade_has_docstring(self):
        import sprites
        assert sprites.Grenade.__doc__, "Grenade should have a docstring (P3-003)"
