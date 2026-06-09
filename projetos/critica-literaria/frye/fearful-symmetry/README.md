# Projeto: Fearful Symmetry

- **Fonte:** Northrop Frye, *Fearful Symmetry: A Study of William Blake*. EPUB inglês.
- **Origem:** `~/dev/_ref/livros/Northrop Frye/`
- **Status:** ✅ concluído (sem OCR)
- **Idioma:** inglês
- **Texto integral:** `output/Fearful-Symmetry.md` (~190,7k palavras ≈ 100% do EPUB) — gerado via `--single`.
- **Capítulos:** 12 em `output/chapters/` (C001–C012, os 12 capítulos do livro) — gerados via `--spine` (TOC/ncx).
- **Imagens:** 42 em `output/images/`.

⚠️ O EPUB **não tem headings** (`--level` impossível). O `--spine` (ncx) captura os
12 capítulos mas só **90,9%** das palavras (capa, rosto, copyright, índice e
bibliografia ficam fora do ncx). Por isso o **texto integral** usa `--single`
(documento inteiro, 100%) e os **capítulos** usam `--spine`. O `output/images/`
contém as duas nomeações de imagem (basename p/ o md integral, `C{nnn}_*` p/ os
capítulos).

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
# 1) capítulos (spine)
python ../../../tools/convert_epub.py --write --spine
# 2) preservar capítulos+imagens, gerar integral (--single sobrescreve output/), restaurar
cp -R output/chapters /tmp/fs_ch && cp -R output/images /tmp/fs_img
python ../../../tools/convert_epub.py --write --single
mv "output/Fearful Symmetry - Northrop Frye.md" output/Fearful-Symmetry.md
rm -rf output/chapters && cp -R /tmp/fs_ch output/chapters
cp /tmp/fs_img/* output/images/ ; rm -rf /tmp/fs_ch /tmp/fs_img
```
