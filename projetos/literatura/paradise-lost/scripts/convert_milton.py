#!/usr/bin/env python3
r"""
Paradise Lost (John Milton) — EPUB Feedbooks -> capítulos em output/chapters/.

Por que script próprio (e não tools/convert_epub.py):
  - O EPUB Feedbooks marca os 12 livros como `# Part N {style="text-align: center;"}`.
  - convert_epub.py usa pandoc `-t gfm`, que NÃO preserva esses headings centralizados
    (viram texto solto `Part N\`), então `--level` não os detecta (dry-run viu H1=1).
  - O `--spine` (ncx) aponta para xhtml quase vazios -> perda de 99,5% (395/80360 palavras).

Solução: pandoc `-t markdown` (preserva `# Part N` como H1), limpar os fences de div
`:::` do Feedbooks e os atributos `{...}` dos headings, e dividir por `^# `.

Rodar de dentro de projects/literatura/milton/ com o venv ativo:
    python scripts/convert_milton.py
"""

import re, shutil, tempfile, unicodedata, subprocess
from pathlib import Path

SRC = next(Path("source").glob("*.epub"))
OUT = Path("output")
IMG = OUT / "images"
CHAPTERS = OUT / "chapters"


def slugify(t, maxlen=60):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s_]+", "-", t).strip("-")[:maxlen].strip("-") or "sem-titulo"


def convert():
    """pandoc epub -> markdown (texto) + imagens em output/images/. Retorna texto limpo."""
    tmp = tempfile.mkdtemp(prefix="milton_")
    md_tmp = Path(tmp) / "book.md"
    subprocess.run(
        ["pandoc", str(SRC), "-f", "epub", "-t", "markdown", "--wrap=none",
         f"--extract-media={tmp}/media", "-o", str(md_tmp)],
        check=True, capture_output=True,
    )
    txt = md_tmp.read_text(encoding="utf-8")

    # imagens -> output/images, links -> images/<basename>
    IMG.mkdir(parents=True, exist_ok=True)
    media = Path(tmp) / "media"
    if media.exists():
        for f in media.rglob("*"):
            if f.is_file():
                shutil.copy(f, IMG / f.name)
    txt = re.sub(r'\]\(([^)]*?/)?media/([^)]+)\)', r'](images/\2)', txt)
    txt = re.sub(r'src="([^"]*?/)?media/([^"]+)"', r'src="images/\2"', txt)
    shutil.rmtree(tmp, ignore_errors=True)

    out_lines = []
    for line in txt.splitlines():
        s = line.strip()
        if re.match(r'^:{3,}', s):                       # fences de div pandoc (::: / :::::: body)
            continue
        if re.match(r'^\[\]\{#[^}]*\}$', s):             # âncoras vazias []{#about.xml}
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)         # headings: tira atributos {…}
        if m:
            title = re.sub(r'\s*\{[^}]*\}\s*$', '', m.group(2)).strip()
            out_lines.append(f"{m.group(1)} {title}")
            continue
        out_lines.append(line.rstrip())

    txt = "\n".join(out_lines)
    txt = re.sub(r'\\([\'"\[\]])', r'\1', txt)        # desescapa apóstrofos/aspas/colchetes (artefato pandoc-markdown)
    txt = re.sub(r'\n{3,}', '\n\n', txt).strip() + "\n"   # colapsa 3+ linhas em branco -> 1
    return txt


def split_by_h1(txt):
    """Divide por headings `# ` (nível 1): front matter + 12 Parts."""
    lines = txt.splitlines(keepends=True)
    idxs = [i for i, ln in enumerate(lines) if re.match(r'^# \S', ln)]
    if CHAPTERS.exists():
        shutil.rmtree(CHAPTERS)
    CHAPTERS.mkdir(parents=True)
    bounds = idxs + [len(lines)]
    n = 0
    for k in range(len(idxs)):
        chunk = "".join(lines[bounds[k]:bounds[k + 1]]).strip() + "\n"
        title = re.match(r'^# (.*)$', lines[idxs[k]].rstrip()).group(1)
        n += 1
        path = CHAPTERS / f"C{n:03d}-{slugify(title)}.md"
        path.write_text(chunk, encoding="utf-8")
        words = len(chunk.split())
        print(f"  C{n:03d}  {title:<24} {words:>6} palavras  -> {path.name}")
    return n


if __name__ == "__main__":
    print(f"Fonte: {SRC.name}")
    txt = convert()
    total = len(txt.split())
    print(f"Texto limpo: {total} palavras\nCapítulos:")
    n = split_by_h1(txt)
    print(f"\n✅ {n} capítulos em {CHAPTERS}/  ({total} palavras)")
