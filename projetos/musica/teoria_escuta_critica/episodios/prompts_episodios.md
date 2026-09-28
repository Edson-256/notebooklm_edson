# Prompts dos 10 episódios — Teoria musical para escuta crítica

- **Tarefa:** `notebooklm_edson-c0x3` · lista de episódios aprovada pelo Edson em 2026-09-28
- **Como é usado:** `gerar_episodios.py` lê este arquivo. O bloco `COMMON` vai no início de todo prompt;
  o bloco de cada episódio vem em seguida. Fontes de cada episódio = as do notebook cujo título começa
  com `EpNN ·` (mais as extras indicadas em `extra_sources`).
- **Idioma:** instruções em inglês; saída em pt-BR (diretiva no prompt + `--language pt-BR`).
- **Formato:** `deep_dive`, duração `default` (~15–20 min). Teto do campo de foco: 10.000 caracteres.

## COMMON

```text
SERIES: "Teoria musical para escuta crítica" — a 10-episode audio course. Say the episode number and title at the start.

LISTENER: a Brazilian surgical oncologist — highly educated, scientifically minded, an eclectic listener, but a LAYMAN in music theory (he once read basic keyboard notation and forgot it). He is about to rate ~850 songs from his own collection, generated with an AI music tool (Suno) from literary works (Dante, Victor Hugo's Les Contemplations, Quo Vadis, Don Quixote, William Blake and others), sung in Brazilian Portuguese, French, Italian, Polish, Russian and more, across many genres and world traditions. He likes almost everything; he wants to move from intuition to explicit criteria — to know WHAT to listen for in each item of his listening sheet. He will hear this on a long flight, with no score and no way to play examples.

OUTPUT LANGUAGE: every word MUST be in Brazilian Portuguese (pt-BR). Technical terms may be said in their original language once, immediately followed by a plain Portuguese explanation.

HOW TO TEACH:
- Plain language for an intelligent layperson. Never use a technical term without explaining it in everyday words the first time.
- Audio cannot play music: DESCRIBE sounds in words and point to well-known recordings or familiar Brazilian songs the listener can recall later. Only cite a specific recording when a source mentions it or it is universally known; never invent details about a recording.
- Clinical analogy the listener already uses: first the overall impression (gestalt), then a systematic examination item by item — like a physical exam. Use it where it helps, without overdoing it.
- Keep "how good is it" separate from "how much I like it" (the EFEITO item is rated separately).
- End with a short spoken checklist: 3 to 6 concrete questions he can ask himself while listening to one of his songs for this episode's topic.
- Ground every claim in the notebook sources. Do not invent studies, numbers, dates or quotations. When the sources disagree or evidence is weak, say so.
- Do not re-explain the whole series; a one-sentence link to the previous episode is enough.
```

## Ep01 — Como ouvir com método

```text
EPISODE 1 — "Como ouvir com método".
Goal: give the listener a method for critical listening before any technical topic.
Cover: (1) passive vs active/analytical listening — what changes when you listen with a question in mind; (2) expectation and prediction as the engine of musical emotion: we learn the statistical "grammar" of a style by exposure and constantly predict what comes next; tension, surprise and resolution come from confirming or breaking those predictions (explain in plain words; the sources on statistical learning, predictive processing and the neural time-course of aesthetic experience support this); (3) familiarity bias: repeated listening increases liking regardless of complexity — so "I like it" partly means "I know it"; (4) aesthetic judgment vs emotional response: related but not identical — the reason EFEITO is rated apart; (5) knowing a song is AI-made can change the rating (if a source covers listener attribution, explain it and its implication: rate blind when possible); (6) the "guitar-and-voice test": would the song survive stripped to one voice and one instrument? This separates composition from production; (7) comparing two versions dimension by dimension; (8) a practical routine: first listen for the gestalt, then targeted listens per sheet layer (production, melody, harmony, lyrics, form, context, effect).
Use the Yale "Listening to Music" lectures as a model of a teacher guiding the ear.
```

## Ep02 — Produção e mixagem (inclui artefatos de IA)

```text
EPISODE 2 — "Produção e mixagem: o que se ouve além da canção".
Map to the sheet items: afinação (intonation) · clareza da voz e dicção · separação dos instrumentos (mixagem) · espaço/ambiência · naturalidade (artefatos, voz "metálica").
Cover in listener's terms: what a mix is; frequency balance and masking (why the voice can get "buried"); stereo image and depth (front/back, left/right); reverb and room — how much space sounds natural vs "washed out"; compression and the loudness war (why some tracks sound loud but flat and tiring); vocal intelligibility and what listeners report as the factors that make sung words understandable; audible pitch correction.
Then AI-generated music specifically: what research on detecting AI songs (SONICS, the Fourier explanation of AI-music artifacts, singing-voice deepfake detection, the AI music "arms race" paper, song-aesthetics evaluation) says about typical artifacts — describe them in words a listener can recognize (e.g., metallic/phasey voice, smeared consonants, unstable timbre, spectral "shimmer"), and be honest about what the ear can and cannot detect.
Checklist at the end: questions for each production item.
```

## Ep03 — Melodia

```text
EPISODE 3 — "Melodia: gancho, arco e cantabilidade".
Map to the sheet items: gancho (hook) · arco/ponto culminante · repetição vs variação · cantabilidade (extensão, saltos).
Cover: what makes a hook (use Burns' typology of hooks in popular records) and what makes a melody "stick" (earworm research: melodic features that predict involuntary musical imagery); contour and the arch shape; the high point/climax and where it tends to sit; motif, repetition and variation — why too much repetition bores and too little disorients; range, tessitura and leaps: what makes a line easy or hard to sing (step vs leap, how large leaps are prepared and resolved); phrase structure as "breathing". Mention the melody/harmony independence found in rock (Temperley) as a reason a melody can sound "right" even when it seems to clash with the chords.
Describe examples with familiar tunes (e.g., Happy Birthday's leap, a Brazilian refrain everyone knows) only where you are sure of the description.
```

## Ep04 — Harmonia sem jargão

```text
EPISODE 4 — "Harmonia sem jargão: tensão, surpresa e adequação ao gênero".
Map to the sheet items: tensão e resolução · surpresa · adequação ao gênero.
Cover, without assuming notation: what a chord is (several notes heard as one color); home, away and return — tonic as "home"; cadences as punctuation (full stop vs comma vs question) and phrase endings; the four-chord schemas behind countless pop songs and why they feel predictable; modal colors (songs that avoid the classic "going home" pull) and pentatonic harmony — important because many folk and world traditions in his collection are modal; what research says about harmonic surprise and pleasure (uncertainty + surprise predict enjoyment; the statistical analysis of harmonic surprise and preference); genre fit: the same progression can be perfect in pop and wrong in a Russian lament or a fado. Use Philip Tagg's Everyday Tonality ideas on "real world" tonality and modes. Bridge to Brazilian ears: the modal flavors of Northeastern Brazilian music (baião) as a familiar reference.
```

## Ep05 — Letra: prosódia, rima, métrica, transcriação

```text
EPISODE 5 — "A letra cantada: prosódia, rima, métrica e transcriação".
Map to the sheet items: prosódia (sílaba tônica no tempo forte) · rima e cadência/métrica · imagem concreta · verdade da emoção · fidelidade ao texto literário de origem (transcriação).
Cover: prosody as the fit between how words are spoken and how they are sung — stressed syllable on the strong beat, natural contour; "prosodic dissonance" (when the setting fights the words) and when it is deliberate; Luiz Tatit's idea of "figurativização" (the sung line keeps the intonation of speech) and the canção brasileira; language by language: Brazilian Portuguese; French (stress at the end of the phrase, the mute "e", French vs English text-setting rules); Italian verse types by the position of the last stress (piano, tronco, sdrucciolo) and syllable counting; Polish fixed penultimate stress; Russian mobile stress and vowel reduction in singing. IMPORTANT: do NOT claim that a language's rhythm (stress-timed vs syllable-timed) shapes the rhythm of its songs — research (Temperley, rhythmic variability in European vocal music) did not confirm it; say so if relevant.
Then rhyme, meter, concrete imagery vs abstraction, and emotional truth vs cliché. Finally song translation and adaptation: Peter Low's "pentathlon" (sense, naturalness, singability, rhythm, rhyme — trade-offs), singability, and Haroldo de Campos' "transcriação" (recreating form and effect rather than word-for-word fidelity) — how to judge a song made from Dante, Hugo or Blake: faithful to what — the words, the images, the spirit?
```

## Ep06 — Forma

```text
EPISODE 6 — "Forma: a arquitetura da canção".
Map to the sheet items: contraste verso/refrão · clímax · começo e final · duração.
Cover: the main song forms and how they developed historically (AABA, verse-chorus, bridge, prechorus — use von Appen & Frei-Hauenschild); the function of each section (verse tells, chorus sums up, prechorus builds, bridge departs, postchorus/codetta closes); teleology: how a prechorus creates the feeling of "arriving" at the chorus; contrast between sections as a quality criterion (energy, register, density, lyrics); climax placement; beginnings (how fast the song grabs you) and endings (fade-out vs real close; structural vs rhetorical closure); duration — what research on song length and on songs with over a billion streams shows descriptively (as reference, not as a rule of quality). Practical: how to map a song's form by ear on a first listen (count sections, mark where energy changes).
```

## Ep07 — Contexto e função social

```text
EPISODE 7 — "Para que serve esta música? Contexto e função social".
Map to the sheet item CONTEXTO, whose categories are: cirurgia (operating room), churrasco, adega, confraria de vinho, estudo/leitura, meditação, igreja/solene, estrada, festa/dança, jantar, estudo de músicas do mundo.
Cover: why the same song can be excellent in one setting and wrong in another; the psychological functions of music listening (self-awareness, social relatedness, arousal and mood regulation). Then setting by setting, only what the sources support:
- Operating room: the systematic review on balancing music and safety in the OR — effects on team communication, noise and performance. The listener is a surgeon and the clinical judgment is his: present the evidence and its limits plainly, without prescribing.
- Wine cellar / wine club / dinner: crossmodal matching of wine and music (Spence & Wang), wine psychology, and background music effects on dining duration, tips and bill.
- Study/reading: music with lyrics interferes with cognition; the meta-analysis of auditory distraction during reading.
- Meditation/relaxation: systematic reviews of music interventions on stress and stress recovery.
- Church/solemn: what the Catholic Church's own documents ask of sacred music (Sacrosanctum Concilium ch. VI; Musicam Sacram) — dignity, text intelligibility, participation — as criteria, not dogma.
- Road: music and driving performance.
- Party/dance: groove — syncopation and the urge to move (Witek; Janata): why medium syncopation grooves most.
Close with a matching checklist: tempo, energy, lyrics vs no lyrics, loudness, predictability — for each context.
```

## Ep08 — Tradições do mundo I: Mediterrâneo, mundo árabe e ibérico

```text
EPISODE 8 — "Tradições do mundo (1): Mediterrâneo, mundo árabe e ibérico".
Traditions: Arabic maqam and Turkish makam, oud and ney, microtones; Mevlevi music; flamenco, cante jondo and saeta; Andalusian nuba; rebetiko; Byzantine chant (and the ison drone); klezmer (doina, bulgar, its modes); fado (Lisbon and Coimbra; Artur Paredes and the Coimbra guitar); morna of Cape Verde; tango.
For EACH tradition, briefly: where and when it lives socially; its scale/mode system in plain words; rhythm; instruments and timbre; vocal style and ornamentation; typical form — and "3 things to listen for" so the listener can judge whether an AI-generated song in that style sounds idiomatic or like a cliché.
Warn against exoticism and generalizations (not "all Arab music uses quarter tones"; maqam is a system of melodic behavior, not just a scale). Build bridges to what a Brazilian ear already knows (e.g., modal melodies of the Brazilian Northeast; Mário de Andrade's reflections on Brazilian music) only where sources support it. Keep it moving: this episode covers many traditions — prioritize clarity over completeness.
```

## Ep09 — Tradições do mundo II: Leste europeu

```text
EPISODE 9 — "Tradições do mundo (2): Leste europeu — Rússia, Polônia, Geórgia, Bulgária".
Traditions: Russian znamenny chant; bylina (epic songs) and northern bylina tunes; Russian folk song traditions and polyphony; Russian-Gypsy romance; Polish oberek (and the kujawiak/mazurka family, only as the sources allow), Polish lullabies (kołysanka), folk models absorbed into Polish art song; Georgian polyphonic singing; Bulgarian archaic polyphony (Bistritsa Babi).
For EACH: social setting, mode/scale behavior, rhythm (e.g., the oberek's fast triple feel), voices and harmony (drones, parallel seconds, open fifths), vocal timbre, form — and "3 things to listen for" to judge whether an AI-generated song in that style sounds authentic.
Be explicit where the sources are thin: there is little open material here on the Russian lament (plach), khorovod, balalaika/bayan and the Polish dumka — say so instead of improvising. Two sources are in Russian and one in Polish: use them, and translate what you cite.
```

## Ep10 — Tradições do mundo III: Ásia e África

```text
EPISODE 10 — "Tradições do mundo (3): Ásia e África".
Traditions: Hindustani raga (time-of-day ragas, alap-jor-jhala, tala cycles); qawwali (Sufi devotional song, call-and-response, gradual intensification); Javanese gamelan (cyclic structure, colotomic gongs, density and tempo layers); Japanese shakuhachi (suizen — breath as practice), koto and enka; West African kora and the griot/jali tradition; Ghanaian highlife and Nigerian afrobeat (Tony Allen's drumming); Moroccan gnawa (guembri, qraqeb, trance ritual).
For EACH: social/ritual setting, pitch system, time organization (cycles vs phrases), instruments and timbre, vocal style — and "3 things to listen for" to judge whether an AI-generated song in that style sounds idiomatic or like a tourist cliché.
Note where the sources are thin (enka and koto have little open material; one enka source is in Japanese) and say so rather than filling gaps. Close the series by returning to the method of Episode 1: gestalt first, then systematic examination — now with ears for many musical worlds.
```
