from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import webbrowser

import pygame

from .config import Difficulty


@dataclass
class MenuState:
    selected_difficulty: Difficulty = Difficulty.MEDIUM
    selected_car_index: int = 0
    show_settings: bool = False
    show_credits: bool = False
    sound_enabled: bool = True
    music_enabled: bool = True


class MainMenu:
    def __init__(self, screen_width: int, screen_height: int, car_count: int = 1) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.car_count = max(1, car_count)
        self.screen = pygame.display.get_surface() or pygame.display.set_mode(
            (screen_width, screen_height)
        )
        
        self.title_font = pygame.font.SysFont("Segoe UI", 56, bold=True)
        self.subtitle_font = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.menu_font = pygame.font.SysFont("Segoe UI", 28)
        self.small_font = pygame.font.SysFont("Segoe UI", 20)

        self.state = MenuState()
        self.credits_url = "https://www.freepik.com/vectors/pixel-art-car-top-down?log-in=google"
        self.menu_items = ["Start Game", "Settings", "Exit"]
        self.selected_menu_index = 0
        self.difficulty_items = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        self.selected_difficulty_index = 1  # Medium by default
        self.clock = pygame.time.Clock()
        self.car_preview_size = (112, 192)
        self.car_previews = self._load_car_previews()
        
        # Store clickable rects for mouse interaction
        self.menu_rects: list[pygame.Rect] = []
        self.difficulty_rects: list[pygame.Rect] = []
        self.main_car_left_rect: pygame.Rect | None = None
        self.main_car_right_rect: pygame.Rect | None = None
        self.main_car_preview_rect: pygame.Rect | None = None
        self.car_left_rect: pygame.Rect | None = None
        self.car_right_rect: pygame.Rect | None = None
        self.car_choice_rect: pygame.Rect | None = None
        self.credits_button_rect: pygame.Rect | None = None
        self.credits_link_rect: pygame.Rect | None = None
        self.credits_back_rect: pygame.Rect | None = None
        self.sound_toggle_rect: pygame.Rect | None = None
        self.music_toggle_rect: pygame.Rect | None = None
        self.back_button_rect: pygame.Rect | None = None

    def handle_input(self) -> str | None:
        """Returns 'quit' to exit, 'start' to start game, or None to stay in menu"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state.show_settings:
                    if self.state.show_credits:
                        if self.credits_link_rect and self.credits_link_rect.collidepoint(mouse_pos):
                            self._open_credits_url()
                        if self.credits_back_rect and self.credits_back_rect.collidepoint(mouse_pos):
                            self.state.show_credits = False
                    else:
                        # Check difficulty clicks
                        for index, rect in enumerate(self.difficulty_rects):
                            if rect.collidepoint(mouse_pos):
                                self.selected_difficulty_index = index

                        # Check audio toggles
                        if self.sound_toggle_rect and self.sound_toggle_rect.collidepoint(mouse_pos):
                            self.state.sound_enabled = not self.state.sound_enabled

                        if self.music_toggle_rect and self.music_toggle_rect.collidepoint(mouse_pos):
                            self.state.music_enabled = not self.state.music_enabled

                        if self.credits_button_rect and self.credits_button_rect.collidepoint(mouse_pos):
                            self.state.show_credits = True

                        # Check back button
                        if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
                            self.state.show_settings = False
                else:
                    if self.main_car_left_rect and self.main_car_left_rect.collidepoint(mouse_pos):
                        self._change_selected_car(-1)
                        continue

                    if self.main_car_right_rect and self.main_car_right_rect.collidepoint(mouse_pos):
                        self._change_selected_car(1)
                        continue

                    if self.main_car_preview_rect and self.main_car_preview_rect.collidepoint(mouse_pos):
                        self._change_selected_car(1)
                        continue

                    # Check menu item clicks
                    for index, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            selected = self.menu_items[index]
                            if selected == "Start Game":
                                self.state.selected_difficulty = (
                                    self.difficulty_items[self.selected_difficulty_index]
                                )
                                return "start"
                            elif selected == "Settings":
                                self.state.show_settings = True
                            elif selected == "Exit":
                                return "quit"
            
            # Mouse hover for settings menu
            if event.type == pygame.MOUSEMOTION:
                if self.state.show_settings:
                    if not self.state.show_credits:
                        # Update selected index on hover
                        for index, rect in enumerate(self.difficulty_rects):
                            if rect.collidepoint(mouse_pos):
                                self.selected_difficulty_index = index
                                break
                else:
                    # Update selected menu index on hover
                    for index, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_menu_index = index
                            break

            if event.type == pygame.KEYDOWN:
                if self.state.show_settings:
                    if self.state.show_credits:
                        if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                            self.state.show_credits = False
                        elif event.key == pygame.K_c:
                            self._open_credits_url()
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.state.show_settings = False
                        elif event.key == pygame.K_UP:
                            self.selected_difficulty_index = (
                                self.selected_difficulty_index - 1
                            ) % len(self.difficulty_items)
                        elif event.key == pygame.K_DOWN:
                            self.selected_difficulty_index = (
                                self.selected_difficulty_index + 1
                            ) % len(self.difficulty_items)
                        elif event.key == pygame.K_LEFT:
                            self.state.selected_car_index = (self.state.selected_car_index - 1) % self.car_count
                        elif event.key == pygame.K_RIGHT:
                            self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count
                        elif event.key == pygame.K_d:
                            self.state.sound_enabled = not self.state.sound_enabled
                        elif event.key == pygame.K_m:
                            self.state.music_enabled = not self.state.music_enabled
                        elif event.key == pygame.K_c:
                            self.state.show_credits = True
                else:
                    if event.key == pygame.K_UP:
                        self.selected_menu_index = (self.selected_menu_index - 1) % len(
                            self.menu_items
                        )
                    elif event.key == pygame.K_DOWN:
                        self.selected_menu_index = (self.selected_menu_index + 1) % len(
                            self.menu_items
                        )
                    elif event.key == pygame.K_LEFT:
                        self._change_selected_car(-1)
                    elif event.key == pygame.K_RIGHT:
                        self._change_selected_car(1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        selected = self.menu_items[self.selected_menu_index]
                        if selected == "Start Game":
                            self.state.selected_difficulty = (
                                self.difficulty_items[self.selected_difficulty_index]
                            )
                            return "start"
                        elif selected == "Settings":
                            self.state.show_settings = True
                        elif selected == "Exit":
                            return "quit"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"

        return None

    def draw(self) -> None:
        self.screen.fill((214, 239, 245))

        if self.state.show_settings:
            if self.state.show_credits:
                self.draw_credits()
            else:
                self.draw_settings()
        else:
            self.draw_main_menu()

        pygame.display.flip()

    def draw_main_menu(self) -> None:
        self.menu_rects.clear()
        self.main_car_left_rect = None
        self.main_car_right_rect = None
        self.main_car_preview_rect = None
        
        # Title
        title = self.title_font.render("Don't Drink & Drive & Text", True, (25, 45, 85))
        title_rect = title.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render("Stay Safe on the Road", True, (60, 90, 130))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)

        # Current Difficulty Display
        difficulty_text = self.small_font.render(
            f"Difficulty: {self.state.selected_difficulty.value}",
            True,
            (100, 120, 160),
        )
        difficulty_rect = difficulty_text.get_rect(
            center=(self.screen_width // 2, 220)
        )
        self.screen.blit(difficulty_text, difficulty_rect)

        # Car preview and selector arrows
        preview_rect = pygame.Rect(self.screen_width // 2 - 56, 245, 112, 192)
        pygame.draw.rect(self.screen, (230, 245, 255), preview_rect.inflate(14, 14), border_radius=10)
        pygame.draw.rect(self.screen, (132, 153, 208), preview_rect.inflate(14, 14), 2, border_radius=10)
        self.main_car_preview_rect = preview_rect.inflate(14, 14)

        selected_car = self._get_selected_car_preview()
        if selected_car is not None:
            self.screen.blit(selected_car, preview_rect)
        else:
            pygame.draw.rect(self.screen, (80, 180, 210), preview_rect, border_radius=10)
            windshield = pygame.Rect(preview_rect.x + 12, preview_rect.y + 14, preview_rect.width - 24, 34)
            pygame.draw.rect(self.screen, (220, 250, 255), windshield, border_radius=6)
            light_left = pygame.Rect(preview_rect.x + 10, preview_rect.bottom - 14, 14, 8)
            light_right = pygame.Rect(preview_rect.right - 24, preview_rect.bottom - 14, 14, 8)
            pygame.draw.rect(self.screen, (255, 68, 68), light_left, border_radius=2)
            pygame.draw.rect(self.screen, (255, 68, 68), light_right, border_radius=2)

        left_rect = pygame.Rect(preview_rect.x - 58, preview_rect.centery - 26, 46, 52)
        right_rect = pygame.Rect(preview_rect.right + 12, preview_rect.centery - 26, 46, 52)
        pygame.draw.rect(self.screen, (220, 230, 245), left_rect, border_radius=8)
        pygame.draw.rect(self.screen, (220, 230, 245), right_rect, border_radius=8)
        left_text = self.menu_font.render("<", True, (40, 70, 120))
        right_text = self.menu_font.render(">", True, (40, 70, 120))
        self.screen.blit(left_text, left_text.get_rect(center=left_rect.center))
        self.screen.blit(right_text, right_text.get_rect(center=right_rect.center))
        self.main_car_left_rect = left_rect
        self.main_car_right_rect = right_rect

        car_label = self.small_font.render(
            f"Car {self.state.selected_car_index + 1}/{self.car_count}",
            True,
            (100, 120, 160),
        )
        self.screen.blit(car_label, car_label.get_rect(center=(self.screen_width // 2, 455)))

        # Menu Items
        menu_start_y = 520
        item_spacing = 58
        for index, item in enumerate(self.menu_items):
            if index == self.selected_menu_index:
                color = (255, 100, 100)
                bg_rect = pygame.Rect(
                    self.screen_width // 2 - 150,
                    menu_start_y + index * item_spacing - 20,
                    300,
                    50,
                )
                pygame.draw.rect(self.screen, (230, 245, 255), bg_rect, border_radius=8)
                self.menu_rects.append(bg_rect)
            else:
                color = (40, 70, 120)
                bg_rect = pygame.Rect(
                    self.screen_width // 2 - 150,
                    menu_start_y + index * item_spacing - 20,
                    300,
                    50,
                )
                self.menu_rects.append(bg_rect)

            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, menu_start_y + index * item_spacing))
            self.screen.blit(text, text_rect)

        # Instructions
        instructions = self.small_font.render(
            "UP/DOWN: menu | LEFT/RIGHT: car | ENTER: select",
            True,
            (80, 110, 150),
        )
        instructions_rect = instructions.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)
        )
        self.screen.blit(instructions, instructions_rect)

    def draw_settings(self) -> None:
        self.difficulty_rects.clear()
        self.car_left_rect = None
        self.car_right_rect = None
        self.car_choice_rect = None
        self.credits_button_rect = None
        self.credits_link_rect = None
        self.credits_back_rect = None
        
        # Title
        title = self.subtitle_font.render("Settings", True, (25, 45, 85))
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(title, title_rect)

        # Difficulty Selection
        difficulty_title = self.menu_font.render("Select Difficulty:", True, (40, 70, 120))
        self.screen.blit(difficulty_title, (100, 140))

        difficulty_start_y = 200
        difficulty_spacing = 60
        difficulty_info = {
            Difficulty.EASY: "Slower traffic, longer reaction time",
            Difficulty.MEDIUM: "Standard difficulty, balanced challenge",
            Difficulty.HARD: "Aggressive traffic, minimal reaction time",
        }

        for index, difficulty in enumerate(self.difficulty_items):
            is_selected = index == self.selected_difficulty_index
            if is_selected:
                color = (255, 100, 100)
                bg_rect = pygame.Rect(100, difficulty_start_y + index * difficulty_spacing - 15, 600, 50)
                pygame.draw.rect(self.screen, (230, 245, 255), bg_rect, border_radius=8)
            else:
                color = (40, 70, 120)
                bg_rect = pygame.Rect(100, difficulty_start_y + index * difficulty_spacing - 15, 600, 50)
            
            self.difficulty_rects.append(bg_rect)

            text = self.menu_font.render(f"• {difficulty.value}", True, color)
            self.screen.blit(text, (120, difficulty_start_y + index * difficulty_spacing))

            info_text = self.small_font.render(difficulty_info[difficulty], True, (80, 110, 150))
            self.screen.blit(info_text, (300, difficulty_start_y + index * difficulty_spacing))

        # Audio Settings
        audio_start_y = 420
        settings_title = self.menu_font.render("Audio Settings:", True, (40, 70, 120))
        self.screen.blit(settings_title, (100, audio_start_y))

        # Sound toggle with checkbox
        checkbox_size = 24
        checkbox_x = 120
        sound_checkbox_y = audio_start_y + 50
        
        # Draw sound checkbox
        checkbox_rect = pygame.Rect(checkbox_x, sound_checkbox_y, checkbox_size, checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), checkbox_rect, border_radius=4)
        pygame.draw.rect(self.screen, (40, 70, 120), checkbox_rect, 2, border_radius=4)
        
        if self.state.sound_enabled:
            # Draw checkmark
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 6, sound_checkbox_y + 12), (checkbox_x + 12, sound_checkbox_y + 18), 3)
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 12, sound_checkbox_y + 18), (checkbox_x + 20, sound_checkbox_y + 6), 3)
        
        self.sound_toggle_rect = checkbox_rect
        
        sound_text = self.small_font.render("Sound Effects (D to toggle)", True, (40, 70, 120))
        self.screen.blit(sound_text, (checkbox_x + 40, sound_checkbox_y + 2))

        # Music toggle with checkbox
        music_checkbox_y = audio_start_y + 90
        
        # Draw music checkbox
        music_checkbox_rect = pygame.Rect(checkbox_x, music_checkbox_y, checkbox_size, checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), music_checkbox_rect, border_radius=4)
        pygame.draw.rect(self.screen, (40, 70, 120), music_checkbox_rect, 2, border_radius=4)
        
        if self.state.music_enabled:
            # Draw checkmark
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 6, music_checkbox_y + 12), (checkbox_x + 12, music_checkbox_y + 18), 3)
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 12, music_checkbox_y + 18), (checkbox_x + 20, music_checkbox_y + 6), 3)
        
        self.music_toggle_rect = music_checkbox_rect
        
        music_text = self.small_font.render("Music (M to toggle)", True, (40, 70, 120))
        self.screen.blit(music_text, (checkbox_x + 40, music_checkbox_y + 2))

        # Credits button
        credits_button = pygame.Rect(100, 620, 180, 42)
        pygame.draw.rect(self.screen, (220, 230, 245), credits_button, border_radius=8)
        credits_text = self.small_font.render("Credits (C)", True, (40, 70, 120))
        self.screen.blit(
            credits_text,
            credits_text.get_rect(center=credits_button.center),
        )
        self.credits_button_rect = credits_button

        # Back button
        back_button_text = self.menu_font.render("← Back to Menu", True, (100, 120, 160))
        self.back_button_rect = back_button_text.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        pygame.draw.rect(self.screen, (220, 230, 245), self.back_button_rect.inflate(20, 10), border_radius=8)
        self.screen.blit(back_button_text, self.back_button_rect)

        # Instructions
        instructions = self.small_font.render(
            "Select difficulty and audio options here, then press ESC to return",
            True,
            (80, 110, 150),
        )
        instructions_rect = instructions.get_rect(
            center=(self.screen_width // 2, self.screen_height - 30)
        )
        self.screen.blit(instructions, instructions_rect)

    def draw_credits(self) -> None:
        self.credits_link_rect = None
        self.credits_back_rect = None

        title = self.subtitle_font.render("Credits", True, (25, 45, 85))
        self.screen.blit(title, title.get_rect(center=(self.screen_width // 2, 70)))

        desc1 = self.small_font.render("Car sprites attribution:", True, (40, 70, 120))
        self.screen.blit(desc1, (100, 150))

        link_box = pygame.Rect(100, 190, self.screen_width - 200, 56)
        pygame.draw.rect(self.screen, (230, 245, 255), link_box, border_radius=8)
        pygame.draw.rect(self.screen, (132, 153, 208), link_box, 2, border_radius=8)

        link_text = self.small_font.render(self.credits_url, True, (25, 70, 150))
        self.screen.blit(link_text, (link_box.x + 12, link_box.y + 18))
        self.credits_link_rect = link_box

        helper = self.small_font.render("Click the link box or press C to open in browser", True, (80, 110, 150))
        self.screen.blit(helper, (100, 270))

        back_box = pygame.Rect(100, 330, 180, 42)
        pygame.draw.rect(self.screen, (220, 230, 245), back_box, border_radius=8)
        back_text = self.small_font.render("Back", True, (40, 70, 120))
        self.screen.blit(back_text, back_text.get_rect(center=back_box.center))
        self.credits_back_rect = back_box

        tip = self.small_font.render("ESC or Backspace returns to Settings", True, (80, 110, 150))
        self.screen.blit(tip, (100, 390))

    def _open_credits_url(self) -> None:
        try:
            webbrowser.open(self.credits_url, new=2)
        except Exception:
            # Ignore browser launch failures to keep menu interaction stable.
            pass

    def _change_selected_car(self, delta: int) -> None:
        self.state.selected_car_index = (self.state.selected_car_index + delta) % self.car_count

    def _load_car_previews(self) -> list[pygame.Surface]:
        sprites_dir = Path(__file__).resolve().parents[2] / "assets" / "sprites"
        preview_paths = sorted(sprites_dir.glob("car*.png"))
        previews: list[pygame.Surface] = []

        for path in preview_paths:
            try:
                loaded = pygame.image.load(str(path)).convert_alpha()
                previews.append(pygame.transform.smoothscale(loaded, self.car_preview_size))
            except pygame.error:
                continue

        return previews

    def _get_selected_car_preview(self) -> pygame.Surface | None:
        if not self.car_previews:
            return None
        return self.car_previews[self.state.selected_car_index % len(self.car_previews)]

    def show(self) -> Difficulty | None:
        """Show the menu and return selected difficulty when starting, or None if quitting"""
        running = True
        while running:
            result = self.handle_input()
            
            if result == "start":
                return self.state.selected_difficulty
            elif result == "quit":
                return None

            self.draw()
            self.clock.tick(60)

        return None
