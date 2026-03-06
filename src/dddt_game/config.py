from dataclasses import dataclass


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


CONFIG = GameConfig()
