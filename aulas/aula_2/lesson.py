from engine import *

titulo = "Vetores"

desafios = [
    MoverVetor(para=(3, 2), mostrar_alvo=True),
    MoverVetor(para=(2, 3)),
    MoverVetor(para=(-3, 1)),
    MoverVetor(para=(-2, -4)),
    SomarVetores((2, 1), (1, 2)),
    SomarVetores((-1, 3), (3, -1)),
    Segurar(peso=3),                                  # uma corda: o contrário do peso
    Segurar(peso=4, cordas=[(-2, 2)]),                # a outra corda já puxa
    Segurar(peso=3, cordas=[(-3, 1)]),
    Segurar(peso=4, cordas=[(-1, 2)], vento=(3, 0)),  # e ainda há vento
    Escalar((1, 2), por=2),
    Escalar((2, 1), por=-1),
]
