# Prompt de deep research — Glossário técnico em cascata (piloto de 10 famílias)

- **Tarefa:** `notebooklm_edson-mmf9` · criado 2026-10-01 · pedido da sessão `musica_composicao`
  (pauta: `~/dev/_pessoal/musica_composicao/catalogo/escuta/PAUTA_PESQUISA_GLOSSARIO.md`;
  issue do lado de lá: `musica_composicao-m6wl`).
- **Uso:** o mesmo prompt vai ao ChatGPT (Deep Research — o Edson cola), a um agente Claude e, em
  versão condensada, ao Deep Research do NotebookLM (Gemini).
- **Idioma:** instruções em inglês, saída em pt-BR (regra do ecossistema).
- **Método:** igual ao da pesquisa 1 (`../teoria_escuta_critica/deep_research/`, tarefa
  `notebooklm_edson-c0x3`): três pesquisas → consolidação com decisão e motivo por fonte (CSV) →
  aprovação do Edson → notebook. **Sem áudio** — a saída serve a verbetes escritos.
- **Notebook:** o mesmo da pesquisa 1 (`4ac56794`), fontes com prefixo `Gloss ·` — os termos
  básicos já estão lá (Open Music Theory, Schmidt-Jones, Tagg) e serão reaproveitados.
- **Onde colar o resultado do ChatGPT:** `01_chatgpt/resultado.md` (nesta pasta). Se o export
  perder os links (aconteceu na pesquisa 1), cole também a parte F (CSV) num arquivo à parte.

---

## PROMPT COMPLETO (copiar daqui até o fim da seção)

```text
# ROLE
You are a research librarian with expertise in ethnomusicology, Latin American, Iberian and
Russian folk and popular music, Brazilian popular music, and music-theory pedagogy. You are
selecting sources for a CASCADING TECHNICAL GLOSSARY of musical genres and terms, written in
Brazilian Portuguese, that will be linked to a song-listening app.

# WHO WILL USE IT AND FOR WHAT
The user is a Brazilian surgical oncologist: highly literate, scientifically trained, a layman in
music theory. He already listened to an introductory audio series on critical listening and found
it useful but superficial. He recognizes the SOUND of a genre ("this sounds gaúcho") but cannot
connect it to the technical TERMS used to describe it, nor to their MEANING. Real case: a song
whose style tag says "Chamamé, Argentine correntino litoral folk, accordion and acoustic guitar,
~116 BPM rolling 6/8 sway" sounded to him like music from Rio Grande do Sul — and he could not say
why it was or was not.

Each glossary entry will have three layers: (1) in plain words; (2) the technical term, translated
and explained; (3) the theory behind it. Each term must lead to the term it depends on, e.g.
2/4 → meter → pulse; 3+3+2 → syncopation → strong/weak beat; 6/8 → compound meter → ternary
subdivision → hemiola. So the sources must be TECHNICALLY PRECISE (rhythmic patterns, meters,
modes, harmonic idioms, instruments, vocal technique) while still usable to write accessible
explanations. Every factual claim in an entry will cite a source, so sources must be reliable and
citable. No audio will be produced from this research.

# TASK
For each of the 10 genre families below AND for the list of basic terms, find the best sources,
verify that each one exists and is accessible, and return a prioritized, deduplicated list ready to
be loaded into Google NotebookLM. The leads named below are LEADS TO VERIFY, not facts — confirm
each one; if a lead is wrong, weak or inaccessible, say so and propose a better source.

For EACH family, the selected sources together must cover, with a source for each claim:
meter and typical rhythmic pattern (ideally in notation or a counting scheme such as 3+3+2) ·
usual tempo range · scale/mode · typical harmony · instruments and timbres · singing style ·
form · origin and geography · HOW TO RECOGNIZE IT BY EAR (audible markers) · WHAT IT IS CONFUSED
WITH AND HOW TO TELL THEM APART. If the sources disagree on a point (e.g., whether a rhythm is
in 6/8 or 3/4, or its tempo), report the disagreement and who says what — do not resolve it
silently.

## The 10 families
F1. Brazilian sertanejo raiz (música caipira) and its rhythms — moda de viola, toada, cururu,
    cateretê/catira, pagode de viola, guarânia (Paraguayan origin), rasqueado, recortado,
    cana-verde, calango, fandango caiçara. What distinguishes each rhythm: the viola caipira
    strumming/plucking pattern ("batida", "ponteio"), meter, tempo, the viola's tunings (cebolão,
    rio abaixo, etc.), the singing in parallel thirds ("dupla", "terça"). Leads: Romildo Sant'Anna,
    "A moda é viola"; Rosa Nepomuceno, "Música caipira: da roça ao rodeio"; Ivan Vilela (USP)
    on the viola caipira; José de Souza Martins on música sertaneja; Roberto Corrêa (viola
    method, "A arte de pontear viola"); IPHAN material on fandango caiçara (registered heritage);
    theses in USP/UNICAMP/UNESP/UFU repositories; Revista do IEB; Per Musi; Música Popular em
    Revista (UNICAMP).
F2. Music of the pampa and the Litoral (River Plate basin) — chamamé, milonga (campera/rural vs
    urban/ciudadana), vanera/vaneira/vaneirão, chimarrita, and the Paraguayan polca/guarania where
    they meet. Where each lives (Corrientes and the Argentine Litoral, Uruguay, Rio Grande do Sul,
    Paraguay); the rhythmic difference between chamamé (6/8 with 3/4 superposition, "sesquiáltera")
    and Gaucho vanera (binary, habanera-derived); the accordion/bandoneon/"gaita" roles; what, BY
    EAR, separates the Argentine and the Brazilian (gaúcho) variants — if sources make that
    distinction; if they do not, say so explicitly. Leads: UNESCO ICH nomination of chamamé
    (inscribed 2020: "Chamamé"); Carlos Vega and Isabel Aretz on Argentine folk rhythms (Instituto
    Nacional de Musicología "Carlos Vega"); Lauro Ayestarán on Uruguayan milonga; Paixão Côrtes and
    Barbosa Lessa, "Manual de danças gaúchas"; theses at UFRGS/UFSM on música gaúcha/nativista;
    Revista Argentina de Musicología; Latin American Music Review.
F3. Fado — Lisbon fado vs Coimbra fado (vocal style, who sings, guitar tuning and "guitarra
    portuguesa" vs "viola", fado menor / corrido / mouraria as base fados, social setting). Leads:
    Rui Vieira Nery (Para uma história do fado); Salwa El-Shawan Castelo-Branco (INET-md,
    Universidade Nova de Lisboa); Museu do Fado; UNESCO ICH file "Fado" (2011). Already loaded —
    do not repeat: UNESCO "Fado, urban popular song of Portugal"; Museu do Fado page on Artur
    Paredes.
F4. Flamenco / cante jondo — palos and their families (soleá, seguiriya, bulería, alegrías,
    tangos, fandangos, malagueña), the 12-beat compás and its accents, the Phrygian/"modo de mi"
    and the Andalusian cadence, cante/toque/baile, melisma ("quejío"). Leads: Lola Fernández,
    "Teoría musical del flamenco"; Manuel Granados; Peter Manuel on the Andalusian cadence and
    flamenco harmony; Junta de Andalucía (Instituto Andaluz del Flamenco); Revista de
    Investigación sobre Flamenco "La Madrugá" (Universidad de Murcia). Already loaded — do not
    repeat: UNESCO "Flamenco"; Junta de Andalucía "Saetas"; Lola Fernández Marín, "La
    terminología musical del flamenco" (Revista de Flamencología 30); "La saeta en la Semana Santa
    cartagenera".
F5. Bossa nova — the guitar "batida" (João Gilberto) and its relation to the samba surdo/tamborim
    pattern, syncopation, harmony with seventh, ninth and altered chords, chromatic voice leading,
    the "speech-like" vocal style. Leads: Walter Garcia, "Bim bom: a contradição sem conflitos de
    João Gilberto"; Brasil Rocha Brito, "Bossa nova" (in Augusto de Campos, Balanço da bossa);
    Almir Chediak, Songbook Bossa Nova (harmony); Ruy Castro, Chega de saudade (history); academic
    articles in Per Musi, Música Popular em Revista, Revista Brasileira de Música (UFRJ).
F6. Choro, samba de breque, seresta and modinha — choro form (rondo ABACA), the regional
    instruments (flute, cavaquinho, 7-string guitar "baixaria", pandeiro), modinha's origin in
    18th-century salon song, seresta as serenade practice, samba de breque (spoken "breaks",
    Moreira da Silva). Leads: IPHAN registration file of choro as cultural heritage (2024);
    Instituto Moreira Salles (IMS) choro and modinha collections; Mário de Andrade, "Modinhas
    imperiais"; Thiago de Oliveira Pinto / Carlos Sandroni ("Feitiço decente", on the
    "paradigma do Estácio" and the "tresillo"/3+3+2); Música Popular em Revista; Per Musi.
F7. Bolero and tango — Cuban vs Mexican bolero (the "cinquillo"/bolero rhythm, trio romántico
    with requinto guitar); tango (2/4 and 4/8, "marcato", "síncopa", "arrastre", "yumba",
    bandoneon, orquesta típica), tango vs milonga vs vals criollo. Leads: Ramón Pelinski on tango;
    Kacey Link & Kristin Wendland, "Tracing Tangueros"; Academia Nacional del Tango; Cuban and
    Mexican musicology sources on bolero (e.g., Pablo Dueñas, "Bolero: historia documental";
    Cuban musicology from Casa de las Américas / CIDMUC); UNESCO "Tango" is already loaded — do not repeat, nor the MTO
    review of Tracing Tangueros.
F8. French chanson — chanson réaliste (Fréhel, Damia, Piaf), valse chantée and bal musette
    (accordion, 3/4, "valse musette"), the primacy of the text and the vocal style. Leads: Chanson
    studies by Peter Hawkins ("Chanson: the French singer-songwriter"), Joëlle Deniot on chanson
    réaliste, Volume! (open journal, French popular music studies), Philharmonie de Paris /
    Cité de la musique educational pages, BnF Gallica (period sources, open), Musée de la
    musique.
F9. Forró — baião, xote, xaxado, arrasta-pé, forró pé-de-serra: the zabumba–triângulo–sanfona
    trio, the baião rhythmic cell, the Northeastern modes (Mixolydian with raised fourth —
    "modo nordestino"/Lydian-dominant —, Dorian), Luiz Gonzaga's role. Leads: IPHAN registration
    of "Matrizes tradicionais do forró" as Brazilian cultural heritage (2021); José Siqueira,
    "Sistema modal na música folclórica do Brasil"; Elba Braga Ramalho on Luiz Gonzaga; the USP
    thesis "Procedimentos modais na música brasileira" (Paes) is ALREADY LOADED — do not repeat.
F10. Russian music — plach / prichitanie (lament), chastushka, znamenny chant (neumes, unison
     church chant), byliny, and the balalaika and bayan. Leads: Izaly Zemtsovsky; Margarita
     Mazo; Natalie Kononenko on laments; Johann von Gardner on Russian chant; the Russian Folklore
     Center / Pushkin House (IRLI) archives; Smithsonian Folkways liner notes for Russian folk
     recordings; Laura Olson, "Performing Russia"; Ethnomusicology Forum / Yearbook for
     Traditional Music articles. Sources in Russian are welcome if authoritative and openly
     readable.

## The basic terms (base of the cascade)
Find open, didactic, precise sources (definition + example) for: pulse/beat · tempo and BPM ·
meter (simple vs compound; 2/4, 3/4, 6/8; 12-beat cycles) · binary vs ternary subdivision ·
hemiola / sesquiáltera · syncopation (incl. tresillo and 3+3+2) · strong/weak beat · scale ·
interval · major/minor mode · church modes (Dorian, Phrygian, Mixolydian, Lydian) · chord ·
seventh chord / tétrade · cadence (incl. the Andalusian cadence) · timbre · ornamentation and
melisma. Prefer open textbooks with clear examples (Open Music Theory; Schmidt-Jones,
"Understanding Basic Music Theory"; Philip Tagg; Comprehensive Musicianship (Iowa State
Pressbooks); musictheory.net lessons; Bohumil Med, "Teoria da Música" — check open access) and
at least some sources IN PORTUGUESE (e.g., open courseware from Brazilian universities, the
"Teoria musical" material of federal institutes, SciELO). Already loaded — do not repeat:
Open Music Theory chapters "Introduction to Harmony, Cadences, and Phrase Endings", "Four-Chord
Schemas", "Pentatonic Harmony", OMT 2e 7.3, 7.7 and 7.12; Schmidt-Jones 7.6 "Cadence"; Tagg,
"Everyday Tonality" and its chapter 4 sample on non-heptatonic modes; Comprehensive Musicianship
7.1. Point to OTHER chapters of these same open books when they cover a term above (e.g., meter,
syncopation, modes) — that is welcome.

# SOURCE QUALITY RULES (strict)
1. Prefer AUTHORED and INSTITUTIONAL sources: ethnomusicology journals and theses, university and
   conservatory material, open textbooks, national musicology institutes, IPHAN, UNESCO ICH
   nomination files, national libraries/archives (BN Digital, Gallica, Biblioteca Nacional de
   España), Smithsonian Folkways, encyclopedias with signed entries.
2. EXCLUDE: SEO blogs, content farms, AI-generated pages, sellers' marketing, Scribd/slide decks,
   unsourced listicles, and "exotic" generalizations about any tradition.
3. Every item must be VERIFIED: you must have actually opened the URL. Never invent a title,
   author, year or URL. If you cannot confirm something, put it in "Não verificado".
4. NotebookLM ingests readable text (web page, PDF, YouTube with transcript). Mark whether the
   FULL TEXT is openly readable. Paid books go to Part E, not to the main table.
5. Prefer depth and precision over breadth: a thesis chapter that describes the rhythmic pattern
   in notation beats a general overview.
6. Target 60–100 items in the main table: 4–9 per family (more for F1 and F2, which have many
   rhythms) plus 10–20 for the basic terms. Prefer sources in the language of the tradition
   (Portuguese, Spanish, French, Russian) when they are better than English ones.

# OUTPUT (write the whole report in Brazilian Portuguese, pt-BR)
Part A — Resumo executivo (≤ 15 linhas): what is well covered by open sources, what is weak,
which families lack good open sources, and the 10 most important sources to load first.

Part B — Tabela principal, one row per source, grouped by family F1–F10 and then T (terms), with
EXACTLY these columns (keep the column names in Portuguese as written):
| id | familia | aspectos_cobertos | prioridade (1-3) | titulo | autor_instituicao | tipo | ano | idioma | url | formato | acesso | nivel | por_que_importa |
- id: F1-01, F1-02, ..., T-01, T-02, ...
- familia: F1..F10 or T
- aspectos_cobertos: which of the aspects it covers (compasso · andamento · modo · harmonia ·
  instrumentos · canto · forma · origem · reconhecer de ouvido · confusões), or the terms (for T)
- tipo: livro-texto aberto | capítulo | tese/dissertação | artigo revisado | documento oficial |
  dossiê de patrimônio | enciclopédia | encarte/guia de escuta | curso universitário | outro
- idioma: pt | es | fr | ru | en | other
- formato: HTML | PDF | YouTube | outro   · acesso: aberto | pago | cadastro
- nivel: leigo | intermediário | técnico
- por_que_importa: one sentence on what the user learns from it (be concrete: "describes the
  chamamé's 6/8 against 3/4 accompaniment with notated examples").

Part C — Mapa de confusões: for each pair the user is likely to confuse (at least: chamamé ×
vanera gaúcha; chamamé × guarânia; milonga × tango; vanera × xote; toada × moda de viola;
cateretê × cururu; fado de Lisboa × fado de Coimbra; bolero cubano × bolero mexicano; valse
musette × valsa brasileira/seresta; baião × xote), one line on the audible difference, with the
id(s) of the source(s) that support it. If no verified source supports a distinction, say so.

Part D — Divergências entre fontes (meter, tempo, origin, naming) with who says what.

Part E — Não verificado (what you tried) · Fontes descartadas relevantes (why) · Livros pagos
recomendados (8–12, one line each).

Part F — The main table again as a single CSV block (semicolon-separated, UTF-8, header row
included), so it can be merged automatically with other researchers' results. Keep the full URL
in the CSV.
```

---

## VERSÃO CONDENSADA — NotebookLM Deep Research (duas rodadas)

Em inglês, porque funciona como consulta de busca; o escopo é largo demais para uma só, então vão
duas rodadas no mesmo notebook.

**Rodada 1 — Brasil e Prata (F1, F2, F5, F6, F9) + termos:**

```text
Authoritative open sources (ethnomusicology theses and articles from Brazilian, Argentine and Uruguayan universities, IPHAN and UNESCO heritage files, national musicology institutes, open music theory textbooks) that describe precisely, with rhythmic patterns, meter, tempo, modes, harmony, instruments and singing style, how to recognize by ear and tell apart: Brazilian música caipira rhythms (moda de viola, toada, cururu, cateretê, pagode de viola, guarânia, rasqueado, recortado, cana-verde, calango, fandango caiçara; viola caipira tunings and strumming); chamamé (Corrientes, 6/8 sesquiáltera), milonga campera and ciudadana, vanera/vaneirão and chimarrita of Rio Grande do Sul, Paraguayan polca and guarania; bossa nova guitar batida and extended-chord harmony; choro, modinha, seresta, samba de breque; forró, baião, xote and the Northeastern Brazilian modes (Mixolydian, Lydian-dominant, Dorian). Also open didactic definitions of meter, compound vs simple time, 6/8, hemiola, syncopation, tresillo 3+3+2, church modes, seventh chords and cadence. Exclude blogs, SEO content and sellers.
```

**Rodada 2 — Ibéria, França, Prata urbano, Caribe/México, Rússia (F3, F4, F7, F8, F10):**

```text
Authoritative open sources (ethnomusicologists, university theses, national musicology institutes, UNESCO heritage files, national libraries, Smithsonian Folkways notes) that describe precisely, with meter, rhythmic pattern, tempo, mode, harmony, instruments, singing style, form and social setting, how to recognize by ear and tell apart: Lisbon vs Coimbra fado (guitarra portuguesa, fado menor, corrido, mouraria); flamenco palos (soleá, seguiriya, bulería, alegrías, tangos, fandangos), the 12-beat compás, Phrygian mode and Andalusian cadence; tango (marcato, síncopa, arrastre, bandoneon) vs milonga vs vals criollo; Cuban vs Mexican bolero (cinquillo, requinto, trio romántico); French chanson réaliste, valse musette and bal musette accordion; Russian lament (plach, prichitanie), chastushka, byliny, znamenny chant, balalaika and bayan. Exclude blogs, travel sites and exoticizing generalizations.
```
