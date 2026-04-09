from __future__ import annotations

import random
from dataclasses import dataclass

import pygame


TEXT_OBJECTIVES = [
    ("Mamma", "Kommer du hjem til middag klokka 8?", ["ja", "kommer snart"]),
    ("Sjef", "Trenger statusoppdatering nå", ["jobber med det", "på saken"]),
    ("Venn", "Hvor er du nå?", ["på vei", "nesten fremme"]),
    ("Lagchat", "Kan du bekrefte at du kommer?", ["bekreftet", "jeg kommer"]),
    ("Trener", "Kommer du på trening i morgen?", ["ja jeg må", "ja"]),
    ("Nabo", "Kan du kjøpe melk?", ["klart det", "ok"]),
    ("Partner", "Ring meg når du er ledig", ["kjører nå", "ringer snart"]),
    ("Klassen", "Har du levert oppgaven?", ["levert", "ja levert"]),
    ("Storesøster", "Kan du svare når du er hjemme?", ["jeg er hjemme nå", "hjemme nå"]),
    ("Pappa", "Hvor skal du etterpå?", ["til børsa", "hjem"]),
]


@dataclass
class PhoneTask:
    sender: str
    message: str
    accepted_replies: list[str]


class PhoneSystem:
    def __init__(self, required_total: int) -> None:
        self.required_total = required_total
        self.completed = 0
        self.current_task = self._new_task()
        self.current_input = ""
        self.last_result = ""
        self.result_timer = 0.0
        self.cursor_timer = 0.0
        self.key_buttons: list[tuple[pygame.Rect, str, str]] = []

    @property
    def is_goal_reached(self) -> bool:
        return self.completed >= self.required_total

    def _new_task(self) -> PhoneTask:
        sender, message, replies = random.choice(TEXT_OBJECTIVES)
        return PhoneTask(sender=sender, message=message, accepted_replies=replies)

    def process_click(self, position: tuple[int, int]) -> bool:
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
                        self.last_result = "Sendt"
                        self.current_task = self._new_task()
                    else:
                        hints = " / ".join(self.current_task.accepted_replies[:2])
                        self.last_result = f"Feil. Godkjent svar: {hints}"
                    self.current_input = ""
                    self.result_timer = 2.7
                    return success
                if action == "char" and len(self.current_input) < 30:
                    self.current_input += label
                return False
        return False

    def update(self, dt: float) -> None:
        if self.result_timer > 0:
            self.result_timer = max(0.0, self.result_timer - dt)
            if self.result_timer == 0:
                self.last_result = ""
        self.cursor_timer += dt
        if self.cursor_timer > 1.0:
            self.cursor_timer -= 1.0

    def draw(self, surface: pygame.Surface, area: pygame.Rect, title_font: pygame.font.Font, body_font: pygame.font.Font) -> None:
        pygame.draw.rect(surface, (248, 250, 255), area, border_radius=14)
        pygame.draw.rect(surface, (35, 53, 98), area, 3, border_radius=14)

        notch = pygame.Rect(area.x + area.width // 2 - 56, area.y + 6, 112, 18)
        pygame.draw.rect(surface, (24, 34, 66), notch, border_radius=8)

        header = title_font.render("Telefon", True, (35, 53, 98))
        surface.blit(header, (area.x + 18, area.y + 30))

        sender_label = body_font.render(f"Fra: {self.current_task.sender}", True, (44, 66, 122))
        surface.blit(sender_label, (area.x + 18, area.y + 80))

        msg_bg = pygame.Rect(area.x + 16, area.y + 110, area.width - 32, 130)
        pygame.draw.rect(surface, (230, 238, 255), msg_bg, border_radius=10)
        wrapped_message = self._wrap_text(self.current_task.message, body_font, msg_bg.width - 18)
        for index, line in enumerate(wrapped_message):
            line_surf = body_font.render(line, True, (30, 46, 89))
            surface.blit(line_surf, (msg_bg.x + 10, msg_bg.y + 12 + index * 24))

        entry_label = body_font.render("Trykk svar på tastaturet:", True, (35, 53, 98))
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
            f"Mål: {self.completed}/{self.required_total} meldinger sendt",
            True,
            (45, 121, 96),
        )
        surface.blit(objective, (area.x + 18, area.y + area.height - 72))

        if self.last_result:
            color = (34, 139, 95) if self.last_result == "Sendt" else (179, 66, 66)
            result_surface = body_font.render(self.last_result, True, color)
            surface.blit(result_surface, (area.x + 18, area.y + area.height - 42))

    def _draw_keyboard(self, surface: pygame.Surface, area: pygame.Rect, body_font: pygame.font.Font) -> None:
        self.key_buttons = []

        rows = ["QWERTYUIOPÅ", "ASDFGHJKLØÆ", "ZXCVBNM"]
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

        self._draw_key(surface, space_rect, "MELLOMROM", body_font)
        self._draw_key(surface, backspace_rect, "SLETT", body_font)
        self._draw_key(surface, send_rect, "SEND", body_font)

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
