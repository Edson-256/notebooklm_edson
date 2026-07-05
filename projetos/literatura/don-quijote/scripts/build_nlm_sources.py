#!/usr/bin/env python3
"""
Fase 4 (custom) — Monta os DOIS arquivos-fonte do NotebookLM (1 por Parte: 1605 e 1615).

Substitui 04_build_nlm_source.py (generico) porque este assume 1 unica pasta de capitulos e
produz 1 unico arquivo de saida (`next(glob("*-capitulos"))`, sem filtro por subconjunto). Aqui
rodamos o MESMO algoritmo de casamento de ancora duas vezes, filtrando o manifesto e o indice de
capitulos por 'parte' (P1/P2), produzindo:
  don-quijote_p1_fonte_nlm.md
  don-quijote_p2_fonte_nlm.md
Ambos sobem no MESMO notebook (um notebook aceita varias fontes) — padrao da skill para
mega-livros ("1 fonte por parte/volume").

Casamento de ancora: regex com \\s+ entre tokens (tolerante a quebras de linha/espacos). Ancoras
nao encontradas sao REPORTADAS (para correcao manual em _anchors.json).

Roda DEPOIS que existirem cenas com ancoras (Fase 2/3); nao ha nada para processar antes disso.

Uso:
    python3 build_nlm_sources.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
CAP_DIR = PROJ / "DQ-capitulos"
MANIFEST = PROJ / "_cenas_manifest.json"
ANCHORS = PROJ / "_anchors.json"

PARTE_TITULO = {"P1": "Primera Parte (1605)", "P2": "Segunda Parte (1615)"}


def anchor_regex(anchor: str):
    parts = [re.escape(tok) for tok in anchor.split()]
    pat = r"\s+".join(parts)
    return re.compile(pat)


def find_span(text: str, anchor: str):
    m = anchor_regex(anchor).search(text)
    return (m.start(), m.end()) if m else None


def build_source_for_parte(parte: str, man: dict, idx: dict, anchors: dict, width: int):
    cenas_by_chapter = {}
    for c in man["cenas"]:
        cenas_by_chapter.setdefault(c["source_chapter"], []).append(c)

    capitulos_parte = [ch for ch in idx["capitulos"] if ch["parte"] == parte]

    out = [f"# Don Quijote de la Mancha — {PARTE_TITULO[parte]}", "_Miguel de Cervantes Saavedra_", "",
           "> Fonte para NotebookLM. Marcadores `<<< CENA n — INICIO/FIM >>>` delimitam as cenas "
           "da leitura formativa. O prompt de cada cena usa as mesmas ancoras.", ""]
    unmatched = []
    n_cenas_parte = 0

    for ch in capitulos_parte:
        fname = ch["arquivo"]
        text = (CAP_DIR / fname).read_text(encoding="utf-8")

        inserts = []
        for c in sorted(cenas_by_chapter.get(fname, []), key=lambda x: x["cena_local"]):
            n_cenas_parte += 1
            a = anchors.get(str(c["seq_global"]), {})
            si = find_span(text, a.get("inicio", "")) if a.get("inicio") else None
            sf = find_span(text, a.get("fim", "")) if a.get("fim") else None
            if si:
                inserts.append((si[0], f"\n<<< CENA {c['seq_global']:0{width}d}: {c['titulo']} — INICIO >>>\n"))
            else:
                unmatched.append(f"cena {c['seq_global']} inicio")
            if sf:
                inserts.append((sf[1], f"\n<<< CENA {c['seq_global']:0{width}d} — FIM >>>\n"))
            else:
                unmatched.append(f"cena {c['seq_global']} fim")
        for pos, marker in sorted(inserts, key=lambda t: t[0], reverse=True):
            text = text[:pos] + marker + text[pos:]

        cap_label = "Prólogo" if ch["cap_natural"] == "Prólogo" else f"Capítulo {ch['cap_natural']}"
        out += [f"## {cap_label}", "", text.strip(), ""]

    source = "\n".join(out) + "\n"
    return source, len(capitulos_parte), n_cenas_parte, unmatched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.is_file():
        print(f"AVISO: {MANIFEST} nao existe ainda (autoria de cenas nao comecou) — nada a fazer.")
        return 0
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not man.get("cenas"):
        print("AVISO: manifesto existe mas 'cenas' esta vazio (autoria ainda nao rodou) — nada a fazer.")
        return 0
    idx = json.loads((CAP_DIR / "_capitulos_index.json").read_text(encoding="utf-8"))
    anchors = json.loads(ANCHORS.read_text(encoding="utf-8")) if ANCHORS.is_file() else {}
    width = man.get("width", 3)

    total_unmatched = []
    for parte in ("P1", "P2"):
        source, n_caps, n_cenas, unmatched = build_source_for_parte(parte, man, idx, anchors, width)
        out_path = PROJ / f"{man['slug']}_{parte.lower()}_fonte_nlm.md"
        print(f"\n  {PARTE_TITULO[parte]}: {n_caps} capitulos, {n_cenas} cenas")
        print(f"  Marcadores inseridos: {2*n_cenas - len(unmatched)}/{2*n_cenas}")
        if unmatched:
            print(f"  AVISO — ancoras nao encontradas (corrigir em _anchors.json): {', '.join(unmatched)}")
            total_unmatched += unmatched
        if args.dry_run:
            print(f"  [dry-run] {out_path} nao escrito.")
        else:
            out_path.write_text(source, encoding="utf-8")
            kb = len(source.encode("utf-8")) / 1024
            print(f"  Escrito: {out_path} ({kb:.0f} KB)")

    return 0 if not total_unmatched else 2


if __name__ == "__main__":
    sys.exit(main())
