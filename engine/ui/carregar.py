"""Loading screen: decodes audio clips before they are needed, with a progress bar.

Decoding an OGG in the browser takes a noticeable moment on a phone. Doing it here, once, means
the game never freezes later to decode a clip, and every clip starts instantly.
"""
from __future__ import annotations

import time

import pygame

from .. import audio, theme
from ..scene import draw
from ..textos import t

FATIA = 0.03     # seconds of decoding per frame, so the progress bar keeps moving


class Carregar:
    def __init__(self, app, caminhos, depois):
        self.app = app
        self.falta = [p for p in dict.fromkeys(caminhos) if not audio.carregado(p)]
        self.total = max(1, len(self.falta))
        self.depois = depois          # called when everything is loaded (opens the next scene)
        self.quadros = 0
        self.inicio = None

    @property
    def vazio(self) -> bool:
        return not self.falta

    def handle_event(self, ev) -> None:
        pass

    def resize(self, w: int, h: int) -> None:
        pass

    def update(self, dt: float) -> None:
        self.quadros += 1
        if self.quadros < 2:          # show the screen first, then start the slow part
            return
        inicio = time.perf_counter()
        self.inicio = self.inicio or inicio
        while self.falta and time.perf_counter() - inicio < FATIA:
            audio.carregar(self.falta.pop(0))
        if not self.falta:
            # one line in the console (browser: F12) to see how long the phone took
            print(f"sons preparados: {self.total} em {time.perf_counter() - self.inicio:.1f} s")
            self.depois()

    def draw(self, surf) -> None:
        surf.fill(theme.BG)
        w, h = surf.get_size()
        feito = 1 - len(self.falta) / self.total
        largura = min(320, w - 60)
        barra = pygame.Rect(0, 0, largura, 10)
        barra.center = (w // 2, h // 2 + 30)
        pygame.draw.rect(surf, theme.PANEL_HI, barra, border_radius=5)
        if feito > 0:
            pygame.draw.rect(surf, theme.OK, (barra.x, barra.y, max(10, int(largura * feito)), 10), border_radius=5)
        draw.text(surf, t("a_preparar_sons"), (w / 2, h / 2 - 10), 30, theme.TEXT_DIM)
