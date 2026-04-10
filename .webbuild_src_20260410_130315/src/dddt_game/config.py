from dataclasses import dataclass
from enum import Enum


class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


@dataclass(frozen=True)
class GameConfig:
    screen_width: int = 1200
    screen_height: int = 720
    road_width: int = 820
    phone_panel_width: int = 380
    lane_count: int = 3
    lane_padding: int = 70
    fps: int = 60
    initial_world_speed: float = 220.0
    max_world_speed: float = 390.0
    obstacle_spawn_interval: float = 1.45
    objective_texts_required: int = 5
    inevitable_crash_time: float = 120.0


@dataclass(frozen=True)
class DifficultyConfig:
    """Modifiers for different difficulty levels"""
    speed_multiplier: float = 1.0
    spawn_interval_multiplier: float = 1.0
    drunk_acceleration_multiplier: float = 1.0
    inevitable_crash_time_modifier: float = 1.0


DIFFICULTY_CONFIGS = {
    Difficulty.EASY: DifficultyConfig(
        speed_multiplier=0.75,
        spawn_interval_multiplier=1.3,
        drunk_acceleration_multiplier=0.7,
        inevitable_crash_time_modifier=1.2,
    ),
    Difficulty.MEDIUM: DifficultyConfig(
        speed_multiplier=1.0,
        spawn_interval_multiplier=1.0,
        drunk_acceleration_multiplier=1.0,
        inevitable_crash_time_modifier=1.0,
    ),
    Difficulty.HARD: DifficultyConfig(
        speed_multiplier=1.25,
        spawn_interval_multiplier=0.75,
        drunk_acceleration_multiplier=1.3,
        inevitable_crash_time_modifier=0.8,
    ),
}


CONFIG = GameConfig()
