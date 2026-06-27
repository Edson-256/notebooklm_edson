# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Objetivo

Catalogar os vídeos públicos do canal **Bishop Robert Barron** no YouTube
(`https://www.youtube.com/@BishopBarron/videos`) — apenas **títulos + links**,
sem baixar vídeo — e classificá-los por assunto, para que o usuário selecione os
relevantes e cole os links no **NotebookLM** (Adicionar fonte → Link do YouTube),
criando um notebook de estudo formativo (teologia).

Subprojeto de `notebooklm_edson` (ver CLAUDE.md raiz do repo: conta NLM
`--profile default`, regras Beads, idioma de output pt-BR). Categoria temática:
`projetos/teologia/`.

## Conformidade (YouTube ToS)

- Extraímos **somente metadados públicos** (títulos + IDs) — a mesma lista que
  qualquer um vê na aba "Vídeos". **Nunca** baixar o vídeo/áudio em si.
- Caminho 100% oficial = YouTube Data API v3 (requer chave Google Cloud). O
  método atual (`yt-dlp --flat-playlist`) é área cinza dos ToS, aceito aqui por
  ser uso pessoal/educacional e zero download de conteúdo protegido. Se for
  preciso rigor estrito, migrar para a Data API.

## Pipeline

```bash
# 1. Extrair metadados (regenera data/barron_videos.tsv) — demora ~1 min
yt-dlp --flat-playlist --no-warnings --ignore-errors \
  --print "%(id)s\t%(title)s\t%(duration)s\t%(view_count)s\t%(upload_date)s" \
  "https://www.youtube.com/@BishopBarron/videos" > data/barron_videos.tsv 2> data/extract.log

# 2. Classificar por assunto e gerar o catálogo Markdown
python3 scripts/classificar.py
```

## Arquivos

- `data/barron_videos.tsv` — dump bruto do yt-dlp. **Quirk importante:** o `\t`
  do `--print` é gravado como os **dois caracteres literais `\` + `t`**, NÃO como
  tab real. Por isso o parser usa `line.split("\\t")`. Validar com `od -c`.
- `scripts/classificar.py` — classificador. Dois estágios: (1) **override por id**
  (`data/overrides.tsv`) tem prioridade absoluta; (2) fallback **keyword
  single-label por ordem de prioridade** (1ª regex que casa vence). Ordem das
  regras: séries/formatos identificáveis (Sunday Sermon, Catholicism, Pivotal
  Players, Bishop Barron Presents, WOF) primeiro; categoria genérica
  "Igreja/Vaticano" por último para não roubar vídeos das temáticas. **Nunca**
  usar `\bbishop\b` como keyword — casa com "Bishop Barron" em ~536 títulos.
  A ordem das SEÇÕES no `.md` é `ORDEM_EXIBICAO` (lista explícita).
- `data/overrides.tsv` (id → categoria) — classificação **manual/LLM** dos 526
  vídeos que o keyword-classifier deixava em "Outros" (títulos poéticos sem
  palavra-chave temática). Gerado por `scripts/gerar_overrides.py`, que contém a
  lista `CODES` (1 código por linha de `data/outros.tsv`, mesma ordem) +
  `CODE2CAT`. Resultado: balde "Outros" zerado, 1.574 vídeos em 19 categorias.
- `data/outros.tsv` — snapshot dos ids+títulos que foram classificados à mão;
  é a chave de ordem para `CODES` em `gerar_overrides.py`.
- `CATALOGO_BISHOP_BARRON.md` — saída: índice + uma tabela por assunto
  (`# | Título | Duração | Link`), pronta para copiar a coluna Link.

## Como ajustar a classificação

- Categoria de um vídeo específico errada → editar `data/overrides.tsv` (id →
  categoria) e rerodar `classificar.py`. Override sempre vence a keyword.
- Regra ampla nova (vale p/ muitos títulos) → editar `CATEGORIAS` e/ou
  `ORDEM_EXIBICAO` em `classificar.py`.
- Re-extraiu o canal e surgiram vídeos novos não cobertos → eles caem nas regras
  de keyword ou em "Outros"; reclassificar o "Outros" repetindo o fluxo
  `outros.tsv` → `CODES` em `gerar_overrides.py`.

## NotebookLM

O NotebookLM limita o nº de fontes por notebook (free ~50; Plus ~300). 1.574
vídeos não cabem num só notebook → o catálogo existe justamente para **selecionar
por assunto**. Considerar 1 notebook por tema (ex.: "Barron — Filosofia & Fé e
Razão") em vez de um único notebook gigante.
