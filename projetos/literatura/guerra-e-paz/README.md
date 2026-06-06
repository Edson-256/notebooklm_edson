# Projeto: Guerra e Paz

- **Fonte:** Leon Tolstoi (EPUB)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 24 em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --level 1`

Dividido por heading H1 (partes/livros); o TOC plano misturava front matter.

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_epub.py --write --level 1
```
