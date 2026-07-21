#!/bin/bash
# Cron wrapper: Don Quijote de la Mancha (espanhol) — cota efetiva 2/dia (Free, margem=1).
# Runner da skill leitura-formativa cuida do dell-sync internamente (cfg [lifecycle] em
# projeto.toml). O relatório Telegram consolidado (título/caminho/data/Criados/Pendentes/
# Baixados até o momento — notebooklm_edson-d4p0) é montado por este wrapper no final,
# lendo logs/don-quijote_lastrun.json que as duas fases do runner alimentam.

set -u

REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
PROJECT_DIR="$REPO_DIR/projetos/literatura/don-quijote"
RUNNER="$REPO_DIR/.claude/skills/leitura-formativa/scripts/audio_runner.py"
LOG_DIR="$REPO_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/donquijote_cron_${TS}.log"
TAG="Don Quijote"
PROFILE="espanhol"

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
      -group "donquijote-cron" >/dev/null 2>&1
  else
    local title_e="${title//\"/\\\"}" msg_e="${msg//\"/\\\"}"
    /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
  fi
}

{
  echo "=== $TAG cron run @ $(date) ==="
  cd "$REPO_DIR" || { notify "$TAG cron ERRO" "cd falhou" "Basso"; exit 1; }

  # Fase 1: baixar itens criados em dias anteriores (limpa fila studio antes de criar novos)
  echo "--- FASE DOWNLOAD ---"
  python3 "$RUNNER" --project "$PROJECT_DIR" --download
  dl_rc=$?
  echo "download exit: $dl_rc"
  echo

  # Fase 2: criar novos áudios (--all respeita a cota diária efetiva do projeto.toml)
  echo "--- FASE CRIAÇÃO ---"
  python3 "$RUNNER" --project "$PROJECT_DIR" --profile "$PROFILE" --all
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

# ── Notificação Telegram (1 msg consolidada — mesmo padrão dos runners
# legados, notebooklm_edson-d4p0) ────────────────────────────────────────
# O runner grava logs/don-quijote_lastrun.json (download 1ª fase reseta,
# criação 2ª fase faz merge); aqui só resolvemos o status e mandamos.
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

  python3 "$REPO_DIR/scripts/tg_notify.py" report-state \
    --slug "don-quijote" --project "Don Quijote de la Mancha" \
    --path "projetos/literatura/don-quijote" \
    --profile "$PROFILE" --status "$_status" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    --run-cmd "python3 $RUNNER --project $PROJECT_DIR --profile $PROFILE --all" \
    >/dev/null 2>&1 || true
}
_tg_report

# ── Auto-commit do metadata.json (progresso created->downloaded) ─────────
bash "$REPO_DIR/scripts/git_state_commit.sh" \
  "projetos/literatura/don-quijote/audios/metadata.json" "don-quijote" >/dev/null 2>&1 || true

exit "${rc:-1}"
