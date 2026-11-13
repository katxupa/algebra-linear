from engine import *

titulo = "Sistemas"

# Sebenta, cap. 4: resolver um sistema levando a matriz ampliada à forma escalonada reduzida.
# Os dois últimos são os exercícios 1.1 e 1.2 da secção 4.5 (o 1.2 tem incógnitas livres).
# Falta no motor: classificar o sistema (impossível, determinado, indeterminado) e o homogéneo.
desafios = [
    Escalonar([[1, 1, 3],
               [1, -1, 1]], objetivo="reduzida", forma="sistema", recursos="todos"),
    Escalonar([[2, 1, 5],
               [1, 3, 5]], objetivo="reduzida", forma="sistema"),
    Escalonar([[1, 1, -1, -2],
               [1, -2, 1, 5],
               [-1, 2, 1, 3]], objetivo="reduzida", forma="sistema"),
    Escalonar([[1, -2, 3, 1, -3],
               [2, -1, 3, -1, 0]], objetivo="reduzida", forma="sistema"),
]
