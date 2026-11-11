"""Narrator audio: short clips played by event key, preloaded before they are needed.

Files are named `<key>.ogg` or `<key>_<n>.ogg` (variants, picked at random, never the
same twice in a row). `.wav` also works. Folders are searched in order; the first folder
that has a key wins (so an aula can override the shared clips in aulas/_audio).

Preloading: for every key that may play soon, the bank already picks WHICH variant will
play next and decodes it in the background of the game loop (one clip per frame, only in
calm moments). When the event happens the clip is already in memory and starts instantly;
right after it plays, the following variant is picked and queued.
"""
from __future__ import annotations

import os
import random
import re
from collections import deque

import pygame

EXTS = (".ogg", ".wav", ".mp3")
_SOUNDS: dict = {}   # path -> decoded Sound, shared by every aula (aulas/_audio clips are decoded once)
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
        self._cache = _SOUNDS
        self._last: dict[str, str] = {}
        self._next: dict[str, str] = {}             # key -> variant that will play next
        self._queue: deque[str] = deque()
        self._channel = None

    def has(self, key: str) -> bool:
        return key in self.files

    # ---- preloading ------------------------------------------------------------------
    def _pick_next(self, key: str) -> str | None:
        if key not in self._next:
            paths = self.files.get(key)
            if not paths:
                return None
            choices = [p for p in paths if p != self._last.get(key)] or paths
            self._next[key] = random.choice(choices)
        return self._next[key]

    def preparar(self, keys) -> None:
        """Queue the next variant of each key for loading (most important keys first)."""
        if not AudioBank.enabled:
            return
        for key in keys:
            path = self._pick_next(key)
            if path and path not in self._cache and path not in self._queue:
                self._queue.append(path)

    def carregar_um(self) -> bool:
        """Decode one queued clip. Call once per frame in calm moments. False when idle."""
        while self._queue:
            path = self._queue.popleft()
            if path not in self._cache:
                self._load(path)
                return True
        return False

    def pendentes(self) -> int:
        return len(self._queue)

    def _load(self, path: str):
        snd = self._cache.get(path)
        if snd is None and pygame.mixer.get_init():
            try:
                snd = self._cache[path] = pygame.mixer.Sound(path)
            except pygame.error:
                snd = None
        return snd

    # ---- playing -----------------------------------------------------------------------
    def play(self, key: str, interrupt: bool = True) -> bool:
        """Play a clip for `key`. Returns False if there is no clip (silent)."""
        if not AudioBank.enabled or not pygame.mixer.get_init():
            return False
        path = self._pick_next(key)
        if not path:
            return False
        del self._next[key]
        self._last[key] = path
        snd = self._load(path)          # instant if it was preloaded
        if snd is None:
            return False
        if interrupt:
            self.stop()
        self._channel = snd.play()
        self.preparar([key])            # get the following variant ready
        return True

    def busy(self) -> bool:
        return bool(self._channel and self._channel.get_busy())

    def stop(self) -> None:
        if self._channel:
            self._channel.stop()


def init_mixer() -> None:
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)   # same rate as the recordings: no resampling
        pygame.mixer.init()
    except pygame.error:
        AudioBank.enabled = False  # no audio device: game still works, silently
