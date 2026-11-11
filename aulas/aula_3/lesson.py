from engine import *

titulo = "Matrizes"

desafios = [
    MoverBase(matriz=[[2, 0], [0, 1]], ver="forma"),
    MoverBase(matriz=[[0, -1], [1, 0]], ver="forma"),
    MoverBase(matriz=[[1, 1], [0, 1]]),
    MoverBase(matriz=[[2, -1], [1, 2]]),
    EditarMatriz(alvo=[[1, 2], [0, 1]]),
    EditarMatriz(alvo=[[-1, 0], [1, 2]]),
    Determinante(area=2),
    Determinante(area=-3),
]
