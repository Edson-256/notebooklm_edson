# COF v2 — projeto de novo notebook NotebookLM

**Status:** compilação concluída em 2026-05-02, pronta para upload.

## Decisão estratégica

Em vez de completar o notebook existente (`12fec66e-81c2-4b94-b0d6-15d76a0b5e9b`,
73/300 fontes), o usuário optou por **criar um notebook novo do zero** com todo
o material disponível, partindo do disco do dell-server (cobertura completa).

O notebook antigo serve como referência histórica; este projeto produz fontes
para um notebook **novo**.

## Auditoria 01 vs 02

- **Aulas:** disco cobre 100% (222/222) das aulas que estavam no notebook antigo
  e tem mais 360 aulas adicionais. Disco é superset.
- **Livros:** 7 livros do Olavo estavam só no notebook (curtos textos como
  "A consciência da consciência", "Meditação e consciência" etc). Foram baixados
  via `nlm source content` para `_raw/livros_notebook/` e incorporados.
- **Compilações temáticas:** 4 fontes únicas do notebook (`2016`, `Apostilas`,
  `Artigos`, `Teoria do estado`) baixadas para `_raw/tematicas_notebook/` e
  copiadas para `compiladas/aulas/` mantidas sem reedição.
- **Unif extracurriculares:** sobreposição 100% (22 = 22). Conteúdo do disco
  é a fonte canônica.

## Critérios de compilação

- **Limite por fonte:** 450.000 palavras (margem de 10% sobre o teto NLM de 500k).
- **Aulas inteiras, sem corte:** se a próxima aula faria estourar, fechar o
  arquivo e abrir `YYYY-b`, `YYYY-c`, etc.
- **Preferência Remasterizado > Original** quando ambos existem (Aulas 1-40).
- **Header por aula:** `## Aula NNN — DD de mês de YYYY` para navegação
  dentro da fonte.
- **1 fonte = 1 livro** (folga no orçamento permite curadoria fina).
- **1 fonte = 1 curso extracurricular** (apenas o `Unif_*` unificado).

## Estrutura

```
projetos/cof_v2/
├── CLAUDE.md                          # este arquivo
├── _raw/
│   ├── dell_md/                       # 712 arquivos convertidos do disco
│   ├── livros_notebook/               # 7 livros baixados do notebook antigo
│   └── tematicas_notebook/            # 4 compilações temáticas baixadas
├── compiladas/                        # ←── fontes prontas para upload (121)
│   ├── aulas/                         # 25 anuais + 4 temáticas = 29
│   ├── livros/                        # 63 disco + 7 notebook = 70
│   └── extracurriculares/             # 22 Unif_*
├── scripts/
│   ├── 01_convert_to_md.py            # rodou no dell-server
│   ├── 02_compile_year_groups.py      # gera arquivos por ano
│   └── 03_collect_books_extras.py     # gera livros + Unif + temáticas
└── docs/
```

## Manifesto de fontes (121 totais)

### Aulas (29 fontes)

Anuais (25):
- `COF-Aulas-2009-a.md` — 19 aulas (Aula 001-019), 438,698 palavras
- `COF-Aulas-2009-b.md` — 18 aulas (Aula 020-038), 352,724 palavras
- `COF-Aulas-2010-a.md` — 23 aulas (Aula 039-060), 438,628 palavras
- `COF-Aulas-2010-b.md` — 26 aulas (Aula 061-086), 449,296 palavras
- `COF-Aulas-2010-c.md` — 1 aulas (Aula 087-087), 10,140 palavras
- `COF-Aulas-2011-a.md` — 33 aulas (Aula 089-121), 448,697 palavras
- `COF-Aulas-2011-b.md` — 14 aulas (Aula 122-135), 180,467 palavras
- `COF-Aulas-2012-a.md` — 34 aulas (Aula 136-169), 445,064 palavras
- `COF-Aulas-2012-b.md` — 17 aulas (Aula 170-185), 206,644 palavras
- `COF-Aulas-2013-a.md` — 34 aulas (Aula 186-219), 443,206 palavras
- `COF-Aulas-2013-b.md` — 13 aulas (Aula 220-232), 157,888 palavras
- `COF-Aulas-2014-a.md` — 43 aulas (Aula 233-274), 447,288 palavras
- `COF-Aulas-2014-b.md` — 2 aulas (Aula 275-276), 20,883 palavras
- `COF-Aulas-2015-a.md` — 34 aulas (Aula 277-315), 448,785 palavras
- `COF-Aulas-2015-b.md` — 5 aulas (Aula 316-320), 72,499 palavras
- `COF-Aulas-2016-a.md` — 38 aulas (Aula 321-354), 448,382 palavras
- `COF-Aulas-2016-b.md` — 7 aulas (Aula 356-365), 61,124 palavras
- `COF-Aulas-2017-a.md` — 43 aulas (Aula 367-407), 441,696 palavras
- `COF-Aulas-2017-b.md` — 7 aulas (Aula 408-412), 65,719 palavras
- `COF-Aulas-2018.md` — 40 aulas (Aula 455-454), 313,479 palavras
- `COF-Aulas-2019.md` — 45 aulas (Aula 456-500), 346,903 palavras
- `COF-Aulas-2020.md` — 48 aulas (Aula 501-548), 380,645 palavras
- `COF-Aulas-2021.md` — 34 aulas (Aula 549-584), 343,713 palavras
- `COF-Aulas-2022.md` — 3 aulas (Aula 585-545), 16,888 palavras
- `COF-Aulas-sem_data.md` — 1 aulas (Aula 000-000), 6,889 palavras

Temáticas (mantidas do notebook antigo, sem reedição):
- `COF-Tematicas-2016.md` (61,413 bytes)
- `COF-Tematicas-Apostilas.md` (2,220,702 bytes)
- `COF-Tematicas-Artigos.md` (448,930 bytes)
- `COF-Tematicas-Teoria-do-estado.md` (148,187 bytes)

### Livros (70 fontes)

Conteúdo individual; cada livro é uma fonte para curadoria fácil.

- `A Criminalidade em Ascensão uma Visão Civilizacional.md.md`
- `A Nova era e a revolução cultural.md.md`
- `A Organização Econômica.md.md`
- `A aula da Vontade.md.md`
- `A consciência da consciência - Olavo de Carvalho.md`
- `A consciência sem consciência - OIavo de Carvalho.md`
- `A depreciação da humanidade.md.md`
- `A filosofia de Mário Ferreira dos Santos.md.md`
- `A imortalidade como premissa do método filosófico.md.md`
- `A leitura Hermenêutica.md.md`
- … e mais 60 livros (lista completa em `compiladas/livros/`).

### Extracurriculares (22 fontes)

- `COF Extracurricular — A Guerra Contra a Inteligência o que estão fazendo para imbecilizar você.md`
- `COF Extracurricular — A crise da inteligência segundo Roger Scruton.md`
- `COF Extracurricular — A formação da personalidade.md`
- `COF Extracurricular — As raízes da modernidade.md`
- `COF Extracurricular — Ciência Política Saber, Prever e Poder.md`
- `COF Extracurricular — Como tornar-se um leitor inteligente.md`
- `COF Extracurricular — Conceitos fundamentais de psicologia.md`
- `COF Extracurricular — Conhecimento e moralidade.md`
- `COF Extracurricular — Consciência de imortalidade.md`
- `COF Extracurricular — Esoterismo na História e hoje em dia.md`
- `COF Extracurricular — Filosofia da ciência.md`
- `COF Extracurricular — Guerra Cultural história e estratégias.md`
- `COF Extracurricular — II Encontro de Escritores Brasileiros na Virginia.md`
- `COF Extracurricular — Introdução ao método filosófico.md`
- `COF Extracurricular — Introdução à filosofia de Eric Voegelin.md`
- `COF Extracurricular — Introdução à filosofia de Louis Lavelle.md`
- `COF Extracurricular — Mário Ferreira dos Santos Guia para o estudo de sua obra.md`
- `COF Extracurricular — Política e Cultura no Brasil história e perspectivas.md`
- `COF Extracurricular — Princípios e métodos da auto-educação.md`
- `COF Extracurricular — Ser e Poder Princípios e Métodos da Ciência Política.md`
- `COF Extracurricular — Simbolismo e ordem cósmica ontem e hoje.md`
- `COF Extracurricular — Sociologia da filosofia.md`

## Próximos passos

1. **Criar novo notebook** no NotebookLM (interface web ou via `nlm notebook create`).
2. **Upload das 121 fontes** via `nlm source add <NEW_NOTEBOOK_ID> compiladas/**/*.md`
   ou interface manual (drag-drop).
3. **Validar** que todas entraram (`nlm source list`).
4. **Construir manifest canônico** com IDs globais para o futuro pipeline de áudio
   (deep dive por aula). Aplicar regras de
   `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`.

## Comandos úteis

```bash
# Reconverter PDFs/DOCX no dell (se mais arquivos baixados)
ssh edson@100.71.148.95 "cd /home/edson/dev/cof && .venv/bin/python 01_convert_to_md.py"
rsync -aq edson@100.71.148.95:/home/edson/dev/cof/data/_md/ _raw/dell_md/

# Recompilar
python3 scripts/02_compile_year_groups.py
python3 scripts/03_collect_books_extras.py

# Verificar tamanho de uma compilação em palavras
wc -w compiladas/aulas/COF-Aulas-2017-a.md
```
