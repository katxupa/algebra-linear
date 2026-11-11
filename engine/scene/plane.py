"""The coordinate plane: faint fixed grid + live grid transformed by a matrix."""
from __future__ import annotations

import math

from ..linalg import Mat2, Vec2
from .. import theme
from . import draw


def draw_plane(surf, cam, m: Mat2 | None = None, show_basis: bool = True) -> None:
    m = m or Mat2.identity()
    ext = cam.visible_extent()
    n = int(math.ceil(ext))

    # fixed background grid
    for k in range(-n, n + 1):
        draw.line(surf, theme.GRID_BG, cam.to_screen((k, -ext)), cam.to_screen((k, ext)))
        draw.line(surf, theme.GRID_BG, cam.to_screen((-ext, k)), cam.to_screen((ext, k)))

    # transformed grid: map each grid line through m. Extend far enough for shears/stretches.
    stretch = max(0.25, min(m.i.length() or 1, m.j.length() or 1))
    k_max = min(60, int(math.ceil(ext / stretch)) + 1)
    far = k_max * 3 + ext
    for k in range(-k_max, k_max + 1):
        color = theme.GRID_MAJOR if k % 5 == 0 else theme.GRID
        if k == 0:
            continue
        draw.line(surf, color, cam.to_screen(m.apply((k, -far))), cam.to_screen(m.apply((k, far))))
        draw.line(surf, color, cam.to_screen(m.apply((-far, k))), cam.to_screen(m.apply((far, k))))
    # transformed axes
    draw.line(surf, theme.AXIS, cam.to_screen(m.apply((-far, 0))), cam.to_screen(m.apply((far, 0))), 2)
    draw.line(surf, theme.AXIS, cam.to_screen(m.apply((0, -far))), cam.to_screen(m.apply((0, far))), 2)

    if show_basis:
        o = cam.to_screen((0, 0))
        draw.arrow(surf, theme.I_HAT, o, cam.to_screen(m.i), theme.VECTOR_WIDTH_PX)
        draw.arrow(surf, theme.J_HAT, o, cam.to_screen(m.j), theme.VECTOR_WIDTH_PX)


def unit_square(m: Mat2) -> list[Vec2]:
    return [m.apply(p) for p in ((0, 0), (1, 0), (1, 1), (0, 1))]
