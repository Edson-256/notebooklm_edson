#!/bin/bash
# git_state_commit.sh — auto-commit + push de UM metadata.json de estado.
#
# Chamado pelos cron_*.sh ao fim da rodada para versionar o progresso de
# download (status created->downloaded) que o runner grava no metadata.json.
# Sem isso, as mudanças de estado acumulam como working-tree sujo e bloqueiam
# `git pull --rebase` (ver notebooklm_edson-xdp).
#
# Uso:  git_state_commit.sh <caminho-relativo-ao-repo> <label>
# Ex.:  git_state_commit.sh "projetos/filosofia/cof_v2/audios/metadata.json" "cof"
#
# Best-effort: NUNCA derruba o cron (todos os passos com || true / exit 0).
# credential.helper=store (~/.git-credentials) => push funciona em cron headless.
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FILE="${1:-}"
LABEL="${2:-estado}"

[ -z "$FILE" ] && exit 0
cd "$REPO_ROOT" || exit 0

# Arquivo precisa ser rastreado (gitignored => ignora silenciosamente).
git ls-files --error-unmatch -- "$FILE" >/dev/null 2>&1 || exit 0

# Nada mudou (nem working-tree nem index)? Sai.
if git diff --quiet -- "$FILE" && git diff --cached --quiet -- "$FILE"; then
  exit 0
fi

# Commita SÓ este arquivo (pathspec) — não arrasta outras mudanças soltas.
git commit -m "chore(state): ${LABEL} download progress [cron]" -- "$FILE" >/dev/null 2>&1 || exit 0

# --autostash: metadata.json sujo de OUTROS projetos não bloqueia o rebase.
git pull --rebase --autostash >/dev/null 2>&1 || true
git push >/dev/null 2>&1 || true
exit 0
