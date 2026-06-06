#!/usr/bin/env python3
"""
Fase 4a — Monta o ARQUIVO-FONTE unico do NotebookLM (a obra inteira, bem delimitada).

NotebookLM identifica a cena pelo --focus (prompt) + ancoras; este arquivo da o contexto e
marca CAPITULOS e INICIO/FIM de cada CENA, reduzindo a 'mistura de cenas'. Para mega-livros,
rodar com --part-files (1 arquivo por parte/volume) — aqui o default e 1 arquivo unico.

Casamento de ancora: regex com \\s+ entre tokens (tolerante a quebras de linha/espacos).
Ancoras nao encontradas sao REPORTADAS (para correcao manual em _anchors.json).

Uso:
    python3 04_build_nlm_source.py --project projetos/literatura/<slug> [--dry-run]
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata
from pathlib import Path


def anchor_regex(anchor: str):
    # escapa e troca runs de espaco por \s+ (tolera quebras de linha); normaliza travessao
    parts = [re.escape(tok) for tok in anchor.split()]
    pat = r"\s+".join(parts)
    return re.compile(pat)


def find_span(text: str, anchor: str):
    m = anchor_regex(anchor).search(text)
    return (m.start(), m.end()) if m else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Fase 4a: monta o arquivo-fonte unico do NotebookLM")
    ap.add_argument("--project", required=True)
    ap.add_argument("--manifest", default="_cenas_manifest.json")
    ap.add_argument("--anchors", default="_anchors.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.project).expanduser()
    man = json.loads((proj / args.manifest).read_text(encoding="utf-8"))
    anchors = json.loads((proj / args.anchors).read_text(encoding="utf-8"))
    cap_dir = next((d for d in proj.glob("*-capitulos") if d.is_dir()), None)
    idx = json.loads((cap_dir / "_capitulos_index.json").read_text(encoding="utf-8"))
    width = man.get("width", 2)

    cenas_by_chapter = {}
    for c in man["cenas"]:
        cenas_by_chapter.setdefault(c["source_chapter"], []).append(c)

    out = [f"# {man['obra']}", f"_{man['autor']}_", "",
           "> Fonte para NotebookLM. Marcadores `<<< CENA n — INICIO/FIM >>>` delimitam as cenas "
           "da leitura formativa. O prompt de cada cena usa as mesmas ancoras.", ""]
    unmatched = []

    for ch in idx["capitulos"]:
        fname = ch["arquivo"]
        text = (cap_dir / fname).read_text(encoding="utf-8")
        # remove a linha-numero inicial isolada (artefato Docling), se houver
        text = re.sub(r"^\s*\d+\s*\n", "", text, count=1)

        inserts = []  # (pos, marker_text)
        for c in sorted(cenas_by_chapter.get(fname, []), key=lambda x: x["cena_local"]):
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
        # aplica de tras p/ frente para nao deslocar offsets
        for pos, marker in sorted(inserts, key=lambda t: t[0], reverse=True):
            text = text[:pos] + marker + text[pos:]

        out += [f"## Capítulo {ch['cap_label']}", "", text.strip(), ""]

    source = "\n".join(out) + "\n"
    out_path = proj / f"{man['slug']}_fonte_nlm.md"

    print(f"\n  {man['obra']}: arquivo-fonte com {len(idx['capitulos'])} capitulos, {len(man['cenas'])} cenas")
    print(f"  Marcadores inseridos: {2*len(man['cenas']) - len(unmatched)}/{2*len(man['cenas'])}")
    if unmatched:
        print(f"  AVISO — ancoras nao encontradas (corrigir em _anchors.json): {', '.join(unmatched)}")
    else:
        print("  Todas as ancoras casaram.")
    if args.dry_run:
        print("  [dry-run] nada escrito.\n"); return 0
    out_path.write_text(source, encoding="utf-8")
    kb = len(source.encode("utf-8")) / 1024
    print(f"  Escrito: {out_path} ({kb:.0f} KB)\n")
    return 0 if not unmatched else 2


if __name__ == "__main__":
    sys.exit(main())
