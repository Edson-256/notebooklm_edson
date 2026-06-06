# Projeto: Os Irmãos Karamázov (editora 34)

- **Fonte:** Fiódor Dostoiévski (EPUB, ed. 34)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 21 em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --spine`

Dividido pelos 12 livros do TOC + front matter.

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_epub.py --write --spine
```
