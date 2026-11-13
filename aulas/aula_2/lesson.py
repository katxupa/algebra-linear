from engine import *

titulo = "Matrizes"

# Sebenta, cap. 2.1 e 2.2. As matrizes A, B e C são as dos exemplos 2.1 e 2.2.
A = [[3, 2],
     [-1, 4],
     [2, 0]]
B = [[1, 1, 1, 1],                 # b_ij = i^(j−1)
     [1, 2, 4, 8],
     [1, 3, 9, 27],
     [1, 4, 16, 64]]
C = [[1, 2, 3, 4],
     [4, 3, 2, 1],
     [-1, -2, -3, -4],
     [-4, -3, -2, -1]]
E = [[2, 5, 1],
     [7, 3, 4],
     [8, 9, 6]]

desafios = [
    Entrada(A, 1, 2),                          # entradas: primeiro a linha, depois a coluna
    Entrada(A, 3, 1),
    Entrada(B, 2, 4),
    Tipo(A),                                   # tipo m × n
    Tipo([[1, -3, 5, 3]]),
    Forma([[1, -3, 5, 3]]),                    # matriz linha, coluna, quadrada, retangular
    Forma([[4], [-2], [2]]),
    Forma(E),
    Forma(A),
    Diagonal(E),                               # diagonal principal e traço
    Traco(E),
    Zerar(E, "triangular superior"),           # tipos de matrizes quadradas
    Zerar(E, "triangular inferior"),
    Zerar(E, "diagonal"),
    Qual("escalar"),
    Qual("identidade"),
    Submatriz(C, ficar=([1, 3], [2, 3, 4])),   # A[1,3 | 2,3,4]
    Submatriz(C, tirar=([2, 4], [1])),         # A(2,4 | 1): a mesma submatriz
]
