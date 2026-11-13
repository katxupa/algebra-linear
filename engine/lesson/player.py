"""Plays one Aula: runs its challenges, judges attempts, gives audio + visual feedback."""
from __future__ import annotations

import pygame

from .. import theme
from ..challenges.base import Ctx, SUCESSO, ERRO
from ..coords import Camera
from ..narrador import Narrador
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
        self.audio = app.banco(aula)   # shared with the menu, which already preloaded the intro
        self._overlays: dict = {}
        self.back = Button("back", radius=26)
        self.ok = Button("check", theme.OK, radius=34)
        self.shake = Shake()
        self.flash_bad = Effect(0.5)
        self.flash_ok = Effect(1.0)
        self.blink = Blink()
        self.cam = Camera(app.width, app.height)
        self.ctx = Ctx(self.cam, app.width, app.height, HUD_H / 2, 0)
        self.finished = False
        self.narrador = Narrador(self.audio)      # decides when the voice speaks (engine/narrador.py)
        self.ctx.aviso = self._aviso
        self.ctx.som = lambda chave: self.narrador.falar(chave)
        self.idx = -1
        self.narrador.falar("intro")
        self._next()

    # ---- flow ---------------------------------------------------------------------
    def _next(self) -> None:
        self.idx += 1
        if self.idx >= len(self.aula.desafios):
            self.finished = True
            self.end_tween = Tween(0.8)
            self.app.mark_done(self.aula)
            self.narrador.falar("fim")
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
            self.narrador.falar(self.d.audio, forcar=True, interromper=False)
        self.audio.preparar(self._chaves_provaveis())

    def _chaves_provaveis(self) -> list[str]:
        """Clips that may play during this challenge, most likely first."""
        keys = [SUCESSO, ERRO, *self.d.ERROS.keys(), "dica", "parado"]
        nxt = self.idx + 1
        if nxt < len(self.aula.desafios):
            if self.aula.desafios[nxt].audio:
                keys.append(self.aula.desafios[nxt].audio)
        else:
            keys.append("fim")
        return keys

    def _calmo(self) -> bool:
        """Good moment to decode audio: nobody dragging, no feedback animation running."""
        busy_fx = self.flash_ok.active or self.flash_bad.active or self.shake.active
        return not busy_fx and not pygame.mouse.get_pressed()[0]

    def _aviso(self, chave: str) -> None:
        """Instant feedback for an invalid action (not an attempt: no hint counter)."""
        self.shake.start()
        self.flash_bad.start()
        self.narrador.erro(chave)

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
            self.narrador.acerto(self.fails)
            return
        self.fails += 1
        self.shake.start()
        self.flash_bad.start()
        if self.fails >= self.d.dica_apos and not self.hint:
            self.hint = True
            if self.narrador.falar("dica"):
                return
        self.narrador.erro(result)

    # ---- scene interface ----------------------------------------------------------
    def resize(self, w: int, h: int) -> None:
        bottom = self.d.altura_painel(w) if (not self.finished and self.d.painel) else 0
        self.cam.top_margin, self.cam.bottom_margin = HUD_H, bottom
        self.cam.resize(w, h)
        self.ctx.width, self.ctx.height = w, h
        self.ctx.hud_y = HUD_H / 2 + 6
        self.ctx.bottom_y = h - (self.d.altura_painel(w) if not self.finished else PANEL_H) / 2
        self.back.place(40, 40)
        self.ok.place(w - 60, h - 60 - bottom)
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
        elif ev.type in (pygame.KEYDOWN, pygame.TEXTINPUT) and not self.finished and self.solved_at is None:
            self.idle = 0.0
            self.d.tecla(self.ctx, ev)
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
        self.narrador.tick(dt)
        if self._calmo():
            self.audio.carregar_um()      # preload one upcoming clip per calm frame
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
            self.narrador.falar("parado", forcar=True)

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
            draw_plane(surf, self.cam, self.d.matriz(), show_basis=self.d.base)
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
            ph = self.d.altura_painel(w)
            pygame.draw.rect(surf, theme.PANEL, (0, h - ph, w, ph))
            self.d.desenhar_painel(surf, self.ctx)
        self.back.draw(surf)
        self.ok.visible = self.d.confirmar and self.solved_at is None
        self.ok.draw(surf)

        self._draw_flash(surf, w, h)
        if self.enter.raw < 1:
            veil = self._overlay("veil", w, h)
            veil.set_alpha(int(255 * (1 - self.enter.value)))
            surf.blit(veil, (0, 0))

    # ---- drawing helpers ----------------------------------------------------------
    def _draw_progress(self, surf, w) -> None:
        n = len(self.aula.desafios)
        gap = max(8, min(22, (w - 130) / max(1, n - 1)))
        x0 = w - 30 - (n - 1) * gap
        for k in range(n):
            color = theme.OK if k < self.idx or (k == self.idx and self.ctx.solved) else (
                theme.TEXT if k == self.idx else theme.TEXT_DIM)
            draw.circle(surf, color, (x0 + k * gap, 30), (6 if k == self.idx else 4) if gap >= 14 else (4 if k == self.idx else 3))

    def _draw_flash(self, surf, w, h) -> None:
        for fx, name in ((self.flash_bad, "bad"), (self.flash_ok, "ok")):
            if fx.active:
                edge = self._overlay(name, w, h)
                edge.set_alpha(int(170 * fx.strength))
                surf.blit(edge, (0, 0))
        if self.flash_ok.active:
            r = 30 + 40 * (1 - self.flash_ok.strength)
            c = tuple(int(v * self.flash_ok.strength) for v in theme.OK)
            draw.circle(surf, c, (w / 2, h / 2), r, 4)

    def _overlay(self, name: str, w: int, h: int) -> pygame.Surface:
        """Full-screen overlay surfaces, built once per screen size (not every frame)."""
        key = (name, w, h)
        s = self._overlays.get(key)
        if s is None:
            if name == "veil":
                s = pygame.Surface((w, h))
                s.fill(theme.BG)
            else:
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                color = theme.BAD if name == "bad" else theme.OK
                pygame.draw.rect(s, (*color, 255), (0, 0, w, h), 10)
            self._overlays[key] = s
        return s

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
