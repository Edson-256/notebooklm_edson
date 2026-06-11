#!/bin/bash
# nlm_quota_guard.sh — quota guard compartilhado para conta NLM 'default'.
#
# O NotebookLM tem cota de ~20 Audio Overviews por rolling 24h.
# Aristóteles (dias ímpares) e COF (dias pares) compartilham essa cota.
# Este guard garante >= 25h entre lotes da mesma conta.
#
# Uso (source nos cron wrappers):
#   source "$REPO_DIR/scripts/nlm_quota_guard.sh"
#   nlm_quota_check >> "$LOG" || exit 0   # sai se em cooldown
#   nlm_quota_mark                        # chama ANTES de disparar criações
#
# Estado gravado em: $REPO_DIR/.nlm_quota_default_ts (Unix timestamp)

_NLM_QUOTA_FILE="/Users/edsonmichalkiewicz/dev/notebooklm_edson/.nlm_quota_default_ts"
_NLM_QUOTA_COOLDOWN=90000  # 25h em segundos (1h de buffer acima do limite rolling 24h da API)

nlm_quota_check() {
  # Retorna 0 se pode rodar, 1 se ainda em cooldown.
  # Imprime mensagem no stdout em ambos os casos (redirecionar p/ LOG).
  if [ ! -f "$_NLM_QUOTA_FILE" ]; then
    printf '%s — quota guard: nenhum lote anterior registrado, pode rodar.\n' \
      "$(date '+%Y-%m-%d %H:%M')"
    return 0
  fi
  local last; last=$(cat "$_NLM_QUOTA_FILE" 2>/dev/null || echo 0)
  local now; now=$(date +%s)
  local elapsed=$(( now - last ))
  if [ "$elapsed" -lt "$_NLM_QUOTA_COOLDOWN" ]; then
    local remaining=$(( _NLM_QUOTA_COOLDOWN - elapsed ))
    printf '%s — quota guard: %dh%02dm decorridas, %dh%02dm restantes — aguardando.\n' \
      "$(date '+%Y-%m-%d %H:%M')" \
      "$(( elapsed / 3600 ))" "$(( (elapsed % 3600) / 60 ))" \
      "$(( remaining / 3600 ))" "$(( (remaining % 3600) / 60 ))"
    return 1
  fi
  printf '%s — quota guard: %dh%02dm decorridas — janela aberta.\n' \
    "$(date '+%Y-%m-%d %H:%M')" \
    "$(( elapsed / 3600 ))" "$(( (elapsed % 3600) / 60 ))"
  return 0
}

nlm_quota_mark() {
  # Chama ANTES de disparar criações — registra início do lote.
  printf '%s\n' "$(date +%s)" > "$_NLM_QUOTA_FILE"
  printf '%s — quota guard: lote iniciado, próxima janela em 25h.\n' \
    "$(date '+%Y-%m-%d %H:%M')"
}
