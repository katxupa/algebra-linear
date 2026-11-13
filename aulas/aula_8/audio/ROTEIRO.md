# Roteiro de áudio: aula_8 (Cramer e Adjunta)

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
| `nao_transpos` | escreveu a matriz dos cofatores sem a transpor | 1, 2 | ⬜ falta |
| `sinal_cofator` | esqueceu os sinais (−1)^(i+j) dos cofatores | 1, 2 | ⬜ falta |
| `incompleto` | o que escreveu está certo, mas ainda faltam entradas | 1, 2, 3, 4 | ⬜ falta |
| `faltou_dividir` | escreveu a adjunta e esqueceu de dividir pelo determinante | 3, 4, 6, 8, 10 | ⬜ falta |
| `coluna_errada` | substituiu outra coluna, não a da incógnita pedida | 5, 6, 7, 8, 9, 10 | ⬜ falta |
| `linha_coluna` | substituiu uma linha em vez de uma coluna | 5, 7, 9 | ⬜ falta |

## Desafios

1. adjunta de A
2. adjunta de A
3. inversa de A pela adjunta
4. inversa de A pela adjunta
5. regra de Cramer: qual é a matriz A1?
6. regra de Cramer: x1 = 2
7. regra de Cramer: qual é a matriz A2?
8. regra de Cramer: x2 = 1
9. regra de Cramer: qual é a matriz A2?
10. regra de Cramer: x3 = 1/3
