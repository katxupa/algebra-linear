"""Matrix arithmetic with exact fractions (pure logic, no drawing): sum, product, transpose, power,
determinant, cofactors, adjoint, inverse, rank, classification of a linear system, permutations."""
from __future__ import annotations

from fractions import Fraction

from . import escalonamento as E


def matriz(m) -> list[list[Fraction]]:
    m = [[E.frac(v) for v in r] for r in m]
    if not m or not m[0] or any(len(r) != len(m[0]) for r in m):
        raise ValueError("a matriz precisa de linhas com o mesmo número de entradas")
    return m


def tipo(m) -> tuple[int, int]:
    return len(m), len(m[0])


def soma(a, b, sinal: int = 1):
    if tipo(a) != tipo(b):
        raise ValueError("só se somam matrizes do mesmo tipo")
    return [[x + sinal * y for x, y in zip(ra, rb)] for ra, rb in zip(a, b)]


def escala(k, a):
    k = E.frac(k)
    return [[k * x for x in r] for r in a]


def transposta(a):
    return [list(col) for col in zip(*a)]


def produto(a, b):
    if len(a[0]) != len(b):
        raise ValueError("produto impossível: as colunas da primeira não batem com as linhas da segunda")
    cols = list(zip(*b))
    return [[sum((x * y for x, y in zip(row, col)), Fraction(0)) for col in cols] for row in a]


def potencia(a, n: int):
    r = a
    for _ in range(n - 1):
        r = produto(r, a)
    return r


def menor(a, i: int, j: int):
    """The submatrix A(i | j): row i and column j removed (0-based)."""
    return [[v for c, v in enumerate(row) if c != j] for r, row in enumerate(a) if r != i]


def det(a) -> Fraction:
    n = len(a)
    if any(len(r) != n for r in a):
        raise ValueError("o determinante só existe para matrizes quadradas")
    if n == 1:
        return a[0][0]
    return sum(((-1) ** j * a[0][j] * det(menor(a, 0, j)) for j in range(n)), Fraction(0))


def cofator(a, i: int, j: int) -> Fraction:
    """A_ij = (−1)^(i+j) |A(i | j)|   (0-based indices)."""
    if len(a) == 1:
        return Fraction(1)
    return (-1) ** (i + j) * det(menor(a, i, j))


def cofatores(a):
    n = len(a)
    return [[cofator(a, i, j) for j in range(n)] for i in range(n)]


def adjunta(a):
    return transposta(cofatores(a))


def inversa(a):
    d = det(a)
    if d == 0:
        raise ValueError("a matriz não é regular (determinante 0)")
    return escala(1 / d, adjunta(a))


def escalonar(a, n_coef: int | None = None):
    """Echelon form reached by the reference solver."""
    m = [r[:] for r in a]
    for _ in range(500):
        op = E.proximo_passo(m, "escalonada", n_coef)
        if op is None:
            break
        m = E.aplicar(m, op, n_coef)
    return m


def caracteristica(a, n_coef: int | None = None) -> int:
    """Number of pivots of an echelon form (looking only at the first `n_coef` columns, if given)."""
    cols = n_coef if n_coef is not None else len(a[0])
    return sum(1 for row in escalonar([r[:cols] for r in a]) if any(v != 0 for v in row))


def classificar(ampliada) -> str:
    """'imp' (impossible), 'pd' (one solution) or 'pi' (infinitely many) for the system [A | B]."""
    n = len(ampliada[0]) - 1
    ca, cab = caracteristica(ampliada, n), caracteristica(ampliada)
    return "imp" if ca != cab else "pd" if ca == n else "pi"


def e_solucao(ampliada, ponto) -> bool:
    p = [E.frac(v) for v in ponto]
    return all(sum((a * x for a, x in zip(row[:-1], p)), Fraction(0)) == row[-1] for row in ampliada)


def inversoes(perm) -> int:
    """How many pairs are out of order in a permutation of 1..n."""
    perm = list(perm)
    if sorted(perm) != list(range(1, len(perm) + 1)):
        raise ValueError("isto não é uma permutação de 1, 2, ..., n")
    return sum(1 for i in range(len(perm)) for j in range(i + 1, len(perm)) if perm[i] > perm[j])


def cramer_matriz(ampliada, i: int):
    """A_i: the coefficient matrix with column i (0-based) replaced by the independent terms."""
    return [[row[-1] if c == i else v for c, v in enumerate(row[:-1])] for row in ampliada]
