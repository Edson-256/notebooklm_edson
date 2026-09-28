# Prompt de deep research — Teoria musical para escuta crítica

- **Tarefa:** `notebooklm_edson-c0x3` · criado 2026-09-27 · pedido da sessão `musica-composicao-71`
  (repo `musica_composicao`), pauta aprovada pelo Edson.
- **Uso:** o mesmo prompt vai ao ChatGPT (Deep Research, o Edson cola), a um agente Claude e — em
  versão condensada, porque o campo do NotebookLM é curto — ao Deep Research do NotebookLM (Gemini).
- **Idioma:** instruções em inglês, saída em pt-BR (regra do ecossistema).
- **Método:** igual ao da Perícia (`projetos/medicina/pericia_medica/deep_research/`): três
  pesquisas → consolidação com decisão e motivo por fonte (CSV) → aprovação do Edson → notebook.
- **Onde colar o resultado do ChatGPT:** `01_chatgpt/resultado.md` (nesta pasta).

---

## PROMPT COMPLETO (copiar daqui até o fim da seção)

```text
# ROLE
You are a research librarian with expertise in music-theory pedagogy, music perception and
cognition, audio production, songwriting and lyric craft, song translation, and ethnomusicology.
You are selecting the source library for a Google NotebookLM notebook titled "Teoria musical
para escuta crítica" (Music theory for critical listening).

# WHO WILL USE IT AND FOR WHAT
The user is a Brazilian surgical oncologist: highly literate, scientifically trained, an
eclectic listener, but a layman in music theory (he once read basic keyboard notation and has
forgotten it). He is about to evaluate ~850 songs from his own collection. The songs were
generated with an AI music tool (Suno) from literary works — Dante's Divine Comedy, Victor Hugo's
Les Contemplations, Quo Vadis, Don Quixote, William Blake, among others — in Portuguese (Brazil),
French, Italian, Polish, Russian and other languages, and in many genres and world traditions.
He likes almost everything he hears and wants to move from intuition to explicit criteria: to know
WHAT to listen for in each item of the listening sheet below.

The notebook will be used in two ways:
1. To generate a series of instructional AUDIO episodes (15–20 min each) in Brazilian Portuguese,
   which he will listen to offline on a long flight. Audio cannot play music, so sources that
   DESCRIBE sounds in words, give guided listening examples of well-known recordings, or offer
   listening guides are especially valuable.
2. As the shared evidence base for a short written guide inside his listening tool. Guide and
   audio episodes must not contradict each other, so sources must be reliable and citable.

# THE LISTENING SHEET — every source must serve at least one of these items
- PRODUÇÃO (production): intonation/pitch accuracy · vocal clarity and diction · instrument
  separation (mixing) · space/ambience (reverb, depth, stereo) · naturalness — audible artifacts
  and "metallic" voice typical of AI-generated music.
- MELODIA: hook · arc and climax (high point) · repetition vs variation · singability (range, leaps).
- HARMONIA: tension and resolution · surprise · fitness to the genre.
- POESIA (lyrics): prosody — stressed syllable on the strong beat, in Brazilian Portuguese,
  French, Italian, Polish and Russian · rhyme, cadence and meter · concrete imagery · emotional
  truth · fidelity to the literary source text (song translation / "transcriação").
- FORMA: verse/chorus contrast · climax · beginning and ending · duration.
- CONTEXTO (social function of music): surgery/operating room, barbecue, wine cellar, wine-tasting
  club, study/reading, meditation, church/solemn occasions, driving, party/dance, dinner, study of
  world musics.
- EFEITO: personal response, rated separately from the other items.
Conceptual base already discussed with him: gestalt vs systematic examination (the clinical
analogy of a first impression followed by a structured exam); expectation and predictability
(David Huron, Sweet Anticipation; Leonard B. Meyer); the "guitar-and-voice test" (separating the
song as composition from its production); comparing two versions of the same song dimension by
dimension.

# TASK
Find the best sources for this notebook, verify that each one exists and is accessible, and return
a prioritized, deduplicated list ready to be loaded into NotebookLM. The search leads below are
LEADS TO VERIFY, not facts — confirm each one; if a lead is wrong, weak or inaccessible, say so
and propose a better source.

D1. How to listen with method — active/analytical listening pedagogy; expectation, tension and
    prediction (Huron; Meyer, Emotion and Meaning in Music); music cognition for non-specialists
    (e.g., Levitin, Sloboda, Margulis); critical listening and ear training for sound (e.g., Corey,
    Audio Production and Critical Listening); open university courses with transcripts (e.g., Yale
    Open Courses "Listening to Music", MIT OpenCourseWare music subjects); comparative (A/B)
    listening; reliability of aesthetic judgment and separating liking from evaluating.
D2. Production and mixing for listeners — frequency balance, masking, stereo image, depth and
    reverb, vocal intelligibility, pitch correction and its audible signs, loudness/compression;
    AND recent peer-reviewed or preprint research on artifacts of AI-generated music and singing
    voice (e.g., detection datasets and benchmarks of synthetic songs, typical spectral/codec
    artifacts, vocal "metallic" or phasey quality). Prefer papers with open full text (arXiv,
    ISMIR proceedings, ICASSP/Interspeech open versions).
D3. Melody — contour, arch shape and high point, motif and development, repetition and variation
    (e.g., Margulis, On Repeat), hooks in popular music (e.g., Burns' typology of hooks), range,
    tessitura and leaps (singability), memorability research.
D4. Harmony without jargon — tension/resolution, cadence, modulation, "surprise" chords,
    harmonic conventions by genre (pop/rock, folk, modal traditions, Brazilian popular music);
    open textbooks (e.g., Open Music Theory; Tagg, Everyday Tonality; Moore, Song Means;
    Temperley on rock). Prefer explanations a layperson can follow.
D5. Lyrics and text-setting — prosody and stress alignment (e.g., Pat Pattison; Luiz Tatit,
    O Cancionista, on Brazilian song); text-setting research across languages: stress-timed vs
    syllable-timed, French mute "e" and syllable counting in song, Italian verse endings (piano,
    tronco, sdrucciolo) in libretti and song, Polish fixed penultimate stress, Russian mobile
    stress; rhyme and meter; concrete imagery; song translation and singability (e.g., Peter Low's
    "pentathlon principle"; Johan Franzon; Haroldo de Campos on "transcriação"); setting canonical
    poetry to music (art song, chanson, poesia musicada).
D6. Form — verse/chorus/bridge, sectional contrast, build-up and climax, intros and endings,
    song duration (including research on trends in song length); open primers on form in popular
    music (e.g., Covach; Music Theory Online articles).
D7. Music and context (social function) — functions of music (e.g., Merriam; DeNora, Music in
    Everyday Life); peer-reviewed evidence on music in the OPERATING ROOM (effects on surgeons,
    team communication, noise — systematic reviews preferred); background music in restaurants
    and wine perception/sales (e.g., North & Hargreaves; Spence on crossmodal wine–music effects);
    music while reading/studying (meta-analyses; the irrelevant-speech effect of lyrics); music for
    meditation and relaxation; liturgical/sacred music norms (e.g., Vatican II, Sacrosanctum
    Concilium ch. VI; Musicam Sacram 1967 — official texts on vatican.va); music and driving;
    groove and danceability (e.g., Janata; Witek); dinner/ambient music.
D8. World traditions present in the collection — for EACH, find 1–3 sources that help a Brazilian
    ear understand what to listen for (scale/mode system, rhythm, instruments, vocal style, form,
    social setting), written by ethnomusicologists, musicians of the tradition, or institutions:
    Turkish/Arabic (oud, ney, makam/maqam, microtones) · Russian (znamenny chant, bylina,
    chastushka, lament/plach, khorovod, Russian-Gypsy romance, balalaika/bayan) · Polish (dumka,
    oberek, kołysanka) · fado (Lisbon and Coimbra) · flamenco, cante jondo and saeta · tango ·
    klezmer (doina, bulgar) · rebetiko · qawwali · Hindustani raga · gamelan · enka, shakuhachi,
    koto · griot/jali and kora · highlife and afrobeat · gnawa · Byzantine chant · Georgian and
    Bulgarian polyphony · Andalusian (al-Andalus/nuba) music · morna.
    Good leads: UNESCO Intangible Cultural Heritage nomination pages (authored, official, open);
    Smithsonian Folkways liner notes and lesson plans; textbooks such as Titon (Worlds of Music),
    Bakan (World Music: Traditions and Transformations), Nettl, the Garland Encyclopedia of World
    Music; specialist references (e.g., maqamworld.com by Johnny Farraj; Scott Marcus on Arab
    music; Sumarsam on gamelan; Gail Holst on rebetiko; Regula Qureshi on qawwali; Rui Vieira Nery
    on fado). Where helpful, bridge to Brazilian references a Brazilian listener already knows
    (e.g., modal scales in Northeastern Brazilian music).
D9. Brazilian-Portuguese sources — good didactic material in Portuguese on music appreciation,
    song (canção), prosody and harmony (e.g., Tatit; José Miguel Wisnik, O som e o sentido; Bohumil
    Med, Teoria da Música; Mário de Andrade, Ensaio sobre a música brasileira — check public-domain
    status and open copies), university repositories (USP, UNICAMP, UFRJ, SciELO).

# SOURCE QUALITY RULES (strict)
1. Prefer AUTHORED and INSTITUTIONAL sources: university and conservatory courseware, open
   textbooks, peer-reviewed journals (e.g., Music Perception, Psychology of Music, Musicae
   Scientiae, Journal of New Music Research, Music Theory Online — open access, Ethnomusicology,
   Popular Music, Translation journals), ISMIR/ICASSP proceedings, encyclopedias with signed
   entries, UNESCO, Smithsonian Folkways, national libraries/archives, official Vatican texts.
2. EXCLUDE: SEO blogs, content farms, AI-generated pages, course/plugin sellers' marketing,
   Scribd/slide decks, unsourced listicles, and "exotic" generalizations or orientalist clichés
   about non-Western traditions (e.g., "Eastern music is mystical", "quarter tones everywhere").
3. Every item must be VERIFIED: you must have actually opened the URL. Never invent a title,
   author, year or URL. If you cannot confirm something, put it in the "Não verificado" section.
4. NotebookLM ingests readable text (a web page, a PDF, a YouTube video with transcript). Mark
   whether the FULL TEXT is openly readable. Paid books go to a separate section (Part E) — they
   may still be worth acquiring and digitizing, but do not put them in the main table.
5. Prefer depth over breadth: a complete open chapter or course is better than a short summary.
6. Target 50–90 items in the main table, prioritized, covering all domains D1–D9 and every
   tradition listed in D8. The notebook can hold up to 300 sources of up to 500,000 words each.

# OUTPUT (write the whole report in Brazilian Portuguese, pt-BR)
Part A — Resumo executivo (≤ 15 linhas): what is well covered by open sources, what is weak, and
the 10 most important sources to load first.

Part B — Tabela principal, one row per source, grouped by domain D1–D9, with EXACTLY these columns
(keep the column names in Portuguese as written):
| id | dominio | item_da_ficha | prioridade (1-3) | titulo | autor_instituicao | tipo | ano | url | formato | acesso | nivel | por_que_importa | episodio_sugerido |
- id: D1-01, D1-02, ...
- item_da_ficha: which sheet item(s) it serves (e.g., "Poesia: prosódia"; "Contexto: cirurgia")
- tipo: livro-texto aberto | capítulo | curso universitário | artigo revisado | revisão sistemática | anais | enciclopédia | documento oficial | guia de escuta | outro
- formato: HTML | PDF | YouTube | outro   · acesso: aberto | pago | cadastro
- nivel: leigo | intermediário | técnico
- por_que_importa: one sentence on what the listener learns to hear from it.
- episodio_sugerido: 1 método · 2 produção/mixagem · 3 melodia · 4 harmonia · 5 letra
  (prosódia, rima, métrica, transcriação) · 6 forma · 7 contexto/função social · 8+ tradições do mundo

Part C — "Não verificado": items you believe exist but could not confirm, with what you tried.

Part D — Fontes descartadas relevantes: notable items you rejected and why.

Part E — Livros pagos recomendados (fora da tabela principal): the 10–15 books most worth buying
for this purpose, with one line each on why.

Part F — The main table again as a single CSV block (semicolon-separated, UTF-8, header row
included), so it can be merged automatically with other researchers' results.
```

---

## VERSÃO CONDENSADA — NotebookLM Deep Research (duas rodadas)

Diferente da Perícia, aqui fica em **inglês**: a maior parte das boas fontes (musicologia,
cognição, etnomusicologia) está em inglês, e o texto funciona como consulta de busca. O escopo é
largo demais para uma consulta só, então vão **duas rodadas** no mesmo notebook.

**Rodada 1 — escuta, produção, melodia, harmonia, letra, forma, contexto:**

```text
Open, authored, didactic sources for a layperson learning critical listening of songs: active/analytical listening pedagogy and open university courses with transcripts (Yale Listening to Music, MIT OpenCourseWare); musical expectation (Huron, Meyer); critical listening for audio production (mixing, masking, reverb, vocal clarity, pitch correction); research on audible artifacts of AI-generated music and singing voice (ISMIR, arXiv); melody (contour, climax, hooks, repetition, singability); harmony without jargon (tension/resolution, cadences, genre conventions; Open Music Theory, Tagg Everyday Tonality); lyrics and text-setting: prosody and stress alignment in Portuguese, French, Italian, Polish and Russian song, rhyme and meter, song translation and singability (Peter Low pentathlon, Franzon, Tatit O Cancionista); form in popular song (verse/chorus, climax, song length; Music Theory Online); social functions of music (Merriam, DeNora) and evidence on music in the operating room, restaurants and wine, studying/reading, meditation, liturgical music (Sacrosanctum Concilium, Musicam Sacram), driving, groove and dance. Prefer university courseware, open textbooks, peer-reviewed journals and systematic reviews. Exclude blogs, SEO content, course sellers.
```

**Rodada 2 — tradições do mundo:**

```text
Authoritative open sources (ethnomusicologists, UNESCO Intangible Cultural Heritage pages, Smithsonian Folkways liner notes and lesson plans, university material) explaining what a listener should hear in: Arabic and Turkish maqam/makam, oud, ney, microtones; Russian znamenny chant, bylina, chastushka, lament, khorovod, Russian-Gypsy romance, balalaika and bayan; Polish dumka, oberek, kołysanka; Lisbon and Coimbra fado; flamenco, cante jondo, saeta; tango; klezmer doina and bulgar; rebetiko; qawwali; Hindustani raga; gamelan; enka, shakuhachi, koto; griot/jali and kora; highlife and afrobeat; gnawa; Byzantine chant; Georgian and Bulgarian polyphony; Andalusian nuba; Cape Verdean morna. For each: scale or mode system, rhythm, instruments, vocal style, form and social setting. Exclude blogs, travel sites and exoticizing generalizations.
```
