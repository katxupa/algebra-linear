"""One screenshot of every exercise of every aula, to see what is inside without playing them all.

    python tools/capturas.py                 -> capturas/ (ignored by git and by the web build)
    python tools/capturas.py --tamanho 420x860   phone size
    python tools/capturas.py --pasta outra       another folder (e.g. to compare before / after a change)

Writes <pasta>/aula_NN_<título>/NN_<descrição>.png and <pasta>/index.html to browse them all.
The answer tiles are shuffled with a fixed seed, so two runs of the same code give the same images.
"""
import argparse
import html
import os
import random
import re
import shutil
import sys
import unicodedata

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import pygame  # noqa: E402

from engine.app import App  # noqa: E402
from engine.lesson.player import LessonPlayer  # noqa: E402

PASTA_PADRAO = os.path.join(ROOT, "capturas")


def nome_ficheiro(s: str, maximo: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()
    return s[:maximo] or "desafio"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tamanho", default="1024x720", help="largura x altura do ecrã, ex: 420x860")
    ap.add_argument("--pasta", default=PASTA_PADRAO, help="onde guardar (é apagada e criada de novo)")
    args = ap.parse_args()
    w, h = (int(v) for v in args.tamanho.lower().split("x"))
    pasta = os.path.abspath(args.pasta)
    if os.path.normcase(pasta) in (os.path.normcase(ROOT), os.path.normcase(os.path.dirname(ROOT))):
        sys.exit("--pasta não pode ser o projeto nem a pasta de cima: ela é apagada antes de começar")

    if os.path.isdir(pasta):
        shutil.rmtree(pasta)
    os.makedirs(pasta)

    app = App(size=(w, h))
    app.screen = pygame.display.set_mode((w, h))
    app.width, app.height = w, h
    seccoes = []
    total = 0
    for aula in app.aulas:
        if aula.erro or aula.em_breve:
            continue
        sub = f"aula_{aula.numero:02d}_{nome_ficheiro(aula.titulo, 30)}"
        os.makedirs(os.path.join(pasta, sub))
        itens = []
        for k, d in enumerate(aula.desafios):
            p = LessonPlayer(app, aula)
            app.scene = p
            p.audio.stop()
            p.idx = k - 1
            random.seed(1000 * aula.numero + k)   # same tile order on every run
            p._next()
            for _ in range(45):            # let the entry fade and the animations settle
                p.update(1 / 60)
            p.draw(app.screen)
            ficheiro = f"{k + 1:02d}_{nome_ficheiro(p.d.descricao())}.png"
            pygame.image.save(app.screen, os.path.join(pasta, sub, ficheiro))
            itens.append((f"{sub}/{ficheiro}", f"{k + 1}. {p.d.descricao()}", type(p.d).__name__))
            total += 1
        seccoes.append((f"Aula {aula.numero}: {aula.titulo}", itens))
        print(f"aula {aula.numero:2d} {aula.titulo}: {len(itens)} capturas")

    partes = []
    for titulo, itens in seccoes:
        cartoes = "".join(
            f'<figure><a href="{html.escape(src)}"><img src="{html.escape(src)}" loading="lazy"></a>'
            f'<figcaption>{html.escape(txt)} <span>{html.escape(tipo)}</span></figcaption></figure>'
            for src, txt, tipo in itens)
        partes.append(f"<h2>{html.escape(titulo)}</h2><div class=grelha>{cartoes}</div>")
    with open(os.path.join(pasta, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!doctype html><meta charset=utf-8><title>Capturas das aulas</title>
<style>
body{{background:#000;color:#e6e8f0;font-family:system-ui,sans-serif;margin:24px}}
h1{{font-size:22px}} h2{{font-size:18px;margin-top:36px;color:#fad23c}}
.grelha{{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}}
figure{{margin:0}} img{{width:100%;border:1px solid #2c344c;border-radius:8px}}
figcaption{{font-size:14px;margin-top:4px}} figcaption span{{color:#82889b;font-size:12px}}
</style>
<h1>Capturas das aulas ({total} exercícios, {w}×{h})</h1>
{''.join(partes)}
""")
    print(f"{total} capturas em {pasta}")


if __name__ == "__main__":
    main()
