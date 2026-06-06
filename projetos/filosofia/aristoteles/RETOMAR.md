# Aristóteles — RETOMAR

> **Quando voltar:** leia este arquivo primeiro. Depois `CLAUDE.md`, `docs/plano_execucao.md` e `docs/workflow_audio.md`.
>
> **Última atualização:** 2026-05-20 — fim das fases 1-6.

## Estado atual ✅

| Fase | Status |
|---|---|
| 1. Download corpus (33 obras, MIT + Archive.org) | ✅ |
| 2. Limpeza dos textos (`obras/*/clean/`) | ✅ |
| 3. Segmentação em capítulos (1364 .md em `obras/*/capitulos/`) | ✅ |
| 4. Definição da fila de cenas (1695 em `_raw/cenas_master.json`) | ✅ |
| 5. Geração de cenas + prompts (1695 cada em `obras/*/cenas/` e `obras/*/prompts/`) | ✅ |
| 6. Notebook NLM criado + audio runner híbrido | ✅ (em standby) |

**Nenhuma cena de áudio gerada ainda.** Aguardando ativação do cron OU operação manual.

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

1. **Politics truncado** no Google cache MIT — só Books I-II (de 8). Issue Beads: `notebooklm_edson-... (Politics)`.
2. **Eudemo OCR ruim** — Loeb 285 perdeu BOOK IV, V, VI. Issue Beads `notebooklm_edson-... (Eudemo)`.
3. **Magna Moralia / Generation of Animals / Virtues OCR variável** — segmentação imperfeita. Issue Beads `notebooklm_edson-... (4 obras OCR)`.
4. **Politics "Every tate"** (1 letra perdida do "state" no Google cache) — irreversível, ignorável.
5. **`--create` é stub** — falta implementar invocação real de `nlm studio create` antes de ativar cron.

## Sessões anteriores (Obsidian Vault)

- `Projects/04-Education-Content/notebooklm_edson/Log-2026-05-20-aristoteles-projeto-completo-fases-1-a-6.md`

## Para retomar com Claude

```
claude --resume a7cab8df-a6c1-44b2-9abb-8e6b03de1b42
```

Sessão: `aristoteles-projeto-completo-fases-1-a-6`
