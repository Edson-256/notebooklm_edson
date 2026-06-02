#!/bin/bash
# Cron wrapper: dispara próximo lote de 20 áudios COF v2 no NotebookLM.
# Roda 21h00 local (cron entry em `crontab -l`). Baixa pendentes antes de criar novos.
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
COF_DIR="$PROJECT_DIR/projetos/cof_v2"
VENV_PY="$COF_DIR/.venv/bin/python"
RUNNER="$COF_DIR/scripts/06_audio_runner.py"
LOG_DIR="$PROJECT_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/cof_cron_${TS}.log"

# Cron tem PATH minimalista
export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

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

# Alternância diária com Aristóteles (mesma conta 'default', limite ~20/dia
# compartilhado): COF roda em dias PARES do ano; Aristóteles em ÍMPARES.
# (10# força base decimal — evita erro de octal em 008/009.)
DOY=$(( 10#$(date +%j) ))
if [ $(( DOY % 2 )) -ne 0 ]; then
  echo "$(date '+%Y-%m-%d %H:%M') — dia ímpar (DOY=$DOY): vez do Aristóteles, COF pula." >>"$LOG"
  exit 0
fi

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

# ── Notificação Telegram (sempre — sucesso e falha) ─────────────────────
# COF v2 usa print_summary com formato diferente: "Criados OK: N" / "Falhas: N"
_tg_report() {
  local _dl _dlp _crt _fal _status _rc _sum
  _dl=$(  awk '/Baixados:/{print $2+0}'                        "$LOG" | tail -1)
  _dlp=$( awk '/processando:/{for(i=1;i<NF;i++) if($i=="processando:") print $(i+1)+0}' "$LOG" | tail -1)
  _crt=$( awk '/Criados OK:/{print $NF+0}'                    "$LOG" | tail -1)
  _fal=$( awk '/Falhas:/ && !/Baixados:/{print $NF+0}'        "$LOG" | tail -1)

  if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
    _status="auth_expired"
  elif [ "${rc:-1}" -ne 0 ]; then
    _status="failed"; _rc="${rc:-1}"
    _sum="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
  else
    _status="ok"
  fi

  /opt/homebrew/bin/python3 "$PROJECT_DIR/scripts/tg_notify.py" report \
    --project "COF v2" --profile "default" --status "$_status" \
    --dl "${_dl:-0}" --dl-proc "${_dlp:-0}" \
    --created "${_crt:-0}" --failed "${_fal:-0}" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    >/dev/null 2>&1 || true
}
_tg_report

exit "${rc:-1}"
