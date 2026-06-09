#!/usr/bin/env python3
"""Fase 4 (não-ficção) — monta a FONTE única do NotebookLM a partir dos capítulos.

O integral do Docling (--single) é plano (sem headings), o que dificulta o NLM
localizar "o capítulo X". Aqui concatenamos os arquivos de capítulo substantivos
(na ordem do manifesto) com HEADINGS + marcadores de capítulo, dando ao NLM uma
fonte navegável que casa com as âncoras dos prompts.

Saída: <projeto>/output/<slug>_fonte_nlm.md  (1 arquivo = upload no notebook)

Uso:  python3 04_build_nlm_source.py <projeto> [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sys
import tomllib
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.projeto).expanduser().resolve()
    cfg = tomllib.load(open(proj / "config.toml", "rb"))
    man = json.loads((proj / cfg["paths"]["unidades"]).read_text(encoding="utf-8"))
    chapters_dir = proj / cfg["docling"]["chapters_dir"]

    parts = [f"# {man['obra']}", f"_{man['autor']}_", ""]
    for c in man["capitulos"]:
        text = (chapters_dir / c["source_chapter"]).read_text(encoding="utf-8").strip()
        parts.append(f"\n<<< CAPÍTULO {c['cap']}: {c['titulo']} — INÍCIO >>>\n")
        parts.append(f"## Capítulo {c['cap']} — {c['titulo']}\n")
        parts.append(text)
        parts.append(f"\n<<< CAPÍTULO {c['cap']} — FIM >>>\n")

    source = "\n".join(parts) + "\n"
    words = len(source.split())
    out = proj / "output" / f"{man['slug']}_fonte_nlm.md"

    print(f"\n  Fonte NLM: {len(man['capitulos'])} capítulos | ~{words:,} palavras")
    print(f"  Destino: {out}")
    if args.dry_run:
        print("  [dry-run] não escrito.\n"); return 0
    out.write_text(source, encoding="utf-8")
    print(f"  Escrito ({out.stat().st_size/1e6:.2f} MB)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
