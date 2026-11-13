# Matéria de referência

O jogo segue a sebenta de **Álgebra Linear e Geometria Analítica I**: "Corpos, matrizes,
determinantes e sistemas de equações lineares" (Grupo ALGA I, 44 páginas). O PDF não está no
repositório.

## O que a sebenta tem e o que o jogo já cobre

| Cap. | Matéria | No jogo hoje | Falta |
|---|---|---|---|
| 1 | **Corpo**: operação binária; associativa, neutro, simétrico, comutativa (+); associativa, distributiva, unidade, comutativa, inverso (·); ℝ e ℚ são corpos | Aula 1: neutro, simétrico, inverso, comutativa, associativa, distributiva, "0 não tem inverso" | operação binária (o resultado fica dentro do conjunto); porque é que ℤ e ℕ não são corpos |
| 2.1 | **Matriz**: tipo m×n, entrada a<sub>ij</sub>, linha, coluna, submatriz | Aula 2: entradas, tipo, matriz linha / coluna / quadrada / retangular, submatriz nas duas notações | matriz definida por uma fórmula (b<sub>ij</sub> = i<sup>j−1</sup>) |
| 2.2 | **Matrizes quadradas**: triangular superior e inferior, diagonal, escalar, identidade | Aula 2: diagonal principal, traço, triangular superior e inferior, diagonal, escalar, identidade | matriz nula (o motor já tem, falta pôr na aula) |
| 2.3 | **Álgebra das matrizes**: igualdade, transposta, simétrica e anti-simétrica, soma, produto por escalar, produto (linha × coluna), matrizes comutáveis, potências, a identidade como neutro | o extra "Matrizes no Plano" (Aula 10) trata a matriz como transformação do plano, que não é a abordagem da sebenta | tudo, na forma da sebenta |
| 3.1 | **Operações elementares**, forma escalonada e escalonada reduzida | Aula 4: calculadora de operações, linhas e colunas | — |
| 3.2 | **Característica** de uma matriz | nada | contar os pivots depois de escalonar |
| 4.1–4.2 | **SEL**: equação linear, solução, AX = B, matriz ampliada | Aula 5: resolver até à forma escalonada reduzida (inclui os exercícios 1.1 e 1.2 da secção 4.5) | verificar se um ponto é solução |
| 4.3 | **Classificação**: impossível, possível determinado, possível indeterminado (c(A), c([A\|B]) e n); grau de indeterminação; incógnitas livres | nada | tudo |
| 4.4 | **Sistema homogéneo** | nada | tudo |
| 5 | **Matriz regular**: inversa, propriedades, método [A \| I] → [I \| A⁻¹] | nada (a calculadora da Aula 4 já serve) | tudo |
| 6.1 | **Permutações**: inversões e paridade | nada | tudo |
| 6.2–6.3 | **Determinante**: definição, Laplace (cofatores), efeito das operações elementares, propriedades | Aula 10 (extra): só a área 2×2 | tudo, na forma da sebenta |
| 6.5–6.7 | det ≠ 0 ⇔ regular; inversa pela **adjunta**; **sistema de Cramer** | nada | tudo |

Os **vetores** não fazem parte desta sebenta: ficam na Aula 9 (extra), com a cena das cordas.

## Ordem das aulas (segue a sebenta)

| N.º | Aula | Estado |
|---|---|---|
| 1 | Corpo | feita |
| 2 | Matrizes: tipo, entradas, tipos de matrizes quadradas | feita |
| 3 | Operações com Matrizes: soma, escalar, transposta, produto | em breve |
| 4 | Escalonamento | feita; falta a característica |
| 5 | Sistemas | resolver: feita; falta classificar e o sistema homogéneo |
| 6 | Matriz Inversa | em breve |
| 7 | Determinantes | em breve |
| 8 | Cramer e Adjunta | em breve |
| 9 | Extra: Vetores | feita (fora da sebenta) |
| 10 | Extra: Matrizes no Plano | feita (fora da sebenta) |

A sebenta escreve as operações com a seta para a esquerda (`L2 ← L2 − 2L1`); o jogo mostra
`L2 → L2 − 2L1` e aceita as duas formas no teclado.

## Situações "reais" por capítulo (ideias)

| Matéria | Situação | Se o aluno errar |
|---|---|---|
| Corpo | Balança: o simétrico são balões, o neutro é uma pena | a balança vira e atira o boneco |
| Tipo m×n e produto | Cantina: matriz de pedidos × coluna de preços = conta de cada mesa. Tipos que não encaixam não se multiplicam | a conta sai absurda e o cozinheiro zanga-se |
| Transposta, simétrica | Espelho: a matriz dobra-se pela diagonal | o reflexo sai torto |
| Escalonamento | Escada do farol: cada zero abaixo do pivot é um degrau | o degrau falha |
| Classificação de SEL | Bote com cargas: determinado = só uma arrumação; indeterminado = várias; impossível = afunda sempre | o bote vira |
| Característica | Cordas a segurar um piano: uma corda que é cópia de outra não conta | o piano cai |
| Inversa | Prédio torto: a inversa endireita-o; se o determinante for 0 fica panqueca e não há volta | o prédio tomba |
| Determinante | Trocar duas linhas troca o sinal: o prédio fica virado ao contrário | prédio de pernas para o ar |
| Cramer | Três planos (3D em linhas) cruzam-se num ponto: é lá que o boneco está seguro | o boneco fica fora do ponto e cai |
