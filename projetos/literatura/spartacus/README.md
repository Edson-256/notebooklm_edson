# Projeto: Spartacus

- **Fonte:** Howard Fast (EPUB)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 9 em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --level 1`

Dividido pelas 5 partes (H1); o depth1 do TOC tinha 67 capítulos minúsculos.

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_epub.py --write --level 1
```
