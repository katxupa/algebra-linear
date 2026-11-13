# Roteiro de áudio: aula_9 (Extra: Vetores)

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
| `trocou_xy` | trocou x e y (ex: colocou em (2,3) em vez de (3,2)) | 1, 2, 3, 4 | ⬜ falta |
| `sinal` | acertou os números mas errou o sinal (+/−) | 1, 2, 3, 4, 11, 12 | ⬜ falta |
| `quase` | ficou a 1 casinha do lugar certo | 1, 2, 3, 4, 5, 6, 11, 12 | ⬜ falta |
| `ao_contrario` | encostou a PONTA de w na ponta de v (em vez do início de w) | 5, 6 | ⬜ falta |
| `caiu` | a soma das forças aponta para baixo: o boneco cai à água | 7, 8, 9, 10 | ⬜ falta |
| `voou` | a soma das forças aponta para cima: o boneco sai disparado para o céu | 7, 8, 9, 10 | ⬜ falta |
| `de_lado` | para cima e para baixo está certo, mas sobra força para um lado | 7, 8, 9, 10 | ⬜ falta |
| `paralelo` | na direção certa, mas tamanho errado | 11, 12 | ⬜ falta |

## Início de desafio (`audio=`)

| chave | desafio | status |
|---|---|---|
| `cena_cordas` | 7 | ⬜ falta |

## Desafios

1. mover vetor até (3, 2)
2. mover vetor até (2, 3)
3. mover vetor até (-3, 1)
4. mover vetor até (-2, -4)
5. somar v=(2, 1) + w=(1, 2)
6. somar v=(-1, 3) + w=(3, -1)
7. segurar o boneco: falta a força (0, 3)
8. segurar o boneco: falta a força (2, 2)
9. segurar o boneco: falta a força (3, 2)
10. segurar o boneco: falta a força (-2, 2)
11. escalar 2·(1, 2)
12. escalar -1·(2, 1)
