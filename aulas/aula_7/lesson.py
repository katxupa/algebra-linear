from engine import *

titulo = "Determinantes"

# Sebenta, cap. 6.1 a 6.5. A matriz H é a do exemplo 6.4 (cofator A21 = 4).
A = [[1, 2],
     [3, 4]]
H = [[1, -1, 2],
     [0, 2, 3],
     [-1, 1, 2]]

desafios = [
    Inversoes([1, 3, 2]),                            # permutações: inversões e paridade
    Inversoes([3, 1, 2]),
    Paridade([3, 1, 2]),
    Paridade([2, 1, 3]),
    Det(A),                                          # determinante de ordem 2
    Det([[2, 5], [1, 3]]),
    Cofator(H, 2, 1),                                # cofatores e teorema de Laplace
    Cofator(H, 1, 1),
    Det(H),
    Det([[2, 5, 1], [0, 3, 4], [0, 0, 6]]),          # triangular: produto da diagonal
    Det([[1, 2, 3], [1, 2, 3], [4, 5, 6]]),          # duas linhas iguais: determinante 0
    DetApos(A, "L1 <-> L2"),                         # operações elementares e o determinante
    DetApos(A, "L1 -> 3L1"),
    DetApos(A, "L2 -> L2 - 3L1"),
    DetProp("produto", 2, 3),                        # propriedades do determinante
    DetProp("transposta", 5),
    DetProp("escalar", 3, k=2, n=2),
    DetProp("inversa", 4),
    Regular(H),                                      # determinante diferente de 0 <=> regular
    Regular([[1, 2, 3], [1, 2, 3], [4, 5, 6]]),
]
