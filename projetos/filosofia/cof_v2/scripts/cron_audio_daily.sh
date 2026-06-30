#!/bin/bash
# Cron wrapper: dispara próximo lote de 20 áudios COF v2 no NotebookLM.
# Roda a cada 2h (crontab: 5 */2 * * *). Só dispara criações quando o quota guard
# confirma >= 25h desde o último lote da conta 'default' (compartilhada com Aristóteles).
# Runner auto-detecta o próximo seq pendente via metadata.json — sem --from/--to.
#
# Notificação em camadas (cron não tem identidade de app no macOS, então
# osascript sozinho é frágil — o notification center silencia sem permissão):
#   1. afplay   — som direto, sempre funciona, sem permissão
#   2. terminal-notifier — visual; precisa autorização única em
#      System Settings → Notifications (aparece como "terminal-notifier"
#      após o primeiro disparo)
#   3. osascript display notification — fallback se terminal-notifier sumir

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
COF_DIR="$PROJECT_DIR/projetos/filosofia/cof_v2"
VENV_PY="$COF_DIR/.venv/bin/python"
RUNNER="$COF_DIR/scripts/06_audio_runner.py"
LOG_DIR="$PROJECT_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/cof_cron_${TS}.log"

# Cron tem PATH minimalista
export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"
# Credenciais do StudioM4_bot (Telegram). tg_notify.py também faz fallback
# lendo ~/.secrets, mas sourcear aqui mantém o padrão do lifecycle.
source "$HOME/.secrets" 2>/dev/null || true

mkdir -p "$LOG_DIR"

play_sound() {
  # $1 = nome do arquivo .aiff em /System/Library/Sounds/
  local sound="${1:-Funk}"
  /usr/bin/afplay "/System/Library/Sounds/${sound}.aiff" >/dev/null 2>&1 &
}

notify() {
  # $1 = title, $2 = message, $3 = sound (opcional, default Funk)
  local title="$1" msg="$2" sound="${3:-Funk}"
  play_sound "$sound"
  if command -v terminal-notifier >/dev/null 2>&1; then
    terminal-notifier -title "$title" -message "$msg" -sound "$sound" \
      -group "cof-cron" >/dev/null 2>&1
  else
    local title_e="${title//\"/\\\"}" msg_e="${msg//\"/\\\"}"
    /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
  fi
}

# COF v2 CONCLUÍDO — 782/782 baixados e auditados no dell em 2026-06-30.
# Cron DESATIVADO: nada mais a criar/baixar. Sai ANTES do nlm_quota_mark, então
# NÃO consome a cota da conta 'default' — libera a conta inteira para o Aristóteles
# (que agora roda todo dia). Para reativar, remover este bloco. (bd notebooklm_edson-fey)
echo "$(date '+%Y-%m-%d %H:%M') — COF completo 782/782: cron desativado, saindo." >>"$LOG"
exit 0

# Quota guard: só roda se >= 25h desde o último lote da conta 'default' (COF ou Aristóteles).
source "$PROJECT_DIR/scripts/nlm_quota_guard.sh"
nlm_quota_check >>"$LOG" || exit 0

{
  echo "=== COF cron run @ $(date) ==="
  echo "PWD=$COF_DIR"
  echo "PATH=$PATH"
  echo
  cd "$COF_DIR" || { notify "COF cron ERRO" "cd $COF_DIR falhou" "Basso"; exit 1; }

  # Fase 1: baixar itens criados em dias anteriores
  echo "--- FASE DOWNLOAD ---"
  "$VENV_PY" "$RUNNER" --download
  dl_rc=$?
  echo "download exit: $dl_rc"
  echo

  # Fase 2: criar novos áudios
  echo "--- FASE CRIAÇÃO ---"
  nlm_quota_mark  # registra início do lote (impede próxima rodada por 25h)
  "$VENV_PY" "$RUNNER" --max 20
  rc=$?
  echo
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

# Notificação fora do bloco redirecionado
if [ "${rc:-1}" -ne 0 ]; then
  if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
    notify "COF cron — AUTH EXPIRADO" \
           "nlm token expirou. Rode: nlm login --profile default" \
           "Funk"
  else
    summary="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
    [ -z "$summary" ] && summary="exit code $rc — ver $LOG"
    notify "COF cron FALHOU (rc=$rc)" "$summary" "Basso"
  fi
fi

# ── Notificação Telegram (1 msg consolidada — 3 seções) ─────────────────
# O runner grava logs/cof_lastrun.json (criação+download+transferência);
# aqui só resolvemos o status (ok/failed/auth_expired) e mandamos o resumo.
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

  /opt/homebrew/bin/python3 "$PROJECT_DIR/scripts/tg_notify.py" report-state \
    --slug "cof" --project "COF v2" --profile "default" --status "$_status" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    --run-cmd "$COF_DIR/scripts/cron_audio_daily.sh" \
    >/dev/null 2>&1 || true
}
_tg_report

# ── Auto-commit do metadata.json (progresso created->downloaded) ─────────
bash "$PROJECT_DIR/scripts/git_state_commit.sh" \
  "projetos/filosofia/cof_v2/audios/metadata.json" "cof" >/dev/null 2>&1 || true

exit "${rc:-1}"
