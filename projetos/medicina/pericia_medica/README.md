# Perícia Médica — Biblioteca de Referência (NotebookLM, conta pessoal)

- **Notebook:** `1af19855-4523-4ba9-8837-343f474a2a83` — https://notebooklm.google.com/notebook/1af19855-4523-4ba9-8837-343f474a2a83
- **Conteúdo:** os 84 livros de `~/dev/_ref/docling-projeto/projects/pericia/` em **157 fontes** (livros > 400 mil palavras fatiados; maior parte 436.565 palavras; teto do NotebookLM = 500 mil). Plano Pro (limite 300 fontes).
- **Para quem:** colega perito, como **Leitor**. Guia de acesso para imprimir: `Guia_acesso_biblioteca_pericia.docx`.
- **Tarefa:** `notebooklm_edson-r4oq`.

## Arquivos

| Arquivo | O que é |
|---|---|
| `catalogo.json` | 84 livros: slug no docling-projeto, área (grupo) e título legível da fonte |
| `notebook_fontes.json` | registro do que subiu: título, `source_id`, caminho do `.md` enviado. Protegido por `docling-projeto/tools/check_notebooklm_sources.py` |
| `Guia_acesso_biblioteca_pericia.docx` | passo a passo para o colega (entrar, perguntar, voltar, cuidados) |

## Como foi montado (2026-09-14)

```bash
NLMPY=~/.local/share/uv/tools/notebooklm-mcp-cli/bin/python3
cd ~/dev/notebooklm_edson/projetos/medicina/pericia_medica
$NLMPY ~/dev/notebooklm_michalk/tools/criar_notebook_de_acervo.py --catalogo catalogo.json \
  --area pericia --prefixo-slug x- --titulo "Perícia Médica — Biblioteca de Referência" \
  --prefixo-fonte GRUPO --perfil default [--dry-run | --retry]
```

Auditoria antes do envio: 83/84 livros completos e legíveis (amostragem de 20 páginas PDF×md por
4-gramas; EPUBs por contagem de palavras). O Adams y Victor tinha só 60% do texto e foi reconstruído
na origem (`docling-projeto-d1v`). Uma fonte falhou por abrir com `<!-- image -->` — corrigido na
ferramenta.

## Pendências conhecidas

- Obras repetidas mantidas por decisão ("todas as fontes"): Wall & Melzack EN+ES, Spitz & Fisher EN+ES,
  Histology (Ross) EN+PT, Delton Croce EPUB+PDF, Modi ×2, Simpson's ×2.
- Modern Epidemiology: ~700 fórmulas não decodificadas pelo Docling. Best & Taylor: marca d'água repetida.
- O NotebookLM não mostra página; para citar em laudo, localizar o trecho no PDF original.
- Já existe outro notebook de perícia na conta pessoal: "Tratado Técnico e Jurídico da Perícia Médica Brasileira" (`e5f0fdb9`, 31 fontes).
