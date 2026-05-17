# Plano de Execução — Leitura Formativa de Aristóteles

> Adaptação do modelo `victor_hugo/notre-dame_de_paris/plano_execucao_notre-dame.md` para o corpus aristotelicum.

## Fase 1 — Aquisição do corpus ✅

**Concluída em 2026-05-16.**

- 33 obras baixadas via `scripts/01_download_corpus.py`
- Manifesto em `_raw/download_manifest.json`
- Índice canônico em `docs/corpus_index.md`

## Fase 2 — Limpeza dos textos brutos ✅

**Concluída em 2026-05-16** via `scripts/02_clean_raw.py`. Output em `obras/{cat}/{obra}/clean/*.txt`. Manifesto em `_raw/clean_manifest.json`.

**Pipelines implementados:**
- **MIT (28 obras)**: detecta início do corpo (primeira ocorrência de `BOOK N` / `SECTION N` / `Part 1`), trunca em `THE END`, normaliza marcadores `Part N \"` (artefato de aspas escapadas).
- **Archive.org book_start (3 obras)**: descarta tudo antes da primeira ocorrência de `BOOK I`, remove page headers repetitivos (`GENERATION OF ANIMALS`, `OECONOMICA`, etc.).
- **Archive.org extract_range (2 obras)**: para Eudemian e Virtues e Vícios — extraem trecho específico do volume Loeb 285 (que contém 3 obras coladas), usando `min_line` para pular a capa e índices.

**Qualidade observada:**
- MIT: 95-100% retido após limpeza (apenas header/footer removidos). Excelente.
- Generation of Animals (Peck Loeb): OCR Loeb com artefatos `_` decorativos e palavras quebradas como `[produc-` `tion]`. Aceitável.
- Magna Moralia (Stock Oxford): começa com TOC analítico antes do corpo. OK.
- **Eudemian Ethics (Solomon Loeb 285): OCR muito ruidoso** (ex: `co^^iposed`, `temj,{j`). Pode demandar fonte alternativa (ver issue notebooklm_edson-... a criar).
- Politics: 1 letra perdida ("Every tate" em vez de "state") — único artefato do Google cache, irreversível, ignorável (108 outras ocorrências íntegras).

**Comando para regenerar:**
```bash
python3 scripts/02_clean_raw.py            # tudo
python3 scripts/02_clean_raw.py --only etica  # filtra
python3 scripts/02_clean_raw.py --dry-run
```

## Fase 3 — Segmentação por livros/capítulos ✅

**Concluída em 2026-05-16** via `scripts/03_segment_capitulos.py`. Output: **1364 arquivos markdown** em `obras/{cat}/{obra}/capitulos/L{NN}-C{MM}.md`. Manifesto em `_raw/segment_manifest.json`.

**Markers reconhecidos:**
- `BOOK I`/`BOOK II`/...`BOOK ONE`/`BOOK TWO` (Politics MIT usa palavras), `SECTION 1`/`SECTION 2` — livro.
- `Part 1`/`Part I`, `CHAPTER 1`/`CHAPTER I` — capítulo.
- Capítulo numérico isolado (Nicomachean Ethics: `1`, `2`, `3` sozinho com brancos antes/depois) — capítulo, com heurística de sequenciamento.

**Sanity check:** rejeita números de livro fora de 1-20 (protege contra OCR ruim como `BOOK Ill` virando 99 via conversão romana).

**Distribuição final** (por categoria):
- 01_organon: 270 capítulos
- 02_fisica: 173
- 03_psicologia_biologia: 394 (inclui Parva Naturalia com 7 sub-obras prefixadas)
- 04_metafisica: 142 (14 livros, ~10 cap cada)
- 05_etica: 180 (Nicômaco 99 + Eudemo 4 + Magna 76 + Virtues 1)
- 06_politica: 126 (Política 22 + Const. Atenienses 69 + Econômicos 35)
- 07_retorica_poetica: 86

**Limitações conhecidas** (issues criadas):
- **Politics truncado**: o Google cache do MIT só preservou Books I-II (de 8 totais). Issue para baixar de fonte alternativa.
- **Eudemian Ethics OCR ruim**: Loeb 285 perdeu BOOK IV, V, VI. Segmentado em 4 livros em vez de 8.
- **Magna Moralia**: arquivo Stock tem múltiplas seções (texto inglês, grego, comentários) que confundem segmentador. 76 capítulos em livros L01/02/07/08 — revisão manual recomendada.
- **Generation of Animals**: sem CHAPTER markers claros, cada livro virou 1 capítulo único.
- **Parva Naturalia**: 7 sub-obras compartilham diretório; arquivos prefixados com slug (ex: `on_dreams-L01-C01.md`).

**Comando para regenerar:**
```bash
python3 scripts/03_segment_capitulos.py            # tudo
python3 scripts/03_segment_capitulos.py --only metafisica
python3 scripts/03_segment_capitulos.py --dry-run
```

**Exemplo de frontmatter gerado:**
```yaml
---
obra_pt: "Metafísica"
obra_en: "Metaphysics"
categoria: 04_metafisica
obra_slug: 01_metafisica
fonte: MIT/Oxford-Ross
livro_num: 1
livro_marker: "BOOK I"
total_livros: 14
capitulo_num: 1
capitulo_marker: "Part 1"
total_capitulos_no_livro: 10
bytes: 5555
---
```

## Fase 4-5 — Seleção de cenas e geração de prompts (rotina diária) ✅

**Concluída em 2026-05-16** via 2 scripts:

### `scripts/04_define_cenas_master.py` (executar 1x ou ao alterar capítulos)

Percorre os 1364 `obras/*/capitulos/L*-C*.md`, divide capítulos longos (>12k chars)
em sub-cenas de até ~8k chars (limite prático NotebookLM), ordena por prioridade
canônica (ver `docs/priority_order.md`) e grava em `_raw/cenas_master.json`.

**Resultado:** 1695 cenas planejadas (1364 capítulos + 331 sub-cenas extras).

**Flag `--force`:** regenera o master preservando o status (`done`/`failed`/`pending`)
das cenas que já existiam — útil ao re-segmentar uma obra.

### `scripts/05_daily_cenas_runner.py` (chamado pelo cron)

Pega próximas N cenas `pending` em ordem de priority_rank e gera:
- `obras/{cat}/{obra}/cenas/{slug}_cena01.md` — texto recortado da cena
- `obras/{cat}/{obra}/prompts/{slug}_cena01.md` — prompt para o NotebookLM
- Atualiza `status='done'` + `done_at` no master, append em `_raw/cenas_log.jsonl`

**Flags úteis:**
```bash
python3 scripts/05_daily_cenas_runner.py             # 100 cenas (default)
python3 scripts/05_daily_cenas_runner.py --limit 5   # lote menor (teste)
python3 scripts/05_daily_cenas_runner.py --status    # apenas relatório
python3 scripts/05_daily_cenas_runner.py --dry-run   # mostra sem gravar
```

### Cron — automação diária

```cron
# Aristóteles: gera 100 cenas+prompts/dia em ordem canônica de prioridade
0 7 * * * /Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/aristoteles/scripts/cron_daily.sh
```

Wrapper `scripts/cron_daily.sh` chama o runner com limit 100, loga em
`logs/aristoteles_cron_YYYYMMDD_HHMMSS.log`, notifica via afplay/terminal-notifier
em caso de falha (e ao concluir tudo).

**Cronograma:** 1695 cenas / 100 por dia = ~17 dias até cobrir todas as obras.
Ordem segue `docs/priority_order.md` (Ética → Política → Poética → Retórica → …).

### Template do prompt

O prompt está em `scripts/05_daily_cenas_runner.py:PROMPT_TEMPLATE`. Pontos
principais:
- **Idioma do áudio**: inglês (todas as 33 obras estão em traduções inglesas).
- **Pedagogia**: formativa, não acadêmica. Estrutura em 5 blocos:
  1. Anchor the question.
  2. Walk the argument.
  3. Name the method (4 causas, divisão por gênero, dialética, etc.).
  4. From concept to life (1 exemplo moderno concreto).
  5. Tie back.
- **Anti-invenção**: "Do not invent doctrine. If Aristotle is silent on a modern
  application, say so." — coerente com a regra global.
- **Recap**: o tutor faz "Previously On" para áudios além do 1º da obra.

## Fase 5 — Geração de áudios via NotebookLM

Seguir o padrão de `quo_vadis_runner.py` / `ben_hur_runner.py`:
- Notebook ID: `de324f7f-25ca-438c-96d5-16ff36a2bddc` (Aristóteles, conta pessoal)
- Profile: `default`
- Limite: **20 áudios/dia** (silencioso na CLI nlm — planejar lotes de 18-19)
- "Completed" é prematuro: janela de 10-40min entre status e download viável
- Filenames: usar `.m4a` (não `.mp3`)

**Estimativa de volume:**
Se cada obra gerar ~10 cenas em média (variável: Política tem 8 livros, podem ser 40+ cenas), o total fica em ~330-500 cenas → ~17-25 dias para gerar tudo via NotebookLM.

## Fase 6 — Distribuição

Encadear com o **podcast ecosystem** (`reference_podcast_ecosystem` em MEMORY.md):
- Mac (criação) → dell-server (publicação Caddy + feed RSS) → DROBO (arquivo cold)
- Slug provável: `aristoteles` ou `corpus-aristotelicum`
- Feed: `https://edson:SENHA@dell-server.tail3f4f14.ts.net/aristoteles/feed.xml`

## Riscos / TODOs

- [ ] Validar que Notebook ID `de324f7f-25ca-438c-96d5-16ff36a2bddc` ainda existe e pertence à conta correta
- [ ] Decidir EN vs PT para o áudio
- [ ] Definir critério de seleção de cenas (1-5 por capítulo? por densidade conceitual?)
- [ ] Estabelecer ordem de execução por categoria (sugerido: Poética/Retórica primeiro como aquecimento, depois Ética → Política → Metafísica → Organon → Física/Biologia)
- [ ] Limpar OCR dos 5 textos Archive.org antes de segmentar
