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

# ── Tudo abaixo está DORMENTE (exit 0 acima). Já corrigido para quando reativar
#    (bd notebooklm_edson-eev), espelhando o cron_audio.sh do Aristóteles:
#    cota marcada só após criação confirmada + detecção de auth case-insensitive.

# Patch de timeout do nlm (30s -> 120s) — sem ele o 'studio status' do --download
# estoura com ~783 artifacts (ver scripts/nlm_patch_timeout.py, bd notebooklm_edson-jvq).
python3 "$PROJECT_DIR/scripts/nlm_patch_timeout.py" >>"$LOG" 2>&1 || true

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
  create_out="$(mktemp)"
  "$VENV_PY" "$RUNNER" --max 20 | tee "$create_out"
  rc=${PIPESTATUS[0]}
  ok_count="$(grep -oE 'Criados OK: +[0-9]+' "$create_out" | tail -1 | grep -oE '[0-9]+$')"
  rm -f "$create_out"
  # Só marca a cota se pelo menos 1 áudio foi criado de fato. Antes marcava ANTES de
  # disparar: auth expirado / rate-limit / erro queimavam 25h sem consumir nada.
  if [ "${ok_count:-0}" -gt 0 ]; then
    nlm_quota_mark  # impede próxima rodada da conta 'default' por 25h
  else
    echo "quota guard: 0 áudios criados neste lote — NÃO marcando cota (nada foi consumido de fato)."
  fi
  echo
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

# Notificação fora do bloco redirecionado
if [ "${rc:-1}" -ne 0 ]; then
  if grep -qiE "nlm.*nao autenticado|auth.*expir|Authentication.*fail|ClientAuthenticationError" "$LOG" 2>/dev/null; then
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
  if grep -qiE "nlm.*nao autenticado|auth.*expir|Authentication.*fail|ClientAuthenticationError" "$LOG" 2>/dev/null; then
    _status="auth_expired"
  elif [ "${rc:-1}" -ne 0 ]; then
    _status="failed"; _rc="${rc:-1}"
    _sum="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
  else
    _status="ok"
  fi

  /opt/homebrew/bin/python3 "$PROJECT_DIR/scripts/tg_notify.py" report-state \
    --slug "cof" --project "Curso Online de Filosofia (COF v2)" \
    --path "projetos/filosofia/cof_v2" \
    --profile "default" --status "$_status" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    --run-cmd "bash $COF_DIR/scripts/cron_audio_daily.sh" \
    >/dev/null 2>&1 || true
}
_tg_report

# ── Auto-commit do metadata.json (progresso created->downloaded) ─────────
bash "$PROJECT_DIR/scripts/git_state_commit.sh" \
  "projetos/filosofia/cof_v2/audios/metadata.json" "cof" >/dev/null 2>&1 || true

exit "${rc:-1}"
