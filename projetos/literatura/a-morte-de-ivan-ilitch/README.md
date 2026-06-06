# Projeto: A Morte de Ivan Ilitch

- **Fonte:** Leon Tolstoi (EPUB)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 15 em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --spine`

EPUB sem headings; dividido pelos arquivos-capítulo do TOC (ncx).

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_epub.py --write --spine
```
