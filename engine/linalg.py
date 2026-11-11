"""Tiny pure-Python 2D linear algebra (no numpy, so the web build stays simple)."""
from __future__ import annotations

import math
from dataclasses import dataclass

EPS = 1e-6


@dataclass(frozen=True)
class Vec2:
    x: float = 0.0
    y: float = 0.0

    @staticmethod
    def of(v) -> "Vec2":
        return v if isinstance(v, Vec2) else Vec2(float(v[0]), float(v[1]))

    def __add__(self, o): o = Vec2.of(o); return Vec2(self.x + o.x, self.y + o.y)
    def __sub__(self, o): o = Vec2.of(o); return Vec2(self.x - o.x, self.y - o.y)
    def __mul__(self, k: float): return Vec2(self.x * k, self.y * k)
    __rmul__ = __mul__
    def __neg__(self): return Vec2(-self.x, -self.y)
    def __iter__(self): yield self.x; yield self.y

    def length(self) -> float:
        return math.hypot(self.x, self.y)

    def dot(self, o) -> float:
        o = Vec2.of(o)
        return self.x * o.x + self.y * o.y

    def cross(self, o) -> float:
        o = Vec2.of(o)
        return self.x * o.y - self.y * o.x

    def close(self, o, tol: float = 1e-3) -> bool:
        return (self - o).length() <= tol

    def snapped(self, step: float = 1.0) -> "Vec2":
        return Vec2(round(self.x / step) * step, round(self.y / step) * step)

    def lerp(self, o, t: float) -> "Vec2":
        o = Vec2.of(o)
        return Vec2(self.x + (o.x - self.x) * t, self.y + (o.y - self.y) * t)

    def fmt(self) -> str:
        return f"({fmt_num(self.x)}, {fmt_num(self.y)})"


@dataclass(frozen=True)
class Mat2:
    """Row-major [[a, b], [c, d]]. Columns are where î and ĵ land."""
    a: float = 1.0
    b: float = 0.0
    c: float = 0.0
    d: float = 1.0

    @staticmethod
    def of(m) -> "Mat2":
        if isinstance(m, Mat2):
            return m
        (a, b), (c, d) = m
        return Mat2(float(a), float(b), float(c), float(d))

    @staticmethod
    def identity() -> "Mat2":
        return Mat2()

    @staticmethod
    def from_cols(i, j) -> "Mat2":
        i, j = Vec2.of(i), Vec2.of(j)
        return Mat2(i.x, j.x, i.y, j.y)

    @property
    def i(self) -> Vec2:
        return Vec2(self.a, self.c)

    @property
    def j(self) -> Vec2:
        return Vec2(self.b, self.d)

    def apply(self, v) -> Vec2:
        v = Vec2.of(v)
        return Vec2(self.a * v.x + self.b * v.y, self.c * v.x + self.d * v.y)

    def __matmul__(self, o: "Mat2") -> "Mat2":
        return Mat2(
            self.a * o.a + self.b * o.c, self.a * o.b + self.b * o.d,
            self.c * o.a + self.d * o.c, self.c * o.b + self.d * o.d,
        )

    def det(self) -> float:
        return self.a * self.d - self.b * self.c

    def transpose(self) -> "Mat2":
        return Mat2(self.a, self.c, self.b, self.d)

    def inverse(self) -> "Mat2":
        det = self.det()
        if abs(det) < EPS:
            raise ZeroDivisionError("singular matrix")
        return Mat2(self.d / det, -self.b / det, -self.c / det, self.a / det)

    def swap_cols(self) -> "Mat2":
        return Mat2.from_cols(self.j, self.i)

    def lerp(self, o: "Mat2", t: float) -> "Mat2":
        return Mat2(
            self.a + (o.a - self.a) * t, self.b + (o.b - self.b) * t,
            self.c + (o.c - self.c) * t, self.d + (o.d - self.d) * t,
        )

    def close(self, o, tol: float = 1e-3) -> bool:
        o = Mat2.of(o)
        return all(abs(p - q) <= tol for p, q in zip(self.rows_flat(), o.rows_flat()))

    def rows_flat(self):
        return (self.a, self.b, self.c, self.d)

    def rows(self):
        return ((self.a, self.b), (self.c, self.d))

    def fmt(self) -> str:
        return f"[[{fmt_num(self.a)}, {fmt_num(self.b)}], [{fmt_num(self.c)}, {fmt_num(self.d)}]]"


def fmt_num(x: float) -> str:
    if abs(x - round(x)) < 1e-6:
        return str(int(round(x)))
    return f"{x:.1f}"
