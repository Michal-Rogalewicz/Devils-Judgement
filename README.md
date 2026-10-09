# Devils Judgement

A Pac-Man-style maze game built with Python and Pygame, with a twist: you play a **devil sneaking into heaven**. Collect good deeds to earn your way to the gate, dodge the angels hunting you, then survive a frantic key-mashing climb to ascend.

## Gameplay

The game has two stages.

### 1. The maze
- **Collect good deeds** (white dots) to build up your score. Once you've earned enough points, the gate at the top of the maze opens.
- **Avoid the angels.** They alternate between wandering (scatter) and hunting you down (chase). Touching one costs a life.
- **Grab a halo** (gold ring) to disguise yourself. For a few seconds the angels turn blue and flee, and you can **redeem** them on contact for bonus points.
- **Temptations** (pink orbs) are worth big points, but each one summons another angel, up to a maximum of 6. Greed has a price.
- Once the gate is open, reach it to start the climb.

### 2. The Ascent
A timed mini-game: press the key shown above the devil to climb towards the door.

- The right key moves you forward and a wrong key triggers an angel jumpscare and costs a heart.
- You have 3 hearts and 20 seconds, and the clock speeds up as you climb.
- Reach the top to **ascend** and win. Run out of hearts or time and you're **cast back to hell**.

## Controls

| Action | Keys |
| --- | --- |
| Move | `W` `A` `S` `D` or arrow keys |
| Pause / resume | `P` (resume also with `Space`) |
| Start / confirm | `Space` or `Enter` |
| Back to menu / quit | `Esc` |
| Climb mini-game | The `WASD` / arrow key shown on screen |

## Getting started

### Requirements
- Python 3.9 or newer
- [Pygame](https://www.pygame.org/)

### Install and run

```bash
git clone https://github.com/Michal-Rogalewicz/Devils-Judgement.git
cd Devils-Judgement
pip install pygame
cd Main
python main.py
```

Run it from inside the `Main` folder, because the modules import each other directly.

You can also try the climb mini-game on its own:

```bash
python climb.py
```

## Project structure

```
Main/
├── main.py       # Entry point
├── game.py       # Game rules, states (menu / play / pause / climb / win / lose), scoring, drawing
├── settings.py   # All tweakable constants: speeds, colours, scoring, rules
├── maze.py       # The level layout (editable text grid), pickups and the gate
├── entity.py     # Mover: shared tile-to-tile movement for the devil and angels
├── player.py     # Devil: the player character
├── angel.py      # Angel: enemy AI (scatter, chase, frightened)
└── climb.py      # The Ascent mini-game
```

## Customising the game

- **Tweak the rules** in `settings.py`: movement speeds, starting lives, halo duration, the maximum number of angels, how much of the score is needed to open the gate, and the climb length and time limit.
- **Design your own level** by editing the `MAZE` grid in `maze.py`:

  | Character | Meaning |
  | --- | --- |
  | `#` | Wall |
  | `.` | Good deed |
  | `H` | Halo |
  | `S` | Temptation |
  | `D` | Devil start |
  | `G` | Gate |

## How it works

- The maze is a tile grid and every character moves tile to tile with smooth interpolation (`Mover`).
- Angels pick a direction at each junction. In **chase** mode they head for the tile closest to you, in **frightened** mode they pick the tile furthest away, and in **scatter** mode they wander randomly. They never turn back on themselves unless they hit a dead end.
- Scatter and chase alternate on a timer (5 s scatter, 18 s chase), as in classic arcade maze games.
