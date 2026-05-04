#!/bin/bash
# Cron wrapper: dispara próximo lote de 20 áudios COF v2 no NotebookLM.
# Roda 21h00 local (cron entry em `crontab -l`). Downloads ficam manuais.
# Runner auto-detecta o próximo seq pendente via metadata.json — sem --from/--to.
#
# Notificação:
#   - Sucesso silencioso (não polui notification center)
#   - Falha → osascript display notification + som "Sosumi"
#   - Auth expirado é tratado como caso especial (mensagem orienta `nlm login`)

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
COF_DIR="$PROJECT_DIR/projetos/cof_v2"
VENV_PY="$COF_DIR/.venv/bin/python"
RUNNER="$COF_DIR/scripts/06_audio_runner.py"
LOG_DIR="$PROJECT_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/cof_cron_${TS}.log"

# Cron tem PATH minimalista; nlm fica em ~/.local/bin, osascript em /usr/bin
export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

mkdir -p "$LOG_DIR"

notify() {
  # $1 = title, $2 = message, $3 = sound (opcional)
  local title="$1" msg="$2" sound="${3:-Sosumi}"
  # Escapa aspas duplas para AppleScript
  local title_e="${title//\"/\\\"}"
  local msg_e="${msg//\"/\\\"}"
  /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
}

{
  echo "=== COF cron run @ $(date) ==="
  echo "PWD=$COF_DIR"
  echo "PATH=$PATH"
  echo
  cd "$COF_DIR" || { notify "COF cron ERRO" "cd $COF_DIR falhou" ; exit 1; }
  "$VENV_PY" "$RUNNER" --max 20
  rc=$?
  echo
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

# Notificação fora do bloco redirecionado para não poluir o log
if [ "${rc:-1}" -ne 0 ]; then
  if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
    notify "COF cron — AUTH EXPIRADO" \
           "nlm token expirou. Rode: nlm login --profile default" \
           "Funk"
  else
    # Pega últimas 2 linhas com ERRO/FALHOU para dar pista
    summary="$(grep -E 'ERRO|FALHOU|AVISO' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
    [ -z "$summary" ] && summary="exit code $rc — ver $LOG"
    notify "COF cron FALHOU (rc=$rc)" "$summary"
  fi
fi

exit "${rc:-1}"
