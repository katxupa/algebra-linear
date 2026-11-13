# Matéria de referência

O jogo segue a sebenta de **Álgebra Linear e Geometria Analítica I**: "Corpos, matrizes,
determinantes e sistemas de equações lineares" (Grupo ALGA I, 44 páginas). O PDF não está no
repositório.

## O que a sebenta tem e o que o jogo cobre

| Cap. | Matéria | No jogo | Falta |
|---|---|---|---|
| 1 | **Corpo**: operação binária; os 9 axiomas; ℝ e ℚ são corpos | Aula 1: neutro, simétrico, inverso, comutativa, associativa, distributiva, "0 não tem inverso"; contas dentro de ℕ, ℤ e ℚ (ℕ e ℤ não são corpos) | — |
| 2.1 | **Matriz**: tipo m×n, entrada a<sub>ij</sub>, linha, coluna, submatriz | Aula 2: entradas, matriz dada por fórmula, tipo, linha / coluna / quadrada / retangular, submatriz nas duas notações | — |
| 2.2 | **Matrizes quadradas**: diagonal principal, traço, triangular, diagonal, escalar, identidade, nula | Aula 2: todas | — |
| 2.3 | **Álgebra das matrizes**: igualdade, transposta, simétrica e anti-simétrica, soma, produto por escalar, produto, comutáveis, potências, identidade como neutro | Aula 3: transposta, simétrica / anti-simétrica, soma e subtração, escalar, tipo do produto, produto (incluindo A·B ≠ B·A e a identidade), potência | igualdade de matrizes; os teoremas de propriedades (associativa, distributiva, (AB)<sup>t</sup> = B<sup>t</sup>A<sup>t</sup>, AA<sup>t</sup> simétrica) |
| 3.1 | **Operações elementares**, forma escalonada e escalonada reduzida | Aula 4: calculadora de operações, linhas e colunas | — |
| 3.2 | **Característica** | Aula 4: c(A) em matrizes escalonadas e por escalonar | as propriedades da característica (teorema 3.2) |
| 4.1–4.2 | **SEL**: equação linear, solução, AX = B, matriz ampliada | Aula 5: "é solução?", vista sistema / matriz | — |
| 4.3 | **Resolução e classificação**: impossível, possível determinado, possível indeterminado; grau de indeterminação; incógnitas livres | Aula 5: resolver até à forma reduzida (exercícios 1.1 e 1.2 da secção 4.5), classificar, grau de indeterminação | escrever o conjunto-solução com parâmetros |
| 4.4 | **Sistema homogéneo** | Aula 5: nunca é impossível; determinado ou indeterminado | solução geral = particular + homogéneo (teorema 4.3) |
| 5 | **Matriz regular**: inversa, propriedades, método [A \| I] → [I \| A⁻¹] | Aula 6: regular ou não, inversa pelo método [A \| I] (2×2 e 3×3) | propriedades das regulares ((AB)⁻¹ = B⁻¹A⁻¹, etc.) |
| 6.1 | **Permutações**: inversões e paridade | Aula 7 | a definição do determinante como soma sobre as permutações |
| 6.2–6.4 | **Determinante**: Laplace (cofatores), operações elementares, propriedades | Aula 7: ordem 2 e 3, cofator (exemplo 6.4), triangular, linhas iguais, efeito das três operações elementares, produto / transposta / escalar / inversa | desenvolver por uma linha ou coluna à escolha |
| 6.5–6.7 | det ≠ 0 ⇔ regular; inversa pela **adjunta**; **sistema de Cramer** | Aulas 7 e 8: regular pelo determinante, adjunta, inversa = adjunta / determinante, regra de Cramer (exemplo 6.11) | — |

Os **vetores** não fazem parte desta sebenta: ficam na Aula 9 (extra), com a cena das cordas.

## Ordem das aulas (segue a sebenta)

| N.º | Aula | Exercícios |
|---|---|---|
| 1 | Corpo | 17 |
| 2 | Matrizes | 21 |
| 3 | Operações com Matrizes | 17 |
| 4 | Escalonamento | 13 |
| 5 | Sistemas | 14 |
| 6 | Matriz Inversa | 7 |
| 7 | Determinantes | 20 |
| 8 | Cramer e Adjunta | 10 |
| 9 | Extra: Vetores | 12 (fora da sebenta) |
| 10 | Extra: Matrizes no Plano | 8 (fora da sebenta) |

A sebenta escreve as operações com a seta para a esquerda (`L2 ← L2 − 2L1`); o jogo mostra
`L2 → L2 − 2L1` e aceita as duas formas no teclado.

## Situações "reais" por capítulo (ideias, ainda por construir)

Só a cena das cordas (Aula 9) existe. As aulas 1 a 8 são, por agora, só com números.

| Matéria | Situação | Se o aluno errar |
|---|---|---|
| Corpo | Balança: o simétrico são balões, o neutro é uma pena | a balança vira e atira o boneco |
| Entrada a<sub>ij</sub> | Cinema: fila i, cadeira j | acorda o espectador errado |
| Tipo m×n e produto | Cantina: matriz de pedidos × coluna de preços = conta de cada mesa | a conta sai absurda e o cozinheiro zanga-se |
| Transposta, simétrica | Espelho: a matriz dobra-se pela diagonal | o reflexo sai torto |
| Escalonamento | Escada do farol: cada zero abaixo do pivot é um degrau | o degrau falha |
| Classificação de SEL | Bote com cargas: determinado = só uma arrumação; indeterminado = várias; impossível = afunda sempre | o bote vira |
| Característica | Cordas a segurar um piano: uma corda que é cópia de outra não conta | o piano cai |
| Inversa | Prédio torto: a inversa endireita-o; se o determinante for 0 fica panqueca e não há volta | o prédio tomba |
| Determinante | Trocar duas linhas troca o sinal: o prédio fica virado ao contrário | prédio de pernas para o ar |
| Cramer | Três planos (3D em linhas) cruzam-se num ponto: é lá que o boneco está seguro | o boneco fica fora do ponto e cai |
