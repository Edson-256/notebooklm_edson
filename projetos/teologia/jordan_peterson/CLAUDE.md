# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Objetivo

Catalogar os vídeos públicos do canal **Jordan B. Peterson** no YouTube
(`https://www.youtube.com/@JordanBPeterson/videos`) — apenas **títulos + links**,
sem baixar vídeo — e classificá-los por assunto, para que o usuário selecione os
relevantes e cole os links no **NotebookLM** (Adicionar fonte → Link do YouTube).

Subprojeto de `notebooklm_edson`, categoria temática `projetos/teologia/`. Segue o
**mesmo pipeline** do projeto irmão `../bishop_barron/` (ver o CLAUDE.md de lá: a
mecânica é idêntica; muda só o canal e o conjunto de categorias). Regras do repo
raiz valem: conta NLM `--profile default`, Beads, idioma de output pt-BR.

## Conformidade (YouTube ToS)

Extraímos **somente metadados públicos** (títulos + IDs) via `yt-dlp
--flat-playlist` — a mesma lista visível na aba "Vídeos". **Nunca** baixar o
vídeo/áudio. Caminho 100% oficial seria a YouTube Data API v3 (requer chave); o
método atual é área cinza dos ToS, aceito por ser uso pessoal/educacional sem
download de conteúdo protegido.

## Pipeline

```bash
# 1. Extrair metadados (regenera data/jbp_videos.tsv) — ~1-2 min
yt-dlp --flat-playlist --no-warnings --ignore-errors \
  --print "%(id)s\t%(title)s\t%(duration)s\t%(view_count)s\t%(upload_date)s" \
  "https://www.youtube.com/@JordanBPeterson/videos" > data/jbp_videos.tsv 2> data/extract.log

# 2. Classificar por assunto e gerar o catálogo Markdown
python3 scripts/classificar.py

# 3. (depois de escolher um grupo) adicionar ao notebook em lotes
#    via nlm source add <NB> -y <url> -y <url> ... (ver add_*.py do bishop_barron)
```

## Quirks herdados do pipeline (importantes)

- **Separador do TSV:** o `\t` do `--print` é gravado como os **dois caracteres
  literais `\` + `t`**, NÃO tab real → parser usa `line.split("\\t")`. Validar com
  `od -c data/jbp_videos.tsv | head`.
- **Ordem do TSV = mais recente primeiro** (ordem da aba "Vídeos"). Para
  "recentes→antigos" basta usar a ordem do arquivo; NÃO ordenar por título.
- **`nlm source add` cria a fonte mesmo sem `--wait`**; o título pode aparecer
  como a própria URL enquanto o NotebookLM processa o transcript. Vídeos sem
  legenda/transcript podem falhar no processamento mas ainda ocupam 1 slot.
- **Limite de fontes do notebook:** plano Plus/Pro = 300; grátis = 50. Confirmar
  com o usuário antes de encher.
- **Nunca** usar `\bpeterson\b`/`\bjordan\b` como keyword de classificação —
  casaria com o nome no título de muitos vídeos.

## Classificação

`scripts/classificar.py` (adaptado de `../bishop_barron/scripts/classificar.py`):
estágio 1 = override por id (`data/overrides.tsv`, classificação manual/LLM);
estágio 2 = keyword single-label por ordem de prioridade. Categorias específicas
do JP (ex.: Biblical Series / Exodus / Gospels, Maps of Meaning, palestras de
psicologia/personalidade, cultura & política, entrevistas/podcast, saúde mental
& autodesenvolvimento) ficam em `CATEGORIAS` + `ORDEM_EXIBICAO`. Saída:
`CATALOGO_JORDAN_PETERSON.md` (índice + tabela por assunto: `# | Título |
Duração | Link`).
```
