# Projeto COF — Curso Online de Filosofia (Olavo de Carvalho)

## Identificação

- **Notebook NotebookLM:** `12fec66e-81c2-4b94-b0d6-15d76a0b5e9b`
- **Conta:** `default` (edson.michalkiewicz@gmail.com) — usar `--profile default` em todo comando `nlm`.
- **Total de fontes no notebook:** 73 (ver `01_fontes_e_aulas.md`).

## Estrutura

```
projetos/cof/
├── CLAUDE.md                       # este arquivo
├── 01_fontes_e_aulas.md            # mapa hierárquico fonte → aula (gerado)
├── _sources_list.json              # `nlm source list` cru
├── _build_fontes_md.py             # regenera 01_fontes_e_aulas.md
├── _raw/
│   └── sources_content/            # conteúdo de cada compilação .md baixado
├── audios/                         # mp3s + metadata.json (futuro)
├── prompts_aulas/                  # prompts customizados por aula (futuro)
└── docs/                           # decisões/notas do projeto
```

## Estado atual

Estágio: **inventário das fontes concluído**. Próximas etapas (a definir):

1. Definir granularidade do material formativo (aula inteira? cena dentro de aula?
   tópico transversal entre aulas?). Ver `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`
   antes de desenhar o pipeline — não repetir o bug Quo Vadis de numeração local↔global.
2. Decidir formato dos áudios (deep_dive long? brief? por aula? por tema?).
3. Construir manifest canônico (`_prompts_manifest.json`) com **ID global único** ANTES
   de criar prompts ou disparar áudios.

## Inventário de fontes (resumo)

- **13 compilações por ano** (`Aulas Olavo - COF - 2009-a.md` … `2015.md`):
  205 aulas numeradas detectadas, faixa **001–287**, com datas entre
  14/03/2009 e meados de 2015. Markdown estruturado, parseável por regex
  `^Aula\s+\d+$` + busca de data nas próximas linhas.
- **3 compilações temáticas** (`2016.md`, `Apostilas.md`, `Artigos.md`,
  `Teoria do estado.md`): sem padrão `Aula NN` interno; agrupam material
  por tema/formato.
- **28 PDFs avulsos** (`COF - Aula 144.pdf` … `Aula 320.pdf`): cada PDF é
  uma aula isolada. Sem data no nome do arquivo.
- **7 livros/ensaios do Olavo** (PDFs/word_doc).
- **22 textos complementares** (prefixo `Unif_*`).

## Regras herdadas do ecossistema

- **Memória/tarefas:** Beads (`bd`) — ver `~/.claude/CLAUDE.md` e
  `~/dev/notebooklm_edson/CLAUDE.md`.
- **Pipeline de áudio:** seguir
  `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`. Em
  particular: ID canônico global único, manifest JSON como fonte da
  verdade, sanity-checks no startup, dry-run obrigatório, backup antes
  de reparar metadata.

## Comandos úteis

```bash
# Re-listar fontes do notebook
nlm source list 12fec66e-81c2-4b94-b0d6-15d76a0b5e9b --profile default --json > _sources_list.json

# Re-baixar conteúdo de uma compilação
nlm source content <SOURCE_ID> --profile default --output _raw/sources_content/<nome>.md

# Regenerar 01_fontes_e_aulas.md a partir do que já está em _raw/
python3 _build_fontes_md.py
```
