# Roteiro de áudio: aula_7 (Determinantes)

Grave em .ogg (ou .wav e rode com `--convert`). Variações: `chave_1.ogg`, `chave_2.ogg`...

## Gerais

| chave | quando toca | status |
|---|---|---|
| `intro` | começo da aula | ⬜ falta |
| `sucesso` | acertou um desafio (grave várias variações curtas!) | ☑️ 6 compartilhado(s) |
| `erro` | errou (genérico, quando não é um erro conhecido) | ☑️ 3 compartilhado(s) |
| `sequencia` | acertou várias seguidas sem errar (a cada 3); se faltar, toca sucesso | ⬜ falta |
| `finalmente` | acertou depois de errar 2+ vezes; se faltar, toca sucesso | ⬜ falta |
| `dica` | errou várias vezes seguidas: aparece uma dica visual | ⬜ falta |
| `parado` | ficou 20s sem mexer em nada | ⬜ falta |
| `fim` | terminou a aula | ⬜ falta |

## Erros conhecidos (se faltar, toca `erro`)

| chave | quando toca | desafios | status |
|---|---|---|---|
| `sinal` | valor certo, sinal errado | 5, 6, 9, 10, 11 | ⬜ falta |
| `so_diagonal` | multiplicou só a diagonal principal (isso só serve para matrizes triangulares) | 5, 6, 9, 10, 11 | ⬜ falta |
| `somou` | somou os dois produtos em vez de os subtrair | 5, 6, 9, 10, 11 | ⬜ falta |
| `sinal_cofator` | calculou o determinante menor e esqueceu o sinal (−1)^(i+j) | 7, 8 | ⬜ falta |
| `entrada` | respondeu com a entrada a_ij em vez do cofator | 7, 8 | ⬜ falta |
| `troca_sinal` | trocou duas linhas e esqueceu que o determinante muda de sinal | 12, 13, 14 | ⬜ falta |
| `fator_esquecido` | multiplicou uma linha por k e esqueceu de multiplicar o determinante por k | 12, 13, 14 | ⬜ falta |
| `combina_muda` | somou a uma linha um múltiplo de outra e achou que o determinante mudava | 12, 13, 14 | ⬜ falta |
| `det_soma` | somou os determinantes: o determinante do produto é o PRODUTO dos determinantes | 15, 16, 17, 18 | ⬜ falta |
| `fator_n` | multiplicou por k só uma vez: o k sai de cada linha, fica k elevado à ordem da matriz | 15, 16, 17, 18 | ⬜ falta |
| `det_transposta` | achou que transpor muda o determinante | 15, 16, 17, 18 | ⬜ falta |
| `det_inversa` | não inverteu: o determinante da inversa é 1 / |A| | 15, 16, 17, 18 | ⬜ falta |
| `det_zero` | disse que é regular, mas o determinante é 0 (as linhas dependem umas das outras) | 19, 20 | ⬜ falta |

## Desafios

1. inversões da permutação [1, 3, 2]: 1
2. inversões da permutação [3, 1, 2]: 2
3. paridade da permutação [3, 1, 2]
4. paridade da permutação [2, 1, 3]
5. determinante = −2
6. determinante = 1
7. cofator A21 = 4
8. cofator A11 = 1
9. determinante = 8
10. determinante = 36
11. determinante = 0
12. determinante depois de L1 ↔ L2
13. determinante depois de L1 → 3L1
14. determinante depois de L2 → L2 − 3L1
15. propriedade do determinante (produto): 6
16. propriedade do determinante (transposta): 5
17. propriedade do determinante (escalar): 12
18. propriedade do determinante (inversa): 1/4
19. a matriz é regular?
20. a matriz é regular?
