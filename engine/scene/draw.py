"""Low-level drawing primitives (anti-aliased where pygame-ce allows it)."""
from __future__ import annotations

import math

import pygame

_fonts: dict[int, pygame.font.Font] = {}


def font(size: int) -> pygame.font.Font:
    size = max(8, int(size))
    if size not in _fonts:
        _fonts[size] = pygame.font.Font(None, size)
    return _fonts[size]


def line(surf, color, p1, p2, width: int = 1) -> None:
    try:
        pygame.draw.aaline(surf, color, p1, p2, width)
    except TypeError:  # older pygame without aaline width
        pygame.draw.line(surf, color, p1, p2, width)


def circle(surf, color, center, radius: float, width: int = 0) -> None:
    try:
        pygame.draw.aacircle(surf, color, center, radius, width)
    except AttributeError:
        pygame.draw.circle(surf, color, center, radius, width)


def polygon(surf, color, points, width: int = 0) -> None:
    pygame.draw.polygon(surf, color, points, width)
    pygame.draw.aalines(surf, color, True, points)


def polygon_alpha(surf, color, points, alpha: int) -> None:
    """Translucent filled polygon."""
    if len(points) < 3:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w, h = int(max(xs)) - x0 + 2, int(max(ys)) - y0 + 2
    if w <= 0 or h <= 0 or w > 8000 or h > 8000:
        return
    layer = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*color[:3], alpha), [(x - x0, y - y0) for x, y in points])
    surf.blit(layer, (x0, y0))


def arrow(surf, color, p1, p2, width: int = 4, head: float = 16) -> None:
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1:
        circle(surf, color, p2, width)
        return
    ux, uy = dx / length, dy / length
    head = min(head, length * 0.6)
    base = (p2[0] - ux * head, p2[1] - uy * head)
    line(surf, color, p1, base, width)
    nx, ny = -uy, ux
    half = head * 0.5
    tri = [p2, (base[0] + nx * half, base[1] + ny * half), (base[0] - nx * half, base[1] - ny * half)]
    polygon(surf, color, tri)


def dashed_line(surf, color, p1, p2, width: int = 2, dash: float = 10) -> None:
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1:
        return
    n = int(length / dash)
    for k in range(0, n, 2):
        a, b = k / n, min(1, (k + 1) / n)
        line(surf, color, (p1[0] + dx * a, p1[1] + dy * a), (p1[0] + dx * b, p1[1] + dy * b), width)


def dashed_arrow(surf, color, p1, p2, width: int = 2, head: float = 14) -> None:
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    if length < 1:
        return
    ux, uy = dx / length, dy / length
    head = min(head, length * 0.6)
    base = (p2[0] - ux * head, p2[1] - uy * head)
    dashed_line(surf, color, p1, base, width)
    nx, ny = -uy, ux
    half = head * 0.5
    pygame.draw.aalines(surf, color, True,
                        [p2, (base[0] + nx * half, base[1] + ny * half), (base[0] - nx * half, base[1] - ny * half)])


def text(surf, s: str, pos, size: int = 28, color=(230, 232, 240), anchor: str = "center") -> pygame.Rect:
    img = font(size).render(s, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, (int(pos[0]), int(pos[1])))
    surf.blit(img, rect)
    return rect


_ARROWS = "→←↔"   # → ← ↔ (missing in the default font: drawn by hand)


def text_width(s: str, size: int) -> int:
    f = font(size)
    w = 0
    for part in _split_arrows(s):
        w += int(size * 0.9) if part in _ARROWS and len(part) == 1 else f.size(part)[0]
    return w


def _split_arrows(s: str):
    buf = ""
    for ch in s:
        if ch in _ARROWS:
            if buf:
                yield buf
            buf = ""
            yield ch
        else:
            buf += ch
    if buf:
        yield buf


def text_setas(surf, s: str, pos, size: int = 28, color=(230, 232, 240), anchor: str = "center") -> pygame.Rect:
    """Like text(), but also draws → ← ↔ (row-operation notation)."""
    w, h = text_width(s, size), font(size).get_height()
    rect = pygame.Rect(0, 0, w, h)
    setattr(rect, anchor, (int(pos[0]), int(pos[1])))
    x, cy = rect.x, rect.centery
    f = font(size)
    for part in _split_arrows(s):
        if len(part) == 1 and part in _ARROWS:
            aw = size * 0.9
            x0, x1 = x + aw * 0.12, x + aw * 0.88
            lw = max(2, size // 14)
            hd = size * 0.22
            line(surf, color, (x0, cy), (x1, cy), lw)
            if part in "→↔":
                line(surf, color, (x1, cy), (x1 - hd, cy - hd), lw)
                line(surf, color, (x1, cy), (x1 - hd, cy + hd), lw)
            if part in "←↔":
                line(surf, color, (x0, cy), (x0 + hd, cy - hd), lw)
                line(surf, color, (x0, cy), (x0 + hd, cy + hd), lw)
            x += aw
        else:
            img = f.render(part, True, color)
            surf.blit(img, img.get_rect(midleft=(int(x), cy)))
            x += img.get_width()
    return rect


def matrix(surf, rows, pos, size: int = 34, color=(230, 232, 240), col_colors=None) -> pygame.Rect:
    """Draw a matrix (any size, e.g. 2x2 or a 2x1 column vector) with brackets, centered at pos.
    col_colors colors each column."""
    from ..linalg import fmt_num
    f = font(size)
    cells = [[f.render(fmt_num(v), True, (col_colors[c] if col_colors else color))
              for c, v in enumerate(row)] for row in rows]
    col_w = max(img.get_width() for row in cells for img in row) + size * 0.5
    row_h = size * 0.95
    w, h = col_w * len(rows[0]), row_h * len(rows)
    x0, y0 = pos[0] - w / 2, pos[1] - h / 2
    for r, row in enumerate(cells):
        for c, img in enumerate(row):
            cx, cy = x0 + col_w * (c + 0.5), y0 + row_h * (r + 0.5)
            surf.blit(img, img.get_rect(center=(int(cx), int(cy))))
    tick = size * 0.25
    for side in (-1, 1):
        x = x0 - 4 if side < 0 else x0 + w + 4
        pts = [(x - side * tick, y0), (x, y0), (x, y0 + h), (x - side * tick, y0 + h)]
        pygame.draw.lines(surf, color, False, pts, 2)
    return pygame.Rect(int(x0), int(y0), int(w), int(h))
