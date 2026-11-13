"""When should the narrator speak? Hearing a clip on every right/wrong answer gets tiring,
so the visual feedback (flash, shake) is always there, but the voice follows these rules.

Change the numbers below to make the narrator talk more or less.

Kinds of clips:
    sempre      intro, fim, dica, challenge start (`audio=`)          -> always
    importante  specific mistakes (trocou_xy, dividir_por_zero, ...)  -> usually (not the same one again too soon)
    normal      sucesso, erro                                         -> sometimes (see below)
    raro        operacao                                              -> rarely
"""
from __future__ import annotations

import random

# ---- knobs ------------------------------------------------------------------------------------
PAUSA_MINIMA = 4.0          # seconds of silence after any clip before a non-"sempre" clip
REPETIR_IMPORTANTE = 25.0   # the same specific mistake is not repeated within this time
PAUSA_NORMAL = 15.0         # seconds between two generic clips (sucesso / erro)
CHANCE_NORMAL = 0.30        # otherwise, chance that a generic clip plays
CHANCE_RARO = 0.12          # chance for "raro" clips (operacao)
PAUSA_RARO = 30.0
SEQUENCIA = 3               # celebrate every N right answers in a row (no mistakes)

SEMPRE = {"intro", "fim", "dica"}
POSITIVAS = {"sucesso", "sequencia", "finalmente"}   # a clip of the other "mood" is cut at once
NORMAL = {"sucesso", "erro"}
RARO = {"operacao"}


class Narrador:
    def __init__(self, banco, rng: random.Random | None = None):
        self.banco = banco
        self.rng = rng or random.Random()
        self.agora = 0.0
        self.ultimo = -1e9                       # time the last clip started
        self.ultimo_por_chave: dict[str, float] = {}
        self.ja_tocou: set[str] = set()           # keys heard at least once in this aula
        self.sequencia = 0                        # right answers in a row without mistakes
        self.tocando: str | None = None           # key of the clip that was started last

    def tick(self, dt: float) -> None:
        self.agora += dt

    def tipo(self, chave: str) -> str:
        if chave in SEMPRE:
            return "sempre"
        if chave in NORMAL:
            return "normal"
        if chave in RARO:
            return "raro"
        return "importante"

    # ---- events from the player ---------------------------------------------------------
    def _cortar_se(self, positiva: bool) -> None:
        """Stop the clip that is playing if it has the opposite mood (e.g. an error clip
        still talking when the student gets it right)."""
        k = self.tocando
        if k and self.banco.busy() and self.tipo(k) != "sempre" and (k in POSITIVAS) != positiva:
            self.banco.stop()
            self.tocando = None

    def acerto(self, falhas: int) -> bool:
        """A challenge was solved after `falhas` wrong attempts."""
        self._cortar_se(positiva=True)
        self.sequencia = self.sequencia + 1 if falhas == 0 else 0
        if self.sequencia and self.sequencia % SEQUENCIA == 0:     # streak: "you know more than the teacher!"
            return self.falar("sequencia", forcar=True) or self.falar("sucesso", forcar=True)
        if falhas >= 2:                                             # finally got it after struggling
            return self.falar("finalmente", forcar=True) or self.falar("sucesso", forcar=True)
        primeira = "sucesso" not in self.ja_tocou                  # first success of the aula
        return self.falar("sucesso", forcar=primeira)

    def erro(self, chave: str) -> bool:
        """A wrong attempt; `chave` is the specific mistake or 'erro'."""
        self._cortar_se(positiva=False)
        self.sequencia = 0
        if chave != "erro" and self.banco.has(chave):
            return self.falar(chave)
        return self.falar("erro")

    # ---- core rule ------------------------------------------------------------------------
    def falar(self, chave: str, forcar: bool = False, interromper: bool = True) -> bool:
        if not self.banco.has(chave):
            return False
        tipo = self.tipo(chave)
        if tipo != "sempre" and not forcar:
            if self.banco.busy() or self.agora - self.ultimo < PAUSA_MINIMA:
                return False
            if tipo == "importante":
                if self.agora - self.ultimo_por_chave.get(chave, -1e9) < REPETIR_IMPORTANTE:
                    return False
            elif tipo == "normal":
                primeira = chave not in self.ja_tocou
                ultimo_normal = max((self.ultimo_por_chave.get(k, -1e9) for k in NORMAL), default=-1e9)
                if not primeira:
                    if self.agora - ultimo_normal < PAUSA_NORMAL or self.rng.random() > CHANCE_NORMAL:
                        return False
            elif tipo == "raro":
                if self.agora - self.ultimo_por_chave.get(chave, -1e9) < PAUSA_RARO \
                        or self.rng.random() > CHANCE_RARO:
                    return False
        if not self.banco.play(chave, interrupt=interromper):
            return False
        self.tocando = chave
        self.ultimo = self.agora
        self.ultimo_por_chave[chave] = self.agora
        self.ja_tocou.add(chave)
        return True
