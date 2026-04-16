from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pygame


@dataclass(frozen=True)
class SpriteSet:
    car_variants: list[pygame.Surface]
    road: pygame.Surface | None


def _resolve_sprites_dir() -> Path:
    """Find sprite directory across desktop and pygbag launch contexts."""
    candidates = [
        Path(__file__).resolve().parents[2] / "assets" / "sprites",
        Path.cwd() / "assets" / "sprites",
        Path("assets") / "sprites",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    # Fall back to source-root-relative path so loading gracefully returns None.
    return candidates[0]


def load_game_sprites(road_size: tuple[int, int], car_size: tuple[int, int]) -> SpriteSet:
    """Load and scale game sprites from assets/sprites."""
    sprites_dir = _resolve_sprites_dir()

    return SpriteSet(
        car_variants=_load_car_variants(sprites_dir, car_size),
        road=_load_and_scale(sprites_dir / "road.png", road_size),
    )


def discover_car_variant_count() -> int:
    sprites_dir = _resolve_sprites_dir()
    shared_variants = sorted(sprites_dir.glob("car*.png"))
    if shared_variants:
        return len(shared_variants)

    legacy_variants = [
        sprites_dir / "player_car.png",
        *sorted(sprites_dir.glob("obstacle_car*.png")),
    ]
    return sum(1 for path in legacy_variants if path.exists())


def _load_car_variants(
    sprites_dir: Path,
    size: tuple[int, int],
) -> list[pygame.Surface]:
    car_surfaces: list[pygame.Surface] = []
    car_paths = sorted(sprites_dir.glob("car*.png"))

    if not car_paths:
        car_paths = [
            sprites_dir / "player_car.png",
            *sorted(sprites_dir.glob("obstacle_car*.png")),
        ]

    for path in car_paths:
        surface = _load_and_scale(path, size)
        if surface is not None:
            car_surfaces.append(surface)

    return car_surfaces


def _load_and_scale(path: Path, size: tuple[int, int]) -> pygame.Surface | None:
    if not path.exists():
        return None

    try:
        surface = pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None

    return pygame.transform.smoothscale(surface, size)