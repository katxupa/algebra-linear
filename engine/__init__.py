"""Linear-algebra lesson engine.

Lessons only need:  `from engine import *`  and then a `titulo` and a `desafios` list.
"""
from .challenges import (Desafio, MoverVetor, SomarVetores, Escalar,
                         MoverBase, EditarMatriz, Determinante,
                         Neutro, Simetrico, Inverso, Comutativa, Associativa, Distributiva,
                         Escalonar, Segurar)

__all__ = ["Desafio", "MoverVetor", "SomarVetores", "Escalar",
           "MoverBase", "EditarMatriz", "Determinante",
           "Neutro", "Simetrico", "Inverso", "Comutativa", "Associativa", "Distributiva",
           "Escalonar", "Segurar"]
