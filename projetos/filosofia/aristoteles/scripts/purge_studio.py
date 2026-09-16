#!/usr/bin/env python3
"""Apaga do NotebookLM Studio só os artifacts cujo áudio está BAIXADO e no BACKUP.

Por que existe
--------------
O studio deste notebook acumula um artifact por cena (815 em 2026-09-16). Acima de umas
poucas centenas, `nlm studio status` fica lento e passa a estourar o timeout do CLI — o
que derruba o `--harvest` do cron (ver notebooklm_edson-gqq8 e a limpeza de 2026-08-03).

Regra de segurança: um artifact só é apagado se a cena estiver `downloaded` no
`_raw/audio_metadata.json` E o arquivo existir **no dell E no DROBO**. Cena ainda
`created` (áudio pronto, não baixado) nunca é tocada.

Uso:
    python3 scripts/purge_studio.py              # dry-run: só relata
    python3 scripts/purge_studio.py --apply      # apaga de verdade
    python3 scripts/purge_studio.py --apply --incluir-falhos   # inclui artifacts 'failed' órfãos
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
import sys
import unicodedata
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
NOTEBOOK = json.loads((PROJ / "_raw/notebook_aristoteles.json").read_text())["notebook_id"]
META = PROJ / "_raw/audio_metadata.json"
PROFILE = "default"
DELL = ("dell-server", "/srv/podcasts/aristoteles")
DROBO = Path("/Volumes/Public/dell_backup/podcasts/aristoteles")
LOTE = 50


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def nlm(args: list[str], timeout: int = 200) -> subprocess.CompletedProcess:
    env = dict(os.environ, NLM_PROFILE=PROFILE)
    return subprocess.run(["nlm", *args], capture_output=True, text=True, env=env, timeout=timeout)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--incluir-falhos", action="store_true",
                    help="apaga também artifacts com status 'failed' que nenhuma cena reivindica")
    args = ap.parse_args()

    meta = json.loads(META.read_text())
    audios = meta["audios"]

    r = nlm(["studio", "status", NOTEBOOK, "--json"])
    if r.returncode != 0:
        print("ERRO: studio status falhou — o patch de timeout está aplicado? "
              "(python3 scripts/nlm_patch_timeout.py --check)", file=sys.stderr)
        print((r.stderr or r.stdout)[:300], file=sys.stderr)
        return 1
    studio = json.loads(r.stdout)
    por_id = {a["id"]: a for a in studio}

    if not DROBO.is_dir():
        print(f"ERRO: DROBO não montado ({DROBO})", file=sys.stderr)
        return 1
    no_drobo = {nfc(p.name) for p in DROBO.iterdir()}
    d = subprocess.run(["ssh", "-o", "ConnectTimeout=20", DELL[0], f"ls -1 {DELL[1]}"],
                       capture_output=True, text=True, timeout=120)
    if d.returncode != 0:
        print(f"ERRO: não consegui listar o dell: {d.stderr[:200]}", file=sys.stderr)
        return 1
    no_dell = {nfc(x) for x in d.stdout.split("\n") if x.strip()}

    apagar, manter = [], {"nao_baixada": 0, "sem_backup": [], "fora_do_studio": 0}
    reivindicados = set()
    for cena, info in audios.items():
        aid = info.get("artifact_id")
        if not aid:
            continue
        reivindicados.add(aid)
        if aid not in por_id:
            manter["fora_do_studio"] += 1
            continue
        if info.get("status") != "downloaded":
            manter["nao_baixada"] += 1
            continue
        nome = nfc(info.get("audio_filename") or "")
        if nome in no_dell and nome in no_drobo:
            apagar.append((aid, cena))
        else:
            onde = ("dell" if nome in no_dell else "") + (" DROBO" if nome in no_drobo else "")
            manter["sem_backup"].append((cena, onde.strip() or "nenhum"))

    falhos = [a["id"] for a in studio
              if a.get("status") == "failed" and a["id"] not in reivindicados]

    print(f"studio: {len(studio)} artifacts | dell: {len(no_dell)} | DROBO: {len(no_drobo)}")
    print(f"A APAGAR (baixado + dell + DROBO): {len(apagar)}")
    print(f"MANTER: {manter['nao_baixada']} cenas ainda não baixadas, "
          f"{len(manter['sem_backup'])} sem backup completo, "
          f"{manter['fora_do_studio']} já fora do studio")
    for cena, onde in manter["sem_backup"][:15]:
        print(f"   sem backup completo ({onde}): {cena}")
    if len(manter["sem_backup"]) > 15:
        print(f"   ... e mais {len(manter['sem_backup']) - 15}")
    print(f"artifacts 'failed' órfãos: {len(falhos)}"
          f"{' (serão apagados)' if args.incluir_falhos else ' (mantidos; use --incluir-falhos)'}")

    ids = [a for a, _ in apagar] + (falhos if args.incluir_falhos else [])
    if not args.apply:
        print("\nDRY-RUN — nada apagado. Rode com --apply para executar.")
        return 0
    if not ids:
        print("nada a apagar.")
        return 0

    # `nlm studio delete` aceita UM artifact por vez (0.11.4).
    apagados, erros = 0, []
    for n, aid in enumerate(ids, 1):
        r = nlm(["studio", "delete", NOTEBOOK, aid, "--confirm"], timeout=120)
        if r.returncode != 0:
            erros.append((aid, (r.stderr or r.stdout).strip()[:120]))
            if len(erros) >= 10:
                print("ERRO: 10 falhas seguidas/acumuladas — abortando", file=sys.stderr)
                break
        else:
            apagados += 1
        if n % 25 == 0:
            print(f"  {n}/{len(ids)} processados ({apagados} apagados, {len(erros)} erros)",
                  flush=True)
        time.sleep(0.5)
    print(f"\n{apagados} artifacts apagados, {len(erros)} erros; "
          "o áudio segue no dell e no DROBO.")
    for aid, msg in erros[:5]:
        print(f"  erro {aid}: {msg}")
    return 0 if not erros else 1


if __name__ == "__main__":
    sys.exit(main())
