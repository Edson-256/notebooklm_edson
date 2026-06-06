#!/bin/bash
# Cron wrapper: Aristóteles — gera 100 cenas+prompts/dia em ordem de prioridade.
# Processo é leve (não chama NotebookLM, só prepara arquivos), em segundos.
# Notifica apenas em falha.

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/aristoteles"
RUNNER="$PROJECT_DIR/scripts/05_daily_cenas_runner.py"
REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
LOG_DIR="$REPO_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/aristoteles_cron_${TS}.log"
TAG="Aristóteles"
LIMIT="${ARISTOTELES_LIMIT:-100}"

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

mkdir -p "$LOG_DIR"

play_sound() {
  /usr/bin/afplay "/System/Library/Sounds/${1:-Funk}.aiff" >/dev/null 2>&1 &
}

notify() {
  local title="$1" msg="$2" sound="${3:-Funk}"
  play_sound "$sound"
  if command -v terminal-notifier >/dev/null 2>&1; then
    terminal-notifier -title "$title" -message "$msg" -sound "$sound" \
      -group "aristoteles-cron" >/dev/null 2>&1
  else
    local title_e="${title//\"/\\\"}" msg_e="${msg//\"/\\\"}"
    /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
  fi
}

{
  echo "=== $TAG cron run @ $(date) ==="
  echo "PWD=$PROJECT_DIR  LIMIT=$LIMIT"
  cd "$PROJECT_DIR" || { notify "$TAG cron ERRO" "cd falhou" "Basso"; exit 1; }
  /opt/homebrew/bin/python3 "$RUNNER" --limit "$LIMIT"
  rc=$?
  echo
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

if [ "${rc:-1}" -ne 0 ]; then
  summary="$(grep -E 'FAIL|ERRO' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
  [ -z "$summary" ] && summary="exit code $rc — ver $LOG"
  notify "$TAG cenas FALHOU (rc=$rc)" "$summary" "Basso"
else
  # Notifica apenas se concluiu tudo (status milestone)
  if grep -q "Nada a fazer" "$LOG" 2>/dev/null; then
    notify "$TAG cenas — COMPLETO" "Todas as cenas processadas." "Glass"
  fi
fi

exit "${rc:-1}"
