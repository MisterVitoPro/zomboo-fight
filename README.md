# ZOMBOO

A top-down zombie shooter built with Pygame. Supports 1-2 players with controllers, or single-player with keyboard.

## Controls

If a controller is connected, it will be used automatically. Otherwise, keyboard controls are available as a fallback.

### Keyboard Controls

| Key | Action |
|-----|--------|
| W | Move up |
| A | Move left |
| S | Move down |
| D | Move right |
| Arrow Keys | Aim direction (overrides movement direction for firing) |
| Space | Fire weapon |
| T | Reload |
| G | Throw grenade |
| E | Pick up item |
| Left Shift | Sprint (drains stamina) |
| Escape | Quit |

### Controller Controls (Xbox layout)

| Input | Action |
|-------|--------|
| Left Stick | Move |
| Right Stick | Aim direction |
| Right Trigger (pull past halfway) | Fire weapon |
| Right Trigger (light pull) | Sprint (drains stamina) |
| RB (Right Shoulder) | Throw grenade |
| LB (Left Shoulder) | Reload |
| A Button | Pick up item |

### Menu

| Key | Action |
|-----|--------|
| Space | Start game |
| Escape | Quit |

## Running the Game

```bash
python gameLib/main.py
```

## Notes

- Two controllers connected = two-player co-op mode
- One or zero controllers = single-player mode with keyboard fallback
- Stamina regenerates over time; regenerates faster when standing still
- Health above 100 slowly decays back to 100
