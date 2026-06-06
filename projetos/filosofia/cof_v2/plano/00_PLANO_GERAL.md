# Plano de geração de prompts + guias de áudio para o notebook COF v2

**Notebook NLM:** `5508086a-da53-4947-bce4-a1d7d83cf0e2`
**Conta:** `default` (edson.michalkiewicz@gmail.com)
**Status:** plano (não executar ainda)

## Objetivo do projeto

Transformar o conteúdo filosófico denso do Curso Online de Filosofia (COF) de
Olavo de Carvalho em **aprendizado acessível** por meio de áudios sequenciais
gerados pelo NotebookLM, **um áudio por aula/curso/livro/apostila**, cada um
acompanhado por um **guia de aula** que oriente expansão e aprofundamento
remetendo às fontes citadas.

## Escopo

**Itens cobertos (678 totais):**

| Categoria | Quantidade | Detalhes |
|---|---:|---|
| Aulas individuais | 582 | Numeração 0–585, datas conhecidas, conteúdo COF original |
| Cursos extracurriculares | 23 | Cada curso = 1 item (usando `Unif_*` unificado) |
| Livros / textos | 70 | 63 do disco + 7 do notebook antigo (Olavo) |
| Compilações temáticas | 4 | Apostilas, Artigos, Teoria do estado, 2016 |

**O que está fora deste plano:**
- Áudios e vídeos das aulas (conteúdo equivalente já está nas transcrições).
- Pasta `transcricoes/` dos extracurriculares (não curada por humano).
- Citações e referências contidas nas aulas (apenas o conteúdo COF original
  é processado; referências viram parte do **guia de aula**, não fonte própria).

## Formatos do NotebookLM disponíveis

| Formato | Quando usar |
|---|---|
| **Deep Dive** | Análise detalhada. Aulas densas, livros longos, cursos completos. **Default da maioria das aulas.** |
| **The Brief** | Resumo executivo. Textos curtos (<4.000 palavras), aulas de apresentação/preliminar, artigos curtos. |
| **The Critique** | Visão crítica. Aulas/textos polêmicos onde Olavo confronta autores ou ideologias (palavras-chave: crítica, contra, imbecilização, refutação). |
| **The Debate** | Múltiplas perspectivas. Temas amplos políticos/sociais/morais que admitem posições legítimas distintas (guerra cultural, política, estado, Brasil). |

## Critério de seleção de formato (heurística automatizada)

Aplicada em `01_inventario_completo.json` e revisável manualmente:

```
1. words < 4000                              → The Brief
2. título/conteúdo casa /crítica|contra|...   → The Critique
3. título/conteúdo casa /debate|política|...  → The Debate
4. título/conteúdo casa /introdução|...       → The Brief
5. (default)                                 → Deep Dive
```

Distribuição resultante (total 678):
- **Deep Dive: 596** (88%)
- **The Brief: 63** (9%)
- **The Critique: 5** (1%)
- **The Debate: 14** (2%)

## Sequência didática

**Cada áudio é parte de uma série**. Por isso o prompt obriga:

1. **Identificação no início**: "Esta é a Aula NNN do COF, apresentada em <data>".
2. **Intro sequencial (~1–2 min)**: lembrar brevemente o que foi visto na aula
   anterior (`anterior` no inventário), reativando o fio condutor.
3. **Desenvolvimento**: aplica o formato escolhido, restrito ao conteúdo da aula.
4. **Outro sequencial (~30 seg)**: adiantar o que vem na próxima aula
   (`proxima` no inventário), instigando curiosidade.

Sequências internas:
- **Aulas COF**: ordenadas por (data, número). Cada uma referencia anterior/próxima.
- **Cursos extracurriculares**: ordem alfabética (independentes; cada Unif_ é
  autocontido, mas o áudio ainda referencia o anterior na fila).
- **Livros**: ordem alfabética; opcional citar livros relacionados.
- **Temáticas**: 1→2→3→4 (4 itens, sequência arbitrária).

## Estrutura do prompt por item

Ver `02_template_prompt.md` para o template completo.

Cada prompt instanciado conterá:
- ID canônico (ex: `aula-144`, `livro-arte-sacra`, `extra-sociologia-da-filosofia`)
- Formato escolhido
- Source IDs do NLM (a serem capturados após upload das fontes)
- Campos `anterior`/`proxima` para o trecho sequencial
- Diretiva de escopo (não vazar para outras aulas)
- Diretiva de linguagem (PT-BR didático)

## Estrutura do guia de aula por item

Ver `03_template_guia_aula.md`. Cada guia (.md gerado em
`guias/<id>.md`) contém:
- Síntese (máx. 300 palavras)
- 5–8 conceitos-chave
- Autores/obras citadas no curso (extraídos da transcrição da aula, **só fontes
  reais**, sem inventar)
- Sugestões de leitura para aprofundar (a partir das fontes citadas)
- 3–5 exercícios de fixação
- Posição na trajetória (continuidade explícita com anterior/próxima)

## Plano de execução em lotes

**Restrição operacional:** executar **20 itens por vez**, para que o usuário
controle consumo de tokens e evite estourar cota.

- **Total: 678 itens → 34 lotes de 20** (último lote: 18 itens).
- Cada execução de lote envolve, por item:
  1. Ler conteúdo da aula no markdown
  2. Identificar autores/obras citadas (regex + filtragem)
  3. Gerar prompt completo (template instanciado)
  4. Gerar guia de aula (template instanciado)
  5. Salvar em `prompts/<id>.md` e `guias/<id>.md`
  6. Atualizar `_progresso.json` com status `prepared`
- **Não dispara áudio** automaticamente — só prepara prompt+guia.
  O disparo no NLM é etapa posterior (script `cof_v2_audio_runner.py` análogo
  ao `quo_vadis_runner.py`, respeitando `regras_pipeline_audio_por_cena.md`).

Ver `04_lotes_execucao.md` para o detalhamento dos 34 lotes (lista exata de
IDs por lote) e o comando para disparar cada lote.

## Inventários de itens

- `01_inventario_completo.json` — fonte canônica machine-readable (todos os 678
  itens com formato, sequência, paths).
- `05_aulas_por_ano.md` — visão humana das 582 aulas agrupadas por ano.
- `06_extracurriculares.md` — 23 cursos extracurriculares.
- `07_livros.md` — 70 livros.
- `08_tematicas.md` — 4 compilações temáticas.

## Próximas etapas (ordem)

1. **Revisar este plano** (você). Especialmente: heurística de formato,
   templates, agrupamento por lote.
2. **Upload das 121 fontes** no notebook `5508086a-…` (não coberto neste plano).
3. **Capturar source_ids** de cada fonte após upload em
   `_sources_map.json` (mapeamento `cof-aulas-2009-a.md` → `<source_id>`).
4. **Gerar lotes** com `scripts/04_generate_prompt_batch.py --batch N` (20
   itens/lote). Implementação a fazer.
5. **Disparar áudios** com runner próprio (futuro), aplicando as regras
   anti-bug do `regras_pipeline_audio_por_cena.md` (ID canônico global, manifest
   JSON, dry-run, etc).
6. **Curadoria**: revisar guias gerados, complementar referências bibliográficas
   conforme necessário.

## Decisões pendentes (esperam sua confirmação)

1. **Heurística de formato** está OK? Quer ajustar limiares (ex: usar `<5000`
   em vez de `<4000` para Brief)?
2. **Cursos extracurriculares**: tratar cada Unif_ como **um único** item de
   áudio, ou subdividir em "aulas internas" (Unif_ contém aulas 01, 02, …)?
   Padrão atual = 1 item por curso.
3. **Apostilas/Artigos/Teoria do estado**: tratar como **1 item cada** (default
   atual) ou subdividir em palestras individuais? Cada compilação temática é
   um arquivo grande sem cabeçalhos claros para cortar.
4. **Sequência entre categorias**: hoje cada categoria tem sequência interna
   independente. Quer uma "fila mestra" cronológica? (mais complexo, e a
   maioria das aulas COF são contínuas — categorias mistas confundem).
