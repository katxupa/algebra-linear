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
| `nao_escalonada` | carregou em ✓ mas a matriz ainda não está em escada | 3, 4, 5, 6 | ⬜ falta |
| `nao_reduzida` | está escalonada, mas não reduzida (pivôs ≠ 1 ou números acima dos pivôs) | 3, 4, 5, 6 | ⬜ falta |
| `multiplicar_por_zero` | tentou multiplicar uma linha por 0 | 3, 4, 5, 6 | ⬜ falta |
| `mesma_linha` | tentou trocar/somar uma linha com ela própria | 3, 4, 5, 6 | ⬜ falta |
| `comando` | montou uma operação que não é elementar ou está incompleta | 3, 4, 5, 6 | ⬜ falta |
| `coluna_sistema` | num sistema, tentou multiplicar/somar colunas (só se pode trocar) | 3, 4, 5, 6 | ⬜ falta |
| `operacao` | (opcional) fez uma operação válida — som curto de confirmação | 3, 4, 5, 6 | ⬜ falta |
| `incognita_livre` | disse determinado, mas há incógnitas livres (c(A) < n) | 7, 8, 9, 11, 12, 13 | ⬜ falta |
| `linha_impossivel` | disse possível, mas há uma linha do tipo 0 = número (c(A) ≠ c([A|B])) | 7, 8, 9, 11, 12, 13 | ⬜ falta |
| `nao_impossivel` | disse impossível, mas o sistema tem solução | 7, 8, 9, 11, 12, 13 | ⬜ falta |
| `homogeneo_impossivel` | disse impossível num sistema homogéneo (tem sempre a solução nula) | 7, 8, 9, 11, 12, 13 | ⬜ falta |
| `contou_pivots` | deu o número de pivots (c(A)) em vez das incógnitas livres (n − c(A)) | 10, 14 | ⬜ falta |

## Desafios

1. o ponto é solução do sistema?
2. o ponto é solução do sistema?
3. escalonar matriz 2x3 até forma reduzida
4. escalonar matriz 2x3 até forma reduzida
5. escalonar matriz 3x4 até forma reduzida
6. escalonar matriz 2x5 até forma reduzida
7. classificar o sistema: possível determinado
8. classificar o sistema: impossível
9. classificar o sistema: possível indeterminado
10. grau de indeterminação = 2
11. classificar o sistema: possível indeterminado
12. classificar o sistema: possível determinado
13. classificar o sistema: possível indeterminado
14. grau de indeterminação = 1
