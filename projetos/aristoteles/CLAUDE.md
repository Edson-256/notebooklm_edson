# Projeto Aristóteles — Leitura Formativa via NotebookLM

## Objetivo

Aplicar a metodologia de Leitura Formativa (mesmo padrão de `quo_vadis`, `victor_hugo/notre-dame_de_paris`, `cof_v2`) ao corpus completo de Aristóteles. Cada obra é segmentada em capítulos/livros e cenas, e cada cena gera um áudio Deep Dive no NotebookLM.

## Conta NotebookLM

Usar `--profile default` (conta pessoal `edson.michalkiewicz@gmail.com`). Notebook canônico do autor:

- **Aristóteles**: `de324f7f-25ca-438c-96d5-16ff36a2bddc` (cadastrado em `docs/notebooklm/notebooks_conta_pessoal.md` do projeto pai)

Verificar se o ID atual ainda é o canônico antes de uso intensivo (notebooks podem ser recriados).

## Estrutura

```
aristoteles/
├── CLAUDE.md                       # este arquivo
├── _raw/
│   └── download_manifest.json      # manifesto consolidado dos downloads
├── docs/
│   ├── corpus_index.md             # índice canônico das 33 obras + fontes
│   └── plano_execucao.md           # roteiro do projeto
├── scripts/
│   └── 01_download_corpus.py       # baixa o corpus aristotelicum (MIT + Archive.org)
├── obras/
│   ├── 01_organon/                 # 6 obras lógicas
│   ├── 02_fisica/                  # 4 obras de filosofia natural
│   ├── 03_psicologia_biologia/     # De Anima + Parva Naturalia + 5 biológicos
│   ├── 04_metafisica/              # Metafísica (14 livros)
│   ├── 05_etica/                   # Nicômaco + Eudemo + Magna Moralia + Virtudes
│   ├── 06_politica/                # Política + Const. dos Atenienses + Econômicos
│   └── 07_retorica_poetica/        # Retórica + Poética
└── audios/                         # áudios consolidados (Mac → dell → DROBO)
```

Cada `obras/{categoria}/{obra}/` contém:
- `_raw/` — texto bruto consolidado (`*.txt`) + metadados (`*.source.json`)
- (a criar) `capitulos/` — segmentação por livro
- (a criar) `cenas/` — trechos selecionados para Deep Dive
- (a criar) `prompts/` — prompts para o NotebookLM
- (a criar) `audios/` — áudios gerados desta obra

## Padrão de nomenclatura (a aplicar quando segmentar)

Seguindo o padrão de `notre-dame_de_paris`:
- Capítulos: `L01-C01-<titulo_kebab>.md` (Livro 01, Capítulo 01)
- Cenas: `L01-C01-<titulo>_cena001.md`
- Prompts: `L01-C01-<titulo>_prompt001.md`

## Fontes do corpus baixado

- **Internet Classics Archive (MIT)** — 28 obras. Tradução Oxford (Ross, Smith, Edghill, Jowett, etc.). Versão text-only consolidada (`.mb.txt` para multi-book, `.1b.txt` para single-book).
- **Archive.org** — 5 obras complementares (Geração dos Animais, Eudemo, Magna Moralia, Virtudes e Vícios, Econômicos), via DJVU OCR de volumes Oxford/Loeb dos anos 1910-1930.

### Quirks da fonte (registrar)

- O servidor `classics.mit.edu` ocasionalmente serve a versão **Google cache** de alguns arquivos em vez do original. O script `01_download_corpus.py` detecta isso (presença do wrapper Google) e extrai apenas o `<pre>...</pre>` real.
- Em `obras/06_politica/01_politica/_raw/politics.txt`, a primeira ocorrência da palavra "state" virou "tate" (Google cache removeu a letra destacada). É 1 ocorrência em 108 — segue íntegro para propósitos práticos. Outras 9 obras vieram pelo mesmo caminho cache→pre e estão limpas.
- Os arquivos baixados de Archive.org são **OCR de DJVU** com ruído OCR (acentos errados, página de rosto da biblioteca no topo, números de página intercalados). Necessitam limpeza antes de segmentação.

## Workflow Beads

Toda tarefa significativa neste projeto deve ser criada em Beads ANTES de iniciar.
- `bd ready --json` — ver tarefas prontas
- `bd create --title="..." --description="..." --type=task|feature|bug --priority=2 --json`
- `bd close <id> --reason "..."` — ao concluir
- `bd sync` — antes de encerrar sessão

## Re-rodar o download

```bash
cd /Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/aristoteles
python3 scripts/01_download_corpus.py            # baixa apenas o que falta
python3 scripts/01_download_corpus.py --force    # re-baixa tudo
python3 scripts/01_download_corpus.py --only etica  # filtra categoria
python3 scripts/01_download_corpus.py --dry-run  # apenas lista
```

Manifesto gerado em `_raw/download_manifest.json` (resumo por obra: status, bytes, URL efetiva, timestamp).
