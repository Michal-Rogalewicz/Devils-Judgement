"""The maze: the grid the whole game lives on.

The layout is just text - one character per tile:
    #  wall
    .  a good deed (collect for points + progress to the gate)
    H  a halo power-up (disguises you; angels flee)
    S  a temptation/sin (big points, but it summons another angel)
    G  the gate to heaven (a wall until you've earned enough; then your exit)
    D  the devil's start tile
    (space) empty path, no pickup

Keeping the level as editable data (not code) means you can redesign the whole
map by typing - just keep every row the same width (19 here).
"""

import pygame
import settings

MAZE = [
    "#########G#########",
    "#.................#",
    "#.###.###.###.###.#",
    "#.................#",
    "#####.#.#.#.#.#####",
    "#H...............H#",
    "#.#.#.#.#.#.#.#.#.#",
    "#........S........#",
    "#.###.###.###.###.#",
    "#........D........#",
    "#.................#",
    "#.###.###.###.###.#",
    "#.................#",
    "#####.#.#S#.#.#####",
    "#.................#",
    "#H#.#.#.#.#.#.#.#H#",
    "#.................#",
    "#.###.###.###.###.#",
    "#.................#",
    "#.................#",
    "###################",
]


class Maze:
    def __init__(self):
        self.layout = MAZE
        self.rows = len(MAZE)
        self.cols = len(MAZE[0])
        self.width_px = self.cols * settings.TILE
        self.height_px = self.rows * settings.TILE

        self.deeds = set()
        self.halos = set()
        self.sins = set()
        self.gate = None
        self.devil_spawn = (1, 1)
        self.gate_open = False

        for r, row in enumerate(self.layout):
            for c, char in enumerate(row):
                if char == ".":
                    self.deeds.add((c, r))
                elif char == "H":
                    self.halos.add((c, r))
                elif char == "S":
                    self.sins.add((c, r))
                elif char == "G":
                    self.gate = (c, r)
                elif char == "D":
                    self.devil_spawn = (c, r)

        self.total_deeds = len(self.deeds)

    # --- Queries ---
    def is_wall(self, col, row):
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return True
        if (col, row) == self.gate:
            return not self.gate_open      # the gate is solid until it opens
        return self.layout[row][col] == "#"

    def tile_center(self, col, row):
        return (col * settings.TILE + settings.TILE / 2,
                row * settings.TILE + settings.TILE / 2)

    def deeds_remaining(self):
        return len(self.deeds)

    def collect(self, col, row):
        """If a pickup is on this tile, take it. Returns its type or None."""
        tile = (col, row)
        if tile in self.deeds:
            self.deeds.remove(tile)
            return "deed"
        if tile in self.halos:
            self.halos.remove(tile)
            return "halo"
        if tile in self.sins:
            self.sins.remove(tile)
            return "sin"
        return None

    # --- Drawing ---
    def draw(self, surface):
        t = settings.TILE
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == "#":
                    rect = pygame.Rect(c * t + 2, r * t + 2, t - 4, t - 4)
                    pygame.draw.rect(surface, settings.WALL_COLOR, rect, border_radius=6)

        # Gate: closed bars, or a glowing opening once earned
        if self.gate:
            gc, gr = self.gate
            rect = pygame.Rect(gc * t + 2, gr * t + 2, t - 4, t - 4)
            color = settings.GATE_OPEN if self.gate_open else settings.GATE_CLOSED
            pygame.draw.rect(surface, color, rect, border_radius=6)
            if self.gate_open:
                pygame.draw.rect(surface, (255, 255, 255), rect, width=2, border_radius=6)

        for (c, r) in self.deeds:
            cx, cy = self.tile_center(c, r)
            pygame.draw.circle(surface, settings.DOT_COLOR, (int(cx), int(cy)), 3)

        for (c, r) in self.halos:
            cx, cy = self.tile_center(c, r)
            pygame.draw.circle(surface, settings.HALO_COLOR, (int(cx), int(cy)), 7, 2)

        for (c, r) in self.sins:
            cx, cy = self.tile_center(c, r)
            pygame.draw.circle(surface, settings.SIN_COLOR, (int(cx), int(cy)), 6)