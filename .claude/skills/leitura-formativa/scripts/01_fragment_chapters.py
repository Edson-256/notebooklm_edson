#!/usr/bin/env python3
"""
Fase 1 — Fragmentacao de capitulos (skill leitura-formativa).

Consome a saida do Docling (output/chapters/) e produz, na pasta do projeto,
1 ARQUIVO POR CAPITULO no padrao da skill:  <seq>_cap-<cap>_<titulo>.md

Regras:
  - 1 capitulo = 1 arquivo (texto legivel E fonte unica no NotebookLM). As cenas
    (1-5 por capitulo, fase 2) sao apenas focos que apontam para este arquivo.
  - NAO re-fragmenta: o Docling ja fragmentou. Aqui so renomeia/copia + classifica.
  - Duracao estimada a 130 ppm (mesmo ritmo do Docling). Capitulo > hard_max_min
    e marcado para split em N partes (_p1/_p2...), em fronteiras de paragrafo.
  - Padding dinamico: largura = max(2, digitos do total de capitulos incluidos).
  - Front/back-matter (Notas, Biografia, Creditos, Sumario, Indice, Copyright...)
    e EXCLUIDO por padrao, mas REPORTADO (o usuario e o especialista; pode incluir
    com --include-all ou reincluir manualmente). Prefacio/prologo/introducao/
    epilogo sao MANTIDOS (relevantes).

Uso:
    python3 01_fragment_chapters.py \
        --docling-src ~/dev/_ref/docling-projeto/projects/literatura/<livro>/output \
        --dest <pasta-do-projeto> --sigla XX [--dry-run] [--ppm 130] [--max-min 35]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

# Front/back-matter: nomes que NAO sao narrativa. Prefacio/prologo/intro/epilogo NAO entram aqui.
SKIP_KEYWORDS = [
    "nota", "notas", "credito", "creditos", "biografia", "sobre o autor",
    "sobre a autora", "sumario", "indice", "copyright", "ficha", "agradecimento",
    "agradecimentos", "apendice", "glossario", "posfacio", "dados internacionais",
    "colofao", "ISBN",
]

CHAP_RE = re.compile(r"^C(\d+)-(.+)\.md$", re.IGNORECASE)


def strip_accents_lower(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


def slugify(s: str, keep_accents: bool = True) -> str:
    """Slug legivel: espacos/barras -> hifen; remove pontuacao perigosa. Mantem acentos (NFC)."""
    s = s.strip()
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^\w\-]", "", s, flags=re.UNICODE)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    if keep_accents:
        return unicodedata.normalize("NFC", s)
    return strip_accents_lower(s)


def word_count(text: str) -> int:
    return len(text.split())


def extract_title(text: str, label: str) -> str:
    """Titulo = 1a linha nao-vazia se for descritiva (nao apenas o numero do capitulo)."""
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # primeira linha costuma ser so o numero do capitulo (ex.: "1") ou o nome do back-matter
        if line == label or line.isdigit():
            return ""  # sem titulo descritivo
        if len(line) <= 80 and not line.endswith((".", "!", "?", ":", ";", ",")):
            return line  # parece um titulo
        return ""  # primeira linha ja e corpo de texto
    return ""


def is_skippable(label: str, words: int) -> bool:
    lab = strip_accents_lower(label)
    return any(k in lab for k in SKIP_KEYWORDS)


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


def main() -> int:
    ap = argparse.ArgumentParser(description="Fase 1: fragmentacao de capitulos (Docling -> projeto)")
    ap.add_argument("--docling-src", required=True, help="pasta output/ do livro no Docling")
    ap.add_argument("--dest", required=True, help="pasta do projeto (saida)")
    ap.add_argument("--sigla", required=True, help="prefixo da pasta de capitulos (ex.: IVAN)")
    ap.add_argument("--ppm", type=int, default=130, help="palavras/min (ritmo de narracao)")
    ap.add_argument("--max-min", type=int, default=35, help="acima disto, split do capitulo")
    ap.add_argument("--target-min", type=int, default=30, help="alvo de duracao por parte no split")
    ap.add_argument("--include-all", action="store_true", help="nao excluir front/back-matter")
    ap.add_argument("--dry-run", action="store_true", help="so mostra o plano")
    args = ap.parse_args()

    src = Path(args.docling_src).expanduser()
    chapters_dir = src / "chapters"
    if not chapters_dir.is_dir():
        print(f"ERRO: nao encontrei {chapters_dir}", file=sys.stderr)
        return 1

    # coleta + ordena por numero CNNN
    raw = []
    for p in chapters_dir.glob("*.md"):
        m = CHAP_RE.match(p.name)
        if not m:
            continue
        raw.append((int(m.group(1)), m.group(2), p))
    raw.sort(key=lambda t: t[0])
    if not raw:
        print(f"ERRO: nenhum capitulo CNNN-*.md em {chapters_dir}", file=sys.stderr)
        return 1

    # classifica
    items = []
    for cnum, label, path in raw:
        text = path.read_text(encoding="utf-8")
        words = word_count(text)
        minutes = round(words / args.ppm)
        skip = (not args.include_all) and is_skippable(label, words)
        items.append({
            "cnum": cnum, "label": label, "path": path, "text": text,
            "words": words, "minutes": minutes, "title": extract_title(text, label),
            "numeric": label.isdigit(), "included": not skip,
        })

    included = [it for it in items if it["included"]]
    excluded = [it for it in items if not it["included"]]
    width = max(2, len(str(len(included))))

    # planeja nomes + splits
    plan = []
    for seq, it in enumerate(included, 1):
        cap_token = f"{int(it['label']):0{width}d}" if it["numeric"] else slugify(it["label"])
        base = f"{seq:0{width}d}_cap-{cap_token}"
        title_slug = slugify(it["title"]) if it["title"] else ""
        if title_slug:
            base = f"{base}_{title_slug}"
        n_parts = max(1, -(-it["minutes"] // args.target_min)) if it["minutes"] > args.max_min else 1
        it.update({"seq": seq, "n_parts": n_parts, "base": base})
        if n_parts == 1:
            plan.append((it, base + ".md", it["text"]))
        else:
            for i, chunk in enumerate(split_into_parts(it["text"], n_parts), 1):
                plan.append((it, f"{base}_p{i}.md", chunk))

    # relatorio
    print(f"\n  Livro: {src.parent.name}")
    print(f"  Capitulos no Docling: {len(items)} | incluidos: {len(included)} | excluidos: {len(excluded)}")
    print(f"  Padding: {width} digitos | ppm: {args.ppm} | split acima de {args.max_min}min\n")
    print("  INCLUIDOS:")
    for it, fname, _ in plan:
        tag = f"(split {it['n_parts']}p)" if it["n_parts"] > 1 else ""
        print(f"    {fname:<40} {it['words']:>6}w ~{it['minutes']:>2}min {tag}")
    if excluded:
        print("\n  EXCLUIDOS (front/back-matter — confirme; use --include-all p/ manter):")
        for it in excluded:
            print(f"    C{it['cnum']:03d}-{it['label']:<28} {it['words']:>6}w  [{it['label']}]")

    if args.dry_run:
        print("\n  [dry-run] nada escrito.\n")
        return 0

    # escreve
    out_dir = Path(args.dest).expanduser() / f"{args.sigla}-capitulos"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for it, fname, content in plan:
        (out_dir / unicodedata.normalize("NFC", fname)).write_text(content, encoding="utf-8")
        manifest.append({
            "arquivo": fname, "seq": it["seq"], "cap_label": it["label"],
            "titulo": it["title"], "palavras": word_count(content),
            "minutos_est": round(word_count(content) / args.ppm), "parte_de": it["base"],
        })
    (out_dir / "_capitulos_index.json").write_text(
        json.dumps({"sigla": args.sigla, "ppm": args.ppm, "width": width,
                    "excluidos": [f"C{it['cnum']:03d}-{it['label']}" for it in excluded],
                    "capitulos": manifest}, indent=2, ensure_ascii=False),
        encoding="utf-8")
    print(f"\n  Escrito: {len(plan)} arquivo(s) em {out_dir}")
    print(f"  Index: {out_dir/'_capitulos_index.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
