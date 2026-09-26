# Consolidação dos três deep research — Perícia Médica

Tarefa `notebooklm_edson-ll06` · 2026-09-26 · aprovado pelo Edson (todas as 83) · **inseridas 78 em 2026-09-26** — ver `fontes_inseridas_final.json`

**Não inseridas (5):** #16 IF-BrA (DOU bloqueia download) · #28 TNU Tema 343 (já contido no Repositório TNU, #27) · #68 AACN 2021, #73 IASP, #74 EULAR (sem texto aberto; só resumo)

## Números

- Brutos: ChatGPT 42 · Claude 79 · NotebookLM 58 = **179 linhas / 159 URLs únicas**
- Após deduplicar e triar: **83 fontes selecionadas** (P1: 30 · P2: 33 · P3: 20); 78 linhas descartadas, motivo por linha em `decisao_por_fonte.csv`
- Notebook: 157 fontes + 83 = 240 (limite do Pro: 300)
- Nenhuma selecionada duplica os 84 livros nem o notebook irmão `e5f0fdb9`

## Divergências resolvidas no texto oficial

| Ponto | O que cada um disse | Verificado na fonte |
|---|---|---|
| Teto do Atestmed | NotebookLM: PC 13/2026 ampliou para 90 dias · ChatGPT: PC 72/2025 (60 dias) vigente · Claude: 30 dias pela lei, 90 pela PC 14/2026, prorrogado pela PC 43/2026 | **Claude correto.** PC 13/2026 art. 3º: teto 30 dias; art. 12 revoga PC 38/2023 (logo a 72/2025 caiu). PC 14/2026: 90 dias por 180 dias. PC 43/2026 (DOU 21/09/2026): prorroga por 365 dias |
| Norma do CFM sobre médicos do trabalho | NotebookLM ofereceu Res. 2.297/2021 e 2.183/2018 | **Ambas revogadas.** Vigente: Res. 2.323/2022 (arts. 10, 12 e 15 §2 suspensos judicialmente) |
| Norma-mãe da perícia no CFM | os três citam Res. 2.430/2025 | Confirmado: revoga Res. 1.497/1998 e 2.325/2022 |
| DPVAT/SPVAT | Claude: sem seguro obrigatório vigente | Confirmado: LC 211/2024 art. 4º revoga a LC 207/2024 |
| CNJ 595/2024 | Claude: instrumento BPC obrigatório em 03/11/2026 | Confirmado no texto compilado (Res. 673/2026 e 697/2026) |

## Critérios aplicados

1. Domínio oficial/primário ou periódico indexado com texto aberto; legislação pelo texto compilado do Planalto/DOU.
2. Norma revogada fica fora — exceção única rotulada: Lei 6.194/1974 (tabela DPVAT), útil para sinistros antigos.
3. Excluídos: notícias, acórdãos isolados não vinculantes, cópias de terceiros, páginas-índice/busca, obras pagas (AMA Guides, DSM), material de fornecedor.
4. Achada por um só pesquisador: incluída só se oficial e com URL aberta; as normas-chave de 2025–2026 foram lidas no DOU.

## Pendências técnicas na inserção

- OMS (CIF, WHODAS, saúde mental no trabalho): trocar a página-índice pelo PDF direto.
- URLs que bloqueiam robô (IF-BrA no DOU, AACN, IASP): testar no NotebookLM; se falhar, baixar e subir como arquivo ou usar cópia PMC.
- DL 352/2007 (Portugal): conferir se a página traz as tabelas anexas.

## Fontes selecionadas

### D1 — Previdência (INSS/RGPS) e BPC

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 1 | 1 | [Lei 8.213/1991 — Planos de Benefícios (compilado)](https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm) | ChatGPT+Claude |  |
| 2 | 1 | [Decreto 3.048/1999 — Regulamento da Previdência (compilado)](https://www.planalto.gov.br/ccivil_03/decreto/d3048.htm) | ChatGPT+Claude |  |
| 3 | 1 | [Decreto 3.048/1999 — Anexos II, III e IV (agentes, Lista C/NTEP)](https://www.planalto.gov.br/ccivil_03/decreto/D3048anexoii-iii-iv.htm) | Claude | base do NTEP |
| 4 | 1 | [IN PRES/INSS 128/2022 (consolidada)](https://www.gov.br/inss/pt-br/centrais-de-conteudo/legislacao/instrucao-normativa/2022/instrucao-normativa-pres-inss-no-128-de-28-de-marco-de-2022) | ChatGPT+Claude | URL do Claude (a do ChatGPT é página-índice) |
| 5 | 1 | [Portaria Conjunta MPS/INSS 13/2026 — Atestmed/análise documental](https://www.in.gov.br/en/web/dou/-/portaria-conjunta-mps/inss-n-13-de-23-de-marco-de-2026-694778266) | Claude (+NotebookLM no relatório) | conferida: revogou PC 38/2023 e outras; teto-base 30 dias |
| 6 | 1 | [Portaria Conjunta MPS/INSS 14/2026 — teto de 90 dias](https://www.in.gov.br/en/web/dou/-/portaria-conjunta-mps/inss-n-14-de-23-de-marco-de-2026-694772597) | Claude | conferida: 90 dias, vigência 180 dias |
| 7 | 1 | [Portaria Conjunta MPS/INSS 43/2026 — prorroga a PC 14 por 365 dias](https://www.in.gov.br/en/web/dou/-/portaria-conjunta-mps/inss-n-43-de-18-de-setembro-de-2026-733208414) | Claude | conferida: DOU 21/09/2026 |
| 8 | 2 | [Portaria Conjunta MPS/INSS 15/2026 — análise documental no auxílio-acidente](https://www.in.gov.br/en/web/dou/-/portaria-conjunta-mps/inss-n-15-de-23-de-marco-de-2026-694780534) | Claude |  |
| 9 | 2 | [Portaria Conjunta DPMF/INSS 19/2026 — teleperícia (SAT Remoto)](https://www.in.gov.br/web/dou/-/portaria-conjunta-dpmf/inss-n-19-de-31-de-marco-de-2026-*-698610961) | Claude |  |
| 10 | 1 | [Lei 8.742/1993 — LOAS (compilado)](https://www.planalto.gov.br/ccivil_03/leis/l8742compilado.htm) | ChatGPT+Claude |  |
| 11 | 1 | [Decreto 6.214/2007 — Regulamento do BPC (compilado)](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2007/decreto/d6214compilado.htm) | ChatGPT+Claude |  |
| 12 | 2 | [Portaria Conjunta MDS/INSS 2/2015 — instrumentos de avaliação do BPC](https://www.mds.gov.br/webarquivos/legislacao/assistencia_social/portarias/2015/portaria_conjunta_INSS_2_2015_BPC.pdf) | Claude |  |
| 13 | 2 | [Portaria Conjunta MDS/INSS 34/2025 — regras do BPC](https://www.gov.br/inss/pt-br/centrais-de-conteudo/legislacao/portarias-conjuntas/2025/ptcj34mds-inss.pdf) | Claude |  |
| 14 | 2 | [Lei 13.146/2015 — Estatuto da Pessoa com Deficiência (compilado)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm) | ChatGPT+Claude |  |
| 15 | 2 | [LC 142/2013 — aposentadoria da pessoa com deficiência](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp142.htm) | ChatGPT+Claude |  |
| 16 | 2 | [Portaria Interministerial 1/2014 — IF-BrA](https://www.in.gov.br/materia/-/asset_publisher/Kujrw0TZC2Mb/content/id/30050742/do1-2014-01-30-portaria-interministerial-n-1-de-27-de-janeiro-de-2014-30050738) | Claude | URL bloqueia robô (403); testar no NotebookLM |
| 17 | 3 | [Portaria Conjunta 66/2026 — instrumento para dependente com deficiência](https://www.in.gov.br/web/dou/-/portaria-conjunta-pres/inss/srgps/mps-n-66-de-14-de-julho-de-2026-719260532) | Claude |  |
| 18 | 3 | [Análise da aplicação do IFBr-M no BPC (GT biopsicossocial, MDH)](https://www.gov.br/mdh/pt-br/navegue-por-temas/pessoa-com-deficiencia/acoes-e-programas/avaliacao-biopsicossocial/grupo-de-trabalho-sobre-a-avaliacao-biopsicossocial-de-2020/Doc.09AnlisedaAplicaodondicedeFuncionalidadeBrasileiroModificadoemRequerentesdoBenefciodePrestaoContinuadaPessoaComDeficinciaUnimar.pdf) | NotebookLM [4] | estudo acadêmico hospedado no gov.br; complementar |

### D2 — Perícia judicial e precedentes

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 19 | 1 | [Lei 13.105/2015 — CPC (compilado)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13105.htm) | ChatGPT+Claude |  |
| 20 | 1 | [Resolução CNJ 595/2024 — perícias previdenciárias/Prevjud (compilado)](https://atos.cnj.jus.br/files/compilado123341202609176aabde2593a4c.pdf) | Claude | conferida: inclui Res. 673/2026 e 697/2026; instrumento BPC obrigatório em 03/11/2026 |
| 21 | 2 | [Resolução CNJ 233/2016 — cadastro de peritos (compilado)](https://atos.cnj.jus.br/files/compilado174307202209136320c12ba6490.pdf) | Claude |  |
| 22 | 2 | [Resolução CNJ 232/2016 — honorários periciais AJG (compilado)](https://atos.cnj.jus.br/files/compilado2133252024121667609ca581fdf.pdf) | Claude (+NotebookLM notícia [8]) |  |
| 23 | 1 | [Lei 10.259/2001 — Juizados Especiais Federais](https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10259.htm) | ChatGPT+Claude |  |
| 24 | 3 | [Lei 13.876/2019 — custeio das perícias contra o INSS](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/l13876.htm) | Claude |  |
| 25 | 3 | [Resolução CJF 937/2025 (altera Res. CJF 305/2014)](https://www.cjf.jus.br/publico/biblioteca/Res_937-2025.pdf) | Claude |  |
| 26 | 1 | [Súmulas da TNU (lista oficial)](https://www.cjf.jus.br/phpdoc/virtus/listaSumulas.php) | Claude |  |
| 27 | 1 | [Repositório TNU — versão 22/06/2026](https://www.cjf.jus.br/cjf/corregedoria-da-justica-federal/turma-nacional-de-uniformizacao/publicacoes-1/repositorio-tnu/repositorio-tnu/view/++widget++form.widgets.arquivo/@@download/Reposit%C3%B3rio+TNU+-+Vers%C3%A3o+atualizada+em+22.06.2026.pdf) | Claude |  |
| 28 | 2 | [TNU Tema Representativo 343 — DII na data do exame](https://www.cjf.jus.br/cjf/corregedoria-da-justica-federal/turma-nacional-de-uniformizacao/temas-representativos/tema-343) | ChatGPT |  |
| 29 | 2 | [STJ Tema Repetitivo 416 — auxílio-acidente, lesão mínima](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?novaConsulta=true&tipo_pesquisa=T&cod_tema_inicial=416&cod_tema_final=416) | Claude |  |
| 30 | 3 | [STJ Tema Repetitivo 862 — termo inicial do auxílio-acidente](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?novaConsulta=true&tipo_pesquisa=T&cod_tema_inicial=862&cod_tema_final=862) | Claude |  |
| 31 | 3 | [STJ Tema Repetitivo 1013 — trabalho no período de incapacidade](https://processo.stj.jus.br/repetitivos/temas_repetitivos/pesquisa.jsp?novaConsulta=true&tipo_pesquisa=T&cod_tema_inicial=1013&cod_tema_final=1013) | Claude |  |
| 32 | 2 | [STF Tema 932 — responsabilidade objetiva do empregador](https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?incidente=4608798&numeroProcesso=828040&classeProcesso=RE&numeroTema=932) | Claude |  |
| 33 | 2 | [STF RE 1.469.150 (Tema 1.300) — auxílio sem perícia presencial](https://www.stf.jus.br/arquivo/cms/noticiaNoticiaStf/anexo/Info_RE1469150FINAL.pdf) | NotebookLM [7] | PDF oficial do STF |
| 34 | 1 | [TST — tabela de Recursos de Revista Repetitivos](https://www.tst.jus.br/en/nugep-sp/recursos-repetitivos/tabela-completa) | Claude |  |
| 35 | 1 | [Decreto-Lei 5.452/1943 — CLT (compilado)](https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452compilado.htm) | ChatGPT+Claude |  |

### D3 — Ética e normas do CFM

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 36 | 1 | [Resolução CFM 2.430/2025 — ato médico pericial e telemedicina pericial](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2025/2430_2025.pdf) | ChatGPT+Claude+NotebookLM | conferida: revoga Res. 1.497/1998 e 2.325/2022 |
| 37 | 1 | [Código de Ética Médica — Res. CFM 2.217/2018](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2018/2217_2018.pdf) | Claude |  |
| 38 | 1 | [Resolução CFM 2.381/2024 — documentos médicos/atestados](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2024/2381_2024.pdf) | ChatGPT+Claude |  |
| 39 | 1 | [Resolução CFM 2.323/2022 — médicos que atendem o trabalhador](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2022/2323_2022.pdf) | Claude | conferida: revoga 2.297/2021; arts. 10, 12, 15 §2 suspensos |
| 40 | 2 | [Resolução CFM 2.314/2022 — telemedicina](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2022/2314_2022.pdf) | ChatGPT+Claude |  |
| 41 | 2 | [Parecer CFM 10/2024 — documentos médicos para benefício previdenciário](https://sistemas.cfm.org.br/normas/arquivos/pareceres/BR/2024/10_2024.pdf) | Claude |  |
| 42 | 3 | [Resolução CFM 1.638/2002 — prontuário](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2002/1638_2002.pdf) | Claude |  |
| 43 | 3 | [Resolução CFM 1.821/2007 — prontuário eletrônico](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2007/1821_2007.pdf) | Claude |  |
| 44 | 3 | [Resolução CFM 2.380/2024 — especialidades e áreas de atuação](https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2024/2380_2024.pdf) | ChatGPT+Claude |  |
| 45 | 2 | [Lei 13.787/2018 — digitalização e guarda de prontuários](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13787.htm) | ChatGPT |  |

### D4 — Medicina do trabalho e nexo

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 46 | 1 | [Portaria GM/MS 5.674/2024 — Lista de Doenças Relacionadas ao Trabalho](https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-5.674-de-1-de-novembro-de-2024-594040700) | Claude+NotebookLM[15] | URL do DOU (a do NotebookLM é cópia de terceiro) |
| 47 | 3 | [Portaria GM/MS 1.999/2023 — LDRT (corpo; anexo substituído)](https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-1.999-de-27-de-novembro-de-2023-526629116) | Claude |  |
| 48 | 1 | [NR-1 — GRO e riscos psicossociais (versão 2025)](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-01-atualizada-2025-i-3.pdf) | ChatGPT+Claude | mesma URL nos dois |
| 49 | 2 | [Manual do Capítulo 1.5 da NR-1](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/inspecao-do-trabalho/manuais-e-publicacoes/2026/manual_gro_pgr_da_nr_1.pdf) | Claude |  |
| 50 | 1 | [NR-7 — PCMSO](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-07-atualizada-2022-1.pdf) | ChatGPT+Claude |  |
| 51 | 1 | [NR-15 — insalubridade](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-15-atualizada-2025.pdf/view) | ChatGPT+Claude |  |
| 52 | 2 | [NR-16 — periculosidade](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/nr-16-atualizada-2025-ii.pdf) | ChatGPT+Claude |  |
| 53 | 1 | [NR-17 — ergonomia](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/arquivos/normas-regulamentadoras/nr-17-atualizada-2021.pdf/view) | ChatGPT+Claude |  |
| 54 | 3 | [Portaria Interministerial MPS/MF 10/2025 — FAP](https://www.gov.br/previdencia/pt-br/assuntos/previdencia-social/saude-e-seguranca-do-trabalhador/fap/rois-de-percentis/PORTARIA_INTERMINISTERIAL_MPS_MF_N__10__DE_10_DE_SETEMBRO_DE_2025___PORTARIA_INTERMINISTERIAL_MPS_MF_N__10__DE_10_DE_SETEMBRO_DE_2025___DOU___Imprensa_Nacional.pdf) | ChatGPT |  |
| 55 | 3 | [Lei 10.666/2003 — FAP/NTEP (base legal)](https://www.planalto.gov.br/ccivil_03/leis/2003/l10.666.htm) | ChatGPT |  |
| 56 | 2 | [Guia de Vigilância em Saúde vol. 3 — Saúde do Trabalhador](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/svsa/vigilancia/guia-de-vigilancia-em-saude-volume-3-6a-edicao) | Claude |  |
| 57 | 2 | [Protocolo MS nº 10 — Dor relacionada ao trabalho: LER/DORT](https://renastonline.ensp.fiocruz.br/sites/default/files/arquivos/recursos/dor_relacionada_trabalho_ler_dort.pdf) | Claude (+ChatGPT página MS) |  |
| 58 | 1 | [OIT — Diagnostic and exposure criteria for occupational diseases](https://www.ilo.org/sites/default/files/2024-07/wcms_836362.pdf) | ChatGPT+Claude | PDF direto |
| 59 | 3 | [OIT — List of Occupational Diseases (2010)](https://www.ilo.org/media/336021/download) | Claude |  |

### D5 — Baremos e avaliação de incapacidade

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 60 | 3 | [Lei 6.194/1974 — DPVAT, tabela de danos corporais [REVOGADA; sinistros antigos]](https://www.planalto.gov.br/ccivil_03/leis/l6194.htm) | Claude | conferido: LC 207/2024 revogada pela LC 211/2024 |
| 61 | 2 | [Decreto-Lei 352/2007 (Portugal) — Tabelas Nacionais de Incapacidades](https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid=1179&tabela=leis) | Claude | verificar se inclui as tabelas anexas |
| 62 | 2 | [OMS — CIF/ICF](https://www.who.int/standards/classifications/international-classification-of-functioning-disability-and-health) | Claude | página-índice; resolver PDF na inserção |
| 63 | 2 | [OMS — Manual WHODAS 2.0](https://www.who.int/publications/i/item/measuring-health-and-disability-manual-for-who-disability-assessment-schedule-(-whodas-2.0)) | Claude | resolver PDF na inserção |

### D6 — Classificações

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 64 | 2 | [Nota Técnica MS 91/2024 — implementação da CID-11 no Brasil](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2024/nota-tecnica-no-91-2024-cgiae-daent-svsa-ms.pdf/@@download/file) | ChatGPT |  |
| 65 | 2 | [ICD-11 Reference Guide (OMS)](https://icdcdn.who.int/icd11referenceguide/en/html/index.html) | Claude |  |
| 66 | 3 | [OMS — Burn-out, fenômeno ocupacional na CID-11](https://www.who.int/news/item/28-05-2019-burn-out-an-occupational-phenomenon-international-classification-of-diseases) | Claude |  |

### D7 — Evidência (simulação, dor, retorno ao trabalho)

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 67 | 1 | [Multidimensional Malingering Criteria — atualização de 20 anos (Sherman 2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7452950/) | Claude | PMC aberto |
| 68 | 1 | [AACN 2021 — consenso sobre avaliação de validade](https://pubmed.ncbi.nlm.nih.gov/33823750/) | ChatGPT+Claude | testar texto integral; senão só resumo |
| 69 | 2 | [Validade de sintomas e desempenho na Europa — atualização](https://pmc.ncbi.nlm.nih.gov/articles/PMC8612718/) | Claude |  |
| 70 | 2 | [Cochrane — retorno ao trabalho na depressão](https://pmc.ncbi.nlm.nih.gov/articles/PMC8094165/) | Claude |  |
| 71 | 2 | [Intervenções no local de trabalho e retorno (MSK, dor, mental)](https://pmc.ncbi.nlm.nih.gov/articles/PMC5820404/) | Claude |  |
| 72 | 1 | [OMS — diretrizes de saúde mental no trabalho (2022)](https://www.who.int/publications/i/item/9789240053052) | ChatGPT+Claude | resolver PDF na inserção |
| 73 | 2 | [IASP — dor crônica na CID-11](https://doi.org/10.1097/j.pain.0000000000001384) | Claude | doi bloqueia robô; buscar PMC |
| 74 | 3 | [EULAR — recomendações revisadas para fibromialgia](https://doi.org/10.1136/annrheumdis-2016-209724) | Claude |  |
| 75 | 1 | [ACOEM — Work-Relatedness (2018)](https://acoem.org/acoem/media/News-Library/JOEM-Work-relatedness-Dec-2018.pdf) | ChatGPT |  |
| 76 | 3 | [Intervenções no trabalho para distúrbios MSK crônicos (BMJ Open)](https://pubmed.ncbi.nlm.nih.gov/42331580/) | ChatGPT | testar texto integral |
| 77 | 3 | [Exagero de sintomas e testes de validade em sintomas sem explicação médica](https://pmc.ncbi.nlm.nih.gov/articles/PMC5764424/) | NotebookLM [21] | PMC aberto |
| 78 | 3 | [Revisão de abordagens para detectar simulação em contexto forense](https://pmc.ncbi.nlm.nih.gov/articles/PMC6308182/) | NotebookLM [30] | PMC aberto |

### D8 — Perícia criminal e protocolos

| # | P | Fonte | Achada por | Nota |
|---|---|---|---|---|
| 79 | 2 | [Decreto-Lei 3.689/1941 — CPP (compilado)](https://www.planalto.gov.br/ccivil_03/decreto-lei/del3689compilado.htm) | ChatGPT+Claude |  |
| 80 | 2 | [Lei 12.030/2009 — perícias oficiais criminais](https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2009/lei/l12030.htm) | ChatGPT+Claude |  |
| 81 | 2 | [Protocolo de Istambul (Rev. 2, 2022)](https://www.ohchr.org/sites/default/files/documents/publications/2022-06-29/Istanbul-Protocol_Rev2_EN.pdf) | Claude |  |
| 82 | 3 | [Protocolo de Minnesota (2016)](https://www.ohchr.org/sites/default/files/Documents/Publications/MinnesotaProtocol.pdf) | Claude |  |
| 83 | 2 | [Resolução CNJ 414/2021 — quesitos periciais em casos de tortura](https://atos.cnj.jus.br/atos/detalhar/4105) | Claude |  |

