#The angels - the hunters.

import random
import settings
from entity import Mover


class Angel(Mover):
    def __init__(self, col, row):
        super().__init__(col, row, settings.ANGEL_SPEED)
        self.spawn = (col, row)

    def set_scared(self, scared):
        self.speed = settings.ANGEL_SCARED_SPEED if scared else settings.ANGEL_SPEED

    def reset(self):
        """Send the angel home (after being redeemed)."""
        self.col, self.row = self.spawn
        self.stop()

    @staticmethod
    def _dist2(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    def _decide(self, maze, devil, mode):
        options = self.valid_directions(maze, allow_reverse=False)
        if not options:                       # dead end: turning back is allowed
            options = self.valid_directions(maze, allow_reverse=True)
        if not options:
            self.stop()
            return

        target = (devil.col, devil.row)
        if mode == settings.CHASE:
            # Pick the exit whose next tile lands closest to the devil.
            choice = min(options, key=lambda d: self._dist2(
                (self.col + d[0], self.row + d[1]), target))
        elif mode == settings.FRIGHTENED:
            # Flee: pick the exit that gets *furthest* from the devil.
            choice = max(options, key=lambda d: self._dist2(
                (self.col + d[0], self.row + d[1]), target))
        else:  # SCATTER
            choice = random.choice(options)
        self.start_move(choice)

    def update(self, dt, maze, devil, mode):
        if self.is_moving():
            if self.advance(dt):
                self._decide(maze, devil, mode)
        else:
            self._decide(maze, devil, mode)

    def draw(self, surface, maze, scared):
        import pygame
        pos = self.pixel_pos(maze)
        radius = int(settings.TILE * 0.4)
        body = settings.ANGEL_SCARED if scared else settings.ANGEL_COLOR
        pygame.draw.circle(surface, body, (int(pos.x), int(pos.y)), radius)
        if not scared:
            pygame.draw.circle(surface, settings.ANGEL_HALO,
                               (int(pos.x), int(pos.y - radius * 1.15)),
                               radius // 2, 2)
        else:
            # little frightened eyes
            for sign in (-1, 1):
                pygame.draw.circle(surface, (255, 255, 255),
                                   (int(pos.x + sign * radius * 0.35),
                                    int(pos.y - radius * 0.1)), 3)