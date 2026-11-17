"""Main loop (async so the same code runs on desktop and in the browser via pygbag)."""
from __future__ import annotations

import asyncio
import os
import sys

import pygame

from . import progress
from .audio import AudioBank, ficheiros, init_mixer
from .lesson.loader import SHARED_AUDIO, discover
from .lesson.player import LessonPlayer
from .ui.carregar import Carregar
from .ui.menu import Menu

WEB = sys.platform == "emscripten"
FPS = 60
VER_TAMANHO = 0.5        # web: seconds between checks of the browser size (rotation, resize)
MINIMO = (360, 600)      # never smaller than this: a phone lying down gets a taller canvas, scaled to fit


def tamanho_navegador(padrao):
    """Web: the visible size of the page in CSS pixels, so the game fills the phone screen in
    portrait as well as in landscape. Desktop: `padrao`."""
    if not WEB:
        return padrao
    try:
        import platform  # pygbag exposes the browser window here
        w, h = int(platform.window.innerWidth), int(platform.window.innerHeight)
    except Exception:
        return padrao
    if w <= 0 or h <= 0:
        return padrao
    k = max(1.0, MINIMO[0] / w, MINIMO[1] / h)
    return int(w * k), int(h * k)


def _reajustar_canvas():
    """Ask pygbag to fit the canvas to the page again (it keeps the canvas aspect ratio)."""
    try:
        import platform
        platform.window.window_resize()
    except Exception:
        pass


class App:
    def __init__(self, size=(1024, 720), start_aula: int | None = None):
        pygame.init()
        flags = 0 if WEB else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(tamanho_navegador(size), flags)
        self._ver_tamanho = 0.0
        pygame.display.set_caption("Álgebra Linear")
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.aulas = discover()
        self.done = progress.load()
        self.running = True
        self.bancos: dict[str, AudioBank] = {}

        # on the web, pygbag's "toque na tela" page already got the tap that unlocks audio
        self.start_audio()
        match = [a for a in self.aulas if a.numero == start_aula and not a.erro and not a.em_breve]
        depois = (lambda: self.open_aula(match[0])) if match else self.open_menu
        # the clips every aula uses (success, mistakes, streaks...) are decoded once, right now
        self._carregar(ficheiros(SHARED_AUDIO), depois)

    # ---- navigation ---------------------------------------------------------------
    def start_audio(self) -> None:
        init_mixer()

    def banco(self, aula) -> AudioBank:
        """One audio bank per aula, kept for the whole session (preloaded clips stay ready)."""
        if aula.id not in self.bancos:
            self.bancos[aula.id] = AudioBank(aula.audio_dirs)
        return self.bancos[aula.id]

    def open_menu(self) -> None:
        self.scene = Menu(self)

    def open_aula(self, aula) -> None:
        # this aula's own clips (intro, its mistakes...) are decoded before it starts
        pasta = os.path.join(aula.pasta, "audio")
        self._carregar(ficheiros(pasta), lambda: setattr(self, "scene", LessonPlayer(self, aula)))

    def _carregar(self, caminhos, depois) -> None:
        tela = Carregar(self, caminhos if AudioBank.enabled else [], depois)
        if tela.vazio:
            depois()
        else:
            self.scene = tela

    def mark_done(self, aula) -> None:
        self.done.add(aula.id)
        progress.save(self.done)

    # ---- loop ---------------------------------------------------------------------
    def _handle(self, ev) -> None:
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
            if isinstance(self.scene, Menu):
                self.running = WEB  # Esc quits on desktop, never on the web
            else:
                self.open_menu()
        elif ev.type == pygame.VIDEORESIZE and not WEB:
            self.width, self.height = ev.w, ev.h
            self.scene.resize(self.width, self.height)
        else:
            self.scene.handle_event(ev)

    def _seguir_navegador(self, dt: float) -> None:
        """Web: when the phone rotates (or the window changes), the game takes the new shape."""
        self._ver_tamanho += dt
        if not WEB or self._ver_tamanho < VER_TAMANHO:
            return
        self._ver_tamanho = 0.0
        novo = tamanho_navegador(self.screen.get_size())
        if novo != self.screen.get_size():
            self.screen = pygame.display.set_mode(novo)
            _reajustar_canvas()

    async def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for ev in pygame.event.get():
                self._handle(ev)
            self._seguir_navegador(dt)
            size = self.screen.get_size()
            if size != (self.width, self.height):
                self.width, self.height = size
                self.scene.resize(*size)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()
