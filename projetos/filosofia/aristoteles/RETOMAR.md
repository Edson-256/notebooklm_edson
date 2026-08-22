# Aristóteles — RETOMAR

> **Quando voltar:** leia este arquivo primeiro. Depois `CLAUDE.md`, `docs/plano_execucao.md` e `docs/workflow_audio.md`.
>
> **Última atualização:** 2026-08-22 — recuperação das 4 fontes defeituosas e integração ao pipeline.

## Estado atual ✅

**Em produção, rodando sozinho.** O cron dispara a cada 2h, com quota guard de 24h rolantes
(a cota do NotebookLM é rolante, não por dia de calendário — nunca usar horário fixo).

| Item | Estado (medido em 2026-08-22) |
|---|---|
| Cenas planejadas | **1.629** em `_raw/cenas_master.json` — todas com cena + prompt gerados |
| Áudios já produzidos | **1.096** (`_raw/audio_metadata.json`) |
| Fila pendente | **530 áudios**, ~27 dias a 20/dia |
| Obra em produção agora | **História dos Animais** (obra 19) — faltam 72 |
| Sources no notebook | 33, todas conferidas |

### Ordem de produção da fila (blocos contíguos, uma obra por vez)

História dos Animais (72) → **Política III–VIII (82)** → Movimento dos Animais (11) →
Marcha dos Animais (19) → **Geração dos Animais (78)** → Parva Naturalia (54) →
Constituição dos Atenienses (69) → **Ética a Eudemo (44)** → **Magna Moralia (59)** →
Virtudes e Vícios (8) → Econômicos (37).

Em negrito, as obras cuja fonte foi recuperada em 2026-08-21/22.

## O que mudou em 2026-08-22 (ler antes de mexer em cena ou prompt)

Quatro obras tinham fonte truncada ou com OCR ruim e foram substituídas
(diagnóstico completo em `docs/FONTES_INCOMPLETAS_recuperar.md`):

| Obra | Fonte nova | Livros |
|---|---|---|
| Política (29) | Wayback 1997 do MIT — Jowett íntegro | 8 (era 2) |
| Ética a Eudemo (26) | Wikisource — Oxford vol. IX, tr. Solomon | 4 (I, II, III, VII) |
| Magna Moralia (27) | Wikisource — Oxford vol. IX, tr. Stock | 2 |
| Geração dos Animais (23) | Wikisource — Oxford vol. V, tr. Platt | 5 |
| Virtudes e Vícios (28) | Wikisource — Oxford vol. IX, tr. Solomon | 1 (SECTION 1, 8 caps) |

**A Ética a Eudemo tem 4 livros e isso está certo** — os Livros IV, V e VI são o mesmo texto
dos Livros V, VI e VII da Ética a Nicômaco e não foram traduzidos por Solomon; o VIII foi
anexado ao VII. Não tratar como fonte incompleta.

**A Magna Moralia termina abruptamente** — o tratado chegou assim até nós. Não é truncamento.

Scripts novos:
- `scripts/00_normalize_recovered_sources.py` — converte os textos recuperados para o formato
  canônico MIT (`BOOK ONE` / `Part I`), que é o que 02 e 03 já sabem ler.
- `scripts/08_replace_recovered_sources.py` — troca uma source no notebook sem deixar buraco
  (sobe a nova → confere → só então apaga a velha → renomeia).

Mudanças de comportamento no pipeline:
- **`04:sort_cenas` agora ordena por `obra_idx`** dentro do rank. Sem isso, obras que dividem
  o mesmo rank saíam intercaladas capítulo a capítulo na fila (os 7 Parva Naturalia entre si;
  a Magna Moralia partida ao meio por Virtudes e Vícios).
- **`04:annotate_audio_position` agora agrupa por `obra_idx`**, não por `obra_slug`. O prompt
  dizia "áudio 3 de 64" somando obras diferentes que dividem diretório.
- **`04:NOTAS_SERIE` + `05:{nota_serie_block}`** — texto extra injetado no prompt de cenas de
  transição, para o ouvinte entender a sequência. Hoje são 4: retomada da Política, abertura da
  Ética a Eudemo, salto do Livro III para o VII no Eudemo, fim abrupto da Magna Moralia.
- **`04:apply_segunda_leva_rank`** — as 82 cenas novas da Política receberam rank 18.5 para
  entrar depois da História dos Animais, e não furar a fila da obra em produção.

O áudio 22 da Política (`aristoteles_29_l02_c09_cena01_politica`) foi **removido do
`audio_metadata.json` para ser refeito** — ele tinha ido ao ar com 5.775 dos 12.683 bytes do
capítulo, cortado no meio da palavra "givin". O registro antigo ficou em
`audio_metadata.json > substituidos`. O arquivo velho segue no dell até ser sobrescrito pelo
novo, de propósito: assim o feed não fica com buraco.

## Notebook NLM ativo

- **Título:** `Aristóteles (completo)`
- **ID:** `48eb1ca3-5f9b-484a-be94-fe959c3e40dc`
- **URL:** https://notebooklm.google.com/notebook/48eb1ca3-5f9b-484a-be94-fe959c3e40dc
- **Conta:** default (pessoal — `edson.michalkiewicz@gmail.com`)
- **Sources:** 33 obras em ordem canônica Bekker
- **Nomenclatura:** `{NN}. {Título inglês} (Aristotle, tr. {Tradutor})`
- Manifest local: `_raw/notebook_aristoteles.json` (mapping `obra_idx` → `source_id`)

> Notebook antigo (`de324f7f-...`) está **descontinuado**: tinha uploads incompletos de 5KB do MIT misturados com 50+ papers. Não usar.

## Convenção de nome de áudio (canônica)

```
aristoteles_{NN_obra}_{lXX}_{cYY}_cenaSS_{slug_obra}.m4a
```

Exemplo: `aristoteles_25_l01_c01_cena01_etica_nicomaco.m4a`
- 25 = Nicomachean Ethics (ordem Bekker)
- l01-c01 = Book I, Chapter 1
- cena01 = primeira sub-cena
- etica_nicomaco = slug humano-legível

O nome **completo** aparece no cabeçalho de cada prompt em `obras/*/prompts/*.md`.

## Como retomar a geração de áudios

### Opção A — Fluxo manual via UI (até ~50 áudios/dia, sem entrar no limite CLI)

```bash
cd /Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/filosofia/aristoteles

# 1. Ver próximas em ordem de prioridade
python3 scripts/07_audio_runner.py --list-pending 5

# 2. Copiar prompt para clipboard
cat obras/05_etica/01_etica_nicomaco/prompts/L01-C01_cena01.md | pbcopy

# 3. NLM Web: Audio Overview > Customize > colar > gerar
#    No Studio: renomear o áudio para o "audio_title" do cabeçalho do prompt

# 4. Baixar em lote (operação leve, sem custo de quota):
python3 scripts/07_audio_runner.py --harvest

# 5. Se esqueceu de renomear:
python3 scripts/07_audio_runner.py --claim <artifact_id> <cena_id>
```

### Opção B — Ativar cron (20 áudios/dia via CLI)

⚠ **Pré-requisitos:**
1. Cron do COF v2 (21:00, 20/dia) terminar — restam ~2 semanas a partir de 2026-05-17
2. Implementar a parte `--create` em `07_audio_runner.py:cmd_create` (hoje é stub — só registra, não chama `nlm studio create`)

```bash
# Quando estiver pronto:
cp scripts/cron_audio.sh.template scripts/cron_audio.sh
chmod +x scripts/cron_audio.sh
crontab -e
# Adicionar: 0 7 * * * /Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/filosofia/aristoteles/scripts/cron_audio.sh
```

## Arquivos-chave

| Caminho | O que tem |
|---|---|
| `CLAUDE.md` | Instruções e quirks do projeto. |
| `docs/plano_execucao.md` | Roteiro completo das fases 1-6. |
| `docs/workflow_audio.md` | Workflow detalhado de geração de áudio. |
| `docs/corpus_index.md` | Catálogo das 33 obras com tradutor e fonte. |
| `docs/priority_order.md` | Ordem canônica de prioridade (Tier 1-8). |
| `_raw/cenas_master.json` | 1695 cenas planejadas, status por cena. |
| `_raw/notebook_aristoteles.json` | IDs do notebook NLM + sources. |
| `_raw/audio_metadata.json` | Tracking de áudios gerados/baixados (vazio hoje). |
| `obras/{cat}/{obra}/clean/*.txt` | Texto limpo (gitignored). |
| `obras/{cat}/{obra}/capitulos/L*-C*.md` | 1364 capítulos com frontmatter (gitignored). |
| `obras/{cat}/{obra}/cenas/*_cenaXX.md` | 1695 cenas recortadas (gitignored). |
| `obras/{cat}/{obra}/prompts/*_cenaXX.md` | 1695 prompts NLM, cabeçalho com `audio_title` (gitignored). |
| `audios/` | .m4a baixados (criados conforme `--harvest`). |
| `scripts/01_download_corpus.py` | Download MIT + Archive.org. |
| `scripts/02_clean_raw.py` | Limpeza de header/footer e OCR. |
| `scripts/03_segment_capitulos.py` | Segmentação em livros/capítulos. |
| `scripts/04_define_cenas_master.py` | Monta master ordenado. Flag `--force` preserva status. |
| `scripts/05_daily_cenas_runner.py` | Gera arquivos cenas/prompts (todos 1695 já feitos). |
| `scripts/06_create_notebook_and_upload.py` | Cria notebook NLM + upload 33 sources. |
| `scripts/07_audio_runner.py` | Híbrido. `--harvest` operacional, `--create` stub. |
| `scripts/cron_audio.sh.template` | Wrapper cron em standby. |

## Limitações conhecidas (issues abertos)

1. ~~`aristoteles/28_virtudes_e_vicios`~~ — **resolvido em 2026-08-22**, junto com as outras
   quatro: a fonte agora é o tratado de verdade (Wikisource, Oxford vol. IX, tr. Solomon,
   pp. 527-532), 8 capítulos, 1.813 palavras. Eram 5 cenas do prefácio do tradutor; agora são 8
   cenas do texto. Issue `notebooklm_edson-x5lr` fechada.
2. **Política "Every tate"** — resolvido junto com a troca de fonte: o texto de 1997 traz
   "EVERY STATE" correto. Só os áudios 1 a 21, já publicados, carregam o defeito.

## Sessões anteriores (Obsidian Vault)

- `Projects/04-Education-Content/notebooklm_edson/Log-2026-05-20-aristoteles-projeto-completo-fases-1-a-6.md`

## Para retomar com Claude

```
claude --resume a7cab8df-a6c1-44b2-9abb-8e6b03de1b42
```

Sessão: `aristoteles-projeto-completo-fases-1-a-6`
