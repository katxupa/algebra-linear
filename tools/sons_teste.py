"""Generates placeholder beeps in aulas/_audio/ so feedback can be heard before real recordings.

    python tools/sons_teste.py

The beeps use the real keys (sucesso.ogg, erro.ogg, ...). A real clip with the same key in
aula_N/audio/ overrides them; when you record the shared version, delete the beep in aulas/_audio/.
"""
import math
import os

import numpy as np
from audio_io import write_audio

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "aulas", "_audio")
RATE = 22050


def tone(notes, path):
    parts = []
    for freq, dur in notes:
        n = int(RATE * dur)
        i = np.arange(n)
        env = np.minimum(1.0, np.minimum(i / 200, (n - i) / 400))
        parts.append(0.35 * env * np.sin(2 * math.pi * freq * i / RATE) if freq else np.zeros(n))
    write_audio(path, np.concatenate(parts).astype("float32"), RATE)


SOUNDS = {
    "sucesso": [(660, 0.09), (880, 0.09), (1320, 0.16)],
    "erro": [(220, 0.12), (180, 0.18)],
    "dica": [(520, 0.08), (0, 0.05), (520, 0.08), (0, 0.05), (700, 0.12)],
    "intro": [(440, 0.1), (550, 0.1), (660, 0.15)],
    "fim": [(523, 0.12), (659, 0.12), (784, 0.12), (1046, 0.3)],
    "parado": [(400, 0.1), (0, 0.1), (400, 0.1)],
}

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for key, notes in SOUNDS.items():
        tone(notes, os.path.join(OUT, f"{key}.ogg"))
        print("ok", key)
