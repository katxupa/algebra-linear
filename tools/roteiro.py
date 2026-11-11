"""Narrator checklist: which audio clips an aula can use, and which are already recorded.

    python tools/roteiro.py aula_1            -> prints + writes aulas/aula_1/audio/ROTEIRO.md
    python tools/roteiro.py aula_1 --convert  -> also converts .wav/.mp3 in that folder to .ogg

Clips are optional: a missing key is silent (mistake keys fall back to `erro`).
Record many short variants: sucesso_1.ogg, sucesso_2.ogg, ... (random pick).
Clips in aulas/_audio/ are shared by every aula; a clip in aula_N/audio/ overrides it.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from engine.audio import scan                       # noqa: E402
from engine.lesson.loader import AULAS_DIR, SHARED_AUDIO, load_aula  # noqa: E402

GERAIS = {
    "intro": "começo da aula",
    "sucesso": "acertou um desafio (grave várias variações curtas!)",
    "erro": "errou (genérico, quando não é um erro conhecido)",
    "dica": f"errou várias vezes seguidas: aparece uma dica visual",
    "parado": "ficou 20s sem mexer em nada",
    "fim": "terminou a aula",
}


def build(nome: str) -> str:
    numero = int(nome.split("_")[1])
    pasta = os.path.join(AULAS_DIR, nome)
    aula = load_aula(pasta, numero)
    if aula.erro:
        raise SystemExit(f"lesson.py com erro:\n{aula.erro}")
    local = scan(os.path.join(pasta, "audio"))
    shared = scan(SHARED_AUDIO)

    def status(key: str) -> str:
        if key in local:
            return f"✅ {len(local[key])} na aula"
        if key in shared:
            return f"☑️ {len(shared[key])} compartilhado(s)"
        return "⬜ falta"

    lines = [f"# Roteiro de áudio: {nome} ({aula.titulo})", "",
             "Grave em .ogg (ou .wav e rode com `--convert`). Variações: `chave_1.ogg`, `chave_2.ogg`...", "",
             "## Gerais", "", "| chave | quando toca | status |", "|---|---|---|"]
    for key, why in GERAIS.items():
        lines.append(f"| `{key}` | {why} | {status(key)} |")

    # each mistake key once, with the challenges (by number) that can trigger it
    erros: dict[str, tuple[str, list[int]]] = {}
    intros: list[tuple[int, str]] = []
    for k, d in enumerate(aula.desafios, 1):
        if d.audio:
            intros.append((k, d.audio))
        for key, why in d.ERROS.items():
            erros.setdefault(key, (why, []))[1].append(k)

    lines += ["", "## Erros conhecidos (se faltar, toca `erro`)", "",
              "| chave | quando toca | desafios | status |", "|---|---|---|---|"]
    for key, (why, nums) in erros.items():
        lines.append(f"| `{key}` | {why} | {', '.join(map(str, nums))} | {status(key)} |")

    if intros:
        lines += ["", "## Início de desafio (`audio=`)", "", "| chave | desafio | status |", "|---|---|---|"]
        for k, key in intros:
            lines.append(f"| `{key}` | {k} | {status(key)} |")

    lines += ["", "## Desafios", ""]
    lines += [f"{k}. {d.descricao()}" for k, d in enumerate(aula.desafios, 1)]
    return "\n".join(lines)


def convert(pasta: str) -> None:
    """.wav / .mp3 / .flac -> .ogg (the web version only plays .ogg). Originals are removed."""
    import soundfile as sf
    from audio_io import write_audio
    for name in os.listdir(pasta):
        stem, ext = os.path.splitext(name)
        if ext.lower() in (".wav", ".mp3", ".flac"):
            src, dst = os.path.join(pasta, name), os.path.join(pasta, stem + ".ogg")
            data, rate = sf.read(src, dtype="float32")
            write_audio(dst, data, rate)
            os.remove(src)
            print(f"convertido: {name} -> {stem}.ogg")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    nome = args[0]
    audio_dir = os.path.join(AULAS_DIR, nome, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    if "--convert" in sys.argv:
        convert(audio_dir)
    text = build(nome)
    with open(os.path.join(audio_dir, "ROTEIRO.md"), "w", encoding="utf-8") as f:
        f.write(text + "\n")
    sys.stdout.reconfigure(encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
