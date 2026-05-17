# Ordem de Prioridade — Geração de Cenas

Esta é a ordem em que as 33 obras de Aristóteles serão processadas pelo `05_daily_cenas_runner.py`. A ordem segue a tradição da **leitura formativa da filosofia clássica**: começa pelas obras práticas (mais acessíveis e imediatamente úteis para a vida), passa pelas centrais teóricas, e termina pelas técnicas/atribuídas.

Para editar a ordem, modifique a lista no script `04_define_cenas_master.py` ou diretamente em `_raw/cenas_master.json` (campo `priority_rank`).

## Tier 1 — Obras práticas e centrais (vida + sabedoria)

| Pos | Obra | Justificativa |
|----|------|---------------|
| 1 | Ética a Nicômaco | Filosofia prática central. Ponto de entrada clássico para Aristóteles. |
| 2 | Política | Sequência natural da Ética ("o homem é animal político"). NB: truncado no MIT. |
| 3 | Poética | Curto, denso, fundacional para teoria da arte e narrativa. |
| 4 | Retórica | Arte do discurso público; complementa Poética. |

## Tier 2 — Filosofia primeira

| Pos | Obra | Justificativa |
|----|------|---------------|
| 5 | Metafísica | Magnum opus. 14 livros. Núcleo da ontologia ocidental. |
| 6 | Sobre a Alma (De Anima) | Psicologia filosófica; ponte entre física e metafísica. |

## Tier 3 — Lógica fundamental (Organon)

| Pos | Obra | Justificativa |
|----|------|---------------|
| 7 | Categorias | Fundamento da lógica e ontologia formal. |
| 8 | Da Interpretação | Proposição e juízo. |
| 9 | Analíticos Posteriores | Epistemologia: ciência demonstrativa. |
| 10 | Analíticos Anteriores | Silogismo formal. |

## Tier 4 — Filosofia natural

| Pos | Obra | Justificativa |
|----|------|---------------|
| 11 | Física | Filosofia natural — movimento, tempo, espaço. |
| 12 | Sobre o Céu | Cosmologia. |
| 13 | Sobre a Geração e a Corrupção | Mudança substancial. |
| 14 | Meteorologia | Fenômenos sublunares. |

## Tier 5 — Dialética e refutação

| Pos | Obra | Justificativa |
|----|------|---------------|
| 15 | Tópicos | Método dialético. |
| 16 | Refutações Sofísticas | Falácias. |

## Tier 6 — Biologia

| Pos | Obra | Justificativa |
|----|------|---------------|
| 17 | Sobre as Partes dos Animais | Biologia teleológica. |
| 18 | História dos Animais | Observação empírica. Mais longo do corpus (~230 caps). |
| 19 | Sobre o Movimento dos Animais | |
| 20 | Sobre a Marcha dos Animais | |
| 21 | Sobre a Geração dos Animais | OCR variável (Loeb Peck). |

## Tier 7 — Parva Naturalia (mente e corpo)

| Pos | Obra | Justificativa |
|----|------|---------------|
| 22 | Sobre o Sentido e o Sensível | |
| 23 | Sobre a Memória e a Reminiscência | |
| 24 | Sobre o Sono e a Vigília | |
| 25 | Sobre os Sonhos | |
| 26 | Sobre a Adivinhação pelos Sonhos | |
| 27 | Sobre a Longevidade e a Brevidade da Vida | |
| 28 | Juventude/Velhice, Vida/Morte, Respiração | |

## Tier 8 — Atribuídas e históricas (deixar por último)

| Pos | Obra | Justificativa |
|----|------|---------------|
| 29 | Constituição dos Atenienses | Documento histórico (não filosófico puro). |
| 30 | Ética a Eudemo | OCR ruim, autoria disputada. |
| 31 | Magna Moralia | Autoria atribuída. OCR ruim. |
| 32 | Sobre as Virtudes e os Vícios | Atribuída. |
| 33 | Econômicos | Atribuída. |

## Estimativa de cronograma

- **Total de capítulos:** 1364
- **Capítulos longos (>8000 chars) viram 2-3 cenas:** estimativa ~1500-1700 cenas totais
- **Ritmo:** 100 cenas/dia
- **Conclusão estimada:** ~15-17 dias
