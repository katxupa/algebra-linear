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
| `trocou_ij` | trocou a linha com a coluna (tocou em a_ji em vez de a_ij) | 1, 2, 3, 4, 5 | ⬜ falta |
| `so_linha` | acertou na linha, errou na coluna | 1, 2, 3, 20, 21 | ⬜ falta |
| `so_coluna` | acertou na coluna, errou na linha | 1, 2, 3, 20, 21 | ⬜ falta |
| `incompleto` | o que escreveu está certo, mas ainda faltam entradas | 4, 5, 12, 14, 15, 16 | ⬜ falta |
| `trocou_mn` | trocou linhas com colunas (disse n × m em vez de m × n) | 6, 7 | ⬜ falta |
| `linha_coluna` | confundiu matriz linha com matriz coluna | 8, 9, 10, 11 | ⬜ falta |
| `diagonal_errada` | marcou a outra diagonal (a secundária) | 12, 13, 17, 18, 19 | ⬜ falta |
| `somou_tudo` | somou todas as entradas da matriz | 13 | ⬜ falta |
| `triangulo_trocado` | pôs os zeros do lado errado da diagonal (superior ↔ inferior) | 14, 15, 16, 17, 18, 19 | ⬜ falta |
| `diagonal_apagada` | pôs zeros também na diagonal principal | 14, 15, 16 | ⬜ falta |
| `parenteses_trocados` | fez o contrário: ficou com o que era para tirar (confundiu [ ] com ( )) | 20, 21 | ⬜ falta |

## Desafios

1. tocar na entrada a12
2. tocar na entrada a31
3. tocar na entrada a24
4. matriz com a_ij = i + j
5. matriz com a_ij = i ^ (j − 1)
6. tipo da matriz: 3 × 2
7. tipo da matriz: 1 × 4
8. matriz linha
9. matriz coluna
10. matriz quadrada
11. matriz retangular
12. marcar a diagonal principal
13. traço = 11
14. pôr zeros até a matriz ser triangular superior
15. pôr zeros até a matriz ser triangular inferior
16. pôr zeros até a matriz ser diagonal
17. qual é a matriz escalar?
18. qual é a matriz identidade?
19. qual é a matriz nula?
20. submatriz A[1,3 | 2,3,4]
21. submatriz A(2,4 | 1)
