"""Main loop (async so the same code runs on desktop and in the browser via pygbag)."""
from __future__ import annotations

import asyncio
import sys

import pygame

from . import progress
from .audio import AudioBank, init_mixer
from .lesson.loader import discover
from .lesson.player import LessonPlayer
from .ui.menu import Menu

WEB = sys.platform == "emscripten"
FPS = 60


class App:
    def __init__(self, size=(1024, 720), start_aula: int | None = None):
        pygame.init()
        flags = 0 if WEB else pygame.RESIZABLE
        self.screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Álgebra Linear")
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        self.aulas = discover()
        self.done = progress.load()
        self.running = True
        self.bancos: dict[str, AudioBank] = {}

        # on the web, pygbag's "toque na tela" page already got the tap that unlocks audio
        self.start_audio()
        self.open_menu()
        if start_aula is not None:
            match = [a for a in self.aulas if a.numero == start_aula and not a.erro]
            if match:
                self.open_aula(match[0])

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
        self.scene = LessonPlayer(self, aula)

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

    async def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            for ev in pygame.event.get():
                self._handle(ev)
            size = self.screen.get_size()
            if size != (self.width, self.height):
                self.width, self.height = size
                self.scene.resize(*size)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()
