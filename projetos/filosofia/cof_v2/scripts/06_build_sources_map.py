#!/usr/bin/env python3
"""Constrói _sources_map.json mapeando cada um dos 782 itens do inventário à
fonte correspondente no NotebookLM (5508086a-da53-4947-bce4-a1d7d83cf0e2).

Uso:
    .venv/bin/python scripts/06_build_sources_map.py
    .venv/bin/python scripts/06_build_sources_map.py --refresh-nlm  # re-busca lista de fontes
    .venv/bin/python scripts/06_build_sources_map.py --validate     # só audita o map existente

Saídas:
    _sources_map.json — fonte da verdade pro runner de áudio
    _sources_map_raw.json — cache da listagem nlm
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_ID = "5508086a-da53-4947-bce4-a1d7d83cf0e2"
PROFILE = "default"
INVENTARIO = ROOT / "plano" / "01_inventario_completo.json"
COMPILADAS = ROOT / "compiladas"
PROMPTS = ROOT / "prompts"
GUIAS = ROOT / "guias"
RAW_OUT = ROOT / "_sources_map_raw.json"
MAP_OUT = ROOT / "_sources_map.json"

# Fontes temáticas (kind → título da fonte no notebook)
TEMATICA_SOURCE = {
    "apostila": "COF-Tematicas-Apostilas.md",
    "artigo": "COF-Tematicas-Artigos.md",
    "teoria_estado": "COF-Tematicas-Teoria-do-estado.md",
}

# Overrides manuais: id do inventário → título da fonte no notebook
# Quando o filename do inventário não bate com nenhuma variação automática.
TITLE_OVERRIDES = {
    "livro-elementos-de-tipologia-espiritual": "Elementos de tipologia espiritual.md (remasterizado).md",
}


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def fetch_nlm_sources(refresh: bool) -> list[dict]:
    """Lista as fontes do notebook. Cacheia em _sources_map_raw.json."""
    if not refresh and RAW_OUT.exists():
        return json.loads(RAW_OUT.read_text())
    print(f"[nlm] listando fontes do notebook {NOTEBOOK_ID}...", file=sys.stderr)
    result = subprocess.run(
        ["nlm", "source", "list", NOTEBOOK_ID, "--profile", PROFILE, "--json"],
        capture_output=True, text=True, check=True,
    )
    sources = json.loads(result.stdout)
    RAW_OUT.write_text(json.dumps(sources, ensure_ascii=False, indent=2))
    print(f"[nlm] {len(sources)} fontes salvas em {RAW_OUT.relative_to(ROOT)}", file=sys.stderr)
    return sources


def build_aula_to_bucket() -> dict[int, str]:
    """Varre os COF-Aulas-*.md para descobrir em qual arquivo está cada Aula NNN."""
    pat = re.compile(r"^## Aula 0*(\d+)\b", re.MULTILINE)
    mapping: dict[int, str] = {}
    aulas_dir = COMPILADAS / "aulas"
    for f in sorted(aulas_dir.glob("COF-Aulas-*.md")):
        if "Tematicas" in f.name:
            continue
        text = f.read_text(encoding="utf-8")
        for m in pat.finditer(text):
            num = int(m.group(1))
            if num in mapping and mapping[num] != f.name:
                print(f"[warn] Aula {num} aparece em {mapping[num]} e em {f.name}",
                      file=sys.stderr)
            mapping[num] = f.name
    return mapping


def resolve_source_candidates(item: dict, aula_bucket: dict[int, str]) -> list[str]:
    """Retorna candidatos a título de fonte, em ordem de preferência."""
    if (override := TITLE_OVERRIDES.get(item["id"])) is not None:
        return [override]
    kind = item["kind"]
    if kind == "aula":
        num = item["numero_aula"]
        title = aula_bucket.get(num)
        return [title] if title else []
    if kind == "livro":
        # Inventário tem ".md", mas algumas fontes no notebook estão com ".md.md"
        # (artefato de scripts/03_collect_books_extras.py). Tenta ambas variações.
        f = item["file"]
        return [f, f + ".md"]
    if kind == "extra_aula":
        return [f"COF Extracurricular — {item['curso']}.md"]
    if kind in TEMATICA_SOURCE:
        return [TEMATICA_SOURCE[kind]]
    return []


def build_map(refresh_nlm: bool) -> dict:
    inv = json.loads(INVENTARIO.read_text())
    sources = fetch_nlm_sources(refresh_nlm)
    title_to_id = {nfc(s["title"]): s["id"] for s in sources}
    aula_bucket = build_aula_to_bucket()

    items: dict[str, dict] = {}
    misses: list[str] = []
    slug_seen: dict[str, list[int]] = {}
    for it in inv:
        slug_seen.setdefault(it["id"], []).append(it["seq_global"])
        candidates = resolve_source_candidates(it, aula_bucket)
        if not candidates:
            misses.append(f"seq={it['seq_global']} {it['id']} (kind={it['kind']}): regra ausente")
            continue
        title = next((c for c in candidates if nfc(c) in title_to_id), None)
        if title is None:
            tried = " | ".join(candidates)
            misses.append(f"seq={it['seq_global']} {it['id']}: nenhum candidato bate ({tried})")
            continue
        sid = title_to_id[nfc(title)]
        prompt_p = PROMPTS / f"{it['id']}.md"
        guide_p = GUIAS / f"{it['id']}.md"
        # Indexa por seq_global (string) — ID canônico do runner, sem colisão.
        items[str(it["seq_global"])] = {
            "seq_global": it["seq_global"],
            "slug": it["id"],
            "kind": it["kind"],
            "titulo": it["titulo"],
            "audio_format": it.get("formato_audio"),
            "audio_format_reason": it.get("formato_razao"),
            "source_title": title,
            "source_id": sid,
            "prompt_path": str(prompt_p.relative_to(ROOT)) if prompt_p.exists() else None,
            "guide_path": str(guide_p.relative_to(ROOT)) if guide_p.exists() else None,
        }

    slug_collisions = {s: seqs for s, seqs in slug_seen.items() if len(seqs) > 1}

    return {
        "metadata": {
            "notebook_id": NOTEBOOK_ID,
            "profile": PROFILE,
            "total_inventario": len(inv),
            "total_mapeados": len(items),
            "total_misses": len(misses),
            "slug_collisions": slug_collisions,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "items": items,
        "misses": misses,
    }


def validate(data: dict) -> int:
    """Imprime estatísticas do mapeamento e retorna exit code (0 = ok)."""
    md = data["metadata"]
    items = data["items"]
    misses = data["misses"]

    print(f"Notebook: {md['notebook_id']}")
    print(f"Inventário: {md['total_inventario']} itens")
    print(f"Mapeados:   {md['total_mapeados']}")
    print(f"Misses:     {md['total_misses']}")
    print()

    by_kind: dict[str, int] = {}
    no_prompt = 0
    no_guide = 0
    for it in items.values():
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
        if not it["prompt_path"]:
            no_prompt += 1
        if not it["guide_path"]:
            no_guide += 1
    print("Por kind:")
    for k, c in sorted(by_kind.items()):
        print(f"  {k:14s} {c}")
    print()
    print(f"Itens sem prompt: {no_prompt}")
    print(f"Itens sem guia:   {no_guide}")

    collisions = md.get("slug_collisions", {})
    if collisions:
        print(f"\n[warn] {len(collisions)} colisões de slug (dois seq_global compartilham id):")
        for s, seqs in collisions.items():
            print(f"  - {s}: seq_global={seqs}")
        print("  → seq_global é o ID canônico (índice do _sources_map.json), sem colisão.")
        print("  → mas prompts/guias compartilham filename — runner deve copiar/regenerar se precisar variar.")

    if misses:
        print("\n[!] Misses:")
        for m in misses[:30]:
            print(f"  - {m}")
        if len(misses) > 30:
            print(f"  ... +{len(misses)-30} mais")
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-nlm", action="store_true",
                    help="Re-busca lista de fontes do NotebookLM (ignora cache)")
    ap.add_argument("--validate", action="store_true",
                    help="Só valida _sources_map.json existente, sem reconstruir")
    ap.add_argument("--out", type=Path, default=MAP_OUT)
    args = ap.parse_args()

    if args.validate:
        if not args.out.exists():
            print(f"[err] {args.out} não existe — rode sem --validate primeiro",
                  file=sys.stderr)
            return 2
        data = json.loads(args.out.read_text())
        return validate(data)

    data = build_map(args.refresh_nlm)
    args.out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"[ok] {args.out.relative_to(ROOT)} escrito ({len(data['items'])} itens)\n",
          file=sys.stderr)
    return validate(data)


if __name__ == "__main__":
    sys.exit(main())
