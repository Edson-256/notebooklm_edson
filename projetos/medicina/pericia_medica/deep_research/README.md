# Deep research — complementar a biblioteca de Perícia Médica

Tarefa: `notebooklm_edson-ll06` · iniciado 2026-09-26 · notebook `1af19855` (conta pessoal)

## Por que existe

As 157 fontes do notebook são livros-texto. Falta a camada **atual e oficial**: normas em vigor
(texto compilado), manuais da Perícia Médica Federal, resoluções do CFM/CNJ, precedentes
vinculantes, baremos e consensos recentes. Um mesmo prompt foi submetido a três pesquisadores
independentes; o cruzamento dos três reduz o risco de fonte inventada ou revogada.

## Pastas

| Pasta | Conteúdo | Estado |
|---|---|---|
| `00_PROMPT_deep_research.md` | prompt completo (inglês → saída pt-BR) + versão condensada do NotebookLM | pronto |
| `_acervo_atual_84_livros.txt`, `_notebook_irmao_e5f0fdb9_31_fontes.tsv` | o que já temos — base da checagem de duplicidade (anexar no ChatGPT) | pronto |
| `01_chatgpt/` | `resultado.md` — relatório do ChatGPT Deep Research | recebido 2026-09-26 |
| `02_claude_cloud/` | `resultado.md` — relatório do agente Claude na nuvem | concluído 2026-09-26 |
| `03_notebooklm_gemini/` | `relatorio.md` + `fontes_descobertas.tsv` (59 itens; o [0] é o próprio relatório). Task `27ae246d-9f75-44cd-a920-b1b636f127df` — **não importado**; importar depois com `nlm research import 1af19855-… 27ae246d-… --indices …` | concluído 2026-09-26 |
| `04_consolidacao/` | `CONSOLIDACAO.md` (83 selecionadas), `selecionadas.json`, `decisao_por_fonte.csv` (179 linhas com decisão e motivo) | concluído — 78 inseridas (`fontes_inseridas_final.json`) |

| `05_arquivos_enviados/` | 35 .md baixados e limpos, enviados como arquivo (sites que bloqueiam o NotebookLM) | enviados 2026-09-26 |

## Regra da consolidação

1. Juntar as quatro partes E (CSV) + a lista do NotebookLM.
2. Deduplicar por URL normalizada e por norma (número + ano), entre si e contra o acervo atual e o notebook irmão.
3. Fidedignidade: domínio oficial/primário ou periódico indexado; texto compilado para legislação; vigência conferida; URL aberta de verdade. Achado por um só pesquisador → conferir à mão antes de incluir.
4. Inserir as aprovadas (URL via `nlm source add`, ou importação por índice do Deep Research do NotebookLM) e registrar em `../notebook_fontes.json` e `../README.md`.
