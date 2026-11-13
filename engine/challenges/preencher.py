"""Fill in the result of a matrix operation, entry by entry, with a small keypad (sebenta 2.3, 6.6).

    Transposta(A)          Soma(A, B)            VezesEscalar(3, A)
    Produto(A, B)          Potencia(A, 2)        Formula(3, 3, "i + j")
    Adjunta(A)             InversaAdjunta(A)

The check button marks the wrong entries in red, so the student can try entry by entry.
"""
from __future__ import annotations

from fractions import Fraction

import pygame

from .. import escalonamento as E
from .. import matrizes as M
from .. import theme
from ..scene import draw
from .base import Desafio, SUCESSO, ERRO
from .nocoes import Grade, LIN, COL, MARCA, _partes, fmt_num

MINUS = "−"
APAGAR = "←"
INCOMPLETO = {"incompleto": "o que escreveu está certo, mas ainda faltam entradas"}


def _ler(s: str):
    """Text typed in a cell -> Fraction, or None if it is not a number yet."""
    try:
        return Fraction(s.replace(MINUS, "-"))
    except (ValueError, ZeroDivisionError):
        return None


class Preencher(Desafio):
    """Generic: operand matrices on top, the result (with blanks) below, a keypad at the bottom.
    Subclasses give the operands, the right result, the title and the typical wrong results."""

    ERROS = INCOMPLETO
    confirmar = True
    painel = True
    plano = False
    painel_altura = 146
    simbolo = ""                 # drawn between the operands (e.g. "+")

    def __init__(self, operandos, resultado, titulo, enganos=None, **kw):
        super().__init__(**kw)
        self.operandos = [(nome, M.matriz(m)) for nome, m in operandos]
        self.resultado = M.matriz(resultado)
        self.titulo = titulo
        # a wrong result that equals the right one is not a mistake
        self.enganos = {k: M.matriz(m) for k, m in (enganos or {}).items()
                        if M.tipo(m) == M.tipo(self.resultado) and M.matriz(m) != self.resultado}
        self.fracoes = any(v.denominator != 1 for r in self.resultado for v in r)

    # ---- state ------------------------------------------------------------------------
    def iniciar(self):
        rows, cols = M.tipo(self.resultado)
        self.gs = [Grade(m) for _, m in self.operandos]
        self.g = Grade([[""] * cols for _ in range(rows)])
        self.txt: dict = {}
        self.sel = (0, 0)
        self.erradas: set = set()
        self.keys: list = []
        self.ajuda = False

    def celulas(self):
        rows, cols = M.tipo(self.resultado)
        return [(r, c) for r in range(rows) for c in range(cols)]

    def estado(self):
        return tuple(sorted(self.txt.items()))

    def avaliar(self):
        valores = {cel: _ler(self.txt.get(cel, "")) for cel in self.celulas()}
        escritas = {cel for cel in valores if self.txt.get(cel)}
        self.erradas = {cel for cel in escritas if valores[cel] != self.resultado[cel[0]][cel[1]]}
        if not self.erradas and len(escritas) == len(valores):
            return SUCESSO
        if len(escritas) == len(valores):
            for chave, m in self.enganos.items():
                if all(valores[(r, c)] == m[r][c] for r, c in valores):
                    return chave
        return "incompleto" if not self.erradas and escritas else ERRO

    def fontes(self, r, c) -> list:
        """Where entry (r, c) comes from, for the help: (operand, "cel" | "linha" | "coluna", index)."""
        return []

    # ---- input ------------------------------------------------------------------------
    def escrever(self, key: str) -> None:
        s = self.txt.get(self.sel, "")
        if key == APAGAR:
            s = s[:-1]
        elif key == MINUS:
            s = s[1:] if s.startswith(MINUS) else MINUS + s
        elif key == "/":
            if "/" not in s and s.strip(MINUS):
                s += "/"
        elif len(s) < 6:
            s += key
        self.txt[self.sel] = s
        if not s:
            del self.txt[self.sel]
        self.erradas.discard(self.sel)

    def seguinte(self, passo: int = 1) -> None:
        cels = self.celulas()
        self.sel = cels[(cels.index(self.sel) + passo) % len(cels)]

    def press(self, ctx, sx, sy):
        for rect, key in self.keys:
            if rect.collidepoint(sx, sy):
                self.escrever(key)
                return True
        cel = self.g.celula(sx, sy)
        if cel is not None:
            self.sel = cel
            return True
        return False

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        return False

    def tecla(self, ctx, ev):
        if ev.type != pygame.KEYDOWN:
            return
        if ev.key == pygame.K_BACKSPACE:
            self.escrever(APAGAR)
        elif ev.key in (pygame.K_TAB, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_RIGHT):
            self.seguinte()
        elif ev.key == pygame.K_LEFT:
            self.seguinte(-1)
        elif ev.key in (pygame.K_DOWN, pygame.K_UP):
            self.seguinte(len(self.resultado[0]) * (1 if ev.key == pygame.K_DOWN else -1))
        else:
            ch = getattr(ev, "unicode", "")
            if ch and ch in "0123456789":
                self.escrever(ch)
            elif ch == "-":
                self.escrever(MINUS)
            elif ch == "/" and self.fracoes:
                self.escrever("/")

    # ---- layout / drawing ---------------------------------------------------------------
    def layout(self, ctx):
        ph = self.altura_painel(ctx.width)
        top, bottom = 124, ctx.height - ph - 16
        area = pygame.Rect(16, top, ctx.width - 32, bottom - top)
        if self.gs:
            meio = top + int((bottom - top) * 0.42)
            cada = (ctx.width - 32) / len(self.gs)
            for k, g in enumerate(self.gs):
                g.max_cell = 60
                g.layout(pygame.Rect(int(16 + k * cada), top + 30, int(cada), meio - top - 34), folga=False)
            area = pygame.Rect(16, meio, ctx.width - 32, bottom - meio)
        self.g.max_cell = 84
        self.g.layout(area, folga=False)
        if self.g.x0 + self.g.cols * self.g.cell + 14 > ctx.width - 96:      # keep clear of the check button
            self.g.layout(pygame.Rect(area.x, area.y, area.w, area.h - 84), folga=False)
        linhas = [list("12345") + [MINUS], list("67890") + (["/"] if self.fracoes else []) + [APAGAR]]
        n = max(len(l) for l in linhas)
        gap = 8
        kw = min(88, (ctx.width - 20 - gap * (n - 1)) / n)
        self.keys = []
        for r, linha in enumerate(linhas):
            x0 = (ctx.width - (len(linha) * kw + (len(linha) - 1) * gap)) / 2
            for c, key in enumerate(linha):
                self.keys.append((pygame.Rect(int(x0 + c * (kw + gap)), int(ctx.height - ph + 12 + r * 64), int(kw), 54),
                                  key))

    def desenhar_dica(self, surf, ctx):
        self.ajuda = True

    def desenhar(self, surf, ctx):
        if self.ajuda and not ctx.solved:                   # help: where the selected entry comes from
            for k, tipo, idx in self.fontes(*self.sel):
                g = self.gs[k]
                if tipo == "linha":
                    g.faixa(surf, LIN, linha=idx)
                elif tipo == "coluna":
                    g.faixa(surf, COL, coluna=idx)
                else:
                    pygame.draw.rect(surf, tuple(int(v * 0.4) for v in MARCA), g.rect(*idx).inflate(-6, -6),
                                     border_radius=8)
        for k, ((nome, _), g) in enumerate(zip(self.operandos, self.gs)):
            g.desenhar(surf)
            draw.text(surf, nome, (g.x0 + g.cols * g.cell / 2, g.y0 - 18), 26, theme.TEXT_DIM)
            if k and self.simbolo:
                ant = self.gs[k - 1]
                mx = (ant.x0 + ant.cols * ant.cell + g.x0) / 2
                draw.text(surf, self.simbolo, (mx, g.y0 + g.rows * g.cell / 2), 40, theme.TEXT_DIM)

        def estilo(r, c):
            cel = (r, c)
            borda = (theme.OK if ctx.solved else theme.BAD if cel in self.erradas
                     else COL if cel == self.sel else theme.PANEL_HI)
            return {"txt": self.txt.get(cel, ""), "fundo": theme.PANEL, "borda": borda,
                    "cor": theme.OK if ctx.solved else theme.TEXT}

        self.g.desenhar(surf, estilo, cor=theme.OK if ctx.solved else COL)

    def desenhar_painel(self, surf, ctx):
        for rect, key in self.keys:
            pygame.draw.rect(surf, theme.BG, rect, border_radius=10)
            pygame.draw.rect(surf, theme.BAD if key == APAGAR else theme.VEC2, rect, 2, border_radius=10)
            draw.text_setas(surf, key, rect.center, 30, theme.TEXT)

    def desenhar_alvo(self, surf, ctx):
        _partes(surf, self.titulo, ctx.width / 2, ctx.hud_y, 46, ctx.width - 170)


# ---- 2.3: the algebra of matrices ----------------------------------------------------------------

class Transposta(Preencher):
    """Aᵗ: rows become columns."""
    ERROS = {"nao_transpos": "copiou a matriz sem trocar as linhas com as colunas", **INCOMPLETO}

    def __init__(self, a, **kw):
        a = M.matriz(a)
        super().__init__([("A", a)], M.transposta(a), [("A", theme.TEXT), ("t", COL, "sup")],
                         {"nao_transpos": a}, **kw)

    def fontes(self, r, c):
        return [(0, "cel", (c, r))]

    def descricao(self):
        return "transposta de A"


class Soma(Preencher):
    """A + B (or A − B with sinal="-"): entry by entry."""
    ERROS = {"sinal": "somou em vez de subtrair (ou o contrário)", **INCOMPLETO}

    def __init__(self, a, b, sinal: str = "+", **kw):
        a, b = M.matriz(a), M.matriz(b)
        s = -1 if sinal in ("-", MINUS) else 1
        self.simbolo = MINUS if s < 0 else "+"
        super().__init__([("A", a), ("B", b)], M.soma(a, b, s), [(f"A {self.simbolo} B", theme.TEXT)],
                         {"sinal": M.soma(a, b, -s)}, **kw)

    def fontes(self, r, c):
        return [(0, "cel", (r, c)), (1, "cel", (r, c))]

    def descricao(self):
        return f"A {self.simbolo} B"


class VezesEscalar(Preencher):
    """k · A: every entry times k."""

    def __init__(self, k, a, **kw):
        a = M.matriz(a)
        self.k = E.frac(k)
        super().__init__([("A", a)], M.escala(self.k, a), [(fmt_num(self.k), COL), (" · A", theme.TEXT)], **kw)

    def fontes(self, r, c):
        return [(0, "cel", (r, c))]

    def descricao(self):
        return f"{fmt_num(self.k)} · A"


class Produto(Preencher):
    """A · B: row of A times column of B."""
    ERROS = {
        "entrada_a_entrada": "multiplicou entrada por entrada, em vez de linha por coluna",
        "ordem_trocada": "calculou B · A em vez de A · B",
        **INCOMPLETO,
    }
    simbolo = "·"

    def __init__(self, a, b, **kw):
        a, b = M.matriz(a), M.matriz(b)
        enganos = {}
        if M.tipo(a) == M.tipo(b):
            enganos["entrada_a_entrada"] = [[x * y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]
        if len(b[0]) == len(a):
            enganos["ordem_trocada"] = M.produto(b, a)
        super().__init__([("A", a), ("B", b)], M.produto(a, b), [("A · B", theme.TEXT)], enganos, **kw)

    def fontes(self, r, c):
        return [(0, "linha", r), (1, "coluna", c)]

    def descricao(self):
        return "produto A · B"


class Potencia(Preencher):
    """Aⁿ = A · A · ... · A."""
    ERROS = {"entrada_a_entrada": "elevou cada entrada à potência, em vez de multiplicar as matrizes", **INCOMPLETO}
    simbolo = "·"

    def __init__(self, a, n: int = 2, **kw):
        a = M.matriz(a)
        self.n = n
        super().__init__([("A", a), ("A", a)], M.potencia(a, n), [("A", theme.TEXT), (str(n), COL, "sup")],
                         {"entrada_a_entrada": [[v ** n for v in r] for r in a]}, **kw)

    def fontes(self, r, c):
        return [(0, "linha", r), (1, "coluna", c)] if self.n == 2 else []

    def descricao(self):
        return f"potência A^{self.n}"


class Formula(Preencher):
    """A matrix given by a rule on the indices: Formula(3, 3, "i + j"), Formula(3, 3, "i ** (j - 1)")."""
    ERROS = {"trocou_ij": "trocou o i (linha) com o j (coluna) na fórmula", **INCOMPLETO}

    def __init__(self, m: int, n: int, regra: str, texto: str | None = None, **kw):
        def calc(i, j):
            return eval(regra, {"__builtins__": {}}, {"i": i, "j": j})   # the rule comes from lesson.py

        certo = [[calc(i, j) for j in range(1, n + 1)] for i in range(1, m + 1)]
        self.texto = texto or regra.replace("**", "^").replace("*", "·").replace("-", MINUS)
        enganos = {"trocou_ij": [[calc(j, i) for j in range(1, n + 1)] for i in range(1, m + 1)]} if m == n else {}
        super().__init__([], certo, [("a", theme.TEXT), ("i", LIN, "sub"), ("j", COL, "sub"),
                                     (" = " + self.texto, theme.TEXT)], enganos, **kw)

    def desenhar(self, surf, ctx):
        super().desenhar(surf, ctx)
        self.g.rotulos(surf)

    def layout(self, ctx):
        super().layout(ctx)
        ph = self.altura_painel(ctx.width)
        self.g.layout(pygame.Rect(16, 124, ctx.width - 32, ctx.height - ph - 16 - 124 - 70))

    def descricao(self):
        return f"matriz com a_ij = {self.texto}"


# ---- 6.6: adjoint and inverse ------------------------------------------------------------------

class Adjunta(Preencher):
    """adj(A): the transpose of the matrix of cofactors."""
    ERROS = {
        "nao_transpos": "escreveu a matriz dos cofatores sem a transpor",
        "sinal_cofator": "esqueceu os sinais (−1)^(i+j) dos cofatores",
        **INCOMPLETO,
    }

    def __init__(self, a, **kw):
        a = M.matriz(a)
        n = len(a)
        menores = [[M.det(M.menor(a, i, j)) if n > 1 else Fraction(1) for j in range(n)] for i in range(n)]
        super().__init__([("A", a)], M.adjunta(a), [("adj(A)", theme.TEXT)],
                         {"nao_transpos": M.cofatores(a), "sinal_cofator": M.transposta(menores)}, **kw)

    def fontes(self, r, c):
        return [(0, "linha", c), (0, "coluna", r)]      # entry (r, c) is the cofactor A_cr

    def descricao(self):
        return "adjunta de A"


class InversaAdjunta(Preencher):
    """A⁻¹ = adj(A) / |A|."""
    ERROS = {"faltou_dividir": "escreveu a adjunta e esqueceu de dividir pelo determinante", **INCOMPLETO}

    def __init__(self, a, **kw):
        a = M.matriz(a)
        super().__init__([("A", a)], M.inversa(a), [("A", theme.TEXT), (MINUS + "1", COL, "sup")],
                         {"faltou_dividir": M.adjunta(a)}, **kw)
        self.fracoes = True

    def fontes(self, r, c):
        return [(0, "linha", c), (0, "coluna", r)]

    def descricao(self):
        return "inversa de A pela adjunta"
