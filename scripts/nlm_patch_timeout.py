#!/usr/bin/env python3
"""Reaplica o patch de timeout do CLI `nlm` (30s -> 120s), idempotente.

Por que existe
--------------
`nlm studio status` num notebook com muitos artifacts (Aristóteles: 815 em 2026-09-16)
demora mais de 30 segundos. O httpx.Client do pacote nasce com `timeout=30.0`, e quando
estoura o CLI devolve uma mensagem que PARECE erro do Google:

    {"status": "error", "error": "Could not retrieve studio status."}

É timeout do lado de cá, não recusa do servidor — o sintoma engana (foi diagnosticado
como "limite de volume do NotebookLM" em 2026-08-03). O sinal que separa os dois casos:
o comando falha em ~30,0 s cravados.

Consequência prática: o `--harvest` do 07_audio_runner.py falha em TODA rodada que cria
lote, o cron sai com rc=1 e o backlog de `created` (áudio pronto, não baixado) cresce sem
que nada mais quebre. Foi o que aconteceu em 13, 14 e 15/09/2026.

**Toda atualização do `nlm` apaga este patch** (o arquivo é reescrito). Por isso o
cron_audio.sh chama este script antes de rodar: é barato e evita o modo de falha.

Uso:
    python3 scripts/nlm_patch_timeout.py          # aplica se faltar; 0 = ok
    python3 scripts/nlm_patch_timeout.py --check  # só verifica; 1 = patch ausente
"""
import argparse
import re
import sys
from pathlib import Path

BASE = (Path.home() / ".local/share/uv/tools/notebooklm-mcp-cli/lib/python3.14"
        "/site-packages/notebooklm_tools/core/base.py")
MARCA = "PATCH LOCAL"
NOVO_DEFAULT = ("DEFAULT_TIMEOUT = 120.0  # PATCH LOCAL (nlm_patch_timeout.py): era 30.0 — "
                "studio status com muitos artifacts estoura")


def aplicar(texto: str) -> tuple[str, int]:
    mudancas = 0
    texto, n = re.subn(r"DEFAULT_TIMEOUT = 30\.0[^\n]*", NOVO_DEFAULT, texto)
    mudancas += n
    # os dois clients (sync e async) nascem com o literal 30.0
    texto, n = re.subn(r"(\n\s+)timeout=30\.0,",
                       r"\1timeout=DEFAULT_TIMEOUT,  # PATCH LOCAL (era 30.0)", texto)
    mudancas += n
    return texto, mudancas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="só verifica, não escreve")
    args = ap.parse_args()

    if not BASE.exists():
        print(f"ERRO: não achei {BASE} — o nlm mudou de lugar?", file=sys.stderr)
        return 2
    texto = BASE.read_text()
    if MARCA in texto:
        print("patch presente")
        return 0
    if args.check:
        print("patch AUSENTE (o nlm foi reinstalado/atualizado)")
        return 1
    novo, mudancas = aplicar(texto)
    if mudancas == 0:
        print("ERRO: nada para substituir — o código do nlm mudou; revisar à mão",
              file=sys.stderr)
        return 2
    BASE.with_suffix(".py.orig").write_text(texto)
    BASE.write_text(novo)
    print(f"patch aplicado ({mudancas} substituições); cópia do original em {BASE.name}.orig")
    return 0


if __name__ == "__main__":
    sys.exit(main())
