from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame


@dataclass
class PlayerCar:
    lane_index: int
    lane_centers: list[int]
    y: int
    width: int = 70
    height: int = 120
    actual_x: float = 0.0
    target_lane_index: int | None = None
    move_speed: float = 600.0
    sprite: pygame.Surface | None = None
    sway_phase: float = 0.0
    sway_offset_x: float = 0.0

    def __post_init__(self) -> None:
        if self.actual_x == 0.0:
            self.actual_x = float(self.lane_centers[self.lane_index] - self.width // 2)
        if self.target_lane_index is None:
            self.target_lane_index = self.lane_index
        self.sway_phase = random.uniform(0.0, 6.283185307)

    def set_target_lane_left(self) -> None:
        current_target = self.target_lane_index if self.target_lane_index is not None else self.lane_index
        self.target_lane_index = max(0, current_target - 1)

    def set_target_lane_right(self) -> None:
        current_target = self.target_lane_index if self.target_lane_index is not None else self.lane_index
        self.target_lane_index = min(len(self.lane_centers) - 1, current_target + 1)

    def update(self, dt: float, drunk_meter: float = 0.0) -> None:
        if self.target_lane_index is None:
            self.target_lane_index = self.lane_index
        
        target_x = float(self.lane_centers[self.target_lane_index] - self.width // 2)
        diff = target_x - self.actual_x
        max_move = self.move_speed * dt
        
        if abs(diff) > max_move:
            self.actual_x += max_move if diff > 0 else -max_move
        else:
            self.actual_x = target_x
            self.lane_index = self.target_lane_index

        # Add visible horizontal wobble when intoxicated; intensity and speed scale with drunk meter.
        sway_intensity = max(0.0, min(1.0, (drunk_meter - 25.0) / 75.0))
        self.sway_phase += dt * (5.0 + 3.5 * sway_intensity)
        max_sway_pixels = 26.0
        self.sway_offset_x = max_sway_pixels * sway_intensity * math.sin(self.sway_phase)

    @property
    def x(self) -> int:
        return int(self.actual_x + self.sway_offset_x)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def collision_rect(self) -> pygame.Rect:
        return self.rect.inflate(-8, -10)

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect
        if self.sprite is not None:
            surface.blit(self.sprite, rect)
            return

        pygame.draw.rect(surface, (38, 198, 218), rect, border_radius=11)
        window = pygame.Rect(rect.x + 8, rect.y + 12, rect.width - 16, 28)
        pygame.draw.rect(surface, (220, 250, 255), window, border_radius=6)
        light_left = pygame.Rect(rect.x + 8, rect.bottom - 12, 10, 6)
        light_right = pygame.Rect(rect.right - 18, rect.bottom - 12, 10, 6)
        pygame.draw.rect(surface, (255, 68, 68), light_left, border_radius=2)
        pygame.draw.rect(surface, (255, 68, 68), light_right, border_radius=2)


@dataclass
class ObstacleCar:
    lane_index: int
    lane_centers: list[int]
    y: float
    speed: float
    width: int = 70
    height: int = 120
    sprite: pygame.Surface | None = None

    @property
    def x(self) -> int:
        return self.lane_centers[self.lane_index] - self.width // 2

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def collision_rect(self) -> pygame.Rect:
        return self.rect.inflate(8, 12)

    def update(self, dt: float) -> None:
        self.y += self.speed * dt

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.rect
        if self.sprite is not None:
            surface.blit(self.sprite, rect)
            return

        pygame.draw.rect(surface, (255, 184, 77), rect, border_radius=11)
        pygame.draw.rect(surface, (255, 245, 215), (rect.x + 8, rect.y + 12, rect.width - 16, 24), border_radius=6)
        pygame.draw.rect(surface, (255, 153, 153), (rect.x + 8, rect.bottom - 12, 10, 6), border_radius=2)
        pygame.draw.rect(surface, (255, 153, 153), (rect.right - 18, rect.bottom - 12, 10, 6), border_radius=2)


def spawn_obstacle(
    lane_centers: list[int],
    world_speed: float,
    sprite: pygame.Surface | None = None,
    width: int = 70,
    height: int = 120,
) -> ObstacleCar:
    lane_index = random.randrange(0, len(lane_centers))
    spawn_y = random.randrange(-280, -120)
    speed = world_speed + random.uniform(25, 110)
    return ObstacleCar(
        lane_index=lane_index,
        lane_centers=lane_centers,
        y=float(spawn_y),
        speed=speed,
        sprite=sprite,
        width=width,
        height=height,
    )
