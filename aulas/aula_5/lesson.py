from engine import *

titulo = "Sistemas"

# Sebenta, cap. 4. Cada matriz é a matriz ampliada [A | B] do sistema.
# O sistema P é o do exemplo 4.6 (exercício 1.2 da secção 4.5); o 1.1 também está aqui.
P = [[1, -2, 3, 1, -3],
     [2, -1, 3, -1, 0]]

desafios = [
    Solucao([[1, 1, 3], [1, -1, 1]], (2, 1)),        # o que é uma solução
    Solucao([[1, 1, 3], [1, -1, 1]], (1, 2)),
    Escalonar([[1, 1, 3],                            # resolver: forma escalonada reduzida
               [1, -1, 1]], objetivo="reduzida", forma="sistema", recursos="todos"),
    Escalonar([[2, 1, 5],
               [1, 3, 5]], objetivo="reduzida", forma="sistema"),
    Escalonar([[1, 1, -1, -2],
               [1, -2, 1, 5],
               [-1, 2, 1, 3]], objetivo="reduzida", forma="sistema"),
    Escalonar(P, objetivo="reduzida", forma="sistema"),
    Classificar([[1, 1, 3],                          # classificar: impossível, determinado, indeterminado
                 [0, 1, 1]]),
    Classificar([[1, 2, 3],
                 [0, 0, 5]]),
    Classificar([[1, -2, 3, 1, -3],
                 [0, 3, -3, -3, 6]]),
    Grau([[1, -2, 3, 1, -3],                         # grau de indeterminação: incógnitas livres
          [0, 3, -3, -3, 6]]),
    Classificar([[1, 2, 5],
                 [2, 4, 10]]),
    Classificar([[1, 2, 0],                          # sistemas homogéneos: nunca são impossíveis
                 [0, 1, 0]]),
    Classificar([[1, 2, 3, 0],
                 [0, 1, 1, 0]]),
    Grau([[1, 2, 3, 0],
          [0, 1, 1, 0]]),
]
