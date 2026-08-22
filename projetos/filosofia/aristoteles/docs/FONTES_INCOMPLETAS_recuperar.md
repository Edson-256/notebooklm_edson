# Aristóteles — obras com fonte incompleta ou defeituosa

> ✅ **RESOLVIDO EM 2026-08-22.** As quatro fontes foram recuperadas, conferidas, normalizadas e
> integradas ao pipeline: sources trocadas no notebook NotebookLM, cenas e prompts gerados no mesmo
> padrão das demais obras, fila do cron reordenada. Nada aqui embaixo é mais tarefa pendente — o
> texto foi mantido como registro de como o problema foi diagnosticado.
>
> **Três coisas escritas abaixo estão erradas e foram corrigidas na prática:**
> **(a)** a Política foi resolvida pelo caminho **(C)** — Jowett completo, achado na captura de
> 1997 do Wayback do próprio MIT, zero retrabalho de tradução;
> **(b)** a Ética a Eudemo na edição Oxford tem **4** livros (I, II, III, VII), não 8 — a tabela
> abaixo erra isso e teria gerado falso alarme na conferência;
> **(c)** nenhuma outra obra veio truncada do MIT (conferido no `download_manifest.json`).
>
> **O que sobrou:** a obra 28, *Sobre as Virtudes e os Vícios*, ainda usa o volume Loeb ruim —
> issue `notebooklm_edson-x5lr`.
>
> **Registro completo da conferência:** `../_fontes_recuperadas_temp/README_CONFERENCIA.md`.

> **Criado em:** 2026-08-21 · **Origem:** auditoria do acervo (1.056 áudios no Dell) durante sessão de consultoria.
> **Issues relacionadas:** `notebooklm_edson-6so`, `notebooklm_edson-477`, `notebooklm_edson-0kr`.
>
> **Por que este arquivo existe:** quatro obras do corpus foram baixadas de fontes truncadas ou com
> OCR ruim. O pipeline não tinha como perceber — ele gerou fielmente os áudios do texto que existia.
> Uma delas **já está publicada pela metade no feed**.

---

## Resumo do que precisa ser recuperado

| # | Obra | Problema | Áudios já publicados | Urgência |
|---|---|---|---|---|
| 1 | **Política** | Fonte tem só os **Livros I–II de 8** | **22 (Livros I e II)** | 🔴 já no ar incompleta |
| 2 | **Ética a Eudemo** | OCR ilegível (`co^^iposed`, `temj,{j`) + segmentação (4 livros em vez de 8) | 0 | 🟡 antes da fila chegar |
| 3 | **Magna Moralia** | Segmentação confusa (76 caps colapsados em L01/02/07/08; a obra tem 2 livros) | 0 | 🟡 antes da fila chegar |
| 4 | **Geração dos Animais** | Segmentação (4 livros em vez de 5) | 0 | 🟡 antes da fila chegar |

**Só a Política é problema publicado.** As outras três ainda não entraram na fila de áudio — dá tempo
de corrigir a fonte antes que cheguem lá.

---

## 1. Política — ⚠️ o diagnóstico da issue estava errado

A issue `notebooklm_edson-6so` diz que o download veio truncado *"via cache do Google"*. **Não é isso.**
Verificado em 2026-08-21, baixando direto da fonte:

```
https://classics.mit.edu/Aristotle/politics.mb.txt   → 103.724 bytes
                                                      → contém APENAS "BOOK ONE" e "BOOK TWO"
                                                      → termina no meio de uma frase:
                                                        "...in the habit of givin</pre></body></html>"
```

**O arquivo do próprio MIT está quebrado na origem.** Rebaixar da mesma URL não resolve nada — é o
erro que se cometeria sem verificar. O `download_manifest.json` registrou 102.400 bytes (100 KB
exatos), que *parecia* assinatura de truncamento de cache, mas a origem tem o mesmo defeito.

### ✅ Fonte de substituição — verificada e funcionando (2026-08-21)

```
https://www.gutenberg.org/cache/epub/6762/pg6762.txt
```

- **604.414 bytes** (contra 103 KB da fonte quebrada)
- **8 livros completos** — `BOOK I` a `BOOK VIII`, conferido
- Tradução: **William Ellis** · domínio público · texto limpo, sem OCR

### ⚠️ Decisão que é sua antes de baixar

Os 22 áudios já publicados usam a tradução **Jowett** (via MIT/Oxford). O Gutenberg 6762 é
**Ellis**. Trocar a fonte no meio da obra faz os Livros I–II (Jowett) e III–VIII (Ellis) terem
vocabulário e estilo diferentes no mesmo feed.

**Três caminhos:**

- **(A) Ellis para a obra inteira** — baixar o 6762, refazer a segmentação dos 8 livros e
  **regerar os 22 áudios** dos Livros I–II. Coerente, custa 22 áudios de retrabalho.
- **(B) Ellis só do III em diante** — rápido, zero retrabalho, mas mistura tradutores.
  Aceitável se o objetivo é ouvir o conteúdo, não estudar a tradução.
- **(C) procurar Jowett completo** — mantém tudo coerente sem retrabalho. Ver o prompt de busca
  abaixo; a série Oxford é a candidata natural (é a mesma família de tradução que o MIT usa).

**Recomendação:** (C) primeiro — se aparecer Jowett completo com texto limpo, é a melhor das três.
Se não aparecer em 10 minutos de busca, ir de **(A)**, porque coerência de tradução dentro de uma
mesma obra vale mais que 22 áudios.

---

## 2 a 4 — as três que ainda dão tempo

As fontes atuais vieram todas do Archive.org, em digitalizações com OCR ruim:

| Obra | Fonte atual (defeituosa) | O que a obra deveria ter |
|---|---|---|
| Ética a Eudemo | `athenianconstitu00arisuoft` (Loeb 285 — volume que junta *Athenian Constitution* + *Eudemian Ethics* + *On Virtues and Vices*) | **8 livros** (III deles comuns com a Ética a Nicômaco) |
| Magna Moralia | `magnamoralia00arisuoft` (tr. Stock) | **2 livros** |
| Geração dos Animais | `generationofanim00arisuoft` (Loeb, tr. Peck) | **5 livros** |

> Note que a Ética a Eudemo e *On Virtues and Vices* apontam para **o mesmo arquivo** no manifest
> (bytes idênticos: 1.166.474) — é um volume Loeb com três obras dentro, o que explica boa parte da
> confusão de segmentação.

### A pista que vale seguir primeiro

O corpus já usa, para 30 das 33 obras, a série **"The Works of Aristotle Translated into English"**
(Oxford, ed. W. D. Ross / J. A. Smith) — é o que aparece no manifest como `MIT/Oxford-Edghill`,
`MIT/Oxford-Jowett`, `MIT/Oxford-Ross` etc. Essa série cobre **todo** o corpus aristotélico e está
em domínio público no Archive.org, em digitalizações geralmente melhores que os Loeb usados aqui.

Se as quatro obras faltantes vierem dessa mesma série, **o corpus inteiro fica com uma família única
de tradução** — e o problema de coerência da Política desaparece junto.

`[NÃO VERIFICADO — o Archive.org estava retornando 503 em 2026-08-21 03:32. Os volumes da série
existem, mas os identificadores exatos precisam ser confirmados na busca.]`

---

## Prompt para a busca das fontes

> Cole em um assistente com acesso à web (NotebookLM, ChatGPT com busca, Claude com busca).
> Está em inglês de propósito — a busca é em catálogos anglófonos.

```text
I need public-domain English translations of four works by Aristotle, as plain text
files (.txt) that I can download directly with a URL. Quality of the text matters more
than anything else: I will feed these into a text-to-speech pipeline, so OCR garbage
makes the output unusable.

THE FOUR WORKS, with what a complete copy must contain:

1. POLITICS — must contain all EIGHT books (Book I through Book VIII).
   Preferred translation: Benjamin JOWETT (Oxford / "The Works of Aristotle
   Translated into English", ed. W. D. Ross). A William Ellis translation is already
   available at gutenberg.org/cache/epub/6762/pg6762.txt — I am looking for JOWETT
   specifically, to stay consistent with the rest of my corpus.
   NOTE: classics.mit.edu/Aristotle/politics.mb.txt is BROKEN AT THE SOURCE — it stops
   in the middle of Book Two. Do not suggest it.

2. EUDEMIAN ETHICS — must contain all EIGHT books.
   Preferred translation: J. SOLOMON (Oxford / Works of Aristotle series).
   AVOID: the Loeb volume "athenianconstitu00arisuoft", which bundles three works
   together and has poor OCR (visible garbage such as "co^^iposed", "temj,{j").

3. MAGNA MORALIA — must contain BOTH books.
   Preferred translation: St. G. STOCK (Oxford / Works of Aristotle series).

4. ON THE GENERATION OF ANIMALS — must contain all FIVE books.
   Preferred translation: Arthur PLATT (Oxford / Works of Aristotle series).

WHERE TO LOOK, in this order:
  a) Project Gutenberg (gutenberg.org) — cleanest text, no OCR at all
  b) Wikisource (en.wikisource.org) — proofread, usually clean
  c) Internet Archive (archive.org) — look for the "Works of Aristotle Translated
     into English" volumes (Oxford, Ross/Smith). Prefer scans whose _djvu.txt is
     legible; reject anything with obvious OCR corruption.
  d) Perseus Digital Library (perseus.tufts.edu)

FOR EACH WORK, REPORT:
  - the direct download URL for the plain-text file
  - the translator and the publication year
  - the approximate file size
  - HOW YOU VERIFIED COMPLETENESS — quote the heading of the FIRST and the LAST book
    found in the file (e.g. "BOOK I" ... "BOOK VIII"), and quote the last sentence of
    the file to prove it does not end mid-sentence
  - a short sample of the text (about 200 words) so I can judge OCR quality myself

DO NOT report a source you have not actually opened and checked. If you cannot verify
completeness for one of the four, say so explicitly instead of guessing — a truncated
source that looks fine is exactly the failure that created this problem.
```

---

## Depois de baixar — o que fazer com os arquivos

Não basta trocar o `.txt`. O pipeline tem quatro etapas encadeadas a partir da fonte:

1. `scripts/01_download_corpus.py` — atualizar a URL no mapa de fontes e rebaixar
2. `scripts/02_clean_raw.py` — limpeza (`obras/*/clean/`)
3. `scripts/03_segment_capitulos.py` — **é aqui que a segmentação errada nasce**; conferir a
   contagem de livros e capítulos contra a tabela deste documento antes de seguir
4. `scripts/04_define_cenas_master.py` — refazer a fila de cenas

**Conferência obrigatória entre a 3 e a 4:** contar os livros segmentados e comparar com o esperado
(Política 8 · Eudemo 8 · Magna Moralia 2 · Geração dos Animais 5). Foi a ausência dessa conferência
que deixou a Política ir ao ar com um quarto do conteúdo, sem nenhum erro aparecer.

---

## Estado do acervo em 2026-08-21 (medido, não estimado)

- **1.056 áudios** publicados no Dell (`/srv/podcasts/aristoteles/`)
- Produção **ativa**: cron a cada 2h; 20 áudios gerados entre 00:00 e 00:12 de 20/08
- Obra em produção no momento: **História dos Animais** (obra 19) — não afetada por nenhum destes defeitos
- **Não é necessário pausar a produção** para resolver isto
