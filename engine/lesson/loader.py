"""Finds lessons: every `aulas/aula_<N>/lesson.py` becomes an Aula, sorted by N.

A lesson file only needs:
    from engine import *
    titulo = "..."
    desafios = [ ... ]
Errors in a lesson never crash the game: the Aula is marked broken and shown in the menu.
"""
from __future__ import annotations

import importlib.util
import os
import re
import traceback
from dataclasses import dataclass, field

from ..challenges.base import Desafio

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AULAS_DIR = os.path.join(ROOT, "aulas")
SHARED_AUDIO = os.path.join(AULAS_DIR, "_audio")
_NAME = re.compile(r"^aula_(\d+)$")


@dataclass
class Aula:
    numero: int
    pasta: str
    titulo: str = ""
    desafios: list[Desafio] = field(default_factory=list)
    erro: str | None = None

    @property
    def id(self) -> str:
        return f"aula_{self.numero}"

    @property
    def audio_dirs(self) -> list[str]:
        return [os.path.join(self.pasta, "audio"), SHARED_AUDIO]


def load_aula(pasta: str, numero: int) -> Aula:
    aula = Aula(numero=numero, pasta=pasta, titulo=f"Aula {numero}")
    path = os.path.join(pasta, "lesson.py")
    try:
        spec = importlib.util.spec_from_file_location(f"aulas_aula_{numero}_lesson", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        aula.titulo = str(getattr(mod, "titulo", aula.titulo))
        desafios = getattr(mod, "desafios", None)
        if not isinstance(desafios, (list, tuple)) or not desafios:
            raise ValueError("lesson.py precisa de uma lista `desafios = [...]` não vazia")
        bad = [d for d in desafios if not isinstance(d, Desafio)]
        if bad:
            raise TypeError(f"item de `desafios` não é um desafio: {bad[0]!r}")
        aula.desafios = list(desafios)
        for d in aula.desafios:   # catch setup errors now, not mid-game
            d.iniciar()
    except Exception:
        aula.erro = traceback.format_exc(limit=3)
    return aula


def discover(base: str = AULAS_DIR) -> list[Aula]:
    aulas = []
    if not os.path.isdir(base):
        return aulas
    for name in os.listdir(base):
        m = _NAME.match(name)
        pasta = os.path.join(base, name)
        if m and os.path.isfile(os.path.join(pasta, "lesson.py")):
            aulas.append(load_aula(pasta, int(m.group(1))))
    return sorted(aulas, key=lambda a: a.numero)
