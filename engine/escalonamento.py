"""Elementary row operations on matrices of exact fractions (pure logic, no drawing).

Operations (1-based row/column numbers, as students write them):
    ("troca", i, j)          Li <-> Lj
    ("multiplica", i, k)     Li -> k·Li          (k != 0)
    ("combina", i, k, j)     Li -> Li + k·Lj     (i != j)
    ("troca_col", i, j)      Ci <-> Cj
    ("multiplica_col", i, k) Ci -> k·Ci          (plain matrices only)
    ("combina_col", i, k, j) Ci -> Ci + k·Cj     (plain matrices only)

Column scaling / combining would change the solution of a system, so on an augmented
matrix only column swaps (renaming the variables) are allowed: pass `sistema=True`.
"""
from __future__ import annotations

import re
from fractions import Fraction

MINUS = "−"


class OperacaoInvalida(ValueError):
    """Operation that is not elementary. `chave` is the narrator audio key for it."""

    def __init__(self, chave: str, msg: str = ""):
        super().__init__(msg or chave)
        self.chave = chave


def frac(x) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, str):
        return Fraction(x.replace(MINUS, "-").replace(" ", ""))
    return Fraction(x).limit_denominator(10_000)


def fmt(x: Fraction) -> str:
    x = frac(x)
    s = str(abs(x.numerator)) if x.denominator == 1 else f"{abs(x.numerator)}/{x.denominator}"
    return (MINUS if x < 0 else "") + s


def matriz(rows) -> list[list[Fraction]]:
    return [[frac(v) for v in r] for r in rows]


def aplicar(m, op, n_coef: int | None = None, sistema: bool = False):
    """Return a NEW matrix with the operation applied. Raises OperacaoInvalida."""
    m = [r[:] for r in m]
    n = len(m)
    kind = op[0]
    cols = n_coef if n_coef is not None else len(m[0])

    def coluna(j):
        if not 1 <= j <= cols:
            raise OperacaoInvalida("coluna_inexistente", "essa coluna não existe (ou é a dos termos independentes)")
        return j - 1

    if kind in ("multiplica_col", "combina_col") and sistema:
        raise OperacaoInvalida("coluna_sistema", "num sistema só se podem trocar colunas (as outras mudam a solução)")

    def linha(i):
        if not 1 <= i <= n:
            raise OperacaoInvalida("linha_inexistente", f"não existe a linha {i}")
        return i - 1

    if kind == "troca":
        a, b = linha(op[1]), linha(op[2])
        if a == b:
            raise OperacaoInvalida("mesma_linha", "trocar uma linha com ela própria não muda nada")
        m[a], m[b] = m[b], m[a]
    elif kind == "multiplica":
        a, k = linha(op[1]), frac(op[2])
        if k == 0:
            raise OperacaoInvalida("multiplicar_por_zero", "multiplicar uma linha por 0 apaga a equação")
        m[a] = [k * v for v in m[a]]
    elif kind == "combina":
        a, k, b = linha(op[1]), frac(op[2]), linha(op[3])
        if a == b:
            raise OperacaoInvalida("mesma_linha", "não se soma uma linha a ela própria")
        if k == 0:
            raise OperacaoInvalida("combina_zero", "somar 0 vezes outra linha não muda nada")
        m[a] = [x + k * y for x, y in zip(m[a], m[b])]
    elif kind == "troca_col":
        a, b = coluna(op[1]), coluna(op[2])
        if a == b:
            raise OperacaoInvalida("mesma_coluna", "trocar uma coluna com ela própria não muda nada")
        for r in m:
            r[a], r[b] = r[b], r[a]
    elif kind == "multiplica_col":
        a, k = coluna(op[1]), frac(op[2])
        if k == 0:
            raise OperacaoInvalida("multiplicar_por_zero", "multiplicar uma coluna por 0 apaga-a")
        for r in m:
            r[a] = k * r[a]
    elif kind == "combina_col":
        a, k, b = coluna(op[1]), frac(op[2]), coluna(op[3])
        if a == b:
            raise OperacaoInvalida("mesma_coluna", "não se soma uma coluna a ela própria")
        if k == 0:
            raise OperacaoInvalida("combina_zero", "somar 0 vezes outra coluna não muda nada")
        for r in m:
            r[a] = r[a] + k * r[b]
    else:
        raise OperacaoInvalida("erro", f"operação desconhecida: {kind}")
    return m


def texto(op) -> str:
    """Operation in the usual class notation, e.g. 'L3 → L3 − 2L1'."""
    kind = op[0]
    if kind == "troca":
        return f"L{op[1]} ↔ L{op[2]}"
    if kind == "troca_col":
        return f"C{op[1]} ↔ C{op[2]}"
    x = "C" if kind.endswith("_col") else "L"
    if kind in ("multiplica", "multiplica_col"):
        return f"{x}{op[1]} → {_coef(frac(op[2]))}{x}{op[1]}"
    if kind in ("combina", "combina_col"):
        k = frac(op[2])
        sinal = "+" if k > 0 else MINUS
        return f"{x}{op[1]} → {x}{op[1]} {sinal} {_coef(abs(k))}{x}{op[3]}"
    return str(op)


def _coef(k: Fraction) -> str:
    if k == 1:
        return ""
    if k == -1:
        return MINUS
    s = fmt(k)
    return f"({s})" if "/" in s else s


# ---- shape checks -------------------------------------------------------------------------

def pivos(m, n_coef: int | None = None) -> list[int | None]:
    """Column of the first non-zero coefficient of each row (None for a zero row)."""
    cols = n_coef if n_coef is not None else len(m[0])
    out = []
    for r in m:
        out.append(next((c for c in range(cols) if r[c] != 0), None))
    return out


def escalonada(m, n_coef: int | None = None) -> bool:
    """Row echelon form: zero rows at the bottom, each pivot strictly right of the one above."""
    last = -1
    seen_zero = False
    for p in pivos(m, n_coef):
        if p is None:
            seen_zero = True
            continue
        if seen_zero or p <= last:
            return False
        last = p
    return True


def reduzida(m, n_coef: int | None = None) -> bool:
    """Reduced row echelon form: echelon, every pivot is 1 and the only non-zero in its column."""
    if not escalonada(m, n_coef):
        return False
    for i, p in enumerate(pivos(m, n_coef)):
        if p is None:
            continue
        if m[i][p] != 1:
            return False
        if any(m[r][p] != 0 for r in range(len(m)) if r != i):
            return False
    return True


def proximo_passo(m, objetivo: str = "escalonada", n_coef: int | None = None, colunas: bool = False):
    """One useful next operation (Gauss / Gauss-Jordan), or None if the goal is reached.
    With `colunas=True`, a column with nothing left to pivot is swapped with a later one,
    so the pivots stay on the diagonal."""
    cols = n_coef if n_coef is not None else len(m[0])
    n = len(m)
    r = 0
    for c in range(cols):
        if r >= n:
            break
        rows = [i for i in range(r, n) if m[i][c] != 0]
        if not rows:
            if colunas:
                later = next((c2 for c2 in range(c + 1, cols) if any(m[i][c2] != 0 for i in range(r, n))), None)
                if later is not None:
                    return ("troca_col", c + 1, later + 1)
            continue
        if m[r][c] == 0:
            return ("troca", r + 1, rows[0] + 1)
        for i in range(r + 1, n):
            if m[i][c] != 0:
                return ("combina", i + 1, -m[i][c] / m[r][c], r + 1)
        r += 1
    if objetivo != "reduzida":
        return None
    for i, p in enumerate(pivos(m, n_coef)):
        if p is None:
            continue
        if m[i][p] != 1:
            return ("multiplica", i + 1, 1 / m[i][p])
        for k in range(n):
            if k != i and m[k][p] != 0:
                return ("combina", k + 1, -m[k][p], i + 1)
    return None


def recursos_necessarios(m, objetivo: str = "escalonada", n_coef: int | None = None,
                         colunas: bool = False) -> set[str]:
    """What a reference solution needs: 'troca', 'multiplica', 'combina', 'fracoes', 'colunas'.
    Used to introduce the calculator keys gradually (only what the exercise requires)."""
    need: set[str] = set()
    m = [r[:] for r in m]
    for _ in range(100):
        op = proximo_passo(m, objetivo, n_coef, colunas)
        if op is None:
            break
        need.add("colunas" if op[0] == "troca_col" else op[0])
        if op[0] in ("multiplica", "combina") and frac(op[2]).denominator != 1:
            need.add("fracoes")
        m = aplicar(m, op, n_coef)
    return need


# ---- typed commands --------------------------------------------------------------------------

_NUM = r"[+\-]?\s*\(?\s*[+\-]?\d+(?:\s*/\s*\d+)?\s*\)?"
_ARROW = r"(?:->|→|<-|←|=|:=)"


def _clean(s: str) -> str:
    s = s.strip().upper()
    for a, b in (("−", "-"), ("↔", "<->"), ("→", "->"), ("·", "*"), (" X ", "*")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s)


def _k(text: str | None, sign: str = "+") -> Fraction:
    if not text or text.strip() in ("", "+"):
        k = Fraction(1)
    elif text.strip() == "-":
        k = Fraction(-1)
    else:
        k = frac(text.replace("(", "").replace(")", "").replace(" ", "").replace("*", ""))
    return -k if sign == "-" else k


def parse(cmd: str):
    """Typed operation -> op tuple. Accepts e.g.:
        L1 <-> L2      L1<->L2      L1 ↔ L2      C1 <-> C3
        L2 -> 1/3 L2   L2 = (1/3)L2   L2 -> -L2
        L3 -> L3 - 2L1   L3 = L3 + (-1/2)*L1   L3 <- L3 + L1
    Raises OperacaoInvalida('comando') when it cannot understand."""
    s = _clean(cmd)
    m = re.fullmatch(r"([LC])\s*(\d+)\s*<->\s*([LC])\s*(\d+)", s)
    if m:
        if m.group(1) != m.group(3):
            raise OperacaoInvalida("comando", "não se troca uma linha com uma coluna")
        kind = "troca" if m.group(1) == "L" else "troca_col"
        return (kind, int(m.group(2)), int(m.group(4)))

    m = re.fullmatch(rf"([LC])\s*(\d+)\s*{_ARROW}\s*(.*)", s)
    if not m:
        raise OperacaoInvalida("comando", "não percebi a operação")
    x, i, rhs = m.group(1), int(m.group(2)), m.group(3).replace(" ", "")
    suf = "" if x == "L" else "_col"
    if re.search("C" if x == "L" else "L", rhs):
        raise OperacaoInvalida("comando", "não se misturam linhas com colunas")

    # k·Xi   (scale)
    sm = re.fullmatch(rf"({_NUM}|[+\-])?\*?{x}(\d+)", rhs)
    if sm and int(sm.group(2)) == i:
        return ("multiplica" + suf, i, _k(sm.group(1)))

    # Xi ± k·Xj   (combine)   — also accepts k·Xj + Xi
    cm = re.fullmatch(rf"{x}(\d+)([+\-])({_NUM})?\*?{x}(\d+)", rhs)
    if cm and int(cm.group(1)) == i:
        return ("combina" + suf, i, _k(cm.group(3), cm.group(2)), int(cm.group(4)))
    cm = re.fullmatch(rf"({_NUM}|[+\-])?\*?{x}(\d+)\+{x}(\d+)", rhs)
    if cm and int(cm.group(3)) == i:
        return ("combina" + suf, i, _k(cm.group(1)), int(cm.group(2)))
    raise OperacaoInvalida("comando", "não percebi a operação")
    i, rhs = int(m.group(1)), m.group(2).replace(" ", "")

    # k·Li   (scale)
    sm = re.fullmatch(rf"({_NUM}|[+\-])?\*?L(\d+)", rhs)
    if sm and int(sm.group(2)) == i:
        return ("multiplica", i, _k(sm.group(1)))

    # Li ± k·Lj   (combine)   — also accepts k·Lj + Li
    cm = re.fullmatch(rf"L(\d+)([+\-])({_NUM})?\*?L(\d+)", rhs)
    if cm and int(cm.group(1)) == i:
        return ("combina", i, _k(cm.group(3), cm.group(2)), int(cm.group(4)))
    cm = re.fullmatch(rf"({_NUM}|[+\-])?\*?L(\d+)\+L(\d+)", rhs)
    if cm and int(cm.group(3)) == i:
        return ("combina", i, _k(cm.group(1)), int(cm.group(2)))
    raise OperacaoInvalida("comando", "não percebi a operação")
