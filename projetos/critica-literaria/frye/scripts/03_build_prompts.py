#!/usr/bin/env python3
"""Fase 3 (não-ficção) — gera N prompts por unidade (1 por formato).

Lê _unidades_manifest.json + config.toml + templates/. Para cada capítulo e cada
formato do seu stack, preenche o template correspondente (com âncoras início/fim
do capítulo) e escreve prompts/prompt_<seq>_cap-<cap>_<formato>.md.

Templates ausentes são PULADOS com aviso (permite construir o leque aos poucos).

Uso:
  python3 03_build_prompts.py <projeto> [--only-cap N] [--only-formato K] [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import tomllib
import unicodedata
from pathlib import Path

# formato (manifesto) -> arquivo de template
TEMPLATE_FILE = {
    "portico": "fmt_portico.md",
    "reconstrucao": "fmt_reconstrucao.md",
    "arena": "fmt_arena.md",
    "filtro": "fmt_filtro.md",
    "meditatio": "fmt_meditatio.md",
    "lexico": "fmt_lexico.md",
    # camada-livro
    "portico_geral": "livro_portico_geral.md",
    "lexico_geral": "livro_lexico.md",
    "filtro_tese": "livro_filtro_tese.md",
}
BOOK_LEVEL = {"portico_geral", "lexico_geral", "filtro_tese"}


def clean_text(t: str) -> str:
    # remove imagens, headings e LINHAS DE TABELA markdown (o Docling põe o
    # título do capítulo numa tabela no topo), depois junta em texto corrido.
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)
    kept = []
    for line in t.splitlines():
        s = line.strip()
        if not s:
            continue
        # linha de tabela (| a | b |) ou separador (|---|---|)
        if s.startswith("|") or set(s) <= set("|-: "):
            continue
        s = re.sub(r"^#+\s*", "", s)          # heading
        s = re.sub(r"[*_`]+", "", s)          # ênfase markdown
        kept.append(s)
    return re.sub(r"\s+", " ", " ".join(kept)).strip()


def anchors(chapter_path: Path, max_len: int = 160) -> tuple[str, str]:
    txt = clean_text(chapter_path.read_text(encoding="utf-8"))
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", txt) if len(s.split()) >= 5]
    if not sents:
        return ("", "")
    ini = sents[0][:max_len]
    fim = sents[-1][:max_len]
    return (ini, fim)


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"-{2,}", "-", re.sub(r"[^\w\-]", "", re.sub(r"[\s/]+", "-", s.lower()))).strip("-")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("projeto")
    ap.add_argument("--only-cap", default=None)
    ap.add_argument("--only-formato", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.projeto).expanduser().resolve()
    cfg = tomllib.load(open(proj / "config.toml", "rb"))
    man = json.loads((proj / cfg["paths"]["unidades"]).read_text(encoding="utf-8"))
    tdir = Path(__file__).resolve().parent / "templates"
    chapters_dir = proj / cfg["docling"]["chapters_dir"]
    width = man["width"]

    def load_template(fmt: str) -> str | None:
        fname = TEMPLATE_FILE.get(fmt)
        if not fname:
            return None
        p = tdir / fname
        return p.read_text(encoding="utf-8") if p.exists() else None

    out_dir = proj / cfg["paths"]["prompts"]
    written, skipped = [], []

    total_audios = len(man["camada_livro"]) + sum(len(c["formatos"]) for c in man["capitulos"])

    # camada-livro (sem capítulo/âncoras) — pula se --only-cap
    if not args.only_cap:
        for fmt in man["camada_livro"]:
            if args.only_formato and fmt != args.only_formato:
                continue
            tpl = load_template(fmt)
            if tpl is None:
                skipped.append(f"livro/{fmt}")
                continue
            prompt = tpl.format(
                obra=man["obra"], autor=man["autor"],
                modelo_dominante=man["modelo_dominante"],
                cap="", titulo="", seq=0, total=total_audios,
                ancora_inicio="", ancora_fim="",
            )
            fname = f"prompt_L0_{fmt}.md"
            if args.dry_run:
                print(f"\n{'='*78}\n{fname}\n{'='*78}\n{prompt}")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / fname).write_text(prompt, encoding="utf-8")
            written.append(fname)

    for c in man["capitulos"]:
        if args.only_cap and str(c["cap"]) != str(args.only_cap):
            continue
        ini, fim = anchors(chapters_dir / c["source_chapter"])
        for fmt in c["formatos"]:
            if args.only_formato and fmt != args.only_formato:
                continue
            tpl = load_template(fmt)
            if tpl is None:
                skipped.append(f"cap{c['cap']}/{fmt}")
                continue
            prompt = tpl.format(
                obra=man["obra"], autor=man["autor"],
                modelo_dominante=man["modelo_dominante"],
                cap=c["cap"], titulo=c["titulo"], seq=c["seq"],
                total=total_audios, ancora_inicio=ini, ancora_fim=fim,
            )
            fname = f"prompt_{c['seq']:0{width}d}_cap-{c['cap']}_{fmt}.md"
            if args.dry_run:
                print(f"\n{'='*78}\n{fname}\n{'='*78}\n{prompt}")
            else:
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / fname).write_text(prompt, encoding="utf-8")
            written.append(fname)

    print(f"\n  Gerados: {len(written)} | pulados (sem template): {len(skipped)}")
    if skipped:
        print(f"  Faltam templates p/: {', '.join(sorted(set(s.split('/')[1] for s in skipped)))}")
    if not args.dry_run and written:
        print(f"  Em: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
