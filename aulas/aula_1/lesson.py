from engine import *

titulo = "Corpo"

desafios = [
    Neutro("+"),
    Neutro("·"),
    Simetrico(5),
    Inverso(5),
    Simetrico(-3),
    Inverso(-2),
    Comutativa(3, 4),
    Comutativa(6, 2, "·"),
    Associativa(2, 3, 4),
    Distributiva(2, 3, 4),
    Inverso(0),
    # operação binária: o resultado tem de ficar dentro do conjunto. N e Z não são corpos.
    FechadoEm("N", 2, "+", 3),
    FechadoEm("N", 3, "-", 5),
    SimetricoEm("N", 3),
    FechadoEm("Z", 3, "-", 5),
    InversoEm("Z", 2),
    InversoEm("Q", 2),
]
