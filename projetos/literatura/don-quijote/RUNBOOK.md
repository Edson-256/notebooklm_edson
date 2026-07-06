# RUNBOOK — Don Quijote de la Mancha (geração e download de áudio)

Comandos do dia a dia do projeto. **Rodar sempre da raiz do repo** (`~/dev/notebooklm_edson`),
exceto os scripts customizados deste projeto (rodam de dentro da própria pasta — ver Fase 1-4).

```bash
cd ~/dev/notebooklm_edson
RUNNER=.claude/skills/leitura-formativa/scripts/audio_runner.py
PROJ=projetos/literatura/don-quijote
```

> **Perfil:** `espanhol` (conta `edsonmdphd@gmail.com`), Free, **3/dia** (margem 1 → efetivo
> 2/dia). Muito mais lento que os projetos em conta Pro — estimativa de planejamento: ~4 a 7 meses
> só na fase de criação de áudio, depois que a autoria de cenas e as Fases 3/4 estiverem prontas.
>
> **Dual-conta (futuro):** quando quiser agilizar, a conta `profissional` (Pro, 20/dia, hoje
> ociosa) pode gerar os mesmos áudios mais rápido — **replicando** (não compartilhando) as 2
> fontes num notebook próprio dela. Ver bloco comentado `[notebooklm.accounts]` em `projeto.toml`.

---

## Status atual (2026-07-05)

**Ciclo completo automatizado.** Fases 1–4 concluídas: `DQ-capitulos/` (137 arquivos / 128 unidades),
`_cenas_manifest.json` com **403 cenas**, `_anchors.json` (806 âncoras verbatim), `cenas/` (403
descritores), `prompts_cenas/` (403 prompts es-ES). Fase 5: notebook renomeado, 2 fontes NLM
subidas via `nlm source add --file` (ready), cena 001 criada (aguardando D+1 p/ verificar). Cron
`scripts/cron_daily.sh` instalado (08:20 diário, download+create --all respeitando cota); o runner
já cuida de dell-sync + Telegram sozinho via `[lifecycle]`/`[telegram]` do `projeto.toml`. Podcast
registrado no dell-server (`_meta/don-quijote.toml`, `lifecycle/registry.toml`, cover gerado) —
feed em `https://dell-server.tail3f4f14.ts.net/don-quijote/feed.xml` (login `edson` / senha do
SplashID, mesma dos outros feeds), ainda vazio até o 1º episódio ser baixado e sincronizado.

## Fase 1 — Fragmentação (já executada; comando de referência para re-rodar se necessário)

```bash
cd $PROJ
python3 scripts/build_manifest.py --dry-run     # relatório sem escrever nada
python3 scripts/build_manifest.py               # (re)escreve DQ-capitulos/ + índice
```

⚠️ Rodar de novo **apaga e recria** `DQ-capitulos/` — se `_cenas_manifest.json` já tiver cenas
autoradas apontando para nomes de arquivo antigos, confirme que a fragmentação não mudou antes de
sobrescrever.

## Fase 2 — Autoria de cenas (trabalho grande, sessões seguintes, capítulo a capítulo)

Ler cada unidade em `DQ-capitulos/` (128 no total: 2 prólogos + 126 capítulos) e preencher
`_cenas_manifest.json` com 1–5 cenas por capítulo, seguindo
`.claude/skills/leitura-formativa/templates/prompt_identificacao_cena_por_capitulo.md`. Depois:

```bash
cd $PROJ
python3 ../../../.claude/skills/leitura-formativa/scripts/02_build_scene_files.py --project . --dry-run
python3 ../../../.claude/skills/leitura-formativa/scripts/02_build_scene_files.py --project .
```

## Fase 3 — Prompts (genérico + postprocess es-ES)

```bash
cd $PROJ
python3 ../../../.claude/skills/leitura-formativa/scripts/03_build_prompts.py --project . --dry-run
python3 ../../../.claude/skills/leitura-formativa/scripts/03_build_prompts.py --project .
python3 scripts/postprocess_prompts.py     # injeta diretiva es-ES + anúncio "Parte I/II, capítulo N"
```

## Fase 4 — Arquivo-fonte do NotebookLM (2 arquivos, 1 por Parte)

```bash
cd $PROJ
python3 scripts/build_nlm_sources.py --dry-run
python3 scripts/build_nlm_sources.py
```

Sobe `don-quijote_p1_fonte_nlm.md` e `don-quijote_p2_fonte_nlm.md` no notebook
`a7117d29-754d-45b5-9cf7-eb6b646f64b8` (renomear antes para "Don Quijote de la Mancha").
**Feito via CLI** (não precisou do browser): `nlm rename notebook <id> "Don Quijote de la Mancha"
--profile espanhol` + `nlm source add <id> --file <arquivo.md> --profile espanhol --wait`.

## Fase 5 — Runner (criação e download)

```bash
cd ~/dev/notebooklm_edson

# Ver status (não toca a conta)
python3 $RUNNER --project $PROJ --status

# Prévia da fila (dry-run, não dispara nada)
python3 $RUNNER --project $PROJ --create 2 --dry-run

# Criar áudios (perfil espanhol, cota efetiva ~2/dia)
python3 $RUNNER --project $PROJ --profile espanhol --create 2

# Baixar (D+1 — logo após a criação o "completed" é prematuro)
python3 $RUNNER --project $PROJ --download
```

- Se a conta bater o limite, a cena vira `deferred` (não é falha) e reentra no próximo dia.
- `nlm login --check --profile espanhol` antes de qualquer lote, se desconfiar de sessão expirada.
- **Cota efetiva padrão = 2/dia** (`margem=1` em `projeto.toml`, convenção do skill — reserva 1 slot
  de segurança na cota real de 3/dia da conta Free). Para acelerar pontualmente num dia específico,
  pode pedir para editar `margem=0` só naquele dia (cota cheia 3/dia) — decisão do Edson por sessão,
  não mudar o default do arquivo permanentemente.

## Fluxo típico (manual, se quiser rodar fora do cron)

```bash
# Dia 1 — criar o lote do dia
python3 $RUNNER --project $PROJ --profile espanhol --create 2
# Dia 2 — baixar o que ficou pronto e criar o próximo lote
python3 $RUNNER --project $PROJ --download
python3 $RUNNER --project $PROJ --profile espanhol --create 2
```

## Fase 6 — Automação completa (cron + Telegram + podcast dell-server)

Ativada em 2026-07-05:

- **Cron:** `scripts/cron_daily.sh`, `crontab -l` → `20 8 * * *` (08:20 diário, 20min depois do
  francês). Faz `--download` seguido de `--profile espanhol --all` (o `--all` já respeita a cota
  efetiva do `projeto.toml`). Log em `logs/donquijote_cron_*.log`.
- **Telegram:** já embutido no `audio_runner.py` da skill (não precisa de wrapper extra) — dispara
  via `[telegram] enabled = true` no `projeto.toml`; manda resumo de criação/download + o link do
  feed após o 1º download bem-sucedido.
- **Dell-sync + podcast:** `[lifecycle] dell_sync = true, dell_slug = "don-quijote"` no
  `projeto.toml` aciona `_sync_to_dell()` a cada download. Registrado em
  `~/dev/dell_server/podcast_system/lifecycle/registry.toml` +
  `_meta/don-quijote.toml` (parser do filename `NNN_cap-NNN_cena-NNN_slug.m4a`) + cover gerado
  (`covers/don-quijote.jpg`, accent dourado). Feed já no ar (vazio até o 1º episódio sincronizar):
  `https://dell-server.tail3f4f14.ts.net/don-quijote/feed.xml` (login `edson` / senha do SplashID,
  igual aos outros feeds — instalar no app de podcast do iPhone).
