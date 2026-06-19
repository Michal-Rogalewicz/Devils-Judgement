#Game - orchestrates everything.

import pygame
import settings
from maze import Maze
from player import Devil
from angel import Angel
from climb import ClimbGame   ###:) <-- 

ANGEL_SPAWNS = [(1, 1), (17, 1), (1, 19), (17, 19)]
START_ANGELS = 3


class Game:
    def __init__(self):
        pygame.init()
        self.reset()
        self.screen = pygame.display.set_mode(
            (self.maze.width_px, self.maze.height_px + settings.HUD_HEIGHT)
        )
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.big = pygame.font.SysFont("consolas", 40, bold=True)
        self.mid = pygame.font.SysFont("consolas", 22)
        self.small = pygame.font.SysFont("consolas", 17)
        self.state = settings.MENU
        self.running = True
        self.climb_game = None   # <

    # ---------------------------------------------------------------- setup
    def reset(self):
        """Start a fresh round: rebuild the maze and reset everyone."""
        self.maze = Maze()
        self.target = int(self.maze.total_deeds * settings.DOT_POINTS
                          * settings.REDEMPTION_FRACTION)
        self.score = 0
        self.lives = settings.START_LIVES
        self.devil = Devil(*self.maze.devil_spawn)
        self.angels = [Angel(*ANGEL_SPAWNS[i]) for i in range(START_ANGELS)]
        self.base_mode = settings.SCATTER
        self.mode_timer = settings.SCATTER_TIME
        self.scared_timer = 0.0
        self.flash = 0.0
        self.spawn_cycle = START_ANGELS

    def _reset_positions(self):
        """After losing a life: everyone back to start, but keep the maze."""
        self.devil = Devil(*self.maze.devil_spawn)
        for a in self.angels:
            a.reset()
            a.set_scared(False)
        self.scared_timer = 0.0
        self.base_mode = settings.SCATTER
        self.mode_timer = settings.SCATTER_TIME
        self.flash = 0.4

    # ---------------------------------------------------------------- events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == settings.CLIMB:
                    self.climb_game.handle_event(event)
                else:
                    self._on_key(event.key)

    def _on_key(self, key):
        if self.state == settings.MENU:
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.reset()
                self.state = settings.PLAYING
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == settings.PLAYING:
            if key in (pygame.K_w, pygame.K_UP):
                self.devil.set_direction(settings.UP)
            elif key in (pygame.K_s, pygame.K_DOWN):
                self.devil.set_direction(settings.DOWN)
            elif key in (pygame.K_a, pygame.K_LEFT):
                self.devil.set_direction(settings.LEFT)
            elif key in (pygame.K_d, pygame.K_RIGHT):
                self.devil.set_direction(settings.RIGHT)
            elif key == pygame.K_p:
                self.state = settings.PAUSED
            elif key == pygame.K_ESCAPE:
                self.state = settings.MENU

        elif self.state == settings.PAUSED:
            if key in (pygame.K_p, pygame.K_SPACE):
                self.state = settings.PLAYING
            elif key == pygame.K_ESCAPE:
                self.state = settings.MENU

        elif self.state == settings.WIN:
            # we no longer go directly to win; we transition to climb
            # but if we are already at final win, this will handle menu
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = settings.MENU
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == settings.LOSE:
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.state = settings.MENU
            elif key == pygame.K_ESCAPE:
                self.running = False

    # ---------------------------------------------------------------- update
    def update(self, dt):
        if self.state == settings.PLAYING:
            self._update_playing(dt)

        elif self.state == settings.CLIMB:
            self.climb_game.update(dt)
            if self.climb_game.done:
                if self.climb_game.game_state == settings.CLIMB_STATE_WON:
                    self.state = settings.WIN
                else:
                    self.state = settings.LOSE
                self.climb_game = None

    def _update_playing(self, dt):
        self._update_modes(dt)
        mode = settings.FRIGHTENED if self.scared_timer > 0 else self.base_mode

        self.devil.update(dt, self.maze)
        self._collect_pickup()
        self._open_gate_if_earned()

        for a in self.angels:
            a.update(dt, self.maze, self.devil, mode)

        self._check_collisions()
        self._check_win()

        if self.flash > 0:
            self.flash -= dt

    def _update_modes(self, dt):
        if self.scared_timer > 0:
            self.scared_timer -= dt
            if self.scared_timer <= 0:
                for a in self.angels:
                    a.set_scared(False)
        else:
            self.mode_timer -= dt
            if self.mode_timer <= 0:
                if self.base_mode == settings.SCATTER:
                    self.base_mode, self.mode_timer = settings.CHASE, settings.CHASE_TIME
                else:
                    self.base_mode, self.mode_timer = settings.SCATTER, settings.SCATTER_TIME

    def _collect_pickup(self):
        kind = self.maze.collect(self.devil.col, self.devil.row)
        if kind == "deed":
            self.score += settings.DOT_POINTS
        elif kind == "halo":
            self.score += settings.HALO_POINTS
            self.scared_timer = settings.HALO_DURATION
            for a in self.angels:
                a.set_scared(True)
        elif kind == "sin":
            self.score += settings.SIN_POINTS
            self._spawn_extra_angels(settings.SIN_PENALTY_ANGELS)

    def _spawn_extra_angels(self, n):
        for _ in range(n):
            if len(self.angels) >= settings.MAX_ANGELS:
                return
            spot = ANGEL_SPAWNS[self.spawn_cycle % len(ANGEL_SPAWNS)]
            self.spawn_cycle += 1
            new = Angel(*spot)
            new.set_scared(self.scared_timer > 0)
            self.angels.append(new)

    def _open_gate_if_earned(self):
        if not self.maze.gate_open and self.score >= self.target:
            self.maze.gate_open = True

    def _check_collisions(self):
        dpos = self.devil.pixel_pos(self.maze)
        for a in self.angels:
            if dpos.distance_to(a.pixel_pos(self.maze)) < settings.TILE * 0.5:
                if self.scared_timer > 0:
                    a.reset()
                    self.score += settings.REDEEM_POINTS
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = settings.LOSE
                    else:
                        self._reset_positions()
                    return

    def _check_win(self):
        if self.maze.gate_open and (self.devil.col, self.devil.row) == self.maze.gate:
            # transition to climb minigame instead of showing win screen
            self._start_climb_minigame()

    def _start_climb_minigame(self):
        self.climb_game = ClimbGame(self.maze.width_px, self.maze.height_px + settings.HUD_HEIGHT)
        self.climb_game.set_fonts(self.big, self.mid, self.small)
        self.state = settings.CLIMB

    # ---------------------------------------------------------------- draw
    def draw(self):
        self.screen.fill(settings.BG_COLOR)

        if self.state == settings.MENU:
            self._draw_menu()
        elif self.state in (settings.PLAYING, settings.PAUSED):
            self._draw_play()
            if self.state == settings.PAUSED:
                self._overlay("PAUSED", "P or SPACE to resume", settings.TEXT_COLOR)
        elif self.state == settings.WIN:
            self._overlay("YOU ASCENDED", f"Score {self.score}   -   SPACE for menu",
                          settings.WIN_COLOR)
        elif self.state == settings.LOSE:
            self._overlay("CAST BACK TO HELL", f"Score {self.score}   -   SPACE for menu",
                          settings.LOSE_COLOR)
        elif self.state == settings.CLIMB:
            self.climb_game.draw(self.screen)

        pygame.display.flip()

    def _draw_play(self):
        self.maze.draw(self.screen)
        for a in self.angels:
            blink = self.scared_timer > 0 and (self.scared_timer > 1.5
                                               or int(self.scared_timer * 8) % 2 == 0)
            a.draw(self.screen, self.maze, blink)
        self.devil.draw(self.screen, self.maze)

        if self.flash > 0:                       # quick red flash on a life lost
            overlay = pygame.Surface(self.screen.get_size())
            overlay.set_alpha(int(120 * (self.flash / 0.4)))
            overlay.fill((180, 30, 30))
            self.screen.blit(overlay, (0, 0))

        self._draw_hud()

    def _draw_hud(self):
        y0 = self.maze.height_px + 6
        y1 = self.maze.height_px + 30
        left = self.small.render(f"Score: {self.score}    Lives: {self.lives}",
                                 True, settings.TEXT_COLOR)
        self.screen.blit(left, (12, y0))

        if self.maze.gate_open:
            gate = self.small.render("GATES OPEN - reach the top!", True, settings.WIN_COLOR)
        else:
            gate = self.small.render(f"To open gate: {self.score} / {self.target}",
                                     True, settings.DIM_TEXT)
        self.screen.blit(gate, (12, y1))

        if self.scared_timer > 0:
            tag = self.small.render(f"DISGUISED {self.scared_timer:0.1f}s",
                                    True, settings.ANGEL_SCARED)
            self.screen.blit(tag, (self.maze.width_px - tag.get_width() - 12, y0))

    def _draw_menu(self):
        cx = self.screen.get_width() // 2
        self._center(self.big, "Devils Judgement", cx, 70, settings.WALL_COLOR)
        self._center(self.mid, "A devil sneaks into heaven", cx, 115, settings.DIM_TEXT)
        lines = [
            "Collect good deeds to earn your way to the gate.",
            "Grab a halo to disguise yourself - angels flee, and",
            "you can redeem them on contact.",
            "Temptations are worth big points... but each one",
            "summons another angel. Greed has a price.",
            "",
            "WASD / arrows to move    P to pause",
        ]
        y = 175
        for ln in lines:
            self._center(self.small, ln, cx, y, settings.TEXT_COLOR)
            y += 26
        self._center(self.mid, "Press SPACE to begin", cx, y + 20, settings.WIN_COLOR)

    def _overlay(self, title, subtitle, color):
        cx = self.screen.get_width() // 2
        cy = self.screen.get_height() // 2
        self._center(self.big, title, cx, cy - 30, color)
        self._center(self.mid, subtitle, cx, cy + 20, settings.TEXT_COLOR)

    def _center(self, font, text, cx, cy, color):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))

    # ---------------------------------------------------------------- loop
    def run(self):
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()