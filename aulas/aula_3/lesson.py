from engine import *

titulo = "Operações com Matrizes"

# Sebenta, cap. 2.3: transposta, simétrica e anti-simétrica, soma, produto por escalar,
# produto (linha × coluna), potências, a identidade como neutro.
A = [[1, 2],
     [3, 4]]
B = [[0, 1],
     [5, -2]]
R = [[1, 2, 3],
     [4, 5, 6]]
S = [[1, 0],
     [2, 1],
     [0, 3]]

desafios = [
    Transposta(R),                                   # transposta: linhas passam a colunas
    Transposta(A),
    Simetrica([[1, 2, 3], [2, 5, 4], [3, 4, 6]]),
    Simetrica([[0, 2, -1], [-2, 0, 3], [1, -3, 0]]),
    Simetrica(A),
    Soma(A, B),                                      # soma e produto por escalar
    Soma(A, B, "-"),
    VezesEscalar(3, A),
    TipoProduto((2, 3), (3, 2)),                     # quando é que o produto existe, e de que tipo
    TipoProduto((2, 3), (2, 3)),
    TipoProduto((3, 1), (1, 3)),
    Produto([[1, 2, 3]], [[4], [5], [6]]),           # linha × coluna (produto escalar)
    Produto(A, B),
    Produto(B, A),                                   # A · B ≠ B · A
    Produto(R, S),
    Produto(A, [[1, 0], [0, 1]]),                    # a identidade não muda nada
    Potencia(A, 2),
]
