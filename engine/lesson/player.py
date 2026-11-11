"""Plays one Aula: runs its challenges, judges attempts, gives audio + visual feedback."""
from __future__ import annotations

import pygame

from .. import theme
from ..audio import AudioBank
from ..challenges.base import Ctx, SUCESSO, ERRO
from ..coords import Camera
from ..scene import draw
from ..scene.anim import Shake, Effect, Blink, Tween
from ..scene.plane import draw_plane
from ..ui.widgets import Button

HUD_H = 110          # goal area at the top
PANEL_H = 210        # bottom panel for challenges that need one
NEXT_DELAY = 1.6     # seconds between solving and the next challenge
IDLE_AFTER = 20.0    # seconds without input before the "parado" clip


class LessonPlayer:
    def __init__(self, app, aula):
        self.app = app
        self.aula = aula
        self.audio = AudioBank(aula.audio_dirs)
        self.back = Button("back", radius=26)
        self.ok = Button("check", theme.OK, radius=34)
        self.shake = Shake()
        self.flash_bad = Effect(0.5)
        self.flash_ok = Effect(1.0)
        self.blink = Blink()
        self.cam = Camera(app.width, app.height)
        self.ctx = Ctx(self.cam, app.width, app.height, HUD_H / 2, 0)
        self.finished = False
        self.idx = -1
        self.audio.play("intro")
        self._next()

    # ---- flow ---------------------------------------------------------------------
    def _next(self) -> None:
        self.idx += 1
        if self.idx >= len(self.aula.desafios):
            self.finished = True
            self.end_tween = Tween(0.8)
            self.app.mark_done(self.aula)
            self.audio.play("fim")
            return
        self.d = self.aula.desafios[self.idx]
        self.d.iniciar()
        self.fails = 0
        self.hint = False
        self.solved_at = None
        self.last_state = self.d.estado()
        self.idle = 0.0
        self.idle_played = False
        self.ctx.solved = False
        self.enter = Tween(0.5)
        self.resize(self.app.width, self.app.height)
        if self.d.audio:
            self.audio.play(self.d.audio, interrupt=False)

    def _attempt(self) -> None:
        state = self.d.estado()
        if state == self.last_state:
            return                       # nothing changed: not a new attempt
        self.last_state = state
        result = self.d.avaliar()
        if result == SUCESSO:
            self.ctx.solved = True
            self.solved_at = 0.0
            self.flash_ok.start()
            for h in self.d.handles:
                h.enabled = False
            self.audio.play(SUCESSO)
            return
        self.fails += 1
        self.shake.start()
        self.flash_bad.start()
        if self.fails >= self.d.dica_apos and not self.hint:
            self.hint = True
            if self.audio.play("dica"):
                return
        if not self.audio.play(result):
            self.audio.play(ERRO)

    # ---- scene interface ----------------------------------------------------------
    def resize(self, w: int, h: int) -> None:
        bottom = PANEL_H if (not self.finished and self.d.painel) else 0
        self.cam.top_margin, self.cam.bottom_margin = HUD_H, bottom
        self.cam.resize(w, h)
        self.ctx.width, self.ctx.height = w, h
        self.ctx.hud_y = HUD_H / 2 + 6
        self.ctx.bottom_y = h - PANEL_H / 2
        self.back.place(40, 40)
        self.ok.place(w - 60, h - 60 - (PANEL_H if bottom else 0))
        if not self.finished:
            self.d.layout(self.ctx)

    def handle_event(self, ev) -> None:
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            x, y = ev.pos
            self.idle = 0.0
            if self.back.hit(x, y):
                self.audio.stop()
                self.app.open_menu()
                return
            if self.finished:
                if self.end_tween.done:
                    self.app.open_menu()
                return
            if self.solved_at is not None:
                return
            if self.d.confirmar and self.ok.hit(x, y):
                self.ok.flash = 1.0
                self._attempt()
                return
            self.d.press(self.ctx, x, y)
        elif ev.type == pygame.MOUSEMOTION and not self.finished and self.solved_at is None:
            if ev.buttons[0]:
                self.idle = 0.0
                self.d.move(self.ctx, *ev.pos)
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not self.finished:
            if self.solved_at is None and self.d.release(self.ctx):
                self._attempt()

    def update(self, dt: float) -> None:
        self.ctx.dt = dt
        self.ctx.time += dt
        for fx in (self.shake, self.flash_bad, self.flash_ok, self.blink):
            fx.update(dt)
        self.ok.update(dt)
        self.ctx.hint_alpha = self.blink.alpha
        if self.finished:
            self.end_tween.update(dt)
            return
        self.enter.update(dt)
        self.d.update(self.ctx)
        if self.solved_at is not None:
            self.solved_at += dt
            if self.solved_at >= NEXT_DELAY and not self.audio.busy():
                self._next()
            elif self.solved_at >= NEXT_DELAY * 4:   # never wait forever on a long clip
                self._next()
            return
        self.idle += dt
        if self.idle >= IDLE_AFTER and not self.idle_played:
            self.idle_played = True
            self.audio.play("parado")

    def draw(self, surf) -> None:
        surf.fill(theme.BG)
        w, h = surf.get_size()
        if self.finished:
            self._draw_end(surf, w, h)
            self.back.draw(surf)
            return
        base_ox = self.cam.ox
        self.cam.ox = base_ox + self.shake.offset
        if self.d.plano:
            draw_plane(surf, self.cam, self.d.matriz(), show_basis=True)
        if self.hint:
            self.d.desenhar_dica(surf, self.ctx)
        self.d.desenhar(surf, self.ctx)
        self.cam.ox = base_ox

        # HUD
        pygame.draw.rect(surf, theme.BG, (0, 0, w, HUD_H))
        pygame.draw.line(surf, theme.PANEL_HI, (0, HUD_H), (w, HUD_H), 1)
        self.d.desenhar_alvo(surf, self.ctx)
        self._draw_progress(surf, w)
        if self.d.painel:
            pygame.draw.rect(surf, theme.PANEL, (0, h - PANEL_H, w, PANEL_H))
            self.d.desenhar_painel(surf, self.ctx)
        self.back.draw(surf)
        self.ok.visible = self.d.confirmar and self.solved_at is None
        self.ok.draw(surf)

        self._draw_flash(surf, w, h)
        if self.enter.raw < 1:
            veil = pygame.Surface((w, h), pygame.SRCALPHA)
            veil.fill((*theme.BG, int(255 * (1 - self.enter.value))))
            surf.blit(veil, (0, 0))

    # ---- drawing helpers ----------------------------------------------------------
    def _draw_progress(self, surf, w) -> None:
        n = len(self.aula.desafios)
        gap = 22
        x0 = w - 30 - (n - 1) * gap
        for k in range(n):
            color = theme.OK if k < self.idx or (k == self.idx and self.ctx.solved) else (
                theme.TEXT if k == self.idx else theme.TEXT_DIM)
            draw.circle(surf, color, (x0 + k * gap, 30), 6 if k == self.idx else 4)

    def _draw_flash(self, surf, w, h) -> None:
        for fx, color in ((self.flash_bad, theme.BAD), (self.flash_ok, theme.OK)):
            if fx.active:
                a = int(170 * fx.strength)
                edge = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(edge, (*color, a), (0, 0, w, h), 10)
                surf.blit(edge, (0, 0))
        if self.flash_ok.active:
            r = 30 + 40 * (1 - self.flash_ok.strength)
            c = tuple(int(v * self.flash_ok.strength) for v in theme.OK)
            draw.circle(surf, c, (w / 2, h / 2), r, 4)

    def _draw_end(self, surf, w, h) -> None:
        t = self.end_tween.value
        cx, cy = w / 2, h / 2
        r = 90 * t
        if r > 2:
            draw.circle(surf, theme.OK, (cx, cy), r, 6)
            s = r * 0.45
            draw.line(surf, theme.OK, (cx - s, cy), (cx - s * 0.25, cy + s * 0.7), 8)
            draw.line(surf, theme.OK, (cx - s * 0.25, cy + s * 0.7), (cx + s, cy - s * 0.6), 8)
        draw.text(surf, self.aula.titulo, (cx, cy + 140), 40, theme.TEXT)
