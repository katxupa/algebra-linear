"""Vector challenges: MoverVetor, SomarVetores, Escalar."""
from __future__ import annotations

from ..linalg import Vec2, fmt_num
from ..scene import draw
from ..ui.widgets import Handle
from .. import theme
from .base import Desafio, SUCESSO, ERRO, ERROS_VETOR, erro_vetor


def _vector(surf, cam, tail, tip, color, width=theme.VECTOR_WIDTH_PX):
    draw.arrow(surf, color, cam.to_screen(tail), cam.to_screen(tip), width)


def _coords_label(surf, cam, p: Vec2, color):
    sx, sy = cam.to_screen(p)
    dx = 18 if p.x >= 0 else -18
    dy = -18 if p.y >= 0 else 18
    draw.text(surf, p.fmt(), (sx + dx, sy + dy), 26, color, "midleft" if dx > 0 else "midright")


def _snap_for(*points) -> float:
    """Grid step that reaches every given point (1 for integers, else 0.5)."""
    ok = all(abs(c * 1 - round(c)) < 1e-6 for p in points for c in p)
    return 1.0 if ok else 0.5


class MoverVetor(Desafio):
    """Drag the vector tip to the target written as a column vector.
    `mostrar_alvo=True` also shows the target as a ghost arrow from the start."""

    ERROS = ERROS_VETOR

    def __init__(self, para, de=(1, 1), mostrar_alvo: bool = False, **kw):
        super().__init__(**kw)
        self.alvo = Vec2.of(para)
        self.inicio = Vec2.of(de)
        self.mostrar_alvo = mostrar_alvo

    def iniciar(self):
        self.tip = Handle(self.inicio, theme.VEC, snap=_snap_for(self.alvo, self.inicio))
        self.handles = [self.tip]

    def avaliar(self):
        return erro_vetor(self.tip.pos, self.alvo)

    def desenhar(self, surf, ctx):
        cam = ctx.cam
        if self.mostrar_alvo:
            draw.dashed_arrow(surf, theme.GHOST, cam.to_screen((0, 0)), cam.to_screen(self.alvo), 3)
        _vector(surf, cam, (0, 0), self.tip.pos, theme.VEC)
        _coords_label(surf, cam, self.tip.pos, theme.VEC)
        self.tip.draw(surf, cam)

    def desenhar_alvo(self, surf, ctx):
        draw.matrix(surf, [[self.alvo.x], [self.alvo.y]], (ctx.width / 2, ctx.hud_y), 40, theme.VEC)

    def desenhar_dica(self, surf, ctx):
        cam = ctx.cam
        c = tuple(int(v * (0.3 + 0.7 * ctx.hint_alpha)) for v in theme.GHOST)
        # walk: x along the axis, then y up/down
        corner = Vec2(self.alvo.x, 0)
        draw.dashed_line(surf, theme.I_HAT, cam.to_screen((0, 0)), cam.to_screen(corner), 3)
        draw.dashed_line(surf, theme.J_HAT, cam.to_screen(corner), cam.to_screen(self.alvo), 3)
        draw.circle(surf, c, cam.to_screen(self.alvo), 10, 2)

    def descricao(self):
        return f"mover vetor até {self.alvo.fmt()}"


class SomarVetores(Desafio):
    """v is fixed at the origin; drag w by its tail. Solved when w starts at v's tip
    (tip-to-tail). On success the sum v + w appears."""

    ERROS = {
        "ao_contrario": "encostou a PONTA de w na ponta de v (em vez do início de w)",
        "quase": "ficou a 1 casinha do lugar certo",
    }

    def __init__(self, v, w, **kw):
        super().__init__(**kw)
        self.v = Vec2.of(v)
        self.w = Vec2.of(w)

    def iniciar(self):
        start = next(p for p in (Vec2(-3, -3), Vec2(3, -3), Vec2(-3, 3))
                     if not p.close(self.v) and not (p + self.w).close(self.v))
        self.tail = Handle(start, theme.VEC2, snap=_snap_for(self.v, self.w), limit=theme.WORLD_RADIUS)
        self.handles = [self.tail]

    def avaliar(self):
        t = self.tail.pos
        if t.close(self.v):
            return SUCESSO
        if (t + self.w).close(self.v):
            return "ao_contrario"
        if max(abs(t.x - self.v.x), abs(t.y - self.v.y)) <= 1 + 1e-6:
            return "quase"
        return ERRO

    def desenhar(self, surf, ctx):
        cam = ctx.cam
        if ctx.solved:
            _vector(surf, cam, (0, 0), self.v + self.w, theme.RESULT, theme.VECTOR_WIDTH_PX + 2)
            _coords_label(surf, cam, self.v + self.w, theme.RESULT)
        _vector(surf, cam, (0, 0), self.v, theme.VEC)
        _vector(surf, cam, self.tail.pos, self.tail.pos + self.w, theme.VEC2)
        self.tail.draw(surf, cam)

    def desenhar_alvo(self, surf, ctx):
        cx, y = ctx.width / 2, ctx.hud_y
        draw.text(surf, "v", (cx - 50, y), 52, theme.VEC)
        draw.text(surf, "+", (cx, y), 52, theme.TEXT)
        draw.text(surf, "w", (cx + 50, y), 52, theme.VEC2)

    def desenhar_dica(self, surf, ctx):
        cam = ctx.cam
        c = tuple(int(v * (0.3 + 0.7 * ctx.hint_alpha)) for v in theme.VEC2)
        draw.dashed_arrow(surf, c, cam.to_screen(self.v), cam.to_screen(self.v + self.w), 3)

    def descricao(self):
        return f"somar v={self.v.fmt()} + w={self.w.fmt()}"


class Escalar(Desafio):
    """v is fixed; drag the free vector to k·v."""

    ERROS = {
        "sinal": "apontou para o lado contrário (−k·v)",
        "paralelo": "na direção certa, mas tamanho errado",
        "quase": "ficou a 1 casinha do lugar certo",
    }

    def __init__(self, v, por, **kw):
        super().__init__(**kw)
        self.v = Vec2.of(v)
        self.k = float(por)
        self.alvo = self.v * self.k

    def iniciar(self):
        start = Vec2(self.v.y, -self.v.x).snapped() if self.v.length() else Vec2(1, 0)
        self.tip = Handle(start, theme.RESULT, snap=_snap_for(self.alvo))
        self.handles = [self.tip]

    def avaliar(self):
        p = self.tip.pos
        if p.close(self.alvo):
            return SUCESSO
        if p.close(-self.alvo):
            return "sinal"
        if p.length() > 1e-6 and abs(p.cross(self.v)) < 1e-6:
            return "paralelo"
        if max(abs(p.x - self.alvo.x), abs(p.y - self.alvo.y)) <= 1 + 1e-6:
            return "quase"
        return ERRO

    def desenhar(self, surf, ctx):
        cam = ctx.cam
        _vector(surf, cam, (0, 0), self.tip.pos, theme.RESULT)
        _vector(surf, cam, (0, 0), self.v, theme.VEC)
        _coords_label(surf, cam, self.tip.pos, theme.RESULT)
        self.tip.draw(surf, cam)

    def desenhar_alvo(self, surf, ctx):
        cx, y = ctx.width / 2, ctx.hud_y
        draw.text(surf, fmt_num(self.k), (cx - 8, y), 52, theme.RESULT, "midright")
        draw.text(surf, "v", (cx + 8, y), 52, theme.VEC, "midleft")

    def desenhar_dica(self, surf, ctx):
        cam = ctx.cam
        c = tuple(int(v * (0.3 + 0.7 * ctx.hint_alpha)) for v in theme.GHOST)
        far = self.v * (12 / max(self.v.length(), 1e-6))
        draw.dashed_line(surf, c, cam.to_screen(-far), cam.to_screen(far), 2)
        # copies of v laid tip-to-tail
        n = int(abs(self.k))
        step = self.v if self.k >= 0 else -self.v
        for i in range(n):
            draw.dashed_arrow(surf, c, cam.to_screen(step * i), cam.to_screen(step * (i + 1)), 2)

    def descricao(self):
        return f"escalar {fmt_num(self.k)}·{self.v.fmt()}"
