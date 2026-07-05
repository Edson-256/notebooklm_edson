#!/usr/bin/env python3
"""
Fase 1 (custom) — Fragmentacao parte-aware de Don Quijote de la Mancha (P1 1605 + P2 1615).

Substitui 01_fragment_chapters.py (generico) porque:
  - a fonte usa nomenclatura P1-C0NN-*/P2-C0NN-* (nao CNNN-*, que e o que o script generico casa);
  - os 2 front-matters (P1-00-FrontMatter, P2-00-FrontMatter) carregam o PROLOGO de cada Parte —
    peso literario proprio (nao sao so tassa/licenca) — viram 1 unidade-PROLOGO cada, nao sao
    excluidos como back-matter comum;
  - precisa numeracao GLOBAL continua (cap 1..128) atravessando as duas Partes, para que os
    scripts genericos da skill (02_build_scene_files.py, 04_build_nlm_source.py) funcionem sem
    modificacao (eles fazem groupby/lookup so por 'cap', sem nocao de Parte).

Z-BackMatter.md (indice de capitulos + notas) e EXCLUIDO por completo — nao tem valor narrativo.

Limpeza: remove comentarios '<!-- image -->' (capitulares/ornamentos) e links de nota de rodape
inline '[[N]](#_ftnN)' (o back-matter com as notas fica fora do pipeline; o link apontaria para
uma ancora inexistente) + normaliza espaco solto antes de pontuacao remanescente.

Saida:
  DQ-capitulos/<cap>_cap-<cap>_<slug>.md   (128 unidades; split em _p1/_p2... se > hard-max-min)
  DQ-capitulos/_capitulos_index.json
  _cenas_manifest.json  (esqueleto: cenas=[], pronto para autoria na Fase 2)

Uso:
    python3 scripts/build_manifest.py [--dry-run] [--ppm 130] [--max-min 35] [--target-min 30]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
SRC_DIR = PROJ / "output" / "chapters"
OUT_DIR = PROJ / "DQ-capitulos"

FRONT_RE = re.compile(r"^P(\d)-00-FrontMatter\.md$", re.IGNORECASE)
CHAP_RE = re.compile(r"^P(\d)-C(\d+)-(.+)\.md$", re.IGNORECASE)
BACKMATTER = "Z-BackMatter.md"

FOOTNOTE_RE = re.compile(r"\s*\[\[\d+\]\]\(#_ftn\d+\)")
IMAGE_COMMENT_RE = re.compile(r"^\s*<!--\s*image\s*-->\s*\n?", re.MULTILINE)
LOOSE_PUNCT_RE = re.compile(r"[ \t]+([,.;:!?])")
# Glifos de area privada (ex.: U+E000): resquicio de capitulares/ornamentos de fonte customizada
# sem mapeamento Unicode, sobras do OCR do Docling — puro ruido cosmetico.
PRIVATE_USE_RE = re.compile(r"[-]")


def slugify(s: str, max_len: int = 60) -> str:
    s = unicodedata.normalize("NFKD", s.strip()).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^\w\-]", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if len(s) > max_len:
        s = s[:max_len].rsplit("-", 1)[0]
    return s


def word_count(text: str) -> int:
    return len(text.split())


def clean_text(text: str) -> str:
    text = IMAGE_COMMENT_RE.sub("", text)
    text = FOOTNOTE_RE.sub("", text)
    text = PRIVATE_USE_RE.sub("", text)
    text = LOOSE_PUNCT_RE.sub(r"\1", text)
    return text.strip() + "\n"


def extract_chapter_title(text: str) -> str:
    """1a linha e sempre '# Capitulo <label>. <titulo descritivo>' nos capitulos do Quijote."""
    first = text.splitlines()[0].strip()
    return re.sub(r"^#\s*", "", first).strip()


def split_into_parts(text: str, n_parts: int) -> list[str]:
    """Divide o texto em n_parts equilibradas, em fronteiras de paragrafo (linha em branco)."""
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    total = sum(word_count(p) for p in paras)
    target = total / n_parts
    parts, cur, cur_w = [], [], 0
    for p in paras:
        cur.append(p)
        cur_w += word_count(p)
        if cur_w >= target and len(parts) < n_parts - 1:
            parts.append("\n\n".join(cur))
            cur, cur_w = [], 0
    if cur:
        parts.append("\n\n".join(cur))
    return parts


def collect_units(src: Path) -> tuple[list[dict], list[str]]:
    """Varre output/chapters/, classifica e ordena: P1 prologo, P1-C001..N, P2 prologo, P2-C001..N."""
    fronts, chapters, excluded = {}, {}, []
    for p in sorted(src.glob("*.md")):
        if p.name == BACKMATTER:
            excluded.append(p.name)
            continue
        m = FRONT_RE.match(p.name)
        if m:
            fronts[int(m.group(1))] = p
            continue
        m = CHAP_RE.match(p.name)
        if m:
            parte, cnum, _label = int(m.group(1)), int(m.group(2)), m.group(3)
            chapters.setdefault(parte, {})[cnum] = p
            continue
        excluded.append(p.name)  # inesperado; reportar, nao incluir

    units = []
    for parte in sorted(fronts.keys() | chapters.keys()):
        if parte in fronts:
            text = clean_text(fronts[parte].read_text(encoding="utf-8"))
            units.append({
                "parte": f"P{parte}", "cap_natural": "Prólogo", "titulo": "Prólogo",
                "text": text, "words": word_count(text),
            })
        for cnum in sorted(chapters.get(parte, {}).keys()):
            path = chapters[parte][cnum]
            text = clean_text(path.read_text(encoding="utf-8"))
            units.append({
                "parte": f"P{parte}", "cap_natural": cnum, "titulo": extract_chapter_title(text),
                "text": text, "words": word_count(text),
            })
    return units, excluded


def main() -> int:
    ap = argparse.ArgumentParser(description="Fase 1 (custom): fragmentacao parte-aware do Don Quijote")
    ap.add_argument("--ppm", type=int, default=130, help="palavras/min (ritmo de narracao)")
    ap.add_argument("--max-min", type=int, default=35, help="acima disto, split do capitulo")
    ap.add_argument("--target-min", type=int, default=30, help="alvo de duracao por parte no split")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not SRC_DIR.is_dir():
        print(f"ERRO: nao encontrei {SRC_DIR}", file=sys.stderr)
        return 1

    units, excluded = collect_units(SRC_DIR)
    for seq, u in enumerate(units, 1):
        u["cap"] = seq

    width = max(2, len(str(len(units))))

    plan = []  # (unit, filename, content)
    for u in units:
        minutes = round(u["words"] / args.ppm)
        u["minutos_est"] = minutes
        # Prologo = 1 unidade -> 1 cena (mecanismo de ancoras, Fase 4); nunca splitar, mesmo
        # que passe do limiar, para nao arriscar cortar a cena ao meio entre 2 arquivos.
        is_prologue = u["cap_natural"] == "Prólogo"
        n_parts = (max(1, -(-minutes // args.target_min))
                   if (minutes > args.max_min and not is_prologue) else 1)
        title_slug = slugify(u["titulo"]) if u["titulo"] else ""
        base = f"{u['cap']:0{width}d}_cap-{u['cap']:0{width}d}"
        if title_slug:
            base = f"{base}_{title_slug}"
        u["n_parts"] = n_parts
        u["base"] = base
        if n_parts == 1:
            plan.append((u, base + ".md", u["text"]))
        else:
            for i, chunk in enumerate(split_into_parts(u["text"], n_parts), 1):
                plan.append((u, f"{base}_p{i}.md", chunk))

    print(f"\n  Don Quijote de la Mancha — Cervantes")
    print(f"  Fontes em {SRC_DIR}: {len(units) + len(excluded)} | incluidas: {len(units)} "
          f"| excluidas: {len(excluded)}")
    print(f"  Padding: {width} digitos | ppm: {args.ppm} | split acima de {args.max_min}min\n")
    print("  INCLUIDOS:")
    for u, fname, _ in plan:
        tag = f"(split {u['n_parts']}p)" if u["n_parts"] > 1 else ""
        natural = u["cap_natural"] if isinstance(u["cap_natural"], str) else f"{u['parte']} cap.{u['cap_natural']}"
        print(f"    {fname:<70} {natural:<14} {u['words']:>6}w ~{u['minutos_est']:>2}min {tag}")
    if excluded:
        print("\n  EXCLUIDOS (nao entram no pipeline de cenas):")
        for name in excluded:
            print(f"    {name}")

    total_words = sum(u["words"] for u in units)
    print(f"\n  Total de palavras incluidas: {total_words:,}".replace(",", "."))

    if args.dry_run:
        print("\n  [dry-run] nada escrito.\n")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_capitulos = []
    for u, fname, content in plan:
        (OUT_DIR / unicodedata.normalize("NFC", fname)).write_text(content, encoding="utf-8")
        index_capitulos.append({
            "arquivo": fname, "cap": u["cap"], "parte": u["parte"], "cap_natural": u["cap_natural"],
            "titulo": u["titulo"], "palavras": word_count(content),
            "minutos_est": round(word_count(content) / args.ppm),
            "parte_de": u["base"] if u["n_parts"] > 1 else None,
        })
    (OUT_DIR / "_capitulos_index.json").write_text(
        json.dumps({
            "sigla": "DQ", "ppm": args.ppm, "width": width,
            "excluidos": excluded,
            "capitulos": index_capitulos,
        }, indent=2, ensure_ascii=False),
        encoding="utf-8")

    manifest_path = PROJ / "_cenas_manifest.json"
    if not manifest_path.is_file():
        manifest_path.write_text(json.dumps({
            "obra": "Don Quijote de la Mancha",
            "autor": "Miguel de Cervantes Saavedra",
            "slug": "don-quijote",
            "width": width,
            "cenas": [],
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  Esqueleto de manifesto criado: {manifest_path}")
    else:
        print(f"\n  Manifesto ja existe, mantido intacto: {manifest_path}")

    print(f"  Escrito: {len(plan)} arquivo(s) em {OUT_DIR}")
    print(f"  Index: {OUT_DIR/'_capitulos_index.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
