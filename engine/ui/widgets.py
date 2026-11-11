"""Interactive widgets. All work with mouse and touch (SDL turns touches into mouse events)."""
from __future__ import annotations

import math

import pygame

from .. import theme
from ..linalg import Vec2
from ..scene import draw


class Handle:
    """A draggable point in world space, snapping to a grid step on release (and while dragging)."""

    def __init__(self, pos, color, snap: float = 1.0, limit: float = theme.WORLD_RADIUS):
        self.pos = Vec2.of(pos)
        self.color = color
        self.snap = snap
        self.limit = limit
        self.dragging = False
        self.grab_offset = Vec2()
        self.enabled = True

    def hit(self, cam, sx, sy) -> bool:
        hx, hy = cam.to_screen(self.pos)
        return math.hypot(sx - hx, sy - hy) <= theme.HANDLE_RADIUS_PX * 1.4

    def press(self, cam, sx, sy) -> bool:
        if self.enabled and self.hit(cam, sx, sy):
            self.dragging = True
            self.grab_offset = self.pos - cam.to_world(sx, sy)
            return True
        return False

    def move(self, cam, sx, sy) -> bool:
        if not self.dragging:
            return False
        p = cam.to_world(sx, sy) + self.grab_offset
        lim = self.limit
        p = Vec2(max(-lim, min(lim, p.x)), max(-lim, min(lim, p.y)))
        self.pos = p.snapped(self.snap) if self.snap else p
        return True

    def release(self) -> bool:
        was = self.dragging
        self.dragging = False
        return was

    def draw(self, surf, cam, scale: float = 1.0) -> None:
        if not self.enabled:
            return
        c = cam.to_screen(self.pos)
        r = theme.HANDLE_RADIUS_PX * 0.45 * scale * (1.3 if self.dragging else 1.0)
        draw.circle(surf, self.color, c, r + 4, 2)
        draw.circle(surf, self.color, c, r * 0.55)


class Button:
    """Screen-space round icon button. icon: 'check', 'back', 'plus', 'minus'."""

    def __init__(self, icon: str, color=theme.TEXT, radius: int = 30):
        self.icon = icon
        self.color = color
        self.radius = radius
        self.center = (0, 0)
        self.visible = True
        self.flash = 0.0

    def place(self, x, y) -> "Button":
        self.center = (x, y)
        return self

    def hit(self, sx, sy) -> bool:
        return self.visible and math.hypot(sx - self.center[0], sy - self.center[1]) <= self.radius * 1.2

    def update(self, dt) -> None:
        self.flash = max(0.0, self.flash - dt * 4)

    def draw(self, surf) -> None:
        if not self.visible:
            return
        cx, cy = self.center
        r = self.radius
        fill = [int(a + (b - a) * self.flash) for a, b in zip(theme.PANEL, theme.PANEL_HI)]
        draw.circle(surf, fill, (cx, cy), r)
        draw.circle(surf, self.color, (cx, cy), r, 2)
        s = r * 0.45
        w = max(3, r // 8)
        if self.icon == "check":
            draw.line(surf, self.color, (cx - s, cy), (cx - s * 0.25, cy + s * 0.7), w)
            draw.line(surf, self.color, (cx - s * 0.25, cy + s * 0.7), (cx + s, cy - s * 0.6), w)
        elif self.icon == "back":
            draw.line(surf, self.color, (cx + s * 0.3, cy - s), (cx - s * 0.5, cy), w)
            draw.line(surf, self.color, (cx - s * 0.5, cy), (cx + s * 0.3, cy + s), w)
        elif self.icon in ("plus", "minus"):
            draw.line(surf, self.color, (cx - s, cy), (cx + s, cy), w)
            if self.icon == "plus":
                draw.line(surf, self.color, (cx, cy - s), (cx, cy + s), w)
        elif self.icon == "play":
            draw.polygon(surf, self.color, [(cx - s * 0.6, cy - s), (cx - s * 0.6, cy + s), (cx + s, cy)])


class MatrixEditor:
    """2x2 matrix with +/- buttons on every entry. Columns colored like î and ĵ."""

    def __init__(self, rows=((1, 0), (0, 1)), step: float = 1.0, limit: float = 5):
        self.values = [list(map(float, r)) for r in rows]
        self.step = step
        self.limit = limit
        self.buttons: list[tuple[Button, int, int, float]] = []
        for r in range(2):
            for c in range(2):
                self.buttons.append((Button("plus", radius=18), r, c, +1))
                self.buttons.append((Button("minus", radius=18), r, c, -1))
        self.center = (0, 0)
        self.size = 40

    def layout(self, cx, cy, size: int = 40) -> None:
        self.center, self.size = (cx, cy), size
        col_w = size * 4.0
        row_h = size * 1.5
        for b, r, c, sign in self.buttons:
            x = cx + (c - 0.5) * col_w + (sign * size * 1.05)
            y = cy + (r - 0.5) * row_h
            b.place(x, y)
            b.radius = max(14, int(size * 0.38))

    def press(self, sx, sy) -> bool:
        for b, r, c, sign in self.buttons:
            if b.hit(sx, sy):
                v = self.values[r][c] + sign * self.step
                self.values[r][c] = max(-self.limit, min(self.limit, v))
                b.flash = 1.0
                return True
        return False

    def update(self, dt) -> None:
        for b, *_ in self.buttons:
            b.update(dt)

    def draw(self, surf) -> None:
        from ..linalg import fmt_num
        cx, cy = self.center
        col_w = self.size * 4.0
        row_h = self.size * 1.5
        colors = (theme.I_HAT, theme.J_HAT)
        for r in range(2):
            for c in range(2):
                draw.text(surf, fmt_num(self.values[r][c]),
                          (cx + (c - 0.5) * col_w, cy + (r - 0.5) * row_h), int(self.size), colors[c])
        h = row_h * 2
        x_left, x_right = cx - col_w * 1.05, cx + col_w * 1.05
        t = self.size * 0.3
        pygame.draw.lines(surf, theme.TEXT, False,
                          [(x_left + t, cy - h / 2), (x_left, cy - h / 2), (x_left, cy + h / 2), (x_left + t, cy + h / 2)], 2)
        pygame.draw.lines(surf, theme.TEXT, False,
                          [(x_right - t, cy - h / 2), (x_right, cy - h / 2), (x_right, cy + h / 2), (x_right - t, cy + h / 2)], 2)
        for b, *_ in self.buttons:
            b.draw(surf)
