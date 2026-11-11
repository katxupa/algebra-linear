"""Matrix challenges: MoverBase, EditarMatriz, Determinante."""
from __future__ import annotations

import math

from ..linalg import Mat2, Vec2, fmt_num
from ..scene import draw
from ..scene.plane import unit_square
from ..ui.widgets import Handle, MatrixEditor
from .. import theme
from .base import Desafio, SUCESSO, ERRO, ERROS_MATRIZ, erro_matriz, ghost_basis


def _ghost_shape(surf, cam, m: Mat2, alpha: float = 1.0):
    pts = [cam.to_screen(p) for p in unit_square(m)]
    draw.polygon_alpha(surf, theme.GHOST, pts, int(40 + 30 * alpha))
    ghost_basis(surf, cam, m, alpha)


class MoverBase(Desafio):
    """Drag î (green) and ĵ (red); the whole grid follows. Goal shown as the matrix
    (`ver="matriz"`) or as a ghost shape (`ver="forma"`). Confirm with ✓."""

    ERROS = ERROS_MATRIZ
    confirmar = True

    def __init__(self, matriz, ver: str = "matriz", **kw):
        super().__init__(**kw)
        self.alvo = Mat2.of(matriz)
        self.ver = ver

    def iniciar(self):
        self.hi = Handle((1, 0), theme.I_HAT)
        self.hj = Handle((0, 1), theme.J_HAT)
        self.handles = [self.hi, self.hj]

    def matriz(self):
        return Mat2.from_cols(self.hi.pos, self.hj.pos)

    def avaliar(self):
        return erro_matriz(self.matriz(), self.alvo)

    def desenhar(self, surf, ctx):
        if self.ver == "forma":
            _ghost_shape(surf, ctx.cam, self.alvo)
        pts = [ctx.cam.to_screen(p) for p in unit_square(self.matriz())]
        draw.polygon_alpha(surf, theme.AREA, pts, 50)
        for h in self.handles:
            h.draw(surf, ctx.cam)

    def desenhar_alvo(self, surf, ctx):
        if self.ver == "matriz":
            draw.matrix(surf, self.alvo.rows(), (ctx.width / 2, ctx.hud_y), 40,
                        col_colors=(theme.I_HAT, theme.J_HAT))

    def desenhar_dica(self, surf, ctx):
        ghost_basis(surf, ctx.cam, self.alvo, ctx.hint_alpha)

    def descricao(self):
        return f"mover î e ĵ para formar {self.alvo.fmt()}"


class EditarMatriz(Desafio):
    """Tap +/− on the matrix entries until the grid covers the ghost shape. Confirm with ✓."""

    ERROS = ERROS_MATRIZ
    confirmar = True
    painel = True

    def __init__(self, alvo, inicio=((1, 0), (0, 1)), **kw):
        super().__init__(**kw)
        self.alvo = Mat2.of(alvo)
        self.inicio = inicio

    def iniciar(self):
        self.editor = MatrixEditor(self.inicio)
        self.mostrada = Mat2.of(self.inicio)

    def valor(self) -> Mat2:
        return Mat2.of(self.editor.values)

    def estado(self):
        return self.valor()

    def matriz(self):
        return self.mostrada

    def update(self, ctx):
        # grid glides smoothly toward the edited matrix
        k = 1 - math.exp(-ctx.dt * 8)
        self.mostrada = self.mostrada.lerp(self.valor(), k)
        self.editor.update(ctx.dt)

    def avaliar(self):
        return erro_matriz(self.valor(), self.alvo)

    def layout(self, ctx):
        size = max(22, min(44, int((ctx.width - 40) / 9), int(ctx.height / 16)))
        self.editor.layout(ctx.width / 2, ctx.bottom_y, size)

    def press(self, ctx, sx, sy):
        return self.editor.press(sx, sy)

    def desenhar(self, surf, ctx):
        _ghost_shape(surf, ctx.cam, self.alvo)
        pts = [ctx.cam.to_screen(p) for p in unit_square(self.mostrada)]
        draw.polygon_alpha(surf, theme.AREA, pts, 50)

    def desenhar_painel(self, surf, ctx):
        self.editor.draw(surf)

    def desenhar_dica(self, surf, ctx):
        # mark where î and ĵ must land, with their coordinates
        cam = ctx.cam
        for v, color in ((self.alvo.i, theme.I_HAT), (self.alvo.j, theme.J_HAT)):
            c = tuple(int(x * (0.3 + 0.7 * ctx.hint_alpha)) for x in color)
            draw.circle(surf, c, cam.to_screen(v), 10, 3)
            sx, sy = cam.to_screen(v)
            draw.text(surf, v.fmt(), (sx + 14, sy - 14), 24, c, "midleft")

    def descricao(self):
        return f"editar matriz até {self.alvo.fmt()}"


class Determinante(Desafio):
    """Drag î and ĵ so the yellow area equals `area` (negative = flipped). Confirm with ✓."""

    ERROS = {
        "orientacao": "área certa, mas virada (sinal do determinante trocado: î e ĵ invertidos)",
        "quase": "área errada por 1",
        "zero": "esmagou tudo numa linha (área 0)",
    }
    confirmar = True

    def __init__(self, area, **kw):
        super().__init__(**kw)
        self.area = float(area)

    def iniciar(self):
        self.hi = Handle((1, 0), theme.I_HAT)
        self.hj = Handle((0, 1), theme.J_HAT)
        self.handles = [self.hi, self.hj]

    def matriz(self):
        return Mat2.from_cols(self.hi.pos, self.hj.pos)

    def avaliar(self):
        det = self.matriz().det()
        if abs(det - self.area) < 1e-6:
            return SUCESSO
        if abs(det + self.area) < 1e-6:
            return "orientacao"
        if abs(det) < 1e-6:
            return "zero"
        if abs(det - self.area) <= 1 + 1e-6:
            return "quase"
        return ERRO

    def desenhar(self, surf, ctx):
        m = self.matriz()
        det = m.det()
        pts = [ctx.cam.to_screen(p) for p in unit_square(m)]
        color = theme.AREA if det >= 0 else theme.BAD
        draw.polygon_alpha(surf, color, pts, 80)
        center = ctx.cam.to_screen(m.apply((0.5, 0.5)))
        draw.text(surf, fmt_num(det), center, 34, color)
        for h in self.handles:
            h.draw(surf, ctx.cam)

    def desenhar_alvo(self, surf, ctx):
        cx, y = ctx.width / 2, ctx.hud_y
        s = 22
        draw.polygon_alpha(surf, theme.AREA, [(cx - 70, y - s), (cx - 70 + 2 * s, y - s),
                                             (cx - 70 + 2 * s, y + s), (cx - 70, y + s)], 120)
        draw.text(surf, f"= {fmt_num(self.area)}", (cx, y), 52, theme.AREA, "midleft")

    def desenhar_dica(self, surf, ctx):
        # one simple solution: î stretched along x, ĵ untouched
        alvo = Mat2(self.area, 0, 0, 1) if abs(self.area) <= theme.WORLD_RADIUS else Mat2(1, 0, 0, 1)
        ghost_basis(surf, ctx.cam, alvo, ctx.hint_alpha)

    def descricao(self):
        return f"área (determinante) = {fmt_num(self.area)}"
