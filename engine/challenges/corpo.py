"""Field (corpo) challenges: an equation with a blank and number tiles to tap.

Each type builds its own equation, options and known mistakes from a few numbers:
    Neutro("+"), Simetrico(5), Inverso(5), Inverso(0), Comutativa(3, 4),
    Associativa(2, 3, 4), Distributiva(2, 3, 4)
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

import pygame

from .. import theme
from ..scene import draw
from .base import Desafio, SUCESSO, ERRO

LACUNA = object()        # the blank in the equation
NAO_EXISTE = "nao_existe"  # "there is no such number" tile (drawn as a crossed-out circle)


def _num(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x).limit_denominator(1000)


def fmt(v) -> str:
    if v is NAO_EXISTE:
        return ""
    if isinstance(v, str):
        return v
    v = _num(v)
    s = str(abs(v.numerator)) if v.denominator == 1 else f"{abs(v.numerator)}/{v.denominator}"
    return ("−" if v < 0 else "") + s


class Tile:
    def __init__(self, valor):
        self.valor = valor
        self.rect = pygame.Rect(0, 0, 0, 0)


class Completar(Desafio):
    """Generic 'fill the blank' challenge. Subclasses only describe the equation."""

    plano = False
    #: shown blinking after `dica_apos` failed attempts (a pattern, like a cheat sheet)
    regra = ""

    def __init__(self, conta, resposta, opcoes, erros=None, **kw):
        super().__init__(**kw)
        self.conta = conta
        self.resposta = resposta
        uniq = []
        for o in opcoes:
            if not any(_same(o, u) for u in uniq):
                uniq.append(o)
        random.Random(repr(conta)).shuffle(uniq)
        self.opcoes = uniq
        self.erros_valor = erros or {}

    # -- state ----------------------------------------------------------------------
    def iniciar(self):
        self.tiles = [Tile(v) for v in self.opcoes]
        self.sel = None
        self.pressed = False

    def estado(self):
        return None if self.sel is None else repr(self.sel)

    def avaliar(self):
        if _same(self.sel, self.resposta):
            return SUCESSO
        for valor, chave in self.erros_valor.items():
            if _same(self.sel, valor):
                return chave
        return ERRO

    # -- input ----------------------------------------------------------------------
    def press(self, ctx, sx, sy):
        for t in self.tiles:
            if t.rect.collidepoint(sx, sy):
                self.sel = t.valor
                self.pressed = True
                return True
        return False

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        was, self.pressed = self.pressed, False
        return was

    # -- layout / drawing -------------------------------------------------------------
    def _sizes(self, ctx):
        return max(40, min(84, int(ctx.width / 14))), max(70, min(120, int(ctx.width / 8)))

    def layout(self, ctx):
        _, tile = self._sizes(ctx)
        gap = tile // 4
        per_row = max(1, min(len(self.tiles), (ctx.width - 40) // (tile + gap)))
        rows = math.ceil(len(self.tiles) / per_row)
        y0 = ctx.height * 0.62
        for k, t in enumerate(self.tiles):
            r, c = divmod(k, per_row)
            n = min(per_row, len(self.tiles) - r * per_row)
            x0 = (ctx.width - (n * tile + (n - 1) * gap)) / 2
            t.rect = pygame.Rect(int(x0 + c * (tile + gap)), int(y0 + r * (tile + gap)), tile, tile)
        self._rows = rows

    def desenhar(self, surf, ctx):
        size, tile = self._sizes(ctx)
        cy = ctx.height * 0.38
        filled = self.resposta if ctx.solved else None
        self._equation(surf, ctx.width / 2, cy, size, filled, ctx)
        for t in self.tiles:
            chosen = self.sel is not None and _same(t.valor, self.sel)
            if ctx.solved and chosen:
                border, fill = theme.OK, theme.PANEL_HI
            elif chosen:
                border, fill = theme.BAD, theme.PANEL_HI
            else:
                border, fill = theme.GRID_MAJOR, theme.PANEL
            pygame.draw.rect(surf, fill, t.rect, border_radius=16)
            pygame.draw.rect(surf, border, t.rect, 3, border_radius=16)
            _value(surf, t.valor, t.rect.center, int(tile * 0.42), theme.TEXT)

    def desenhar_dica(self, surf, ctx):
        if self.regra:
            size, _ = self._sizes(ctx)
            c = tuple(int(v * (0.35 + 0.65 * ctx.hint_alpha)) for v in theme.VEC2)
            draw.text(surf, self.regra, (ctx.width / 2, ctx.height * 0.38 - size * 1.3), int(size * 0.6), c)

    def _layout_equation(self, size):
        f = draw.font(size)
        parts = [("box", int(size * 1.5)) if tok is LACUNA else ("img", f.render(fmt(tok), True, theme.TEXT))
                 for tok in self.conta]
        space = size * 0.18
        total = sum((p[1] if p[0] == "box" else p[1].get_width()) for p in parts) + space * (len(parts) - 1)
        return parts, space, total

    def _equation(self, surf, cx, cy, size, filled, ctx):
        parts, space, total = self._layout_equation(size)
        if total > ctx.width - 40:  # long equation on a narrow (phone) screen: shrink to fit
            size = max(18, int(size * (ctx.width - 40) / total))
            parts, space, total = self._layout_equation(size)
        x = cx - total / 2
        for kind, obj in parts:
            if kind == "box":
                rect = pygame.Rect(int(x), int(cy - size * 0.6), obj, int(size * 1.2))
                color = theme.OK if filled is not None else theme.VEC
                pygame.draw.rect(surf, theme.PANEL, rect, border_radius=10)
                pygame.draw.rect(surf, color, rect, 3, border_radius=10)
                if filled is not None:
                    _value(surf, filled, rect.center, int(size * 0.8), theme.OK)
                x += obj + space
            else:
                surf.blit(obj, obj.get_rect(midleft=(int(x), int(cy))))
                x += obj.get_width() + space

    def descricao(self):
        return " ".join("▢" if t is LACUNA else fmt(t) for t in self.conta)


def _same(a, b) -> bool:
    if a is None or b is None:
        return a is b
    if a is NAO_EXISTE or b is NAO_EXISTE:
        return a is b
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    return _num(a) == _num(b)


def _value(surf, v, center, size, color):
    if v is NAO_EXISTE:  # crossed-out circle: "no such number"
        r = size * 0.55
        draw.circle(surf, color, center, r, 3)
        draw.line(surf, color, (center[0] - r * 1.2, center[1] + r * 1.2),
                  (center[0] + r * 1.2, center[1] - r * 1.2), 3)
    else:
        draw.text(surf, fmt(v), center, size, color)


# ---- the field axioms, as challenge types --------------------------------------------------

class Neutro(Completar):
    """a + ▢ = a  (answer 0)   or   a · ▢ = a  (answer 1)."""
    ERROS = {"neutro_trocado": "trocou o neutro da soma (0) com o do produto (1)"}

    def __init__(self, op: str = "+", a=7, **kw):
        soma = op == "+"
        sinal = "+" if soma else "·"
        certo, trocado = (0, 1) if soma else (1, 0)
        self.regra = "a + 0 = a" if soma else "a · 1 = a"
        super().__init__([a, sinal, LACUNA, "=", a], certo, [0, 1, a, -a],
                         {trocado: "neutro_trocado"}, **kw)


class Simetrico(Completar):
    """a + ▢ = 0  (answer −a)."""
    ERROS = {"simetrico_inverso": "confundiu o simétrico (−a) com o inverso (1/a)"}
    regra = "a + (−a) = 0"

    def __init__(self, a=5, **kw):
        a = _num(a)
        opcoes = [-a, a, 0] + ([1 / a] if a else [])
        super().__init__([a, "+", LACUNA, "=", 0], -a, opcoes,
                         {1 / a: "simetrico_inverso"} if a else {}, **kw)


class Inverso(Completar):
    """a · ▢ = 1  (answer 1/a). For a = 0 the answer is the 'não existe' tile."""
    ERROS = {
        "simetrico_inverso": "confundiu o inverso (1/a) com o simétrico (−a)",
        "dividir_por_zero": "tentou dar um inverso ao zero",
    }
    regra = "a · (1/a) = 1"

    def __init__(self, a=5, **kw):
        a = _num(a)
        if a == 0:
            opcoes = [0, 1, -1, NAO_EXISTE]
            erros = {0: "dividir_por_zero", 1: "dividir_por_zero", -1: "dividir_por_zero"}
            super().__init__([0, "·", LACUNA, "=", 1], NAO_EXISTE, opcoes, erros, **kw)
            self.regra = "0 · x = 0"
        else:
            super().__init__([a, "·", LACUNA, "=", 1], 1 / a, [1 / a, -a, a, NAO_EXISTE],
                             {-a: "simetrico_inverso"}, **kw)


class Comutativa(Completar):
    """a + b = b + ▢  (answer a). op="·" for multiplication."""
    ERROS = {"comutatividade": "pôs o mesmo número dos dois lados (não trocou a ordem)"}

    def __init__(self, a=3, b=4, op: str = "+", **kw):
        soma = op == "+"
        sinal = "+" if soma else "·"
        self.regra = f"a {sinal} b = b {sinal} a"
        total = _num(a) + _num(b) if soma else _num(a) * _num(b)
        super().__init__([a, sinal, b, "=", b, sinal, LACUNA], a, [a, b, total, 0],
                         {b: "comutatividade"}, **kw)


class Associativa(Completar):
    """(a + b) + c = a + (b + ▢)  (answer c)."""
    ERROS = {"associatividade": "trocou os números ao mudar os parênteses de lugar"}
    regra = "(a + b) + c = a + (b + c)"

    def __init__(self, a=2, b=3, c=4, **kw):
        super().__init__(["(", a, "+", b, ")", "+", c, "=", a, "+", "(", b, "+", LACUNA, ")"],
                         c, [c, a, b, _num(a) + _num(b)],
                         {a: "associatividade", b: "associatividade"}, **kw)


class Distributiva(Completar):
    """a · (b + c) = a · b + ▢  (answer a·c)."""
    ERROS = {"distributividade": "esqueceu de multiplicar o segundo termo (não distribuiu)"}
    regra = "a · (b + c) = a · b + a · c"

    def __init__(self, a=2, b=3, c=4, **kw):
        a, b, c = _num(a), _num(b), _num(c)
        super().__init__([a, "·", "(", b, "+", c, ")", "=", a, "·", b, "+", LACUNA],
                         a * c, [a * c, c, a + c, a * b],
                         {c: "distributividade"}, **kw)
