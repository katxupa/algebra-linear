"""Questions answered with one tap on a tile, about a matrix or a system that is on the screen.

    2.3  Simetrica(A)                 TipoProduto((2, 3), (3, 2))
    3.2  Caracteristica(A)
    4    Solucao(S, (2, 1))           Classificar(S)            Grau(S)
    5    Regular(A)
    6    Inversoes([3, 1, 2])         Paridade([3, 1, 2])       Det(A)        Cofator(A, 2, 1)
         DetApos(A, "L1 <-> L2")      CramerMatriz(S, 1)        CramerValor(S, 1)

`S` is always the augmented matrix [A | B] of the system.
"""
from __future__ import annotations

from fractions import Fraction

import pygame

from .. import escalonamento as E
from .. import matrizes as M
from .. import theme
from ..scene import draw
from ..textos import t
from .base import SUCESSO, ERRO
from .nocoes import Grade, Qual, Tile, _Escolha, _partes, _quatro, LIN, COL, MARCA, fmt_num, mini_matriz

SIM, NAO = "sim", "nao"
NAO_EXISTE = "nao_existe"


def _pergunta(fim: str, ctx) -> tuple:
    return (fim, theme.OK if ctx.solved else COL)


class _SimNao(_Escolha):
    baralhar = False

    def __init__(self, matriz, sim: bool, **kw):
        super().__init__(matriz, **kw)
        self.opcoes = [SIM, NAO]
        self.resposta = SIM if sim else NAO


# ---- 2.3 -------------------------------------------------------------------------------------

class Simetrica(_Escolha):
    """Symmetric (A = Aᵗ), antisymmetric (A = −Aᵗ) or neither."""
    ERROS = {"simetrica_trocada": "confundiu simétrica com anti-simétrica"}
    baralhar = False

    def __init__(self, matriz, **kw):
        super().__init__(matriz, **kw)
        a = M.matriz(self.m)
        at = M.transposta(a)
        if a == M.escala(-1, at) and a == at:
            raise ValueError("Simetrica: a matriz nula é as duas coisas; usar outra")
        self.resposta = "m_simetrica" if a == at else "m_antissimetrica" if a == M.escala(-1, at) else "m_nenhuma"
        self.opcoes = ["m_simetrica", "m_antissimetrica", "m_nenhuma"]
        troca = {"m_simetrica": "m_antissimetrica", "m_antissimetrica": "m_simetrica"}
        self.erros = {troca[self.resposta]: "simetrica_trocada"} if self.resposta in troca else {}

    def _ajuda(self, surf, ctx):
        self.g.diagonal(surf, tuple(int(v * (0.4 + 0.6 * ctx.hint_alpha)) for v in MARCA))

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("matriz") + " ", theme.TEXT), _pergunta(t(self.resposta) if ctx.solved else "?", ctx)])

    def descricao(self):
        return f"matriz {t(self.resposta).lower()}"


class TipoProduto(_Escolha):
    """Type of A · B from the types of A and B, or 'it does not exist'."""
    ERROS = {
        "tipo_de_dentro": "usou os números de dentro (colunas de A × linhas de B) para o tipo do produto",
        "nao_compativel": "deu um tipo a um produto que não existe (colunas de A ≠ linhas de B)",
    }

    def __init__(self, a, b, **kw):
        super().__init__(None, **kw)
        ta = tuple(a) if isinstance(a[0], int) else M.tipo(a)
        tb = tuple(b) if isinstance(b[0], int) else M.tipo(b)
        self.ta, self.tb = ta, tb
        ok = ta[1] == tb[0]
        self.resposta = (ta[0], tb[1]) if ok else NAO_EXISTE
        outros = [(ta[0], tb[1]), (ta[1], tb[0]), ta, tb, (tb[1], ta[0])]
        self.opcoes = _quatro(([self.resposta] if ok else []) + [o for o in outros if o != self.resposta])[:3] + [NAO_EXISTE]
        self.erros = ({(ta[1], tb[0]): "tipo_de_dentro"} if ok
                      else {o: "nao_compativel" for o in self.opcoes if o != NAO_EXISTE})
        self.erros.pop(self.resposta, None)

    def iniciar(self):
        super().iniciar()
        self.formas = [Grade([["·"] * n for _ in range(m)]) for m, n in (self.ta, self.tb)]

    def _layout_matriz(self, ctx, area):
        for k, g in enumerate(self.formas):
            g.max_cell = 44
            g.layout(pygame.Rect(area.x + k * area.w // 2, area.y, area.w // 2, area.h), folga=False)

    def _desenhar_matriz(self, surf, ctx):
        for g in self.formas:
            g.desenhar(surf, cor=theme.TEXT_DIM)

    def _ajuda(self, surf, ctx):
        for g in self.formas:
            g.rotulos(surf)

    def _tile(self, v):
        if v == NAO_EXISTE:
            return [(t(NAO_EXISTE), theme.TEXT)]
        return [(str(v[0]), LIN), (" × ", theme.TEXT), (str(v[1]), COL)]

    def desenhar_alvo(self, surf, ctx):
        (m, n), (p, q) = self.ta, self.tb
        self._titulo(surf, ctx, [("(", theme.TEXT), (str(m), LIN), (" × ", theme.TEXT), (str(n), COL), (") · (", theme.TEXT),
                                 (str(p), LIN), (" × ", theme.TEXT), (str(q), COL), (") = ", theme.TEXT),
                                 _pergunta("?", ctx)], 44)

    def descricao(self):
        return f"tipo do produto ({self.ta[0]} × {self.ta[1]}) · ({self.tb[0]} × {self.tb[1]})"


# ---- 3.2 -------------------------------------------------------------------------------------

class Caracteristica(_Escolha):
    """c(A): the number of pivots of an echelon form of A."""
    ERROS = {"contou_linhas": "contou todas as linhas, mesmo as que ficam nulas depois de escalonar"}

    def __init__(self, matriz, **kw):
        super().__init__(matriz, **kw)
        a = M.matriz(self.m)
        linhas = len(a)
        self.resposta = M.caracteristica(a)
        self.erros = {linhas: "contou_linhas"} if linhas != self.resposta else {}
        self.opcoes = _quatro([v for v in (self.resposta, linhas, self.resposta + 1, self.resposta - 1, len(a[0]),
                                           self.resposta + 2) if v >= 0])

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("c(A) = ", theme.TEXT), _pergunta(str(self.resposta) if ctx.solved else "?", ctx)])

    def _ajuda(self, surf, ctx):
        pass

    def descricao(self):
        return f"característica = {self.resposta}"


# ---- 4: linear systems -----------------------------------------------------------------------------

class _Sistema:
    """Mixin: `self.m` is the augmented matrix [A | B]; the bar is drawn before the last column."""

    def _ampliada(self):
        self.barra = len(self.m[0]) - 1
        return M.matriz(self.m)

    def _ajuda(self, surf, ctx):
        pass


class Solucao(_Sistema, _SimNao):
    """Is this point a solution of the system?"""

    def __init__(self, sistema, ponto, **kw):
        self.ponto = [E.frac(v) for v in ponto]
        super().__init__(sistema, M.e_solucao(M.matriz(sistema), ponto), **kw)
        if len(self.ponto) != len(self._ampliada()[0]) - 1:
            raise ValueError("Solucao: o ponto precisa de um valor para cada incógnita")

    def desenhar_alvo(self, surf, ctx):
        ponto = "(" + ", ".join(fmt_num(v) for v in self.ponto) + ")"
        self._titulo(surf, ctx, [(ponto + " ", COL), (t("e_solucao"), theme.TEXT)], 40)

    def descricao(self):
        return "o ponto é solução do sistema?"


class Classificar(_Sistema, _Escolha):
    """Impossible, possible and determined, or possible and undetermined."""
    ERROS = {
        "incognita_livre": "disse determinado, mas há incógnitas livres (c(A) < n)",
        "linha_impossivel": "disse possível, mas há uma linha do tipo 0 = número (c(A) ≠ c([A|B]))",
        "nao_impossivel": "disse impossível, mas o sistema tem solução",
        "homogeneo_impossivel": "disse impossível num sistema homogéneo (tem sempre a solução nula)",
    }
    baralhar = False

    def __init__(self, sistema, **kw):
        super().__init__(sistema, **kw)
        a = self._ampliada()
        self.resposta = "sel_" + M.classificar(a)
        self.opcoes = ["sel_imp", "sel_pd", "sel_pi"]
        homogeneo = all(r[-1] == 0 for r in a)
        self.erros = {
            "sel_imp": {"sel_pd": "linha_impossivel", "sel_pi": "linha_impossivel"},
            "sel_pd": {"sel_imp": "nao_impossivel"},
            "sel_pi": {"sel_imp": "nao_impossivel", "sel_pd": "incognita_livre"},
        }[self.resposta]
        if homogeneo and "sel_imp" in self.erros:
            self.erros["sel_imp"] = "homogeneo_impossivel"

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("sistema_t") + " ", theme.TEXT), _pergunta(t(self.resposta) if ctx.solved else "?", ctx)], 40)

    def descricao(self):
        return f"classificar o sistema: {t(self.resposta).lower()}"


class Grau(_Sistema, _Escolha):
    """Degree of indetermination g = n − c(A): the number of free unknowns."""
    ERROS = {"contou_pivots": "deu o número de pivots (c(A)) em vez das incógnitas livres (n − c(A))"}

    def __init__(self, sistema, **kw):
        super().__init__(sistema, **kw)
        a = self._ampliada()
        n = len(a[0]) - 1
        if M.classificar(a) == "imp":
            raise ValueError("Grau: o sistema é impossível, não tem grau de indeterminação")
        c = M.caracteristica(a, n)
        self.resposta = n - c
        self.erros = {c: "contou_pivots"} if c != self.resposta else {}
        self.opcoes = _quatro([self.resposta, c, n, self.resposta + 1, 0, self.resposta + 2])

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("g = ", theme.TEXT), _pergunta(str(self.resposta) if ctx.solved else "?", ctx)])

    def descricao(self):
        return f"grau de indeterminação = {self.resposta}"


# ---- 5 and 6: regular matrices, determinants ---------------------------------------------------------

class Regular(_SimNao):
    """Is the matrix regular (invertible)?"""
    ERROS = {"det_zero": "disse que é regular, mas o determinante é 0 (as linhas dependem umas das outras)"}

    def __init__(self, matriz, **kw):
        a = M.matriz(matriz)
        super().__init__(matriz, M.det(a) != 0, **kw)
        self.erros = {SIM: "det_zero"} if self.resposta == NAO else {}

    def _ajuda(self, surf, ctx):
        pass

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("m_regular") + " ", theme.TEXT), _pergunta("?", ctx)])

    def descricao(self):
        return "a matriz é regular?"


class Det(_Escolha):
    """|A|: the determinant."""
    ERROS = {
        "sinal": "valor certo, sinal errado",
        "so_diagonal": "multiplicou só a diagonal principal (isso só serve para matrizes triangulares)",
        "somou": "somou os dois produtos em vez de os subtrair",
    }

    def __init__(self, matriz, **kw):
        super().__init__(matriz, **kw)
        a = M.matriz(self.m)
        n = len(a)
        d = M.det(a)
        diag = Fraction(1)
        for i in range(n):
            diag *= a[i][i]
        anti = Fraction(1)
        for i in range(n):
            anti *= a[i][n - 1 - i]
        self.resposta = d
        cand = {-d: "sinal", diag: "so_diagonal"}
        if n == 2:
            cand[diag + anti] = "somou"
        self.erros = {v: k for v, k in cand.items() if v != d}
        self.opcoes = _quatro([d, *self.erros, d + 1, d - 1, d + 2])

    def _ajuda(self, surf, ctx):
        self.g.diagonal(surf, tuple(int(v * (0.4 + 0.6 * ctx.hint_alpha)) for v in MARCA))

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("|A| = ", theme.TEXT), _pergunta(fmt_num(self.resposta) if ctx.solved else "?", ctx)])

    def descricao(self):
        return f"determinante = {fmt_num(self.resposta)}"


class Cofator(_Escolha):
    """A_ij = (−1)^(i+j) |A(i | j)|."""
    ERROS = {
        "sinal_cofator": "calculou o determinante menor e esqueceu o sinal (−1)^(i+j)",
        "entrada": "respondeu com a entrada a_ij em vez do cofator",
    }

    def __init__(self, matriz, i, j, **kw):
        super().__init__(matriz, **kw)
        a = M.matriz(self.m)
        self.i, self.j = i, j
        c = M.cofator(a, i - 1, j - 1)
        menor = M.det(M.menor(a, i - 1, j - 1))
        self.resposta = c
        self.erros = {v: k for v, k in ((a[i - 1][j - 1], "entrada"), (menor, "sinal_cofator")) if v != c}
        self.opcoes = _quatro([c, *self.erros, -c, c + 1, c - 1, c + 2])

    def _ajuda(self, surf, ctx):                    # the row and the column that are struck out
        self.g.faixa(surf, LIN, linha=self.i - 1)
        self.g.faixa(surf, COL, coluna=self.j - 1)
        self.g.desenhar(surf)

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("A", theme.TEXT), (str(self.i), LIN, "sub"), (str(self.j), COL, "sub"), (" = ", theme.TEXT),
                                 _pergunta(fmt_num(self.resposta) if ctx.solved else "?", ctx)], 52)

    def descricao(self):
        return f"cofator A{self.i}{self.j} = {fmt_num(self.resposta)}"


class DetApos(_Escolha):
    """|A| is shown. What is the determinant after one elementary operation? (Teorema 6.3)"""
    ERROS = {
        "troca_sinal": "trocou duas linhas e esqueceu que o determinante muda de sinal",
        "fator_esquecido": "multiplicou uma linha por k e esqueceu de multiplicar o determinante por k",
        "combina_muda": "somou a uma linha um múltiplo de outra e achou que o determinante mudava",
    }

    def __init__(self, matriz, operacao: str, **kw):
        super().__init__(matriz, **kw)
        a = M.matriz(self.m)
        self.d = M.det(a)
        if self.d == 0:
            raise ValueError("DetApos: usar uma matriz com determinante diferente de 0")
        self.op = E.parse(operacao)
        tipo = self.op[0].replace("_col", "")
        if tipo == "troca":
            self.resposta, self.erros = -self.d, {self.d: "troca_sinal"}
        elif tipo == "multiplica":
            k = E.frac(self.op[2])
            self.resposta, self.erros = k * self.d, {self.d: "fator_esquecido"}
        else:
            k = E.frac(self.op[2])
            self.resposta = self.d
            self.erros = {v: "combina_muda" for v in (-self.d, k * self.d) if v != self.d}
        self.erros.pop(self.resposta, None)
        self.opcoes = _quatro([self.resposta, *self.erros, -self.resposta, self.d, 2 * self.d, 0, self.d + 1])

    def _ajuda(self, surf, ctx):
        pass

    def desenhar_alvo(self, surf, ctx):
        # two lines, so that it stays readable on a phone: the determinants, then the operation
        _partes(surf, [(f"|A| = {fmt_num(self.d)}      |B| = ", theme.TEXT),
                       _pergunta(fmt_num(self.resposta) if ctx.solved else "?", ctx)],
                ctx.width / 2, ctx.hud_y - 12, 38, ctx.width - 170)
        _partes(surf, [("A  →  B :   ", theme.TEXT_DIM), (E.texto(self.op), LIN)],
                ctx.width / 2, ctx.hud_y + 26, 28, ctx.width - 170)

    def descricao(self):
        return f"determinante depois de {E.texto(self.op)}"


class DetProp(_Escolha):
    """Properties of the determinant (Teorema 6.4), from the determinants alone:
        DetProp("produto", 2, 3)          |A| = 2, |B| = 3   ->  |A · B| = 6
        DetProp("transposta", 5)          |A| = 5            ->  |Aᵗ| = 5
        DetProp("escalar", 3, k=2, n=2)   |A| = 3, A 2 × 2   ->  |2A| = 12
        DetProp("inversa", 4)             |A| = 4            ->  |A⁻¹| = 1/4"""
    ERROS = {
        "det_soma": "somou os determinantes: o determinante do produto é o PRODUTO dos determinantes",
        "fator_n": "multiplicou por k só uma vez: o k sai de cada linha, fica k elevado à ordem da matriz",
        "det_transposta": "achou que transpor muda o determinante",
        "det_inversa": "não inverteu: o determinante da inversa é 1 / |A|",
    }

    def __init__(self, tipo, a, b=None, k=None, n=2, **kw):
        super().__init__(None, **kw)
        a = E.frac(a)
        self.tipo, self.a, self.n = tipo, a, n
        self.b = E.frac(b) if b is not None else None
        self.k = E.frac(k) if k is not None else None
        if tipo == "produto":
            self.resposta, cand = a * self.b, {a + self.b: "det_soma"}
        elif tipo == "transposta":
            self.resposta, cand = a, {-a: "det_transposta", 1 / a: "det_transposta"}
        elif tipo == "escalar":
            self.resposta, cand = self.k ** n * a, {self.k * a: "fator_n", a: "fator_n"}
        elif tipo == "inversa":
            self.resposta, cand = 1 / a, {a: "det_inversa", -a: "det_inversa"}
        else:
            raise ValueError("DetProp: tipo deve ser 'produto', 'transposta', 'escalar' ou 'inversa'")
        self.erros = {v: c for v, c in cand.items() if v != self.resposta}
        self.opcoes = _quatro([self.resposta, *self.erros, -self.resposta, self.resposta + 1, 0, self.resposta + 2])

    def _dados(self) -> list:
        dados = f"|A| = {fmt_num(self.a)}"
        if self.tipo == "produto":
            dados += f"        |B| = {fmt_num(self.b)}"
        if self.tipo == "escalar":
            dados += f"        A :  {self.n} × {self.n}"
        return [(dados, theme.TEXT)]

    def _pedido(self) -> list:
        return {
            "produto": [("|A · B|", theme.TEXT)],
            "transposta": [("|A", theme.TEXT), ("t", COL, "sup"), ("|", theme.TEXT)],
            "escalar": [("|", theme.TEXT), (fmt_num(self.k) if self.k is not None else "", COL), ("A|", theme.TEXT)],
            "inversa": [("|A", theme.TEXT), ("−1", COL, "sup"), ("|", theme.TEXT)],
        }[self.tipo]

    def _desenhar_matriz(self, surf, ctx):
        _partes(surf, self._dados(), ctx.width / 2, ctx.height * 0.36, 52, ctx.width - 40)

    def _ajuda(self, surf, ctx):
        pass

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, self._pedido() + [(" = ", theme.TEXT),
                                                  _pergunta(fmt_num(self.resposta) if ctx.solved else "?", ctx)], 48)

    def descricao(self):
        return f"propriedade do determinante ({self.tipo}): {fmt_num(self.resposta)}"


class _Permutacao(_Escolha):
    def __init__(self, perm, **kw):
        self.perm = list(perm)
        self.n_inv = M.inversoes(self.perm)
        super().__init__([self.perm], **kw)

    def _ajuda(self, surf, ctx):
        pass


class Inversoes(_Permutacao):
    """How many inversions does the permutation have (pairs where a bigger number comes first)?"""

    def __init__(self, perm, **kw):
        super().__init__(perm, **kw)
        self.resposta = self.n_inv
        self.opcoes = _quatro([v for v in (self.n_inv, self.n_inv + 1, self.n_inv - 1, len(self.perm),
                                           self.n_inv + 2, 0) if v >= 0])

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("inversoes") + " = ", theme.TEXT), _pergunta(str(self.resposta) if ctx.solved else "?", ctx)], 40)

    def descricao(self):
        return f"inversões da permutação {self.perm}: {self.n_inv}"


class Paridade(_Permutacao):
    """Even or odd permutation (even or odd number of inversions)."""
    baralhar = False

    def __init__(self, perm, **kw):
        super().__init__(perm, **kw)
        self.resposta = "p_par" if self.n_inv % 2 == 0 else "p_impar"
        self.opcoes = ["p_par", "p_impar"]

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [(t("permutacao") + " ", theme.TEXT), _pergunta(t(self.resposta) if ctx.solved else "?", ctx)], 40)

    def descricao(self):
        return f"paridade da permutação {self.perm}"


# ---- 6.7: Cramer ----------------------------------------------------------------------------------

def _cramer(sistema):
    a = M.matriz(sistema)
    n = len(a)
    if len(a[0]) != n + 1 or M.det([r[:-1] for r in a]) == 0:
        raise ValueError("isto não é um sistema de Cramer (n equações, n incógnitas, matriz regular)")
    return a, n


class CramerMatriz(Qual):
    """Which matrix is A_i (column i of A replaced by the independent terms)?"""
    ERROS = {
        "coluna_errada": "substituiu outra coluna, não a da incógnita pedida",
        "linha_coluna": "substituiu uma linha em vez de uma coluna",
    }

    def __init__(self, sistema, i, **kw):
        super(Qual, self).__init__(**kw)
        self.sistema, n = _cramer(sistema)
        self.i = i
        b = [r[-1] for r in self.sistema]
        coef = [r[:-1] for r in self.sistema]
        outra = i % n                                   # another column (0-based)
        linha = [b[:] if r == i - 1 else row[:] for r, row in enumerate(coef)]
        self.lista = [(M.cramer_matriz(self.sistema, i - 1), None),
                      (M.cramer_matriz(self.sistema, outra), "coluna_errada"), (linha, "linha_coluna")]
        self.certa = 0

    def iniciar(self):
        super().iniciar()
        self.g = Grade(self.sistema)
        self.g.barra = len(self.sistema)

    def _topo(self, ctx):
        return int(124 + (ctx.height - 124) * 0.4)

    def layout(self, ctx):
        super().layout(ctx)
        self.g.max_cell = 64
        self.g.layout(pygame.Rect(16, 124, ctx.width - 32, self._topo(ctx) - 124 - 10), folga=False)

    def desenhar(self, surf, ctx):
        self.g.desenhar(surf)
        super().desenhar(surf, ctx)

    def desenhar_alvo(self, surf, ctx):
        _partes(surf, [("A", theme.TEXT), (str(self.i), COL, "sub"), (" = ", theme.TEXT), _pergunta("?", ctx)],
                ctx.width / 2, ctx.hud_y, 50, ctx.width - 170)

    def descricao(self):
        return f"regra de Cramer: qual é a matriz A{self.i}?"


class CramerValor(_Sistema, _Escolha):
    """x_i = |A_i| / |A|."""
    ERROS = {
        "faltou_dividir": "deu |A_i| e esqueceu de dividir por |A|",
        "coluna_errada": "deu o valor de outra incógnita",
    }

    def __init__(self, sistema, i, **kw):
        super().__init__(sistema, **kw)
        a, n = _cramer(sistema)
        self._ampliada()
        self.i = i
        d = M.det([r[:-1] for r in a])
        xs = [M.det(M.cramer_matriz(a, k)) / d for k in range(n)]
        self.resposta = xs[i - 1]
        cand = {xs[i % n]: "coluna_errada", M.det(M.cramer_matriz(a, i - 1)): "faltou_dividir"}
        self.erros = {v: k for v, k in cand.items() if v != self.resposta}
        self.opcoes = _quatro([self.resposta, *self.erros, -self.resposta, self.resposta + 1, self.resposta - 1,
                               self.resposta + 2])

    def desenhar_alvo(self, surf, ctx):
        self._titulo(surf, ctx, [("x", theme.TEXT), (str(self.i), COL, "sub"), (" = ", theme.TEXT),
                                 _pergunta(fmt_num(self.resposta) if ctx.solved else "?", ctx)], 52)

    def descricao(self):
        return f"regra de Cramer: x{self.i} = {fmt_num(self.resposta)}"
