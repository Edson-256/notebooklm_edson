#!/bin/bash
# Job diario da skill leitura-formativa (1 projeto). Padrao 2 fases na MESMA rodada:
#   Fase 1: --download  -> baixa o que ficou pronto em rodadas anteriores (download "dia seguinte"
#           embutido: a rodada de hoje baixa o lote criado ontem; horas de folga, sem 90min).
#   Fase 2: --create N   -> cria o lote do dia (respeita cota diaria; rate-limit -> deferred).
# Telegram (lista de nomes criados/baixados) e disparado pelo proprio runner.
#
# NAO e instalado automaticamente. Para agendar, ver launchd/com.leitura-formativa.plist.template
# e o passo de instalacao (tarefa Beads de ativacao). Standby ate COF-2/Aristoteles concluirem.
#
# Uso:  run_daily.sh <caminho-do-projeto> [batch=19]
set -u

REPO="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
RUNNER="$REPO/.claude/skills/leitura-formativa/scripts/audio_runner.py"
PROJECT="${1:?uso: run_daily.sh <caminho-do-projeto> [batch]}"
BATCH="${2:-19}"

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"
# credenciais do Telegram (StudioM4_bot) e afins
[ -f "$HOME/.secrets" ] && source "$HOME/.secrets"

cd "$REPO" || exit 1
echo "=== leitura-formativa run_daily @ $(date '+%Y-%m-%d %H:%M:%S') | $PROJECT ==="

# Fase 1 — baixar prontos das rodadas anteriores
python3 "$RUNNER" --project "$PROJECT" --download

# Fase 2 — criar o lote do dia
python3 "$RUNNER" --project "$PROJECT" --create "$BATCH"
