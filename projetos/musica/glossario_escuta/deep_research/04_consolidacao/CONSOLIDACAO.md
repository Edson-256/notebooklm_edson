# Consolidação — glossário técnico em cascata (10 famílias + termos)

- **Tarefa:** `notebooklm_edson-mmf9` · 2026-10-01 · pauta: `~/dev/_pessoal/musica_composicao/catalogo/escuta/PAUTA_PESQUISA_GLOSSARIO.md`
- **Entrada:** ChatGPT (63 linhas), agente Claude (87), Deep Research do NotebookLM (20) = 170 linhas, 161 URLs únicas.
- **Saída:** **101 selecionadas** (55 de prioridade 1, 32 de prioridade 2, 14 de prioridade 3) · 68 excluídas · 1 pendente.
  Decisão e motivo de cada uma das 170 linhas em `decisao_por_fonte.csv`; seleção em `selecionadas.json`.
- **Status:** **aguardando aprovação do Edson.** Nada foi subido ao notebook.

## Como a decisão foi tomada

1. **Agente Claude entra por padrão.** Ele abriu cada URL e trouxe as citações com notação. Saíram só a lição interativa do
   musictheory.net, que não tem texto legível, e o índice do curso da UFMA, que não traz as aulas.
2. **ChatGPT entra quando acrescenta fonte própria.** 17 entraram, entre elas as unidades didáticas do Instituto Andaluz
   del Flamenco (soleá, bulerías, seguiriyas, compás misto), que suprem a lacuna dos acentos por palo. 46 saíram: 14 por
   serem duplicatas, páginas-resumo do IPHAN cujo dossiê completo já entrou, catálogos sem texto e links quebrados.
   **Um link estava errado:** o handle da UFRGS que ele deu como "Campeirismo musical" abre uma dissertação de filosofia política.
3. **NotebookLM: nenhuma das 20 passou.** O que veio foi Scribd, dokumen.pub, Wikipedia, ResearchGate, agregadores e uma
   tese sobre funk paulista com título genérico.
4. **Conferido no PDF ou na página:** links de repositório trocados pelo PDF (Ayestarán, Faustino, a tese de York e a
   dissertação de Menezes). As teses da USP de Corrêa e Vilela, a de Castela (Coimbra) e o artigo de Wolffenbüttel não
   são entregues a leitor automático e foram baixados para `../05_arquivos_enviados/`, fora do git.
5. Uma fonte já estava no notebook: Morosan, sobre o canto znamenny (Ep09).

## Divergências conferidas na fonte (01/10)

| Ponto | O que a fonte diz | Fonte (#) | Status |
|---|---|---|---|
| Forma do choro | "três partes (ABC) com 16 compassos cada uma, organizadas na forma **AABBACCA**", e também a forma binária AA\|BB\|A | Dossiê IPHAN #52 | conferido — usar isto, não "ABACA" |
| Guarânia | "Considerando-se o compasso 6/8, o andamento da guarânia é o mais lento… **semínima pontuada = 70**". Rasqueado ≈ 87, moda campera ≈ 93. Nas versões brasileiras, "ora em 6/8, ora em 3/4" | Higa #21 | conferido |
| Chamamé | "la **birritmia del 6/8 y 3/4**": baixos nos três tempos binários, acordes em dois tempos ternários | Giménez #28 | conferido |
| Vaneira / vaneirão | da habanera, em 2/4, com três células de acompanhamento: (a) colcheia pontuada / semicolcheia / colcheia / colcheia (a célula da habanera); (b) a mesma, com a semicolcheia ligada à colcheia; (c) colcheia / semicolcheia / semicolcheia / colcheia / colcheia. Vaneirão: "o que permite diferenciar um vaneirão de uma vaneira é o seu **andamento**" | Wolffenbüttel #32 | conferido (corrigido em 02/10: a versão anterior citava a frase do parágrafo do vaneirão, "colcheia pontuada/colcheia/colcheia", que soma 7 semicolcheias e não fecha o 2/4 — provável erro de digitação do próprio texto; achado do agente da sessão musica_composicao) |
| Guitarra Lisboa × Coimbra | Lisboa si-lá-mi-si-lá-ré; Coimbra lá-sol-ré-lá-sol-dó, um tom abaixo; a de Coimbra é maior e mais simples | Sergl #35, citando Henrique 1994 | conferido |
| Origem do fado | Sergl: "gênero inicialmente popular no Brasil, migra para Portugal provavelmente em 1821" | Sergl #35 | **contestado** — tese de um autor; não afirmar sem Nery (pago) |
| Modos do baião | três leituras: Côrtes (#71) — trechos em Im7–IV7 "que apresentam a sonoridade do modo **dórico**" e melodias "sobre o modo **mixolídio**"; Lucena (#74, p. 22) — "os modos mais utilizados são" mixolídio, lídio e jônico, sem dórico; dossiê IPHAN (#70) — só "o chamado modo mixolídio" | #71, #74, #70 | conferido — divergência real; apresentar as três (Lucena e IPHAN acrescentados em 02/10, achado da sessão musica_composicao) |
| Compás do flamenco | Berlanga escreve 3+3+2+2+2; De las Heras registra a escrita em amálgama. O compás leva o nome do palo | Berlanga #39, De las Heras #41 | do relatório Claude; acentos por palo agora com fonte institucional (Instituto Andaluz #6 #7 #8) |
| Paradigma do Estácio | Sandroni (pago) × crítica de Ferraz (2025) | Ferraz #55 | do relatório Claude — apresentar os dois |
| "Canto falado" de João Gilberto | ruptura (crítica) × descritor construído, porque Mário Reis já cantava assim (Souza) | Souza #48, Ricci #47 | do relatório Claude |

**Caso DVC-082-C ("chamamé… ~116 BPM rolling 6/8 sway"):** as fontes sustentam o chamamé em 6/8 com 3/4 sobreposto e a
vaneira gaúcha em 2/4 binário de habanera. Pela métrica, as duas soam diferentes: o chamamé "balança em três", a vaneira
"marcha em dois". **Nenhuma fonte compara as duas lado a lado** — o contraste é inferência a partir de fontes separadas.
Wolffenbüttel (#32) descreve as duas no mesmo artigo, mas sem confrontá-las. Lá, o chamamé aparece entre as danças do baile
gaúcho, escrito em 3/4, com "puxada" de fole do 2º para o 3º tempo e "acentuação no 3º tempo do compasso, ao invés do 1º".
Isso, diz o artigo, o diferencia da **rancheira**, mais um par de confusão. Giménez (#28) escreve o chamamé em 6/8, com
acento na 5ª colcheia; as duas descrições caem no mesmo ponto do compasso, mas essa convergência é inferência (achado do
agente da sessão musica_composicao, 02/10), não afirmação de fonte.
**Nenhuma fonte separa de ouvido o chamamé argentino do gaúcho.** Os "~116 BPM" da etiqueta não dizem qual figura vale
o tempo, então não dá para comparar com o ≈ 70 da guarânia.

## Mapa de confusões (o que já tem fonte e o que não tem)

| Par | Base em fonte | Situação |
|---|---|---|
| chamamé × vanera gaúcha | 6/8+3/4 #28 #29 #30 × 2/4 habanera #32 | inferência: #32 descreve os dois sem confrontá-los |
| chamamé × rancheira | acento no 3º tempo por "puxada" de fole, no chamamé, em vez do 1º #32 | uma fonte, explícita |
| chamamé × guarânia | mesma família paraguaia; guarânia a mais lenta #21 #31 | sem andamento do chamamé |
| milonga × tango | 3+3+2 #60 #33 × marcato/síncopa/arrastre #59 #61 | razoável |
| vanera × xote | Wolffenbüttel #32 trata os dois sem confrontar | fraco |
| xote gaúcho × xote nordestino | #32 (citando Bangel 1989): "O modo maior domina o chotes gaúcho, ao contrário do nordestino, em que o modo menor aparece com muita frequência, além da elevação do 4º e abaixamento do 7º grau"; andamento: gaúcho "rápido, de caráter alegre", parecido com a polca (#32) × nordestino "um dos gêneros mais lentos do forró" (#70) | modo: uma fonte, explícita; andamento: inferência entre duas fontes (02/10) |
| toada × moda de viola | sem critério rítmico em fonte aberta | **lacuna** |
| cateretê × cururu | batidas separadas em #18 e #25 | sem comparação lado a lado |
| fado Lisboa × Coimbra | afinação, voz, função #35 #36 #37 | bom |
| bolero cubano × mexicano | cubano em #62 #63; mexicano só #64 (fraco) | **lacuna** do lado mexicano |
| valse musette × valsa/seresta | sem comparação | **lacuna** |
| baião × xote | capítulos separados no dossiê #70 | razoável |

> Os números (#) são o campo `n` de `selecionadas.json` e aparecem na primeira coluna das tabelas abaixo.

## Pendências (o Edson pode resolver no navegador)

> **Atualização 03/10:** três pendências foram resgatadas por cópias abertas em outros sites e já estão no notebook,
> aprovadas pelo Edson: **#102** Daniel Wolff, "A milonga gaúcha na gênese do Quinteto… de Fernando Mattos" (site do
> autor; o autor é Wolff, e Mattos é o compositor analisado), **#103** a tese de Valenzuela Lavado sobre o modo de mi
> (UGR) e **#104** Peter Manuel, "Flamenco Jazz" (Rutgers). Continuam pendentes a BN Digital (samba de breque), a UNAM
> (bolero mexicano) e o capítulo de Chenette (#14).
>
> **03/10, mais tarde:** a página da BN Digital tem só um texto curto (os MP3 dão erro). O Edson copiou o texto e ele entrou
> como **#105**, apenas com os parágrafos de definição: samba de breque = síncope acentuada + paradas súbitas ("breques") com
> comentário falado; Moreira da Silva. A lista de gravações ficou de fora porque as datas não batem. Fonte de definição,
> sem análise rítmica. Continuam pendentes a UNAM (bolero mexicano) e Chenette (#14).

- **BN Digital, "Subgêneros do samba"** (única fonte sobre samba de breque; Cloudflare): abrir, salvar como PDF e subir.
- **UNAM, Sánchez-Gallinal, "Bolero"** (revista Archipiélago; 403): a melhor pista para o bolero mexicano.
- **Peter Manuel, "Flamenco Jazz"** (CUNY; 403) e **Valenzuela Lavado, tese sobre o modo de mi** (UGR; timeout): harmonia frígia.
- **Fernando Mattos, "A milonga gaúcha…"** (SciELO Portugal; conexão recusada): a melhor fonte sobre a milonga gaúcha.

## Livros pagos que mais fariam diferença (união das duas listas)

Nery, *Para uma história do fado* · Sandroni, *Feitiço decente* · Lola Fernández, *Teoría musical del flamenco* ·
Corrêa, *A arte de pontear viola* · Higa, *Polca paraguaia, guarânia e chamamé* · Link & Wendland, *Tracing Tangueros* ·
Walter Garcia, *Bim bom* · Chediak, *Songbook Bossa Nova* · Paixão Côrtes & Barbosa Lessa, *Manual de danças gaúchas* ·
Sant'Anna, *A moda é viola* · Hawkins, *Chanson* · Gardner, *Russian Church Singing*.

## Seleção por família

### F1 — Sertanejo raiz e seus ritmos (10)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 18 | 1 | [Viola caipira: das práticas populares à escritura da arte](https://teses.usp.br/teses/disponiveis/27/27157/tde-22092015-112350/publico/ROBERTONUNESCORREA.pdf) | Roberto Nunes Corrêa (USP/ECA) | pt | compasso · instrumentos · origem · confusões |  · subir arquivo `correa_viola_caipira_usp.pdf` |
| 19 | 1 | [Cantando a própria história](https://www.teses.usp.br/teses/disponiveis/47/47134/tde-14062011-163614/publico/vilela_do.pdf) | Ivan Vilela (USP/Instituto de Psicologia) | pt | origem · forma · canto · instrumentos · confusões |  · subir arquivo `vilela_cantando_propria_historia_usp.pdf` |
| 20 | 1 | [O pagode de viola de Tião Carreiro: configurações estilísticas, importância e influências](https://files.cercomp.ufg.br/weby/up/270/o/DENIS_RILK_MALAQUIAS.pdf) | Denis Rilk Malaquias (UFG) | pt | compasso · instrumentos · canto · reconhecer de ouvido | PDF grande (13,9 MB) |
| 21 | 1 | [O gênero musical guarânia no Brasil: décadas de 1940/50](https://anppom.org.br/anais/anaiscongresso_anppom_2014/2822/public/2822-9929-1-PB.pdf) | Evandro Higa (UFMS) — Anais ANPPOM | pt | compasso · andamento · origem · confusões | guarânia: semínima pontuada ≈ 70 em 6/8; versões brasileiras oscilam para 3/4 — conferido |
| 24 | 1 | [Dossiê de Registro do Fandango Caiçara: expressões de um sistema cultural](https://bcr.iphan.gov.br/wp-content/uploads/tainacan-items/65968/66755/Fandango-Caicara_de_Dossie_.pdf) | IPHAN — Departamento de Patrimônio Imaterial | pt | instrumentos · compasso · origem · forma · confusões |  |
| 1 | 2 | [A busca pelos aspectos universais da moda-de-viola](https://revistas.usp.br/revistadatulha/article/download/121319/129293) | Jean Carlo Faustino; Revista da Tulha/USP | pt | forma · origem · canto · reconhecimento |  |
| 22 | 2 | [Música sertaneja e globalização](https://www.unirio.br/mpb/ulhoatextos/MusicaSertaneja.pdf) | Martha Tupinambá de Ulhôa (UNIRIO) — in Torres (ed.), Música Popular en América Latina, IASPM-AL | pt | canto · forma · instrumentos · origem |  |
| 23 | 2 | [Um paradoxo entre o existir e o resistir: a moda de viola através dos tempos](https://www.scielo.br/j/ea/a/3vCjJ4zRbrRpgg8BCpqzpVc/?format=html&lang=pt) | Rafael Marin da Silva Garcia — Estudos Avançados (USP) | pt | forma · canto · instrumentos · origem |  |
| 25 | 2 | [A viola caipira e a experiência musical em uma escola pública do campo – Emboabas/MG](https://ufsj.edu.br/portal2-repositorio/File/mestradoeducacao/DissertacaoLeandroDrumondMarinho.pdf) | Leandro Drumond Marinho (UFSJ) | pt | compasso · instrumentos · reconhecer de ouvido |  |
| 26 | 3 | [Improvisação à viola caipira: um estudo de caso aplicando modelos selecionados ao cateretê Vide Vida Marvada](https://files.cercomp.ufg.br/weby/up/270/o/Almir_Pessoa_-_Disserta%C3%A7%C3%A3o.pdf) | Almir Júnio Pessoa (UFG, coorient. Ivan Vilela) | pt | instrumentos · modo · compasso |  |

### F2 — Pampa e Litoral (chamamé, milonga, vanera, chimarrita) (9)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 27 | 1 | [Chamamé (inscrição 01600, Lista Representativa)](https://ich.unesco.org/en/RL/chamame-01600) | UNESCO — Patrimônio Cultural Imaterial | en | instrumentos · canto · origem |  |
| 28 | 1 | [El acordeón del Litoral argentino. Un análisis de los distintos modos de acompañamiento en el chamamé](https://www.redalyc.org/journal/7876/787682987003/html/) | Héctor José Giménez — Revista del Instituto Superior de Música (UNL) | es | compasso · instrumentos · reconhecer de ouvido | chamamé: "birritmia del 6/8 y 3/4" — conferido |
| 29 | 1 | [El chamamé desde la guitarra](http://sedici.unlp.edu.ar/bitstream/handle/10915/80528/Documento_completo.pdf-PDFA.pdf?sequence=1&isAllowed=y) | María Lucía Troitiño e Alejandro Polemann (UNLP/IPEAL) | es | compasso · instrumentos · confusões |  |
| 31 | 1 | [A assimilação dos gêneros polca paraguaia, guarânia e chamamé no Brasil e suas transformações estruturais](https://www.icgilbertoluizalves.com.br/imagens/galeriapdf/a-assimila-o-dos-g-neros-polca-paraguaia-guar-nia-e-chamam-no-brasil-e-suas-transforma-es-estruturais-site-241138.pdf) | Evandro Higa (UFMS) — Actas VII Congreso IASPM-AL | pt | compasso · origem · confusões |  |
| 32 | 1 | [Música no Rio Grande do Sul: conhecendo as origens e alguns gêneros musicais](https://www.seer.fundarte.rs.gov.br/RevistadaFundarte/en/article/download/757/pdf_74/1797) | Cristina Rolim Wolffenbüttel — Revista da FUNDARTE | pt | compasso · andamento · instrumentos · origem · confusões | vaneira em 2/4 de habanera, três células (ver Divergências); vaneirão = mesma base, mais rápido; chamamé em 3/4 com acento no 3º tempo, diferente da rancheira — conferido 02/10 · subir arquivo `wolffenbuttel_musica_rs.pdf` |
| 2 | 2 | [Del folklore musical uruguayo: La milonga](https://anaforas.fic.edu.uy/jspui/bitstream/123456789/101481/1/Ayesta_Milonga_SELDIA784.pdf) | Lauro Ayestarán | es | compasso · ritmo · forma · origem | Ayestarán: 2 págs. digitalizadas com OCR imperfeito (~2.800 palavras) — única fonte uruguaia clássica sobre a milonga |
| 30 | 2 | [La enseñanza de recursos interpretativos del chamamé en la guitarra](https://www4.fba.unlp.edu.ar/jidap2022/wp-content/uploads/sites/4/2022/11/26.-TROITINO.pdf) | María Lucía Troitiño (UNLP) — Jornadas JIDAP | es | compasso · reconhecer de ouvido |  |
| 33 | 2 | [La problemática del nacionalismo musical argentino (in Revista del IIMCV nº 31)](https://repositorio.uca.edu.ar/bitstream/123456789/1309/1/revista-instituto-carlos-vega-31.pdf) | Roberto Buffo — Revista del Instituto de Investigación Musicológica 'Carlos Vega' (UCA) | es | compasso · harmonia · forma · confusões |  |
| 34 | 3 | [A milonga no redemoinho da canção popular: Bebeto Alves e Vitor Ramil](https://lume.ufrgs.br/bitstream/handle/10183/61206/000863881.pdf?sequence=1) | Marcos Vladimir Miraballes Sosa (UFRGS, Letras) | pt | origem · canto · forma |  |

### F3 — Fado (Lisboa × Coimbra) (5)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 35 | 1 | [O fado: características melódicas, rítmicas e de performance](http://www.musimid.mus.br/3encontro/files/pdf/Marcos%20Julio%20Sergl.pdf) | Marcos Júlio Sergl (USJT/Unesp) — Anais III Encontro MusiMid | pt | compasso · harmonia · forma · instrumentos · origem · confusões | ORIGEM CONTESTADA: Sergl afirma que o fado foi "gênero inicialmente popular no Brasil" e migrou "provavelmente em 1821" — conferido no texto; não usar sem Nery. Afinações Lisboa × Coimbra conferidas (p. 12, citando Henrique 1994) |
| 36 | 1 | [A guitarra portuguesa e a canção de Coimbra: subsídios para o seu estudo e contextualização](https://estudogeral.uc.pt/bitstream/10316/19516/1/A%20Guitarra%20Portuguesa%20e%20a%20Can%C3%A7%C3%A3o%20de%20Coimbra_%20subsidios%20para%20o%20seu%20estudo%20e%20conxtualiza%C3%A7%C3%A3o-Luis%20Castela.pdf) | Luís Pedro Ribeiro Castela (Universidade de Coimbra) | pt | instrumentos · canto · origem · confusões |  · subir arquivo `castela_guitarra_coimbra.pdf` |
| 37 | 1 | [The Portuguese Guitar: History and Transformation of an Instrument Associated with Fado](https://yorkspace.library.yorku.ca/bitstreams/bfa1f800-2480-443c-b1c5-1d38832d2186/download) | Nuno José dos Santos Anaia Cristo (York University) | en | instrumentos · origem · confusões | URL trocada da página do repositório pelo PDF |
| 3 | 3 | [Fado de Coimbra / Canção de Coimbra](https://www.fd.uc.pt/alumni/pdf/newsletter/alumni_9.pdf) | Universidade de Coimbra Alumni | pt | canto · instrumentos · contexto social |  |
| 38 | 3 | ['O fado que nós cantamos, é a sina que nós seguimos': jovens fadistas portugueses e a emoção](https://www.meloteca.com/wp-content/uploads/2019/03/o-fado-que-nos-cantamos.pdf) | Marina Bay Frydberg — RBSE (UFPB) | pt | canto · origem · confusões |  |

### F4 — Flamenco / cante jondo (13)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 5 | 1 | [Aproximación a una didáctica del Flamenco. Tercera parte. Breve introducción a la métrica musical y transcripciones musicales](https://www.juntadeandalucia.es/cultura/flamenco/sites/default/files/flamenco/docs/tercera_parte_didactica.pdf) | Junta de Andalucía / Instituto Andaluz del Flamenco | es | compasso · ritmo · forma · notação |  |
| 6 | 1 | [Unidad de trabajo 11: Soleá](https://www.juntadeandalucia.es/aaiicc/flamenco/node/2241) | Instituto Andaluz del Flamenco | es | compasso · ritmo · reconhecer de ouvido |  |
| 7 | 1 | [Unidad de trabajo 13: Bulerías. Bulerías por Soleá](https://www.juntadeandalucia.es/aaiicc/flamenco/node/2243) | Instituto Andaluz del Flamenco | es | compasso · ritmo · reconhecer de ouvido · confusões |  |
| 39 | 1 | [El flamenco: arte musical y de la danza — Cap. 4: El compás y la sonoridad flamenca](https://www.ugr.es/~berlanga/captulo_4_el_comps_y_la_sonoridad_flamenca.html) | Miguel Ángel Berlanga (Universidad de Granada) | es | compasso · modo · forma · reconhecer de ouvido |  |
| 41 | 1 | [La transcripción musical del zapateado flamenco: una propuesta didáctica](https://revistas.um.es/flamenco/article/download/284241/223281/1082081) | Rosa de las Heras Fernández — La Madrugá nº 14 (Univ. de Murcia) | es | compasso · reconhecer de ouvido |  |
| 42 | 1 | [Aproximación musicológica a las palmas flamencas a través de la fonografía y la praxis contemporánea](https://ddd.uab.cat/pub/tesis/2020/hdl_10803_669363/bjdcp1de1.pdf) | Bernat Jiménez de Cisneros Puig (UAB) | es | compasso · reconhecer de ouvido · confusões |  |
| 8 | 2 | [Seguiriyas](https://www.juntadeandalucia.es/aaiicc/flamenco/content/seguiriyas) | Instituto Andaluz del Flamenco | es | compasso · modo · forma · confusões |  |
| 9 | 2 | [Cantes de compás mixto](https://www.juntadeandalucia.es/aaiicc/flamenco/content/cantes-de-comp%C3%A1s-mixto) | Instituto Andaluz del Flamenco | es | compasso · ritmo · hemiola/sesquiáltera |  |
| 43 | 2 | [Acerca de la cadencia frigia, la cadencia andaluza y la tonalidad menor: aproximaciones fundamentantes](https://www.laguitarra-blog.com/wp-content/uploads/2012/05/acerca-de-la-cadencia-frigiala-cadencia-andaluza-y-la-tonalidad-menor.pdf) | Julio Blasco (Universidad de Alcalá) — Revista Neuma (Univ. de Talca) | es | modo · harmonia | artigo acadêmico hospedado num blog de violão (laguitarra-blog); a fonte é o artigo, não o blog |
| 44 | 2 | [Sobre la poesía flamenca y su métrica](https://revistas.um.es/flamenco/article/download/179601/150851/655061) | Alfonso Carmona (Univ. de Murcia) — La Madrugá nº 8 | es | forma · canto |  |
| 4 | 3 | [Gestión cultural especializada en flamenco. Materiales didácticos](https://www.juntadeandalucia.es/cultura/flamenco/sites/default/files/flamenco/docs/gestion_cultural_materiales_didacticos.pdf) | Junta de Andalucía / Instituto Andaluz del Flamenco | es | compasso · ritmo · modo · harmonia · forma · instrumentos · canto | material de curso de gestão cultural; usar só os capítulos de música |
| 10 | 3 | [Apéndice. Grabaciones](https://www.juntadeandalucia.es/aaiicc/flamenco/content/ap%C3%A9ndice-grabaciones) | Instituto Andaluz del Flamenco | es | reconhecer de ouvido · canto · instrumentos · confusões | lista de gravações por palo — serve de guia de escuta |
| 40 | 3 | [El flamenco: arte musical y de la danza — Cap. 4B: La sonoridad flamenca](https://www.ugr.es/~berlanga/captulo_4b_la_sonoridad_flamenca.html) | Miguel Ángel Berlanga (Universidad de Granada) | es | modo · harmonia · reconhecer de ouvido | capítulo curto (~330 palavras); complementa F4-01 |

### F5 — Bossa nova (9)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 11 | 1 | [Canção do Amor Demais: marco da música popular brasileira contemporânea](https://www.scielo.br/j/pm/a/9KdPQTTrFLLQPkH6KmX5JVt/?lang=pt) | Liliana Harb Bollos; Per Musi | pt | ritmo · batida · harmonia · origem |  |
| 12 | 1 | [A música tímida de João Gilberto](https://teses.usp.br/teses/disponiveis/27/27157/tde-07032013-145429/publico/EnriqueMestrado.pdf) | Enrique Valarelli Menezes; USP | pt | ritmo · síncope · timbre · canto · prosódia · reconhecer de ouvido | servidor da USP não respondeu daqui; existência e PDF conferidos pela página da tese (WebFetch, 01/10) |
| 45 | 1 | [Padrões de acompanhamento na bossa nova ao violão de João Gilberto, em duas faixas do LP João Gilberto (1961)](https://abrapem.org/wp-content/uploads/2023/10/69.-Padroes-de-acompanhamento-na-bossa-nova-ao-violao-de-Joao-Gilberto-02.pdf) | Gustavo Passos Pinheiro e Bruno Mangueira (UnB) — Anais XI Congresso ABRAPEM | pt | compasso · instrumentos · reconhecer de ouvido |  |
| 46 | 1 | [Padrões de acompanhamento ao violão de João Gilberto, em duas faixas do LP O amor, o sorriso e a flor](https://abrapem.org/wp-content/uploads/2023/10/60.-Padroes-de-acompanhamento-ao-violao-de-Joao-Gilberto-01.pdf) | João Victor Rodrigues Vilela e Bruno Mangueira (UnB) — Anais XI Congresso ABRAPEM | pt | compasso · instrumentos · reconhecer de ouvido |  |
| 47 | 1 | [Canto falado no samba e na bossa nova: um estudo de aspectos da relação entre texto e música](https://revistas.ufg.br/musica/article/view/47343) | Gabriela Ricci — Música Hodie (UFG) | pt | canto · reconhecer de ouvido |  |
| 49 | 1 | [Aspetos da harmonia idiomática de Antonio Carlos Jobim: uma abordagem a partir dos processos de cifragem](https://dspace.uevora.pt/rdpc/bitstream/10174/35478/1/Doutoramento-Musica_e_Musicologia-Musicologia-Celso_Ribeiro_Bastos_Filho.pdf) | Celso Ribeiro Bastos Filho (Universidade de Évora) | pt | harmonia · modo |  |
| 48 | 2 | [Canto falado e música popular: apontamentos sobre práticas vocais, escuta e descritores estilísticos](https://www.scielo.br/j/opus/a/3rmH5mZ4JhswLg5CLxhKsht/?lang=pt) | Henrique Almeida Martins de Souza — Opus (ANPPOM) | pt | canto · origem · confusões |  |
| 50 | 2 | [O uso de acordes de empréstimo modal (AEM) na música de Tom Jobim](https://antigo.anppom.com.br/anais/anaiscongresso_anppom_2005/sessao16/ricardofreire_heitoroliveira.pdf) | Ricardo Dourado Freire e Heitor Martins Oliveira (UnB) — Anais ANPPOM | pt | harmonia |  |
| 51 | 3 | [A bossa-nova e sua influência na evolução da linguagem sonora da música instrumental brasileira](https://www.iar.unicamp.br/wp-content/uploads/2021/07/V2_ED03_A1_BossaNova.pdf) | Adercangelo Adépio de Souza — publicado no site do IA/UNICAMP | pt | harmonia · origem |  |

### F6 — Choro, samba de breque, seresta, modinha (7)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 52 | 1 | [Choro: instrução técnica do processo de registro do choro como Patrimônio Cultural do Brasil](https://bcr.iphan.gov.br/wp-content/uploads/tainacan-items/65968/105869/01_Dossie_Tecnico.pdf) | IPHAN / Acamufec | pt | forma · instrumentos · origem · confusões | forma AABBACCA (três partes de 16 compassos) e variante binária AA|BB|A — conferido no dossiê |
| 53 | 1 | [Dino 7 Cordas: o desenvolvimento de uma identidade sonora](https://anppom.org.br/anais/anaiscongresso_anppom_2023/papers/1635/public/1635-7746-1-PB.pdf) | Luiz Sebastião Juttel (UFRJ) — Anais ANPPOM | pt | instrumentos · reconhecer de ouvido |  |
| 55 | 1 | [Paradigma (ou paradoxo) do Estácio?: questões sobre etnocentrismo e limites da musicografia sobre a linha de tempo do samba](https://econtents.sbu.unicamp.br/inpec/index.php/muspop/article/download/19941/14936/59924) | Igor de Bruyn Ferraz — Música Popular em Revista (UNICAMP) | pt | compasso · confusões · origem |  |
| 54 | 2 | [Inovação e tradição nas baixarias do choro de Rogério Caetano](https://files.cercomp.ufg.br/weby/up/270/o/Joao_Fernandes_da_Silva_Neto_-_Disserta%C3%A7%C3%A3o_Final.pdf) | João Fernandes da Silva Neto (UFG) | pt | instrumentos · harmonia |  |
| 56 | 2 | [A modinha e o lundu no Brasil: as primeiras manifestações da música popular urbana no Brasil](https://files.cercomp.ufg.br/weby/up/988/o/LIMA_-_A_modinha_e_o_lundu_no_Brasil.pdf) | Edilson Vicente de Lima (cópia hospedada na UFG) | pt | origem · canto · forma |  |
| 58 | 2 | [Muito além da serenata: a seresta como pervivência da lírica trovadoresca](https://ojs.uel.br/revistas/uel/index.php/estacaoliteraria/article/view/44921) | Felipe Ziliotto Recaman e Ronald Ferreira da Costa — Estação Literária (UEL) | pt | origem · canto · forma |  |
| 57 | 3 | [Os pilares da música popular brasileira e cabo-verdiana: modinha, lundu e morna](https://rbec.ect.ufrn.br/data/_uploaded/artigo/N2/RBEC_N2_A16.pdf) | Fabiana Miraz de Freitas Grecco — Revista Brasileira de Estudos da Canção (UFRN) | pt | origem · canto |  |

### F7 — Bolero e tango (6)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 59 | 1 | [El estilo de ejecución en el tango: un estudio acerca de la temporalidad en la performance](https://sedici.unlp.edu.ar/bitstream/handle/10915/173486/Documento_completo.pdf?sequence=1&isAllowed=y) | Demian Alimenti Bel (UNLP, Doctorado en Artes) | es | compasso · instrumentos · reconhecer de ouvido · confusões |  |
| 60 | 1 | [Al son de la clave: el 3+3+2 en el tango. Las décadas del 20, 30 y 40](http://sedici.unlp.edu.ar/bitstream/handle/10915/53874/Documento_completo.pdf-PDFA.pdf?sequence=1&isAllowed=y) | Pablo Mitilineos (UNLP) — Clang nº 4 | es | compasso · confusões · origem |  |
| 62 | 1 | [The Cuban Bolero in Spanish Jazz](https://rpm-ns.pt/index.php/rpm/article/download/383/679/1365) | Christa Bruckner-Haring (KUG Graz) — Revista Portuguesa de Musicologia 6/2 | en | compasso · andamento · forma · origem · confusões |  |
| 63 | 2 | [Estrategia y táctica para revitalizar el bolero](https://dialnet.unirioja.es/descarga/articulo/5322692.pdf) | César Pagano Villegas — Batey: Revista Cubana de Antropología Sociocultural | es | compasso · forma · origem |  |
| 61 | 3 | [Tracing Tangueros: Argentine Instrumental Tango Music (resumo de sessão)](https://cilam.ucr.edu/diagonal/issues/2013/LinkandWendland.pdf) | Kacey Link e Kristin Wendland — Diagonal (UC Riverside) | en | compasso · instrumentos | resumo de sessão (~700 palavras), não o livro; o livro está na lista de compras |
| 64 | 3 | [Viviendo el amor y sufriendo el desamor. El bolero en México (radio reportaje)](https://tesiunamdocumentos.dgb.unam.mx/ptd2009/abril/0641940/0641940_A1.pdf) | Sandra Alicia Vargas Vergara (UNAM, FES Aragón — Comunicação) | es | origem · instrumentos | radiorreportagem (UNAM) — fraca, mas única fonte aberta sobre o bolero no México |

### F8 — Chanson (réaliste, valse musette) (5)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 65 | 1 | [En bordure de voix, corps et imaginaire dans la chanson réaliste](https://journals.openedition.org/volume/2228) | Joëlle-Andrée Deniot — Volume! 2:2 | fr | canto · reconhecer de ouvido | OpenEdition mostra desafio anti-robô ao curl (o WebFetch leu o texto integral) — se o NotebookLM receber pouco texto, subir como arquivo |
| 67 | 1 | [Musette et stéréotypes sociaux: les différentes appréciations d'un genre « populaire »](https://horizon.documentation.ird.fr/exl-doc/pleins_textes/divers17-07/010041194.pdf) | Kali Argyriadis e Sara Le Menestrel (texto no acervo Horizon do IRD) | fr | instrumentos · compasso · origem · confusões |  |
| 66 | 2 | [Catherine Dutheil-Pessin, La Chanson réaliste. Sociologie d'un genre (resenha)](https://journals.openedition.org/volume/1735?lang=fr) | Stéphane Dorin — Volume! 4:1 | fr | origem · canto · forma | OpenEdition mostra desafio anti-robô ao curl (o WebFetch leu o texto integral) — se o NotebookLM receber pouco texto, subir como arquivo |
| 68 | 2 | [Histoire des bals musette (fresque Danses sans visa)](https://fresques.ina.fr/danses-sans-visa/fiche-media/Dasavi00705/histoire-des-bals-musette.html) | Christian Dubar (éclairage) — INA | fr | compasso · instrumentos · reconhecer de ouvido |  |
| 69 | 3 | [Genèse et mutations du bal musette parisien](https://www.tiennetsimonnin.fr/articles/gen%C3%A8se-et-mutations-du-bal-musette-parisien/) | Tiennet Simonnin | fr | origem · instrumentos | site autoral sem vínculo institucional; usar só com corroboração de F8-03/F8-04 |

### F9 — Forró (baião, xote, pé-de-serra) (5)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 70 | 1 | [Instrução técnica da solicitação de registro das Matrizes Tradicionais do Forró como Patrimônio Cultural Brasileiro](https://bcr.iphan.gov.br/wp-content/uploads/tainacan-items/65968/67001/Matrizes-Tradicionais-do-Forro_de_MatrizesTradicionaisForro_Dossie_.pdf) | IPHAN / Associação Respeita Januário — resp. técnico Carlos Sandroni | pt | compasso · andamento · instrumentos · origem · forma · confusões |  |
| 71 | 1 | [Como se toca o baião: combinações de elementos musicais no repertório de Luiz Gonzaga](https://www.scielo.br/j/pm/a/6sW6mgh4bZhTRngXKxnRygH/?lang=pt) | Almir Côrtes — Per Musi nº 29 | pt | compasso · modo · instrumentos · reconhecer de ouvido | baião: trechos em dórico e em mixolídio, em exemplos notados — conferido |
| 72 | 2 | [Processo criativo musical: o modalismo como ferramenta de ensino-aprendizagem na linguagem musical](https://files.cercomp.ufg.br/weby/up/270/o/DISSERTA%C3%87%C3%83O-REJANE-2015.pdf) | Rejane de Melo e Cunha e Silva (UFG) | pt | modo |  |
| 73 | 2 | [Estrutura da música modal: a importância do ensino do modalismo nos cursos acadêmicos](https://www.unirio.br/cla/ivl/cursos/anitaugarte.pdf) | Anita Mattos Mezo Ugarte (UNIRIO, monografia) | pt | modo |  |
| 74 | 2 | [Obras para contrabaixo com gêneros da música popular brasileira: performance e aspectos pedagógicos](https://files.cercomp.ufg.br/weby/up/270/o/Diuliano_Vitor_Lucena_-_Dissertac%CC%A7a%CC%83o_Final.pdf) | Diuliano Vitor Lucena (UFG) | pt | compasso · modo · instrumentos |  |

### F10 — Música russa (9)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 75 | 1 | [Знаменный распев (Znamenny raspev)](https://www.pravenc.ru/text/%D0%B7%D0%BD%D0%B0%D0%BC%D0%B5%D0%BD%D0%BD%D0%BE%D0%B3%D0%BE%20%D1%80%D0%B0%D1%81%D0%BF%D0%B5%D0%B2%D0%B0.html) | И. Е. Лозовая (I. E. Lozovaya) — Православная энциклопедия, t. 20 | ru | modo · canto · forma · origem |  |
| 77 | 1 | [Частушки и «короткие песни»: к вопросу о внутрижанровой классификации](https://cyberleninka.ru/article/n/chastushki-i-korotkie-pesni-k-voprosu-o-vnutrizhanrovoy-klassifikatsii) | С. Р. Кулева (S. R. Kuleva) — Известия РГПУ им. Герцена | ru | forma · compasso · canto · confusões |  |
| 79 | 1 | [Эпические напевы из сборника Кирши Данилова и традиции Северного былинного мелоса](https://cyberleninka.ru/article/n/epicheskie-napevy-iz-sbornika-kirshi-danilova-i-traditsii-severnogo-bylinnogo-melosa) | М. А. Богданова e М. Р. Черная — Южно-Российский музыкальный альманах | ru | forma · canto · origem |  |
| 80 | 1 | [Communism and Folklore Revisited: Russian Traditional Music and the Janus-faced Nature of Soviet Cultural Politics](https://pressto.amu.edu.pl/index.php/ism/article/download/43462/36110) | Ulrich Morgenstern (mdw Viena) — Interdisciplinary Studies in Musicology 22 | en | instrumentos · origem · confusões |  |
| 76 | 2 | [The Influence of Znamenny Liturgical Chant on the Nineteenth-Century Russian Choral School](https://acda-publications.s3.us-east-2.amazonaws.com/choral_journals/Wall.pdf) | Jeffery B. Wall — Choral Journal | en | canto · modo · origem |  |
| 78 | 2 | [Забытые мотивы материнского фольклора](https://cyberleninka.ru/article/n/zabytye-motivy-materinskogo-folklora) | Н. Паутова (N. Pautova) — Развитие личности | ru | canto · modo · reconhecer de ouvido |  |
| 81 | 2 | [Stravinsky's 'Les Noces' and Russian Village Wedding Ritual](https://sites.nd.edu/choral-lit/files/2018/08/Mazo-Les-Noces-and-Wedding-Ritual.pdf) | Margarita Mazo — Journal of the American Musicological Society 43/1 | en | canto · forma · origem |  |
| 13 | 3 | [BALALAIKA! The Andreyev Balalaika Ensemble — liner notes](https://folkways-media.si.edu/docs/folkways/artwork/MON61713.pdf) | Smithsonian Folkways | en | instrumentos · timbre · repertório | encarte curto de conjunto de balalaica em formato orquestral — "tradição inventada" segundo Morgenstern (claude:F10-06) |
| 82 | 3 | [Russian Choral Music (Folkways FP 8754) — notas do álbum](https://folkways-media.si.edu/docs/folkways/artwork/FW08754.pdf) | Henry Cowell — Folkways Records | en | instrumentos · canto |  |

### T — Termos básicos (base da cascata) (23)

| # | P | Título | Autor / instituição | Idioma | Aspectos | Nota |
|---|---|---|---|---|---|---|
| 14 | 1 | [3s and 2s: Hemiola and Other Across-the-Beat Rhythms](https://uen.pressbooks.pub/auralskills/chapter/3s-2s-across-the-beat/) | Timothy Chenette; Foundations of Aural Skills | en | hemiola · 3:2 · 6/8 × 3/4 · reconhecer de ouvido | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 15 | 1 | [Minor Scales, Scale Degrees, and Key Signatures](https://viva.pressbooks.pub/openmusictheory/chapter/minor-scales-scale-degrees-and-key-signatures/) | Open Music Theory | en | escala · modo menor | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 16 | 1 | [Triads](https://viva.pressbooks.pub/openmusictheory/chapter/triads/) | Open Music Theory | en | acorde · tríade | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 83 | 1 | [Simple Meter and Time Signatures](https://viva.pressbooks.pub/openmusictheory/chapter/simple-meter-and-time-signatures/) | Open Music Theory (Gotham et al., VIVA Pressbooks) | en | pulso/tempo · compasso simples · forte/fraco | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 84 | 1 | [Compound Meter and Time Signatures](https://viva.pressbooks.pub/openmusictheory/chapter/compound-meters-and-time-signatures/) | Open Music Theory (VIVA Pressbooks) | en | compasso composto · 6/8 · subdivisão ternária | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 85 | 1 | [Other Rhythmic Essentials](https://viva.pressbooks.pub/openmusictheory/chapter/other-rhythmic-essentials/) | Open Music Theory (VIVA Pressbooks) | en | síncope | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 86 | 1 | [Metrical Dissonance](https://viva.pressbooks.pub/openmusictheory/chapter/metrical-dissonance/) | Open Music Theory (VIVA Pressbooks) | en | hemíola · tresillo · polirritmia | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 87 | 1 | [Rhythm and Meter in Pop Music](https://viva.pressbooks.pub/openmusictheory/chapter/rhythm-and-meter-in-pop-music/) | Open Music Theory (VIVA Pressbooks) | en | síncope · tresillo 3+3+2 | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 88 | 1 | [Introduction to Diatonic Modes and the Chromatic 'Scale'](https://viva.pressbooks.pub/openmusictheory/chapter/intro-to-diatonic-modes-and-the-chromatic-scale/) | Chelsey Hamm — Open Music Theory | en | escala · modos eclesiásticos | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 89 | 1 | [Diatonic Modes](https://viva.pressbooks.pub/openmusictheory/chapter/diatonic-modes/) | Mark Gotham e Megan Lavengood — Open Music Theory | en | modos (dórico, frígio, lídio, mixolídio) | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 91 | 1 | [Seventh Chords](https://viva.pressbooks.pub/openmusictheory/chapter/seventh-chords/) | Open Music Theory (VIVA Pressbooks) | en | acorde de sétima / tétrade | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 93 | 1 | [2.4: Meter](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/02%3A_Notation_-_Time/2.04%3A_Meter) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | pulso · compasso · forte/fraco · simples/composto |  |
| 94 | 1 | [2.7: Syncopation](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/02%3A_Notation_-_Time/2.07%3A_Syncopation) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | síncope |  |
| 95 | 1 | [2.8: Tempo](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/02%3A_Notation_-_Time/2.08%3A_Tempo) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | andamento · BPM |  |
| 97 | 1 | [5.3: Harmonic Series I — Timbre and Octaves](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/05%3A_The_Physical_Basis/5.03%3A_Harmonic_Series_I-_Timbre_and_Octaves) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | timbre |  |
| 99 | 1 | [Teoria Elementar da Música (apostila)](https://www.ufsm.br/cursos/graduacao/santa-maria/musica/wp-content/uploads/sites/485/2018/12/Teoria-Elementar-2013-1-1.pdf) | Pablo Gusmão — Departamento de Música, UFSM | pt | compasso simples/composto · intervalo · síncope · tétrade · modos |  |
| 17 | 2 | [Advanced Rhythm and Meter](https://tamucc.pressbooks.pub/stepstomusictheory/chapter/more-rhythm-meter/) | Steps to Music Theory | en | síncope · hemiola · compasso irregular · forte/fraco | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 90 | 2 | [Intervals](https://viva.pressbooks.pub/openmusictheory/chapter/intervals/) | Open Music Theory (VIVA Pressbooks) | en | intervalo | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 92 | 2 | [Embellishing Tones](https://viva.pressbooks.pub/openmusictheory/chapter/embellishing-tones/) | Open Music Theory (VIVA Pressbooks) | en | ornamentação | Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1 |
| 96 | 2 | [2.6: Dots, Ties, and Borrowed Divisions](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/02%3A_Notation_-_Time/2.06%3A_Dots_Ties_and_Borrowed_Divisions) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | divisão emprestada · tercina · hemíola |  |
| 98 | 2 | [8.3: Modes and Ragas](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/08%3A_Challenges/8.03%3A_Modes_and_Ragas) | Catherine Schmidt-Jones — Understanding Basic Music Theory (LibreTexts) | en | modos · escalas não ocidentais |  |
| 100 | 2 | [Gramática e Teoria Musical (apostila)](https://hugoribeiro.com.br/biblioteca-digital/Ribeiro-apostila-teoria.pdf) | Hugo Ribeiro (site do autor) | pt | intervalo · compasso · escalas |  |
| 101 | 2 | [Meter (Music Theory for the 21st-Century Classroom)](https://musictheory.pugetsound.edu/mt21c/meter.html) | Robert Hutchinson — University of Puget Sound | en | compasso · hemíola · síncope |  |
