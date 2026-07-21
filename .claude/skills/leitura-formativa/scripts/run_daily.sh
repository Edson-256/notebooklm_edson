#!/bin/bash
# Job diario da skill leitura-formativa (1 projeto). Padrao 2 fases na MESMA rodada:
#   Fase 1: --download  -> baixa o que ficou pronto em rodadas anteriores (download "dia seguinte"
#           embutido: a rodada de hoje baixa o lote criado ontem; horas de folga, sem 90min).
#   Fase 2: --create N   -> cria o lote do dia (respeita cota diaria; rate-limit -> deferred).
# Telegram: 1 msg consolidada no final (título/caminho/data/Criados/Pendentes/Baixados até o
# momento — notebooklm_edson-d4p0), lendo logs/<slug>_lastrun.json que as 2 fases alimentam.
#
# NAO e instalado automaticamente. Para agendar, ver launchd/com.leitura-formativa.plist.template
# e o passo de instalacao (tarefa Beads de ativacao). Standby ate COF-2/Aristoteles concluirem.
#
# Uso:  run_daily.sh <caminho-do-projeto> [batch=19]
set -u

REPO="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
RUNNER="$REPO/.claude/skills/leitura-formativa/scripts/audio_runner.py"
PROJECT="${1:?uso: run_daily.sh <caminho-do-projeto> [batch]}"
BATCH="${2:-19}"
LOG_DIR="$REPO/logs"
TS="$(date +%Y%m%d_%H%M%S)"

export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"
# credenciais do Telegram (StudioM4_bot) e afins
[ -f "$HOME/.secrets" ] && source "$HOME/.secrets"

cd "$REPO" || exit 1
mkdir -p "$LOG_DIR"

# projeto.toml -> título/slug/perfil/caminho (usados no relatório consolidado)
read -r OBRA_TITULO OBRA_SLUG PROFILE <<< "$(python3 -c "
import tomllib, sys
cfg = tomllib.load(open('$PROJECT/projeto.toml', 'rb'))
print(cfg['obra']['titulo'], cfg['obra']['slug'], cfg['notebooklm']['profile'])
")"
PROJECT_PATH="$(python3 -c "import os; print(os.path.relpath('$PROJECT', '$REPO'))")"
LOG="$LOG_DIR/${OBRA_SLUG}_cron_${TS}.log"

{
  echo "=== leitura-formativa run_daily @ $(date '+%Y-%m-%d %H:%M:%S') | $PROJECT ==="

  # Fase 1 — baixar prontos das rodadas anteriores
  python3 "$RUNNER" --project "$PROJECT" --download
  dl_rc=$?

  # Fase 2 — criar o lote do dia
  python3 "$RUNNER" --project "$PROJECT" --create "$BATCH"
  rc=$?
  echo "=== exit code: $rc (download: $dl_rc) @ $(date) ==="
} >>"$LOG" 2>&1

# ── Notificação Telegram (1 msg consolidada, notebooklm_edson-d4p0) ──────
_status="ok"; _rc=""; _sum=""
if grep -q "nlm nao autenticado" "$LOG" 2>/dev/null; then
  _status="auth_expired"
elif [ "${rc:-1}" -ne 0 ]; then
  _status="failed"; _rc="${rc:-1}"
  _sum="$(grep -E 'ERRO|FALHOU' "$LOG" | tail -2 | tr '\n' ' ' | cut -c1-200)"
fi
python3 "$REPO/scripts/tg_notify.py" report-state \
  --slug "$OBRA_SLUG" --project "$OBRA_TITULO" --path "$PROJECT_PATH" \
  --profile "$PROFILE" --status "$_status" \
  --rc "$_rc" --summary "$_sum" \
  --run-cmd "python3 $RUNNER --project $PROJECT --profile $PROFILE --all" \
  >/dev/null 2>&1 || true

exit "${rc:-1}"
