# Projeto: Crime e Castigo

- **Fonte:** Fiódor Dostoiévski (PDF, texto limpo)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 8 em `output/chapters/`
- **Método:** `python ../../../tools/split_pdf_text.py --write --outline --filter 'parte|ep[ií]logo'`

PDF com camada de texto limpa; dividido pelas 6 partes + epílogo via outline, **sem OCR**.

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/split_pdf_text.py --write --outline --filter 'parte|ep[ií]logo'
```
