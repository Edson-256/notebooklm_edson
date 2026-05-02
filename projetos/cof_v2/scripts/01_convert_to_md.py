#!/usr/bin/env python3
"""
Converte transcrições do COF (PDF + DOCX) para markdown.

Roda no dell-server (100.71.148.95).
Saída: /home/edson/dev/cof/data/_md/
  - cof_original_transcricoes/Aula_NNN-YYYY-MM-DD.md
  - cof_original_livros/<nome>.md
  - cof_remasterizado_transcricoes/Aula_NNN-YYYY-MM-DD.md
  - cof_remasterizado_livros/<nome>.md
  - extracurriculares/<curso>__Unif.md
"""
import sys, re, json
from pathlib import Path
from datetime import datetime

import fitz  # pymupdf
import docx  # python-docx

SRC = Path("/home/edson/dev/cof/data")
OUT = SRC / "_md"
LOG = OUT / "_conversion_log.json"


def pdf_to_md(p: Path) -> str:
    """Extrai texto de PDF preservando quebras de página."""
    doc = fitz.open(p)
    parts = []
    for page in doc:
        txt = page.get_text("text").strip()
        if txt:
            parts.append(txt)
    doc.close()
    return "\n\n".join(parts)


def docx_to_md(p: Path) -> str:
    d = docx.Document(p)
    return "\n\n".join(par.text for par in d.paragraphs if par.text.strip())


def convert_one(src: Path, dst: Path) -> dict:
    info = {'src': str(src), 'dst': str(dst), 'ok': False}
    try:
        if src.suffix.lower() == '.pdf':
            text = pdf_to_md(src)
        elif src.suffix.lower() == '.docx':
            text = docx_to_md(src)
        elif src.suffix.lower() in ('.txt', '.md'):
            text = src.read_text(encoding='utf-8', errors='replace')
        else:
            info['error'] = f'unsupported ext: {src.suffix}'
            return info
        # Header com metadata simples
        header = f"<!-- src: {src.name} | size: {len(text)} chars | converted: {datetime.now().isoformat()} -->\n\n"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(header + text, encoding='utf-8')
        info['ok'] = True
        info['chars'] = len(text)
        info['words'] = len(text.split())
    except Exception as e:
        info['error'] = repr(e)
    return info


def stem_to_md(name: str) -> str:
    return Path(name).stem + ".md"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    counters = {'ok': 0, 'fail': 0}

    plan = [
        # (src_subdir, dst_subdir, glob)
        ('COF Original/transcricoes', 'cof_original_transcricoes', '*.pdf'),
        ('COF Original/transcricoes', 'cof_original_transcricoes', '*.docx'),
        ('COF Original/livros',       'cof_original_livros',       '*.pdf'),
        ('COF Original/livros',       'cof_original_livros',       '*.docx'),
        ('COF Remasterizado/transcricoes', 'cof_remasterizado_transcricoes', '*.pdf'),
        ('COF Remasterizado/transcricoes', 'cof_remasterizado_transcricoes', '*.docx'),
        ('COF Remasterizado/livros',       'cof_remasterizado_livros',       '*.pdf'),
        ('COF Remasterizado/livros',       'cof_remasterizado_livros',       '*.docx'),
    ]

    for src_sub, dst_sub, pat in plan:
        src_dir = SRC / src_sub
        if not src_dir.exists():
            continue
        files = sorted(src_dir.glob(pat))
        for i, f in enumerate(files, 1):
            dst = OUT / dst_sub / stem_to_md(f.name)
            if dst.exists():
                continue  # idempotent
            info = convert_one(f, dst)
            log.append(info)
            counters['ok' if info['ok'] else 'fail'] += 1
            if (i % 50) == 0:
                print(f"[{src_sub}] {i}/{len(files)} ({counters})")

    # Extracurriculares: só Unif_*
    ext_root = SRC / "extracurriculares"
    for course_dir in sorted(ext_root.iterdir()):
        if not course_dir.is_dir():
            continue
        editados = course_dir / "editados"
        if not editados.exists():
            continue
        unif = sorted(editados.glob("Unif_*"))
        for u in unif:
            dst = OUT / "extracurriculares" / f"{course_dir.name}__{stem_to_md(u.name)}"
            if dst.exists():
                continue
            info = convert_one(u, dst)
            log.append(info)
            counters['ok' if info['ok'] else 'fail'] += 1

    LOG.write_text(json.dumps({'counters': counters, 'log': log}, ensure_ascii=False, indent=2),
                   encoding='utf-8')
    print(f"\nDone: {counters}")
    print(f"Log: {LOG}")


if __name__ == "__main__":
    main()
