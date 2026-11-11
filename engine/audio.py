"""Narrator audio: short clips played by event key.

Files are named `<key>.ogg` or `<key>_<n>.ogg` (variants, picked at random, never the
same twice in a row). `.wav` also works. Folders are searched in order; the first folder
that has a key wins (so an aula can override the shared clips in aulas/_audio).
"""
from __future__ import annotations

import os
import random
import re

import pygame

EXTS = (".ogg", ".wav", ".mp3")
_VARIANT = re.compile(r"^(.*?)(?:_(\d+))?$")


def key_of(filename: str) -> str | None:
    stem, ext = os.path.splitext(filename)
    if ext.lower() not in EXTS:
        return None
    return _VARIANT.match(stem).group(1)


def scan(folder: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    if folder and os.path.isdir(folder):
        for name in sorted(os.listdir(folder)):
            key = key_of(name)
            if key:
                found.setdefault(key, []).append(os.path.join(folder, name))
    return found


class AudioBank:
    enabled = True

    def __init__(self, folders: list[str]):
        self.files: dict[str, list[str]] = {}
        for folder in folders:
            for key, paths in scan(folder).items():
                self.files.setdefault(key, paths)   # earlier folder wins
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self._last: dict[str, str] = {}
        self._channel = None

    def has(self, key: str) -> bool:
        return key in self.files

    def play(self, key: str, interrupt: bool = True) -> bool:
        """Play a clip for `key`. Returns False if there is no clip (silent)."""
        paths = self.files.get(key)
        if not paths or not AudioBank.enabled or not pygame.mixer.get_init():
            return False
        choices = [p for p in paths if p != self._last.get(key)] or paths
        path = random.choice(choices)
        self._last[key] = path
        try:
            snd = self._cache.get(path)
            if snd is None:
                snd = self._cache[path] = pygame.mixer.Sound(path)
            if interrupt:
                self.stop()
            self._channel = snd.play()
            return True
        except pygame.error:
            return False

    def busy(self) -> bool:
        return bool(self._channel and self._channel.get_busy())

    def stop(self) -> None:
        if self._channel:
            self._channel.stop()


def init_mixer() -> None:
    try:
        pygame.mixer.init()
    except pygame.error:
        AudioBank.enabled = False  # no audio device: game still works, silently
