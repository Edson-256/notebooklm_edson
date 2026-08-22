# Fontes recuperadas — conferência pendente

> ✅ **CONFERIDO E PROCESSADO EM 2026-08-22.** Esta pasta deixou de ser temporária: ela é agora
> a **entrada** de `scripts/00_normalize_recovered_sources.py`, que converte estes quatro textos
> para o formato canônico do pipeline e grava em `obras/*/_raw/`. Não apagar — sem ela o passo
> de normalização deixa de ser reproduzível. O texto abaixo é o registro da conferência.

> **Gerado em:** 2026-08-21 · **Issue:** `notebooklm_edson-rumd`
> **Origem do pedido:** `../docs/FONTES_INCOMPLETAS_recuperar.md`
> **Status:** arquivos baixados e verificados automaticamente. **Nada foi tocado no pipeline.**
> Nenhum destes arquivos está em `obras/`, em `download_manifest.json`, nem na fila de cenas.

## O que está aqui

| Arquivo | Obra | Tradutor / edição | Bytes | Palavras | Livros |
|---|---|---|---|---|---|
| `01_politica_jowett.txt` | Política | **Benjamin Jowett** (Oxford/Ross) | 499.789 | 87.820 | **8/8** |
| `02_etica_eudemo_solomon.txt` | Ética a Eudemo | **J. Solomon** — Works of Aristotle vol. IX (Ross), Clarendon 1925 | 199.448 | 35.899 | **4/4** (ver nota) |
| `03_magna_moralia_stock.txt` | Magna Moralia | **St. George Stock** — vol. IX (Ross), Clarendon 1925 | 176.196 | 32.884 | **2/2** |
| `04_geracao_animais_platt.txt` | Geração dos Animais | **Arthur Platt** — vol. V (Smith/Ross), Clarendon 1912 | 374.249 | 68.501 | **5/5** |

`_bruto/` guarda a extração crua das três obras do Wikisource, antes da remoção de notas de
rodapé e navegação — mantida para auditoria.

`sem_bekker/` guarda a **variante sem os números Bekker** das mesmas três obras (item 1 das
decisões abaixo, já resolvido — ver "Variante sem Bekker").

**As quatro obras ficam na mesma família de tradução (Oxford, ed. Ross/Smith) que o resto do
corpus.** O problema de coerência da Política some: os 22 áudios já publicados são Jowett e
continuam válidos — **zero retrabalho**.

---

## Proveniência e prova de completude

### 1. Política — Jowett, 8 livros ✅

```
https://web.archive.org/web/19970416151218if_/http://classics.mit.edu/Aristotle/politics.mb.txt
```

É **o mesmo arquivo do MIT que o pipeline já usava**, na captura de 16/04/1997 do Wayback
Machine — de quando ainda estava inteiro. Texto idêntico em formato e tradução ao dos outros
30 arquivos MIT do corpus: sem OCR, sem HTML, sem notas.

- Primeiro cabeçalho: `BOOK ONE` · último: `BOOK EIGHT`
- Última frase: *"…education should be based upon three principles- the mean, the possible, the becoming, these three."* seguida de `-THE END-`
- Capítulos por livro: **13 · 12 · 18 · 16 · 12 · 8 · 17 · 7** (bate com o cânone)

**Por que não rebaixar do MIT hoje:** o servidor do MIT corta qualquer arquivo em ~100 KB.
Verificado: `politics.mb.txt` para no meio do Livro II, e as versões HTML por livro
(`politics.2.two.html`, `.5.five.html`, `.7.seven.html`) **também terminam no meio de uma frase**,
todas em ~101.500 bytes. Não é cache do Google — é o servidor. Os outros arquivos MIT do corpus
menores que 100 KB não foram afetados; **vale conferir se alguma outra obra grande do corpus
veio do MIT truncada pelo mesmo teto** (ver "Pendência" abaixo).

**Gutenberg 6762 (Ellis) foi descartado** — está completo, mas é outro tradutor, e o Jowett
completo apareceu.

### 2. Ética a Eudemo — Solomon, edição Oxford completa ✅

```
https://en.wikisource.org/wiki/Eudemian_Ethics   (Livros 1, 2, 3, 7)
```

> ⚠️ **Correção a uma premissa do documento original.** O doc esperava **8 livros**. A edição
> Oxford (Solomon, 1925) **não tem 8 arquivos de livro, e isso está certo**: os Livros IV, V e VI
> da Ética a Eudemo são **idênticos** aos Livros V, VI e VII da Ética a Nicômaco e por isso não
> foram traduzidos por Solomon; e o Livro VIII foi anexado ao VII como §§ 13–15, seguindo uma
> tradição manuscrita. Logo o completo é: **I, II, III, VII** — e o VII com 15 capítulos.
> Isto está declarado na própria nota editorial do Wikisource.
>
> **Consequência para a conferência da etapa 3:** a regra "Eudemo = 8 livros" da tabela do
> documento original **produziria um falso alarme**. O número a conferir é **4 arquivos de
> livro, capítulos 8 · 11 · 7 · 15**.

- Fonte: transcrição proofread do **mesmo volume IX de Ross** de onde sai a Magna Moralia
- Última frase: *"So much, then, for the standard of perfection and the object of the absolute goods."* (fim canônico)

### 3. Magna Moralia — Stock, 2 livros ✅

```
https://en.wikisource.org/wiki/Index:Works_of_Aristotle_v9_(ed._Ross).djvu   (páginas 301–392)
```

Não existe página de leitura corrida no Wikisource (o link `Great Ethics` é vermelho); o texto
foi montado transcluindo o intervalo de páginas do volume IX pela API do MediaWiki.

- `BOOK I` (34 capítulos) · `BOOK II` (17 capítulos) — ambos batem com o cânone
- **O fim abrupto é real, não truncamento.** A Magna Moralia chega até nós interrompida; o texto
  termina em *"…how we ought to treat a friend in the friendship between friends who are on a
  footing of equality."* A edição impressa marca isso com asteriscos (removidos aqui).
  **Não "consertar" isso depois.**

> ⚠️ **Armadilha de segmentação (etapa 3).** No Livro I, 7 dos 34 capítulos têm o número colado
> ao número Bekker no início da linha — `1184b 3 After this, then…` em vez de `3 After this…`.
> Um regex `^(\d+) ` acha só 27. O padrão a usar é `^(?:\d{4}[ab] )?(\d{1,2}) `.
> **Foi exatamente esse tipo de coisa que produziu a segmentação errada original.**

### 4. Geração dos Animais — Platt, 5 livros ✅

```
https://en.wikisource.org/wiki/On_the_Generation_of_Animals   (Livros I–V)
```

- Capítulos por livro: **23 · 8 · 11 · 10 · 8** (bate com o cânone)
- Última frase: *"…not for any final end but of necessity and on account of the motive or efficient cause."* (fim canônico)

---

## Qualidade do texto — medido

Varredura por assinaturas de OCR ruim (`co^^iposed`, `temj,{j`, pontuação duplicada, caracteres
fora do repertório) nos quatro arquivos: **nenhuma ocorrência**. As três obras do Wikisource são
transcrições humanas revisadas, não OCR bruto; a Política é texto digitado do Internet Classics
Archive.

Foram removidos, e ficam registrados aqui porque **mudam a contagem de palavras**:
- notas de rodapé do aparato crítico (361 no Eudemo, 110 na Magna Moralia) — eram referências a
  variantes gregas de manuscrito, inúteis e ruidosas em áudio
- navegação do Wikisource (`Book II`, `→`, `[edit]`, linha de crédito repetida por livro)

## Variante sem números Bekker — `sem_bekker/`

As três obras do Wikisource traziam o localizador canônico embutido no corpo
(*"1181a Since our purpose is to speak about ethics…"*), coisa que os 30 textos do MIT não têm e
que o NotebookLM leria em voz alta. A pasta `sem_bekker/` tem a cópia sem eles:

| Arquivo | Bekker removidos |
|---|---|
| `sem_bekker/02_etica_eudemo_solomon.txt` | 71 |
| `sem_bekker/03_magna_moralia_stock.txt` | 69 |
| `sem_bekker/04_geracao_animais_platt.txt` | 0 — Platt não usa Bekker; a cópia é idêntica, existe só para o conjunto ficar completo |

Removido com `\b\d{3,4}[ab]\b` mais o espaço seguinte; cabeçalho de proveniência preservado e
marcado. Livros, capítulos e últimas frases reconferidos depois da remoção: **inalterados**.

> 🎁 **Efeito colateral bom: consertou a armadilha de segmentação da Magna Moralia.** Aqueles 7
> capítulos do Livro I cujo número estava colado ao Bekker (`1184b 3 After this…`) agora começam
> como todos os outros (`3 After this…`). No arquivo sem Bekker, um regex simples `^(\d{1,2}) `
> acha **2 a 34 contíguos** no Livro I e **1 a 17** no Livro II. Só o capítulo 1 do Livro I não tem
> marcador — ele começa direto depois de `BOOK I`, e sempre foi assim no impresso. Se quiser
> uniformidade total na etapa 3, basta inserir um `1` ali à mão; não fiz porque é mexer no texto
> além do pedido.

**Use `sem_bekker/` como fonte se o objetivo é áudio.** Guarde os arquivos da raiz caso um dia
queira que o áudio cite passagem pelo localizador canônico.

## Duas coisas que ainda são decisão sua

1. **Tabelas achatadas na Magna Moralia.** Stock imprime tabelas de virtudes (Excesso · Meio ·
   Falta) com os termos em grego; ao virar texto corrido elas ficam como uma sequência de linhas
   soltas (`κολακεία` / `φιλία` / `ἀπέχθεια`…). São poucas. Em áudio viram um trecho sem sentido
   — vale decidir se apaga ou se reescreve em prosa antes da etapa 2.
2. **Grego no corpo.** Eudemo e Magna Moralia têm palavras gregas isoladas no texto (convenção da
   edição Oxford). Igual ao item 1: o TTS não lida bem com isso.

## Duas coisas verificadas de quebra (e que dão sossego)

**1. Nenhuma outra obra do corpus veio truncada pelo MIT.** O teto de ~100 KB do servidor do MIT
poderia ter atingido outras obras grandes em silêncio. Conferi `_raw/download_manifest.json`:
das 28 obras de origem MIT, a Política era a **única** com ~100 KB (102.400 exatos). Todas as
outras grandes passam folgadamente do teto — História dos Animais 715 KB, Metafísica 619 KB,
Ética a Nicômaco 467 KB, Física 466 KB. Ou seja, o corte é recente ou intermitente e **só pegou a
Política**. Não há varredura pendente.

**2. A Magna Moralia estava registrada duas vezes no manifest**, com duas fontes diferentes:

```
605.832 bytes   archive.org/download/magnamoralia00arisuoft/...
1.166.474 bytes archive.org/download/athenianconstitu00arisuoft/...   <- o volume Loeb com 3 obras
```

Esse segundo registro é o mesmo arquivo apontado pela Ética a Eudemo. **É a explicação mecânica
da segmentação absurda** (76 capítulos colapsados em L01/02/07/08): a obra foi montada a partir de
um volume que contém três obras diferentes. Ao trocar a fonte, **apagar as duas entradas antigas**
de `03_magna_moralia` no mapa de fontes — não basta corrigir uma.

## Quando conferir e aprovar

Seguir a etapa 1→4 de `../docs/FONTES_INCOMPLETAS_recuperar.md`, com a conferência obrigatória
entre a 3 e a 4 usando **estes** números (não os da tabela original, que erra o Eudemo):

| Obra | Livros | Capítulos por livro |
|---|---|---|
| Política | 8 | 13 · 12 · 18 · 16 · 12 · 8 · 17 · 7 |
| Ética a Eudemo | 4 (I, II, III, VII) | 8 · 11 · 7 · 15 |
| Magna Moralia | 2 | 34 · 17 |
| Geração dos Animais | 5 | 23 · 8 · 11 · 10 · 8 |
