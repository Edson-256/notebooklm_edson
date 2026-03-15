#!/usr/bin/env bash
# Shakespeare Audio Batch - wrapper para execução via launchd/cron
# Roda a cada 12h, processando 20 cenas por execução (40/dia)

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${PROJECT_DIR}/logs"
TIMESTAMP=$(date +%Y-%m-%d_%H%M)
LOG_FILE="${LOG_DIR}/batch_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

echo "=== Shakespeare Batch Start: $(date) ===" | tee -a "$LOG_FILE"

# Rodar o batch processor
/opt/homebrew/bin/python3 "${PROJECT_DIR}/scripts/shakespeare_runner.py" \
    >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

echo "=== Shakespeare Batch End: $(date) | Exit: ${EXIT_CODE} ===" | tee -a "$LOG_FILE"

# Manter apenas logs dos últimos 30 dias
find "$LOG_DIR" -name "batch_*.log" -mtime +30 -delete 2>/dev/null || true

exit $EXIT_CODE
