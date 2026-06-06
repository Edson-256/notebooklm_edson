# Workflow de Geração de Áudios — Híbrido (CLI + Manual)

> **Estado atual:** infraestrutura pronta em standby. CLI não vai disparar áudio
> até você ativar o cron (`cron_audio.sh.template` → `cron_audio.sh` + crontab).
> Você pode usar o fluxo manual via UI desde já.

## Visão geral dos dois canais

O NLM tem dois limites distintos:

| Canal | Limite/dia | Quando usar |
|---|---|---|
| **CLI** (`nlm studio create`) | **20** (silencioso) | Automação cron noturna. |
| **UI manual** (notebooklm.google.com) | **~50** (teórico) | Acelera enquanto outros crons rodam. |

Ambos os canais escrevem áudios no mesmo "Studio" do notebook. O script
`07_audio_runner.py` baixa e organiza áudios de qualquer origem.

## Notebook

- **Título:** Aristóteles (completo)
- **ID:** `48eb1ca3-5f9b-484a-be94-fe959c3e40dc`
- **URL:** https://notebooklm.google.com/notebook/48eb1ca3-5f9b-484a-be94-fe959c3e40dc
- **Sources:** 33 obras canônicas (ver `_raw/notebook_aristoteles.json`)

## Convenção de nome de áudio

```
aristoteles_{NN_obra}_{LLL}_{CCC}_cena{SS}_{slug_obra}.m4a
```

- `NN_obra` (01-33): ordem do *Corpus Aristotelicum* (ver source titles no NLM)
- `LLL` (l01-l20): livro
- `CCC` (c01-c99): capítulo
- `SS` (01-10): sub-cena (para capítulos grandes)
- `slug_obra`: identificador humano-legível (`etica_nicomaco`, `on_dreams`, …)

Exemplo: `aristoteles_25_l01_c01_cena01_etica_nicomaco.m4a` = Nicomachean Ethics
(obra 25), Book I, Chapter 1, primeira sub-cena.

Esse nome aparece **no topo do prompt** (`obras/*/prompts/*.md`) como instrução
ao operador: o áudio gerado deve ser renomeado para esse título no NLM Studio.

## Comandos principais

```bash
# ── Inspeção ───────────────────────────────────────────────────────────
python3 scripts/07_audio_runner.py --status
python3 scripts/07_audio_runner.py --list-pending 10
python3 scripts/07_audio_runner.py --show-prompt 05_etica/01_etica_nicomaco/L01-C01_cena01

# ── Modo manual (UI) ───────────────────────────────────────────────────
# 1. lista as próximas (--list-pending)
# 2. copia o prompt do arquivo .md mostrado e cola no NLM
#    (Audio Overview > Customize)
# 3. Renomeia o áudio gerado no Studio para o "audio_title" do prompt
# 4. Quando tiver gerado N áudios, baixa em lote:
python3 scripts/07_audio_runner.py --harvest

# ── Modo CLI (cron, em standby) ────────────────────────────────────────
# Cria 5 áudios novos via CLI + baixa o que está pronto:
python3 scripts/07_audio_runner.py --create 5
python3 scripts/07_audio_runner.py --harvest

# ── Caso especial: gerou manual mas esqueceu de renomear ───────────────
# Pega o artifact_id no NLM UI (ou via `nlm studio status NOTEBOOK_ID --json`)
# e associa à cena correta — renomeia + baixa automaticamente:
python3 scripts/07_audio_runner.py --claim <ARTIFACT_ID> <CENA_ID>
```

## Fluxo manual passo-a-passo

1. **Ver o que vem em seguida** (em ordem de prioridade canônica):
   ```bash
   python3 scripts/07_audio_runner.py --list-pending 5
   ```

2. **Abrir o prompt da cena escolhida** (caminho aparece no `--list-pending`):
   ```bash
   cat obras/05_etica/01_etica_nicomaco/prompts/L01-C01_cena01.md | pbcopy
   ```
   (pega o conteúdo e copia para o clipboard)

3. **Ir no NLM Web** e gerar o áudio:
   - Abrir https://notebooklm.google.com/notebook/48eb1ca3-5f9b-484a-be94-fe959c3e40dc
   - Clicar em **Audio Overview** → **Customize**
   - Colar o prompt completo (já tem o título e cabeçalho instrucional)
   - Gerar (~5-10 minutos)

4. **Renomear o áudio gerado** no Studio do NLM:
   - Localizar o áudio recém-gerado no painel Studio
   - Clicar nos `…` → Renomear
   - Colar o `audio_title` que aparece no topo do prompt
     (ex: `aristoteles_25_l01_c01_cena01_etica_nicomaco`)

5. **Quando acumular vários áudios renomeados**, rodar:
   ```bash
   python3 scripts/07_audio_runner.py --harvest
   ```
   Esse comando lista os artifacts do studio, baixa os que batem com
   `aristoteles_*` e atualiza o tracking local (`_raw/audio_metadata.json`).

### Se esqueceu de renomear no Studio

Use `--claim` para corrigir após o fato:

```bash
# Vê o id do artifact com título "errado"
nlm studio status 48eb1ca3-5f9b-484a-be94-fe959c3e40dc --json | jq

# Associa ao cena_id correto — renomeia no NLM e baixa
python3 scripts/07_audio_runner.py --claim abc123ef-... 05_etica/01_etica_nicomaco/L01-C01_cena01
```

## Estado e logs

| Arquivo | O que tem |
|---|---|
| `_raw/cenas_master.json` | 1695 cenas planejadas em ordem canônica (priority_rank) |
| `_raw/notebook_aristoteles.json` | mapping obra → source_id no NLM |
| `_raw/audio_metadata.json` | status por cena: `pending` / `created` / `downloaded` |
| `_raw/audio_log.jsonl` | log incremental de cada criação/download |
| `audios/` | arquivos .m4a baixados, com nome padronizado |

## Ativar o cron (quando COF v2 terminar)

```bash
cp scripts/cron_audio.sh.template scripts/cron_audio.sh
chmod +x scripts/cron_audio.sh

crontab -e
# Adicionar a linha (sugestão 7:00 — convive com Promessi 8:00 / Notre Dame 8:05):
0 7 * * * /Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/aristoteles/scripts/cron_audio.sh
```

> **Atenção:** O comando `--create` ainda está em modo *stub* (apenas registra, não
> chama `nlm studio create` ainda). Antes de ativar o cron, valide a sintaxe exata
> de `nlm studio create` na sua versão do CLI e descomente/ajuste o bloco em
> `07_audio_runner.py:cmd_create`. O modo `--harvest` já está totalmente operacional.
