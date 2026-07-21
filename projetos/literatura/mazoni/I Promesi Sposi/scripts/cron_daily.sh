#!/bin/bash
# Cron wrapper: Promessi Sposi (italiano) — 3 áudios/dia (limite free).
# Notificações em camadas: afplay + terminal-notifier + osascript fallback.

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/mazoni/I Promesi Sposi"
RUNNER="$PROJECT_DIR/scripts/audio_runner.py"
REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
LOG_DIR="$REPO_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/promessi_cron_${TS}.log"
TAG="Promessi Sposi"
PROFILE="italiano"

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
      -group "promessi-cron" >/dev/null 2>&1
  else
    local title_e="${title//\"/\\\"}" msg_e="${msg//\"/\\\"}"
    /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
  fi
}

{
  echo "=== $TAG cron run @ $(date) ==="
  echo "PWD=$PROJECT_DIR"
  cd "$PROJECT_DIR" || { notify "$TAG cron ERRO" "cd falhou" "Basso"; exit 1; }

  # Fase 1: baixar itens criados em dias anteriores (limpa fila studio antes de criar novos)
  echo "--- FASE DOWNLOAD ---"
  /opt/homebrew/bin/python3 "$RUNNER" --download
  dl_rc=$?
  echo "download exit: $dl_rc"
  echo

  # Fase 2: criar novos áudios
  echo "--- FASE CRIAÇÃO ---"
  /opt/homebrew/bin/python3 "$RUNNER" --max 3
  rc=$?
  echo
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

if [ "${rc:-1}" -ne 0 ]; then
  if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
    notify "$TAG — AUTH EXPIRADO" \
           "nlm token expirou. Rode: nlm login --profile $PROFILE" "Funk"
  else
    summary="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
    [ -z "$summary" ] && summary="exit code $rc — ver $LOG"
    notify "$TAG FALHOU (rc=$rc)" "$summary" "Basso"
  fi
fi

# ── Notificação Telegram (1 msg consolidada — 3 seções) ─────────────────
# O runner grava logs/promessi_lastrun.json (criação+download+transferência);
# aqui só resolvemos o status e mandamos o resumo.
_tg_report() {
  local _status _rc _sum
  if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
    _status="auth_expired"
  elif [ "${rc:-1}" -ne 0 ]; then
    _status="failed"; _rc="${rc:-1}"
    _sum="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
  else
    _status="ok"
  fi

  /opt/homebrew/bin/python3 "$REPO_DIR/scripts/tg_notify.py" report-state \
    --slug "promessi" --project "I Promessi Sposi" \
    --path "projetos/literatura/mazoni/I Promesi Sposi" \
    --profile "$PROFILE" --status "$_status" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    --run-cmd "python3 $RUNNER" \
    >/dev/null 2>&1 || true
}
_tg_report

# ── Auto-commit do metadata.json (progresso created->downloaded) ─────────
bash "$REPO_DIR/scripts/git_state_commit.sh" \
  "projetos/literatura/mazoni/I Promesi Sposi/audios/metadata.json" "promessi" >/dev/null 2>&1 || true

exit "${rc:-1}"
