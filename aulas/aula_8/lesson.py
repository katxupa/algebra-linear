from engine import *

titulo = "Cramer e Adjunta"

# Sebenta, cap. 6.6 e 6.7. O sistema K é o do exemplo 6.11.
A = [[1, 2],
     [3, 4]]
S = [[2, 1, 5],
     [1, 3, 5]]
K = [[1, -1, 2, -1],
     [0, 2, 3, 2],
     [-1, 1, 4, 3]]

desafios = [
    Adjunta(A),                                      # adjunta: transposta dos cofatores
    Adjunta([[2, 1], [5, 3]]),
    InversaAdjunta([[2, 1], [5, 3]]),                # inversa = adjunta / determinante
    InversaAdjunta(A),
    CramerMatriz(S, 1),                              # regra de Cramer
    CramerValor(S, 1),
    CramerMatriz(S, 2),
    CramerValor(S, 2),
    CramerMatriz(K, 2),
    CramerValor(K, 3),
]
