# Correção da divisão em capítulos — 2026-08-18

`capitulos/` foi **regenerado** por `scripts/resplit_capitulos.py`: passou de **43** para os
**59** capítulos reais de *Notre-Dame de Paris*. A pasta anterior está preservada em
`capitulos_old_43/` (e o git guarda o histórico).

## Causa

`process_notre_dame.py` exigia cabeçalho na forma `### <ROMANO> – TÍTULO`. Mas **16** dos 59
cabeçalhos estão malformados no arquivo-fonte `Notre-Dame_de_Paris.md` — vêm como
`– TÍTULO EM CAIXA ALTA`, sem `###` e sem numeral romano. Consequências:

- O texto desses 16 era **concatenado ao capítulo anterior**: `L02-C02` continha os capítulos
  II–VII do Livre II; `L04-C01`, o Livre IV inteiro; `L09-C01`, o Livre IX inteiro.
- O cabeçalho malformado do **Livre VIII, cap. I** vinha logo após `# LIVRE HUITIÈME`, quando o
  contador de capítulo ainda era 0 — a guarda `if book_num > 0 and chap_num > 0` **descartava**
  aquele texto. O capítulo se perdia por completo (20.128 chars), e todo o Livre VIII ficava
  **deslocado em −1**.

## Renumeração do Livre VIII (a única que muda nomes já existentes)

| Nome antigo | Nome novo | Capítulo canônico |
|---|---|---|
| *(não existia — descartado pelo bug)* | `L08-C01-LCU_CHANG_EN_FEUILLE_SCHE.md` | VIII, I |
| `L08-C01-SUITE_DE_LCU_CHANG_EN_FEUILLE_SCHE.md` | `L08-C02-SUITE_DE_LCU_CHANG_EN_FEUILLE_SCHE.md` | VIII, II |
| `L08-C02-FIN_DE_LCU_CHANG_EN_FEUILLE_SCHE.md` | `L08-C03-FIN_DE_LCU_CHANG_EN_FEUILLE_SCHE.md` | VIII, III |
| `L08-C03-LASCIATE_OGNI_SPERANZAI.md` | `L08-C04-LASCIATE_OGNI_SPERANZAI.md` | VIII, IV |
| `L08-C04-LA_MRE.md` | `L08-C05-LA_MRE.md` | VIII, V |
| `L08-C05-TROIS_CURS_DHOMME_FAITS_DIFFREMMENT.md` | `L08-C06-TROIS_CURS_DHOMME_FAITS_DIFFREMMENT.md` | VIII, VI |

Os outros 10 livros **não** têm deslocamento: as lacunas eram sempre depois do capítulo I, então
a numeração dos capítulos já existentes se manteve.

## ⚠️ O que NÃO foi tocado (de propósito)

`cenas/`, `prompts/`, `audios/` e `audios/metadata.json` ficaram **como estavam**. Os 175 áudios
de deep dive já foram gerados (maio–junho de 2026) com os identificadores de cena antigos —
inclusive os 19 de `L08-C01…C05`, que agora correspondem aos capítulos II–VI. Re-fatiar as cenas
invalidaria essa rastreabilidade, e isso é decisão do Edson, não deste conserto.

**Portanto:** o nome de cena `L08-C0N-*` dos áudios existentes está **um a menos** que o
capítulo canônico. Use a tabela acima para traduzir. As cenas de `L02`, `L04` e `L09` seguem
apontando para os blocos antigos (que continham vários capítulos), e cobrem apenas o começo
deles.

## Efeito colateral conhecido, não corrigido aqui

`process_notre_dame.py` fatia cenas em blocos cegos de 5.000 chars com teto de 5 por capítulo
(~25.000 chars) — ou seja, as cenas cobrem o **início** do capítulo, não as passagens mais
relevantes, ao contrário do que pede `plano_execucao_notre-dame.md` §3. Nos blocos grandes a
cobertura caía a 26% (`L02-C02`) e 32% (`L09-C01`). Com os capítulos agora bem divididos, um
reprocessamento futuro de cenas cobriria muito mais — ao custo de renomear cenas e áudios.
