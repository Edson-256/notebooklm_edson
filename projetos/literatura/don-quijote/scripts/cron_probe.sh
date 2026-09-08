#!/bin/bash
# Sonda de cota — Don Quijote (conta FREE 'espanhol').
#
# EXPERIMENTO (notebooklm_edson-g5e7, autorizado pelo Edson em 2026-09-08)
# ------------------------------------------------------------------------
# Em 02/09/2026 o Gemini Notebook passou a repor cota a cada ~5h ate um teto
# SEMANAL, com limite baseado em compute. Nenhum desses numeros e publicado e a
# UI desta conta NAO tem painel de uso (verificado 2026-09-08). A unica forma de
# conhecer os tetos e medir o que a API responde.
#
# Esta sonda roda de hora em hora e, a cada rodada, tenta criar ate PROBE_BATCH
# cenas. Para no primeiro RESOURCE_EXHAUSTED (NLM_STOP_ON_RATE_LIMIT=1), que e a
# fronteira que queremos datar. Cada desfecho vai para logs/nlm_usage.jsonl, onde
# rate-limit, falha real e criacao ficam separados — o log de texto os confunde.
#
# Por que hora em hora e nao a cada 5-6h: disparar na cadencia que se quer medir
# mede o proprio cron, nao a API. A sonda horaria acha a fronteira real da janela.
#
# SUBSTITUI o cron_daily.sh durante o experimento (mesma fase de download).
# Para encerrar: restaurar a linha original no crontab (ver README do experimento).

set -u

REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
PROJECT_DIR="$REPO_DIR/projetos/literatura/don-quijote"
RUNNER="$REPO_DIR/.claude/skills/leitura-formativa/scripts/audio_runner.py"
LOG_DIR="$REPO_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/donquijote_probe_${TS}.log"
PROFILE="espanhol"

PROBE_BATCH="${PROBE_BATCH:-5}"     # teto por rodada: granularidade sem esvaziar a fila
COTA_OVERRIDE="${COTA_OVERRIDE:-99}" # alto de proposito: quem freia e a API, nao o toml

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"
mkdir -p "$LOG_DIR"

# Lock por PID (mesma correcao de notebooklm_edson-aa1h): NUNCA expira por idade.
# Com sonda horaria e lotes que podem demorar, expirar por tempo garantiria
# execucoes concorrentes na mesma conta — exatamente o que contaminou os dados
# de setembro e o que este experimento precisa evitar para ter valor.
LOCKDIR="/tmp/.donquijote_probe.lock"
if [ -d "$LOCKDIR" ]; then
  lock_pid=$(cat "$LOCKDIR/pid" 2>/dev/null || echo "")
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    echo "$(date): sonda anterior ainda viva (pid=$lock_pid) — pulando esta rodada." >>"$LOG_DIR/donquijote_probe_lock.log"
    exit 0
  fi
  echo "$(date): lock orfao (pid='${lock_pid:-ausente}') — removendo." >>"$LOG_DIR/donquijote_probe_lock.log"
  rm -f "$LOCKDIR/pid" 2>/dev/null; rmdir "$LOCKDIR" 2>/dev/null
fi
mkdir "$LOCKDIR" 2>/dev/null || exit 0
echo "$$" > "$LOCKDIR/pid"
trap 'rm -f "$LOCKDIR/pid" 2>/dev/null; rmdir "$LOCKDIR" 2>/dev/null' EXIT

{
  echo "=== SONDA Don Quijote @ $(date) (batch=$PROBE_BATCH, cap=$COTA_OVERRIDE) ==="
  cd "$REPO_DIR" || exit 1

  # Fase 1: download do que ja esta pronto no studio (mesma do cron normal).
  echo "--- FASE DOWNLOAD ---"
  python3 "$RUNNER" --project "$PROJECT_DIR" --download
  echo "download exit: $?"

  # Fase 2: sondagem de criacao.
  echo "--- FASE SONDA ---"
  NLM_COTA_OVERRIDE="$COTA_OVERRIDE" NLM_STOP_ON_RATE_LIMIT=1 \
    python3 "$RUNNER" --project "$PROJECT_DIR" --profile "$PROFILE" --create "$PROBE_BATCH"
  rc=$?

  # Alerta so no momento que importa: a cota voltar depois de uma sequencia de recusas.
  python3 "$REPO_DIR/scripts/nlm_probe_notify.py" "$PROFILE"

  echo "=== exit code: $rc @ $(date) ==="
} >>"$LOG" 2>&1
