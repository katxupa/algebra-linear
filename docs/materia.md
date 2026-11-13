# Matéria de referência

O jogo segue a sebenta de **Álgebra Linear e Geometria Analítica I**: "Corpos, matrizes,
determinantes e sistemas de equações lineares" (Grupo ALGA I, 44 páginas). O PDF não está no
repositório.

## O que a sebenta tem e o que o jogo já cobre

| Cap. | Matéria | No jogo hoje | Falta |
|---|---|---|---|
| 1 | **Corpo**: operação binária; associativa, neutro, simétrico, comutativa (+); associativa, distributiva, unidade, comutativa, inverso (·); ℝ e ℚ são corpos | Aula 1: neutro, simétrico, inverso, comutativa, associativa, distributiva, "0 não tem inverso" | operação binária (o resultado fica dentro do conjunto); porque é que ℤ e ℕ não são corpos |
| 2.1 | **Matriz**: tipo m×n, entrada a<sub>ij</sub>, linha, coluna, submatriz | nada | tudo |
| 2.2 | **Matrizes quadradas**: triangular superior e inferior, diagonal, escalar, identidade | nada | tudo |
| 2.3 | **Álgebra das matrizes**: igualdade, transposta, simétrica e anti-simétrica, soma, produto por escalar, produto (linha × coluna), matrizes comutáveis, potências, a identidade como neutro | Aula 3 trata a matriz como transformação do plano (não é a abordagem da sebenta) | tudo, na forma da sebenta |
| 3.1 | **Operações elementares**, forma escalonada e escalonada reduzida | Aula 4: calculadora de operações, linhas e colunas | — |
| 3.2 | **Característica** de uma matriz | nada | contar os pivots depois de escalonar |
| 4.1–4.2 | **SEL**: equação linear, solução, AX = B, matriz ampliada | Aula 4: vista "sistema" | verificar se um ponto é solução |
| 4.3 | **Classificação**: impossível, possível determinado, possível indeterminado (c(A), c([A\|B]) e n); grau de indeterminação; incógnitas livres | nada | tudo |
| 4.4 | **Sistema homogéneo** | nada | tudo |
| 5 | **Matriz regular**: inversa, propriedades, método [A \| I] → [I \| A⁻¹] | nada (a calculadora da Aula 4 já serve) | tudo |
| 6.1 | **Permutações**: inversões e paridade | nada | tudo |
| 6.2–6.3 | **Determinante**: definição, Laplace (cofatores), efeito das operações elementares, propriedades | Aula 3: só a área 2×2 | tudo, na forma da sebenta |
| 6.5–6.7 | det ≠ 0 ⇔ regular; inversa pela **adjunta**; **sistema de Cramer** | nada | tudo |

Os **vetores** (Aula 2) não fazem parte desta sebenta. A cena das cordas fica como aquecimento.

## Ordem de aulas proposta (segue a sebenta)

1. Corpo
2. Matrizes: tipo, entradas, tipos de matrizes quadradas
3. Operações com matrizes: soma, escalar, transposta, produto
4. Escalonamento e característica
5. Sistemas: resolver e classificar
6. Matriz inversa
7. Determinantes
8. Cramer e adjunta

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
