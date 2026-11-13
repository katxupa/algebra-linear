# Roteiro de áudio: aula_4 (Escalonamento)

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
| `nao_escalonada` | carregou em ✓ mas a matriz ainda não está em escada | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `nao_reduzida` | está escalonada, mas não reduzida (pivôs ≠ 1 ou números acima dos pivôs) | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `multiplicar_por_zero` | tentou multiplicar uma linha por 0 | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `mesma_linha` | tentou trocar/somar uma linha com ela própria | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `comando` | montou uma operação que não é elementar ou está incompleta | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `coluna_sistema` | num sistema, tentou multiplicar/somar colunas (só se pode trocar) | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `operacao` | (opcional) fez uma operação válida — som curto de confirmação | 1, 2, 3, 4, 5, 6, 7, 8, 9 | ⬜ falta |
| `contou_linhas` | contou todas as linhas, mesmo as que ficam nulas depois de escalonar | 10, 11, 12, 13 | ⬜ falta |

## Desafios

1. escalonar matriz 2x3 até forma escalonada
2. escalonar matriz 2x3 até forma escalonada
3. escalonar matriz 2x3 até forma escalonada
4. escalonar matriz 3x4 até forma escalonada
5. escalonar matriz 3x4 até forma escalonada
6. escalonar matriz 2x3 até forma reduzida
7. escalonar matriz 3x4 até forma reduzida
8. escalonar matriz 3x4 até forma escalonada
9. escalonar matriz 3x3 até forma escalonada
10. característica = 3
11. característica = 2
12. característica = 1
13. característica = 2
