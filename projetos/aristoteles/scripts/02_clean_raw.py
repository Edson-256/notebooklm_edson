#!/usr/bin/env python3
"""
Limpa os textos brutos baixados em obras/{categoria}/{obra}/_raw/*.txt
e produz versões higienizadas em obras/{categoria}/{obra}/clean/*.txt.

Dois pipelines:

A) MIT/Oxford (28 obras): formato consistente
   - 4 linhas header (Provided by + URL)
   - Título / By Aristotle / Translated by
   - Separador "---..."
   - Corpo com markers BOOK N / Part N
   - "THE END" + separador + bloco copyright

B) Archive.org DJVU OCR (5 obras): cada uma com sua "sujeira"
   - Geração dos Animais (Loeb Peck): página de rosto + corpo
   - Eudemian Ethics (Loeb 285): contém 3 obras coladas (Athenian + Eudemian + Virtues)
   - Magna Moralia (Oxford Stock): introdução + corpo
   - Virtues and Vices (Loeb 285, mesmo arquivo da Eudemian): extrair só essa parte
   - Econômicos (Oxford Forster): page headers "OECONOMICA" repetidos

Uso:
  python scripts/02_clean_raw.py            # processa tudo
  python scripts/02_clean_raw.py --only metafisica
  python scripts/02_clean_raw.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = PROJECT_ROOT / "_raw" / "download_manifest.json"


# ---------------------------------------------------------------------------
# Pipeline A: MIT
# ---------------------------------------------------------------------------

MIT_HEADER_END = re.compile(r"^-{40,}\s*$")
MIT_END_MARKER = re.compile(r"^\s*THE END\s*$", re.IGNORECASE)
MIT_PART_LINE = re.compile(r'^Part\s+\d+\s*"?\s*$')
MIT_BODY_START = re.compile(r"^(BOOK\s+[IVXLCDM\d]+|SECTION\s+\d+|Part\s+1)\s*\"?\s*$",
                            re.IGNORECASE)


def clean_mit(raw: str) -> str:
    """Detecta início do corpo (BOOK / SECTION / Part 1) e fim em THE END.
    Estratégia robusta tanto para arquivos com separador '---' no topo (download
    direto) quanto sem (extraídos do Google cache, que só têm '---' antes do footer)."""
    lines = raw.splitlines()

    # 1. Encontra início do corpo: primeiro BOOK/SECTION/Part 1.
    body_start = None
    for i, ln in enumerate(lines):
        if MIT_BODY_START.match(ln.strip()):
            body_start = i
            break

    # Fallback: se não achou marker, usa primeiro '---' (formato MIT clássico)
    if body_start is None:
        for i, ln in enumerate(lines):
            if MIT_HEADER_END.match(ln):
                body_start = i + 1
                while body_start < len(lines) and not lines[body_start].strip():
                    body_start += 1
                break
    if body_start is None:
        return raw  # sem marcadores conhecidos — entrega cru

    # 2. Encontra fim do corpo: THE END
    body_end = len(lines)
    for i in range(body_start, len(lines)):
        if MIT_END_MARKER.match(lines[i]):
            body_end = i
            break

    body = lines[body_start:body_end]

    # 3. Normaliza "Part N \"" (artefato MIT) → "Part N"
    cleaned: list[str] = []
    for ln in body:
        if MIT_PART_LINE.match(ln):
            ln = ln.rstrip().rstrip('"').rstrip()
        cleaned.append(ln)

    out = re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned))
    return out.strip() + "\n"


# ---------------------------------------------------------------------------
# Pipeline B: Archive.org DJVU OCR
# ---------------------------------------------------------------------------

def strip_repeating_page_headers(lines: list[str], headers: list[str]) -> list[str]:
    """Remove linhas que são apenas page headers (ex: 'OECONOMICA' isolada)."""
    keep: list[str] = []
    header_set = {h.strip().upper() for h in headers}
    page_num_re = re.compile(r"^\s*\d{1,4}[a-z]?\s*$|^[ivxlcdm]+\s*$|^[Ii]\d{3,4}[a-z']*\s*[A-Z]*\s*$")
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            keep.append(ln)
            continue
        if stripped.upper() in header_set:
            continue
        if page_num_re.match(stripped):
            continue
        keep.append(ln)
    return keep


def clean_archive_with_book_start(raw: str, *, start_marker_re: str,
                                  end_marker_re: str | None = None,
                                  page_headers: list[str] | None = None) -> str:
    """Detecta primeira ocorrência substantiva do start_marker (e.g. 'BOOK I'),
    descarta tudo antes, opcionalmente trunca em end_marker, e remove page headers."""
    lines = raw.splitlines()

    start_re = re.compile(start_marker_re)
    body_start = None
    for i, ln in enumerate(lines):
        if start_re.match(ln.strip()):
            body_start = i
            break
    if body_start is None:
        # não achou marker — mantém tudo
        body_start = 0

    body_end = len(lines)
    if end_marker_re:
        end_re = re.compile(end_marker_re)
        for i in range(body_start + 1, len(lines)):
            if end_re.match(lines[i].strip()):
                body_end = i
                break

    body = lines[body_start:body_end]
    if page_headers:
        body = strip_repeating_page_headers(body, page_headers)

    out = re.sub(r"\n{3,}", "\n\n", "\n".join(body))
    return out.strip() + "\n"


def clean_archive_extract_range(raw: str, *, after_pattern: str, until_pattern: str,
                                page_headers: list[str] | None = None,
                                min_line: int = 0) -> str:
    """Extrai trecho entre after_pattern (inclusive) e until_pattern (exclusivo).
    min_line: ignora matches antes desta linha (útil para pular capa/índice).
    Usado para Eudemian / Virtues dentro do volume Loeb 285."""
    lines = raw.splitlines()
    after_re = re.compile(after_pattern)
    until_re = re.compile(until_pattern)

    start = None
    for i, ln in enumerate(lines):
        if i < min_line:
            continue
        if after_re.search(ln):
            start = i
            break
    if start is None:
        return raw  # fallback

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if until_re.search(lines[i]):
            end = i
            break

    body = lines[start:end]
    if page_headers:
        body = strip_repeating_page_headers(body, page_headers)
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(body))
    return out.strip() + "\n"


# ---------------------------------------------------------------------------
# Configuração por obra (pipeline B)
# ---------------------------------------------------------------------------

ARCHIVE_RULES: dict[str, dict] = {
    # path relativo do .txt (a partir de obras/) → regra
    "03_psicologia_biologia/07_geracao_animais/_raw/on_the_generation_of_animals.txt": {
        "pipeline": "book_start",
        "start_marker_re": r"^BOOK\s+I\s*$",
        "page_headers": ["GENERATION OF ANIMALS", "ARISTOTLE"],
    },
    "05_etica/02_etica_eudemo/_raw/eudemian_ethics.txt": {
        # arquivo Loeb 285 contém: Athenian Const + Eudemian Ethics + Virtues & Vices
        # extrair só Eudemian: começa em "BOOK  I" depois do índice da Eudemian (linha ~8708)
        "pipeline": "extract_range",
        # Depois do índice analítico da Eudemian, vem o texto
        "after_pattern": r"^BOOK\s+I\s*$",
        "until_pattern": r"^ON\s+VIRTUES\s+AND\s+VICES\s*$|^VIRTUES\s+AND\s+VICES\s*$",
        "page_headers": ["EUDEMIAN ETHICS", "ARISTOTLE"],
    },
    "05_etica/03_magna_moralia/_raw/magna_moralia.txt": {
        "pipeline": "book_start",
        "start_marker_re": r"^BOOK\s+I\s*$",
        "page_headers": ["MAGNA MORALIA", "ARISTOTLE"],
    },
    "05_etica/03_magna_moralia/_raw/on_virtues_and_vices.txt": {
        # mesmo arquivo Loeb 285 (cópia de athenianconstitu00arisuoft) — extrai só a parte
        # Pular capa (linhas 1-100) e INDEX da Eudemian (até linha 21900).
        "pipeline": "extract_range",
        "after_pattern": r"ON\s+VIRTUES\s+AND\s+VICES",
        "until_pattern": r"^\s*INDEX\s*$|^\s*GENERAL\s+INDEX\s*$",
        "min_line": 21900,
        "page_headers": ["VIRTUES AND VICES", "ON VIRTUES AND VICES", "ARISTOTLE"],
    },
    "06_politica/03_economicos/_raw/economics.txt": {
        "pipeline": "book_start",
        "start_marker_re": r"^BOOK\s+I\.?\s*$",
        "page_headers": ["OECONOMICA", "ARISTOTLE"],
    },
}


def clean_archive_file(rel_path: str, raw: str) -> str | None:
    rule = ARCHIVE_RULES.get(rel_path)
    if not rule:
        return None
    if rule["pipeline"] == "book_start":
        return clean_archive_with_book_start(
            raw,
            start_marker_re=rule["start_marker_re"],
            end_marker_re=rule.get("end_marker_re"),
            page_headers=rule.get("page_headers"),
        )
    if rule["pipeline"] == "extract_range":
        return clean_archive_extract_range(
            raw,
            after_pattern=rule["after_pattern"],
            until_pattern=rule["until_pattern"],
            page_headers=rule.get("page_headers"),
            min_line=rule.get("min_line", 0),
        )
    raise ValueError(f"pipeline desconhecido: {rule['pipeline']}")


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def detect_pipeline(source: str) -> str:
    if source.startswith("MIT"):
        return "mit"
    if "archive.org" in source.lower() or source.lower().startswith("archive"):
        return "archive"
    return "mit"  # default seguro


def process(item: dict, *, dry_run: bool) -> dict:
    raw_rel = item["txt_path"]  # ex: obras/04_metafisica/01_metafisica/_raw/metaphysics.txt
    raw_path = PROJECT_ROOT / raw_rel
    if not raw_path.exists():
        return {"obra": item["obra"], "status": "missing_raw", "raw_path": raw_rel}

    # Output em sibling 'clean/' (mesmo nível que '_raw/')
    clean_dir = raw_path.parent.parent / "clean"
    clean_path = clean_dir / raw_path.name
    rel_for_rules = str(raw_path.relative_to(PROJECT_ROOT / "obras"))

    pipeline = detect_pipeline(item["fonte"])
    raw_text = raw_path.read_text(encoding="utf-8", errors="replace")

    if pipeline == "mit":
        cleaned = clean_mit(raw_text)
        note = "mit"
    else:
        cleaned = clean_archive_file(rel_for_rules, raw_text)
        if cleaned is None:
            # sem regra específica — aplica book_start padrão
            cleaned = clean_archive_with_book_start(
                raw_text, start_marker_re=r"^BOOK\s+I\s*$"
            )
            note = "archive(default)"
        else:
            note = "archive(rule)"

    if dry_run:
        return {"obra": item["obra"], "status": "dry_run",
                "pipeline": note, "in_bytes": len(raw_text), "out_bytes": len(cleaned)}

    clean_dir.mkdir(parents=True, exist_ok=True)
    clean_path.write_text(cleaned, encoding="utf-8")
    return {
        "obra": item["obra"],
        "categoria": item["categoria"],
        "titulo_pt": item["titulo_pt"],
        "pipeline": note,
        "in_bytes": len(raw_text),
        "out_bytes": len(cleaned),
        "ratio": round(len(cleaned) / max(len(raw_text), 1), 3),
        "clean_path": str(clean_path.relative_to(PROJECT_ROOT)),
        "status": "ok",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None,
                        help="Substring de categoria/obra para filtrar.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not MANIFEST_PATH.exists():
        print(f"ERRO: manifesto não encontrado em {MANIFEST_PATH}.")
        print("Rode antes: python3 scripts/01_download_corpus.py")
        return 2

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    items = [r for r in manifest["results"] if r["status"].startswith(("ok", "cached"))]
    if args.only:
        items = [r for r in items if args.only.lower() in r["categoria"].lower()
                 or args.only.lower() in r["obra"].lower()]

    results = []
    for i, it in enumerate(items, 1):
        print(f"[{i:02d}/{len(items)}] {it['categoria']}/{it['obra']}: {it['titulo_pt']}")
        res = process(it, dry_run=args.dry_run)
        marker = f"  → {res['status']}"
        if "pipeline" in res:
            marker += f" [{res['pipeline']}]"
        if "in_bytes" in res:
            marker += (f"  {res['in_bytes']/1024:.1f} KB → "
                       f"{res['out_bytes']/1024:.1f} KB "
                       f"({res.get('ratio', 0)*100:.0f}%)")
        print(marker)
        results.append(res)

    # manifesto de limpeza
    if not args.dry_run:
        clean_manifest = PROJECT_ROOT / "_raw" / "clean_manifest.json"
        clean_manifest.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total": len(results),
            "ok": sum(1 for r in results if r["status"] == "ok"),
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nManifesto: {clean_manifest.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
