import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from engine import MoverVetor, SomarVetores, Escalar, MoverBase, EditarMatriz, Determinante
from engine.audio import key_of
from engine.coords import Camera
from engine.lesson.loader import discover
from engine.linalg import Mat2, Vec2


# ---- linalg / coords ----------------------------------------------------------------

def test_mat2_basics():
    m = Mat2.of([[2, 1], [0, 3]])
    assert m.i == Vec2(2, 0) and m.j == Vec2(1, 3)
    assert m.apply((1, 1)) == Vec2(3, 3)
    assert m.det() == 6
    assert (m @ m.inverse()).close(Mat2.identity())
    assert Mat2.identity().lerp(m, 0).close(Mat2.identity())
    assert Mat2.identity().lerp(m, 1).close(m)


def test_camera_roundtrip():
    cam = Camera(800, 600, top_margin=100)
    for p in [(0, 0), (3, -2), (-4.5, 1.25)]:
        assert cam.to_world(*cam.to_screen(p)).close(p)


def test_audio_keys():
    assert key_of("sucesso.ogg") == "sucesso"
    assert key_of("sucesso_3.ogg") == "sucesso"
    assert key_of("trocou_xy.wav") == "trocou_xy"
    assert key_of("ROTEIRO.md") is None


# ---- attempt evaluation --------------------------------------------------------------

def place(d, *points):
    d.iniciar()
    for h, p in zip(d.handles, points):
        h.pos = Vec2.of(p)
    return d.avaliar()


@pytest.mark.parametrize("pos,expected", [
    ((3, 2), "sucesso"), ((2, 3), "trocou_xy"), ((-3, 2), "sinal"), ((3, 1), "quase"), ((-1, -4), "erro"),
])
def test_mover_vetor(pos, expected):
    assert place(MoverVetor(para=(3, 2)), pos) == expected


def test_somar_vetores():
    d = SomarVetores((2, 1), (1, 2))
    assert place(d, (2, 1)) == "sucesso"
    assert place(d, (1, -1)) == "ao_contrario"     # tip of w on tip of v
    assert place(d, (-4, -4)) == "erro"


def test_escalar():
    d = Escalar((1, 2), por=2)
    assert place(d, (2, 4)) == "sucesso"
    assert place(d, (-2, -4)) == "sinal"
    assert place(d, (3, 6)) == "paralelo"


def test_mover_base():
    d = MoverBase(matriz=[[1, 1], [0, 1]])
    assert place(d, (1, 0), (1, 1)) == "sucesso"
    assert place(d, (1, 1), (0, 1)) == "transposta"
    d = MoverBase(matriz=[[2, -1], [1, 2]])
    assert place(d, (-1, 2), (2, 1)) == "trocou_base"


def test_editar_matriz():
    d = EditarMatriz(alvo=[[1, 2], [0, 1]])
    d.iniciar()
    d.editor.values = [[1, 2], [0, 1]]
    assert d.avaliar() == "sucesso"
    d.editor.values = [[1, 0], [2, 1]]
    assert d.avaliar() == "transposta"


def test_determinante():
    d = Determinante(area=2)
    assert place(d, (2, 0), (0, 1)) == "sucesso"
    assert place(d, (0, 1), (2, 0)) == "orientacao"
    assert place(d, (1, 1), (2, 2)) == "zero"


# ---- lessons ----------------------------------------------------------------------------

def test_discover_real_aulas():
    aulas = discover()
    assert [a.numero for a in aulas][:2] == [1, 2]
    for a in aulas:
        assert a.erro is None, a.erro


def test_broken_lesson_is_isolated(tmp_path):
    for n, body in [(1, "from engine import *\ntitulo='ok'\ndesafios=[MoverVetor(para=(1,2))]"),
                    (10, "this is not python"),
                    (2, "titulo='sem desafios'")]:
        p = tmp_path / f"aula_{n}"
        p.mkdir()
        (p / "lesson.py").write_text(body, encoding="utf-8")
    aulas = discover(str(tmp_path))
    assert [a.numero for a in aulas] == [1, 2, 10]      # numeric order, not text order
    assert aulas[0].erro is None
    assert aulas[1].erro and aulas[2].erro


# ---- corpo (field axioms) -------------------------------------------------------------------

from fractions import Fraction

from engine import Neutro, Simetrico, Inverso, Comutativa, Associativa, Distributiva
from engine.challenges.corpo import NAO_EXISTE


def pick(d, value):
    d.iniciar()
    d.sel = value
    return d.avaliar()


def test_corpo_answers_and_mistakes():
    assert pick(Neutro("+"), 0) == "sucesso"
    assert pick(Neutro("+"), 1) == "neutro_trocado"
    assert pick(Neutro("·"), 1) == "sucesso"
    assert pick(Simetrico(5), -5) == "sucesso"
    assert pick(Simetrico(5), Fraction(1, 5)) == "simetrico_inverso"
    assert pick(Inverso(5), Fraction(1, 5)) == "sucesso"
    assert pick(Inverso(5), -5) == "simetrico_inverso"
    assert pick(Inverso(0), NAO_EXISTE) == "sucesso"
    assert pick(Inverso(0), 0) == "dividir_por_zero"
    assert pick(Comutativa(3, 4), 3) == "sucesso"
    assert pick(Comutativa(3, 4), 4) == "comutatividade"
    assert pick(Associativa(2, 3, 4), 4) == "sucesso"
    assert pick(Distributiva(2, 3, 4), 8) == "sucesso"
    assert pick(Distributiva(2, 3, 4), 4) == "distributividade"


def test_corpo_answer_is_always_an_option():
    for d in [Neutro("+"), Neutro("·"), Simetrico(-3), Inverso(-2), Inverso(0),
              Comutativa(6, 2, "·"), Associativa(1, 1, 1), Distributiva(2, 2, 2)]:
        assert any(pick(d, o) == "sucesso" for o in d.opcoes), d.descricao()
        assert len(d.opcoes) >= 2


# ---- audio preloading -------------------------------------------------------------------------

def test_audio_preloading(tmp_path):
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    import pygame
    import numpy as np
    import soundfile as sf
    from engine import audio as A
    pygame.mixer.init()
    for name in ("sucesso_1", "sucesso_2", "erro"):
        sf.write(str(tmp_path / f"{name}.wav"), np.zeros(2205, dtype="float32"), 22050)
    bank = A.AudioBank([str(tmp_path)])
    bank.preparar(["sucesso", "erro", "nao_existe"])
    assert bank.pendentes() == 2
    while bank.carregar_um():
        pass
    nxt = bank._next["sucesso"]
    assert nxt in A._SOUNDS                      # decoded before it is needed
    assert bank.play("sucesso")
    assert bank._next["sucesso"] != nxt          # following variant already chosen...
    assert bank.pendentes() == 1                 # ...and queued for loading
    assert not bank.play("nao_existe")
