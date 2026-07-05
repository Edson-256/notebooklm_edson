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

## Estrutura (provisionada — infraestrutura pronta; cenas ainda por autorar)

```
output/chapters/               129 .md brutos copiados do docling-projeto (intocados, auditoria)
DQ-capitulos/                  137 arquivos (128 unidades logicas: 2 prólogos + 126 capítulos;
                                9 capítulos longos splitados em 2 partes) + _capitulos_index.json
_cenas_manifest.json           esqueleto (cenas: []) — autoria fica para sessões seguintes
cenas/, prompts_cenas/, audios/  vazias — populadas nas próximas fases
projeto.toml                   config lida pelo audio_runner.py
scripts/
  build_manifest.py            Fase 1 (custom) — fragmentação parte-aware, já executado
  postprocess_prompts.py       Fase 3+ (custom) — diretiva es-ES + anúncio "Parte I/II, capítulo N"
  build_nlm_sources.py         Fase 4 (custom) — 2 arquivos-fonte (1 por Parte), mesmo notebook
```

**128 unidades incluídas** (52 capítulos + prólogo da Primeira Parte, 74 capítulos + prólogo da
Segunda Parte), **379.817 palavras** limpas. Estimativa de planejamento para a Fase 2 (autoria de
cenas, 1–5 por capítulo): **~250–330 cenas** (central ~290) — o trabalho realmente grande do
projeto, muito maior que montar esta infraestrutura.

## Reproduzir o build desta infraestrutura (do diretório do projeto)

```bash
python3 scripts/build_manifest.py --dry-run     # relatório: 128 unidades, exclui Z-BackMatter
python3 scripts/build_manifest.py               # escreve DQ-capitulos/ + índice + manifest-esqueleto
```

`postprocess_prompts.py` e `build_nlm_sources.py` só têm efeito depois que a Fase 2 (autoria de
cenas, leitura capítulo a capítulo com critério COF) e a Fase 3 genérica (`03_build_prompts.py` da
skill) rodarem — hoje eles só verificam pré-condição e saem sem erro.

## Próximos passos

1. **Autoria de cenas** (Fase 2, sessões seguintes): ler cada uma das 128 unidades em
   `DQ-capitulos/` e preencher `_cenas_manifest.json` com 1–5 cenas por capítulo (critério COF:
   tensão moral, decisão existencial, monólogo interno, choque de perspectiva, experiência
   vicariante), seguindo `.claude/skills/leitura-formativa/templates/prompt_identificacao_cena_por_capitulo.md`.
2. Rodar `02_build_scene_files.py` (genérico) → `cenas/`.
3. Rodar `03_build_prompts.py` (genérico) → `prompts_cenas/`, depois `scripts/postprocess_prompts.py`
   (injeta es-ES + anúncio Parte/capítulo).
4. Rodar `scripts/build_nlm_sources.py` → `don-quijote_p1_fonte_nlm.md` +
   `don-quijote_p2_fonte_nlm.md`.
5. Renomear o notebook vazio existente no perfil `espanhol` (`a7117d29-754d-45b5-9cf7-eb6b646f64b8`)
   para "Don Quijote de la Mancha" e subir as 2 fontes.
6. `audio_runner.py --status` / `--create N` / `--download` — ver `RUNBOOK.md`.
