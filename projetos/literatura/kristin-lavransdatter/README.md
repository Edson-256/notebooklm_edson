# Projeto: Kristin Lavransdatter

- **Fonte:** Sigrid Undset (EPUB, Penguin Classics) — trilogia
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído
- **Capítulos:** 67 + FrontMatter em `output/chapters/`
- **Método:** `python ../../../tools/convert_epub.py --write --level 1`

⚠️ O `--spine` capturava só **2,4%** do livro (o ncx desta edição lista apenas
seções, não os arquivos de conteúdo). Corrigido com `--level 1` (H1=67), que
divide sobre o documento inteiro — captura 100%.

## Reprocessar
```bash
python ../../../tools/convert_epub.py --write --level 1
```
