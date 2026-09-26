# Perícia Médica — Biblioteca de Referência (NotebookLM, conta pessoal)

- **Notebook:** `1af19855-4523-4ba9-8837-343f474a2a83` — https://notebooklm.google.com/notebook/1af19855-4523-4ba9-8837-343f474a2a83
- **Conteúdo:** os 84 livros de `~/dev/_ref/docling-projeto/projects/pericia/` em **157 fontes** (livros > 400 mil palavras fatiados; maior parte 436.565 palavras; teto do NotebookLM = 500 mil). Plano Pro (limite 300 fontes).
- **Para quem:** colega perito, como **Leitor**. Guia de acesso para imprimir: `Guia_acesso_biblioteca_pericia.docx`.
- **Tarefa:** `notebooklm_edson-r4oq` (montagem) · `notebooklm_edson-ll06` (camada atual 2026).
- **Total em 2026-09-26:** 235 fontes = 157 dos livros + **78 "Atual 2026"** (normas vigentes, precedentes, protocolos oficiais, consensos).

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

## Camada "Atual 2026" (2026-09-26)

Um mesmo prompt de deep research foi submetido ao ChatGPT, a um agente Claude na nuvem e ao Deep
Research do NotebookLM (Gemini). Consolidação em `deep_research/04_consolidacao/CONSOLIDACAO.md`
(179 achados → 83 selecionadas → **78 inseridas**; motivo de cada descarte em
`decisao_por_fonte.csv`). Títulos no notebook começam por **"Atual 2026 · <área> ·"**.

- As normas-chave de 2025–2026 foram lidas no DOU/texto oficial (Atestmed PC 13, 14 e 43/2026; Res.
  CFM 2.430/2025; CNJ 595/2024 compilada; LC 211/2024). O NotebookLM e o ChatGPT erraram o teto do
  Atestmed e o NotebookLM ofereceu duas resoluções do CFM revogadas — ver a tabela de divergências.
- 35 fontes entraram como **arquivo** (`deep_research/05_arquivos_enviados/NN.md`) porque Planalto,
  DOU, STJ, STF e PMC bloqueiam o leitor do NotebookLM. No Planalto o texto tachado (redação
  revogada) foi removido antes do envio. **Isso congela o texto em 2026-09-26** — lei alterada
  depois exige reenviar o arquivo.
- Fora por falta de texto aberto: AACN 2021 (consenso de validade), IASP (dor crônica na CID-11),
  EULAR fibromialgia; e a Portaria Interministerial 1/2014 (IF-BrA), cujo DOU bloqueia download.
  O Tema 343 da TNU já está dentro do Repositório TNU.

## Acesso do colega (2026-09-26)

Convidado como **Leitor** (`nlm share invite`, perfil default; acesso restrito, sem link público).
Configurado presencialmente pelo Edson na casa do colega. **Confirmado:** o colega abriu o notebook
e fez perguntas com sucesso — um leitor sem plano pago consegue usar um notebook de 235 fontes.
(E-mail do colega não registrado aqui: repositório público.)

## Pendências conhecidas

- Obras repetidas mantidas por decisão ("todas as fontes"): Wall & Melzack EN+ES, Spitz & Fisher EN+ES,
  Histology (Ross) EN+PT, Delton Croce EPUB+PDF, Modi ×2, Simpson's ×2.
- Modern Epidemiology: ~700 fórmulas não decodificadas pelo Docling. Best & Taylor: marca d'água repetida.
- O NotebookLM não mostra página; para citar em laudo, localizar o trecho no PDF original.
- Já existe outro notebook de perícia na conta pessoal: "Tratado Técnico e Jurídico da Perícia Médica Brasileira" (`e5f0fdb9`, 31 fontes).
