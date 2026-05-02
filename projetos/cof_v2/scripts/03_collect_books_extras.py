#!/usr/bin/env python3
"""
Reúne em compiladas/ todos os livros, Unif_* e compilações temáticas
necessárias para upload no novo notebook NLM.

Saídas:
  compiladas/livros/<nome>.md            (livros do disco já convertidos)
  compiladas/livros/<nome do PDF>.md     (livros do notebook atual, convertidos)
  compiladas/extracurriculares/<curso>__Unif.md
  compiladas/aulas/COF-Tematicas-*.md    (4 compilações temáticas do notebook)
"""
import re, shutil, json
from pathlib import Path
import fitz  # pymupdf

ROOT = Path(__file__).parent.parent
RAW = ROOT / "_raw"
DELL = RAW / "dell_md"
OUT_LIVROS = ROOT / "compiladas/livros"
OUT_EXTRA = ROOT / "compiladas/extracurriculares"
OUT_AULAS = ROOT / "compiladas/aulas"

OUT_LIVROS.mkdir(parents=True, exist_ok=True)
OUT_EXTRA.mkdir(parents=True, exist_ok=True)
OUT_AULAS.mkdir(parents=True, exist_ok=True)


def strip_md_header(text: str) -> str:
    return re.sub(r'^<!--.*?-->\n+', '', text, count=1, flags=re.DOTALL)


def pdf_to_md(p: Path) -> str:
    doc = fitz.open(p)
    parts = [page.get_text("text").strip() for page in doc]
    doc.close()
    return "\n\n".join(p for p in parts if p)


def slug(name: str) -> str:
    name = re.sub(r'\.(pdf|docx|txt)$', '', name, flags=re.IGNORECASE)
    return name.strip()


# ── 1. Livros do disco (já convertidos) ───────────────────────────────
print("== Livros do disco ==")
livros_disk_count = 0
for src in sorted((DELL / "cof_original_livros").glob("*.md")):
    name = slug(src.name) + ".md"
    dst = OUT_LIVROS / name
    text = strip_md_header(src.read_text(encoding='utf-8', errors='replace'))
    title_h = f"# {slug(src.name)}\n\n*Fonte: COF Original / livros*\n\n---\n\n"
    dst.write_text(title_h + text.strip(), encoding='utf-8')
    livros_disk_count += 1
for src in sorted((DELL / "cof_remasterizado_livros").glob("*.md")):
    name = slug(src.name) + " (remasterizado).md"
    dst = OUT_LIVROS / name
    text = strip_md_header(src.read_text(encoding='utf-8', errors='replace'))
    title_h = f"# {slug(src.name)}\n\n*Fonte: COF Remasterizado / livros*\n\n---\n\n"
    dst.write_text(title_h + text.strip(), encoding='utf-8')
    livros_disk_count += 1
print(f"  → {livros_disk_count} livros do disco")

# ── 2. Livros que estavam SÓ no notebook (PDFs, converter aqui) ──────
print("== Livros do notebook (converter PDFs) ==")
livros_nb_count = 0
for src in sorted((RAW / "livros_notebook").iterdir()):
    if not src.is_file():
        continue
    # Esses arquivos foram baixados via `nlm source content` — pode ser texto
    # extraído (não PDF binário) com extensão .pdf no nome. Tentar abrir como PDF
    # e cair para leitura como texto se falhar.
    try:
        text = pdf_to_md(src)
        if not text.strip():
            raise RuntimeError("empty pdf body")
    except Exception:
        text = src.read_text(encoding='utf-8', errors='replace')
    name = slug(src.name) + ".md"
    dst = OUT_LIVROS / name
    title_h = f"# {slug(src.name)}\n\n*Fonte: notebook NLM (livro Olavo)*\n\n---\n\n"
    dst.write_text(title_h + text.strip(), encoding='utf-8')
    livros_nb_count += 1
print(f"  → {livros_nb_count} livros do notebook")

# ── 3. Extracurriculares (Unif_*) ─────────────────────────────────────
print("== Extracurriculares (Unif_*) ==")
unif_count = 0
for src in sorted((DELL / "extracurriculares").glob("*.md")):
    text = strip_md_header(src.read_text(encoding='utf-8', errors='replace'))
    # nome: Curso__Unif_XYZ.md → "Unif - Curso.md"
    raw = src.stem
    parts = raw.split('__', 1)
    if len(parts) == 2:
        curso = parts[0]
        title = f"COF Extracurricular — {curso}"
    else:
        title = raw
    fname = title.replace('/', '_') + ".md"
    dst = OUT_EXTRA / fname
    title_h = f"# {title}\n\n*Fonte: extracurriculares (transcrição editada/unificada)*\n\n---\n\n"
    dst.write_text(title_h + text.strip(), encoding='utf-8')
    unif_count += 1
print(f"  → {unif_count} cursos extracurriculares")

# ── 4. Compilações temáticas do notebook (.md já) ────────────────────
print("== Compilações temáticas do notebook ==")
tematicas_count = 0
for src in sorted((RAW / "tematicas_notebook").iterdir()):
    if not src.is_file():
        continue
    text = src.read_text(encoding='utf-8', errors='replace')
    name = src.name
    # Renomear: Aulas_Olavo_-_COF_-_Apostilas → COF-Tematicas-Apostilas
    m = re.match(r'^Aulas_Olavo_-_COF_-_(.+?)\.md$', name)
    if m:
        title = f"COF-Tematicas-{m.group(1).replace('_', '-')}"
    else:
        title = name.replace('.md','')
    dst = OUT_AULAS / f"{title}.md"
    title_h = f"# {title}\n\n*Fonte: compilação temática originalmente no notebook NLM (mantida sem reedição)*\n\n---\n\n"
    dst.write_text(title_h + text.strip(), encoding='utf-8')
    tematicas_count += 1
print(f"  → {tematicas_count} compilações temáticas")

# ── Resumo e manifest ────────────────────────────────────────────────
manifest = {
    'livros_disco': livros_disk_count,
    'livros_notebook': livros_nb_count,
    'extracurriculares_unif': unif_count,
    'tematicas_notebook': tematicas_count,
}
print(f"\nResumo: {manifest}")
(ROOT / "compiladas/_extras_manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
