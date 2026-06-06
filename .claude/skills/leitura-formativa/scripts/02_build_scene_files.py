#!/usr/bin/env python3
"""
Fase 2 (materializacao) — gera os descritores de cena a partir do _cenas_manifest.json.

Abordagem (a) "Claude no loop": o Claude LE os capitulos, aplica o prompt COF
(templates/prompt_identificacao_cena_por_capitulo.md) e AUTORA o _cenas_manifest.json
(1-5 cenas por capitulo, numeracao global continua). Este script apenas materializa:
  - cenas/<seq>_cap-<cap>_cena-<cena_local>_<slug>.md  (descritor por cena, idioma original)
e valida a consistencia (numeracao continua, capitulos-fonte existentes).

NAO chama LLM. A inteligencia (selecao de cenas) vem do manifesto.

Uso:
    python3 02_build_scene_files.py --project projetos/literatura/<slug> [--dry-run]
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata
from pathlib import Path

PILAR_NOME = {
    "intuicao": "Primazia da Intuição",
    "sinceridade": "Sinceridade Existencial",
    "memoria": "Memória Afetiva e Imaginativa",
    "meio": "Literatura como Meio",
}


def slugify(s: str) -> str:
    """Slug ASCII para filenames: remove acentos (so nomes de arquivo; conteudo mantem acentos)."""
    s = unicodedata.normalize("NFKD", s.strip()).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^\w\-]", "", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description="Fase 2: materializa descritores de cena do manifesto")
    ap.add_argument("--project", required=True, help="pasta do projeto do livro")
    ap.add_argument("--manifest", default="_cenas_manifest.json")
    ap.add_argument("--cenas-dir", default="cenas")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.project).expanduser()
    man_path = proj / args.manifest
    if not man_path.is_file():
        print(f"ERRO: manifesto nao encontrado: {man_path}", file=sys.stderr)
        return 1
    man = json.loads(man_path.read_text(encoding="utf-8"))
    cenas = man.get("cenas", [])
    width = man.get("width", 2)

    # --- sanity check ---
    erros = []
    seqs = [c["seq_global"] for c in cenas]
    if seqs != list(range(1, len(cenas) + 1)):
        erros.append(f"seq_global nao e continuo 1..{len(cenas)}: {seqs}")
    # cena_local reinicia por capitulo e e continuo dentro do capitulo
    from itertools import groupby
    for cap, grp in groupby(sorted(cenas, key=lambda c: (c["cap"], c["cena_local"])), key=lambda c: c["cap"]):
        locais = [c["cena_local"] for c in grp]
        if locais != list(range(1, len(locais) + 1)):
            erros.append(f"cena_local do cap {cap} nao e continuo: {locais}")
    # capitulos-fonte existem?
    cap_dir = next((d for d in proj.glob("*-capitulos") if d.is_dir()), None)
    for c in cenas:
        if cap_dir and not (cap_dir / c["source_chapter"]).is_file():
            erros.append(f"cena {c['seq_global']}: capitulo-fonte ausente {c['source_chapter']}")
        if c["pilar_foco"] not in PILAR_NOME:
            erros.append(f"cena {c['seq_global']}: pilar invalido '{c['pilar_foco']}'")
    if erros:
        print("SANITY FALHOU:")
        for e in erros:
            print("  -", e)
        return 1
    print(f"Sanity OK: {len(cenas)} cenas, seq 1..{len(cenas)} continuo, fontes e pilares validos.")

    # --- plano de nomes ---
    plan = []
    for c in cenas:
        fn = (f"{c['seq_global']:0{width}d}_cap-{c['cap']:0{width}d}"
              f"_cena-{c['cena_local']:0{width}d}_{slugify(c['titulo'])}.md")
        plan.append((c, fn))

    print(f"\n  {man['obra']} — {len(plan)} cenas")
    for c, fn in plan:
        print(f"    {fn}")

    if args.dry_run:
        print("\n  [dry-run] nada escrito.\n")
        return 0

    cdir = proj / args.cenas_dir
    cdir.mkdir(parents=True, exist_ok=True)
    for c, fn in plan:
        body = (
            f"# Cena {c['seq_global']:0{width}d} — {c['titulo']}\n\n"
            f"- **Capítulo:** {c['cap']} (cena {c['cena_local']} do capítulo)\n"
            f"- **Localização:** {c['localizacao']}\n"
            f"- **Capítulo-fonte (NotebookLM):** `{c['source_chapter']}`\n"
            f"- **Pilar COF em foco:** {PILAR_NOME[c['pilar_foco']]}\n\n"
            f"## Resumo\n{c['resumo']}\n\n"
            f"## Justificativa (leitura formativa)\n{c['justificativa_cof']}\n"
        )
        (cdir / unicodedata.normalize("NFC", fn)).write_text(body, encoding="utf-8")
    print(f"\n  Escrito: {len(plan)} descritores em {cdir}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
