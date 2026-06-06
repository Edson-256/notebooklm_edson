---
name: leitura-formativa
description: >-
  Leitura formativa de FICÇÃO (método COF) em áudio via NotebookLM CLI (nlm). Use quando o usuário
  quiser transformar um romance/obra de ficção em uma série de áudios "deep dive" estilo leitura
  formativa: consumir capítulos do Docling, identificar cenas, gerar prompts sequenciais, criar áudios
  no NotebookLM respeitando a cota diária, baixar no dia seguinte, arquivar no dell-server e notificar
  no Telegram. Escopo: conta pessoal (default) + perfis de idioma (italiano/frances/espanhol/alemao).
  Para NÃO-ficção (aulas/CME), ver a skill futura baseada em leitura_nao_ficcional_COF.md. Gatilhos:
  "gerar áudios do livro", "leitura formativa em áudio", "rodar o pipeline de áudio do projeto".
---

# leitura-formativa (ficção, método COF)

Skill que consolida o **melhor estado da arte** dos runners do repo: **formato de artefatos** do
quo_vadis (fragmentos, cenas, template de prompt) + **runner/automação** do cof_v2 (robustez).
Spec de design completa em `SKILL_pipeline_audio_nlm.md` (raiz do repo) — **leia antes de alterar**.

## Escopo e fonte dos livros
- **Contas:** só pessoal (`default`, pt-BR) + perfis de idioma. A profissional (michalkcare) **não**
  é usada aqui (share bloqueado por política de Workspace) — fica para a skill de não-ficção.
- **Livros:** movidos do Docling para **dentro do projeto** em `projetos/literatura/<livro>/output/`
  (13 obras, processadas aos poucos). O Docling **já fragmenta** (`chapters/`), **já segmenta por
  tempo** (`segments/`) e **já calcula duração** a 130 ppm (`tempo-leitura.md`/`segmentos-tempo.md`).
  → a Fase 1 **consome e renomeia**, não re-fragmenta; lê a duração do Docling (não recalcula).
- **Cron:** os scripts de agendamento ficam **prontos mas NÃO são instalados** automaticamente. A
  skill entrega um comando explícito de instalação; **o usuário adiciona ao cron/launchd no momento
  certo** (cada projeto é processado lentamente).

## Quando usar
- Transformar uma obra em série de áudios deep-dive (leitura formativa COF).
- Rodar/retomar a geração de áudios de um projeto existente (criar lote, baixar, status).
- Provisionar um projeto novo (fragmentar → cenas → prompts → config).

## Pipeline (scripts em `scripts/`)
1. `01_fragment_chapters.py` — obra → `<SIGLA>-capitulos/NN_cap-NN_*.md`. Padding dinâmico
   (≤99→2 díg., ≥100→3, ≥1000→4). Capítulo com áudio estimado >35 min → split em N partes
   (`_p1/_p2…`). Se já fragmentado (Docling/OCR), só renomeia.
2. `02_identify_scenes.py` — **capítulo a capítulo**, 1–5 cenas/cap → `cenas/NN_cap-NN_cena-NN_*.md`
   (conteúdo no **idioma original**). Gera `_cenas_manifest.json` (numeração global contínua).
   Requer revisão humana antes dos prompts.
3. `03_build_prompts.py` — manifest → `prompts_cenas/prompt_<nome-da-cena>.md`. Template **sequencial**.
4. `audio_runner.py` — cria/baixa áudios via `nlm`. Flags: `--dry-run --max-scenes N --from/--to
   --cap N --download --bootstrap --status --regen-prompts`.
5. `schedule_*.{launchd}` — job CRIAR (manhã) + BAIXAR (dia seguinte, idempotente).
6. lifecycle + `tg_notify` (lista de nomes) + keepalive estendido.

## Regras in&shy;negociáveis (lições aprendidas — não reintroduzir bugs)
- **Paralelismo entre contas SÓ via `NLM_PROFILE` (env var) em todo subprocess. NUNCA `nlm login
  switch` no runner** (grava estado global → quebra execução paralela). Ref: cof_v2:471.
- **Um notebook vive em UMA conta.** Não dá para gerar em conta sem acesso ao notebook
  (compartilhar pessoal→Workspace é bloqueado por `BLOCKED_BY_ADMIN_POLICY`).
- **Download exige `.m4a`** (AAC/MP4), nunca `.mp3`. Filenames em **NFC**.
- **`download audio` NÃO aceita `--profile`** — só respeita `NLM_PROFILE`.
- **Rate-limit é estado** (`deferred`), não falha. `poll_status` 3 estados (completed/failed +
  `_POLL_MISSING`/`_POLL_ERROR`). Download com backoff `[0,90,240]s`.
- **Cota:** pro=20/dia, free=3/dia. Contador por `(perfil, data-local)`, margem de 1, reset à
  meia-noite local. **Guard anti-colisão:** abortar se `NLM_PROFILE` ≠ perfil do projeto sem `--force`.
- **Idioma:** cenas no idioma original; **prompts sempre em inglês**; output = pt-BR (pessoal/profissional)
  ou idioma do perfil (italiano/frances/espanhol/alemao), sobreponível por prompt.
- **Metodologia da leitura formativa explicada SÓ no episódio 1**; demais só citam qual dos 4 pilares.
- **Nunca deletar o artifact do studio NLM** (acesso via app); só a cópia local entra no lifecycle.
- **Truncamento >10k chars:** evitar; se ocorrer, **avisar o nome do arquivo** (log + Telegram).

## Tabela de contas/perfis
Ver `SKILL_pipeline_audio_nlm.md` §1/Passo 6 (⚠️ cross-wiring: `.fr`→alemão, `.de`→frances) e a
memória do Beads (`bd memories nlm-contas`). Profissional (michalkcare) = worker independente.

## Config por projeto
`config.example.toml` neste diretório. Um arquivo por obra; o runner lê dele tudo (slug, notebook_id,
perfil, idioma, cota, paths). Estado interno (status/artifact_id/quota) fica em `audios/metadata.json`
+ `_daily_quota.json` — expostos ao usuário via `--status` legível (não precisa abrir JSON).

## Tarefas (Beads)
Épico `notebooklm_edson-m99`; fases jr3/h6s/71r/9g7/x6h/eaz/ay7/nv0/9ep. `bd ready` mostra a próxima.
