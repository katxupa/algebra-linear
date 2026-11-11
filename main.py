"""Algebra Linear: interactive lessons.

Desktop:  python main.py            (menu)
          python main.py --aula 2   (jump straight into aula 2)
Web:      pygbag .                  (then open http://localhost:8000)
"""
import asyncio
import os
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: F401  (pygbag scans main.py imports to know it must load pygame)

from engine.app import App


def _start_aula():
    if "--aula" in sys.argv:
        try:
            return int(sys.argv[sys.argv.index("--aula") + 1])
        except (IndexError, ValueError):
            pass
    return None


async def main():
    await App(start_aula=_start_aula()).run()


asyncio.run(main())
