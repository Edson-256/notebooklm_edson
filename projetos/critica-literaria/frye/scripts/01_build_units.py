#!/usr/bin/env python3
"""Fase 1 (não-ficção) — classifica capítulos do Docling em UNIDADES de áudio.

Diferente da leitura-formativa (ficção): NÃO divide capítulo por tempo de leitura
(o NotebookLM gera um deep-dive ~10-40min DISCUTINDO o capítulo, não o lê inteiro).
Aqui só: (1) lê output/chapters/, (2) pula front/back matter, (3) emite o manifesto
de unidades = camada-livro + 1 unidade por capítulo substantivo, cada uma com a
lista de formatos a gerar (default do config + overrides).

Uso:  python3 01_build_units.py <pasta-do-projeto> [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

CHAP_RE = re.compile(r"^C(\d+)-(.+)\.md$", re.IGNORECASE)

# Front/back matter (PT + EN). Prefácio/intro/prólogo/epílogo NÃO entram (são relevantes).
SKIP_KEYWORDS = [
    "nota", "notas", "credito", "creditos", "sumario", "indice", "copyright",
    "ficha", "agradecimento", "apendice", "glossario", "posfacio", "colofao", "isbn",
    "cover", "title page", "title-page", "contents", "index", "notes",
    "bibliography", "acknowledg", "frontmatter", "front matter", "appendix",
]


def strip_lower(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower().strip()


def is_skippable(label: str) -> bool:
    lab = strip_lower(label)
    return any(k in lab for k in SKIP_KEYWORDS)


def parse_cap_and_title(label: str) -> tuple[str, str]:
    """'1-The-Case-Against-Locke' -> ('1', 'The Case Against Locke')."""
    parts = label.split("-")
    if parts and parts[0].isdigit():
        cap, rest = parts[0], parts[1:]
    else:
        cap, rest = "", parts
    title = " ".join(rest).strip()
    return cap, title


def word_count(p: Path) -> int:
    return len(p.read_text(encoding="utf-8").split())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto", help="pasta do projeto (contém config.toml)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.projeto).expanduser().resolve()
    cfg = tomllib.load(open(proj / "config.toml", "rb"))

    chapters_dir = proj / cfg["docling"]["chapters_dir"]
    if not chapters_dir.is_dir():
        print(f"ERRO: não achei {chapters_dir}", file=sys.stderr); return 1

    fmt = cfg["formatos"]
    default_stack = fmt["default_capitulo"]
    overrides = fmt.get("overrides", {})

    raw = []
    for p in sorted(chapters_dir.glob("*.md")):
        m = CHAP_RE.match(p.name)
        if not m:
            continue
        raw.append((int(m.group(1)), m.group(2), p))
    raw.sort(key=lambda t: t[0])

    incluidos, excluidos = [], []
    for cnum, label, path in raw:
        (excluidos if is_skippable(label) else incluidos).append((cnum, label, path))

    width = max(2, len(str(len(incluidos))))
    capitulos = []
    for seq, (cnum, label, path) in enumerate(incluidos, 1):
        cap, title = parse_cap_and_title(label)
        cap = cap or str(cnum)
        capitulos.append({
            "seq": seq,
            "cap": cap,
            "titulo": title,
            "source_chapter": path.name,
            "palavras": word_count(path),
            "formatos": overrides.get(cap, default_stack),
        })

    manifest = {
        "obra": cfg["obra"]["titulo"],
        "autor": cfg["obra"]["autor"],
        "slug": cfg["obra"]["slug"],
        "idioma_obra": cfg["obra"]["idioma_obra"],
        "idioma_saida": cfg["obra"]["idioma_saida"],
        "modelo_dominante": cfg["obra"].get("modelo_dominante", ""),
        "width": width,
        "camada_livro": fmt["camada_livro"],
        "capitulos": capitulos,
        "excluidos": [f"C{c:03d}-{l}" for c, l, _ in excluidos],
    }

    # relatório
    print(f"\n  Obra: {manifest['obra']}")
    print(f"  Capítulos: {len(raw)} | substantivos: {len(incluidos)} | front/back: {len(excluidos)}")
    print(f"  Camada-livro: {', '.join(manifest['camada_livro'])}")
    print(f"  Stack padrão/capítulo: {', '.join(default_stack)}\n")
    for c in capitulos:
        ov = "  (override)" if c["cap"] in overrides else ""
        print(f"    {c['seq']:>2}. cap {c['cap']:>2} — {c['titulo'][:42]:<42} {c['palavras']:>6}w  [{'·'.join(c['formatos'])}]{ov}")
    if excluidos:
        print(f"\n  Excluídos (front/back): {', '.join(manifest['excluidos'])}")
    n_audios = len(manifest["camada_livro"]) + sum(len(c["formatos"]) for c in capitulos)
    print(f"\n  Total de áudios previstos: {n_audios} "
          f"({len(manifest['camada_livro'])} camada-livro + {sum(len(c['formatos']) for c in capitulos)} por-capítulo)")

    if args.dry_run:
        print("\n  [dry-run] manifesto não escrito.\n"); return 0

    out = proj / cfg["paths"]["unidades"]
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Escrito: {out}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
