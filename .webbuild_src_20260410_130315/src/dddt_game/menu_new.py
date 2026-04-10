from __future__ import annotations

from dataclasses import dataclass

import pygame

from .config import Difficulty


@dataclass
class MenuState:
    selected_difficulty: Difficulty = Difficulty.MEDIUM
    selected_car_index: int = 0
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
    
    def handle_input(self) -> str | None:
        """Returns 'resume', 'menu', or None"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
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
    
    def draw(self) -> None:
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        if self.show_settings:
            self._draw_settings()
        else:
            self._draw_pause_menu()
        
        pygame.display.flip()
    
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
        self.menu_items = ["Start Game", "Exit"]
        self.selected_menu_index = 0
        self.difficulty_items = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
        self.selected_difficulty_index = 1  # Medium by default
        self.in_setup_phase = False  # True when setting difficulty and car
        self.clock = pygame.time.Clock()
        
        # Store clickable rects for mouse interaction
        self.menu_rects: list[pygame.Rect] = []
        self.difficulty_rects: list[pygame.Rect] = []
        self.car_left_rect: pygame.Rect | None = None
        self.car_right_rect: pygame.Rect | None = None
        self.car_preview_rect: pygame.Rect | None = None
        self.start_game_rect: pygame.Rect | None = None

    def handle_input(self) -> str | None:
        """Returns 'quit' to exit, 'start' to start game, or None to stay in menu"""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.in_setup_phase:
                    # Difficulty selection
                    for index, rect in enumerate(self.difficulty_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_difficulty_index = index
                    
                    # Car selection arrows
                    if self.car_left_rect and self.car_left_rect.collidepoint(mouse_pos):
                        self.state.selected_car_index = (self.state.selected_car_index - 1) % self.car_count
                    
                    if self.car_right_rect and self.car_right_rect.collidepoint(mouse_pos):
                        self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count
                    
                    # Start game button
                    if self.start_game_rect and self.start_game_rect.collidepoint(mouse_pos):
                        self.state.selected_difficulty = self.difficulty_items[self.selected_difficulty_index]
                        return "start"
                else:
                    # Main menu clicks
                    for index, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            if self.menu_items[index] == "Start Game":
                                self.in_setup_phase = True
                            elif self.menu_items[index] == "Exit":
                                return "quit"
            
            # Mouse hover
            if event.type == pygame.MOUSEMOTION:
                if self.in_setup_phase:
                    for index, rect in enumerate(self.difficulty_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_difficulty_index = index
                            break
                else:
                    for index, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(mouse_pos):
                            self.selected_menu_index = index
                            break

            if event.type == pygame.KEYDOWN:
                if self.in_setup_phase:
                    if event.key == pygame.K_ESCAPE:
                        self.in_setup_phase = False
                    elif event.key == pygame.K_UP:
                        self.selected_difficulty_index = (self.selected_difficulty_index - 1) % len(self.difficulty_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_difficulty_index = (self.selected_difficulty_index + 1) % len(self.difficulty_items)
                    elif event.key == pygame.K_LEFT:
                        self.state.selected_car_index = (self.state.selected_car_index - 1) % self.car_count
                    elif event.key == pygame.K_RIGHT:
                        self.state.selected_car_index = (self.state.selected_car_index + 1) % self.car_count
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state.selected_difficulty = self.difficulty_items[self.selected_difficulty_index]
                        return "start"
                else:
                    if event.key == pygame.K_UP:
                        self.selected_menu_index = (self.selected_menu_index - 1) % len(self.menu_items)
                    elif event.key == pygame.K_DOWN:
                        self.selected_menu_index = (self.selected_menu_index + 1) % len(self.menu_items)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu_items[self.selected_menu_index] == "Start Game":
                            self.in_setup_phase = True
                        elif self.menu_items[self.selected_menu_index] == "Exit":
                            return "quit"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"

        return None

    def draw(self) -> None:
        self.screen.fill((214, 239, 245))

        if self.in_setup_phase:
            self.draw_setup()
        else:
            self.draw_main_menu()

        pygame.display.flip()

    def draw_main_menu(self) -> None:
        self.menu_rects.clear()
        
        # Title
        title = self.title_font.render("Don't Drink & Drive & Text", True, (25, 45, 85))
        title_rect = title.get_rect(center=(self.screen_width // 2, 120))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.subtitle_font.render("Stay Safe on the Road", True, (60, 90, 130))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # Menu Items
        menu_start_y = 350
        item_spacing = 100
        for index, item in enumerate(self.menu_items):
            is_selected = index == self.selected_menu_index
            color = (255, 100, 100) if is_selected else (40, 70, 120)
            
            bg_rect = pygame.Rect(
                self.screen_width // 2 - 150,
                menu_start_y + index * item_spacing - 20,
                300,
                50,
            )
            
            if is_selected:
                pygame.draw.rect(self.screen, (230, 245, 255), bg_rect, border_radius=8)
            
            self.menu_rects.append(bg_rect)

            text = self.menu_font.render(item, True, color)
            text_rect = text.get_rect(center=(self.screen_width // 2, menu_start_y + index * item_spacing))
            self.screen.blit(text, text_rect)

        # Instructions
        instructions = self.small_font.render(
            "Use UP/DOWN to navigate, ENTER to select",
            True,
            (80, 110, 150),
        )
        instructions_rect = instructions.get_rect(
            center=(self.screen_width // 2, self.screen_height - 50)
        )
        self.screen.blit(instructions, instructions_rect)

    def draw_setup(self) -> None:
        self.difficulty_rects.clear()
        self.car_left_rect = None
        self.car_right_rect = None
        self.car_preview_rect = None
        
        # Title
        title = self.title_font.render("Game Setup", True, (25, 45, 85))
        title_rect = title.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title, title_rect)

        # Difficulty Selection
        difficulty_title = self.menu_font.render("Select Difficulty:", True, (40, 70, 120))
        self.screen.blit(difficulty_title, (80, 130))

        difficulty_start_y = 190
        difficulty_spacing = 50
        difficulty_info = {
            Difficulty.EASY: "Slower traffic, longer reaction time",
            Difficulty.MEDIUM: "Standard difficulty, balanced challenge",
            Difficulty.HARD: "Aggressive traffic, minimal reaction time",
        }

        for index, difficulty in enumerate(self.difficulty_items):
            is_selected = index == self.selected_difficulty_index
            if is_selected:
                color = (255, 100, 100)
                bg_rect = pygame.Rect(80, difficulty_start_y + index * difficulty_spacing - 12, 560, 44)
                pygame.draw.rect(self.screen, (230, 245, 255), bg_rect, border_radius=8)
            else:
                color = (40, 70, 120)
                bg_rect = pygame.Rect(80, difficulty_start_y + index * difficulty_spacing - 12, 560, 44)
            
            self.difficulty_rects.append(bg_rect)

            text = self.menu_font.render(f"• {difficulty.value}", True, color)
            self.screen.blit(text, (100, difficulty_start_y + index * difficulty_spacing))

            info_text = self.small_font.render(difficulty_info[difficulty], True, (80, 110, 150))
            self.screen.blit(info_text, (280, difficulty_start_y + index * difficulty_spacing))

        # Car Selection
        car_title = self.menu_font.render("Choose Car:", True, (40, 70, 120))
        self.screen.blit(car_title, (80, 420))

        # Car preview area
        car_preview_center_x = self.screen_width // 2
        car_preview_y = 470
        
        left_arrow_rect = pygame.Rect(car_preview_center_x - 120, car_preview_y, 50, 50)
        right_arrow_rect = pygame.Rect(car_preview_center_x + 70, car_preview_y, 50, 50)
        
        # Draw arrows
        for rect in [left_arrow_rect, right_arrow_rect]:
            pygame.draw.rect(self.screen, (220, 230, 245), rect, border_radius=8)
            pygame.draw.rect(self.screen, (132, 153, 208), rect, 2, border_radius=8)
        
        left_arrow_text = self.menu_font.render("<", True, (40, 70, 120))
        right_arrow_text = self.menu_font.render(">", True, (40, 70, 120))
        self.screen.blit(left_arrow_text, left_arrow_text.get_rect(center=left_arrow_rect.center))
        self.screen.blit(right_arrow_text, right_arrow_text.get_rect(center=right_arrow_rect.center))
        
        self.car_left_rect = left_arrow_rect
        self.car_right_rect = right_arrow_rect
        
        # Car number display
        car_label = self.menu_font.render(f"Car {self.state.selected_car_index + 1} / {self.car_count}", True, (255, 100, 100))
        car_label_rect = car_label.get_rect(center=(car_preview_center_x + 25, car_preview_y + 25))
        self.screen.blit(car_label, car_label_rect)

        # Start game button
        start_button_rect = pygame.Rect(self.screen_width // 2 - 100, 600, 200, 50)
        self.start_game_rect = start_button_rect
        
        pygame.draw.rect(self.screen, (100, 180, 100), start_button_rect, border_radius=8)
        pygame.draw.rect(self.screen, (50, 140, 50), start_button_rect, 2, border_radius=8)
        
        start_text = self.menu_font.render("Start Game", True, (255, 255, 255))
        self.screen.blit(start_text, start_text.get_rect(center=start_button_rect.center))
        
        # Instructions
        instructions = self.small_font.render(
            "UP/DOWN: Difficulty | LEFT/RIGHT: Car | SPACE: Start | ESC: Back",
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
