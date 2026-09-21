#!/bin/bash
# Liga/desliga o cron do Promessi Sposi comentando a linha no crontab do Mac.
#
#   ./cron_disable.sh            # desativa (comenta a linha)
#   ./cron_disable.sh --enable   # reativa (descomenta)
#   ./cron_disable.sh --status   # só mostra o estado atual
#
# Não remove nada: a linha fica no crontab prefixada com o marcador abaixo,
# então reativar é reversível e o backup fica em logs/.

set -u

PATTERN="I Promesi Sposi/scripts/cron_daily.sh"
MARKER="#PROMESSI-DISABLED# "
REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
BACKUP_DIR="$REPO_DIR/logs"
MODE="disable"

case "${1:-}" in
  --enable) MODE="enable" ;;
  --status) MODE="status" ;;
  --disable|"") MODE="disable" ;;
  *) echo "uso: $0 [--enable|--disable|--status]"; exit 2 ;;
esac

current="$(crontab -l 2>/dev/null)" || true
if [ -z "$current" ]; then
  echo "crontab vazio ou inacessível (no macOS pode faltar Acesso Total ao Disco para o Terminal)."
  exit 1
fi

show() {
  echo "--- linhas do Promessi no crontab ---"
  printf '%s\n' "$current" | grep -F "$PATTERN" || echo "(nenhuma)"
}

if [ "$MODE" = "status" ]; then
  show
  exit 0
fi

if ! printf '%s\n' "$current" | grep -qF "$PATTERN"; then
  echo "Nenhuma linha do Promessi encontrada no crontab — nada a fazer."
  exit 0
fi

mkdir -p "$BACKUP_DIR"
BACKUP="$BACKUP_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt"
printf '%s\n' "$current" > "$BACKUP"
echo "Backup do crontab: $BACKUP"

if [ "$MODE" = "disable" ]; then
  new="$(printf '%s\n' "$current" | awk -v pat="$PATTERN" -v mk="$MARKER" \
    'index($0, pat) && index($0, mk) != 1 { print mk $0; next } { print }')"
  action="desativado"
else
  new="$(printf '%s\n' "$current" | awk -v mk="$MARKER" \
    'index($0, mk) == 1 { print substr($0, length(mk) + 1); next } { print }')"
  action="reativado"
fi

printf '%s\n' "$new" | crontab -
current="$(crontab -l 2>/dev/null)"
echo "Cron do Promessi $action."
show
