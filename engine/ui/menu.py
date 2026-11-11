"""Menu: one card per aula found in aulas/. Tap a card to play."""
from __future__ import annotations

import math

import pygame

from .. import theme
from ..scene import draw
from ..textos import t


class Menu:
    def __init__(self, app):
        self.app = app
        self.cards: list[tuple[pygame.Rect, object]] = []
        self.time = 0.0
        self.resize(app.width, app.height)

    def resize(self, w: int, h: int) -> None:
        aulas = self.app.aulas
        n = max(1, len(aulas))
        size = max(110, min(180, int(min(w, h) / 3.2)))
        gap = size // 5
        cols = max(1, min(n, (w - gap) // (size + gap)))
        rows = math.ceil(n / cols)
        total_w = cols * size + (cols - 1) * gap
        total_h = rows * size + (rows - 1) * gap
        x0 = (w - total_w) // 2
        y0 = max(110, (h - total_h) // 2)
        self.cards = []
        for k, aula in enumerate(aulas):
            r, c = divmod(k, cols)
            rect = pygame.Rect(x0 + c * (size + gap), y0 + r * (size + gap), size, size)
            self.cards.append((rect, aula))

    def handle_event(self, ev) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            for rect, aula in self.cards:
                if rect.collidepoint(ev.pos) and not aula.erro:
                    self.app.open_aula(aula)
                    return

    def update(self, dt: float) -> None:
        self.time += dt

    def draw(self, surf) -> None:
        surf.fill(theme.BG)
        w, h = surf.get_size()
        # animated decorative basis vectors in the title area
        a = self.time * 0.6
        o = (w / 2, 60)
        draw.arrow(surf, theme.I_HAT, o, (o[0] + 40 * math.cos(a), o[1] - 40 * math.sin(a)), 4)
        draw.arrow(surf, theme.J_HAT, o, (o[0] + 40 * math.cos(a + 1.8), o[1] - 40 * math.sin(a + 1.8)), 4)

        if not self.cards:
            draw.text(surf, t("sem_aulas"), (w / 2, h / 2), 32, theme.TEXT_DIM)
        mouse = pygame.mouse.get_pos()
        for rect, aula in self.cards:
            done = aula.id in self.app.done
            hover = rect.collidepoint(mouse) and not aula.erro
            border = theme.BAD if aula.erro else theme.OK if done else theme.GRID_MAJOR
            pygame.draw.rect(surf, theme.PANEL_HI if hover else theme.PANEL, rect, border_radius=18)
            pygame.draw.rect(surf, border, rect, 3, border_radius=18)
            draw.text(surf, str(aula.numero), (rect.centerx, rect.centery - rect.h * 0.08),
                      int(rect.h * 0.5), theme.TEXT)
            label = t("aula_com_erro") if aula.erro else aula.titulo
            draw.text(surf, label[:16], (rect.centerx, rect.bottom - rect.h * 0.16),
                      int(rect.h * 0.15), theme.BAD if aula.erro else theme.TEXT_DIM)
            if done:
                cx, cy, s = rect.right - 22, rect.top + 22, 8
                draw.line(surf, theme.OK, (cx - s, cy), (cx - s * 0.3, cy + s * 0.7), 3)
                draw.line(surf, theme.OK, (cx - s * 0.3, cy + s * 0.7), (cx + s, cy - s * 0.6), 3)

