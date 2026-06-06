# Projeto: Os Miseráveis

- **Fonte:** Victor Hugo (EPUB)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 8 em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --level 1`

Dividido pelas 5 partes (H1). O TOC tinha 419 entradas (partes+livros+capítulos achatados) — split por capítulo geraria 365 arquivos.

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_epub.py --write --level 1
```
