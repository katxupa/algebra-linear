"""Matrix notions (sebenta, 2.1 and 2.2): entries a_ij, type m×n, kinds of matrices, main diagonal,
trace, triangular / diagonal / scalar / identity, submatrices.

    Entrada(A, 2, 3)                      tap the entry a23
    Tipo(A)                               pick the type: 3 × 2
    Forma(A)                              row / column / square / rectangular matrix
    Diagonal(A)                           mark the main diagonal
    Traco(A)                              tr(A) = ?
    Zerar(A, "triangular superior")       tap the entries that have to be 0
    Qual("identidade")                    which of these matrices is the identity?
    Submatriz(A, ficar=([1, 3], [2, 3]))  A[1,3 | 2,3]: strike out the other rows and columns
    Submatriz(A, tirar=([2], [1]))        A(2 | 1)

Colour code used in every challenge here: ROW index = blue, COLUMN index = yellow.
"""
from __future__ import annotations

import random

import pygame

from .. import theme
from ..linalg import fmt_num
from ..scene import draw
from ..textos import t
from .base import Desafio, SUCESSO, ERRO

LIN = theme.VEC2
COL = theme.VEC
MARCA = theme.RESULT

#: name used in lesson.py -> text key
NOMES = {
    "triangular superior": "tri_sup", "triangular inferior": "tri_inf", "diagonal": "m_diagonal",
    "escalar": "m_escalar", "identidade": "m_identidade", "nula": "m_nula",
}


def _retangular(m) -> list[list]:
    m = [list(r) for r in m]
    if not m or not m[0] or any(len(r) != len(m[0]) for r in m):
        raise ValueError("a matriz precisa de linhas com o mesmo número de entradas")
    return m


def _quadrada(m) -> list[list]:
    m = _retangular(m)
    if len(m) != len(m[0]):
        raise ValueError("este desafio precisa de uma matriz quadrada")
    return m


def e_do_tipo(nome: str, m) -> bool:
    """The definitions of 2.2 (square matrices)."""
    n = len(m)
    sup = all(m[i][j] == 0 for i in range(n) for j in range(n) if i > j)
    inf = all(m[i][j] == 0 for i in range(n) for j in range(n) if i < j)
    escalar = sup and inf and len({m[i][i] for i in range(n)}) == 1
    return {
        "triangular superior": sup, "triangular inferior": inf, "diagonal": sup and inf,
        "escalar": escalar, "identidade": escalar and m[0][0] == 1,
        "nula": all(v == 0 for r in m for v in r),
    }[nome]


def _partes(surf, partes, cx, cy, size, max_w) -> None:
    """Coloured pieces of text on one centred line. A piece is (text, colour) or (text, colour, True)
    for a subscript. Shrinks to fit `max_w`."""
    def largura(sz):
        return sum(draw.text_width(p[0], int(sz * 0.62) if len(p) > 2 else sz) for p in partes)

    while size > 18 and largura(size) > max_w:
        size -= 2
    x = cx - largura(size) / 2
    for p in partes:
        sub = len(p) > 2
        sz = int(size * 0.62) if sub else size
        draw.text(surf, p[0], (x, cy + (size * 0.3 if sub else 0)), sz, p[1], "midleft")
        x += draw.text_width(p[0], sz)


class Grade:
    """A matrix on the screen: square cells you can tap, plus numbered row and column labels."""

    def __init__(self, m):
        self.m = m
        self.rows, self.cols = len(m), len(m[0])
        self.cell, self.x0, self.y0 = 40, 0.0, 0.0

    def layout(self, area: pygame.Rect) -> None:
        self.cell = int(max(24, min(92, area.w / (self.cols + 1.9), area.h / (self.rows + 1.3))))
        self.x0 = area.centerx - self.cols * self.cell / 2 + self.cell * 0.4
        self.y0 = area.centery - self.rows * self.cell / 2 + self.cell * 0.4

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
        raio = self.cell * 0.5
        for r in range(self.rows):
            cx, cy = self.rot_linha(r)
            if (x - cx) ** 2 + (y - cy) ** 2 <= raio * raio:
                return ("l", r)
        for c in range(self.cols):
            cx, cy = self.rot_coluna(c)
            if (x - cx) ** 2 + (y - cy) ** 2 <= raio * raio:
                return ("c", c)
        return None

    def faixa(self, surf, cor, linha=None, coluna=None) -> None:
        """A dim band over a whole row or column."""
        cor = tuple(int(v * 0.3) for v in cor)
        if linha is not None:
            rect = pygame.Rect(int(self.x0), int(self.y0 + linha * self.cell + 4), self.cols * self.cell, self.cell - 8)
        else:
            rect = pygame.Rect(int(self.x0 + coluna * self.cell + 4), int(self.y0), self.cell - 8, self.rows * self.cell)
        pygame.draw.rect(surf, cor, rect, border_radius=10)

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
        yt, yb = self.y0, self.y0 + self.rows * self.cell
        tick = self.cell * 0.2
        for lado, x in ((-1, self.x0 - 5), (1, self.x0 + self.cols * self.cell + 5)):
            pygame.draw.lines(surf, cor, False, [(x - lado * tick, yt), (x, yt), (x, yb), (x - lado * tick, yb)], 3)

    def rotulos(self, surf, fora_l=(), fora_c=(), pisca_l=(), pisca_c=(), alpha=1.0) -> None:
        """Row numbers (blue) on the left, column numbers (yellow) on top."""
        raio, size = self.cell * 0.3, int(self.cell * 0.36)
        for n, centro, cor, fora, pisca in (
                [(r, self.rot_linha(r), LIN, fora_l, pisca_l) for r in range(self.rows)] +
                [(c, self.rot_coluna(c), COL, fora_c, pisca_c) for c in range(self.cols)]):
            apagado = n in fora
            c2 = tuple(int(v * 0.35) for v in cor) if apagado else cor
            draw.circle(surf, theme.PANEL, centro, raio)
            draw.circle(surf, c2, centro, raio, 2)
            draw.text(surf, str(n + 1), centro, size, c2)
            if n in pisca:
                draw.circle(surf, tuple(int(v * (0.3 + 0.7 * alpha)) for v in theme.TEXT), centro, raio + 6, 2)


class Tile:
    def __init__(self, valor):
        self.valor = valor
        self.rect = pygame.Rect(0, 0, 0, 0)


class _ComMatriz(Desafio):
    """Common ground: a matrix in the middle of a plain black screen, optional answer tiles below."""

    plano = False
    baralhar = True

    def __init__(self, matriz, **kw):
        super().__init__(**kw)
        self.m = _retangular(matriz)
        self.opcoes: list = []

    def iniciar(self):
        self.g = Grade(self.m)
        self.tiles = [Tile(v) for v in self.opcoes]
        if self.baralhar:
            random.shuffle(self.tiles)   # a new order every time: no learning "it is the first one"
        self.sel = None
        self.pressed = False
        self.ajuda = False

    def desenhar_dica(self, surf, ctx):
        self.ajuda = True            # the help itself is drawn in `desenhar`, over the matrix

    # ---- layout ---------------------------------------------------------------------
    def layout(self, ctx):
        base = ctx.height * 0.6 if self.tiles else ctx.height - 90
        self.g.layout(pygame.Rect(16, 124, ctx.width - 32, int(base - 124)))
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

    def _tile(self, valor) -> list:
        """Coloured text pieces shown on a tile."""
        return [(str(valor), theme.TEXT)]

    def _desenhar_tiles(self, surf, ctx):
        for tl in self.tiles:
            escolhido = self.sel is not None and tl.valor == self.sel
            borda = theme.GRID_MAJOR if not escolhido else theme.OK if ctx.solved else theme.BAD
            pygame.draw.rect(surf, theme.PANEL_HI if escolhido else theme.PANEL, tl.rect, border_radius=16)
            pygame.draw.rect(surf, borda, tl.rect, 3, border_radius=16)
            _partes(surf, self._tile(tl.valor), tl.rect.centerx, tl.rect.centery, self.tile_size, tl.rect.w)

    def _titulo(self, surf, ctx, partes, size=46):
        _partes(surf, partes, ctx.width / 2, ctx.hud_y, size, ctx.width - 170)


class _Escolha(_ComMatriz):
    """One tap on a tile is an attempt. Subclasses set `opcoes`, `resposta` and `erros`."""

    resposta = None
    erros: dict = {}

    def estado(self):
        return repr(self.sel)

    def avaliar(self):
        if self.sel == self.resposta:
            return SUCESSO
        return self.erros.get(self.sel, ERRO)

    def press(self, ctx, sx, sy):
        for tl in self.tiles:
            if tl.rect.collidepoint(sx, sy):
                self.sel, self.pressed = tl.valor, True
                return True
        return False

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        was, self.pressed = self.pressed, False
        return was

    def desenhar(self, surf, ctx):
        self.g.desenhar(surf)
        if self.ajuda or ctx.solved:
            self._ajuda(surf, ctx)
        self._desenhar_tiles(surf, ctx)

    def _ajuda(self, surf, ctx):
        self.g.rotulos(surf)


def _quatro(opcoes: list) -> list:
    """The first four different options (the right answer comes first in the list given)."""
    unicas = []
    for o in opcoes:
        if o not in unicas:
            unicas.append(o)
    return unicas[:4]


# ---- 2.1: entries, type, kinds ---------------------------------------------------------------

class Entrada(_ComMatriz):
    """Tap the entry a_ij (row i, column j)."""

    ERROS = {
        "trocou_ij": "trocou a linha com a coluna (tocou em a_ji em vez de a_ij)",
        "so_linha": "acertou na linha, errou na coluna",
        "so_coluna": "acertou na coluna, errou na linha",
    }

    def __init__(self, matriz, i, j, **kw):
        super().__init__(matriz, **kw)
        if not (1 <= i <= len(self.m) and 1 <= j <= len(self.m[0])):
            raise ValueError(f"a entrada ({i}, {j}) não existe nesta matriz")
        self.i, self.j = i, j
        self.alvo = (i - 1, j - 1)

    def estado(self):
        return self.sel

    def avaliar(self):
        if self.sel == self.alvo:
            return SUCESSO
        if self.sel is None:
            return ERRO
        r, c = self.sel
        if (r, c) == (self.alvo[1], self.alvo[0]):
            return "trocou_ij"
        return "so_linha" if r == self.alvo[0] else "so_coluna" if c == self.alvo[1] else ERRO

    def press(self, ctx, sx, sy):
        cel = self.g.celula(sx, sy)
        if cel is None:
            return False
        self.sel, self.pressed = cel, True
        return True

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        was, self.pressed = self.pressed, False
        return was

    def desenhar(self, surf, ctx):
        if self.ajuda and not ctx.solved:            # help: the row (blue) and the column (yellow)
            self.g.faixa(surf, LIN, linha=self.alvo[0])
            self.g.faixa(surf, COL, coluna=self.alvo[1])
        cor = theme.OK if ctx.solved else theme.BAD
        self.g.desenhar(surf, lambda r, c: {"borda": cor, "fundo": theme.PANEL_HI} if (r, c) == self.sel else None)
        if self.ajuda or ctx.solved:
            self.g.rotulos(surf)

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("a", theme.TEXT), (str(self.i), LIN, True), (str(self.j), COL, True)], 60)

    def descricao(self):
        return f"tocar na entrada a{self.i}{self.j}"


class Tipo(_Escolha):
    """Pick the type m × n of the matrix."""

    ERROS = {"trocou_mn": "trocou linhas com colunas (disse n × m em vez de m × n)"}

    def __init__(self, matriz, **kw):
        super().__init__(matriz, **kw)
        m, n = len(self.m), len(self.m[0])
        self.resposta = (m, n)
        self.erros = {(n, m): "trocou_mn"} if m != n else {}
        cand = [(m, n), (n, m), (m + 1, n), (m, n + 1), (m + 1, n + 1), (max(1, m - 1), n)]
        self.opcoes = _quatro(cand)

    def _tile(self, v):
        return [(str(v[0]), LIN), (" × ", theme.TEXT), (str(v[1]), COL)]

    def desenhar_alvo(self, surf, ctx):
        m, n = self.resposta if ctx.solved else ("?", "?")
        self._titulo(surf, ctx, [(str(m), LIN), (" × ", theme.TEXT), (str(n), COL)], 56)

    def descricao(self):
        return f"tipo da matriz: {self.resposta[0]} × {self.resposta[1]}"


class Forma(_Escolha):
    """Row matrix, column matrix, square or rectangular."""

    ERROS = {"linha_coluna": "confundiu matriz linha com matriz coluna"}
    baralhar = False                    # the four names always in the same place

    def __init__(self, matriz, **kw):
        super().__init__(matriz, **kw)
        m, n = len(self.m), len(self.m[0])
        if m == n == 1:
            raise ValueError("uma matriz 1 × 1 é linha, coluna e quadrada: não serve para este desafio")
        self.resposta = "m_linha" if m == 1 else "m_coluna" if n == 1 else "m_quadrada" if m == n else "m_retangular"
        self.opcoes = ["m_linha", "m_coluna", "m_quadrada"]
        if 1 not in (m, n):                 # a row matrix is rectangular too: do not offer both
            self.opcoes.append("m_retangular")
        troca = {"m_linha": "m_coluna", "m_coluna": "m_linha"}
        self.erros = {troca[self.resposta]: "linha_coluna"} if self.resposta in troca else {}

    def _tile(self, v):
        return [(t(v), theme.TEXT)]

    def desenhar_alvo(self, surf, ctx):
        fim = t(self.resposta) if ctx.solved else "?"
        self._titulo(surf, ctx, [(t("matriz") + " ", theme.TEXT), (fim, theme.OK if ctx.solved else COL)])

    def descricao(self):
        return f"matriz {t(self.resposta).lower()}"


# ---- 2.2: square matrices ----------------------------------------------------------------------

class Traco(_Escolha):
    """tr(A): the sum of the main diagonal."""

    ERROS = {
        "diagonal_errada": "usou a outra diagonal (a secundária)",
        "somou_tudo": "somou todas as entradas da matriz",
    }

    def __init__(self, matriz, **kw):
        super().__init__(_quadrada(matriz), **kw)
        n = len(self.m)
        self.resposta = sum(self.m[i][i] for i in range(n))
        outra = sum(self.m[i][n - 1 - i] for i in range(n))
        tudo = sum(v for r in self.m for v in r)
        self.erros = {v: k for v, k in ((tudo, "somou_tudo"), (outra, "diagonal_errada")) if v != self.resposta}
        self.opcoes = _quatro([self.resposta, outra, tudo, self.resposta + 1, self.resposta - 1, self.resposta + 2])

    def _tile(self, v):
        return [(fmt_num(v), theme.TEXT)]

    def _ajuda(self, surf, ctx):
        self.g.diagonal(surf, tuple(int(v * (0.4 + 0.6 * ctx.hint_alpha)) for v in MARCA))

    def desenhar_alvo(self, surf, ctx):
        fim = fmt_num(self.resposta) if ctx.solved else "?"
        self._titulo(surf, ctx, [("tr(A) = ", theme.TEXT), (fim, theme.OK if ctx.solved else COL)])

    def descricao(self):
        return f"traço = {fmt_num(self.resposta)}"


class _Marcar(_ComMatriz):
    """Tap (or sweep over) cells to mark them, then confirm with the check button."""

    confirmar = True

    def iniciar(self):
        super().iniciar()
        self.marc: set = set()
        self.pintar = None

    def estado(self):
        return frozenset(self.marc)

    def _pinta(self, cel):
        (self.marc.add if self.pintar else self.marc.discard)(cel)

    def press(self, ctx, sx, sy):
        cel = self.g.celula(sx, sy)
        if cel is None:
            return False
        self.pintar = cel not in self.marc
        self._pinta(cel)
        return True

    def move(self, ctx, sx, sy):
        cel = self.g.celula(sx, sy)
        if self.pintar is not None and cel is not None:
            self._pinta(cel)

    def release(self, ctx):
        self.pintar = None
        return False

    def _diagonal_ajuda(self, surf, ctx):
        if self.ajuda and not ctx.solved:
            self.g.diagonal(surf, tuple(int(v * (0.4 + 0.6 * ctx.hint_alpha)) for v in theme.TEXT_DIM))


class Diagonal(_Marcar):
    """Mark the entries of the main diagonal."""

    ERROS = {
        "diagonal_errada": "marcou a outra diagonal (a secundária)",
        "incompleto": "o que marcou está certo, mas falta marcar entradas",
    }

    def __init__(self, matriz, **kw):
        super().__init__(_quadrada(matriz), **kw)
        n = len(self.m)
        self.certo = {(i, i) for i in range(n)}
        self.outra = {(i, n - 1 - i) for i in range(n)}

    def avaliar(self):
        if self.marc == self.certo:
            return SUCESSO
        if self.marc == self.outra:
            return "diagonal_errada"
        return "incompleto" if self.marc and self.marc < self.certo else ERRO

    def desenhar(self, surf, ctx):
        cor = theme.OK if ctx.solved else MARCA
        self.g.desenhar(surf, lambda r, c: {"borda": cor, "fundo": theme.PANEL_HI} if (r, c) in self.marc else None)
        self._diagonal_ajuda(surf, ctx)

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("diagonal_principal"), COL)], 40)

    def descricao(self):
        return "marcar a diagonal principal"


class Zerar(_Marcar):
    """Tap the entries that have to become 0 for the matrix to be triangular / diagonal."""

    ERROS = {
        "triangulo_trocado": "pôs os zeros do lado errado da diagonal (superior ↔ inferior)",
        "diagonal_apagada": "pôs zeros também na diagonal principal",
        "incompleto": "os zeros estão no sítio certo, mas ainda faltam",
    }

    def __init__(self, matriz, tipo="triangular superior", **kw):
        super().__init__(_quadrada(matriz), **kw)
        if tipo not in ("triangular superior", "triangular inferior", "diagonal"):
            raise ValueError("Zerar: tipo deve ser 'triangular superior', 'triangular inferior' ou 'diagonal'")
        self.tipo = tipo
        n = len(self.m)
        baixo = {(i, j) for i in range(n) for j in range(n) if i > j and self.m[i][j] != 0}
        cima = {(i, j) for i in range(n) for j in range(n) if i < j and self.m[i][j] != 0}
        self.certo = {"triangular superior": baixo, "triangular inferior": cima, "diagonal": baixo | cima}[tipo]
        self.oposto = {"triangular superior": cima, "triangular inferior": baixo, "diagonal": None}[tipo]
        if not self.certo:
            raise ValueError(f"Zerar: esta matriz já é {tipo}")

    def avaliar(self):
        if self.marc == self.certo:
            return SUCESSO
        if self.oposto and self.marc == self.oposto:
            return "triangulo_trocado"
        if any(r == c for r, c in self.marc):
            return "diagonal_apagada"
        return "incompleto" if self.marc and self.marc < self.certo else ERRO

    def desenhar(self, surf, ctx):
        cor = theme.OK if ctx.solved else MARCA
        self.g.desenhar(surf, lambda r, c: {"txt": "0", "cor": cor} if (r, c) in self.marc else None)
        self._diagonal_ajuda(surf, ctx)

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t(NOMES[self.tipo]), COL)], 40)

    def descricao(self):
        return f"pôr zeros até a matriz ser {self.tipo}"


_CHEIA = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
_I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
_ANTI_I = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
_SUP = [[2, 5, 1], [0, 3, 4], [0, 0, 6]]
_INF = [[2, 0, 0], [5, 3, 0], [1, 4, 6]]
_DIAG = [[2, 0, 0], [0, 5, 0], [0, 0, 7]]
_ESC = [[4, 0, 0], [0, 4, 0], [0, 0, 4]]
#: name -> [(matrix, mistake key or None)]; exactly one matrix of each list has that name
_OPCOES = {
    "triangular superior": [(_SUP, None), (_INF, "triangulo_trocado"), (_CHEIA, None),
                            ([[1, 2, 3], [4, 5, 0], [6, 0, 0]], "diagonal_errada")],
    "triangular inferior": [(_INF, None), (_SUP, "triangulo_trocado"), (_CHEIA, None),
                            ([[0, 0, 3], [0, 5, 6], [7, 8, 9]], "diagonal_errada")],
    "diagonal": [(_DIAG, None), (_SUP, None), ([[0, 0, 2], [0, 5, 0], [7, 0, 0]], "diagonal_errada"), (_CHEIA, None)],
    "escalar": [(_ESC, None), (_DIAG, None), ([[0, 0, 4], [0, 4, 0], [4, 0, 0]], "diagonal_errada"),
                ([[4, 4, 4], [4, 4, 4], [4, 4, 4]], None)],
    "identidade": [(_I3, None), (_ANTI_I, "diagonal_errada"), (_ESC, None), ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], None)],
    "nula": [([[0, 0, 0], [0, 0, 0], [0, 0, 0]], None), (_I3, None), (_ANTI_I, None),
             ([[1, 1, 1], [1, 1, 1], [1, 1, 1]], None)],
}


class Qual(Desafio):
    """Which of these matrices is ...? Tap it. The engine brings its own matrices for each name;
    `opcoes=[m1, m2, ...]` replaces them (exactly one must have that name)."""

    ERROS = {
        "triangulo_trocado": "escolheu a triangular do outro lado (superior ↔ inferior)",
        "diagonal_errada": "escolheu a matriz arrumada pela diagonal secundária",
    }
    plano = False

    def __init__(self, nome, opcoes=None, **kw):
        super().__init__(**kw)
        if nome not in NOMES:
            raise ValueError(f"Qual: nome desconhecido {nome!r}; usar um de {sorted(NOMES)}")
        self.nome = nome
        lista = [(_quadrada(m), None) for m in opcoes] if opcoes else [(m, k) for m, k in _OPCOES[nome]]
        if sum(e_do_tipo(nome, m) for m, _ in lista) != 1:
            raise ValueError(f"Qual({nome!r}): exatamente uma das opções tem de ser {nome}")
        self.lista = lista

    def iniciar(self):
        self.tiles = [Tile(k) for k in range(len(self.lista))]
        random.shuffle(self.tiles)
        self.sel = None
        self.pressed = False

    def estado(self):
        return self.sel

    def avaliar(self):
        if self.sel is None:
            return ERRO
        m, chave = self.lista[self.sel]
        return SUCESSO if e_do_tipo(self.nome, m) else (chave or ERRO)

    def press(self, ctx, sx, sy):
        for tl in self.tiles:
            if tl.rect.collidepoint(sx, sy):
                self.sel, self.pressed = tl.valor, True
                return True
        return False

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        was, self.pressed = self.pressed, False
        return was

    def layout(self, ctx):
        n = len(self.tiles)
        por_linha = n if ctx.width >= n * 190 else 2
        linhas = -(-n // por_linha)
        topo, fundo = 135, ctx.height - 30
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
            escolhido = tl.valor == self.sel
            borda = theme.GRID_MAJOR if not escolhido else theme.OK if ctx.solved else theme.BAD
            pygame.draw.rect(surf, theme.PANEL_HI if escolhido else theme.PANEL, tl.rect, border_radius=18)
            pygame.draw.rect(surf, borda, tl.rect, 3, border_radius=18)
            draw.matrix(surf, self.lista[tl.valor][0], tl.rect.center, int(tl.rect.w * 0.2), theme.TEXT)

    def desenhar_alvo(self, surf, ctx):
        _partes(surf, [(t(NOMES[self.nome]), COL), (" ?", theme.TEXT)], ctx.width / 2, ctx.hud_y, 40, ctx.width - 170)

    def descricao(self):
        return f"qual é a matriz {self.nome}?"


# ---- submatrices -------------------------------------------------------------------------------

class Submatriz(_ComMatriz):
    """Strike out rows and columns (tap their numbers) until the submatrix is left.
    `ficar=(rows, cols)` is the notation A[rows | cols]; `tirar=(rows, cols)` is A(rows | cols)."""

    ERROS = {
        "parenteses_trocados": "fez o contrário: ficou com o que era para tirar (confundiu [ ] com ( ))",
        "so_linha": "as linhas estão certas, as colunas não",
        "so_coluna": "as colunas estão certas, as linhas não",
    }
    confirmar = True

    def __init__(self, matriz, ficar=None, tirar=None, **kw):
        super().__init__(matriz, **kw)
        if (ficar is None) == (tirar is None):
            raise ValueError("Submatriz: dar `ficar=(linhas, colunas)` ou `tirar=(linhas, colunas)`")
        self.ficar = ficar is not None
        ls, cs = ficar if self.ficar else tirar
        self.ls, self.cs = sorted(ls), sorted(cs)
        m, n = len(self.m), len(self.m[0])
        if any(not 1 <= i <= m for i in self.ls) or any(not 1 <= j <= n for j in self.cs):
            raise ValueError("Submatriz: linha ou coluna que não existe")
        dados_l, dados_c = {i - 1 for i in self.ls}, {j - 1 for j in self.cs}
        todas_l, todas_c = set(range(m)), set(range(n))
        # rows / columns that must be struck out
        self.fora_l = todas_l - dados_l if self.ficar else dados_l
        self.fora_c = todas_c - dados_c if self.ficar else dados_c
        self.contrario = (todas_l - self.fora_l, todas_c - self.fora_c)
        if self.fora_l == todas_l or self.fora_c == todas_c:
            raise ValueError("Submatriz: não sobra nenhuma entrada")

    def iniciar(self):
        super().iniciar()
        self.tl: set = set()
        self.tc: set = set()

    def estado(self):
        return (frozenset(self.tl), frozenset(self.tc))

    def avaliar(self):
        if (self.tl, self.tc) == (self.fora_l, self.fora_c):
            return SUCESSO
        if (self.tl, self.tc) == self.contrario:
            return "parenteses_trocados"
        return "so_linha" if self.tl == self.fora_l else "so_coluna" if self.tc == self.fora_c else ERRO

    def press(self, ctx, sx, sy):
        rot = self.g.rotulo(sx, sy)
        if rot is None:
            return False
        alvo = self.tl if rot[0] == "l" else self.tc
        alvo.symmetric_difference_update({rot[1]})
        return True

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        return False

    def desenhar(self, surf, ctx):
        def estilo(r, c):
            if r in self.tl or c in self.tc:
                return {"cor": theme.PANEL_HI}
            return {"cor": theme.OK} if ctx.solved else None

        self.g.desenhar(surf, estilo)
        for r in self.tl:                               # a line through what was struck out
            a, b = self.g.rect(r, 0), self.g.rect(r, self.g.cols - 1)
            draw.line(surf, theme.TEXT_DIM, (a.left + 4, a.centery), (b.right - 4, b.centery), 2)
        for c in self.tc:
            a, b = self.g.rect(0, c), self.g.rect(self.g.rows - 1, c)
            draw.line(surf, theme.TEXT_DIM, (a.centerx, a.top + 4), (b.centerx, b.bottom - 4), 2)
        pisca = self.ajuda and not ctx.solved
        self.g.rotulos(surf, self.tl, self.tc, self.fora_l - self.tl if pisca else (),
                       self.fora_c - self.tc if pisca else (), ctx.hint_alpha)

    def desenhar_alvo(self, surf, ctx):
        abre, fecha = ("[", "]") if self.ficar else ("(", ")")
        self._titulo(surf, ctx, [("A" + abre, theme.TEXT), (",".join(map(str, self.ls)), LIN), (" | ", theme.TEXT),
                                 (",".join(map(str, self.cs)), COL), (fecha, theme.TEXT)], 50)

    def descricao(self):
        abre, fecha = ("[", "]") if self.ficar else ("(", ")")
        return f"submatriz A{abre}{','.join(map(str, self.ls))} | {','.join(map(str, self.cs))}{fecha}"
