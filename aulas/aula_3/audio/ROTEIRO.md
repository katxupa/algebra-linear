# Roteiro de áudio: aula_3 (Matrizes)

Grave em .ogg (ou .wav e rode com `--convert`). Variações: `chave_1.ogg`, `chave_2.ogg`...

## Gerais

| chave | quando toca | status |
|---|---|---|
| `intro` | começo da aula | ⬜ falta |
| `sucesso` | acertou um desafio (grave várias variações curtas!) | ☑️ 6 compartilhado(s) |
| `erro` | errou (genérico, quando não é um erro conhecido) | ⬜ falta |
| `dica` | errou várias vezes seguidas: aparece uma dica visual | ⬜ falta |
| `parado` | ficou 20s sem mexer em nada | ⬜ falta |
| `fim` | terminou a aula | ⬜ falta |

## Erros conhecidos (se faltar, toca `erro`)

| chave | quando toca | desafios | status |
|---|---|---|---|
| `trocou_base` | trocou î com ĵ (colunas trocadas) | 1, 2, 3, 4, 5, 6 | ⬜ falta |
| `transposta` | leu a matriz por linhas em vez de colunas (transposta) | 1, 2, 3, 4, 5, 6 | ⬜ falta |
| `sinal` | números certos, algum sinal (+/−) errado | 1, 2, 3, 4, 5, 6 | ⬜ falta |
| `quase` | só um número errado por 1 | 1, 2, 3, 4, 5, 6, 7, 8 | ⬜ falta |
| `orientacao` | área certa, mas virada (sinal do determinante trocado: î e ĵ invertidos) | 7, 8 | ⬜ falta |
| `zero` | esmagou tudo numa linha (área 0) | 7, 8 | ⬜ falta |

## Desafios

1. mover î e ĵ para formar [[2, 0], [0, 1]]
2. mover î e ĵ para formar [[0, -1], [1, 0]]
3. mover î e ĵ para formar [[1, 1], [0, 1]]
4. mover î e ĵ para formar [[2, -1], [1, 2]]
5. editar matriz até [[1, 2], [0, 1]]
6. editar matriz até [[-1, 0], [1, 2]]
7. área (determinante) = 2
8. área (determinante) = -3
