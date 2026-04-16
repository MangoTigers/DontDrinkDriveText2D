from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from .localization import Language, phone_task_templates, t


@dataclass
class PhoneTask:
    sender: str
    message: str
    accepted_replies: list[str]


class PhoneSystem:
    def __init__(self, required_total: int, language: Language = Language.NORWEGIAN) -> None:
        self.required_total = required_total
        self.language = language
        self.task_pool = phone_task_templates(language)
        self.completed = 0
        self.current_task = self._new_task()
        self.current_input = ""
        self.last_result = ""
        self.result_timer = 0.0
        self.cursor_timer = 0.0
        self.key_buttons: list[tuple[pygame.Rect, str, str]] = []
        self.feedback_visible = False
        self.feedback_title = ""
        self.feedback_replies: list[str] = []
        self.feedback_anim = 0.0
        self.feedback_dragging = False
        self.feedback_drag_offset = 0.0
        self.feedback_drag_start_y = 0
        self._last_area: pygame.Rect | None = None

    @property
    def is_goal_reached(self) -> bool:
        return self.completed >= self.required_total

    def _new_task(self) -> PhoneTask:
        template = random.choice(self.task_pool)
        return PhoneTask(
            sender=template.sender,
            message=template.message,
            accepted_replies=list(template.accepted_replies),
        )

    def process_click(self, position: tuple[int, int]) -> bool:
        if self.feedback_visible:
            return False

        for rect, label, action in self.key_buttons:
            if rect.collidepoint(position):
                if action == "backspace":
                    self.current_input = self.current_input[:-1]
                    return False
                if action == "space":
                    if len(self.current_input) < 30:
                        self.current_input += " "
                    return False
                if action == "send":
                    accepted_normalized = {
                        self._normalize_reply(reply) for reply in self.current_task.accepted_replies
                    }
                    typed = self._normalize_reply(self.current_input)
                    success = typed in accepted_normalized and typed != ""
                    if success:
                        self.completed += 1
                        self.last_result = t(self.language, "phone_sent")
                        self.current_task = self._new_task()
                    else:
                        self._show_feedback(self.current_task.accepted_replies)
                        self.last_result = ""
                    self.current_input = ""
                    self.result_timer = 2.7
                    return success
                if action == "char" and len(self.current_input) < 30:
                    self.current_input += label
                return False
        return False

    def begin_swipe(self, position: tuple[int, int]) -> bool:
        if not self.feedback_visible or self._last_area is None:
            return False

        handle_rect = self._feedback_handle_rect()
        if handle_rect and handle_rect.collidepoint(position):
            self.feedback_dragging = True
            self.feedback_drag_start_y = position[1]
            self.feedback_drag_offset = 0.0
            return True
        return False

    def update_swipe(self, position: tuple[int, int]) -> None:
        if not self.feedback_dragging:
            return

        drag_delta = position[1] - self.feedback_drag_start_y
        self.feedback_drag_offset = max(-140.0, min(0.0, float(drag_delta)))

    def end_swipe(self, position: tuple[int, int]) -> None:
        if not self.feedback_dragging:
            return

        self.update_swipe(position)
        should_dismiss = self.feedback_drag_offset <= -60.0
        self.feedback_dragging = False

        if should_dismiss:
            self.dismiss_feedback()
        else:
            self.feedback_drag_offset = 0.0

    def dismiss_feedback(self) -> None:
        self.feedback_visible = False
        self.feedback_title = ""
        self.feedback_replies = []
        self.feedback_anim = 0.0
        self.feedback_dragging = False
        self.feedback_drag_offset = 0.0
        self.feedback_drag_start_y = 0

    def _show_feedback(self, accepted_replies: list[str]) -> None:
        self.feedback_visible = True
        self.feedback_title = t(self.language, "phone_feedback_title")
        self.feedback_replies = accepted_replies[:2]
        self.feedback_anim = 0.0
        self.feedback_dragging = False
        self.feedback_drag_offset = 0.0
        self.feedback_drag_start_y = 0

    def update(self, dt: float) -> None:
        if self.result_timer > 0:
            self.result_timer = max(0.0, self.result_timer - dt)
            if self.result_timer == 0:
                self.last_result = ""
        self.cursor_timer += dt
        if self.cursor_timer > 1.0:
            self.cursor_timer -= 1.0
        if self.feedback_visible:
            self.feedback_anim = min(1.0, self.feedback_anim + dt * 5.0)
        else:
            self.feedback_anim = 0.0

        if not self.feedback_dragging and self.feedback_drag_offset < 0.0:
            self.feedback_drag_offset = min(0.0, self.feedback_drag_offset + dt * 520.0)

    def draw(self, surface: pygame.Surface, area: pygame.Rect, title_font: pygame.font.Font, body_font: pygame.font.Font) -> None:
        self._last_area = area
        pygame.draw.rect(surface, (248, 250, 255), area, border_radius=14)
        pygame.draw.rect(surface, (35, 53, 98), area, 3, border_radius=14)

        notch = pygame.Rect(area.x + area.width // 2 - 56, area.y + 6, 112, 18)
        pygame.draw.rect(surface, (24, 34, 66), notch, border_radius=8)

        header = title_font.render(t(self.language, "phone_title"), True, (35, 53, 98))
        surface.blit(header, (area.x + 18, area.y + 30))

        sender_label = body_font.render(
            f"{t(self.language, 'phone_from_prefix')} {self.current_task.sender}",
            True,
            (44, 66, 122),
        )
        surface.blit(sender_label, (area.x + 18, area.y + 80))

        msg_bg = pygame.Rect(area.x + 16, area.y + 110, area.width - 32, 130)
        pygame.draw.rect(surface, (230, 238, 255), msg_bg, border_radius=10)
        wrapped_message = self._wrap_text(self.current_task.message, body_font, msg_bg.width - 18)
        for index, line in enumerate(wrapped_message):
            line_surf = body_font.render(line, True, (30, 46, 89))
            surface.blit(line_surf, (msg_bg.x + 10, msg_bg.y + 12 + index * 24))

        entry_label = body_font.render(t(self.language, "phone_reply_prompt"), True, (35, 53, 98))
        surface.blit(entry_label, (area.x + 18, area.y + 260))

        entry_box = pygame.Rect(area.x + 16, area.y + 290, area.width - 32, 54)
        pygame.draw.rect(surface, (255, 255, 255), entry_box, border_radius=8)
        pygame.draw.rect(surface, (132, 153, 208), entry_box, 2, border_radius=8)

        typed = body_font.render(self.current_input, True, (22, 34, 69))
        surface.blit(typed, (entry_box.x + 10, entry_box.y + 15))

        if self.cursor_timer < 0.5:
            cursor_x = entry_box.x + 10 + typed.get_width() + 2
            cursor_y = entry_box.y + 15
            pygame.draw.line(surface, (22, 34, 69), (cursor_x, cursor_y), (cursor_x, cursor_y + typed.get_height()), 2)

        self._draw_keyboard(surface, area, body_font)

        objective = body_font.render(
            f"{t(self.language, 'phone_objective_prefix')} {self.completed}/{self.required_total} {t(self.language, 'phone_objective_suffix')}",
            True,
            (45, 121, 96),
        )
        surface.blit(objective, (area.x + 18, area.y + area.height - 72))

        if self.last_result:
            color = (34, 139, 95) if self.last_result == t(self.language, "phone_sent") else (179, 66, 66)
            result_surface = body_font.render(self.last_result, True, color)
            surface.blit(result_surface, (area.x + 18, area.y + area.height - 42))

        if self.feedback_visible:
            self._draw_feedback_banner(surface, area, title_font, body_font)

    def _draw_feedback_banner(
        self,
        surface: pygame.Surface,
        area: pygame.Rect,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
    ) -> None:
        feedback_title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
        feedback_body_font = pygame.font.SysFont("Segoe UI", 15)

        slide_in = 1.0 - self.feedback_anim
        base_y = area.y + 8 - int(88 * slide_in)
        banner_y = base_y + int(self.feedback_drag_offset)
        banner_rect = pygame.Rect(area.x + 12, banner_y, area.width - 24, 128)

        overlay = pygame.Surface(area.size, pygame.SRCALPHA)
        overlay.fill((15, 20, 35, 62))
        surface.blit(overlay, area.topleft)

        shadow_rect = banner_rect.move(0, 6)
        shadow = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 45), shadow.get_rect(), border_radius=16)
        surface.blit(shadow, shadow_rect.topleft)

        pygame.draw.rect(surface, (255, 244, 246), banner_rect, border_radius=16)
        pygame.draw.rect(surface, (214, 78, 78), banner_rect, 3, border_radius=16)

        handle_center_x = banner_rect.centerx
        handle_y = banner_rect.y + 11
        for offset in (-12, 0, 12):
            pygame.draw.line(
                surface,
                (214, 78, 78),
                (handle_center_x + offset - 8, handle_y),
                (handle_center_x + offset + 8, handle_y),
                4,
            )

        title = feedback_title_font.render(self.feedback_title, True, (134, 36, 36))
        surface.blit(title, (banner_rect.x + 16, banner_rect.y + 28))

        if self.feedback_replies:
            for index, reply in enumerate(self.feedback_replies):
                reply_surface = feedback_body_font.render(f"• {reply}", True, (92, 36, 36))
                surface.blit(reply_surface, (banner_rect.x + 18, banner_rect.y + 56 + index * 20))

        swipe_hint = feedback_body_font.render(t(self.language, "phone_swipe_hint"), True, (134, 36, 36))
        surface.blit(swipe_hint, (banner_rect.x + 16, banner_rect.bottom - 20))

    def _feedback_handle_rect(self) -> pygame.Rect | None:
        if self._last_area is None:
            return None

        slide_in = 1.0 - self.feedback_anim
        base_y = self._last_area.y + 8 - int(88 * slide_in)
        banner_y = base_y + int(self.feedback_drag_offset)
        return pygame.Rect(self._last_area.x + 12, banner_y, self._last_area.width - 24, 128)

    def _draw_keyboard(self, surface: pygame.Surface, area: pygame.Rect, body_font: pygame.font.Font) -> None:
        self.key_buttons = []

        rows = ["QWERTYUIOPÅ", "ASDFGHJKLØÆ", "ZXCVBNM,.-"]
        left = area.x + 16
        keyboard_top = area.y + 358
        gap = 6
        key_height = 36

        for row_index, row in enumerate(rows):
            row_width = area.width - 32
            key_width = int((row_width - (len(row) - 1) * gap) / len(row))
            row_y = keyboard_top + row_index * (key_height + gap)
            row_used = len(row) * key_width + (len(row) - 1) * gap
            row_x = left + (row_width - row_used) // 2

            for char_index, char in enumerate(row):
                x = row_x + char_index * (key_width + gap)
                rect = pygame.Rect(x, row_y, key_width, key_height)
                self._draw_key(surface, rect, char, body_font)
                self.key_buttons.append((rect, char, "char"))

        special_y = keyboard_top + len(rows) * (key_height + gap) + 2
        special_gap = 6
        available = area.width - 32
        space_w = int(available * 0.46)
        backspace_w = int(available * 0.24)
        send_w = available - space_w - backspace_w - 2 * special_gap

        space_rect = pygame.Rect(left, special_y, space_w, 40)
        backspace_rect = pygame.Rect(space_rect.right + special_gap, special_y, backspace_w, 40)
        send_rect = pygame.Rect(backspace_rect.right + special_gap, special_y, send_w, 40)

        self._draw_key(surface, space_rect, t(self.language, "phone_space_label"), body_font)
        self._draw_key(surface, backspace_rect, t(self.language, "phone_backspace_label"), body_font)
        self._draw_key(surface, send_rect, t(self.language, "phone_send_label"), body_font)

        self.key_buttons.append((space_rect, " ", "space"))
        self.key_buttons.append((backspace_rect, "", "backspace"))
        self.key_buttons.append((send_rect, "", "send"))

    @staticmethod
    def _draw_key(surface: pygame.Surface, rect: pygame.Rect, label: str, font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=7)
        pygame.draw.rect(surface, (132, 153, 208), rect, 2, border_radius=7)
        text = font.render(label, True, (29, 45, 89))
        text_x = rect.centerx - text.get_width() // 2
        text_y = rect.centery - text.get_height() // 2
        surface.blit(text, (text_x, text_y))

    @staticmethod
    def _wrap_text(text: str, font: pygame.font.Font, width: int) -> list[str]:
        words = text.split(" ")
        lines: list[str] = []
        current = ""
        for word in words:
            trial = f"{current} {word}".strip()
            if font.size(trial)[0] <= width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    @staticmethod
    def _normalize_reply(value: str) -> str:
        cleaned = " ".join(value.strip().split())
        return cleaned.casefold()
