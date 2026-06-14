# RUNBOOK — Paradise Lost (geração e download de áudio)

Comandos do dia a dia do projeto. **Rodar sempre da raiz do repo** (`~/dev/notebooklm_edson`).

```bash
cd ~/dev/notebooklm_edson
RUNNER=.claude/skills/leitura-formativa/scripts/audio_runner.py
PROJ=projetos/literatura/paradise-lost
```

> **Dual-conta:** literatura mora na conta **pessoal** (`default`, notebook `e79a651a` = casa permanente).
> A **profissional** (`profissional`, notebook `222aaa91`) é cota livre temporária p/ agilizar.
> O `audios/metadata.json` registra **por cena** qual conta/notebook/artifact rodou → uma cena já
> criada **não é regerada em nenhuma conta**, e o download busca na conta certa sozinho.

---

## 1. Ver status (não toca a conta)

```bash
# perfil pessoal (cota da conta pessoal)
python3 $RUNNER --project $PROJ --status

# cota da conta profissional
python3 $RUNNER --project $PROJ --profile profissional --status
```

Mostra: nº de cenas por status (`created`/`downloaded`/`pendente`/…) e a cota usada hoje no perfil.

---

## 2. Prévia da fila (dry-run, não dispara nada)

```bash
python3 $RUNNER --project $PROJ --create 19 --dry-run
```

Lista as próximas N cenas pendentes e o nome do `.m4a` — sem criar.

---

## 3. Criar áudios

Escolha a conta por run. **Preferir pessoal**; usar profissional só p/ agilizar.

```bash
# PESSOAL (casa) — N cenas pendentes
python3 $RUNNER --project $PROJ --profile default --create 5

# PROFISSIONAL (agilizar) — N cenas pendentes
python3 $RUNNER --project $PROJ --profile profissional --create 19

# todas as pendentes (respeita a cota diária do perfil)
python3 $RUNNER --project $PROJ --profile default --all
```

- Cota: `por_dia=20`, `margem=1` → **até 19/dia** por conta (cota é rolling 24h; a real é o rate-limit).
- Entre criações o runner espera **120 s**. Lotes grandes: rodar em **background**:
  ```bash
  nohup python3 $RUNNER --project $PROJ --profile profissional --create 19 \
    > $PROJ/audios/_create_$(date +%Y%m%d_%H%M%S).log 2>&1 &
  ```
- Se a conta bater o limite, a cena vira `deferred` (não é falha) e reentra no próximo dia.

---

## 4. Baixar áudios

```bash
python3 $RUNNER --project $PROJ --download
```

- Baixa só o que está `completed`; o resto continua `created` (rode de novo depois — idempotente).
- **Não precisa de `--profile`**: cada cena é baixada na conta em que foi criada.
- Ao baixar: salva `.m4a` em `audios/`, dispara **sync dell/DROBO** e manda resumo no **Telegram**.
- ⏳ **Rodar D+1** (ou algumas horas depois). Logo após a criação o `completed` é **prematuro** e o
  download falha (o runner tem backoff `[0, 90, 240]s`, mas não adianta forçar cedo demais).

---

## 5. Checar prontidão no studio (sem baixar)

```bash
# profissional (onde estão as cenas 1–20)
NLM_PROFILE=profissional nlm studio status 222aaa91-eebd-4a4d-b95d-a2099dc5103a --profile profissional

# pessoal
NLM_PROFILE=default nlm studio status e79a651a-b2fc-4041-b766-c461b68a65bb --profile default
```

---

## Fluxo típico (dois dias)

```bash
# Dia 1 — criar um lote
python3 $RUNNER --project $PROJ --profile default --create 19      # ou --profile profissional
# Dia 2 — baixar o que ficou pronto e criar o próximo lote
python3 $RUNNER --project $PROJ --download
python3 $RUNNER --project $PROJ --profile default --create 19
```

## Estado atual (2026-06-13)

20/55 cenas **criadas** (1–20) na conta **profissional**, aguardando download. Pendentes: **21–55**.
Próximo passo: `--download` (D+1) das 20; depois gerar 21–55.

## Referência rápida de flags

| Flag | Efeito |
|---|---|
| *(nenhuma)* | só `--status` (standby) |
| `--dry-run` | prévia da fila, não dispara |
| `--create N` | cria até N cenas pendentes |
| `--all` | cria todas as pendentes (respeita cota) |
| `--download` | baixa as `created` que já estão `completed` |
| `--profile <p>` | conta desta run: `default` (pessoal) \| `profissional` |
| `--force` | ignora o guard de perfil (`NLM_PROFILE` divergente) |
