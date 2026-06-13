# Projeto: Paradise Lost — John Milton (Leitura Formativa COF)

- **Fonte:** John Milton, *Paradise Lost* (1667) — EPUB Feedbooks (origem Wikisource), **em inglês**.
  Importado do Docling (`_ref/docling-projeto/.../literatura/milton`) em 2026-06-13.
- **Idioma:** texto e cenas em **inglês** (verso); **áudio em pt-BR citando o verso original** e
  glosando cada citação (decisão do projeto, 2026-06-13).
- **Método:** Leitura Formativa do **COF** (Olavo de Carvalho) — 4 pilares + experiência vicária.
  Ver `leitura_formativa/metodologia_olavo_carvalho.md` e a skill `leitura-formativa`.

## Particularidade crítica desta obra

É uma **epopeia em verso**, não um romance — o método foi pensado para romances. A unidade "cena"
foi redefinida como os **grandes blocos dramático-morais** (invocação, concílio, solilóquio, tentação,
visão, expulsão). O eixo do projeto (*fio condutor*, anunciado no ep. 1 e resolvido no ep. 55) é o
contraste entre o **eu fechado** ("The mind is its own place"; "myself am Hell") e o **"paradise
within"** — que é a própria definição olaviana de romper a "cápsula individual". Satã é o teste
máximo da experiência vicária (vestir a pele do antagonista magnífico).

## Estrutura (provisionada — pronta para gerar áudio)

```
source/                       Paradise Lost - John Milton.epub
output/chapters/              C001 (front matter) + C002–C013 (Livros 1–12)
output/arguments.md           sumários em prosa por Livro (reconstrução editorial; o EPUB os omitiu)
PL-capitulos/                 os 12 Livros renomeados + _capitulos_index.json (fonte das cenas)
_cenas_manifest.json          55 cenas (seq global; cap = Livro; 1–6 cenas por Livro)
_anchors.json                 110 âncoras (1ª/última linha de verso de cada cena) — TODAS verificadas
cenas/                        55 descritores de cena (Fase 2)
prompts_cenas/                55 prompts deep-dive (Fase 3; ep.1 explica método; demais citam 1 pilar)
paradise-lost_fonte_nlm.md    arquivo-fonte único do NotebookLM (461 KB, 110 marcadores de cena)
projeto.toml                  config lido pelo audio_runner.py
scripts/                      build_manifest.py · postprocess_prompts.py · convert_milton.py
```

**55 cenas** (Livros 1–12): L1=5, L2=5, L3=4, L4=5, L5=4, L6=4, L7=4, L8=4, **L9=6**, L10=5, L11=5, L12=4.
Distribuição de pilares: *meio* 16 · *sinceridade* 14 · *memória* 13 · *intuição* 12.

## Reproduzir o build (do diretório do projeto)

```bash
python3 scripts/build_manifest.py                                   # manifest + anchors + QC âncoras
SK=../../../.claude/skills/leitura-formativa/scripts
python3 $SK/02_build_scene_files.py  --project .                    # cenas/
python3 $SK/03_build_prompts.py      --project .                    # prompts_cenas/
python3 scripts/postprocess_prompts.py                              # injeta diretiva pt-BR+verso
python3 $SK/04_build_nlm_source.py   --project .                    # paradise-lost_fonte_nlm.md
```

## Por que script próprio de conversão (`scripts/convert_milton.py`)

O EPUB Feedbooks marca os 12 livros como `# Part N` centralizado, que o `tools/convert_epub.py`
genérico (pandoc gfm) não preserva (perda de 99,5%). O `convert_milton.py` usa pandoc `-t markdown`,
remove os fences `:::` e desescapa artefatos. Validação: EPUB = 80.360 palavras; saída = 80.112 (99,7%).

## Próximos passos (gerar áudio)

1. Criar notebook NotebookLM (conta pessoal) com `paradise-lost_fonte_nlm.md` e colar o ID em `projeto.toml`.
2. `audio_runner.py --create N` (respeitar cota 20/dia, margem 1) → baixar no dia seguinte → dell + Telegram.
3. Verificar o áudio 1 (explica método + fio condutor) antes de disparar o lote.
