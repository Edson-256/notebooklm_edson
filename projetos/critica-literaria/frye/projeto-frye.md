# Plano — Modelo de processamento dos livros (projeto Frye / não-ficção)

## Context
O projeto Frye (parqueado em bd `notebooklm_edson-jui`) vai transformar as obras de
crítica literária de Northrop Frye em séries de áudio NotebookLM, usando o **leque de 6
formatos** (`docs/referencia_formatos_audio_naoficcao.md`). A questão a resolver era a
**unidade de processamento** — capítulo, grupo ou livro inteiro. Este plano fixa o modelo,
fundamentado na mecânica real do pipeline `leitura-formativa` e na forma real dos capítulos
do Docling. NÃO será uma skill genérica — é um projeto específico (decisão do usuário).

## Modelo de processamento (CONFIRMADO)

**Unidade = CAPÍTULO substantivo**, em **duas camadas**:

1. **Camada-livro** (poucos áudios/obra): Pórtico geral (mapa + status quaestionis da obra),
   Léxico (glossário fryeano), e a tese central do Filtro (conceito×símbolo da obra). Dá a
   visão de conjunto.
2. **Camada-capítulo**: cada capítulo recebe um **stack de formatos** — padrão **A→B→D**
   (Pórtico → Reconstrução Interna → Filtro); extras **C/E/F** (Arena / Meditatio / Léxico)
   nos capítulos densos. "Um prompt por capítulo" = "um stack por capítulo".

**Seleção de formato POR CAPÍTULO** (configurável): capítulo denso de obra simples pode
receber extras; capítulo leve de obra densa fica em A→B.

## Escopo desta fase: 6 obras (Notebooks ADIADO p/ Fase 2)

Ordem de estudo (geração/lançamento nesta ordem):
1. **The Educated Imagination** — entrada leve (A · Diálogo COF×Frye · E)
2. **Anatomy of Criticism** — o sistema (stack completo A·B·C·D·E·F)
3. **Fearful Symmetry** — gênese via Blake (A·B camada-dupla·D) ← **PILOTO técnico** (Docling mais limpo)
4. **Fools of Time** — aplicado a Shakespeare (A·B·D·E)
5. **Creation and Recreation** — pórtico bíblico (A·B·D·§2 antropologia)
6. **The Great Code** — ápice teológico (A·B·C·D-máx·níveis-de-significado·E)

**Notebooks for Anatomy** → Fase 2 (formato "laboratório" genético; exige agrupar entradas
minúsculas e dividir Notebook-7 de 46k).

## Pré-passo obrigatório: re-segmentar 2 obras
O Docling NÃO dividiu em capítulos:
- **Anatomy of Criticism** (155k, arquivo único `--single`): re-segmentar **por SEÇÃO**
  (sub-dividir os 4 ensaios em suas seções internas → unidades menores, áudios mais
  digeríveis). Intro polêmica + Conclusão tentativa como unidades próprias.
- **Educated Imagination** (bloco único ~27k): re-segmentar nas **~6 palestras Massey**.
- Ferramentas: `_ref/docling-projeto/tools/` (`split_md.py`, `convert_epub.py --level`,
  `split_pdf_text.py`). Ajustar os caminhos relativos (`../../../tools/`) ao rodar do destino.

## Pipeline (fork da leitura-formativa para dentro do projeto)
Reaproveitar a espinha dorsal; o coração (cenas→formatos) muda. Scripts vivem no projeto
`projetos/critica-literaria/` (versionar scripts + jsons de controle + prompts; NÃO o source).

- **Fase 1 — fragmentar (reuso quase intacto):** base `01_fragment_chapters.py`. Consome
  `output/chapters/`, pula front/back matter (`is_skippable`), divide cap >35min (ppm=130).
- **Fase 2 — REMOVIDA** (sem cenas). Substituída por um **manifesto de unidades** (capítulos
  substantivos + camada-livro) com, por unidade, a **lista de formatos** a gerar.
- **Fase 3 — prompts (adaptar):** em vez de 1 prompt/cena, **N prompts por unidade (1 por
  formato)**. Criar **6 templates de prompt** (A–F) + 1 template "camada-livro". Cada template
  injeta a operação COF correspondente (ver `docs/referencia_formatos_audio_naoficcao.md` e
  `leitura_nao_ficcional/leitura_nao_ficcional_COF.md`).
- **Fase 4a — fonte NLM (adaptar):** marcadores por **capítulo** (não por cena).
- **audio_runner (adaptar):** loop por **(unidade × formato)**; filename
  `<seq>_cap-<cap>_<formato>_<slug>.m4a`; metadata/cota por (unidade, formato). Mantém
  cota diária, rate-limit=deferred, dell sync, Telegram.
- **Config:** trocar `[cenas]` por `[formatos]` (lista default + overrides por capítulo).
- **Idioma:** prompts em inglês, saída pt-BR (regra global) — confirmar por obra.

## Checkpoint obrigatório
**Avisar o usuário ANTES de criar o notebook na conta pessoal** (default) — diretiva explícita.

## Verificação (quando implementar)
- Rodar Fase 1 adaptada no **piloto (fearful-symmetry)** e conferir índice de capítulos +
  skip de front matter.
- Gerar em **dry-run** 1 stack A→B→D de 1 capítulo + os áudios da camada-livro; **revisar os
  prompts** antes de criar qualquer áudio.
- Validar nomes `<seq>_cap-<cap>_<formato>_<slug>` e a contagem esperada de áudios
  (Σ camada-livro + Σ por-capítulo×formatos).
- Só então criar o notebook (com aval) e disparar 1 lote pequeno; baixar no dia seguinte.

## Notas de execução futura
- O build completo (fork dos scripts + 6 templates + re-segmentação + migração das pastas)
  é grande; será disparado quando o usuário pedir "tocar o projeto Frye" (bd `jui`).
- Migração das pastas (cross-repo) e regras de versionamento já estão em `jui`.
