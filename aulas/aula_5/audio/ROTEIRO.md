# Roteiro de áudio: aula_5 (Sistemas)

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
| `nao_escalonada` | carregou em ✓ mas a matriz ainda não está em escada | 1, 2, 3, 4 | ⬜ falta |
| `nao_reduzida` | está escalonada, mas não reduzida (pivôs ≠ 1 ou números acima dos pivôs) | 1, 2, 3, 4 | ⬜ falta |
| `multiplicar_por_zero` | tentou multiplicar uma linha por 0 | 1, 2, 3, 4 | ⬜ falta |
| `mesma_linha` | tentou trocar/somar uma linha com ela própria | 1, 2, 3, 4 | ⬜ falta |
| `comando` | montou uma operação que não é elementar ou está incompleta | 1, 2, 3, 4 | ⬜ falta |
| `coluna_sistema` | num sistema, tentou multiplicar/somar colunas (só se pode trocar) | 1, 2, 3, 4 | ⬜ falta |
| `operacao` | (opcional) fez uma operação válida — som curto de confirmação | 1, 2, 3, 4 | ⬜ falta |

## Desafios

1. escalonar matriz 2x3 até forma reduzida
2. escalonar matriz 2x3 até forma reduzida
3. escalonar matriz 3x4 até forma reduzida
4. escalonar matriz 2x5 até forma reduzida
