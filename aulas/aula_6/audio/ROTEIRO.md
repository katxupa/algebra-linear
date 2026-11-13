# Roteiro de áudio: aula_6 (Matriz Inversa)

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
| `det_zero` | disse que é regular, mas o determinante é 0 (as linhas dependem umas das outras) | 1, 2, 7 | ⬜ falta |
| `nao_escalonada` | carregou em ✓ mas a matriz ainda não está em escada | 3, 4, 5, 6 | ⬜ falta |
| `nao_reduzida` | está escalonada, mas não reduzida (pivôs ≠ 1 ou números acima dos pivôs) | 3, 4, 5, 6 | ⬜ falta |
| `multiplicar_por_zero` | tentou multiplicar uma linha por 0 | 3, 4, 5, 6 | ⬜ falta |
| `mesma_linha` | tentou trocar/somar uma linha com ela própria | 3, 4, 5, 6 | ⬜ falta |
| `comando` | montou uma operação que não é elementar ou está incompleta | 3, 4, 5, 6 | ⬜ falta |
| `coluna_sistema` | num sistema, tentou multiplicar/somar colunas (só se pode trocar) | 3, 4, 5, 6 | ⬜ falta |
| `operacao` | (opcional) fez uma operação válida — som curto de confirmação | 3, 4, 5, 6 | ⬜ falta |

## Desafios

1. a matriz é regular?
2. a matriz é regular?
3. inversa pelo método [A | I]
4. inversa pelo método [A | I]
5. inversa pelo método [A | I]
6. inversa pelo método [A | I]
7. a matriz é regular?
