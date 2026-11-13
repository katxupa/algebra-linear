"""Scenes: "real" situations where the maths decides what happens to somebody.

Segurar: a (well fed) character hangs over the water. Every force is a vector starting at the
same point. The student drags the missing force and presses the check button: the plank goes
away and the SUM of the vectors moves the character. Zero = he stays. Anything else = off he
goes, in the direction of the sum (down: splash, up: to the moon, sideways: bye).
"""
from __future__ import annotations

import math

import pygame

from ..linalg import Vec2
from ..scene import draw
from ..ui.widgets import Handle
from .. import theme
from .base import Desafio, SUCESSO
from .vetores import _coords_label, _snap_for

PESO = theme.BAD
CORDA = theme.VEC2
VENTO = (110, 225, 215)
TUA = theme.VEC
FIO = (95, 98, 115)            # the rope itself, behind the force arrow
PELE = (186, 130, 94)          # the character: skin, T-shirt, shorts, hair, flip-flops
CAMISOLA = (232, 232, 238)
CALCOES = (70, 84, 146)
CABELO = (92, 64, 46)
CHINELO = (240, 150, 60)
TRACO = (38, 26, 20)           # eyebrows, pupils, mouth
MADEIRA = (165, 118, 72)
AGUA = (8, 30, 62)
ONDA = (70, 150, 230)

AGUA_Y = -4.4                  # water level, world units
PES_Y = -3.0                   # feet of the character, relative to the hanging point
ESPERA = 0.35                  # cartoon pause in mid-air before the fall starts
QUEDA = 1.9                    # whole fall animation; then he is back on the plank


class Segurar(Desafio):
    """Hold the character: drag the missing force so that all the forces add up to zero.

        Segurar(peso=3)                                   one rope: the opposite of the weight
        Segurar(peso=4, cordas=[(-2, 2)])                 another rope already pulls
        Segurar(peso=4, cordas=[(-1, 2)], vento=(3, 0))   and the wind pushes
    """

    ERROS = {
        "caiu": "a soma das forças aponta para baixo: o boneco cai à água",
        "voou": "a soma das forças aponta para cima: o boneco sai disparado para o céu",
        "de_lado": "para cima e para baixo está certo, mas sobra força para um lado",
    }
    confirmar = True
    base = False

    def __init__(self, peso, cordas=(), vento=None, **kw):
        super().__init__(**kw)
        if cordas and isinstance(cordas[0], (int, float)):
            cordas = [cordas]                      # a single rope written without the list
        self.fixas = [(Vec2(0, -abs(peso)), PESO, "P")]
        self.fixas += [(Vec2.of(c), CORDA, "T") for c in cordas]
        if vento is not None:
            self.fixas.append((Vec2.of(vento), VENTO, "V"))
        total = Vec2()
        for f, _, _ in self.fixas:
            total = total + f
        self.alvo = -total
        self.queda = None
        self.t = 0.0
        self.ajuda = False

    def no_contexto(self, desafios, indice):
        primeira = not any(isinstance(d, Segurar) for d in desafios[:indice])
        if primeira and self.audio is None:
            self.audio = "cena_cordas"             # the narrator presents the scene once

    def iniciar(self):
        usados = [f for f, _, _ in self.fixas] + [self.alvo]
        inicio = next(p for p in (Vec2(3, 0), Vec2(-3, 0), Vec2(2, -1), Vec2(-2, -1), Vec2(1, 0))
                      if not any(p.close(u) for u in usados))
        self.tip = Handle(inicio, TUA, snap=_snap_for(*usados))
        self.handles = [self.tip]
        self.queda = None                          # [seconds since the check, sum of the forces]
        self.ajuda = False

    def resultante(self) -> Vec2:
        r = self.tip.pos
        for f, _, _ in self.fixas:
            r = r + f
        return r

    def avaliar(self):
        r = self.resultante()
        if r.close((0, 0)):
            self.queda = None
            return SUCESSO
        self.queda = [0.0, r]
        return "caiu" if r.y < -1e-6 else "voou" if r.y > 1e-6 else "de_lado"

    def update(self, ctx):
        self.t = ctx.time
        if self.queda:
            self.queda[0] += ctx.dt
            if self.queda[0] > QUEDA:
                self.queda = None

    def press(self, ctx, sx, sy):
        self.queda = None                          # touching again puts him back on the plank
        return super().press(ctx, sx, sy)

    def descricao(self):
        return f"segurar o boneco: falta a força {self.alvo.fmt()}"

    # ---- the fall -------------------------------------------------------------------
    def _aceleracao(self, r: Vec2) -> float:
        return 14 + 5 * r.length()

    def _desloc(self) -> Vec2:
        """How far the character has moved from the hanging point (world units)."""
        if not self.queda:
            return Vec2()
        t, r = self.queda
        t = max(0.0, t - ESPERA)
        return r * (0.5 * self._aceleracao(r) * t * t / r.length())

    def _mergulho(self):
        """(seconds since the feet hit the water, x of the splash), or None."""
        if not self.queda:
            return None
        t, r = self.queda
        if r.y >= 0:
            return None
        a, n = self._aceleracao(r), r.length()
        t_agua = math.sqrt(2 * (PES_Y - AGUA_Y) / (a * -r.y / n))
        desde = t - ESPERA - t_agua
        if desde < 0:
            return None
        return desde, r.x / n * 0.5 * a * t_agua * t_agua

    # ---- drawing --------------------------------------------------------------------
    def desenhar(self, surf, ctx):
        cam, s = ctx.cam, ctx.cam.scale
        d = self._desloc()
        P = lambda x, y: cam.to_screen((d.x + x, d.y + y))
        o = cam.to_screen((0, 0))
        caindo = self.queda is not None
        modo = "queda" if caindo else "salvo" if ctx.solved else "espera"

        self._desenhar_vento(surf, cam)
        if not caindo:
            if not ctx.solved:
                self._desenhar_prancha(surf, cam, s)
            for f in [f for f, _, letra in self.fixas if letra == "T"] + [self.tip.pos]:
                if f.length() > 1e-6:                  # the rope goes on, up to the ceiling
                    draw.line(surf, FIO, o, cam.to_screen(f * (40 / f.length())), 2)
        self._desenhar_barbatana(surf, cam, s)
        self._desenhar_boneco(surf, P, s, modo)
        self._desenhar_agua(surf, ctx)

        if caindo:
            self._desenhar_salpicos(surf, cam, s)
            draw.arrow(surf, theme.RESULT, P(0, 0), P(*self.queda[1]), theme.VECTOR_WIDTH_PX + 2)
            return
        for f, cor, letra in self.fixas:
            self._forca(surf, cam, f, cor, letra, seta=letra != "P")   # the weight is drawn under the face
        self._forca(surf, cam, self.tip.pos, TUA, "")
        if self.ajuda and not ctx.solved:              # help: the sum of all the forces, live
            c = tuple(int(v * (0.35 + 0.65 * ctx.hint_alpha)) for v in theme.RESULT)
            draw.dashed_arrow(surf, c, o, cam.to_screen(self.resultante()), 4)
        _coords_label(surf, cam, self.tip.pos, TUA)
        self.tip.draw(surf, cam)

    def _forca(self, surf, cam, f: Vec2, cor, letra: str, seta: bool = True):
        o, tip = cam.to_screen((0, 0)), cam.to_screen(f)
        if seta:
            draw.arrow(surf, cor, o, tip, theme.VECTOR_WIDTH_PX + 1)
        n = f.length()
        if letra and n > 1e-6:
            draw.text(surf, letra, (tip[0] + f.x / n * 22, tip[1] - f.y / n * 22), 32, cor)

    def _desenhar_boneco(self, surf, P, s, modo):
        """A chubby person hanging by the hands: T-shirt too short for the belly, flip-flops."""
        caindo = modo == "queda"
        k = 0.0 if modo == "espera" else math.sin(self.t * (20 if caindo else 6)) * 0.22
        fino = max(2, int(s * 0.04))

        def membro(a, b, largura, cor):                # a limb: thick line with round ends
            a, b, r = P(*a), P(*b), max(2, int(largura * s / 2))
            pygame.draw.line(surf, cor, a, b, 2 * r)
            draw.circle(surf, cor, a, r)
            draw.circle(surf, cor, b, r)

        def oval(c, rx, ry, cor, de=0, ate=360):       # an ellipse, or a slice of one
            draw.polygon(surf, cor, [P(c[0] + rx * math.cos(math.radians(g)), c[1] + ry * math.sin(math.radians(g)))
                                     for g in range(de, ate + 1, 12)])

        for lado in (-1, 1):                           # legs, feet, flip-flops
            pe = (lado * 0.38 + (k * lado if caindo else k), PES_Y + 0.11 + abs(k) * 0.4)
            membro((lado * 0.34, -2.2), pe, 0.27, PELE)
            membro(pe, (pe[0] + lado * 0.2, pe[1] - 0.01), 0.17, PELE)
            pygame.draw.line(surf, CHINELO, P(pe[0] - lado * 0.14, pe[1] - 0.11),
                             P(pe[0] + lado * 0.34, pe[1] - 0.11), max(2, int(s * 0.06)))
        draw.polygon(surf, CALCOES, [P(x, y) for x, y in ((-0.72, -1.95), (0.72, -1.95), (0.6, -2.55), (0.08, -2.55),
                                                         (0, -2.38), (-0.08, -2.55), (-0.6, -2.55))])
        for lado in (-1, 1):                           # arms: holding on, or flailing
            ombro, mao = (lado * 0.6, -1.12), (lado * 0.09, -0.02)
            if caindo:
                mao = (lado * 1.15, -0.5 + 0.4 * math.sin(self.t * 24 + lado))
            membro(ombro, mao, 0.19, PELE)
            membro(ombro, (ombro[0] + (mao[0] - ombro[0]) * 0.36, ombro[1] + (mao[1] - ombro[1]) * 0.36),
                   0.26, CAMISOLA)                     # sleeve
        oval((0, -1.55), 0.84, 0.72, PELE)             # the belly...
        oval((0, -1.55), 0.84, 0.72, CAMISOLA, -24, 204)   # ...and the T-shirt that no longer covers it
        draw.circle(surf, TRACO, P(0, -2.03), max(2, s * 0.035))         # navel
        if not caindo:                                 # the weight: over the body, under the face
            draw.arrow(surf, PESO, P(0, 0), P(*self.fixas[0][0]), theme.VECTOR_WIDTH_PX + 1)
        draw.circle(surf, CABELO, P(0, -0.5), 0.33 * s)                  # hair, ears, face
        for lado in (-1, 1):
            draw.circle(surf, PELE, P(lado * 0.29, -0.6), 0.075 * s)
        draw.circle(surf, PELE, P(0, -0.59), 0.29 * s)
        for lado in (-1, 1):                           # eyes wide open while falling; worried eyebrows
            olho = (lado * 0.115, -0.54)
            draw.circle(surf, (250, 250, 250), P(*olho), max(2.5, s * (0.1 if caindo else 0.068)))
            draw.circle(surf, TRACO, P(olho[0], olho[1] - (0 if caindo else 0.015)), max(1.2, s * 0.032))
            sobe = 0.05 if modo != "salvo" else -0.01
            draw.line(surf, TRACO, P(lado * 0.2, -0.44 + (0.06 if caindo else 0)),
                      P(lado * 0.04, -0.44 + sobe + (0.06 if caindo else 0)), fino)
        if caindo:                                     # mouth: scream / smile / worried
            oval((0, -0.74), 0.075, 0.095, TRACO)
        elif modo == "salvo":
            pygame.draw.lines(surf, TRACO, False, [P(-0.13, -0.7), P(-0.06, -0.77), P(0.06, -0.77), P(0.13, -0.7)], fino)
        else:
            draw.line(surf, TRACO, P(-0.08, -0.75), P(0.08, -0.73), fino)
        if not caindo:
            draw.circle(surf, theme.TEXT, P(0, 0), max(4, s * 0.1), 2)   # the ring he hangs from

    def _desenhar_prancha(self, surf, cam, s):
        y = PES_Y - 0.1
        for x in (-1.15, 1.15):
            draw.line(surf, MADEIRA, cam.to_screen((x, y)), cam.to_screen((x, AGUA_Y - 0.3)), 3)
        pygame.draw.line(surf, MADEIRA, cam.to_screen((-1.4, y)), cam.to_screen((1.4, y)), max(4, int(s * 0.12)))

    def _desenhar_barbatana(self, surf, cam, s):
        fase = self.t * 0.45
        x, sentido = 3.4 * math.sin(fase), (1 if math.cos(fase) > 0 else -1)
        bx, by = cam.to_screen((x, AGUA_Y))
        draw.polygon(surf, (120, 135, 150), [(bx - 0.35 * s, by + 6), (bx + 0.35 * s, by + 6),
                                             (bx - sentido * 0.2 * s, by - 0.55 * s)])

    def _desenhar_agua(self, surf, ctx):
        y0 = ctx.cam.to_screen((0, AGUA_Y))[1]
        crista = [(x, y0 + 4 * math.sin(x * 0.03 + self.t * 2)) for x in range(0, ctx.width + 16, 16)]
        pygame.draw.polygon(surf, AGUA, crista + [(ctx.width + 16, ctx.height), (0, ctx.height)])
        pygame.draw.lines(surf, ONDA, False, crista, 2)

    def _desenhar_salpicos(self, surf, cam, s):
        m = self._mergulho()
        if not m or m[0] > 1.0:
            return
        desde, x = m
        cx, cy = cam.to_screen((x, AGUA_Y))
        cor = tuple(int(v * (1 - desde)) for v in ONDA)
        for k in range(3):                             # rings on the water
            r = (0.4 + 1.8 * desde + 0.35 * k) * s
            pygame.draw.ellipse(surf, cor, (cx - r, cy - r * 0.18, 2 * r, r * 0.36), 2)
        for k in range(7):                             # drops flying up
            vx, vy = (k - 3) * 0.9, 5.5 - abs(k - 3) * 0.6
            gy = vy * desde - 7 * desde * desde
            if gy > 0:
                draw.circle(surf, ONDA, cam.to_screen((x + vx * desde, AGUA_Y + gy)), 3)

    def _desenhar_vento(self, surf, cam):
        v = next((f for f, _, letra in self.fixas if letra == "V"), None)
        if v is None or v.length() < 1e-6:
            return
        u = v * (1 / v.length())
        cor = tuple(int(c * 0.45) for c in VENTO)
        for k in range(7):                             # streaks drifting with the wind
            ao_longo = (k * 3.7 + self.t * 5) % 14 - 7
            lado = -4.2 + k * 1.35
            a = Vec2(u.x * ao_longo - u.y * lado, u.y * ao_longo + u.x * lado)
            draw.line(surf, cor, cam.to_screen(a), cam.to_screen(a + u * 0.9), 2)

    def desenhar_alvo(self, surf, ctx):
        partes = []
        for _, cor, letra in self.fixas:
            partes += [(letra, cor), (" + ", theme.TEXT)]
        partes += [("?", TUA), (" = 0", theme.TEXT)]
        size = 48
        while size > 24 and sum(draw.text_width(p, size) for p, _ in partes) > ctx.width - 150:
            size -= 2
        x = ctx.width / 2 - sum(draw.text_width(p, size) for p, _ in partes) / 2
        for p, cor in partes:
            draw.text(surf, p, (x, ctx.hud_y), size, cor, "midleft")
            x += draw.text_width(p, size)

    def desenhar_dica(self, surf, ctx):
        """Help = the sum of the forces shown live (make it disappear). The engine calls this before
        `desenhar`, so the arrow itself is drawn there, on top of the character."""
        self.ajuda = True
