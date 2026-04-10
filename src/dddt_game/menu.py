from __future__ import annotations

from dataclasses import dataclass

import pygame

from .config import Difficulty


@dataclass
class MenuState:
    selected_difficulty: Difficulty = Difficulty.MEDIUM
    selected_car_index: int = 0
    show_settings: bool = False
    sound_enabled: bool = True
    music_enabled: bool = True


class PauseMenu:
    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.get_surface()

        self.title_font = pygame.font.SysFont("Segoe UI", 56, bold=True)
        self.menu_font = pygame.font.SysFont("Segoe UI", 28)
        self.small_font = pygame.font.SysFont("Segoe UI", 20)

        self.menu_items = ["Resume", "Settings", "Main Menu"]
        self.selected_index = 0
        self.menu_rects: list[pygame.Rect] = []
        self.state = MenuState()
        self.clock = pygame.time.Clock()
        self.checkbox_size = 24
        self.sound_toggle_rect: pygame.Rect | None = None
        self.music_toggle_rect: pygame.Rect | None = None
        self.back_button_rect: pygame.Rect | None = None
        self.show_settings = False

    def handle_input(self, event: pygame.event.Event) -> str | None:
        """Process a single event. Returns 'resume', 'menu', 'quit' or None"""
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            return "quit"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_settings:
                if self.sound_toggle_rect and self.sound_toggle_rect.collidepoint(mouse_pos):
                    self.state.sound_enabled = not self.state.sound_enabled
                if self.music_toggle_rect and self.music_toggle_rect.collidepoint(mouse_pos):
                    self.state.music_enabled = not self.state.music_enabled
                if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
                    self.show_settings = False
            else:
                for index, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos):
                        action = self.menu_items[index]
                        if action == "Resume":
                            return "resume"
                        elif action == "Settings":
                            self.show_settings = True
                        elif action == "Main Menu":
                            return "menu"

        if event.type == pygame.MOUSEMOTION:
            if not self.show_settings:
                for index, rect in enumerate(self.menu_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_index = index
                        break

        if event.type == pygame.KEYDOWN:
            if self.show_settings:
                if event.key == pygame.K_ESCAPE:
                    self.show_settings = False
                elif event.key == pygame.K_d:
                    self.state.sound_enabled = not self.state.sound_enabled
                elif event.key == pygame.K_m:
                    self.state.music_enabled = not self.state.music_enabled
            else:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = self.menu_items[self.selected_index]
                    if action == "Resume":
                        return "resume"
                    elif action == "Settings":
                        self.show_settings = True
                    elif action == "Main Menu":
                        return "menu"

        return None

    def draw(self) -> None:
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.show_settings:
            self._draw_settings()
        else:
            self._draw_pause_menu()

    def _draw_pause_menu(self) -> None:
        self.menu_rects.clear()

        title = self.title_font.render("PAUSED", True, (255, 220, 220))
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        menu_start_y = 280
        item_spacing = 80

        for index, item in enumerate(self.menu_items):
            is_selected = index == self.selected_index
            color = (255, 100, 100) if is_selected else (200, 150, 150)

            bg_rect = pygame.Rect(
                self.screen_width // 2 - 150,
                menu_start_y + index * item_spacing - 20,
                300,
                50,
            )

            if is_selected:
                pygame.draw.rect(self.screen, (240, 200, 200), bg_rect, border_radius=8)

            self.menu_rects.append(bg_rect)

            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, menu_start_y + index * item_spacing))
            self.screen.blit(text, text_rect)

    def _draw_settings(self) -> None:
        title = self.title_font.render("Pause Settings", True, (255, 220, 220))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title, title_rect)

        audio_title = self.menu_font.render("Audio Settings:", True, (200, 150, 150))
        self.screen.blit(audio_title, (300, 280))

        checkbox_x = 320
        sound_y = 360

        self.sound_toggle_rect = pygame.Rect(checkbox_x, sound_y, self.checkbox_size, self.checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), self.sound_toggle_rect, border_radius=4)
        pygame.draw.rect(self.screen, (200, 150, 150), self.sound_toggle_rect, 2, border_radius=4)

        if self.state.sound_enabled:
            pygame.draw.line(self.screen, (100, 200, 100), (checkbox_x + 6, sound_y + 12), (checkbox_x + 12, sound_y + 18), 3)
            pygame.draw.line(self.screen, (100, 200, 100), (checkbox_x + 12, sound_y + 18), (checkbox_x + 20, sound_y + 6), 3)

        sound_text = self.small_font.render("Sound Effects (D)", True, (200, 150, 150))
        self.screen.blit(sound_text, (checkbox_x + 40, sound_y + 2))

        music_y = 420
        self.music_toggle_rect = pygame.Rect(checkbox_x, music_y, self.checkbox_size, self.checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), self.music_toggle_rect, border_radius=4)
        pygame.draw.rect(self.screen, (200, 150, 150), self.music_toggle_rect, 2, border_radius=4)

        if self.state.music_enabled:
            pygame.draw.line(self.screen, (100, 200, 100), (checkbox_x + 6, music_y + 12), (checkbox_x + 12, music_y + 18), 3)
            pygame.draw.line(self.screen, (100, 200, 100), (checkbox_x + 12, music_y + 18), (checkbox_x + 20, music_y + 6), 3)

        music_text = self.small_font.render("Music (M)", True, (200, 150, 150))
        self.screen.blit(music_text, (checkbox_x + 40, music_y + 2))

        back_text = self.menu_font.render("← Back", True, (150, 150, 200))
        self.back_button_rect = back_text.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        pygame.draw.rect(self.screen, (100, 100, 150), self.back_button_rect.inflate(20, 10), border_radius=8)
        self.screen.blit(back_text, self.back_button_rect)

    def show(self) -> str:
        """Returns 'resume', 'menu', or 'quit'"""
        running = True
        while running:
            result = self.handle_input()

            if result in ("resume", "menu", "quit"):
                return result

            self.draw()
            self.clock.tick(60)

        return "resume"


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
        self.menu_items = ["Start Game", "Settings", "Exit"]
        self.selected_menu_index = 0
        self.difficulty_items = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        self.selected_difficulty_index = 1  # Medium by default
        self.clock = pygame.time.Clock()
        
        # Store clickable rects for mouse interaction
        self.menu_rects: list[pygame.Rect] = []
        self.difficulty_rects: list[pygame.Rect] = []
        self.difficulty_left_rect: pygame.Rect | None = None
        self.difficulty_right_rect: pygame.Rect | None = None
        self.car_left_rect: pygame.Rect | None = None
        self.car_right_rect: pygame.Rect | None = None
        self.car_choice_rect: pygame.Rect | None = None
        self.sound_toggle_rect: pygame.Rect | None = None
        self.music_toggle_rect: pygame.Rect | None = None
        self.back_button_rect: pygame.Rect | None = None

    def _set_selected_difficulty_index(self, index: int) -> None:
        self.selected_difficulty_index = index % len(self.difficulty_items)
        self.state.selected_difficulty = self.difficulty_items[self.selected_difficulty_index]

    def handle_input(self) -> str | None:
        """Returns 'quit' to exit, 'start' to start game, or None to stay in menu"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state.show_settings:
                    if self.car_left_rect and self.car_left_rect.collidepoint(mouse_pos):
                        self.state.selected_car_index = (self.state.selected_car_index - 1) % self.car_count

                    if self.car_right_rect and self.car_right_rect.collidepoint(mouse_pos):
                        self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count

                    if self.car_choice_rect and self.car_choice_rect.collidepoint(mouse_pos):
                        self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count
                    
                    # Check audio toggles
                    if self.sound_toggle_rect and self.sound_toggle_rect.collidepoint(mouse_pos):
                        self.state.sound_enabled = not self.state.sound_enabled
                    
                    if self.music_toggle_rect and self.music_toggle_rect.collidepoint(mouse_pos):
                        self.state.music_enabled = not self.state.music_enabled
                    
                    # Check back button
                    if self.back_button_rect and self.back_button_rect.collidepoint(mouse_pos):
                        self.state.show_settings = False
                else:
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

                    # Check difficulty arrows in main menu
                    if self.difficulty_left_rect and self.difficulty_left_rect.collidepoint(mouse_pos):
                        self._set_selected_difficulty_index(self.selected_difficulty_index - 1)

                    if self.difficulty_right_rect and self.difficulty_right_rect.collidepoint(mouse_pos):
                        self._set_selected_difficulty_index(self.selected_difficulty_index + 1)
            
            # Mouse hover for settings menu
            if event.type == pygame.MOUSEMOTION:
                if self.state.show_settings:
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
                    if event.key == pygame.K_ESCAPE:
                        self.state.show_settings = False
                    elif event.key == pygame.K_LEFT:
                        self.state.selected_car_index = (self.state.selected_car_index - 1) % self.car_count
                    elif event.key == pygame.K_RIGHT:
                        self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count
                    elif event.key == pygame.K_d:
                        self.state.sound_enabled = not self.state.sound_enabled
                    elif event.key == pygame.K_m:
                        self.state.music_enabled = not self.state.music_enabled
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
                        self._set_selected_difficulty_index(self.selected_difficulty_index - 1)
                    elif event.key == pygame.K_RIGHT:
                        self._set_selected_difficulty_index(self.selected_difficulty_index + 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        selected = self.menu_items[self.selected_menu_index]
                        if selected == "Start Game":
                            self.state.selected_difficulty = self.difficulty_items[self.selected_difficulty_index]
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
            self.draw_settings()
        else:
            self.draw_main_menu()

        pygame.display.flip()

    def draw_main_menu(self) -> None:
        self.menu_rects.clear()
        
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
            f"Difficulty: {self.difficulty_items[self.selected_difficulty_index].value}",
            True,
            (100, 120, 160),
        )
        difficulty_rect = difficulty_text.get_rect(
            center=(self.screen_width // 2, 220)
        )
        self.screen.blit(difficulty_text, difficulty_rect)

        # Difficulty arrows
        center_x = self.screen_width // 2
        arrow_y = 220
        self.difficulty_left_rect = pygame.Rect(center_x - 160, arrow_y - 22, 52, 44)
        self.difficulty_right_rect = pygame.Rect(center_x + 108, arrow_y - 22, 52, 44)

        arrow_font = pygame.font.SysFont("Segoe UI", 36, bold=True)
        left_arrow_text = arrow_font.render("<", True, (40, 70, 120))
        right_arrow_text = arrow_font.render(">", True, (40, 70, 120))
        self.screen.blit(left_arrow_text, left_arrow_text.get_rect(center=self.difficulty_left_rect.center))
        self.screen.blit(right_arrow_text, right_arrow_text.get_rect(center=self.difficulty_right_rect.center))

        # Menu Items
        menu_start_y = 320
        item_spacing = 70
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
            "Click or use UP/DOWN arrows to navigate, ENTER to select",
            True,
            (80, 110, 150),
        )
        instructions_rect = instructions.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)
        )
        self.screen.blit(instructions, instructions_rect)

    def draw_settings(self) -> None:
        self.car_left_rect = None
        self.car_right_rect = None
        self.car_choice_rect = None

        title = self.subtitle_font.render("Settings", True, (25, 45, 85))
        title_rect = title.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(title, title_rect)

        car_start_y = 220
        car_title = self.menu_font.render("Choose Car:", True, (40, 70, 120))
        self.screen.blit(car_title, (100, car_start_y))

        car_box = pygame.Rect(280, car_start_y - 10, 220, 52)
        pygame.draw.rect(self.screen, (230, 245, 255), car_box, border_radius=8)
        car_label = self.menu_font.render(
            f"Car {self.state.selected_car_index + 1} / {self.car_count}",
            True,
            (255, 100, 100),
        )
        car_label_rect = car_label.get_rect(center=car_box.center)
        self.screen.blit(car_label, car_label_rect)
        self.car_choice_rect = car_box

        left_rect = pygame.Rect(214, car_start_y - 16, 52, 64)
        right_rect = pygame.Rect(510, car_start_y - 16, 52, 64)
        arrow_font = pygame.font.SysFont("Segoe UI", 36, bold=True)
        left_text = arrow_font.render("<", True, (40, 70, 120))
        right_text = arrow_font.render(">", True, (40, 70, 120))
        self.screen.blit(left_text, left_text.get_rect(center=left_rect.center))
        self.screen.blit(right_text, right_text.get_rect(center=right_rect.center))
        self.car_left_rect = left_rect
        self.car_right_rect = right_rect

        audio_start_y = 360
        settings_title = self.menu_font.render("Audio Settings:", True, (40, 70, 120))
        self.screen.blit(settings_title, (100, audio_start_y))

        checkbox_size = 24
        checkbox_x = 120
        sound_checkbox_y = audio_start_y + 50

        checkbox_rect = pygame.Rect(checkbox_x, sound_checkbox_y, checkbox_size, checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), checkbox_rect, border_radius=4)
        pygame.draw.rect(self.screen, (40, 70, 120), checkbox_rect, 2, border_radius=4)

        if self.state.sound_enabled:
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 6, sound_checkbox_y + 12), (checkbox_x + 12, sound_checkbox_y + 18), 3)
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 12, sound_checkbox_y + 18), (checkbox_x + 20, sound_checkbox_y + 6), 3)

        self.sound_toggle_rect = checkbox_rect

        sound_text = self.small_font.render("Sound Effects (D to toggle)", True, (40, 70, 120))
        self.screen.blit(sound_text, (checkbox_x + 40, sound_checkbox_y + 2))

        music_checkbox_y = audio_start_y + 90
        music_checkbox_rect = pygame.Rect(checkbox_x, music_checkbox_y, checkbox_size, checkbox_size)
        pygame.draw.rect(self.screen, (255, 255, 255), music_checkbox_rect, border_radius=4)
        pygame.draw.rect(self.screen, (40, 70, 120), music_checkbox_rect, 2, border_radius=4)

        if self.state.music_enabled:
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 6, music_checkbox_y + 12), (checkbox_x + 12, music_checkbox_y + 18), 3)
            pygame.draw.line(self.screen, (100, 150, 100), (checkbox_x + 12, music_checkbox_y + 18), (checkbox_x + 20, music_checkbox_y + 6), 3)

        self.music_toggle_rect = music_checkbox_rect

        music_text = self.small_font.render("Music (M to toggle)", True, (40, 70, 120))
        self.screen.blit(music_text, (checkbox_x + 40, music_checkbox_y + 2))

        back_button_text = self.menu_font.render("← Back to Menu", True, (100, 120, 160))
        self.back_button_rect = back_button_text.get_rect(center=(self.screen_width // 2, self.screen_height - 60))
        pygame.draw.rect(self.screen, (220, 230, 245), self.back_button_rect.inflate(20, 10), border_radius=8)
        self.screen.blit(back_button_text, self.back_button_rect)

        instructions = self.small_font.render(
            "Use LEFT/RIGHT to choose car and press ESC to return",
            True,
            (80, 110, 150),
        )
        instructions_rect = instructions.get_rect(
            center=(self.screen_width // 2, self.screen_height - 30)
        )
        self.screen.blit(instructions, instructions_rect)

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
