# Guia — gerar e baixar áudios dos projetos (manual, no iTerm)

> **Última verificação:** 2026-06-11. Este guia reflete o que **realmente existe e funciona hoje**.
> Onde um passo ainda não está pronto, está marcado **⚠️ NÃO PRONTO** — não tente "adivinhar" o comando.

## 0. Antes de tudo — duas regras de ouro

1. **Diretório importa.** Cada runner roda de um diretório específico (indicado em cada seção). Se errar o diretório, o caminho relativo dos scripts/manifests quebra.
2. **Conta e cota (rolling 24h, Pro = 20 áudios/dia por conta):**
   - **`default`** = `edson.michalkiewicz@gmail.com` (pessoal). **Já ocupada** por COF-2 + Aristóteles (alternância diária via cron). A **trilha de ficção** usa esta conta → **disputa a mesma cota de 20/dia**.
   - **`profissional`** = `edson@michalkcare.com`. Ociosa. O **Frye** usa esta conta como "motor" → **não** disputa com COF/Aristóteles.
   - Cheque a sessão antes de disparar: `nlm login --check --profile default` (e `--profile profissional`).

---

## ⭐ Estratégia preferida: `profissional` como motor de alternância (1–2 áudios por vez)

A conta **pessoal (`default`) está comprometida** com COF-2 + Aristóteles (alternância diária, 20/dia).
Para gerar "um ou outro áudio" sem disputar essa cota, use a conta **`profissional`** (ociosa).
Duas formas:

### A) Frye — já está nesse esquema, é só disparar (jeito mais fácil) ✅
O runner do Frye **já gera na `profissional`**. Para fazer **um por vez** (alternância), use `--max`:
```bash
cd ~/dev/notebooklm_edson/projetos/critica-literaria/frye
python3 scripts/05_frye_runner.py generate fearful-symmetry --max 1 --confirm   # 1 áudio
python3 scripts/05_frye_runner.py generate fearful-symmetry --max 2 --confirm   # ou 2
```
Estado atual do *fearful-symmetry*: **29/39 baixados, 10 pendentes** — dá para escoar 1–2 por dia na cota ociosa. Veja sempre antes: `python3 scripts/05_frye_runner.py status fearful-symmetry`.

### B) Qualquer projeto (Blake, ficção, etc.) — receita crua `nlm` na `profissional`
Para um projeto **sem runner** (Blake) ou que está na conta pessoal (ficção), gere ad-hoc na `profissional` com `nlm` puro. **Uma vez por livro** você cria o notebook e sobe a(s) fonte(s); depois é 1 áudio por vez.

**Passo 1 — uma vez por livro: criar notebook + subir fonte(s) na `profissional`.**
```bash
# (exemplo Blake; ajuste paths/título)
cd ~/dev/notebooklm_edson/projetos/critica-literaria/blake

# cria o notebook na conta profissional e MOSTRA o id (anote)
nlm notebook create "Blake (motor profissional)" --profile profissional --json

# sobe as fontes que a unidade usa (Blake + capítulo do Frye). --wait até processar.
nlm source add <NOTEBOOK_ID> --file fontes_blake/C014-songs-of-experience.md --title "Songs of Experience" --wait --profile profissional
nlm source add <NOTEBOOK_ID> --file ../frye/fearful-symmetry/output/chapters/C006-6-Tradition-and-Experiment.md --title "Frye c6" --wait --profile profissional

# lista os ids das fontes do notebook (anote os que a unidade usa)
nlm source list <NOTEBOOK_ID> --profile profissional
```

**Passo 2 — por áudio: criar (usa o prompt da unidade como `--focus`).**
```bash
nlm audio create <NOTEBOOK_ID> -f deep_dive -l long --language pt-BR \
  --source-ids <ID_BLAKE>,<ID_FRYE> \
  --focus "$(cat prompts/prompt_05_songs-of-experience.md)" \
  --confirm --profile profissional
```

**Passo 3 — baixar (10–40 min depois; o `completed` é prematuro).**
```bash
# achar o artifact_id do áudio pronto
nlm studio status <NOTEBOOK_ID> --json --profile profissional
# baixar (extensão .m4a — NLM entrega AAC em container MP4)
nlm download audio <NOTEBOOK_ID> --id <ARTIFACT_ID> --output audios/05_songs-of-experience.m4a --no-progress
```
> **Notas:** (1) o `--focus` aceita o prompt inteiro via `"$(cat ...)"`; se o prompt for muito longo, o NLM trunca — os prompts deste projeto já são pensados para caber. (2) crie a pasta `audios/` antes (`mkdir -p audios`). (3) faça `nlm login --check --profile profissional` antes de começar.

---

## 1. FRYE — funciona hoje (conta profissional) ✅

**Diretório:** `~/dev/notebooklm_edson/projetos/critica-literaria/frye`

```bash
cd ~/dev/notebooklm_edson/projetos/critica-literaria/frye
```

Runner: `scripts/05_frye_runner.py` (modelo dual-conta: cria o notebook nas DUAS contas; gera os áudios na **profissional**; o notebook pessoal fica de referência; `teardown` apaga só o profissional no fim do livro). Subcomandos: `status` · `setup` · `generate` · `teardown`.

### 1a. Ver o estado (não dispara nada)
```bash
python3 scripts/05_frye_runner.py status fearful-symmetry
```

### 1b. Criar + baixar um lote parcial (ex.: 10 áudios)
O *fearful-symmetry* **já tem os 2 notebooks criados** (setup feito). Para gerar 10 e baixar:
```bash
python3 scripts/05_frye_runner.py generate fearful-symmetry --max 10 --confirm
```
- `generate` faz tudo: cria cada áudio (`--focus <prompt>`) → aguarda (poll) → **baixa o .m4a**.
- `--max 10` = só 10 áudios desta rodada (cota parcial). Sem `--confirm` é **dry-run** (mostra o que faria).
- Para escolher quais: `--only <ids/caps/formatos separados por vírgula>`.

### 1c. Os outros 5 livros do Frye (precisam de setup uma vez)
`educated-imagination`, `the-anatomy-of-criticism`, `the-great-code`, `fools-of-time`, `creation-and-recreation` têm `config.toml`, mas **ainda não criaram os notebooks**. Faça **uma vez** por livro (⚠️ cria notebook na conta pessoal + consome cota na profissional — é o checkpoint, confirme antes):
```bash
# 1) (dry-run) ver o que faria
python3 scripts/05_frye_runner.py setup the-great-code
# 2) criar de verdade os 2 notebooks + subir a fonte
python3 scripts/05_frye_runner.py setup the-great-code --confirm
# 3) depois, gerar em lotes
python3 scripts/05_frye_runner.py generate the-great-code --max 10 --confirm
```

### 1d. Ao terminar um livro inteiro (libera o notebook-motor)
```bash
python3 scripts/05_frye_runner.py teardown fearful-symmetry --confirm   # apaga só o notebook PROFISSIONAL
```

---

## 2. FICÇÃO (leitura-formativa) — funciona p/ Ivan; os outros 11 precisam de setup

**Diretório:** a **raiz do repo** `~/dev/notebooklm_edson` (o runner usa caminhos relativos a partir daí).

```bash
cd ~/dev/notebooklm_edson
```

Runner: `.claude/skills/leitura-formativa/scripts/audio_runner.py`. Usa a conta **`default`** (pessoal → disputa cota com COF/Aristóteles). **Standby por padrão**: sem flag de ação, só mostra status.

### 2a. Ver o estado (não dispara nada)
```bash
python3 .claude/skills/leitura-formativa/scripts/audio_runner.py --project projetos/literatura/a-morte-de-ivan-ilitch --status
```

### 2b. Criar lote parcial + baixar (Ivan Ilitch — já tem `projeto.toml`+notebook) ✅
```bash
# criar até 10 cenas pendentes
python3 .claude/skills/leitura-formativa/scripts/audio_runner.py --project projetos/literatura/a-morte-de-ivan-ilitch --create 10
# baixar o que já ficou pronto (de rodadas anteriores; o download "do dia seguinte" é o padrão)
python3 .claude/skills/leitura-formativa/scripts/audio_runner.py --project projetos/literatura/a-morte-de-ivan-ilitch --download
```
- `--create N` respeita a cota; `--all` cria todas as pendentes (também respeita cota).
- **Importante (download):** o NotebookLM marca `completed` antes do áudio estar baixável (janela de ~10–40 min). O padrão é **criar hoje, baixar na próxima rodada**.
- **Não** exporte `NLM_PROFILE` para outro perfil — o runner aborta se `NLM_PROFILE` ≠ perfil do projeto (guard anti-colisão). Sem a variável, ele usa o perfil do `projeto.toml` (`default`).

### 2c. ⚠️ Os outros 11 livros de ficção — NÃO PRONTOS p/ áudio
Têm cenas + prompts, **mas não têm `projeto.toml` nem notebook criado** (só o Ivan tem). Falta, por livro, um setup único: montar a fonte (`04_build_nlm_source.py`), criar o notebook, subir a(s) fonte(s) e escrever o `projeto.toml` com `notebook_id` + `source_ids`.
> **Não há um comando único de setup para ficção ainda.** Posso construir um helper `setup` (como o do Frye) para automatizar isso nos 11. **Até lá, não tente gerar áudio deles** — sem `projeto.toml` o runner não roda.

Lista dos 11: barrabas · the-robe · spartacus · o-poder-e-a-gloria · os-irmaos-karamazov-ed34 · crime-e-castigo · os-miseraveis · anna-karenina · o-idiota · guerra-e-paz · kristin-lavransdatter.

---

## 3. BLAKE (companion do Frye) — ⚠️ SEM RUNNER ainda

**Estado:** tem `guias/`, `prompts/`, `fontes_blake/`, `config.toml` e `_unidades_manifest.json`, mas **nenhum runner de áudio**. A estrutura é diferente da ficção (fonte = obra Blake **+ capítulo do Frye** por unidade), então o `audio_runner.py` da ficção **não** serve como está.

**Não existe `generate` para o Blake hoje.** Para o seu cenário "criar 10 do Blake", há dois caminhos:
- **(Recomendado)** eu construo um `blake_runner.py` (provavelmente reusando o modelo dual-conta do Frye, já que cada unidade junta Blake+capítulo do Frye) com `setup` / `generate --max N --confirm` / `download`. Aí o Blake fica igual ao Frye.
- **Manual cru** (tedioso, 1 unidade por vez), depois de criar o notebook e subir as 2 fontes da unidade:
  ```bash
  cd ~/dev/notebooklm_edson/projetos/critica-literaria/blake
  nlm audio create <NOTEBOOK_ID> -f deep_dive -l long --language pt-BR \
    --source-ids <id_obra_blake>,<id_cap_frye> \
    --focus "$(cat prompts/prompt_05_songs-of-experience.md)" \
    --confirm --profile profissional
  # baixar depois:
  nlm download audio <NOTEBOOK_ID> --id <ARTIFACT_ID> --output audios/05_songs-of-experience.m4a --no-progress
  ```

---

## 4. Comandos `nlm` avulsos (úteis em qualquer projeto)

```bash
nlm login --check --profile default          # renova/checa a sessão (rode antes de disparar)
nlm notebook list --profile profissional     # ver notebooks da conta
nlm studio status <NOTEBOOK_ID> --json --profile <perfil>   # status dos artefatos (áudios)
nlm download audio <NOTEBOOK_ID> --id <ARTIFACT_ID> --output <arquivo.m4a> --no-progress
```

## 5. Resumo — o que dá para fazer HOJE

| Projeto | Comando de criação parcial | Conta | Pronto? |
|---|---|---|---|
| **Frye fearful-symmetry** | `generate fearful-symmetry --max 10 --confirm` | profissional | ✅ |
| **Frye (outros 5)** | `setup <livro> --confirm` → `generate <livro> --max 10 --confirm` | profissional | ⚙️ setup 1×/livro |
| **Ficção: Ivan Ilitch** | `audio_runner.py --project … --create 10` / `--download` | default | ✅ |
| **Ficção: outros 11** | — | default | ⚠️ falta setup (posso automatizar) |
| **Blake** | — | a definir | ⚠️ falta runner (posso construir) |
