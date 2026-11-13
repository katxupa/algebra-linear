import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest

from engine import MoverVetor, SomarVetores, Escalar, MoverBase, EditarMatriz, Determinante
from engine import Segurar
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


# ---- scenes -------------------------------------------------------------------------

def test_segurar_the_sum_of_the_forces_decides_what_happens():
    d = Segurar(peso=4, cordas=[(-2, 2)])
    d.iniciar()
    assert d.alvo == Vec2(2, 2)
    assert not d.tip.pos.close(d.alvo)            # never starts solved
    for pos, esperado in [((2, 1), "caiu"), ((2, 4), "voou"), ((3, 2), "de_lado"), ((2, 2), "sucesso")]:
        d.tip.pos = Vec2(*pos)
        assert d.avaliar() == esperado
    assert d.queda is None                        # safe: nothing falls


def test_segurar_fall_follows_the_sum_and_ends():
    class Ctx:
        dt, time = 0.1, 0.0

    d = Segurar(peso=3)
    d.iniciar()
    assert d.alvo == Vec2(0, 3)
    d.tip.pos = Vec2(1, 0)
    assert d.avaliar() == "caiu"
    for _ in range(8):
        d.update(Ctx)
    desloc = d._desloc()
    assert desloc.y < -2 and abs(desloc.cross(d.queda[1])) < 1e-6   # moves along the sum (1, -3)
    assert d._mergulho() is not None              # already hit the water
    for _ in range(20):
        d.update(Ctx)
    assert d.queda is None                        # back on the plank, ready to try again


def test_segurar_with_wind_and_first_scene_gets_the_intro_clip():
    a, b = Segurar(peso=4, cordas=(-1, 2), vento=(3, 0)), Segurar(peso=3)
    assert a.alvo == Vec2(-2, 2)
    aula = [MoverVetor(para=(1, 2)), a, b]
    for i, d in enumerate(aula):
        d.no_contexto(aula, i)
    assert a.audio == "cena_cordas" and b.audio is None



# ---- matrix notions (aula 2) --------------------------------------------------------------

from engine import Entrada, Tipo, Forma, Diagonal, Traco, Zerar, Qual, Submatriz

M32 = [[3, 2], [-1, 4], [2, 0]]
M33 = [[2, 5, 1], [7, 3, 4], [8, 9, 6]]


def test_entrada_row_first_then_column():
    d = Entrada(M32, 1, 2)
    d.iniciar()
    for cel, esperado in [((0, 1), "sucesso"), ((1, 0), "trocou_ij"), ((0, 0), "so_linha"),
                          ((2, 1), "so_coluna"), ((2, 0), "erro")]:
        d.sel = cel
        assert d.avaliar() == esperado
    with pytest.raises(ValueError):
        Entrada(M32, 2, 3)                        # there is no column 3


def test_tipo_and_forma():
    d = Tipo(M32)
    d.iniciar()
    assert d.resposta == (3, 2) and (3, 2) in d.opcoes and (2, 3) in d.opcoes and len(d.opcoes) == 4
    d.sel = (2, 3)
    assert d.avaliar() == "trocou_mn"
    d.sel = (3, 2)
    assert d.avaliar() == "sucesso"
    for m, nome in [([[1, 2, 3]], "m_linha"), ([[1], [2]], "m_coluna"), (M33, "m_quadrada"), (M32, "m_retangular")]:
        f = Forma(m)
        f.iniciar()
        assert f.resposta == nome and nome in f.opcoes
    linha = Forma([[1, 2, 3]])
    linha.iniciar()
    assert "m_retangular" not in linha.opcoes         # a row matrix is rectangular too: never both
    linha.sel = "m_coluna"
    assert linha.avaliar() == "linha_coluna"


def test_diagonal_and_trace():
    d = Diagonal(M33)
    d.iniciar()
    d.marc = {(0, 0), (1, 1), (2, 2)}
    assert d.avaliar() == "sucesso"
    d.marc = {(0, 2), (1, 1), (2, 0)}
    assert d.avaliar() == "diagonal_errada"
    d.marc = {(0, 0), (1, 1)}
    assert d.avaliar() == "incompleto"
    tr = Traco(M33)
    tr.iniciar()
    assert tr.resposta == 11 and 11 in tr.opcoes
    tr.sel = 12                                       # 1 + 3 + 8: the other diagonal
    assert tr.avaliar() == "diagonal_errada"
    tr.sel = 45
    assert tr.avaliar() == "somou_tudo"
    with pytest.raises(ValueError):
        Traco(M32)


def test_zerar_builds_triangular_and_diagonal_matrices():
    abaixo, acima = {(1, 0), (2, 0), (2, 1)}, {(0, 1), (0, 2), (1, 2)}
    d = Zerar(M33, "triangular superior")
    d.iniciar()
    for marc, esperado in [(abaixo, "sucesso"), (acima, "triangulo_trocado"), (abaixo | {(1, 1)}, "diagonal_apagada"),
                           ({(1, 0)}, "incompleto"), ({(1, 0), (0, 1)}, "erro")]:
        d.marc = set(marc)
        assert d.avaliar() == esperado
    d = Zerar(M33, "diagonal")
    d.iniciar()
    d.marc = abaixo | acima
    assert d.avaliar() == "sucesso"
    with pytest.raises(ValueError):
        Zerar([[1, 2], [0, 3]], "triangular superior")   # already triangular


def test_qual_has_exactly_one_right_matrix_for_every_name():
    from engine.challenges.nocoes import NOMES, e_do_tipo
    for nome in NOMES:
        d = Qual(nome)
        d.iniciar()
        certas = [k for k, (m, _) in enumerate(d.lista) if e_do_tipo(nome, m)]
        assert len(certas) == 1
        d.sel = certas[0]
        assert d.avaliar() == "sucesso"
        d.sel = (certas[0] + 1) % len(d.lista)
        assert d.avaliar() != "sucesso"
    with pytest.raises(ValueError):
        Qual("diagonal", opcoes=[[[1, 0], [0, 2]], [[3, 0], [0, 3]]])   # two diagonal matrices


def test_submatriz_both_notations_give_the_same_answer():
    c = [[1, 2, 3, 4], [4, 3, 2, 1], [-1, -2, -3, -4], [-4, -3, -2, -1]]
    a, b = Submatriz(c, ficar=([1, 3], [2, 3, 4])), Submatriz(c, tirar=([2, 4], [1]))
    assert (a.fora_l, a.fora_c) == (b.fora_l, b.fora_c) == ({1, 3}, {0})
    a.iniciar()
    a.tl, a.tc = {1, 3}, {0}
    assert a.avaliar() == "sucesso"
    a.tl, a.tc = {0, 2}, {1, 2, 3}
    assert a.avaliar() == "parenteses_trocados"
    a.tl, a.tc = {1, 3}, set()
    assert a.avaliar() == "so_linha"


# ---- the rest of the sebenta: matrix algebra, systems, inverse, determinants, Cramer ---------------

from engine import matrizes as MT
from engine import (Transposta, Soma, VezesEscalar, Produto, Potencia, Formula, Adjunta, InversaAdjunta,
                    Simetrica, TipoProduto, Caracteristica, Solucao, Classificar, Grau, Regular, Det, Cofator,
                    DetApos, DetProp, Inversoes, Paridade, CramerMatriz, CramerValor, Inversa,
                    FechadoEm, SimetricoEm, InversoEm)

H = [[1, -1, 2], [0, 2, 3], [-1, 1, 2]]                 # sebenta, exemplo 6.4
K = [[1, -1, 2, -1], [0, 2, 3, 2], [-1, 1, 4, 3]]       # sebenta, exemplo 6.11


def test_matrix_arithmetic_is_exact():
    a, b = MT.matriz([[1, 2], [3, 4]]), MT.matriz([[0, 1], [5, -2]])
    assert MT.produto(a, b) == [[10, -3], [20, -5]] and MT.produto(b, a) == [[3, 4], [-1, 2]]
    assert MT.transposta(MT.matriz([[1, 2, 3], [4, 5, 6]])) == [[1, 4], [2, 5], [3, 6]]
    assert MT.det(a) == -2 and MT.det(MT.matriz(H)) == 8
    assert MT.cofator(MT.matriz(H), 1, 0) == 4                      # A21 = 4, as in the sebenta
    assert MT.adjunta(a) == [[4, -2], [-3, 1]]
    assert MT.produto(a, MT.inversa(a)) == [[1, 0], [0, 1]]
    assert MT.caracteristica(MT.matriz([[1, 2, 3], [4, 5, 6], [7, 8, 9]])) == 2
    assert MT.inversoes([3, 1, 2]) == 2
    with pytest.raises(ValueError):
        MT.produto(a, MT.matriz([[1, 2, 3]]))


def test_systems_are_classified_by_the_ranks():
    assert MT.classificar(MT.matriz([[1, 1, 3], [0, 1, 1]])) == "pd"
    assert MT.classificar(MT.matriz([[1, 2, 3], [0, 0, 5]])) == "imp"
    assert MT.classificar(MT.matriz([[1, -2, 3, 1, -3], [2, -1, 3, -1, 0]])) == "pi"
    d = Classificar([[1, -2, 3, 1, -3], [0, 3, -3, -3, 6]])
    d.iniciar()
    d.sel = "sel_pd"
    assert d.avaliar() == "incognita_livre"
    d.sel = "sel_pi"
    assert d.avaliar() == "sucesso"
    homogeneo = Classificar([[1, 2, 0], [0, 1, 0]])
    homogeneo.iniciar()
    homogeneo.sel = "sel_imp"
    assert homogeneo.avaliar() == "homogeneo_impossivel"
    assert Grau([[1, -2, 3, 1, -3], [0, 3, -3, -3, 6]]).resposta == 2
    assert Solucao([[1, 1, 3], [1, -1, 1]], (2, 1)).resposta == "sim"
    assert Solucao([[1, 1, 3], [1, -1, 1]], (1, 2)).resposta == "nao"
    c = Caracteristica([[1, 2, 3], [0, 1, 4], [0, 0, 0]])
    c.iniciar()
    c.sel = 3
    assert c.resposta == 2 and c.avaliar() == "contou_linhas"


def preencher(d, m):
    d.iniciar()
    d.txt = {(r, c): MT.E.fmt(MT.E.frac(v)) for r, row in enumerate(m) for c, v in enumerate(row)}
    return d.avaliar()


def test_fill_in_challenges_recognise_the_typical_wrong_results():
    a, b = [[1, 2], [3, 4]], [[0, 1], [5, -2]]
    assert preencher(Produto(a, b), [[10, -3], [20, -5]]) == "sucesso"
    assert preencher(Produto(a, b), [[0, 2], [15, -8]]) == "entrada_a_entrada"
    assert preencher(Produto(a, b), [[3, 4], [-1, 2]]) == "ordem_trocada"
    assert preencher(Transposta(a), a) == "nao_transpos"
    assert preencher(Soma(a, b), [[1, 3], [8, 2]]) == "sucesso"
    assert preencher(Soma(a, b, "-"), [[1, 3], [8, 2]]) == "sinal"
    assert preencher(VezesEscalar(3, a), [[3, 6], [9, 12]]) == "sucesso"
    assert preencher(Potencia(a, 2), [[1, 4], [9, 16]]) == "entrada_a_entrada"
    assert preencher(Formula(3, 3, "i ** (j - 1)"), [[1, 1, 1], [1, 2, 4], [1, 3, 9]]) == "sucesso"
    assert preencher(Adjunta(a), [[4, -3], [-2, 1]]) == "nao_transpos"
    assert preencher(InversaAdjunta(a), [[4, -2], [-3, 1]]) == "faltou_dividir"
    assert preencher(InversaAdjunta(a), [[-2, 1], ["3/2", "-1/2"]]) == "sucesso"
    d = Produto(a, b)
    d.iniciar()
    d.txt = {(0, 0): "10"}
    assert d.avaliar() == "incompleto"            # right so far: the student can check entry by entry
    d.txt = {(0, 0): "10", (0, 1): "7"}
    assert d.avaliar() == "erro" and d.erradas == {(0, 1)}
    d.sel = (1, 1)
    for key in ("5", "−", "←", "5"):              # typing: 5, minus, erase, 5 again
        d.escrever(key)
    assert d.txt[(1, 1)] == "−5"


def test_determinant_questions():
    d = Det([[1, 2], [3, 4]])
    d.iniciar()
    for sel, esperado in [(-2, "sucesso"), (2, "sinal"), (4, "so_diagonal"), (10, "somou")]:
        d.sel = MT.E.frac(sel)
        assert d.avaliar() == esperado
    c = Cofator(H, 2, 1)
    c.iniciar()
    c.sel = MT.E.frac(-4)
    assert c.resposta == 4 and c.avaliar() == "sinal_cofator"
    assert DetApos([[1, 2], [3, 4]], "L1 <-> L2").resposta == 2
    assert DetApos([[1, 2], [3, 4]], "L1 -> 3L1").resposta == -6
    assert DetApos([[1, 2], [3, 4]], "L2 -> L2 - 3L1").resposta == -2
    assert DetProp("produto", 2, 3).resposta == 6
    assert DetProp("escalar", 3, k=2, n=2).resposta == 12
    assert DetProp("inversa", 4).resposta == MT.E.frac("1/4")
    assert Inversoes([3, 1, 2]).resposta == 2 and Paridade([3, 1, 2]).resposta == "p_par"
    assert Regular(H).resposta == "sim" and Regular([[1, 2], [2, 4]]).resposta == "nao"
    assert Simetrica([[0, 2], [-2, 0]]).resposta == "m_antissimetrica"
    assert TipoProduto((2, 3), (3, 2)).resposta == (2, 2)
    assert TipoProduto((2, 3), (2, 3)).resposta == "nao_existe"


def test_cramer_and_the_inverse_by_row_operations():
    m = CramerMatriz(K, 2)
    m.iniciar()
    assert m.lista[m.certa][0] == [[1, -1, 2], [0, 2, 3], [-1, 3, 4]]
    m.sel = 1
    assert m.avaliar() == "coluna_errada"
    s = [[2, 1, 5], [1, 3, 5]]
    assert CramerValor(s, 1).resposta == 2 and CramerValor(s, 2).resposta == 1
    with pytest.raises(ValueError):
        CramerValor([[1, 2, 3], [2, 4, 6]], 1)                    # not a Cramer system
    inv = Inversa([[1, 2], [3, 4]])
    inv.iniciar()
    assert inv.n_coef == 2 and inv.m == MT.matriz([[1, 2, 1, 0], [3, 4, 0, 1]])
    with pytest.raises(ValueError):
        Inversa([[1, 2], [2, 4]])


def test_n_and_z_are_not_fields():
    from engine.challenges.corpo import NAO_EXISTE as NE
    assert FechadoEm("N", 2, "+", 3).resposta == 5
    assert FechadoEm("N", 3, "-", 5).resposta is NE
    assert FechadoEm("Z", 3, "-", 5).resposta == -2
    assert SimetricoEm("N", 3).resposta is NE
    assert InversoEm("Z", 2).resposta is NE
    assert InversoEm("Q", 2).resposta == Fraction(1, 2)


def test_every_lesson_of_the_sebenta_is_playable():
    aulas = {a.numero: a for a in discover()}
    for n in range(1, 9):
        assert not aulas[n].erro and not aulas[n].em_breve and len(aulas[n].desafios) >= 7

