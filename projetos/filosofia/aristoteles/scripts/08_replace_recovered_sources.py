#!/usr/bin/env python3
"""
Substitui, no notebook 'Aristóteles (completo)', as 4 sources cujas fontes foram
recuperadas em 2026-08-21 (ver docs/FONTES_INCOMPLETAS_recuperar.md).

Ordem por obra, deliberadamente conservadora:
  1. sobe a nova source com um título provisório ('NNb. ...')
  2. confere que ela existe na listagem do notebook
  3. só então apaga a antiga
  4. renomeia a nova para o título canônico ('NN. ...')
  5. atualiza _raw/notebook_aristoteles.json

Se qualquer passo falhar, a obra é pulada e o estado anterior permanece —
nunca fica um buraco (obra sem nenhuma source) no notebook.

Uso:
  python3 scripts/08_replace_recovered_sources.py --dry-run
  python3 scripts/08_replace_recovered_sources.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_META = PROJECT_ROOT / "_raw" / "notebook_aristoteles.json"
PROFILE = "default"

# (obra_idx, caminho clean, titulo_en, translator)
JOBS = [
    (23, "obras/03_psicologia_biologia/07_geracao_animais/clean/on_the_generation_of_animals.txt",
     "On the Generation of Animals", "Platt (Oxford)"),
    (26, "obras/05_etica/02_etica_eudemo/clean/eudemian_ethics.txt",
     "Eudemian Ethics", "Solomon (Oxford)"),
    (27, "obras/05_etica/03_magna_moralia/clean/magna_moralia.txt",
     "Magna Moralia", "Stock (Oxford)"),
    (29, "obras/06_politica/01_politica/clean/politics.txt",
     "Politics", "Jowett"),
]


def nlm(args: list[str], timeout: int = 400) -> subprocess.CompletedProcess:
    return subprocess.run(["nlm", *args, "--profile", PROFILE],
                          capture_output=True, text=True, timeout=timeout)


def list_sources(nb: str) -> list[dict]:
    r = nlm(["source", "list", nb, "--json"], timeout=120)
    if r.returncode != 0:
        raise RuntimeError(f"source list falhou: {r.stderr[:300]}")
    return json.loads(r.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    meta = json.loads(NOTEBOOK_META.read_text(encoding="utf-8"))
    nb = meta["notebook_id"]
    before = list_sources(nb)
    by_idx = {}
    for s in before:
        t = s.get("title", "")
        if t[:2].isdigit() and t[2:3] == ".":
            by_idx[int(t[:2])] = s
    print(f"Notebook {nb} — {len(before)} sources hoje\n")

    for idx, rel, titulo_en, translator in JOBS:
        path = PROJECT_ROOT / rel
        antigo = by_idx.get(idx)
        canonico = f"{idx:02d}. {titulo_en} (Aristotle, tr. {translator})"
        provisorio = f"{idx:02d}b. {titulo_en} (Aristotle, tr. {translator})"
        print(f"=== {idx:02d} {titulo_en}  ({path.stat().st_size/1024:.0f} KB)")
        print(f"    antiga: {antigo['title'] if antigo else '(nenhuma)'}")
        print(f"    nova  : {canonico}")
        if args.dry_run:
            continue

        r = nlm(["source", "add", nb, "--file", str(path), "--title", provisorio,
                 "--wait", "--wait-timeout", "300", "--json"], timeout=420)
        if r.returncode != 0:
            print(f"    ✗ upload falhou — obra PULADA, nada removido: {r.stderr[:200]}")
            continue

        time.sleep(3)
        agora = list_sources(nb)
        nova = next((s for s in agora if s.get("title") == provisorio), None)
        if not nova:
            print("    ✗ source nova não apareceu na listagem — obra PULADA, nada removido")
            continue
        print(f"    ✓ subiu: {nova['id']}")

        if antigo:
            rd = nlm(["source", "delete", antigo["id"], "--confirm"], timeout=120)
            print(f"    {'✓' if rd.returncode == 0 else '✗'} antiga removida ({antigo['id']})")

        rr = nlm(["source", "rename", nova["id"], canonico, "--notebook", nb], timeout=120)
        print(f"    {'✓' if rr.returncode == 0 else '✗'} renomeada para o título canônico")

        for s in meta["sources"]:
            if s.get("title", "").startswith(f"{idx:02d}."):
                s["title"] = canonico
                s["source_id"] = nova["id"]
                s["file"] = rel
                s["replaced_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                break
        meta["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        NOTEBOOK_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                 encoding="utf-8")
        print("    ✓ manifest local atualizado")

    depois = list_sources(nb)
    print(f"\nSources no notebook ao final: {len(depois)} (eram {len(before)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
