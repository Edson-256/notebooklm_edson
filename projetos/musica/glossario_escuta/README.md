# Glossário técnico em cascata — base de fontes (NotebookLM, conta pessoal)

- **Para quê:** fontes para os verbetes em três camadas (em palavras · termo técnico traduzido ·
  teoria) que a sessão `musica_composicao` vai escrever e ligar ao app de escuta. **Sem áudio.**
  Pauta: `~/dev/_pessoal/musica_composicao/catalogo/escuta/PAUTA_PESQUISA_GLOSSARIO.md`.
- **Tarefa:** `notebooklm_edson-mmf9` (deste lado) · `musica_composicao-m6wl` (do lado de lá).
- **Notebook:** o mesmo da pesquisa 1, `4ac56794-d00a-436a-a446-24f1161cd9bd` — **138 fontes "Gloss ·"** (#1–#101 em 02/10; #102–#105 resgates e #106–#138 do council_llm em 03/10). Fontes desta pesquisa
  entram com o prefixo `Gloss ·` no título (as da pesquisa 1 têm `EpNN ·`).
- **Método:** igual ao de `../teoria_escuta_critica/` — três pesquisadores (ChatGPT, agente Claude,
  Deep Research do NotebookLM) → consolidação com decisão e motivo por fonte (CSV) → aprovação do
  Edson → notebook.

## Pastas

| Caminho | O que é |
|---|---|
| `deep_research/00_PROMPT_deep_research.md` | prompt único (inglês → saída pt-BR) + versões condensadas do NotebookLM |
| `deep_research/01_chatgpt/resultado.md` | resultado do ChatGPT (o Edson cola) |
| `deep_research/02_claude_agent/resultado.md` | resultado do agente Claude |
| `deep_research/03_notebooklm_gemini/` | relatórios das duas rodadas do Deep Research do NotebookLM |
| `deep_research/04_consolidacao/CONSOLIDACAO.md` | **comece por aqui**: divergências conferidas, mapa de confusões, pendências, seleção por família |
| `deep_research/04_consolidacao/decisao_por_fonte.csv` | decisão e motivo das 170 linhas brutas |
| `deep_research/04_consolidacao/selecionadas.json` | as 101 selecionadas (url, família, prioridade, nota, `arquivo` quando sobe como arquivo) |
| `deep_research/04_consolidacao/juntar.py`, `consolidar.py` | geram `_bruto.json` e os dois arquivos acima |
| `deep_research/05_arquivos_enviados/` | PDFs que o servidor não entrega a leitor automático (fora do git; rebaixáveis pela URL) |

## Carga no notebook (2026-10-02)

- `04_consolidacao/inserir.py` (idempotente) → `adicionadas.jsonl` (source_id e palavras por fonte). Título: `Gloss · <família> · <título>`.
- Subiram como arquivo: 13 capítulos do Open Music Theory/Pressbooks (.md), as teses de Corrêa, Vilela e Castela, Wolffenbüttel (.md) e
  três PDFs cujo link o NotebookLM recusou (Ferraz, Grecco, Mazo).
- Para usar só o glossário numa consulta, selecione no notebook as fontes que começam com `Gloss ·` (ou `Gloss · F2` para uma família).
