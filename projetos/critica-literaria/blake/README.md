# Blake — Companion do *Fearful Symmetry* (Frye)

Audiobook-companion em **pt-BR** para acompanhar a leitura de Blake **antes** do
*Fearful Symmetry* de Northrop Frye. O usuário **lê os versos de Blake em inglês**
(Kindle/EPUB); estes áudios **não leem poesia** — **explicam** Blake em português,
usando a **leitura de Frye como lente**.

## Decisões de desenho (usuário, 2026-06-11)

- **Áudio = explicação pt-BR**, não leitura dos poemas. **Guia escrito pt-BR** por unidade.
- **Lente = Frye**; **assunto = Blake** (Frye é a chave de leitura, não o tema).
- **Escopo focado** no que Frye centra: **13 unidades**, arco Blake autônomo, ouvir **antes** do Frye.
- **Fonte NotebookLM por unidade = obra(s) de Blake (limpa) + o capítulo correspondente do
  *Fearful Symmetry*** como 2ª fonte (ancora a explicação nas palavras reais de Frye).
- **NÃO é COF/leitura-formativa** (isso é ficção/experiência vicária). Aqui é **explicação de
  poesia**, irmão do método Frye não-ficção. Um deep-dive explicativo por unidade.

## Proveniência das fontes

- **Blake:** *Delphi Complete Works of William Blake* (EPUB, 58 MB) — convertido em
  `~/dev/_ref/docling-projeto/projects/literatura/blake/` (repo docling; EPUB não versionado).
  Os textos foram **limpos** (removidos `CONTENTS`/links de navegação, headers `imgN.png`,
  marcadores `\` de quebra) e copiados para `fontes_blake/`. As **notas editoriais Delphi**
  (1 parágrafo por obra) foram **mantidas** — são orientação útil.
- **Frye:** capítulos C001–C012 de `../frye/fearful-symmetry/output/chapters/` (2ª fonte por unidade).

## Estrutura

```
blake/
├── README.md
├── _unidades_manifest.json   # 13 unidades + mapa Blake↔Frye (2ª fonte)
├── config.toml
├── fontes_blake/             # 30 obras de Blake limpas (fontes NLM)
├── guias/                    # guia_NN_<slug>.md  (companion pt-BR — você lê)
└── prompts/                  # prompt_NN_<slug>.md (instruções EN → áudio pt-BR)
```

## As 13 unidades (3 camadas → 3 partes do Frye)

**Orientação:** 1 vida · 2 sistema mitológico [Frye c9] · 3 como Frye lê Blake [c1]
**Líricas:** 4 Songs of Innocence [c6] · 5 Songs of Experience [c6] · 6 pares contrários [c3] · 7 manifestos + Marriage [c3]
**Profecias:** 8 Orc/America+Europe [c7] · 9 Urizen [c8] · 10 Four Zoas I [c9] · 11 Four Zoas II [c9] · 12 Milton [c10] · 13 Jerusalem [c11+c12]

## Estado

- **Setup + piloto** (unidades 2 e 5) — em construção.
- Áudio fica **na fila** (gated por conta/cota NLM + checkpoint), como o resto do projeto.
