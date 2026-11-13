from engine import *

titulo = "Matriz Inversa"

# Sebenta, cap. 5: matriz regular e o método [A | I] -> [I | inversa].
desafios = [
    Regular([[1, 2], [3, 4]]),
    Regular([[1, 2], [2, 4]]),                       # uma linha é o dobro da outra: não é regular
    Inversa([[1, 1],
             [0, 1]]),
    Inversa([[2, 1],
             [1, 1]]),
    Inversa([[1, 2],
             [3, 4]]),                               # aparecem frações
    Inversa([[1, 1, 0],
             [0, 1, 1],
             [0, 0, 1]]),
    Regular([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
]
