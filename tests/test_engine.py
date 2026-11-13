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


# ---- escalonamento ---------------------------------------------------------------------------

from engine import escalonamento as E
from engine import Escalonar


def test_row_operations_exact_fractions():
    m = E.matriz([[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]])
    m = E.aplicar(m, ("combina", 2, Fraction(3, 2), 1))
    assert m[1] == [0, Fraction(1, 2), Fraction(1, 2), 1]
    m = E.aplicar(m, ("multiplica", 2, 2))
    assert m[1] == [0, 1, 1, 2]
    assert E.aplicar(m, ("troca", 1, 3))[0] == m[2]
    with pytest.raises(E.OperacaoInvalida) as e:
        E.aplicar(m, ("multiplica", 1, 0))
    assert e.value.chave == "multiplicar_por_zero"
    with pytest.raises(E.OperacaoInvalida) as e:
        E.aplicar(m, ("combina", 1, 2, 1))
    assert e.value.chave == "mesma_linha"


def test_forms_and_solver_reach_goal():
    for goal in ("escalonada", "reduzida"):
        m = E.matriz([[2, 1, -1, 8], [-3, -1, 2, -11], [-2, 1, 2, -3]])
        for _ in range(30):
            op = E.proximo_passo(m, goal, 3)
            if op is None:
                break
            m = E.aplicar(m, op, 3)
        assert E.escalonada(m, 3)
        if goal == "reduzida":
            assert E.reduzida(m, 3)
            assert [r[3] for r in m] == [2, 3, -1]      # x=2, y=3, z=-1


@pytest.mark.parametrize("cmd,op", [
    ("L1 <-> L2", ("troca", 1, 2)),
    ("C1<->C3", ("troca_col", 1, 3)),
    ("L2 -> 1/3 L2", ("multiplica", 2, Fraction(1, 3))),
    ("L2 = -L2", ("multiplica", 2, -1)),
    ("L3 -> L3 - 2L1", ("combina", 3, -2, 1)),
    ("L3 = L3 + (-1/2)*L1", ("combina", 3, Fraction(-1, 2), 1)),
    ("L2 -> -2L1 + L2", ("combina", 2, -2, 1)),
])
def test_parse_commands(cmd, op):
    assert E.parse(cmd) == op


def test_parse_rejects_nonsense():
    for cmd in ("L1 <-> C2", "L2 -> L3", "hello"):
        with pytest.raises(E.OperacaoInvalida):
            E.parse(cmd)


class _Ctx:
    def __init__(self):
        self.avisos, self.sons = [], []
        self.aviso = self.avisos.append
        self.som = self.sons.append


def test_escalonar_challenge_flow():
    d = Escalonar([[1, 2, 5], [3, 4, 6]], objetivo="reduzida")
    d.iniciar()
    ctx = _Ctx()
    assert d.avaliar() == "nao_escalonada"
    for tok in ["L2", "→", "L2", "−", "3", "L1"]:   # built on the calculator keys
        d.inserir(tok)
    assert d.texto_expr() == "L2 → L2 − 3L1"
    assert d.aplicar_expr(ctx) and d.expr == []
    assert d.avaliar() == "nao_reduzida"
    d.executar(ctx, ("multiplica", 1, 0))
    assert ctx.avisos == ["multiplicar_por_zero"]
    d.desfazer()
    assert d.avaliar() == "nao_escalonada"            # undo went back to the start
    d.executar(ctx, ("combina", 2, -3, 1))
    d.executar(ctx, ("multiplica", 2, Fraction(-1, 2)))
    d.executar(ctx, ("combina", 1, -2, 2))
    assert d.avaliar() == "sucesso"
    assert len(d.hist) == 3 and ctx.sons.count("operacao") == 4   # 1 typed + 3 buttons


def test_column_swap_moves_variable_names():
    d = Escalonar([[0, 2, 1, 4], [1, 0, 3, 5]], colunas=True)
    d.iniciar()
    d.executar(_Ctx(), ("troca_col", 1, 2))
    assert d.nomes[:2] == ["y", "x"] and d.m[0][:2] == [2, 0]
    with pytest.raises(E.OperacaoInvalida):          # the b column cannot be swapped
        E.aplicar(d.m, ("troca_col", 1, 4), d.n_coef)


# ---- narrator: does not talk on every answer ----------------------------------------------------

import random as _random

from engine import narrador as Nr


class _Banco:
    def __init__(self, keys):
        self.keys, self.tocados = set(keys), []

    def has(self, k):
        return k in self.keys

    def play(self, k, interrupt=True):
        self.tocados.append(k)
        return True

    def busy(self):
        return False


def test_narrator_speaks_less_on_repeated_successes():
    b = _Banco({"sucesso", "erro", "intro", "trocou_xy"})
    n = Nr.Narrador(b, _random.Random(1))
    assert n.falar("intro")                      # "sempre"
    falou = []
    for _ in range(12):                          # 12 quick right answers, 6 s apart
        n.tick(6)
        falou.append(n.acerto(falhas=0))
    assert falou[0]                              # first success of the aula: always
    assert falou[2] and falou[5] and falou[8]    # streak of 3 / 6 / 9: always
    assert sum(falou) < 12 * 0.6                 # but far from every time


def test_narrator_specific_mistakes_and_redemption():
    b = _Banco({"sucesso", "erro", "trocou_xy"})
    n = Nr.Narrador(b, _random.Random(1))
    n.tick(10)
    assert n.erro("trocou_xy")                   # specific mistake: speaks
    n.tick(5)
    assert not n.erro("trocou_xy")               # same mistake again too soon: silent
    n.tick(Nr.REPETIR_IMPORTANTE)
    assert n.erro("trocou_xy")                   # ...but later it may speak again
    n.tick(1)
    assert n.acerto(falhas=2)                    # finally right after struggling: always
    assert n.sequencia == 0


def test_narrator_unknown_mistake_falls_back_to_erro():
    b = _Banco({"erro"})
    n = Nr.Narrador(b, _random.Random(1))
    n.tick(10)
    assert n.erro("sinal") and b.tocados == ["erro"]


def test_narrator_streak_and_finally_clips():
    b = _Banco({"sucesso", "sequencia", "finalmente"})
    n = Nr.Narrador(b, _random.Random(1))
    for _ in range(3):
        n.tick(6)
        n.acerto(falhas=0)
    assert b.tocados[0] == "sucesso" and b.tocados[-1] == "sequencia"
    n.tick(6)
    assert n.acerto(falhas=3) and b.tocados[-1] == "finalmente"


def test_calculator_typing_and_bad_operations():
    import pygame
    d = Escalonar([[1, 2, 5], [3, 4, 6]])
    d.iniciar()
    ctx = _Ctx()
    for ch in "l2->l2-3l1":                         # physical keyboard
        d.tecla(ctx, pygame.event.Event(pygame.TEXTINPUT, text=ch))
    assert d.texto_expr() == "L2 → L2 − 3L1"
    assert d.aplicar_expr(ctx)
    for ch in "L1<->L2":
        d.tecla(ctx, pygame.event.Event(pygame.TEXTINPUT, text=ch))
    assert d.texto_expr() == "L1 ↔ L2"
    d.inserir("AC")                                  # clear key
    for tok in ["L1", "→", "0", "L1"]:          # multiply by zero is refused
        d.inserir(tok)
    assert not d.aplicar_expr(ctx) and ctx.avisos[-1] == "multiplicar_por_zero"
    d.inserir("AC")
    for tok in ["L1", "→", "L2"]:               # not an elementary operation
        d.inserir(tok)
    assert not d.aplicar_expr(ctx) and ctx.avisos[-1] == "comando"
    assert len(d.hist) == 1


def test_keys_are_introduced_gradually():
    from engine.lesson.loader import discover
    aula = [a for a in discover() if a.numero == 4][0]
    first, second = aula.desafios[0], aula.desafios[1]
    assert "↔" in first.teclas and "→" not in first.teclas      # 1st: only swapping rows
    assert first.teclas_novas0 == set()                                    # nothing marked new at the start
    assert "→" in second.teclas and "→" in second.teclas_novas0  # 2nd: the arrow appears, marked new
    assert "↔" in second.teclas                                       # earlier keys stay
    assert "/" in aula.desafios[3].teclas


def test_error_clip_is_cut_when_the_student_gets_it_right():
    class Banco(_Banco):
        def __init__(self, keys):
            super().__init__(keys)
            self.playing, self.stops = False, 0

        def play(self, k, interrupt=True):
            self.playing = True
            return super().play(k, interrupt)

        def busy(self):
            return self.playing

        def stop(self):
            self.playing = False
            self.stops += 1

    b = Banco({"sucesso", "erro"})
    n = Nr.Narrador(b, _random.Random(5))
    n.ja_tocou.add("sucesso")                # not the first success: may stay silent
    n.tick(10)
    assert n.erro("erro") and b.busy()       # a long error clip is talking...
    n.tick(1)
    n.acerto(falhas=1)                       # ...and the student gets it right
    assert b.stops == 1                      # the error clip is cut, never heard over a success


def test_column_operations():
    m = E.matriz([[1, 2], [3, 4]])
    assert E.aplicar(m, E.parse("C2 -> C2 - 2C1")) == E.matriz([[1, 0], [3, -2]])
    assert E.aplicar(m, E.parse("C1 -> 3C1")) == E.matriz([[3, 2], [9, 4]])
    assert E.aplicar(m, E.parse("C1 <-> C2")) == E.matriz([[2, 1], [4, 3]])
    with pytest.raises(E.OperacaoInvalida) as e:              # in a system only swaps are allowed
        E.aplicar(E.matriz([[1, 2, 3]]), E.parse("C2 -> C2 + C1"), 2, sistema=True)
    assert e.value.chave == "coluna_sistema"
    with pytest.raises(E.OperacaoInvalida):
        E.parse("L1 -> L1 + C2")                              # rows and columns don't mix


def test_column_swap_is_introduced_when_useful():
    from engine.lesson.loader import discover
    aula = [a for a in discover() if a.numero == 4][0]
    d = aula.desafios[2]                                      # [[0,1,2],[0,3,4]], colunas=True
    assert "colunas" in d.recursos_proprios
    assert {"C1", "C2"} <= d.teclas_novas0
    assert E.proximo_passo(d.inicial, "escalonada", 3, True) == ("troca_col", 1, 2)
