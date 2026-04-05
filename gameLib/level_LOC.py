"""ZOMBOO - Level spawn locations and weapon placement coordinates.

Created 2011 by Anthony D'Alessandro.
"""
import random

entiremapLOC = ((random.randrange(100, 700)), random.randrange(100, 500))
# P2-018: Weapon spawn positions are hardcoded pixel coordinates tuned for the
# 800x600 game field. If the screen size or map layout changes these will need
# to be updated manually; there is no data-driven level loading at this time.
topWeaponSpawn = (400, 100)
bottomWeaponSpawn = (400, 500)
rightWeaponSpawn = (650, 300)
leftWeaponSpawn = (150, 300)