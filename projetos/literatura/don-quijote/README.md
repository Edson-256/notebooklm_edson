# Projeto: Don Quijote de la Mancha — Miguel de Cervantes Saavedra (Leitura Formativa COF)

- **Fonte:** Miguel de Cervantes Saavedra, *El ingenioso hidalgo don Quijote de la Mancha* —
  **Primera Parte (1605)** e **Segunda Parte (1615)**, em **castelhano original** (sem tradução).
  Importado de `_ref/docling-projeto/projects/literatura/cervantes/output/chapters/` em 2026-07-04.
- **Idioma:** texto e cenas em **espanhol** (castelhano do século XVII); áudio em **es-ES moderno**,
  narrando e comentando no mesmo idioma do texto — sem tradução/gloss (diferente de projetos como
  Paradise Lost, onde original ≠ output). Perfil NLM `espanhol` (conta `edsonmdphd@gmail.com`,
  Free, 3 áudios/dia) — reservado para este projeto desde 2026-06-06.
- **Método:** Leitura Formativa do **COF** (Olavo de Carvalho) — 4 pilares + experiência vicária.
  Ver `.claude/skills/leitura-formativa/` e `SKILL_pipeline_audio_nlm.md` (raiz do repo).

## Particularidade crítica desta obra

Publicada em **duas Partes**, dez anos apartadas (1605/1615), com a Segunda Parte respondendo
diretamente à Primeira e a uma continuação apócrifa de terceiros (Avellaneda) — um metaromance
sobre si mesmo. A fonte Docling já preserva essa divisão (`P1-C0NN-*.md` / `P2-C0NN-*.md`).

- **Numeração global contínua** (`cap` 1–128) atravessa as duas Partes, para que os scripts
  genéricos da skill (`02_build_scene_files.py`, `04_build_nlm_source.py`) funcionem sem
  modificação. Campos extras `parte` (P1/P2) e `cap_natural` (o número que o leitor reconhece)
  ficam em `DQ-capitulos/_capitulos_index.json`, usados no anúncio falado e para gerar as 2 fontes.
- **Cada prólogo (P1 e P2) é 1 unidade própria** (`cap` 1 e 54) e está destinado a virar **1 cena
  única** na Fase 2 — são textos com peso literário genuíno (o prólogo de 1605 é a peça
  metaliterária mais citada de Cervantes; o de 1615 responde à continuação de Avellaneda), não só
  boilerplate de tassa/licença. Por isso **nunca são splitados** mesmo passando do limiar de 35 min
  (o prólogo de 1605 tem ~36 min) — dividir arriscaria cortar a cena ao meio entre 2 arquivos, o
  que quebraria o casamento de âncoras da Fase 4.
- **`Z-BackMatter.md` (índice de capítulos + notas, 14.603 palavras) é excluído por completo** do
  pipeline — fica só como cópia bruta em `output/chapters/` (auditoria), nunca entra em
  `DQ-capitulos/`, no manifesto ou nas fontes do NotebookLM.
- **Limpeza aplicada na Fase 1:** remoção de comentários `<!-- image -->` (capitulares/ornamentos),
  links de nota de rodapé inline `[[N]](#_ftnN)` e glifos de área privada Unicode (`U+E000`–`U+F8FF`,
  resquício de fonte decorativa do OCR do Docling) — nenhum desses tem correspondência de conteúdo
  fora do pipeline (o back-matter com as notas está excluído).

## Estrutura (pronta para gerar áudio — cenas/prompts/fontes já gerados)

```
output/chapters/               129 .md brutos copiados do docling-projeto (intocados, auditoria)
DQ-capitulos/                  137 arquivos (128 unidades logicas: 2 prólogos + 126 capítulos;
                                9 capítulos longos splitados em 2 partes) + _capitulos_index.json
_cenas_manifest.json           403 cenas (autoradas na Fase 2) — numeração global seq 1..403
_anchors.json                  806 âncoras (início/fim de cada cena), auto-curadas ao verbatim
cenas/                         403 descritores de cena (Fase 2)
prompts_cenas/                 403 prompts deep-dive (Fase 3; ep.1 explica método; demais citam 1 pilar)
don-quijote_p1_fonte_nlm.md    fonte única da Primeira Parte (1038 KB, 172 cenas marcadas)
don-quijote_p2_fonte_nlm.md    fonte única da Segunda Parte (1088 KB, 231 cenas marcadas)
projeto.toml                   config lida pelo audio_runner.py
scripts/
  build_manifest.py            Fase 1 (custom) — fragmentação parte-aware
  stitch_cenas.py              Fase 2 (custom) — monta manifesto+âncoras a partir da saída dos agentes,
                                numeração global, mapeia cena→arquivo físico, auto-cura âncoras ao verbatim
  postprocess_prompts.py       Fase 3+ (custom) — nuance "não traduzir o castelhano" + anúncio "Parte I/II, capítulo N"
                                (a diretiva-base es-ES já vem da skill: 03_build_prompts.py lê `language_name` do manifesto)
  build_nlm_sources.py         Fase 4 (custom) — 2 arquivos-fonte (1 por Parte), mesmo notebook
  _raw_cenas_calib.json        saída bruta dos agentes autores (caps 1-9, calibração) — auditoria/re-stitch
  _raw_cenas_resto.json        saída bruta dos agentes autores (caps 10-128) — auditoria/re-stitch
```

**403 cenas** em 128 unidades (172 na Primeira Parte, 231 na Segunda). Distribuição: 3 cenas em 98
capítulos, 4 em 24, 2 em 3, 1 em 2, 5 em 1 (média 3,15/cap — decisão do usuário 2026-07-05: aceitar
esta granularidade "1–3 com 3 como default"). Pilares COF: sinceridade 34% · meio 25% · intuição
23% · memória 18%.

## Como as cenas foram autoradas (Fase 2 — workflow paralelo + stitcher)

A autoria (identificar 1–5 cenas por capítulo com critério COF + âncoras verbatim) foi feita por um
**workflow de agentes em paralelo** (um agente Opus por capítulo, lê o texto e retorna JSON
estruturado com as cenas e âncoras). O `scripts/stitch_cenas.py` então monta deterministicamente o
`_cenas_manifest.json` e o `_anchors.json`: numeração global contínua, mapeamento de cada cena ao
arquivo físico (resolve splits `_p1/_p2` pela âncora de início), e **auto-cura das âncoras** —
matching tolerante a acento + fallback por prefixo, gravando sempre o texto verbatim real do
arquivo (alguns agentes copiaram sem acento ou trocaram 1 palavra; o stitcher corrige).

Reproduzir a partir da saída bruta dos agentes (sem re-rodar os agentes):

```bash
python3 scripts/stitch_cenas.py --input scripts/_raw_cenas_calib.json scripts/_raw_cenas_resto.json
python3 ../../../.claude/skills/leitura-formativa/scripts/02_build_scene_files.py --project .   # sanity + cenas/
python3 ../../../.claude/skills/leitura-formativa/scripts/03_build_prompts.py --project .        # prompts (es-ES)
python3 scripts/postprocess_prompts.py                                                           # nuance + anúncio
python3 scripts/build_nlm_sources.py                                                             # 2 fontes NLM
```

## Próximos passos (gerar áudio)

1. Renomear o notebook vazio existente no perfil `espanhol` (`a7117d29-754d-45b5-9cf7-eb6b646f64b8`)
   para "Don Quijote de la Mancha" e subir as 2 fontes (`don-quijote_p1_fonte_nlm.md` e `_p2_`).
2. `audio_runner.py --status` / `--create N` / `--download` — ver `RUNBOOK.md`. Cota Free ~2/dia →
   403 cenas ≈ ~6,7 meses rodando todo dia (a conta profissional pode agilizar; ver `projeto.toml`).
3. Verificar o áudio 1 (explica o método) antes de disparar o lote.
