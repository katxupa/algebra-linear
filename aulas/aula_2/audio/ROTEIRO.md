# Roteiro de áudio: aula_2 (Matrizes)

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
| `trocou_ij` | trocou a linha com a coluna (tocou em a_ji em vez de a_ij) | 1, 2, 3 | ⬜ falta |
| `so_linha` | acertou na linha, errou na coluna | 1, 2, 3, 17, 18 | ⬜ falta |
| `so_coluna` | acertou na coluna, errou na linha | 1, 2, 3, 17, 18 | ⬜ falta |
| `trocou_mn` | trocou linhas com colunas (disse n × m em vez de m × n) | 4, 5 | ⬜ falta |
| `linha_coluna` | confundiu matriz linha com matriz coluna | 6, 7, 8, 9 | ⬜ falta |
| `diagonal_errada` | marcou a outra diagonal (a secundária) | 10, 11, 15, 16 | ⬜ falta |
| `incompleto` | o que marcou está certo, mas falta marcar entradas | 10, 12, 13, 14 | ⬜ falta |
| `somou_tudo` | somou todas as entradas da matriz | 11 | ⬜ falta |
| `triangulo_trocado` | pôs os zeros do lado errado da diagonal (superior ↔ inferior) | 12, 13, 14, 15, 16 | ⬜ falta |
| `diagonal_apagada` | pôs zeros também na diagonal principal | 12, 13, 14 | ⬜ falta |
| `parenteses_trocados` | fez o contrário: ficou com o que era para tirar (confundiu [ ] com ( )) | 17, 18 | ⬜ falta |

## Desafios

1. tocar na entrada a12
2. tocar na entrada a31
3. tocar na entrada a24
4. tipo da matriz: 3 × 2
5. tipo da matriz: 1 × 4
6. matriz linha
7. matriz coluna
8. matriz quadrada
9. matriz retangular
10. marcar a diagonal principal
11. traço = 11
12. pôr zeros até a matriz ser triangular superior
13. pôr zeros até a matriz ser triangular inferior
14. pôr zeros até a matriz ser diagonal
15. qual é a matriz escalar?
16. qual é a matriz identidade?
17. submatriz A[1,3 | 2,3,4]
18. submatriz A(2,4 | 1)
