# Projeto: Os Irmãos Karamázov (edição alternativa)

- **Fonte:** Fiódor Dostoiévski (EPUB)
- **Origem:** mbookpro (`~/Downloads`), baixado 2026-06-05
- **Status:** ✅ concluído (documento único)
- **Saída:** `output/<livro>.md` (1 arquivo, ~363k palavras)
- **Método:** `python ../../../tools/convert_epub.py --write --single`

⚠️ **Edição duplicada** de `os-irmaos-karamazov-ed34` (mesma obra). O `--spine`
desta edição capturava só 42% (ncx parcial) e não há headings utilizáveis para
`--level`. Convertido como **documento único** (sem perda). **Para a versão
dividida em capítulos/livros, use `os-irmaos-karamazov-ed34` (21 partes).**

## Reprocessar
```bash
python ../../../tools/convert_epub.py --write --single
```
