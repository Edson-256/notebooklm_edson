# Teoria musical para escuta crítica (NotebookLM, conta pessoal)

- **Notebook:** `4ac56794-d00a-436a-a446-24f1161cd9bd` — https://notebooklm.google.com/notebook/4ac56794-d00a-436a-a446-24f1161cd9bd
- **Para quê:** base para o Edson avaliar ~850 músicas geradas no Suno (a partir de obras literárias) com a
  ficha de escuta por camadas da ferramenta do repo `musica_composicao`; e série de 10 áudios em pt-BR
  para ouvir offline no voo de 07/10/2026. Pedido da sessão `musica-composicao-71`.
- **Tarefa:** `notebooklm_edson-c0x3`.
- **Fontes:** 134 no notebook (135 aprovadas pelo Edson em 2026-09-28; 1 inacessível). Título no notebook
  = `EpNN · <título>` — cada episódio usa só as fontes com o seu prefixo.

## Pastas

| Caminho | O que é |
|---|---|
| `deep_research/00_PROMPT_deep_research.md` | prompt único (inglês → saída pt-BR) + versões condensadas do NotebookLM |
| `deep_research/01_chatgpt/` | resultado do ChatGPT (o export perdeu os links) + `urls_recuperadas.csv` (links achados pelo título) |
| `deep_research/02_claude_agent/`, `03_notebooklm_gemini/` | resultados dos outros dois pesquisadores |
| `deep_research/04_consolidacao/CONSOLIDACAO.md` | seleção por episódio, divergências, lacunas, livros a comprar |
| `deep_research/04_consolidacao/decisao_por_fonte.csv` | decisão e motivo das 232 linhas brutas |
| `deep_research/04_consolidacao/selecionadas.json` | as 135 aprovadas (url, prioridade, item da ficha, episódio `ep`) |
| `deep_research/05_arquivos_enviados/` | fontes subidas como arquivo (PMC → .md; PDFs fora do git) |
| `episodios/prompts_episodios.md` | prompts de foco dos 10 episódios (bloco COMMON + um por episódio) |
| `episodios/gerar_episodios.py` | `--checar` · `--criar N…` · `--status` · `--baixar`; estado em `estado.json` |

## Armadilhas encontradas (2026-09-28)

- **PMC:** o NotebookLM recebe captcha (~67 palavras, título "Checking your browser"). Subir o texto como
  `.md` via `04_consolidacao/pmc_para_md.py` (Europe PMC, com queda para a E-utilities do NCBI).
- **Pressbooks, The Conversation, OpenBook, Hrčak, BMC:** recusam o leitor; baixar e subir como arquivo
  (Wayback quando o site bloqueia o curl também).
- **Página de resumo (arXiv `abs`, OJS, Zenodo):** entra só o resumo; usar o PDF (`achar_pdf.py`).
- **`nlm source rename` exige `--notebook`** na versão atual do nlm; sem ele falha em silêncio dentro do script.
- **Dois lotes simultâneos** duplicaram fontes — um `pgrep -f` com padrão errado deu "não está rodando".
