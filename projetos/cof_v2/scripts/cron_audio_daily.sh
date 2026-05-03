#!/bin/bash
# Cron wrapper: dispara próximo lote de 20 áudios COF v2 no NotebookLM.
# Roda 21h00 local (cron entry em `crontab -l`). Downloads ficam manuais.
# Runner auto-detecta o próximo seq pendente via metadata.json — sem --from/--to.

set -u

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
COF_DIR="$PROJECT_DIR/projetos/cof_v2"
VENV_PY="$COF_DIR/.venv/bin/python"
RUNNER="$COF_DIR/scripts/06_audio_runner.py"
LOG_DIR="$PROJECT_DIR/logs"
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$LOG_DIR/cof_cron_${TS}.log"

# Cron tem PATH minimalista; nlm fica em ~/.local/bin
export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

mkdir -p "$LOG_DIR"

{
  echo "=== COF cron run @ $(date) ==="
  echo "PWD=$COF_DIR"
  echo "PATH=$PATH"
  echo
  cd "$COF_DIR" || exit 1
  "$VENV_PY" "$RUNNER" --max 20
  rc=$?
  echo
  echo "=== exit code: $rc @ $(date) ==="
  exit $rc
} >>"$LOG" 2>&1
