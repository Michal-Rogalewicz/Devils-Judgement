#The devil - the player you control.


import pygame
import settings
from entity import Mover


class Devil(Mover):
    def __init__(self, col, row):
        super().__init__(col, row, settings.DEVIL_SPEED)
        self.next_direction = settings.STOP   # the turn you've queued up

    def set_direction(self, direction):
        self.next_direction = direction

    def _decide(self, maze):
        # Prefer your queued turn; otherwise keep going; otherwise stop.
        for d in (self.next_direction, self.direction):
            if d != settings.STOP and not maze.is_wall(self.col + d[0], self.row + d[1]):
                self.start_move(d)
                return
        self.stop()

    def update(self, dt, maze):
        if self.is_moving():
            if self.advance(dt):
                self._decide(maze)
        else:
            self._decide(maze)

    def draw(self, surface, maze):
        pos = self.pixel_pos(maze)
        radius = int(settings.TILE * 0.4)

        # Horns first so the head sits over them
        for sign in (-1, 1):
            tip = (pos.x + sign * radius * 0.55, pos.y - radius * 0.95)
            base_l = (pos.x + sign * radius * 0.2, pos.y - radius * 0.3)
            base_r = (pos.x + sign * radius * 0.8, pos.y - radius * 0.3)
            pygame.draw.polygon(surface, settings.HORN_COLOR, [tip, base_l, base_r])

        pygame.draw.circle(surface, settings.DEVIL_COLOR, (int(pos.x), int(pos.y)), radius)

        for sign in (-1, 1):
            ex = int(pos.x + sign * radius * 0.35)
            ey = int(pos.y - radius * 0.1)
            pygame.draw.circle(surface, settings.EYE_COLOR, (ex, ey), 3)