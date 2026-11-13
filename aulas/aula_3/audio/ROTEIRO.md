# Roteiro de áudio: aula_3 (Operações com Matrizes)

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
| `nao_transpos` | copiou a matriz sem trocar as linhas com as colunas | 1, 2 | ⬜ falta |
| `incompleto` | o que escreveu está certo, mas ainda faltam entradas | 1, 2, 6, 7, 8, 12, 13, 14, 15, 16, 17 | ⬜ falta |
| `simetrica_trocada` | confundiu simétrica com anti-simétrica | 3, 4, 5 | ⬜ falta |
| `sinal` | somou em vez de subtrair (ou o contrário) | 6, 7 | ⬜ falta |
| `tipo_de_dentro` | usou os números de dentro (colunas de A × linhas de B) para o tipo do produto | 9, 10, 11 | ⬜ falta |
| `nao_compativel` | deu um tipo a um produto que não existe (colunas de A ≠ linhas de B) | 9, 10, 11 | ⬜ falta |
| `entrada_a_entrada` | multiplicou entrada por entrada, em vez de linha por coluna | 12, 13, 14, 15, 16, 17 | ⬜ falta |
| `ordem_trocada` | calculou B · A em vez de A · B | 12, 13, 14, 15, 16 | ⬜ falta |

## Desafios

1. transposta de A
2. transposta de A
3. matriz simétrica
4. matriz anti-simétrica
5. matriz nenhuma das duas
6. A + B
7. A − B
8. 3 · A
9. tipo do produto (2 × 3) · (3 × 2)
10. tipo do produto (2 × 3) · (2 × 3)
11. tipo do produto (3 × 1) · (1 × 3)
12. produto A · B
13. produto A · B
14. produto A · B
15. produto A · B
16. produto A · B
17. potência A^2
