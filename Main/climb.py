#####corridor clamber w jumpscare
import pygame
import random
import settings


def _draw_keycap(surface, label, cx, cy, font, flashing=False):
    """Draw a keyboard-key style button centred at (cx, cy)."""
    face_color   = (55, 20, 20)  if flashing else (32, 35, 60)
    border_color = settings.LOSE_COLOR if flashing else settings.WALL_COLOR
    ledge_color  = (140, 50, 50) if flashing else (100, 80, 40)

    text_surf = font.render(label, True, (255, 255, 255))
    tw, th = text_surf.get_size()
    kw = max(tw + 36, 56)
    kh = th + 24

    shadow = pygame.Rect(cx - kw // 2 + 4, cy - kh // 2 + 5, kw, kh)
    pygame.draw.rect(surface, (5, 5, 15), shadow, border_radius=10)

    key_rect = pygame.Rect(cx - kw // 2, cy - kh // 2, kw, kh)
    pygame.draw.rect(surface, face_color, key_rect, border_radius=10)

    ledge = pygame.Rect(cx - kw // 2 + 2, cy + kh // 2 - 6, kw - 4, 6)
    pygame.draw.rect(surface, ledge_color, ledge, border_radius=4)

    pygame.draw.rect(surface, border_color, key_rect, width=2, border_radius=10)

    surface.blit(text_surf, text_surf.get_rect(center=(cx, cy - 1)))


#######-> the devil (player) moves forward n morphs on win
class Player:
    def __init__(self):
        self.step = 0
        self.hits = 0
        self.max_hits = 3
        self.morph_progress = 0.0
        self.morphing = False
        self.ascension_y_offset = 0.0

        # jumpscare stuff
        self.jumpscare_timer = 0.0
        self.jumpscare_angel_scale = 0.0

        # fall stuff
        self.falling = False
        self.fall_velocity = 0.0
        self.fall_y = 0.0

    def move_forward(self):
        if self.step < settings.CLIMB_STEPS:
            self.step += 1
            return True
        return False

    def take_hit(self):
        self.hits += 1
        self.jumpscare_timer = 0.3
        self.jumpscare_angel_scale = 0.0
        if self.hits >= self.max_hits:
            self.start_fall()

    def start_fall(self):
        self.falling = True
        self.fall_velocity = -300.0  # pixels/sec upward (bounces up then falls)
        self.fall_y = 0.0

    def start_ascension(self):
        self.morphing = True
        self.morph_progress = 0.0
        self.ascension_y_offset = 0.0

    def update(self, dt):
        if self.jumpscare_timer > 0:
            self.jumpscare_timer -= dt
            self.jumpscare_angel_scale += dt * 8.0
            if self.jumpscare_angel_scale > 1.0:
                self.jumpscare_angel_scale = 1.0

        if self.morphing:
            self.morph_progress += dt * 0.5
            self.ascension_y_offset -= dt * 150
            if self.morph_progress >= 1.0:
                self.morph_progress = 1.0
                self.morphing = False

        if self.falling:
            self.fall_velocity += 1800 * dt   # gravity in pixels/sec²
            self.fall_y += self.fall_velocity * dt
            if self.fall_y > 600:
                self.fall_y = 600

    def draw(self, surface, current_key, font_large, font_medium, flash=False):
        w, h = surface.get_size()
        base_x, base_y = w // 2, int(h * 0.78)
        if self.falling:
            y = base_y + self.fall_y
        elif self.morphing or self.morph_progress > 0:
            y = base_y + self.ascension_y_offset
        else:
            y = base_y
        x = base_x
        r = settings.CLIMB_SIZE

        if not self.morphing and not self.falling and current_key:
            if not flash or int(pygame.time.get_ticks() / 200) % 2 == 0:
                _draw_keycap(surface, current_key, x, y - r - 52, font_large, flashing=flash)

        if self.morphing or self.morph_progress > 0:
            p = self.morph_progress
            devil_c = settings.DEVIL_COLOR
            angel_c = settings.ANGEL_COLOR
            body_colour = (
                int(devil_c[0] + (angel_c[0] - devil_c[0]) * p),
                int(devil_c[1] + (angel_c[1] - devil_c[1]) * p),
                int(devil_c[2] + (angel_c[2] - devil_c[2]) * p)
            )
            if p < 0.5:
                self._draw_devil(surface, x, y, r, body_colour)
            else:
                self._draw_angel(surface, x, y, r, body_colour)
        else:
            self._draw_devil(surface, x, y, r, settings.DEVIL_COLOR)

        if self.jumpscare_timer > 0:
            size = int(200 * self.jumpscare_angel_scale)
            flash_surf = pygame.Surface((w, h))
            flash_surf.fill((255, 0, 0))
            flash_surf.set_alpha(int(140 * self.jumpscare_timer * 3))
            surface.blit(flash_surf, (0, 0))
            if size > 20:
                self._draw_angel(surface, w//2, h//2, size, settings.LOSE_COLOR)

    def _draw_devil(self, surface, x, y, r, colour):
        horn_h = 5
        pygame.draw.polygon(surface, settings.HORN_COLOR, [(x - r + 8, y - r + 5), (x - r + 14, y - r - horn_h), (x - r + 20, y - r + 5)])
        pygame.draw.polygon(surface, settings.HORN_COLOR, [(x + r - 20, y - r + 5), (x + r - 14, y - r - horn_h), (x + r - 8, y - r + 5)])
        pygame.draw.circle(surface, colour, (x, y), r)
        pygame.draw.circle(surface, settings.EYE_COLOR, (x - r//2, y - 2), 3)
        pygame.draw.circle(surface, settings.EYE_COLOR, (x + r//2, y - 2), 3)

    def _draw_angel(self, surface, x, y, r, colour=None):
        if colour is None:
            colour = settings.ANGEL_COLOR
        pygame.draw.circle(surface, colour, (x, y - 5), r)
        pygame.draw.polygon(surface, colour, [(x - r, y - 5), (x + r, y - 5), (x, y + r + 5)])
        halo_width = r + 4
        halo_height = r - 2
        halo_rect = pygame.Rect(x - halo_width//2, y - r - 10 - halo_height//2, halo_width, halo_height)
        pygame.draw.ellipse(surface, settings.ANGEL_HALO, halo_rect, 2)

#######-> the minigame itself
class ClimbGame:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player = None
        self.keys = []
        self.current_key = None
        self.start_time = 0
        self.game_state = settings.CLIMB_STATE_START
        self.message = ""
        self.time_left = settings.CLIMB_TIME_LIMIT
        self.phase_timer = 0
        self.phase = 0
        self.done = False
        self.speed_multiplier = 1.0

        self.font_large = None
        self.font_medium = None
        self.font_small = None

    def set_fonts(self, large, medium, small):
        self.font_large = large
        self.font_medium = medium
        self.font_small = small

    def generate_keys(self):
        return [None] + [random.choice(settings.CLIMB_KEY_NAMES) for _ in range(settings.CLIMB_STEPS)]

    def start(self):
        self.player = Player()
        self.keys = self.generate_keys()
        self.current_key = self.keys[1] if settings.CLIMB_STEPS > 0 else None
        self.start_time = pygame.time.get_ticks()
        self.game_state = settings.CLIMB_STATE_PLAYING
        self.time_left = settings.CLIMB_TIME_LIMIT
        self.phase = 0
        self.phase_timer = 0
        self.done = False
        self.speed_multiplier = 1.0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.game_state == settings.CLIMB_STATE_START:
            if event.key == pygame.K_SPACE:
                self.start()
            return
        if self.game_state == settings.CLIMB_STATE_PLAYING:
            key_name = settings.CLIMB_VALID_KEYS.get(event.key)
            if key_name:
                next_step = self.player.step + 1
                expected = self.keys[next_step] if next_step <= settings.CLIMB_STEPS else None
                if expected and key_name == expected:
                    if self.player.move_forward():
                        if self.player.step >= settings.CLIMB_STEPS:
                            self.game_state = settings.CLIMB_STATE_WON
                            self.player.start_ascension()
                            self.message = "YOU ASCENDED"
                            self.phase_timer = pygame.time.get_ticks()
                            self.phase = 0
                        else:
                            self.current_key = self.keys[self.player.step + 1]
                else:
                    self.player.take_hit()
                    if self.player.hits >= self.player.max_hits:
                        self.game_state = settings.CLIMB_STATE_LOST
                        self.player.start_fall()
                        self.message = "YOU FELL"
                        self.phase_timer = pygame.time.get_ticks()
                        self.phase = 0
                    else:
                        self.current_key = self.keys[self.player.step + 1]

    def update(self, dt):
        if not self.player:
            return
        self.player.update(dt)

        if self.game_state == settings.CLIMB_STATE_PLAYING:
            self.speed_multiplier += dt * 0.02
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            self.time_left = max(0, settings.CLIMB_TIME_LIMIT - elapsed * self.speed_multiplier)
            if self.time_left <= 0:
                self.game_state = settings.CLIMB_STATE_LOST
                self.player.start_fall()
                self.message = "YOU FELL"
                self.phase_timer = pygame.time.get_ticks()
                self.phase = 0

        elif self.game_state in [settings.CLIMB_STATE_WON, settings.CLIMB_STATE_LOST]:
            elapsed = pygame.time.get_ticks() - self.phase_timer
            if elapsed < 2000:
                self.phase = 0
            elif elapsed < 4000:
                self.phase = 1
            else:
                self.phase = 2
                self.done = True

    def draw(self, surface):
        if self.font_large is None:
            return

        if self.game_state == settings.CLIMB_STATE_START:
            self._draw_start(surface)
            return

        if self.game_state in [settings.CLIMB_STATE_WON, settings.CLIMB_STATE_LOST]:
            if self.phase == 0:
                surface.fill(settings.BG_COLOR)
                self._draw_scene(surface)
                self.player.draw(surface, None, self.font_large, self.font_medium, False)
                hint = self.font_small.render(
                    "Ascending..." if self.game_state == settings.CLIMB_STATE_WON else "Falling...",
                    True, settings.TEXT_COLOR
                )
                hint_rect = hint.get_rect(center=(self.screen_width//2, 40))
                surface.blit(hint, hint_rect)
            elif self.phase == 1:
                surface.fill(settings.BG_COLOR)
                msg = self.font_large.render(self.message, True, settings.WIN_COLOR if self.game_state == settings.CLIMB_STATE_WON else settings.LOSE_COLOR)
                msg_rect = msg.get_rect(center=(self.screen_width//2, self.screen_height//2))
                surface.blit(msg, msg_rect)
            return

        surface.fill(settings.BG_COLOR)
        self._draw_scene(surface)
        flash = self.time_left < 3
        self.player.draw(surface, self.current_key, self.font_large, self.font_medium, flash)
        self._draw_ui(surface)

    def _draw_scene(self, surface):
        w, h = surface.get_size()
        center_x = w // 2

        # background gradient
        for i in range(h):
            shade = int(10 + (i / h) * 20)
            pygame.draw.line(surface, (shade, shade, shade + 10), (0, i), (w, i))

        # perspective path of "maze wall" trapezoids
        vp_y = int(h * 0.25)
        num_tiles = 12
        tile_width_bottom = 200
        tile_width_top = 40
        offset = self.player.step * 0.1

        for i in range(num_tiles):
            t = (i + offset) / num_tiles
            depth = 1.0 - t
            y_bottom = h - depth * (h - vp_y)
            y_top = h - (depth - 0.08) * (h - vp_y) if depth > 0.08 else h
            width = tile_width_bottom - depth * (tile_width_bottom - tile_width_top)
            left = center_x - width/2
            right = center_x + width/2
            colour = settings.WALL_COLOR if i % 2 == 0 else (settings.WALL_COLOR[0]-20, settings.WALL_COLOR[1]-20, settings.WALL_COLOR[2]-20)
            points = [(left, y_bottom), (right, y_bottom), (right, y_top), (left, y_top)]
            pygame.draw.polygon(surface, colour, points)
            pygame.draw.polygon(surface, settings.DIM_TEXT, points, 2)

        # door that grows with step
        progress = self.player.step / settings.CLIMB_STEPS if self.player else 0
        if self.game_state == settings.CLIMB_STATE_WON:
            progress = 1.0
        scale = 0.15 + progress * 0.85
        door_width = int(160 * scale)
        door_height = int(220 * scale)
        door_x = center_x - door_width // 2
        door_y = int(h * 0.15)

        # frame
        frame_rect = pygame.Rect(door_x - 8, door_y - 8, door_width + 16, door_height + 16)
        pygame.draw.rect(surface, settings.GATE_CLOSED, frame_rect, border_radius=8)

        # door
        is_open = progress >= 1.0
        door_colour = settings.GATE_OPEN if is_open else (200, 180, 100)
        door_rect = pygame.Rect(door_x, door_y, door_width, door_height)
        pygame.draw.rect(surface, door_colour, door_rect, border_radius=4)

        if not is_open:
            bar_width = 4
            for i in range(3):
                x = door_x + door_width // 4 + i * (door_width // 4)
                pygame.draw.line(surface, (100, 80, 40), (x, door_y + 20), (x, door_y + door_height - 20), bar_width)
            pygame.draw.circle(surface, (180, 160, 80), (center_x, door_y + door_height//2), 8)
        else:
            glow = pygame.Surface((door_width + 40, door_height + 40))
            glow.fill((255, 215, 100))
            glow.set_alpha(100)
            surface.blit(glow, (door_x - 20, door_y - 20), special_flags=pygame.BLEND_RGB_ADD)

        # handles
        handle_y = door_y + door_height // 2
        pygame.draw.circle(surface, settings.WALL_COLOR, (door_x + 20, handle_y), max(4, int(6 * scale)))
        pygame.draw.circle(surface, settings.WALL_COLOR, (door_x + door_width - 20, handle_y), max(4, int(6 * scale)))

    def _draw_ui(self, surface):
        hud_bg = pygame.Surface((self.screen_width, settings.HUD_HEIGHT))
        hud_bg.fill((0, 0, 0))
        hud_bg.set_alpha(130)
        surface.blit(hud_bg, (0, self.screen_height - settings.HUD_HEIGHT))

        step_text = self.font_medium.render(f"STEP: {self.player.step}/{settings.CLIMB_STEPS}", True, settings.TEXT_COLOR)
        surface.blit(step_text, (16, self.screen_height - settings.HUD_HEIGHT + 12))

        hearts = ""
        for i in range(self.player.max_hits):
            hearts += "♥" if i < self.player.max_hits - self.player.hits else "♡"
        heart_text = self.font_large.render(hearts, True, settings.LOSE_COLOR)
        heart_rect = heart_text.get_rect(center=(self.screen_width//2, self.screen_height - settings.HUD_HEIGHT//2))
        surface.blit(heart_text, heart_rect)

        time_colour = settings.TEXT_COLOR if self.time_left > 3 else settings.LOSE_COLOR
        time_text = self.font_medium.render(f"⏱ {self.time_left:.1f}s", True, time_colour)
        time_rect = time_text.get_rect(topright=(self.screen_width - 16, self.screen_height - settings.HUD_HEIGHT + 12))
        surface.blit(time_text, time_rect)

        if self.game_state == settings.CLIMB_STATE_PLAYING:
            speed_text = self.font_small.render(f"speed ×{self.speed_multiplier:.1f}", True, settings.DIM_TEXT)
            speed_rect = speed_text.get_rect(topright=(self.screen_width - 16, self.screen_height - 10))
            surface.blit(speed_text, speed_rect)

    def _draw_start(self, surface):
        surface.fill(settings.BG_COLOR)
        cx = self.screen_width // 2
        title = self.font_large.render("THE ASCENT", True, settings.WALL_COLOR)
        subtitle = self.font_medium.render("Climb through the corridor", True, settings.TEXT_COLOR)
        instructions = [
            "Press the key shown above the devil",
            "Right key = move forward",
            "Wrong key = angel jumpscare (lose a heart)",
            f"Time Limit: {settings.CLIMB_TIME_LIMIT} seconds",
            "The climb gets faster over time...",
            "",
            "Press SPACE to begin"
        ]
        title_rect = title.get_rect(center=(cx, self.screen_height//3 - 20))
        subtitle_rect = subtitle.get_rect(center=(cx, self.screen_height//3 + 40))
        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)
        y = self.screen_height//2 + 20
        for line in instructions:
            text = self.font_small.render(line, True, settings.TEXT_COLOR)
            text_rect = text.get_rect(center=(cx, y))
            surface.blit(text, text_rect)
            y += 30


if __name__ == "__main__":
    pygame.init()
    W, H = 532, 644
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("The Ascent")
    clock = pygame.time.Clock()

    game = ClimbGame(W, H)
    game.set_fonts(
        pygame.font.SysFont("consolas", 40, bold=True),
        pygame.font.SysFont("consolas", 22),
        pygame.font.SysFont("consolas", 17),
    )

    running = True
    while running:
        dt = clock.tick(settings.FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    game.handle_event(event)
        game.update(dt)
        game.draw(screen)
        pygame.display.flip()
        if game.done:
            running = False

    pygame.quit()