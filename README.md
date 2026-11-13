# Álgebra Linear: jogo interativo

Aulas de álgebra linear onde se aprende **mexendo**: arrastar vetores, mover î e ĵ,
editar matrizes. Sem textos a explicar: o jogador tenta, erra, ouve o narrador e tenta de novo.
Funciona no computador e no navegador (também no telemóvel).

**Jogar no navegador:** <https://katxupa.github.io/algebra-linear/> (publicado sozinho a cada
push na `main`, pelo workflow `.github/workflows/pages.yml`).

## Correr

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py            # menu
.venv\Scripts\python main.py --aula 2   # entra direto na aula 2
```

Versão web (abre em http://localhost:8000):

```bash
.venv\Scripts\pygbag --template web/black.tmpl .
```

`pygbag --build --template web/black.tmpl .` gera só o site em `build/web/` para publicar.

## Criar uma aula nova

As aulas seguem a ordem da sebenta de ALGA I:

| N.º | Aula | Estado |
|---|---|---|
| 1 | Corpo | feita |
| 2 | Matrizes | feita |
| 3 | Operações com Matrizes | em breve |
| 4 | Escalonamento | feita |
| 5 | Sistemas | feita (falta classificar sistemas) |
| 6 | Matriz Inversa | em breve |
| 7 | Determinantes | em breve |
| 8 | Cramer e Adjunta | em breve |
| 9 | Extra: Vetores | feita (fora da sebenta) |
| 10 | Extra: Matrizes no Plano | feita (fora da sebenta) |

Uma aula com `desafios = []` aparece no menu como "em breve" e não abre.

Para criar outra, criar a pasta `aulas/aula_11/` com um `lesson.py`:

```python
from engine import *

titulo = "Combinações"

desafios = [
    MoverVetor(para=(3, 2), mostrar_alvo=True),
    SomarVetores((2, 1), (1, 2)),
    Escalar((1, 2), por=3),
    MoverBase(matriz=[[2, 0], [0, 1]], ver="forma"),
    EditarMatriz(alvo=[[1, 2], [0, 1]]),
    Determinante(area=-2),
]
```

A matéria segue a sebenta de ALGA I: ver [docs/materia.md](docs/materia.md).

A aula aparece sozinha no menu. Se o `lesson.py` tiver um erro, o cartão fica vermelho e o
jogo continua a funcionar.

| Desafio | O jogador... | Erros que o motor reconhece |
|---|---|---|
| `Neutro("+")` / `Neutro("·")` | completa `7 + ▢ = 7` tocando num número | `neutro_trocado` |
| `Simetrico(a)` | completa `a + ▢ = 0` | `simetrico_inverso` |
| `Inverso(a)` | completa `a · ▢ = 1` (com `Inverso(0)` a resposta é "não existe") | `simetrico_inverso`, `dividir_por_zero` |
| `Comutativa(a, b)` / `Comutativa(a, b, "·")` | completa `a + b = b + ▢` | `comutatividade` |
| `Associativa(a, b, c)` | completa `(a + b) + c = a + (b + ▢)` | `associatividade` |
| `Distributiva(a, b, c)` | completa `a · (b + c) = a · b + ▢` | `distributividade` |
| `Entrada(A, i, j)` | toca na entrada a<sub>ij</sub> da matriz | `trocou_ij`, `so_linha`, `so_coluna` |
| `Tipo(A)` | escolhe o tipo m × n | `trocou_mn` |
| `Forma(A)` | escolhe: matriz linha, coluna, quadrada ou retangular | `linha_coluna` |
| `Diagonal(A)` | marca as entradas da diagonal principal (✓) | `diagonal_errada`, `incompleto` |
| `Traco(A)` | escolhe o valor de tr(A) | `diagonal_errada`, `somou_tudo` |
| `Zerar(A, "triangular superior")` | toca nas entradas que têm de passar a 0 (também `"triangular inferior"` e `"diagonal"`) (✓) | `triangulo_trocado`, `diagonal_apagada`, `incompleto` |
| `Qual("identidade")` | toca na matriz certa entre quatro (também `"escalar"`, `"diagonal"`, `"nula"`, `"triangular superior"`, `"triangular inferior"`) | `triangulo_trocado`, `diagonal_errada` |
| `Submatriz(A, ficar=(linhas, colunas))` ou `tirar=(...)` | risca linhas e colunas até sobrar A[linhas \| colunas] ou A(linhas \| colunas) (✓) | `parenteses_trocados`, `so_linha`, `so_coluna` |
| `Escalonar(matriz, objetivo="escalonada" ou "reduzida")` | monta cada operação elementar numa calculadora (`L3` `→` `L3` `−` `2` `L1` `=`) ou escrevendo no teclado; nada é sugerido; termina com ✓. Opções: `forma="sistema"`, `aumentada=False`, `colunas=True` (operações de coluna: `C1 ↔ C2`, `C2 → C2 − 3C1`, `C1 → 2C1`; num sistema só a troca) | `nao_escalonada`, `nao_reduzida`, `multiplicar_por_zero`, `mesma_linha`, `comando`, `coluna_sistema` |
| `MoverVetor(para=(x, y))` | arrasta a ponta do vetor até às coordenadas | `trocou_xy`, `sinal`, `quase` |
| `SomarVetores(v, w)` | encosta o início de w na ponta de v | `ao_contrario`, `quase` |
| `Escalar(v, por=k)` | arrasta um vetor até k·v | `sinal`, `paralelo`, `quase` |
| `Segurar(peso=p, cordas=[...], vento=(x, y))` | cena: um boneco pendurado sobre a água. Arrasta a força que falta para a soma dar zero e carrega em ✓; se a soma não for zero, o boneco vai atrás dela | `caiu`, `voou`, `de_lado` |
| `MoverBase(matriz=...)` | arrasta î e ĵ, a grelha segue (✓ para confirmar) | `trocou_base`, `transposta`, `sinal`, `quase` |
| `EditarMatriz(alvo=...)` | carrega em +/− nos números até cobrir a forma (✓) | iguais ao MoverBase |
| `Determinante(area=a)` | arrasta î e ĵ até a área ser a (✓) | `orientacao`, `zero`, `quase` |

Opções em qualquer desafio: `dica_apos=3` (falhas até aparecer a dica) e
`audio="nome"` (áudio próprio no início desse desafio).

## Áudio (narrador)

Ficheiros `.ogg` com o nome da situação:

- `aulas/_audio/`: partilhados por todas as aulas
- `aulas/aula_N/audio/`: só dessa aula (substituem os partilhados)

Situações: `intro`, `sucesso`, `erro`, `dica`, `parado`, `fim` e os erros da tabela acima.
Várias versões da mesma situação (`sucesso_1.ogg`, `sucesso_2.ogg`...) são tocadas à sorte.
Se faltar o áudio de um erro específico, toca `erro`.

O narrador **não fala em todas as respostas** (cansava). O feedback visual aparece sempre, mas a voz segue
regras em `engine/narrador.py`, com os números todos no topo do ficheiro para afinar:
- `intro`, `fim` e `dica` tocam sempre;
- erros específicos (`trocou_xy`, `dividir_por_zero`, ...) tocam, mas o mesmo não se repete antes de 25 s;
- a cada 3 acertos seguidos toca `sequencia`; num acerto depois de 2+ erros toca `finalmente`
  (sem essas gravações, toca `sucesso`);
- `sucesso` e `erro` genéricos: sempre na primeira vez; fora disso só às vezes (30%) e com 15 s de intervalo;
- `operacao` (escalonamento) é raro (12%);
- nunca fala por cima de outra fala nem antes de 4 s de silêncio.

```bash
.venv\Scripts\python tools/roteiro.py aula_1             # lista o que gravar -> aulas/aula_1/audio/ROTEIRO.md
.venv\Scripts\python tools/roteiro.py aula_1 --convert   # converte .wav/.mp3 dessa pasta para .ogg
```

Sem áudio gravado o jogo fica em silêncio (só o feedback visual). Para testar com bips
provisórios: `tools/sons_teste.py` (apague-os depois). Guião das falas: `docs/falas.md`.

Depois de gravar, corte o silêncio do início e do fim (os originais ficam em `gravacoes_originais/`):

```bash
.venv\Scripts\python tools/aparar.py
```

Os áudios vão para o git pelo **Git LFS** (`.gitattributes`), para o repositório não ficar pesado.
Quem clonar o projeto precisa do Git LFS instalado (vem com o Git para Windows).

## Idioma

Todos os textos do jogo estão em `engine/textos.py` (`pt` e `kea` = kriolu).
Mudar `IDIOMA = "kea"` troca o jogo todo. Os títulos das aulas e os áudios são escritos/gravados
na língua que quiser.

## Estrutura

- `engine/`: o motor (desenho, input, áudio, tipos de desafio). Um desafio novo é uma classe em
  `engine/challenges/` que todas as aulas podem usar.
- `aulas/`: as aulas
- `tools/`: roteiro de áudio e sons de teste
- `tests/`: `python -m pytest`
