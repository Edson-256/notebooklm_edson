#!/usr/bin/env python3
"""
Segmenta cada obra (texto em obras/{cat}/{obra}/clean/*.txt) em arquivos por
livro+capítulo: obras/{cat}/{obra}/capitulos/L{NN}-C{MM}.md.

Markers reconhecidos:
- MIT (28 obras): BOOK I/II/.../X, SECTION 1/2 (alternativa para obras curtas),
  Part 1/2/.../N ou Part I/II/.../N (poética usa romanos).
- Archive Stock (Magna Moralia): BOOK I + CHAPTER I/2/3/.../N.
- Outras obras Archive (Eudemian, Generation, Economics, Virtues): só usam
  BOOK como divisão (sem CHAPTER limpa) — vira 1 arquivo por livro.

Cada arquivo gerado tem frontmatter YAML com obra, livro, capítulo e fonte.

Uso:
  python scripts/03_segment_capitulos.py
  python scripts/03_segment_capitulos.py --only metafisica
  python scripts/03_segment_capitulos.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOWNLOAD_MANIFEST = PROJECT_ROOT / "_raw" / "download_manifest.json"


# Markers — captura o "nome bruto" (1) e o "identificador" (2)
# Aceita BOOK I, BOOK II, ..., BOOK ONE, BOOK TWO (Politics MIT usa palavras)
_WORD_NUMS = ("ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|"
              "ELEVEN|TWELVE|THIRTEEN|FOURTEEN|FIFTEEN")
BOOK_RE = re.compile(
    rf"^\s*(BOOK\s+({_WORD_NUMS}|[IVXLCDM\d]+))\s*$", re.IGNORECASE)
SECTION_RE = re.compile(r"^\s*(SECTION\s+(\d+))\s*$", re.IGNORECASE)
PART_RE = re.compile(r"^\s*(Part\s+([IVX\d]+))\s*$", re.IGNORECASE)
# Magna Moralia: "CHAPTER I.", "CHAPTER 2.", "CHAPTER II." (sic), etc.
CHAPTER_RE = re.compile(r"^\s*(CHAPTER\s+([IVX\d]+))[\.,]?(?:\s|$)", re.IGNORECASE)
# Nicomachean Ethics: capítulos como número solitário ("1", "2") seguidos de
# parágrafo. Para não pegar números que aparecem dentro do texto, exige só dígitos
# na linha + linha anterior em branco (validado no varredor).
NUM_CHAPTER_RE = re.compile(r"^\s*(\d{1,2})\s*$")

_WORD_TO_INT = {
    "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5, "SIX": 6,
    "SEVEN": 7, "EIGHT": 8, "NINE": 9, "TEN": 10,
    "ELEVEN": 11, "TWELVE": 12, "THIRTEEN": 13, "FOURTEEN": 14, "FIFTEEN": 15,
}


ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8,
    "IX": 9, "X": 10, "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
}


def to_int(ident: str) -> int | None:
    """Aceita romano (I-XV), arábico, ou palavra em inglês (ONE..FIFTEEN)."""
    ident = ident.strip().upper()
    if ident.isdigit():
        return int(ident)
    if ident in _WORD_TO_INT:
        return _WORD_TO_INT[ident]
    if ident in ROMAN_MAP:
        return ROMAN_MAP[ident]
    # tenta romano genérico
    try:
        result = 0
        prev = 0
        for ch in reversed(ident):
            val = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}.get(ch)
            if val is None:
                return None
            if val < prev:
                result -= val
            else:
                result += val
            prev = val
        return result if result > 0 else None
    except Exception:  # noqa: BLE001
        return None


MAX_BOOKS = 20  # nenhuma obra de Aristóteles tem mais de 20 livros (Metafísica = 14)
MAX_CHAPTERS_PER_BOOK = 200  # História dos Animais L09 tem ~50; margem generosa


def find_markers(lines: list[str]) -> list[tuple[int, str, str, int | None]]:
    """Varre as linhas e retorna lista de (line_idx, kind, raw_marker, num).
    kind ∈ {'book', 'section', 'part', 'chapter'}.

    Aplica sanity checks: rejeita números de livro fora do range plausível
    (1-20) — protege contra OCR ruim ('BOOK Ill' → 99 via conversão romana)."""
    out: list[tuple[int, str, str, int | None]] = []
    last_chapter_num_in_book = 0
    current_book_idx = 0

    for i, ln in enumerate(lines):
        m = BOOK_RE.match(ln)
        if m:
            num = to_int(m.group(2))
            # Sanity: livro plausível (1-20). Sequência também: até o último + 5.
            if num is None or not (1 <= num <= MAX_BOOKS):
                continue
            out.append((i, "book", m.group(1).strip(), num))
            last_chapter_num_in_book = 0
            current_book_idx += 1
            continue
        m = SECTION_RE.match(ln)
        if m:
            num = to_int(m.group(2))
            if num is None or not (1 <= num <= MAX_BOOKS):
                continue
            out.append((i, "section", m.group(1).strip(), num))
            last_chapter_num_in_book = 0
            current_book_idx += 1
            continue
        m = PART_RE.match(ln)
        if m:
            num = to_int(m.group(2))
            out.append((i, "part", m.group(1).strip(), num))
            if num is not None:
                last_chapter_num_in_book = num
            continue
        m = CHAPTER_RE.match(ln)
        if m:
            num = to_int(m.group(2))
            out.append((i, "chapter", m.group(1).strip(), num))
            if num is not None:
                last_chapter_num_in_book = num
            continue
        # numeric chapter (Nicomachean Ethics): "1" / "2" isolado com brancos volta
        m = NUM_CHAPTER_RE.match(ln)
        if m:
            num = int(m.group(1))
            prev_blank = (i == 0) or (not lines[i - 1].strip())
            # próxima linha não-em-branco dentro da janela de 3
            next_has = any((i + k < len(lines) and bool(lines[i + k].strip()))
                           for k in range(1, 4))
            # aceitar somente se sequencial (num == last+1) ou reinício de livro (num == 1)
            sequential = (num == last_chapter_num_in_book + 1) or (
                num == 1 and last_chapter_num_in_book > 0)
            if prev_blank and next_has and sequential:
                out.append((i, "part", m.group(1).strip(), num))
                last_chapter_num_in_book = num
    return out


def segment_into_chapters(lines: list[str]) -> list[dict]:
    """Agrupa as linhas em capítulos. Cada capítulo tem livro_num + cap_num + texto.

    Lógica:
    - Mantém um livro_atual (inicial = 1 se não houver marker BOOK/SECTION antes do
      primeiro Part/CHAPTER).
    - Cada marker BOOK ou SECTION atualiza livro_atual.
    - Cada marker Part ou CHAPTER inicia um novo capítulo.
    - Se não houver Part/CHAPTER markers em uma obra, a obra inteira vira L01-C01.
    """
    markers = find_markers(lines)
    if not markers:
        # nenhuma estrutura — devolve a obra como capítulo único
        return [{
            "livro_num": 1, "livro_marker": "BOOK I (inferido)",
            "capitulo_num": 1, "capitulo_marker": "Part 1 (inferido)",
            "start_line": 0, "end_line": len(lines), "text": "\n".join(lines).strip(),
        }]

    chapters: list[dict] = []
    current_book_num = 1
    current_book_marker = "BOOK I (inferido)"
    pending_chapter: dict | None = None

    has_chapter_marker = any(k in ("part", "chapter") for _, k, _, _ in markers)
    if not has_chapter_marker:
        # só BOOK markers — cada bloco vira um capítulo (L{NN}-C01) por simplicidade
        book_markers = [m for m in markers if m[1] in ("book", "section")]
        for idx, (line_idx, kind, raw, num) in enumerate(book_markers):
            next_line = book_markers[idx + 1][0] if idx + 1 < len(book_markers) else len(lines)
            text = "\n".join(lines[line_idx + 1:next_line]).strip()
            chapters.append({
                "livro_num": num or (idx + 1),
                "livro_marker": raw,
                "capitulo_num": 1,
                "capitulo_marker": f"{raw} (sem CHAPTER)",
                "start_line": line_idx,
                "end_line": next_line,
                "text": text,
            })
        return chapters

    # caso geral: BOOK markers definem o livro, Part/CHAPTER markers definem o capítulo
    for idx, (line_idx, kind, raw, num) in enumerate(markers):
        if kind in ("book", "section"):
            current_book_num = num or (current_book_num + 1)
            current_book_marker = raw
            continue
        # Part ou Chapter — fecha o capítulo pendente
        if pending_chapter is not None:
            pending_chapter["end_line"] = line_idx
            pending_chapter["text"] = "\n".join(
                lines[pending_chapter["start_line"] + 1:line_idx]).strip()
            chapters.append(pending_chapter)
        # Calcula cap_num: se num é None, usa sequencial dentro do livro
        cap_num = num
        if cap_num is None:
            existing_in_book = [c for c in chapters if c["livro_num"] == current_book_num]
            cap_num = len(existing_in_book) + 1
        pending_chapter = {
            "livro_num": current_book_num,
            "livro_marker": current_book_marker,
            "capitulo_num": cap_num,
            "capitulo_marker": raw,
            "start_line": line_idx,
        }
    # fecha o último
    if pending_chapter is not None:
        pending_chapter["end_line"] = len(lines)
        pending_chapter["text"] = "\n".join(
            lines[pending_chapter["start_line"] + 1:]).strip()
        chapters.append(pending_chapter)

    return chapters


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[áàâãä]", "a", s)
    s = re.sub(r"[éèêë]", "e", s)
    s = re.sub(r"[íìîï]", "i", s)
    s = re.sub(r"[óòôõö]", "o", s)
    s = re.sub(r"[úùûü]", "u", s)
    s = re.sub(r"[ç]", "c", s)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def write_chapter_file(out_dir: Path, ch: dict, *, item: dict, total_books: int,
                       total_chs_in_book: int) -> Path:
    fname = f"L{ch['livro_num']:02d}-C{ch['capitulo_num']:02d}.md"
    path = out_dir / fname
    frontmatter = (
        "---\n"
        f"obra_pt: {json.dumps(item['titulo_pt'], ensure_ascii=False)}\n"
        f"obra_en: {json.dumps(item['titulo_en'], ensure_ascii=False)}\n"
        f"categoria: {item['categoria']}\n"
        f"obra_slug: {item['obra']}\n"
        f"fonte: {item['fonte']}\n"
        f"livro_num: {ch['livro_num']}\n"
        f"livro_marker: {json.dumps(ch['livro_marker'])}\n"
        f"total_livros: {total_books}\n"
        f"capitulo_num: {ch['capitulo_num']}\n"
        f"capitulo_marker: {json.dumps(ch['capitulo_marker'])}\n"
        f"total_capitulos_no_livro: {total_chs_in_book}\n"
        f"bytes: {len(ch['text'])}\n"
        f"chars_aprox: {len(ch['text'])}\n"
        "---\n\n"
    )
    body = ch["text"].rstrip() + "\n"
    path.write_text(frontmatter + body, encoding="utf-8")
    return path


def process_item(item: dict, *, dry_run: bool, shared_dirs: set[str]) -> dict:
    raw_rel = item["txt_path"]
    raw_path = PROJECT_ROOT / raw_rel
    # Procurar versão clean
    clean_path = raw_path.parent.parent / "clean" / raw_path.name
    if not clean_path.exists():
        return {"obra": item["obra"], "titulo_pt": item["titulo_pt"],
                "status": "missing_clean", "clean_path": str(clean_path.relative_to(PROJECT_ROOT))}

    capitulos_dir = raw_path.parent.parent / "capitulos"
    text = clean_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    chapters = segment_into_chapters(lines)

    # Se vários itens (sub-obras) escrevem no mesmo diretório capitulos/,
    # prefixa cada arquivo com o slug da sub-obra para evitar colisão.
    dir_key = f"{item['categoria']}/{item['obra']}"
    is_shared_dir = dir_key in shared_dirs
    sub_slug = slugify(item["titulo_en"]) if is_shared_dir else None

    total_books = len({c["livro_num"] for c in chapters})
    books_counter: dict[int, int] = {}
    for c in chapters:
        books_counter[c["livro_num"]] = books_counter.get(c["livro_num"], 0) + 1

    if dry_run:
        return {"obra": item["obra"], "titulo_pt": item["titulo_pt"],
                "status": "dry_run", "n_chapters": len(chapters),
                "n_books": total_books,
                "books_breakdown": {str(k): v for k, v in sorted(books_counter.items())}}

    capitulos_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for ch in chapters:
        if sub_slug:
            # arquivo personalizado para Parva Naturalia
            fname = f"{sub_slug}-L{ch['livro_num']:02d}-C{ch['capitulo_num']:02d}.md"
            path = capitulos_dir / fname
            frontmatter = (
                "---\n"
                f"obra_pt: {json.dumps(item['titulo_pt'], ensure_ascii=False)}\n"
                f"obra_en: {json.dumps(item['titulo_en'], ensure_ascii=False)}\n"
                f"categoria: {item['categoria']}\n"
                f"obra_slug: {item['obra']}\n"
                f"sub_obra: {sub_slug}\n"
                f"fonte: {item['fonte']}\n"
                f"livro_num: {ch['livro_num']}\n"
                f"livro_marker: {json.dumps(ch['livro_marker'])}\n"
                f"capitulo_num: {ch['capitulo_num']}\n"
                f"capitulo_marker: {json.dumps(ch['capitulo_marker'])}\n"
                f"bytes: {len(ch['text'])}\n"
                "---\n\n"
            )
            path.write_text(frontmatter + ch["text"].rstrip() + "\n", encoding="utf-8")
        else:
            path = write_chapter_file(
                capitulos_dir, ch, item=item,
                total_books=total_books,
                total_chs_in_book=books_counter[ch["livro_num"]],
            )
        written.append(str(path.relative_to(PROJECT_ROOT)))

    return {"obra": item["obra"], "titulo_pt": item["titulo_pt"],
            "categoria": item["categoria"],
            "status": "ok", "n_chapters": len(chapters),
            "n_books": total_books,
            "books_breakdown": {str(k): v for k, v in sorted(books_counter.items())},
            "files": written[:3] + (["..."] if len(written) > 3 else [])}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DOWNLOAD_MANIFEST.exists():
        print(f"ERRO: {DOWNLOAD_MANIFEST} não encontrado.")
        return 2

    manifest = json.loads(DOWNLOAD_MANIFEST.read_text(encoding="utf-8"))
    items = [r for r in manifest["results"] if r["status"].startswith(("ok", "cached"))]
    if args.only:
        items = [r for r in items if args.only.lower() in r["categoria"].lower()
                 or args.only.lower() in r["obra"].lower()]

    # Pré-detecta diretórios compartilhados por >1 obra (ex: parva_naturalia,
    # 03_magna_moralia que recebe Magna + Virtues)
    from collections import Counter
    dir_counter = Counter(f"{it['categoria']}/{it['obra']}" for it in items)
    shared_dirs = {k for k, n in dir_counter.items() if n > 1}

    results = []
    total_chapters_all = 0
    for i, it in enumerate(items, 1):
        res = process_item(it, dry_run=args.dry_run, shared_dirs=shared_dirs)
        marker = f"[{i:02d}/{len(items)}] {it['categoria']}/{it['obra']:30s}"
        if res["status"].startswith(("ok", "dry_run")):
            marker += f" → {res['n_books']:2d} livros, {res['n_chapters']:3d} cap."
            total_chapters_all += res["n_chapters"]
        else:
            marker += f" → {res['status']}"
        print(marker)
        results.append(res)

    print(f"\n=== TOTAL: {total_chapters_all} capítulos em {len(items)} obras ===")

    if not args.dry_run:
        out_manifest = PROJECT_ROOT / "_raw" / "segment_manifest.json"
        out_manifest.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_obras": len(results),
            "total_chapters": total_chapters_all,
            "ok": sum(1 for r in results if r["status"] == "ok"),
            "results": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Manifesto: {out_manifest.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
