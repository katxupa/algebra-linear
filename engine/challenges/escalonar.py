"""Escalonar: the student transforms a matrix (or the system it represents) with elementary
row operations until it is in the form the exercise asks for:

    Escalonar([[1, 2, 3], [2, 5, 8]])                         # goal: row echelon form
    Escalonar([[...]], objetivo="reduzida")                   # goal: reduced row echelon form
    Escalonar([[...]], forma="sistema")                       # start showing the equations
    Escalonar([[...]], aumentada=False)                       # plain matrix (no | b column)
    Escalonar([[...]], colunas=True)                          # also allow Ci <-> Cj

The operation is BUILT by the student, like on a calculator: key by key
(L3  →  L3  −  2  L1  =), or by typing on the keyboard, or by tapping a row label to insert
"L3". Nothing is suggested: the engine only checks that the operation is elementary.
Fractions are exact. Every operation is recorded (history) and can be undone.
The student decides when to stop with ✓; the engine checks the requested form.
"""
from __future__ import annotations

import pygame

from .. import theme
from .. import escalonamento as E
from ..scene import draw
from ..textos import t
from .base import Desafio, SUCESSO

ARROW, SWAP, MINUS, DOT = "→", "↔", "−", "·"
OPERADORES = {ARROW, SWAP, "+", MINUS}          # shown with spaces around them
BACKSPACE, LIMPAR, APLICAR = "⌫", "AC", "="


class Escalonar(Desafio):
    ERROS = {
        "nao_escalonada": "carregou em ✓ mas a matriz ainda não está em escada",
        "nao_reduzida": "está escalonada, mas não reduzida (pivôs ≠ 1 ou números acima dos pivôs)",
        "multiplicar_por_zero": "tentou multiplicar uma linha por 0",
        "mesma_linha": "tentou trocar/somar uma linha com ela própria",
        "comando": "montou uma operação que não é elementar ou está incompleta",
        "coluna_sistema": "num sistema, tentou multiplicar/somar colunas (só se pode trocar)",
        "operacao": "(opcional) fez uma operação válida — som curto de confirmação",
    }
    confirmar = True
    painel = True
    plano = False

    def __init__(self, matriz, objetivo: str = "escalonada", aumentada: bool = True,
                 forma: str = "matriz", colunas: bool = False, variaveis=None, recursos=None, **kw):
        super().__init__(**kw)
        self.inicial = E.matriz(matriz)
        self.objetivo = objetivo
        self.aumentada = aumentada
        self.forma_inicial = forma if aumentada else "matriz"
        self.colunas = colunas
        cols = len(self.inicial[0])
        self.n_coef = cols - 1 if aumentada else cols
        if variaveis:
            self.nomes0 = list(variaveis)
        elif self.n_coef <= 4 and aumentada:
            self.nomes0 = list("xyzw"[: self.n_coef])
        else:
            self.nomes0 = [f"x{c + 1}" for c in range(self.n_coef)]
        # Keys are introduced gradually: an exercise shows only what its solution needs
        # ('troca', 'multiplica', 'combina', 'fracoes'), plus what earlier exercises of the
        # same aula already introduced (see no_contexto). `recursos=` overrides it.
        if recursos == "todos":
            recursos = {"troca", "multiplica", "combina", "fracoes"}
        self.recursos_proprios = set(recursos) if recursos else E.recursos_necessarios(
            self.inicial, objetivo, self.n_coef, colunas)
        if colunas:
            self.recursos_proprios.add("colunas")
        self._definir_teclas(self.recursos_proprios, None)

    def no_contexto(self, desafios, indice):
        anteriores = [d for d in desafios[:indice] if isinstance(d, Escalonar)]
        antes: set[str] = set()
        for d in anteriores:
            antes |= d.recursos_proprios
        self._definir_teclas(antes | self.recursos_proprios, antes if anteriores else None)

    def _keys_for(self, rec) -> tuple[list[str], list[str]]:
        rows = len(self.inicial)
        completo = {"troca", "multiplica", "combina", "fracoes"} <= rec
        ops = [f"L{i + 1}" for i in range(rows)]
        if "colunas" in rec:
            ops += [f"C{c + 1}" for c in range(self.n_coef)]
        if rec & {"troca", "colunas"}:
            ops.append(SWAP)
        if rec & {"multiplica", "combina"}:
            ops.append(ARROW)
        if "combina" in rec:
            ops.append("+")
        if rec & {"multiplica", "combina"}:
            ops.append(MINUS)
        if "fracoes" in rec:
            ops.append("/")
        if completo:
            ops += [DOT, "(", ")"]
        nums = list("1234567890") if rec & {"multiplica", "combina"} else []
        return ops, nums

    def _definir_teclas(self, rec, antes):
        self.recursos = set(rec)
        self.teclas_op, self.teclas_num = self._keys_for(self.recursos)
        self.teclas = self.teclas_op + self.teclas_num + [BACKSPACE, LIMPAR]
        if antes is None:          # first exercise of the aula: nothing is "new"
            self.teclas_novas0 = set()
        else:
            old = sum(self._keys_for(set(antes)), [])
            self.teclas_novas0 = {k for k in self.teclas_op + self.teclas_num
                                  if k not in old and not (k[:1] == "L" and k[1:].isdigit())}

    # ---- calculator layout (depends on the screen width) --------------------------------
    # wide screens: operation keys in one row, numbers in another
    # narrow (phone): operation keys on the left (4 per column), number pad 3x4 on the right
    def _largo(self, w) -> bool:
        return w >= 15 * 58 + 20

    def _grade(self, w):
        """Key cells [(col, row, key, block)] and number of rows."""
        cells = []
        if self._largo(w):
            rows = [self.teclas_op + ([] if self.teclas_num else [BACKSPACE, LIMPAR])]
            if self.teclas_num:
                rows.append(self.teclas_num + [BACKSPACE, LIMPAR])
            for r, row in enumerate(rows):
                for c, k in enumerate(row):
                    cells.append((c, r, k, len(row)))
            return cells, len(rows)
        ops = self.teclas_op + ([] if self.teclas_num else [BACKSPACE, LIMPAR])
        for k, key in enumerate(ops):
            c, r = divmod(k, 4)
            cells.append((c, r, key, "op"))
        op_cols = -(-len(ops) // 4)
        n_rows = min(4, len(ops))
        if self.teclas_num:
            pad = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", BACKSPACE, LIMPAR]
            for k, key in enumerate(pad):
                r, c = divmod(k, 3)
                cells.append((op_cols + c, r, key, "pad"))
            n_rows = 4
        return cells, n_rows

    def altura_painel(self, w) -> int:
        _, n_rows = self._grade(w)
        return 14 + 52 + 10 + n_rows * 56 + 64

    # ---- state ----------------------------------------------------------------------
    def iniciar(self):
        self.m = [r[:] for r in self.inicial]
        self.nomes = self.nomes0[:]
        self.hist: list[tuple] = []          # (op, matrix_before, names_before)
        self.forma = self.forma_inicial
        self.expr: list[str] = []            # the operation being built, token by token
        self.realce = ([], 0.0)              # rows (or columns) just changed, time left
        self.erro_expr = 0.0                 # red flash of the display after a bad operation
        self.ui: dict[str, pygame.Rect] = {}
        self.keys_ui: list[tuple[pygame.Rect, str]] = []
        self.rows_ui: list[pygame.Rect] = []
        self.cols_ui: list[pygame.Rect] = []
        self.teclas_novas = set(self.teclas_novas0)   # glow until used
        self.anunciado = False

    def estado(self):
        return tuple(tuple(r) for r in self.m)

    def avaliar(self):
        if self.objetivo == "reduzida":
            if E.reduzida(self.m, self.n_coef):
                return SUCESSO
            return "nao_reduzida" if E.escalonada(self.m, self.n_coef) else "nao_escalonada"
        return SUCESSO if E.escalonada(self.m, self.n_coef) else "nao_escalonada"

    def update(self, ctx):
        rows, left = self.realce
        self.realce = (rows, max(0.0, left - ctx.dt))
        self.erro_expr = max(0.0, self.erro_expr - ctx.dt)
        if self.teclas_novas and not self.anunciado:
            self.anunciado = True
            ctx.som("novidade")          # optional clip: "Olha, tecla nova!"

    # ---- the expression (calculator display) ---------------------------------------------
    def texto_expr(self) -> str:
        out = ""
        for tok in self.expr:
            if tok in OPERADORES:
                out = out.rstrip() + f" {tok} "
            else:
                out += tok
        return out.strip()

    def inserir(self, tok: str) -> None:
        if tok == BACKSPACE:
            if self.expr:
                self.expr.pop()
        elif tok == LIMPAR:
            self.expr = []
        else:
            self.expr.append(tok)

    def aplicar_expr(self, ctx) -> bool:
        txt = self.texto_expr()
        if not txt:
            return False
        try:
            op = E.parse(txt)
        except E.OperacaoInvalida as e:
            self.erro_expr = 0.6
            ctx.aviso(e.chave)
            return False
        if self.executar(ctx, op):
            self.expr = []
            return True
        self.erro_expr = 0.6
        return False

    # ---- operations -------------------------------------------------------------------
    def executar(self, ctx, op) -> bool:
        try:
            novo = E.aplicar(self.m, op, self.n_coef, sistema=self.aumentada)
        except E.OperacaoInvalida as e:
            ctx.aviso(e.chave)
            return False
        self.hist.append((op, self.m, self.nomes[:]))
        self.m = novo
        if op[0] == "troca_col":
            a, b = op[1] - 1, op[2] - 1
            self.nomes[a], self.nomes[b] = self.nomes[b], self.nomes[a]
            self.realce = ([("c", a), ("c", b)], 0.8)
        elif op[0].endswith("_col"):
            self.realce = ([("c", op[1] - 1)], 0.8)
        elif op[0] == "troca":
            self.realce = ([("l", op[1] - 1), ("l", op[2] - 1)], 0.8)
        else:
            self.realce = ([("l", op[1] - 1)], 0.8)
        ctx.som("operacao")
        return True

    def desfazer(self):
        if self.hist:
            _, self.m, self.nomes = self.hist.pop()

    # ---- input --------------------------------------------------------------------------
    def press(self, ctx, sx, sy):
        for rect, key in self.keys_ui:
            if rect.collidepoint(sx, sy):
                self.inserir(key)
                self.teclas_novas.discard(key)
                return True
        for name, rect in self.ui.items():
            if rect.collidepoint(sx, sy):
                if name == "aplicar":
                    self.aplicar_expr(ctx)
                elif name == "desfazer":
                    self.desfazer()
                elif name == "forma":
                    self.forma = "sistema" if self.forma == "matriz" else "matriz"
                return True
        for i, rect in enumerate(self.rows_ui):      # tapping a row label writes "L3"
            if rect.collidepoint(sx, sy):
                self.inserir(f"L{i + 1}")
                return True
        for c, rect in enumerate(self.cols_ui):
            if rect.collidepoint(sx, sy):
                self.inserir(f"C{c + 1}")
                return True
        return False

    def move(self, ctx, sx, sy):
        pass

    def release(self, ctx):
        return False

    def tecla(self, ctx, ev):
        if ev.type == pygame.TEXTINPUT:
            for ch in ev.text:
                self._tecla_fisica(ch)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_BACKSPACE:
                self.inserir(BACKSPACE)
            elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.aplicar_expr(ctx)
            elif ev.key == pygame.K_DELETE:
                self.inserir(LIMPAR)
            elif ev.key == pygame.K_z and ev.mod & pygame.KMOD_CTRL:
                self.desfazer()

    def _tecla_fisica(self, ch: str) -> None:
        """Physical keyboard -> calculator tokens. 'L' '2' -> L2, '->' or '=' -> →, '<->' -> ↔."""
        e = self.expr
        last = e[-1] if e else ""
        up = ch.upper()
        if ch.isspace():
            return
        if up in "LC":
            e.append(up)                              # digits typed next complete it: L -> L2
        elif ch.isdigit() and last in ("L", "C"):
            e[-1] += ch
        elif ch.isdigit():
            e.append(ch)
        elif ch in "-−":
            e[-1:] = ["<-"] if last == "<" else [last, MINUS] if last else [MINUS]
        elif ch == ">":
            if last == MINUS:
                e[-1] = ARROW
            elif last == "<-":
                e[-1] = SWAP
        elif ch == "<":
            e.append("<")
        elif ch == "=":
            e.append(ARROW)
        elif ch in "*·":
            e.append(DOT)
        elif ch in "+/()":
            e.append(ch)

    # ---- layout -------------------------------------------------------------------------
    def layout(self, ctx):
        w, h = ctx.width, ctx.height
        ph = self.altura_painel(w)
        top = h - ph
        self.ui = {}
        # display + aplicar
        self.ui["display"] = pygame.Rect(10, top + 14, w - 20 - 96, 52)
        self.ui["aplicar"] = pygame.Rect(w - 10 - 88, top + 14, 88, 52)
        # calculator keys
        gap = 8
        y0 = top + 14 + 52 + 10
        cells, n_rows = self._grade(w)
        self.keys_ui = []
        if self._largo(w):
            per_row = max(15, max(n for *_, n in cells))
            kw = min(80, (w - 20 - gap * (per_row - 1)) / per_row)
            for c, r, key, n in cells:
                x0 = w / 2 - (n * kw + (n - 1) * gap) / 2
                self.keys_ui.append((pygame.Rect(int(x0 + c * (kw + gap)), int(y0 + r * 56), int(kw), 48), key))
        else:
            total = max(c for c, *_ in cells) + 1
            split = gap if any(blk == "pad" for *_, blk in cells) else 0
            kw = min(80, (w - 20 - gap * (total - 1) - split) / total)
            x0 = w / 2 - (total * kw + (total - 1) * gap + split) / 2
            for c, r, key, blk in cells:
                extra = split if blk == "pad" else 0
                self.keys_ui.append((pygame.Rect(int(x0 + c * (kw + gap) + extra), int(y0 + r * 56), int(kw), 48),
                                     key))
        yb = y0 + n_rows * 56 + 6
        names = ["desfazer"] + (["forma"] if self.aumentada else [])
        bw = (w - 20 - gap * (len(names) - 1)) / len(names)
        for k, name in enumerate(names):
            self.ui[name] = pygame.Rect(int(10 + k * (bw + gap)), yb, int(bw), 46)

    # ---- drawing ------------------------------------------------------------------------
    def desenhar_alvo(self, surf, ctx):
        label = t("objetivo_reduzida") if self.objetivo == "reduzida" else t("objetivo_escalonada")
        size = 34
        while size > 16 and draw.text_width(label, size) > ctx.width - 190:   # room for ← and the dots
            size -= 1
        draw.text(surf, label, (ctx.width / 2, ctx.hud_y + (14 if ctx.width < 600 else 0)), size, theme.VEC)

    def _area(self, ctx):
        return 118, ctx.height - self.altura_painel(ctx.width) - 70

    def desenhar(self, surf, ctx):
        top, bottom = self._area(ctx)
        if self.forma == "sistema":
            self._desenhar_sistema(surf, ctx, top, bottom)
        elif self.hist and ctx.width >= 700:
            # like on paper: previous step  ~(operation)~  current matrix
            op, anterior, _ = self.hist[-1]
            left_w = ctx.width * 0.36
            cy = (top + bottom) / 2 + 10
            size = int(self._cell_size(ctx, top, bottom, left_w) * 0.8)
            _mini_matriz(surf, anterior, left_w / 2 + 10, cy, size, self.n_coef if self.aumentada else None)
            draw.text(surf, "~", (left_w + 12, cy), 54, theme.TEXT_DIM)
            draw.text_setas(surf, E.texto(op), (left_w + 12, cy - 40), 22, theme.VEC2)
            self._desenhar_matriz(surf, ctx, top, bottom, cx=left_w + 24 + (ctx.width - left_w - 24) / 2,
                                  largura=ctx.width - left_w - 24)
        else:
            self._desenhar_matriz(surf, ctx, top, bottom)
        if self.hist:   # last operations
            ultimos = "   ".join(E.texto(op) for op, *_ in self.hist[-3:])
            draw.text_setas(surf, ("… " if len(self.hist) > 3 else "") + ultimos,
                            (ctx.width / 2, bottom + 46), 24, theme.TEXT_DIM)

    def _cell_size(self, ctx, top, bottom, largura=None):
        rows, cols = len(self.m), len(self.m[0])
        largura = largura or ctx.width
        return int(max(18, min(54, (bottom - top) / (rows * 1.9 + 1.2), (largura - 100) / (cols * 2.6 + 1))))

    def _row_label(self, surf, cx, cy, size, row_h, r):
        rad = max(16, int(size * 0.55))
        draw.circle(surf, theme.PANEL_HI, (cx, cy), rad)
        draw.circle(surf, theme.VEC2, (cx, cy), rad, 2)
        draw.text(surf, f"L{r + 1}", (cx, cy), int(rad * 0.95), theme.TEXT)
        self.rows_ui.append(pygame.Rect(int(cx - rad * 1.3), int(cy - row_h / 2), int(rad * 2.6), int(row_h)))

    def _desenhar_matriz(self, surf, ctx, top, bottom, cx=None, largura=None):
        cx = ctx.width / 2 if cx is None else cx
        size = self._cell_size(ctx, top, bottom, largura)
        rows, cols = len(self.m), len(self.m[0])
        col_w = [max(_valor_w(self.m[r][c], size) for r in range(rows)) + size * 0.9 for c in range(cols)]
        row_h = size * 1.75
        sep = size * 0.6 if self.aumentada else 0
        total_w = sum(col_w) + sep
        x0 = cx - total_w / 2 + size * 0.5
        y0 = (top + bottom) / 2 - rows * row_h / 2 + size * 0.5
        piv = E.pivos(self.m, self.n_coef)
        hl, left = self.realce
        fade = left / 0.8 if left else 0

        xs = []
        x = x0
        for c in range(cols):
            if self.aumentada and c == self.n_coef:
                x += sep
            xs.append(x + col_w[c] / 2)
            x += col_w[c]
        # column headers (variables); tappable (inserts "C2") when column swaps are allowed
        self.cols_ui = []
        for c in range(self.n_coef if (self.aumentada or self.colunas) else 0):
            hot = ("c", c) in hl and fade
            color = theme.OK if hot else (theme.VEC2 if self.colunas else theme.TEXT_DIM)
            hy = y0 - size * 0.9
            if self.colunas and self.aumentada:          # column number above the variable name
                r = draw.text(surf, f"C{c + 1}", (xs[c], hy - size * 0.45), int(size * 0.45), color)
                r = r.union(draw.text(surf, self.nomes[c], (xs[c], hy + size * 0.05), int(size * 0.5),
                                      theme.TEXT_DIM))
            elif self.colunas:
                r = draw.text(surf, f"C{c + 1}", (xs[c], hy), int(size * 0.55), color)
            else:
                r = draw.text(surf, self.nomes[c], (xs[c], hy), int(size * 0.55), color)
            if self.colunas:
                self.cols_ui.append(r.inflate(24, 16))

        for c in range(cols):   # a column that just changed: vertical green band
            if ("c", c) in hl and fade:
                band = pygame.Rect(int(xs[c] - col_w[c] / 2 + 4), int(y0 + 2), int(col_w[c] - 8),
                                   int(rows * row_h - 4))
                pygame.draw.rect(surf, tuple(int(v * 0.35 * fade) for v in theme.OK), band, border_radius=10)
        self.rows_ui = []
        for r in range(rows):
            cy = y0 + r * row_h + row_h / 2
            if ("l", r) in hl and fade:
                band = pygame.Rect(int(x0 - size * 0.2), int(cy - row_h / 2 + 4), int(total_w), int(row_h - 8))
                pygame.draw.rect(surf, tuple(int(v * 0.35 * fade) for v in theme.OK), band, border_radius=10)
            for c in range(cols):
                v = self.m[r][c]
                color = theme.VEC if piv[r] == c else theme.TEXT_DIM if v == 0 else theme.TEXT
                _valor(surf, v, (xs[c], cy), size, color)
            self._row_label(surf, x0 - size * 1.4, cy, size, row_h, r)

        yt, yb = y0 + 4, y0 + rows * row_h - 4
        xl, xr = x0 - size * 0.2, x0 + total_w - size * 0.3
        tick = size * 0.3
        pygame.draw.lines(surf, theme.TEXT, False, [(xl + tick, yt), (xl, yt), (xl, yb), (xl + tick, yb)], 2)
        pygame.draw.lines(surf, theme.TEXT, False, [(xr - tick, yt), (xr, yt), (xr, yb), (xr - tick, yb)], 2)
        if self.aumentada:
            bx = xs[self.n_coef] - col_w[self.n_coef] / 2 - sep / 2
            draw.dashed_line(surf, theme.TEXT_DIM, (bx, yt), (bx, yb), 2, 8)

    def _desenhar_sistema(self, surf, ctx, top, bottom):
        rows = len(self.m)
        size = max(20, min(46, int((bottom - top) / (rows * 1.8 + 1))))
        lines = [self._equacao(r) for r in range(rows)]
        widest = max(draw.text_width(s, size) for s in lines)
        livre = ctx.width - (size * 2.4 + 24)      # the row labels (L1, L2...) need room on the left
        if widest > livre:
            size = max(16, int(size * livre / widest))
            widest = max(draw.text_width(s, size) for s in lines)
        row_h = size * 1.8
        y0 = (top + bottom) / 2 - rows * row_h / 2
        x0 = max(size * 2.4, ctx.width / 2 - widest / 2)
        hl, left = self.realce
        fade = left / 0.8 if left else 0
        self.rows_ui, self.cols_ui = [], []
        for r, s in enumerate(lines):
            cy = y0 + r * row_h + row_h / 2
            if ("l", r) in hl and fade:
                pygame.draw.rect(surf, tuple(int(v * 0.35 * fade) for v in theme.OK),
                                 (int(x0 - 10), int(cy - row_h / 2 + 4), int(widest + 20), int(row_h - 8)),
                                 border_radius=10)
            draw.text_setas(surf, s, (x0, cy), size, theme.TEXT, "midleft")
            self._row_label(surf, x0 - size * 1.5, cy, size, row_h, r)
        yt, yb = y0 + 6, y0 + rows * row_h - 6
        bx = x0 - size * 0.45
        pygame.draw.lines(surf, theme.TEXT_DIM, False, [(bx + 6, yt), (bx, yt + 6), (bx, yb - 6), (bx + 6, yb)], 2)

    def _equacao(self, r) -> str:
        parts = []
        for c in range(self.n_coef):
            v = self.m[r][c]
            if v == 0:
                continue
            k = abs(v)
            coef = "" if k == 1 else (f"({E.fmt(k)})" if "/" in E.fmt(k) else E.fmt(k))
            if not parts:
                parts.append((MINUS if v < 0 else "") + coef + self.nomes[c])
            else:
                parts.append(f"{MINUS if v < 0 else '+'} {coef}{self.nomes[c]}")
        return f"{' '.join(parts) if parts else '0'} = {E.fmt(self.m[r][self.n_coef])}"

    def desenhar_painel(self, surf, ctx):
        # display
        d = self.ui["display"]
        bad = self.erro_expr > 0
        pygame.draw.rect(surf, theme.BG, d, border_radius=10)
        pygame.draw.rect(surf, theme.BAD if bad else theme.VEC2, d, 2, border_radius=10)
        txt = self.texto_expr()
        if txt:
            caret = "|" if int(ctx.time * 2) % 2 == 0 else ""
            size = 32
            while size > 16 and draw.text_width(txt + caret, size) > d.w - 24:
                size -= 1
            draw.text_setas(surf, txt + caret, (d.x + 14, d.centery), size, theme.BAD if bad else theme.TEXT, "midleft")
        else:
            if "+" in self.teclas:
                ex = f"L2 {ARROW} L2 {MINUS} 3L1"
            elif ARROW in self.teclas:
                ex = f"L1 {ARROW} 2L1"
            else:
                ex = f"L1 {SWAP} L2"
            draw.text_setas(surf, f"{t('monta_operacao')}  {ex}", (d.x + 14, d.centery), 24, theme.TEXT_DIM,
                            "midleft")
        a = self.ui["aplicar"]
        ready = bool(self.expr)
        pygame.draw.rect(surf, theme.PANEL_HI if ready else theme.PANEL, a, border_radius=10)
        pygame.draw.rect(surf, theme.OK if ready else theme.TEXT_DIM, a, 2, border_radius=10)
        draw.text(surf, "=", a.center, 40, theme.OK if ready else theme.TEXT_DIM)

        # keys
        for rect, key in self.keys_ui:
            kind = ("linha" if key[:1] in "LC" and key[1:].isdigit()
                    else "op" if key in (SWAP, ARROW, "+", MINUS, DOT, "/", "(", ")")
                    else "edit" if key in (BACKSPACE, LIMPAR) else "num")
            border = {"linha": theme.VEC2, "op": theme.VEC, "edit": theme.BAD, "num": theme.GRID_MAJOR}[kind]
            pygame.draw.rect(surf, theme.BG, rect, border_radius=10)
            pygame.draw.rect(surf, border, rect, 2, border_radius=10)
            if key in self.teclas_novas:                       # just introduced: glow + tag
                glow = 0.5 + 0.5 * __import__("math").sin(ctx.time * 5)
                pygame.draw.rect(surf, tuple(int(v * (0.5 + 0.5 * glow)) for v in theme.OK),
                                 rect.inflate(6, 6), 3, border_radius=12)
                draw.text(surf, t("novo"), (rect.centerx, rect.top - 2), 16, theme.OK)
            if key == BACKSPACE:
                cx, cy, s = rect.centerx, rect.centery, rect.h * 0.16
                pygame.draw.lines(surf, theme.TEXT, True, [(cx - s * 1.6, cy), (cx - s * 0.6, cy - s),
                                                           (cx + s * 1.4, cy - s), (cx + s * 1.4, cy + s),
                                                           (cx - s * 0.6, cy + s)], 2)
            else:
                size = 28
                while size > 14 and draw.text_width(key, size) > rect.w - 8:
                    size -= 1
                draw.text_setas(surf, key, rect.center, size, theme.TEXT)

        # undo / view toggle
        for name in ("desfazer", "forma"):
            rect = self.ui.get(name)
            if not rect:
                continue
            on = name != "desfazer" or self.hist
            pygame.draw.rect(surf, theme.BG, rect, border_radius=10)
            pygame.draw.rect(surf, theme.GRID_MAJOR if on else theme.PANEL_HI, rect, 2, border_radius=10)
            label = t("desfazer") if name == "desfazer" else (
                t("ver_matriz") if self.forma == "sistema" else t("ver_sistema"))
            draw.text(surf, label, rect.center, 24, theme.TEXT if on else theme.TEXT_DIM)

    def desenhar_dica(self, surf, ctx):
        op = E.proximo_passo(self.m, self.objetivo, self.n_coef, self.colunas)
        if op:
            c = tuple(int(v * (0.35 + 0.65 * ctx.hint_alpha)) for v in theme.VEC2)
            _, bottom = self._area(ctx)
            draw.text_setas(surf, E.texto(op), (ctx.width / 2, bottom + 16), 30, c)

    def descricao(self):
        return f"escalonar matriz {len(self.inicial)}x{len(self.inicial[0])} até forma {self.objetivo}"


def _mini_matriz(surf, m, cx, cy, size, n_coef=None):
    """Previous step, smaller and dimmed (no buttons)."""
    rows, cols = len(m), len(m[0])
    col_w = [max(_valor_w(m[r][c], size) for r in range(rows)) + size * 0.8 for c in range(cols)]
    row_h = size * 1.6
    sep = size * 0.5 if n_coef is not None else 0
    total = sum(col_w) + sep
    x = cx - total / 2
    y0 = cy - rows * row_h / 2
    xs = []
    for c in range(cols):
        if n_coef is not None and c == n_coef:
            x += sep
        xs.append(x + col_w[c] / 2)
        x += col_w[c]
    for r in range(rows):
        for c in range(cols):
            _valor(surf, m[r][c], (xs[c], y0 + r * row_h + row_h / 2), size, theme.TEXT_DIM)
    yt, yb = y0 + 2, y0 + rows * row_h - 2
    xl, xr = cx - total / 2 - 4, cx + total / 2 + 4
    tick = size * 0.3
    pygame.draw.lines(surf, theme.TEXT_DIM, False, [(xl + tick, yt), (xl, yt), (xl, yb), (xl + tick, yb)], 2)
    pygame.draw.lines(surf, theme.TEXT_DIM, False, [(xr - tick, yt), (xr, yt), (xr, yb), (xr - tick, yb)], 2)
    if n_coef is not None:
        bx = xs[n_coef] - col_w[n_coef] / 2 - sep / 2
        draw.dashed_line(surf, theme.PANEL_HI, (bx, yt), (bx, yb), 2, 6)


def _valor_w(v, size) -> float:
    if v.denominator == 1:
        return draw.font(size).size(E.fmt(v))[0]
    f = draw.font(int(size * 0.62))
    sign = draw.font(size).size(MINUS)[0] if v < 0 else 0
    return sign + max(f.size(str(abs(v.numerator)))[0], f.size(str(v.denominator))[0]) + 6


def _valor(surf, v, center, size, color):
    """Integer, or a stacked fraction (numerator over denominator)."""
    if v.denominator == 1:
        draw.text(surf, E.fmt(v), center, size, color)
        return
    small = int(size * 0.62)
    f = draw.font(small)
    num, den = str(abs(v.numerator)), str(v.denominator)
    bar = max(f.size(num)[0], f.size(den)[0]) + 6
    cx, cy = center
    if v < 0:
        sw = draw.font(size).size(MINUS)[0]
        draw.text(surf, MINUS, (cx - bar / 2 - sw / 2 - 2, cy), size, color)
    draw.text(surf, num, (cx, cy - small * 0.45), small, color)
    draw.line(surf, color, (cx - bar / 2, cy), (cx + bar / 2, cy), 2)
    draw.text(surf, den, (cx, cy + small * 0.5), small, color)
