#!/bin/bash
# Cron wrapper: Aristóteles — gera 20 áudios por janela via NLM CLI + harvest dos prontos.
#
# Roda a cada 2h (crontab: 0 */2 * * *). Só dispara criações quando o quota guard
# confirma >= 25h desde o último lote da conta 'default' (compartilhada com COF).
# O incremento natural de ~2h/rodada garante que COF e Aristóteles nunca colidam.
#
# Notifica em falha (auth expirado etc).

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/filosofia/aristoteles"
RUNNER="$PROJECT_DIR/scripts/07_audio_runner.py"
REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
LOG_DIR="$REPO_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/aristoteles_audio_${TS}.log"
TAG="Aristóteles ÁUDIO"
LIMIT="${ARISTOTELES_AUDIO_LIMIT:-20}"

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"
# Credenciais do StudioM4_bot (Telegram). tg_notify.py também faz fallback
# lendo ~/.secrets, mas sourcear aqui mantém o padrão do lifecycle.
source "$HOME/.secrets" 2>/dev/null || true

mkdir -p "$LOG_DIR"

play_sound() { /usr/bin/afplay "/System/Library/Sounds/${1:-Funk}.aiff" >/dev/null 2>&1 & }

notify() {
  local title="$1" msg="$2" sound="${3:-Funk}"
  play_sound "$sound"
  if command -v terminal-notifier >/dev/null 2>&1; then
    terminal-notifier -title "$title" -message "$msg" -sound "$sound" \
      -group "aristoteles-audio" >/dev/null 2>&1
  else
    local title_e="${title//\"/\\\"}" msg_e="${msg//\"/\\\"}"
    /usr/bin/osascript -e "display notification \"$msg_e\" with title \"$title_e\" sound name \"$sound\"" >/dev/null 2>&1 || true
  fi
}

# Cadência: COF concluído (782/782 em 2026-06-30) — alternância par/ímpar encerrada.
# Aristóteles agora roda TODO dia, limitado APENAS pelo quota guard (>=25h).
# Na prática: 1 lote de 20/dia derivando ~2h para frente por dia (cota NLM rolling 24h).
# (bd notebooklm_edson-fey)

# Quota guard: só roda se >= 25h desde o último lote da conta 'default'.
source "$REPO_DIR/scripts/nlm_quota_guard.sh"
nlm_quota_check >>"$LOG" || exit 0

{
  echo "=== $TAG cron run @ $(date) ==="
  echo "PWD=$PROJECT_DIR  LIMIT=$LIMIT"
  cd "$PROJECT_DIR" || { notify "$TAG cron ERRO" "cd falhou" "Basso"; exit 1; }

  echo
  echo "--- HARVEST (baixa áudios prontos no studio, inclui gerados manualmente na UI) ---"
  /opt/homebrew/bin/python3 "$RUNNER" --harvest
  rc_harvest=$?

  echo
  echo "--- CREATE (dispara novos áudios via CLI, respeitando limite $LIMIT) ---"
  create_out="$(mktemp)"
  /opt/homebrew/bin/python3 "$RUNNER" --create "$LIMIT" | tee "$create_out"
  rc_create=${PIPESTATUS[0]}
  ok_count="$(grep -oE 'Resultado: ok=[0-9]+' "$create_out" | tail -1 | grep -oE '[0-9]+')"
  rm -f "$create_out"
  if [ "${ok_count:-0}" -gt 0 ]; then
    nlm_quota_mark  # só marca cota se pelo menos 1 áudio foi criado de fato (impede próxima rodada por 25h)
  else
    echo "quota guard: 0 áudios criados neste lote — NÃO marcando cota (nada foi consumido de fato)."
  fi

  echo
  echo "--- STATUS final ---"
  /opt/homebrew/bin/python3 "$RUNNER" --status

  rc=$(( rc_harvest != 0 ? rc_harvest : rc_create ))
  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1

if [ "${rc:-1}" -ne 0 ]; then
  if grep -qiE "nlm.*nao autenticado|auth.*expir|ClientAuthenticationError" "$LOG" 2>/dev/null; then
    notify "$TAG — AUTH EXPIRADO" "Rode: nlm login --profile default" "Funk"
  else
    summary="$(grep -E 'FAIL|ERRO' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
    [ -z "$summary" ] && summary="exit code $rc — ver $LOG"
    notify "$TAG FALHOU (rc=$rc)" "$summary" "Basso"
  fi
fi

# ── Notificação Telegram (1 msg consolidada — 3 seções) ─────────────────
# O runner grava logs/aristoteles_lastrun.json (harvest=download+transferência,
# create=criados, status=pendentes); aqui só resolvemos o status e mandamos.
_tg_report() {
  local _status _rc _sum
  if grep -qiE "nlm.*nao autenticado|auth.*expir|Authentication.*fail|ClientAuthenticationError" "$LOG" 2>/dev/null; then
    _status="auth_expired"
  elif [ "${rc:-1}" -ne 0 ]; then
    _status="failed"; _rc="${rc:-1}"
    _sum="$(grep -E 'FAIL|ERRO|Error' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
  else
    _status="ok"
  fi

  /opt/homebrew/bin/python3 "$REPO_DIR/scripts/tg_notify.py" report-state \
    --slug "aristoteles" --project "Aristóteles — Corpus Completo" \
    --path "projetos/filosofia/aristoteles" \
    --profile "default" --status "$_status" \
    --rc "${_rc:-}" --summary "${_sum:-}" \
    --run-cmd "bash $PROJECT_DIR/scripts/cron_audio.sh" \
    >/dev/null 2>&1 || true
}
_tg_report

# ── Auto-commit do estado de áudio (status created->downloaded) ──────────
# _raw/audio_metadata.json tem exceção no .gitignore (resto do _raw/ ignorado).
bash "$REPO_DIR/scripts/git_state_commit.sh" \
  "projetos/filosofia/aristoteles/_raw/audio_metadata.json" "aristoteles" >/dev/null 2>&1 || true

exit "${rc:-1}"
