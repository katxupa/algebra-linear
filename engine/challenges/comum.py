"""Building blocks shared by the matrix challenges (nocoes, perguntas, preencher, escalonar...).

    Grade          a matrix on the screen: cells to tap, row / column numbers, bands, the diagonal
    mini_matriz    a small matrix drawn inside a tile
    texto_partes   one line of coloured text pieces, with subscripts / superscripts
    Peca           an answer tile;  desenhar_peca draws its box
    ComMatriz      challenge with a matrix in the middle and (optionally) answer tiles below
    Escolha        ... where one tap on a tile is the answer
    EscolherMatriz challenge where the answer is one of several matrices

Colour code: ROW index = blue (LIN), COLUMN index = yellow (COL), marks = purple (MARCA).
"""
from __future__ import annotations

import random

import pygame

from .. import escalonamento as E
from .. import theme
from ..scene import draw
from ..textos import t
from .base import DesafioToque, SUCESSO, ERRO

LIN = theme.VEC2
COL = theme.VEC
MARCA = theme.RESULT


def fmt_num(v) -> str:
    """Numbers as the sebenta writes them: exact fractions, a real minus sign. Text stays as it is."""
    return v if isinstance(v, str) else E.fmt(E.frac(v))


def retangular(m) -> list[list]:
    m = [list(r) for r in m]
    if not m or not m[0] or any(len(r) != len(m[0]) for r in m):
        raise ValueError("a matriz precisa de linhas com o mesmo número de entradas")
    return m


def quadrada(m) -> list[list]:
    m = retangular(m)
    if len(m) != len(m[0]):
        raise ValueError("este desafio precisa de uma matriz quadrada")
    return m


def primeiras(opcoes: list, n: int = 4) -> list:
    """The first `n` different options (put the right answer first in the list given)."""
    unicas = []
    for o in opcoes:
        if o not in unicas:
            unicas.append(o)
    return unicas[:n]


def texto_partes(surf, partes, cx, cy, size, max_w) -> None:
    """Coloured pieces of text on one centred line. A piece is (text, colour), or (text, colour, "sub")
    for a subscript (True also works), or (text, colour, "sup") for a superscript. Arrows are drawn.
    Shrinks to fit `max_w`."""
    def modo(p):
        return None if len(p) < 3 or not p[2] else "sup" if p[2] == "sup" else "sub"

    def tam(p, sz):
        return int(sz * 0.62) if modo(p) else sz

    def largura(sz):
        return sum(draw.text_width(p[0], tam(p, sz)) for p in partes)

    while size > 18 and largura(size) > max_w:
        size -= 2
    x = cx - largura(size) / 2
    for p in partes:
        dy = {"sub": size * 0.3, "sup": -size * 0.3, None: 0}[modo(p)]
        draw.text_setas(surf, p[0], (x, cy + dy), tam(p, size), p[1], "midleft")
        x += draw.text_width(p[0], tam(p, size))


def _parenteses(surf, cor, x0, y0, w, h, tick, largura) -> None:
    for lado, x in ((-1, x0), (1, x0 + w)):
        pygame.draw.lines(surf, cor, False, [(x - lado * tick, y0), (x, y0), (x, y0 + h), (x - lado * tick, y0 + h)],
                          largura)


def mini_matriz(surf, m, centro, size, cor=theme.TEXT) -> None:
    """A small matrix with brackets, centred (no interaction)."""
    txt = [[fmt_num(v) for v in r] for r in m]
    col_w = max(draw.text_width(s, size) for r in txt for s in r) + size * 0.5
    row_h = size * 0.95
    w, h = col_w * len(m[0]), row_h * len(m)
    x0, y0 = centro[0] - w / 2, centro[1] - h / 2
    for r, row in enumerate(txt):
        for c, s in enumerate(row):
            draw.text(surf, s, (x0 + col_w * (c + 0.5), y0 + row_h * (r + 0.5)), size, cor)
    _parenteses(surf, cor, x0 - 4, y0, w + 8, h, size * 0.25, 2)


class Grade:
    """A matrix on the screen: square cells you can tap, plus numbered row and column labels."""

    def __init__(self, m):
        self.m = m
        self.rows, self.cols = len(m), len(m[0])
        self.cell, self.x0, self.y0 = 40, 0.0, 0.0
        self.max_cell = 92
        self.barra = None            # column index: a dashed bar before it, as in [A | B]

    def layout(self, area: pygame.Rect, folga: bool = True) -> None:
        """Fit inside `area`. `folga` keeps room for the row / column numbers around the matrix."""
        f = 1.0 if folga else 0.0
        self.cell = int(max(22, min(self.max_cell, area.w / (self.cols + 0.5 + 1.4 * f),
                                    area.h / (self.rows + 0.2 + 1.1 * f))))
        self.x0 = area.centerx - self.cols * self.cell / 2 + self.cell * 0.4 * f
        self.y0 = area.centery - self.rows * self.cell / 2 + self.cell * 0.4 * f

    def rect(self, r, c) -> pygame.Rect:
        return pygame.Rect(int(self.x0 + c * self.cell), int(self.y0 + r * self.cell), self.cell, self.cell)

    def rot_linha(self, r):
        return (self.x0 - self.cell * 0.62, self.y0 + (r + 0.5) * self.cell)

    def rot_coluna(self, c):
        return (self.x0 + (c + 0.5) * self.cell, self.y0 - self.cell * 0.62)

    def celula(self, x, y):
        c, r = int((x - self.x0) // self.cell), int((y - self.y0) // self.cell)
        return (r, c) if 0 <= r < self.rows and 0 <= c < self.cols else None

    def rotulo(self, x, y):
        """("l", row) or ("c", column) if (x, y) is on a row / column number, else None."""
        raio2 = (self.cell * 0.5) ** 2
        for tipo, n, (cx, cy) in ([("l", r, self.rot_linha(r)) for r in range(self.rows)] +
                                  [("c", c, self.rot_coluna(c)) for c in range(self.cols)]):
            if (x - cx) ** 2 + (y - cy) ** 2 <= raio2:
                return (tipo, n)
        return None

    def faixa(self, surf, cor, linha=None, coluna=None) -> None:
        """A dim band over a whole row or column."""
        if linha is not None:
            rect = pygame.Rect(int(self.x0), int(self.y0 + linha * self.cell + 4), self.cols * self.cell, self.cell - 8)
        else:
            rect = pygame.Rect(int(self.x0 + coluna * self.cell + 4), int(self.y0), self.cell - 8, self.rows * self.cell)
        pygame.draw.rect(surf, theme.escurecer(cor, 0.3), rect, border_radius=10)

    def diagonal(self, surf, cor) -> None:
        a, b = self.rect(0, 0).center, self.rect(self.rows - 1, self.cols - 1).center
        draw.dashed_line(surf, cor, a, b, 3, 10)

    def desenhar(self, surf, estilo=None, cor=theme.TEXT) -> None:
        """`estilo(r, c)` may return {"txt", "cor", "fundo", "borda"} to change one cell."""
        size = int(self.cell * 0.5)
        for r in range(self.rows):
            for c in range(self.cols):
                e = (estilo(r, c) if estilo else None) or {}
                rect = self.rect(r, c).inflate(-8, -8)
                if e.get("fundo"):
                    pygame.draw.rect(surf, e["fundo"], rect, border_radius=10)
                if e.get("borda"):
                    pygame.draw.rect(surf, e["borda"], rect, 3, border_radius=10)
                txt = e.get("txt", fmt_num(self.m[r][c]))
                sz = size
                while sz > 12 and draw.text_width(txt, sz) > self.cell - 10:
                    sz -= 2
                draw.text(surf, txt, rect.center, sz, e.get("cor", cor))
        h = self.rows * self.cell
        _parenteses(surf, cor, self.x0 - 5, self.y0, self.cols * self.cell + 10, h, self.cell * 0.2, 3)
        if self.barra is not None:
            bx = self.x0 + self.barra * self.cell
            draw.dashed_line(surf, theme.TEXT_DIM, (bx, self.y0 + 4), (bx, self.y0 + h - 4), 2, 6)

    def rotulos(self, surf, fora_l=(), fora_c=(), pisca_l=(), pisca_c=(), alpha=1.0) -> None:
        """Row numbers (blue) on the left, column numbers (yellow) on top. Numbers in `fora_*` are
        dimmed (struck out); numbers in `pisca_*` get a blinking ring (help)."""
        raio, size = self.cell * 0.3, int(self.cell * 0.36)
        for n, centro, cor, fora, pisca in (
                [(r, self.rot_linha(r), LIN, fora_l, pisca_l) for r in range(self.rows)] +
                [(c, self.rot_coluna(c), COL, fora_c, pisca_c) for c in range(self.cols)]):
            c2 = theme.escurecer(cor, 0.35) if n in fora else cor
            draw.circle(surf, theme.PANEL, centro, raio)
            draw.circle(surf, c2, centro, raio, 2)
            draw.text(surf, str(n + 1), centro, size, c2)
            if n in pisca:
                draw.circle(surf, theme.piscar(theme.TEXT, alpha, 0.3), centro, raio + 6, 2)


class Peca:
    """An answer tile: a value and where it is on the screen."""

    def __init__(self, valor):
        self.valor = valor
        self.rect = pygame.Rect(0, 0, 0, 0)


def desenhar_peca(surf, rect, escolhida: bool, resolvido: bool, raio: int = 16) -> None:
    """The box of a tile: blue border; the chosen one is red (wrong) or green (right)."""
    borda = theme.GRID_MAJOR if not escolhida else theme.OK if resolvido else theme.BAD
    pygame.draw.rect(surf, theme.PANEL_HI if escolhida else theme.PANEL, rect, border_radius=raio)
    pygame.draw.rect(surf, borda, rect, 3, border_radius=raio)


def baralhar(pecas: list) -> list:
    """A new order every time the challenge starts: no learning "it is the first one"."""
    random.shuffle(pecas)
    return pecas


class ComMatriz(DesafioToque):
    """A matrix in the middle of a plain black screen, optional answer tiles below.
    The help (after `dica_apos` failures) is drawn by the subclass in `desenhar`, over the matrix."""

    plano = False
    baralhar = True                  # False: the tiles keep the order of `opcoes`
    barra = None                     # column index of the bar of an augmented matrix [A | B]

    def __init__(self, matriz=None, **kw):
        super().__init__(**kw)
        self.m = retangular(matriz) if matriz is not None else None
        self.opcoes: list = []

    def iniciar(self):
        self.g = Grade(self.m) if self.m else None
        if self.g:
            self.g.barra = self.barra
        self.tiles = [Peca(v) for v in self.opcoes]
        if self.baralhar:
            baralhar(self.tiles)
        self.sel = None
        self.ajuda = False

    def desenhar_dica(self, surf, ctx):
        self.ajuda = True

    # ---- layout ---------------------------------------------------------------------
    def layout(self, ctx):
        base = ctx.height * 0.6 if self.tiles else ctx.height - 90
        self._layout_matriz(ctx, pygame.Rect(16, 124, ctx.width - 32, int(base - 124)))
        if not self.tiles:
            return
        h = max(52, min(84, int(ctx.width / 7)))
        self.tile_size = int(h * 0.42)
        w = max(h, max(sum(draw.text_width(p[0], self.tile_size) for p in self._tile(tl.valor))
                       for tl in self.tiles) + int(h * 0.5))
        gap = h // 4
        por_linha = max(1, min(len(self.tiles), (ctx.width - 30 + gap) // (w + gap)))
        for k, tl in enumerate(self.tiles):
            r, c = divmod(k, por_linha)
            n = min(por_linha, len(self.tiles) - r * por_linha)
            x0 = (ctx.width - (n * w + (n - 1) * gap)) / 2
            tl.rect = pygame.Rect(int(x0 + c * (w + gap)), int(ctx.height * 0.66 + r * (h + gap)), w, h)

    def _layout_matriz(self, ctx, area: pygame.Rect) -> None:
        if self.g:
            self.g.layout(area)

    # ---- drawing --------------------------------------------------------------------
    def _tile(self, valor) -> list:
        """Coloured text pieces shown on a tile (a number, or a text key from textos.py)."""
        return [(t(valor) if isinstance(valor, str) else fmt_num(valor), theme.TEXT)]

    def _desenhar_tiles(self, surf, ctx):
        for tl in self.tiles:
            desenhar_peca(surf, tl.rect, self.sel is not None and tl.valor == self.sel, ctx.solved)
            texto_partes(surf, self._tile(tl.valor), tl.rect.centerx, tl.rect.centery, self.tile_size, tl.rect.w)

    def _titulo(self, surf, ctx, partes, size=46):
        texto_partes(surf, partes, ctx.width / 2, ctx.hud_y, size, ctx.width - 170)


class Escolha(ComMatriz):
    """One tap on a tile is the answer. Subclasses set `opcoes`, `resposta` and `erros`
    (wrong value -> mistake key). The help shows the row / column numbers unless `_ajuda` changes it."""

    resposta = None
    erros: dict = {}

    def estado(self):
        return repr(self.sel)

    def avaliar(self):
        if self.sel == self.resposta:
            return SUCESSO
        return self.erros.get(self.sel, ERRO)

    def tocar(self, ctx, sx, sy):
        for tl in self.tiles:
            if tl.rect.collidepoint(sx, sy):
                self.sel = tl.valor
                return True
        return False

    def desenhar(self, surf, ctx):
        self._desenhar_matriz(surf, ctx)
        if self.ajuda or ctx.solved:
            self._ajuda(surf, ctx)
        self._desenhar_tiles(surf, ctx)

    def _desenhar_matriz(self, surf, ctx):
        if self.g:
            self.g.desenhar(surf)

    def _ajuda(self, surf, ctx):
        if self.g:
            self.g.rotulos(surf)


class EscolherMatriz(DesafioToque):
    """Tap the right matrix among several. Subclasses fill `lista` = [(matrix, mistake key or None)]
    and `certa` (index of the right one). `_topo` leaves room above the tiles for something else."""

    plano = False
    lista: list = []
    certa = 0

    def iniciar(self):
        self.tiles = baralhar([Peca(k) for k in range(len(self.lista))])
        self.sel = None

    def estado(self):
        return self.sel

    def avaliar(self):
        if self.sel is None:
            return ERRO
        return SUCESSO if self.sel == self.certa else (self.lista[self.sel][1] or ERRO)

    def tocar(self, ctx, sx, sy):
        for tl in self.tiles:
            if tl.rect.collidepoint(sx, sy):
                self.sel = tl.valor
                return True
        return False

    def _topo(self, ctx) -> int:
        return 135

    def layout(self, ctx):
        n = len(self.tiles)
        por_linha = n if ctx.width >= n * 190 else 2
        linhas = -(-n // por_linha)
        topo, fundo = self._topo(ctx), ctx.height - 30
        gap = 18
        lado = int(min(230, (ctx.width - 30 - (por_linha - 1) * gap) / por_linha,
                       (fundo - topo - (linhas - 1) * gap) / linhas))
        y0 = topo + (fundo - topo - (linhas * lado + (linhas - 1) * gap)) / 2
        for k, tl in enumerate(self.tiles):
            r, c = divmod(k, por_linha)
            cols = min(por_linha, n - r * por_linha)
            x0 = (ctx.width - (cols * lado + (cols - 1) * gap)) / 2
            tl.rect = pygame.Rect(int(x0 + c * (lado + gap)), int(y0 + r * (lado + gap)), lado, lado)

    def desenhar(self, surf, ctx):
        for tl in self.tiles:
            desenhar_peca(surf, tl.rect, tl.valor == self.sel, ctx.solved, 18)
            mini_matriz(surf, self.lista[tl.valor][0], tl.rect.center, int(tl.rect.w * 0.2))
