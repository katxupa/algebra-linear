from engine import *

titulo = "Escalonamento"

# Do mais fácil para o mais difícil: as teclas da calculadora aparecem aos poucos,
# conforme cada exercício precisa (troca, depois combinação, frações, multiplicar...).
desafios = [
    Escalonar([[0, 1, 2],
               [2, 4, 6]]),                                   # só trocar linhas
    Escalonar([[1, 2, 5],
               [3, 4, 6]]),                                   # L2 → L2 − 3L1
    Escalonar([[0, 1, 2],
               [0, 3, 4]], aumentada=False, colunas=True),    # aparecem as colunas: C1 ↔ C2
    Escalonar([[1, 1, 1, 6],
               [2, -1, 1, 3],
               [1, 2, -1, 2]], forma="sistema"),
    Escalonar([[2, 1, -1, 8],
               [-3, -1, 2, -11],
               [-2, 1, 2, -3]]),                              # aparecem frações
    Escalonar([[1, 2, 5],
               [3, 4, 6]], objetivo="reduzida"),              # multiplicar linhas
    Escalonar([[1, 2, -1, 3],
               [2, 5, 1, 8],
               [-1, 1, 4, 2]], objetivo="reduzida"),
    Escalonar([[0, 2, 1, 4],
               [1, 0, 3, 5],
               [0, 1, 2, 3]], colunas=True),                  # trocar colunas
    Escalonar([[1, 2, 3],
               [4, 5, 6],
               [7, 8, 9]], aumentada=False),
]
