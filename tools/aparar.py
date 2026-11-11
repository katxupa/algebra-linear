"""Cuts the silence at the start and end of the narrator's recordings.

    python tools/aparar.py            -> every .ogg/.wav in aulas/ (all aulas + _audio)
    python tools/aparar.py aula_1     -> only that aula

The originals are copied first to gravacoes_originais/ (same folder structure), so nothing is lost.
Files that are already trimmed are left alone, so it is safe to run again after each recording session.
"""
from __future__ import annotations

import os
import shutil
import sys

import numpy as np
import soundfile as sf

from audio_io import write_audio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AULAS = os.path.join(ROOT, "aulas")
BACKUP = os.path.join(ROOT, "gravacoes_originais")

LIMIAR = 0.03      # "silence" = quieter than 3% of the loudest point of the clip
MARGEM = 0.08      # seconds of silence kept at each end, so words are not cut
MINIMO = 0.15      # only trim if there is more silence than this at one of the ends


def aparar(path: str) -> str | None:
    data, rate = sf.read(path, dtype="float32", always_2d=True)
    if len(data) == 0:
        return None
    level = np.abs(data).max(axis=1)
    if level.max() == 0:
        return None
    loud = np.where(level > level.max() * LIMIAR)[0]
    start, end = loud[0], loud[-1] + 1
    before, after = start / rate, (len(data) - end) / rate
    if before <= MINIMO and after <= MINIMO:
        return None

    rel = os.path.relpath(path, AULAS)
    backup = os.path.join(BACKUP, rel)
    # only untrimmed files get here, so this is the latest original (also after re-recording a clip)
    os.makedirs(os.path.dirname(backup), exist_ok=True)
    shutil.copy2(path, backup)

    pad = int(MARGEM * rate)
    a, b = max(0, start - pad), min(len(data), end + pad)
    clip = data[a:b].copy()
    fade = min(pad, len(clip) // 4)
    if fade:
        ramp = np.linspace(0, 1, fade, dtype="float32")[:, None]
        clip[:fade] *= ramp
        clip[-fade:] *= ramp[::-1]
    # write to a temporary file, check it really has the sound, only then replace the recording
    is_ogg = path.lower().endswith(".ogg")
    tmp = path + ".tmp"
    write_audio(tmp, clip, rate, "OGG" if is_ogg else "WAV")
    check, _ = sf.read(tmp, dtype="float32", always_2d=True)
    if abs(len(check) - len(clip)) > rate * 0.05:
        os.remove(tmp)
        raise RuntimeError(f"{rel}: a gravação aparada saiu errada; o original ficou intacto")
    os.replace(tmp, path)
    return f"{rel}: -{before:.2f}s no início, -{after:.2f}s no fim ({len(data) / rate:.1f}s -> {len(clip) / rate:.1f}s)"


def main() -> None:
    base = os.path.join(AULAS, sys.argv[1]) if len(sys.argv) > 1 else AULAS
    sys.stdout.reconfigure(encoding="utf-8")
    changed = 0
    for folder, _, files in os.walk(base):
        for name in sorted(files):
            if name.lower().endswith((".ogg", ".wav")):
                msg = aparar(os.path.join(folder, name))
                if msg:
                    changed += 1
                    print("aparado:", msg)
    print(f"{changed} ficheiro(s) aparado(s). Originais em gravacoes_originais/" if changed else "Nada para aparar.")


if __name__ == "__main__":
    main()
