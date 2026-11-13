"""Base class for every challenge type.

A challenge type knows how to: set itself up, draw its goal (no words), handle input,
evaluate an attempt, and recognise the common mistakes of its concept. Lessons only
instantiate challenge types with numbers, e.g. `MoverVetor(para=(3, 2))`.

To create a new challenge type: subclass `Desafio`, fill `ERROS` and implement
`iniciar`, `avaliar`, `desenhar` (+ input via `handles` or the press/move/release hooks).
"""
from __future__ import annotations

from ..linalg import Mat2, Vec2
from ..scene import draw
from .. import theme

SUCESSO = "sucesso"
ERRO = "erro"


class Ctx:
    """What the engine hands a challenge while it runs."""

    def __init__(self, cam, width: int, height: int, hud_y: float, bottom_y: float):
        self.cam = cam
        self.width = width
        self.height = height
        self.hud_y = hud_y          # vertical center of the goal area at the top
        self.bottom_y = bottom_y    # vertical center of the bottom panel (if the challenge uses it)
        self.dt = 0.0
        self.time = 0.0
        self.hint_alpha = 1.0       # blinking factor for hints (0..1)
        self.solved = False
        # set by the player: instant feedback without counting an attempt
        self.aviso = lambda chave: None   # warning: shake + red flash + clip (falls back to `erro`)
        self.som = lambda chave: None     # just play a clip if it exists


class Desafio:
    # --- for subclasses -------------------------------------------------------------
    #: mistake key -> what triggers it (used by tools/roteiro.py for the narrator checklist)
    ERROS: dict[str, str] = {}
    #: True: attempts are made with the ✓ button. False: every drag release is an attempt.
    confirmar = False
    #: True: reserve the bottom of the screen for a panel (e.g. the matrix editor).
    painel = False
    #: False: no coordinate grid behind the challenge (e.g. number puzzles)
    plano = True
    #: False: hide the basis vectors î/ĵ (the scene has its own vectors)
    base = True
    #: height in pixels of the bottom panel (when `painel = True`)
    painel_altura = 210

    def __init__(self, *, dica_apos: int = 3, audio: str | None = None):
        self.dica_apos = dica_apos
        self.audio = audio          # optional clip key played when this challenge starts
        self.handles = []

    # --- lifecycle ------------------------------------------------------------------
    def iniciar(self) -> None:
        """(Re)create the challenge state. Called each time the challenge starts."""

    def avaliar(self) -> str:
        """Return SUCESSO, a key from ERROS, or ERRO."""
        raise NotImplementedError

    def estado(self):
        """Hashable snapshot of the answer; an attempt equal to the previous one is ignored."""
        return tuple(h.pos for h in self.handles)

    def matriz(self) -> Mat2:
        """Matrix the background grid is transformed by."""
        return Mat2.identity()

    def update(self, ctx: Ctx) -> None:
        pass

    # --- drawing --------------------------------------------------------------------
    def desenhar(self, surf, ctx: Ctx) -> None:
        """World objects (vectors, shapes). Grid is drawn by the engine."""

    def desenhar_alvo(self, surf, ctx: Ctx) -> None:
        """Goal at the top of the screen (numbers/symbols, no sentences)."""

    def desenhar_dica(self, surf, ctx: Ctx) -> None:
        """Extra visual help shown after `dica_apos` failed attempts."""

    def desenhar_painel(self, surf, ctx: Ctx) -> None:
        """Bottom panel, when `painel = True`."""

    # --- input (default: drag handles) ------------------------------------------------
    def press(self, ctx: Ctx, sx, sy) -> bool:
        for h in reversed(self.handles):
            if h.press(ctx.cam, sx, sy):
                return True
        return False

    def move(self, ctx: Ctx, sx, sy) -> None:
        for h in self.handles:
            h.move(ctx.cam, sx, sy)

    def release(self, ctx: Ctx) -> bool:
        """Return True if this release counts as an attempt."""
        released = False
        for h in self.handles:
            released = h.release() or released
        return released and not self.confirmar

    def no_contexto(self, desafios: list, indice: int) -> None:
        """Called once by the loader with the whole aula (e.g. to introduce things gradually)."""

    def altura_painel(self, w: int) -> int:
        """Bottom panel height for a screen `w` pixels wide (override to adapt to phones)."""
        return self.painel_altura

    def tecla(self, ctx: Ctx, ev) -> None:
        """Keyboard events (KEYDOWN / TEXTINPUT), for challenges where the student types."""

    def layout(self, ctx: Ctx) -> None:
        """Screen size changed: place panel widgets."""

    # --- helpers for subclasses ---------------------------------------------------------
    @classmethod
    def chaves_audio(cls) -> list[str]:
        return [SUCESSO, ERRO, *cls.ERROS.keys()]

    def descricao(self) -> str:
        return type(self).__name__


# ---- reusable mistake detectors ----------------------------------------------------------

def erro_vetor(p: Vec2, alvo: Vec2) -> str:
    """Common mistakes when placing a vector."""
    if p.close(alvo):
        return SUCESSO
    if abs(alvo.x - alvo.y) > 1e-6 and p.close(Vec2(alvo.y, alvo.x)):
        return "trocou_xy"
    if abs(abs(p.x) - abs(alvo.x)) < 1e-6 and abs(abs(p.y) - abs(alvo.y)) < 1e-6:
        return "sinal"
    if max(abs(p.x - alvo.x), abs(p.y - alvo.y)) <= 1 + 1e-6:
        return "quase"
    return ERRO


ERROS_VETOR = {
    "trocou_xy": "trocou x e y (ex: colocou em (2,3) em vez de (3,2))",
    "sinal": "acertou os números mas errou o sinal (+/−)",
    "quase": "ficou a 1 casinha do lugar certo",
}


def erro_matriz(m: Mat2, alvo: Mat2) -> str:
    """Common mistakes when building a matrix / moving î and ĵ."""
    if m.close(alvo):
        return SUCESSO
    if not alvo.close(alvo.swap_cols()) and m.close(alvo.swap_cols()):
        return "trocou_base"
    if not alvo.close(alvo.transpose()) and m.close(alvo.transpose()):
        return "transposta"
    if all(abs(abs(p) - abs(q)) < 1e-6 for p, q in zip(m.rows_flat(), alvo.rows_flat())):
        return "sinal"
    if sum(abs(p - q) for p, q in zip(m.rows_flat(), alvo.rows_flat())) <= 1 + 1e-6:
        return "quase"
    return ERRO


ERROS_MATRIZ = {
    "trocou_base": "trocou î com ĵ (colunas trocadas)",
    "transposta": "leu a matriz por linhas em vez de colunas (transposta)",
    "sinal": "números certos, algum sinal (+/−) errado",
    "quase": "só um número errado por 1",
}


def ghost_basis(surf, cam, m: Mat2, alpha: float = 1.0) -> None:
    """Dashed î/ĵ showing where the basis should land."""
    o = cam.to_screen((0, 0))
    fade = lambda c: tuple(int(v * (0.35 + 0.65 * alpha)) for v in c)
    draw.dashed_arrow(surf, fade(theme.I_HAT), o, cam.to_screen(m.i), 3)
    draw.dashed_arrow(surf, fade(theme.J_HAT), o, cam.to_screen(m.j), 3)
