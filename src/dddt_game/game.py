from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from .config import CONFIG
from .entities import PlayerCar, spawn_obstacle
from .phone import PhoneSystem


@dataclass
class GameStats:
    survived_seconds: float = 0.0
    dodged_cars: int = 0
    texts_sent: int = 0


class DontDrinkDriveTextGame:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Dont Drink & Drive & Text")
        self.screen = pygame.display.set_mode((CONFIG.screen_width, CONFIG.screen_height))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("Segoe UI", 34, bold=True)
        self.body_font = pygame.font.SysFont("Segoe UI", 24)
        self.small_font = pygame.font.SysFont("Segoe UI", 20)

        lane_width = (CONFIG.road_width - (CONFIG.lane_padding * 2)) // CONFIG.lane_count
        self.lane_centers = [
            CONFIG.lane_padding + lane_width // 2 + i * lane_width
            for i in range(CONFIG.lane_count)
        ]

        self.road_rect = pygame.Rect(0, 0, CONFIG.road_width, CONFIG.screen_height)
        self.phone_rect = pygame.Rect(
            CONFIG.road_width + 16,
            18,
            CONFIG.phone_panel_width - 32,
            CONFIG.screen_height - 36,
        )

        self.reset_game()

    def reset_game(self) -> None:
        self.player = PlayerCar(
            lane_index=1,
            lane_centers=self.lane_centers,
            y=CONFIG.screen_height - 160,
        )
        self.obstacles = []
        self.spawn_timer = 0.0
        self.road_scroll = 0.0
        self.world_speed = CONFIG.initial_world_speed
        self.drunk_meter = 8.0
        self.drink_prompt_timer = 10.5
        self.drink_prompt_active = False
        self.phone = PhoneSystem(CONFIG.objective_texts_required)
        self.stats = GameStats()
        self.mood_particles = []
        self.crashed = False
        self.crash_reason = ""
        self.final_overlay_time = 0.0

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(CONFIG.fps) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if not self.crashed:
                        self.handle_keydown(event)
                    if self.crashed and event.key == pygame.K_r:
                        self.reset_game()
                    if event.key == pygame.K_ESCAPE:
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.crashed and self.phone_rect.collidepoint(event.pos):
                        success = self.phone.process_click(event.pos)
                        if success:
                            self.stats.texts_sent = self.phone.completed
                            self.spawn_happy_particles()

            if not self.crashed:
                self.update(dt)
            else:
                self.final_overlay_time += dt

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.player.set_target_lane_left()
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player.set_target_lane_right()
        elif event.key == pygame.K_SPACE:
            self.drink_prompt_active = False
            self.drunk_meter = min(100.0, self.drunk_meter + random.uniform(3.2, 6.2))
            self.spawn_happy_particles()

    def update(self, dt: float) -> None:
        self.stats.survived_seconds += dt
        self.world_speed = min(CONFIG.max_world_speed, self.world_speed + dt * 2.1)
        self.drunk_meter = min(100.0, self.drunk_meter + dt * 0.6)

        self.drink_prompt_timer -= dt
        if self.drink_prompt_timer <= 0:
            self.drink_prompt_active = True
            self.drink_prompt_timer = random.uniform(9.0, 13.0)
            self.drunk_meter = min(100.0, self.drunk_meter + 2.0)

        self.spawn_timer += dt
        spawn_interval = max(0.55, CONFIG.obstacle_spawn_interval - (self.world_speed - CONFIG.initial_world_speed) / 1300)
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0
            self.obstacles.append(spawn_obstacle(self.lane_centers, self.world_speed))

        for obstacle in self.obstacles:
            obstacle.update(dt)

        remaining = []
        for obstacle in self.obstacles:
            if obstacle.rect.top > CONFIG.screen_height + 20:
                self.stats.dodged_cars += 1
            else:
                remaining.append(obstacle)
        self.obstacles = remaining

        if self.drunk_meter > 70 and random.random() < dt * (self.drunk_meter / 420):
            if random.random() > 0.5:
                self.player.set_target_lane_left()
            else:
                self.player.set_target_lane_right()

        self.player.update(dt)

        for obstacle in self.obstacles:
            if obstacle.rect.colliderect(self.player.rect.inflate(-10, -8)):
                self.trigger_crash("Du kolliderte med en annen bil.")

        if self.drunk_meter >= 100:
            self.trigger_crash("Sterk beruselse førte til total kontrollsvikt.")

        if self.stats.survived_seconds >= CONFIG.inevitable_crash_time:
            self.trigger_crash("Tretthet og beruselse endte i en uunngåelig ulykke.")

        self.phone.update(dt)
        self.update_particles(dt)

    def trigger_crash(self, reason: str) -> None:
        if self.crashed:
            return
        self.crashed = True
        self.crash_reason = reason

    def spawn_happy_particles(self) -> None:
        for _ in range(10):
            particle = {
                "x": random.randint(100, CONFIG.road_width - 100),
                "y": random.randint(90, CONFIG.screen_height - 90),
                "vx": random.uniform(-35, 35),
                "vy": random.uniform(-45, -10),
                "life": random.uniform(0.6, 1.2),
            }
            self.mood_particles.append(particle)

    def update_particles(self, dt: float) -> None:
        for particle in self.mood_particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.mood_particles = [p for p in self.mood_particles if p["life"] > 0]

    def draw(self) -> None:
        self.screen.fill((214, 239, 245))
        self.draw_road()
        self.draw_ui()

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.player.draw(self.screen)

        self.phone.draw(self.screen, self.phone_rect, self.title_font, self.body_font)
        self.draw_happy_particles()

        if self.crashed:
            self.draw_crash_overlay()

    def draw_road(self) -> None:
        pygame.draw.rect(self.screen, (65, 72, 93), self.road_rect)

        shoulder_left = pygame.Rect(0, 0, 25, CONFIG.screen_height)
        shoulder_right = pygame.Rect(CONFIG.road_width - 25, 0, 25, CONFIG.screen_height)
        pygame.draw.rect(self.screen, (255, 214, 102), shoulder_left)
        pygame.draw.rect(self.screen, (255, 214, 102), shoulder_right)

        self.road_scroll = (self.road_scroll + self.world_speed / 4.8) % 80
        lane_width = (CONFIG.road_width - (CONFIG.lane_padding * 2)) / CONFIG.lane_count
        for i in range(1, CONFIG.lane_count):
            x = int(CONFIG.lane_padding + i * lane_width)
            y = -80 + int(self.road_scroll)
            while y < CONFIG.screen_height:
                pygame.draw.rect(self.screen, (245, 247, 255), (x - 4, y, 8, 48), border_radius=3)
                y += 80

    def draw_ui(self) -> None:
        title = self.title_font.render("Dont Drink & Drive & Text", True, (246, 249, 255))
        self.screen.blit(title, (24, 18))

        speed_label = self.body_font.render(f"Fart: {int(self.world_speed)}", True, (240, 247, 255))
        self.screen.blit(speed_label, (28, 66))

        time_label = self.body_font.render(f"Tid: {self.stats.survived_seconds:05.1f}s", True, (240, 247, 255))
        self.screen.blit(time_label, (28, 98))

        dodged_label = self.body_font.render(f"Unngåtte biler: {self.stats.dodged_cars}", True, (240, 247, 255))
        self.screen.blit(dodged_label, (28, 130))

        drunk_title = self.small_font.render("Beruselse", True, (233, 240, 255))
        self.screen.blit(drunk_title, (28, 164))
        bar_bg = pygame.Rect(28, 188, 250, 20)
        pygame.draw.rect(self.screen, (32, 44, 74), bar_bg, border_radius=9)
        fill_width = int((self.drunk_meter / 100.0) * (bar_bg.width - 4))
        fill_rect = pygame.Rect(bar_bg.x + 2, bar_bg.y + 2, fill_width, bar_bg.height - 4)
        bar_color = (85, 220, 155) if self.drunk_meter < 40 else (255, 199, 87) if self.drunk_meter < 75 else (255, 102, 102)
        pygame.draw.rect(self.screen, bar_color, fill_rect, border_radius=7)

        controls = self.small_font.render("Styr: A/D eller piler | Drikk: Mellomrom", True, (226, 236, 255))
        self.screen.blit(controls, (28, CONFIG.screen_height - 38))

        if self.drink_prompt_active:
            prompt_bg = pygame.Rect(CONFIG.road_width - 320, 20, 280, 44)
            pygame.draw.rect(self.screen, (255, 239, 204), prompt_bg, border_radius=8)
            prompt = self.small_font.render("Feststemning! Trykk SPACE for å drikke", True, (148, 94, 23))
            self.screen.blit(prompt, (prompt_bg.x + 10, prompt_bg.y + 12))

    def draw_happy_particles(self) -> None:
        for particle in self.mood_particles:
            alpha = max(0, min(255, int(255 * particle["life"])))
            color = (255, 215, 120, alpha)
            sparkle_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surface, color, (4, 4), 4)
            self.screen.blit(sparkle_surface, (particle["x"], particle["y"]))

    def draw_crash_overlay(self) -> None:
        overlay = pygame.Surface((CONFIG.screen_width, CONFIG.screen_height), pygame.SRCALPHA)
        fade = min(220, int(120 + self.final_overlay_time * 120))
        overlay.fill((15, 12, 20, fade))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("Krasj", True, (255, 210, 210))
        self.screen.blit(title, (40, 220))

        reason = self.body_font.render(self.crash_reason, True, (255, 233, 233))
        self.screen.blit(reason, (40, 268))

        consequence_lines = [
            "Konsekvenser kan være skader, straffesak,",
            "økonomisk belastning, traumer og tapt tillit.",
            "Ingen melding eller drink er verdt et liv.",
        ]

        for index, line in enumerate(consequence_lines):
            line_surf = self.body_font.render(line, True, (246, 246, 255))
            self.screen.blit(line_surf, (40, 318 + index * 34))

        stats_line = self.body_font.render(
            f"Du holdt ut {self.stats.survived_seconds:0.1f}s, sendte {self.stats.texts_sent} meldinger og unngikk {self.stats.dodged_cars} biler.",
            True,
            (228, 242, 255),
        )
        self.screen.blit(stats_line, (40, 430))

        reminder = self.body_font.render("Trykk R for nytt forsøk | ESC for å avslutte", True, (171, 217, 255))
        self.screen.blit(reminder, (40, 476))


def run_game() -> None:
    game = DontDrinkDriveTextGame()
    game.run()
