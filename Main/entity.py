#Mover - the shared movement engine for the devil and the angels.

import pygame
import settings


class Mover:
    def __init__(self, col, row, speed):
        self.col = col
        self.row = row
        self.target = (col, row)
        self.progress = 0.0
        self.direction = settings.STOP
        self.speed = speed

    def is_moving(self):
        return self.target != (self.col, self.row)

    @staticmethod
    def opposite(direction):
        return (-direction[0], -direction[1])

    def valid_directions(self, maze, allow_reverse=True):
        """Directions from the current tile that aren't blocked by walls."""
        options = []
        for d in (settings.UP, settings.DOWN, settings.LEFT, settings.RIGHT):
            if not maze.is_wall(self.col + d[0], self.row + d[1]):
                options.append(d)
        # Stop characters spinning on the spot: drop the reverse unless it's a
        # genuine dead end (only one way out).
        if not allow_reverse and self.direction != settings.STOP and len(options) > 1:
            rev = self.opposite(self.direction)
            options = [d for d in options if d != rev]
        return options

    def start_move(self, direction):
        self.direction = direction
        self.target = (self.col + direction[0], self.row + direction[1])
        self.progress = 0.0

    def stop(self):
        self.direction = settings.STOP
        self.target = (self.col, self.row)
        self.progress = 0.0

    def advance(self, dt):
        """Slide toward the target. Returns True on the frame we arrive."""
        if not self.is_moving():
            return False
        self.progress += self.speed * dt
        if self.progress >= 1.0:
            self.col, self.row = self.target
            self.progress = 0.0
            return True
        return False

    def pixel_pos(self, maze):
        """Centre in pixels, interpolated between tiles for smooth motion."""
        ax, ay = maze.tile_center(self.col, self.row)
        bx, by = maze.tile_center(*self.target)
        return pygame.Vector2(ax + (bx - ax) * self.progress,
                              ay + (by - ay) * self.progress)