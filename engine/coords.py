"""World (math units, y up) <-> screen (pixels, y down) camera."""
from __future__ import annotations

from .linalg import Vec2
from . import theme


class Camera:
    def __init__(self, width: int, height: int, radius: float = theme.WORLD_RADIUS,
                 top_margin: int = 0, bottom_margin: int = 0):
        self.radius = radius
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.resize(width, height)

    def resize(self, width: int, height: int) -> None:
        self.width, self.height = width, height
        usable_h = max(1, height - self.top_margin - self.bottom_margin)
        self.scale = min(width, usable_h) / (2 * self.radius + 0.6)
        self.ox = width / 2
        self.oy = self.top_margin + usable_h / 2

    def to_screen(self, p) -> tuple[float, float]:
        p = Vec2.of(p)
        return (self.ox + p.x * self.scale, self.oy - p.y * self.scale)

    def to_world(self, sx: float, sy: float) -> Vec2:
        return Vec2((sx - self.ox) / self.scale, (self.oy - sy) / self.scale)

    def visible_extent(self) -> float:
        """Half-size, in world units, of the largest visible axis."""
        return max(self.width, self.height) / (2 * self.scale) + 1
