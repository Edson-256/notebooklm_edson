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

## Status atual (2026-07-04)

Infraestrutura pronta (Fase 1 rodada): `DQ-capitulos/` com 137 arquivos (128 unidades lógicas),
`_cenas_manifest.json` como esqueleto (`cenas: []`). **Autoria de cenas ainda não começou** — os
passos abaixo de Fase 2 em diante ainda não têm o que processar.

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

Sobe `don-quijote_p1_fonte_nlm.md` e `don-quijote_p2_fonte_nlm.md` **manualmente** no notebook
`a7117d29-754d-45b5-9cf7-eb6b646f64b8` (renomear antes para "Don Quijote de la Mancha").

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

## Fluxo típico (dois dias, quando a Fase 5 estiver ativa)

```bash
# Dia 1 — criar o lote do dia
python3 $RUNNER --project $PROJ --profile espanhol --create 2
# Dia 2 — baixar o que ficou pronto e criar o próximo lote
python3 $RUNNER --project $PROJ --download
python3 $RUNNER --project $PROJ --profile espanhol --create 2
```
