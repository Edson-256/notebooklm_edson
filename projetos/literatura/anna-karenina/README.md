# Projeto: Anna Kariênina

- **Fonte:** Leon Tolstoi (PDF, fonte sem ToUnicode → exigiu OCR de página inteira)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 8 partes em `output/chapters/` (+ FrontMatter)
- **Método:** `python ../../../tools/convert_ocr.py --force 6`

O texto-fonte do PDF é gibberish (fonte sem ToUnicode); sem `--force` o Docling
reaproveita esse texto quebrado e o md sai ilegível. Com `--force`
(force_full_page_ocr) o OCR lê a página inteira → texto perfeito. Sem outline:
dividido pelas 8 partes (headings `## … PARTE` do md OCR).

## Reprocessar

De dentro desta pasta, com o venv ativo (`source ../../../.venv/bin/activate`):

```bash
python ../../../tools/convert_ocr.py --force 6   # PDF -> output/<livro>.md (OCR página inteira)
# depois: split pelas 8 partes (## ... PARTE) -> output/chapters/
```
