"""Remembers finished aulas: JSON file on desktop, browser localStorage on the web."""
from __future__ import annotations

import json
import os
import sys

_KEY = "algebra_linear_progress"
_FILE = os.path.join(os.path.expanduser("~"), ".algebra_linear", "progress.json")
WEB = sys.platform == "emscripten"


def load() -> set[str]:
    try:
        if WEB:
            import platform  # pygbag exposes the browser window here
            raw = platform.window.localStorage.getItem(_KEY)
        else:
            with open(_FILE, encoding="utf-8") as f:
                raw = f.read()
        return set(json.loads(raw or "[]"))
    except Exception:
        return set()


def save(done: set[str]) -> None:
    raw = json.dumps(sorted(done))
    try:
        if WEB:
            import platform
            platform.window.localStorage.setItem(_KEY, raw)
        else:
            os.makedirs(os.path.dirname(_FILE), exist_ok=True)
            with open(_FILE, "w", encoding="utf-8") as f:
                f.write(raw)
    except Exception:
        pass
