#!/bin/bash
# Keep-alive da sessão nlm: renova os cookies Google antes de esfriarem.
#
# Por quê: os cookies do NotebookLM NÃO expiram por calendário (válidos até 2027),
# mas o Google invalida sessões ociosas em ~1 dia. Cada 'nlm login --check' dispara
# o refresh CSRF + reescreve o cookies.json (Layer 1 da auto-recuperação do nlm),
# mantendo a sessão viva. Roda a cada 8h via launchd (com.nlm.keepalive), que —
# diferente do cron — executa ao acordar se o Mac estava dormindo no horário.
#
# Se um perfil falhar no --check, a sessão já esfriou e SÓ um relogin manual
# (nlm login -p <perfil>, que abre o browser) resolve — então notifica.

set -u

REPO_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
LOG_DIR="$REPO_DIR/logs"
LOG="$LOG_DIR/nlm_keepalive.log"
PROFILES=(default italiano frances)

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

mkdir -p "$LOG_DIR"

notify_fail() {
  local p="$1"
  /usr/bin/afplay "/System/Library/Sounds/Funk.aiff" >/dev/null 2>&1 &
  if command -v terminal-notifier >/dev/null 2>&1; then
    terminal-notifier -title "NLM keep-alive — relogin necessário" \
      -message "Perfil '$p' falhou no --check. Rode: nlm login -p $p" \
      -sound Funk -group "nlm-keepalive" >/dev/null 2>&1
  fi
  /opt/homebrew/bin/python3 "$REPO_DIR/scripts/tg_notify.py" send \
    "⚠️ NLM keep-alive: perfil '$p' falhou no --check. Rode: nlm login -p $p" \
    >/dev/null 2>&1 || true
}

echo "=== keep-alive @ $(date '+%Y-%m-%d %H:%M:%S') ===" >>"$LOG"

fails=0
for p in "${PROFILES[@]}"; do
  if NLM_PROFILE="$p" nlm login --check --profile "$p" >/dev/null 2>&1; then
    echo "  $p: OK (sessão renovada)" >>"$LOG"
  else
    echo "  $p: FALHOU — relogin manual necessário" >>"$LOG"
    notify_fail "$p"
    fails=$((fails + 1))
  fi
done

echo "  -> $fails falha(s)" >>"$LOG"

# Trim do log para não crescer indefinidamente (mantém últimas 500 linhas).
if [ -f "$LOG" ]; then
  tail -n 500 "$LOG" >"$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
fi

exit 0
