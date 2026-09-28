# Consolidação dos três deep research — Teoria musical para escuta crítica

Tarefa `notebooklm_edson-c0x3` · 2026-09-28 · **aguardando aprovação do Edson**

Notebook (conta pessoal, ainda vazio): `4ac56794-d00a-436a-a446-24f1161cd9bd` —
https://notebooklm.google.com/notebook/4ac56794-d00a-436a-a446-24f1161cd9bd

## Números

- Brutos: ChatGPT 66 · Claude 90 · NotebookLM 76 citadas (de 103 achadas em 2 rodadas) = **232 linhas**
- **135 selecionadas** (P1: 88 · P2: 32 · P3: 15) — Claude 90 · ChatGPT 39 · NotebookLM 6
- 97 descartadas; motivo linha a linha em `decisao_por_fonte.csv`
- Cabe no notebook (limite do Pro: 300). Cada episódio vai usar só as fontes dele (`--source-ids`), então o
  tamanho do notebook não dilui os áudios.

## Como cada pesquisador se saiu

- **Claude (90):** todas no ar, abertas, de autoria ou institucionais. Um erro: disse que o *Everyday
  Tonality* do Tagg não é aberto — o autor publica o texto inteiro no site (conferido).
- **ChatGPT (66):** boa seleção, mas **o export perdeu todos os links** (copiado e baixado: idênticos, só
  marcas `source_ref`). Links recuperados pelo título por um agente: 63 confirmados, 3 ambíguos (fora).
  Erros de citação: Franzon 2008 dado como aberto (é pago); Pearce com periódico e ano trocados; artigo
  da TISMIR dado como anais; vários "HTML" que são PDF.
- **NotebookLM (76):** o mais fraco, como na Perícia — Scribd, cópias piratas (dokumen.pub), ResearchGate
  bloqueado, Facebook, blogs de turismo e marketing. **6 aproveitadas**, com destaque para von Appen &
  Frei-Hauenschild (2015), 83 págs. sobre a história das formas de canção.

## Divergências resolvidas na fonte

| Ponto | O que cada um disse | Verificado |
|---|---|---|
| *Everyday Tonality* (Tagg) | Claude: só capítulos-amostra · ChatGPT: aberto | **Aberto**: texto integral do ET II (~117 mil palavras) no site do autor, sem figuras nem exemplos musicais |
| Franzon, *Choices in Song Translation* (2008) | ChatGPT: PDF aberto | **Pago** (Taylor & Francis). Fica fora; resenhas abertas de Low e Franzon cobrem o "pentatlo" |
| Ritmo da língua marca o ritmo da canção? (pista do prompt) | — | Claude: Temperley (2017, *Music Perception*) achou o **contrário** do previsto. O episódio de letra não deve afirmar essa ideia |
| FakeMusicCaps como base sobre Suno | pista do prompt | Não inclui Suno/Udio. Para artefatos audíveis: **SONICS** (ICLR) e **Fourier Explanation** (ISMIR 2025) |

## Critérios aplicados

1. Texto integral aberto e legível pelo NotebookLM; autoria ou instituição identificável.
2. Fora: Scribd, cópias não autorizadas, blogs, marketing, turismo, Wikipedia, redes sociais, páginas que bloqueiam leitura.
3. Duplicata (mesma obra por dois pesquisadores): fica uma, preferindo o endereço canônico aberto.
4. Encarte escaneado sem texto: fora quando outra fonte cobre a tradição; dentro quando é a única (koto, romance cigano russo).

## Lacunas que ficam (nenhum dos três achou fonte aberta boa)

- **Enka e koto:** só um artigo em japonês (enka, 1989) e um encarte de 2 págs. (koto). Livro de referência: Yano, *Tears of Longing* (pago).
- **Rússia:** lamento (plach), khorovod, balalaica/bayan sem fonte própria. Há bylina e canção tradicional em russo, znamenny e romance cigano.
- **Polônia:** dumka sem fonte; prosódia polonesa cantada só com fonte fraca (P3).
- **Fado de Coimbra × Lisboa:** sem fonte comparativa (há Artur Paredes no Museu do Fado e a UNESCO).
- **Prosódia russa cantada:** só um artigo técnico sobre redução vocálica no canto clássico.

## Livros pagos que valem a compra (os dois pesquisadores concordam)

Ordem sugerida pelos dois: **Huron** (*Sweet Anticipation*) · **Corey** (*Audio Production and Critical
Listening*) · **Tatit** (*O Cancionista*; e Tatit & Lopes, *Elos de melodia e letra*) · **Moore** (*Song
Means*) · **Peter Low** (*Translating Song*) · Meyer · Margulis (*On Repeat*) · Wisnik (*O som e o sentido*) ·
Pattison (*Writing Better Lyrics*) · DeNora · Qureshi (qawwali) · Bakan ou Titon (world music) · Yano (enka).
Se algum for comprado e digitalizado, entra no notebook depois, pelo mesmo caminho da Perícia.

## Decisões pendentes do Edson

1. **Aprovar a seleção** (as 135 abaixo) — ou marcar o que tirar/acrescentar.
2. **Lista final de episódios.** As tradições do mundo têm 49 fontes: cabem em **3 episódios**, não 1–2.
   Proposta: (8) Mediterrâneo, mundo árabe e ibérico — maqam, oud/ney, flamenco e saeta, nuba andaluza,
   rebetiko, bizantino, klezmer, fado, morna, tango; (9) Leste europeu — russo, polonês, georgiano e
   búlgaro; (10) Ásia e África — raga, qawwali, gamelan, Japão, kora/griot, highlife/afrobeat, gnawa.
   Total: 10 episódios de 15–20 min.

## Fontes selecionadas, por episódio

P = prioridade (1 = núcleo). Número = linha em `selecionadas.json`.

### Episódio 1 · Como ouvir com método — 9 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 1 | 1 | [Statistical learning and probabilistic prediction in music cognition: mechanisms of stylistic enculturation](https://pmc.ncbi.nlm.nih.gov/articles/PMC6849749/) | Marcus T. Pearce / WIREs Cognitive Science | ChatGPT errou o periódico: é Annals of the NY Academy of Sciences (2018) |
| 40 | 1 | [MUSI 112 – Listening to Music, Lecture 1: Introduction (curso inteiro com transcrição por aula)](https://oyc.yale.edu/music/musi-112/lecture-1) | Craig Wright / Yale University (Open Yale Courses) |  |
| 42 | 1 | [Toward a Neural Chronometry for the Aesthetic Experience of Music](https://pmc.ncbi.nlm.nih.gov/articles/PMC3640187/) | Elvira Brattico, Brigitte Bogert, Thomas Jacobsen (Frontiers |  |
| 43 | 1 | [Predictive Processes and the Peculiar Case of Music](https://www.stefan-koelsch.de/papers/koelsch_vuust_friston_2018_predictive_processes_and_the_peculiar_case_of_music_trends_in_cognitive_sciences.pdf) | Stefan Koelsch, Peter Vuust, Karl Friston (Trends in Cogniti |  |
| 44 | 1 | [From perceptual rule transformation to listener attribution judgments: a blind-listening experiment on AI-gene](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1903971/full) | Junsong Chang, Yueqi Jing (Frontiers in Psychology) |  |
| 2 | 2 | [Repeated Listening Increases the Liking for Music Regardless of Its Complexity](https://pmc.ncbi.nlm.nih.gov/articles/PMC5374342/) | Guy Madison; Gunilla Schiölde (Frontiers in Neuroscience) |  |
| 3 | 2 | [Beauty Is How You Feel Inside: Aesthetic Judgments Are Related to Emotional Responses to Contemporary Music](https://pmc.ncbi.nlm.nih.gov/articles/PMC7691637/) | Frontiers in Psychology / PMC |  |
| 38 | 2 | [A palavra em movimento: algumas perspectivas teóricas para a análise de canções no âmbito da música popular](https://periodicos.ufmg.br/index.php/permusi/article/view/45185) | Conrado Vito Rodrigues Falbo |  |
| 129 | 3 | [Resenha de "O som e o sentido. Uma outra história das músicas" (José Miguel Wisnik)](https://www.scielo.br/j/ra/a/yP7KNLj6JTktTMRkbNkXj3y/?lang=pt) | Rose Satiko Gitirana Hikiji / Revista de Antropologia 43(1)  |  |

### Episódio 2 · Produção e mixagem (inclui artefatos de IA) — 10 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 4 | 1 | [Signal Processing in Mixing](https://human.libretexts.org/Courses/Pasadena_City_College/Understanding_Sound_From_Ear_to_Engineer/09%3A_The_Mixing_Process/9.07%3A_Signal_Processing_in_Mixing) | LibreTexts / Pasadena City College |  |
| 5 | 1 | [The AI Music Arms Race: On the Detection of AI-Generated Music](https://transactions.ismir.net/articles/10.5334/tismir.254) | Cros Vila / Sturm / Casini / Dalmazzo | é artigo da revista TISMIR, não dos anais |
| 46 | 1 | [SONICS: Synthetic Or Not – Identifying Counterfeit Songs](https://arxiv.org/abs/2408.14080) | Md Awsafur Rahman et al. (ICLR 2025) |  |
| 47 | 1 | [A Fourier Explanation of AI-music Artifacts](https://arxiv.org/abs/2506.19108) | Darius Afchar, Gabriel Meseguer-Brocal, Kamil Akesbi, Romain |  |
| 49 | 1 | [SongEval: A Benchmark Dataset for Song Aesthetics Evaluation](https://arxiv.org/abs/2505.10793) | Jixun Yao, Guobin Ma, Huixin Xue et al. |  |
| 50 | 1 | [Making myself understood: perceived factors affecting the intelligibility of sung text](https://pmc.ncbi.nlm.nih.gov/articles/PMC4155173/) | Philip A. Fine, Jane Ginsborg (Frontiers in Psychology 5:809 |  |
| 51 | 1 | [The Loudness War: Background, Speculation and Recommendations (AES 129th Convention)](https://www.sfxmachine.com/docs/loudnesswar/loudness_war.pdf) | Earl Vickers |  |
| 52 | 1 | [Perceptual Evaluation and Analysis of Reverberation in Multitrack Music Production (JAES 65(1/2))](http://www.brechtdeman.com/publications/pdf/jaes-DREAMS-hires.pdf) | Brecht De Man, Kirk McNally, Joshua D. Reiss | abre só por http; pode precisar subir como arquivo |
| 48 | 2 | [SingFake: Singing Voice Deepfake Detection](https://arxiv.org/abs/2309.07525) | Yongyi Zang, You Zhang, Mojtaba Heydari, Zhiyao Duan (ICASSP |  |
| 130 | 2 | [From Audio Deepfake Detection to AI-Generated Music Detection – A Pathway and Overview - arXiv](https://arxiv.org/html/2412.00571v3) | arXiv (revisão) |  |

### Episódio 3 · Melodia — 8 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 53 | 1 | [A typology of 'hooks' in popular records](https://www.tagg.org/xpdfs/burns87.pdf) | Gary Burns (Popular Music 6/1, pp. 1-20) |  |
| 54 | 1 | [Dissecting an Earworm: Melodic Features and Song Popularity Predict Involuntary Musical Imagery](https://www.apa.org/pubs/journals/releases/aca-aca0000090.pdf) | Kelly Jakubowski, Sebastian Finkel, Lauren Stewart, Daniel M |  |
| 55 | 1 | [7.3: Melody and Phrasing (Open Music Theory 2e)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/07%3A_Popular_Music/7.03%3A_Melody_and_Phrasing) | Mark Gotham et al. / VIVA – LibreTexts (CC BY-SA 4.0) |  |
| 56 | 1 | [7.1 Melodic Material: Range, Interval Structure, Gesture (Comprehensive Musicianship: A Practical Resource)](https://iastate.pressbooks.pub/comprehensivemusicianship/chapter/7-1-melodic-material-tutorial/) | Randall Harlow, Heather Peyton, Jonathan Schwabe, Daniel Swi |  |
| 57 | 2 | [The melodic-harmonic 'divorce' in rock](https://davidtemperley.com/wp-content/uploads/2015/11/temperley-pm07.pdf) | David Temperley (Popular Music 26/2, pp. 323-342) |  |
| 6 | 3 | [Predicting Variation of Folk Songs: A Corpus Analysis Study on the Memorability of Melodies](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2017.00621/full) | Janssen / Burgoyne / Honing |  |
| 7 | 3 | [Intervals as musical fingerprints: perceptual and pedagogical insights — a scoping review](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2026.1740840/full) | Mustafa Kendüzler |  |
| 45 | 3 | [Review of Elizabeth Margulis, On Repeat: How Music Plays the Mind](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.albrecht.html) | Joshua Albrecht (Music Theory Online 20.4) |  |

### Episódio 4 · Harmonia sem jargão — 12 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 8 | 1 | [Introduction to Harmony, Cadences, and Phrase Endings](https://viva.pressbooks.pub/openmusictheory/chapter/intro-to-harmony/) | Open Music Theory |  |
| 9 | 1 | [Four-Chord Schemas](https://viva.pressbooks.pub/openmusictheory/chapter/4-chord-schemas/) | Open Music Theory |  |
| 11 | 1 | [Everyday Tonality](https://tagg.org/html/FFabBk.htm) | Philip Tagg | texto integral do Everyday Tonality II publicado pelo próprio autor (HTML, ~117 mil palavras, sem exemplos musicais nem figuras) — conferido 28/09 |
| 41 | 1 | [MUSI 112 – Lecture 8: Bass Patterns: Blues and Rock](https://oyc.yale.edu/music/musi-112/lecture-8) | Craig Wright / Yale University (Open Yale Courses) |  |
| 58 | 1 | [7.7: Introduction to Harmonic Schemas in Pop Music (Open Music Theory 2e)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/07%3A_Popular_Music/7.07%3A_Introduction_to_Harmonic_Schemas_in_Pop_Music) | Mark Gotham et al. / VIVA – LibreTexts (CC BY-SA 4.0) |  |
| 59 | 1 | [7.12: Modal Schemas (Open Music Theory 2e)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/07%3A_Popular_Music/7.12%3A_Modal_Schemas) | Mark Gotham et al. / VIVA – LibreTexts (CC BY-SA 4.0) |  |
| 60 | 1 | [7.6: Cadence (Understanding Basic Music Theory)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Understanding_Basic_Music_Theory_(Schmidt-Jones)/07%3A_Harmony_and_Form/7.06%3A_Candence) | Catherine Schmidt-Jones / OpenStax CNX – LibreTexts (CC BY 3 |  |
| 62 | 1 | [A Statistical Analysis of the Relationship between Harmonic Surprise and Preference in Popular Music](https://pmc.ncbi.nlm.nih.gov/articles/PMC5435755/) | Scott A. Miles, David S. Rosen, Norberto M. Grzywacz (Fronti |  |
| 10 | 2 | [Pentatonic Harmony](https://viva.pressbooks.pub/openmusictheory/chapter/pentatonic-harmony/) | Open Music Theory |  |
| 61 | 2 | [Everyday Tonality II – cap. 4: Non-heptatonic modes (capítulo-amostra gratuito)](https://tagg.org/bookxtrax/FFabBk08/EvTon04Modes2Sample.pdf) | Philip Tagg / Mass Media Music Scholars' Press |  |
| 63 | 2 | [Uncertainty and Surprise Jointly Predict Musical Pleasure and Amygdala, Hippocampus, and Auditory Cortex Activ](https://www.stefan-koelsch.de/papers/cheung_harrison_meyer_pearce_haynes_koelsch_2019_uncertainty_and_surprise_jointly_predict_musical_pleasure_and_amygdala_hippocampus_and_auditory_cortex_activity_current_biology_29.pdf) | Vincent Cheung, Peter Harrison, Lars Meyer, Marcus Pearce, J |  |
| 128 | 2 | [Procedimentos Modais na Música Brasileira: do campo étnico do Nordeste ao popular da década de 1960 (tese)](https://teses.usp.br/teses/disponiveis/27/27157/tde-13122009-102355/publico/Tesefinal.pdf) | Paulo José de Siqueira Tiné / ECA-USP |  |

### Episódio 5 · Letra: prosódia, rima, métrica, transcriação — 25 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 13 | 1 | [Comparing Musical Textsetting in French and in English Songs](https://johnhalle.com/musical.writing.technical/fdell-jhalle-comparing-settings-4.pdf) | François Dell / John Halle | manuscrito do autor (2005); o capítulo publicado é fechado |
| 14 | 1 | [Intonation of French Songs: From Text to Tune](https://www.isca-archive.org/speechprosody_2004/martin04_speechprosody.pdf) | Philippe Martin / ISCA |  |
| 16 | 1 | [Versificazione](https://www.treccani.it/enciclopedia/versificazione_(Enciclopedia-dell'Italiano)/) | Claudio Ciociola / Treccani |  |
| 64 | 1 | [Prosody in Music and Songwriting](https://online.berklee.edu/takenote/prosody-in-music-and-songwriting/) | Pat Pattison / Berklee Online (Take Note) |  |
| 65 | 1 | [Prosodic Dissonance (MTO 30.2)](https://mtosmt.org/issues/mto.24.30.2/mto.24.30.2.smith.html) | Eron Smith / Society for Music Theory |  |
| 66 | 1 | [Melodia, texto e O cancionista, de Luiz Tatit: novos rumos para os estudos da música popular brasileira (trad.](https://revistas.usp.br/teresa/article/download/116391/113976) | David Treece (King's College London), Teresa – Revista de Li |  |
| 67 | 1 | ["Sous le rythme de la chanson": Rhythm, Text, and Diegetic Performance in Nineteenth-Century French Opera (MTO](https://www.mtosmt.org/issues/mto.15.21.3/mto.15.21.3.pau.html) | Andrew Pau / Society for Music Theory |  |
| 68 | 1 | [Guida alla identificazione metrica dei versi italiani](http://box.dar.unibo.it/files/didattica/Guida_alla_identificazione_metrica_dei_versi_italiani.pdf) | Marco Beghelli / Università di Bologna (DAR) | abre só por http; pode precisar subir como arquivo |
| 71 | 1 | [Transcriação e crítica literária – Haroldo de Campos e o papel epistêmico do ícone](https://www.scielo.br/j/ct/a/jK4t8rYzjSDdPvqs7RHvBww/?format=html&lang=pt) | Ana Fernandes, João Queiroz, Cadernos de Tradução (SciELO) |  |
| 72 | 1 | [Resenha de Low, P. (2017) Translating Song: Lyrics and Texts](https://www.jostrans.soap2.ch/issue29/rev_low.pdf) | Marta Mateo (Universidad de Oviedo), JoSTrans 29 |  |
| 124 | 1 | [Luiz Tatit: A forma exata da canção (entrevista)](https://revistapesquisa.fapesp.br/luiz-tatit-a-forma-exata-da-cancao/) | Márcio Ferrari / Revista Pesquisa FAPESP n. 246 |  |
| 125 | 1 | [Ordem e desordem em "Fora da Ordem"](https://revistas.usp.br/teresa/en/article/download/116366/113955/213351) | Ivã Carlos Lopes, Luiz Tatit / Teresa – Revista de Literatur |  |
| 126 | 1 | [Fundamentos da semiótica da canção aplicados à musicalização de adultos](https://revistaabem.abem.mus.br/revistaabem/article/download/1159/640/3942) | Kristoff Silva (UFSJ) / Revista da ABEM |  |
| 127 | 1 | [Canto falado: relações entre música e prosódia](https://anppom.org.br/anais/anaiscongresso_anppom_2017/4643/public/4643-16355-1-PB.pdf) | Gabriela Ricci (UFPB) / Anais do XXVII Congresso da ANPPOM |  |
| 12 | 2 | [Prosodic Structure as a Parallel to Musical Structure](https://pmc.ncbi.nlm.nih.gov/articles/PMC4687474/) | Heffner / Slevc |  |
| 17 | 2 | [Pelas redes da tradução: um estudo do conceito de transcriação, de Haroldo de Campos...](https://revistaseletronicas.pucrs.br/ojs/index.php/letronica/article/view/32201) | Ana Carolina Lopes Costa |  |
| 37 | 2 | [A canção e a oralização: sílaba, palavra e frase](https://www.teses.usp.br/teses/disponiveis/8/8139/tde-26062019-103725/publico/2019_MarceloSegreto_VCorr.pdf) | Marcelo Costa Segreto / USP |  |
| 69 | 2 | [Vowel reduction in Russian classical singing: the case of unstressed /a/ after palatalised consonants](https://www.italian-journal-linguistics.com/app/uploads/2021/05/4_Konoshenko.pdf) | Maria Konoshenko (RGGU), Italian Journal of Linguistics 32.1 |  |
| 70 | 2 | [Rhythmic Variability in European Vocal Music](https://davidtemperley.com/wp-content/uploads/2017/11/temperley-mp17.pdf) | David Temperley (Music Perception 35(2):193-199) |  |
| 133 | 2 | [Song Lyrics Adaptations: Computational Interpretation of the Pentathlon Principle - ACL Anthology](https://aclanthology.org/2025.nlp4dh-1.11.pdf) | ACL Anthology (NLP4DH 2025) |  |
| 15 | 3 | [Stress Deafness in a Language with Fixed Word Stress: An ERP Study on Polish](https://pmc.ncbi.nlm.nih.gov/articles/PMC3485581/) | Domahs / Knaus / Orzechowska / Wiese |  |
| 39 | 3 | [Estudo semiótico de percursos passionais no samba-canção](https://www.scielo.br/j/ld/a/V4gMmgRLmDKbH6Rc69nhzFq/?lang=pt) | Álvaro Antônio Caretta |  |
| 73 | 3 | [Resenha de Franzon, Greenall, Kvam & Parianou (eds.), Song Translation: Lyrics in Contexts](https://www.jostrans.org/article/download/7993/7840?inline=1) | Karen Wilson de Roze, JoSTrans |  |
| 74 | 3 | [The Music of Poetry: Chopin's Polish Songs](https://interlude.hk/the-music-of-poetry-chopins-polish-songs/) | Georg Predota / Interlude (revista de música clássica) |  |
| 134 | 3 | [Make it sing? - / CIOL (Chartered Institute of Linguists)](https://www.ciol.org.uk/make-it-sing) | Chartered Institute of Linguists |  |

### Episódio 6 · Forma — 8 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 75 | 1 | [7.4: Introduction to Form in Popular Music (Open Music Theory 2e)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/07%3A_Popular_Music/7.04%3A_Introduction_to_Form_in_Popular_Music) | Mark Gotham et al. / VIVA – LibreTexts (CC BY-SA 4.0) |  |
| 76 | 1 | [7.6: Verse-Chorus Form (Open Music Theory 2e)](https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/07%3A_Popular_Music/7.06%3A_Verse-Chorus_Form) | Mark Gotham et al. / VIVA – LibreTexts (CC BY-SA 4.0) |  |
| 77 | 1 | [Teleology in Verse–Prechorus–Chorus Form, 1965–2020 (MTO 28.3)](https://mtosmt.org/issues/mto.22.28.3/mto.22.28.3.nobile.html) | Drew Nobile / Society for Music Theory |  |
| 78 | 1 | [Structural and Rhetorical Closure in 1970s Rock Songs (MTO 32.1)](https://www.mtosmt.org/issues/mto.26.32.1/mto.26.32.1.braae.html) | Nick Braae / Society for Music Theory |  |
| 79 | 1 | [On popular music and media: Analyzing changes in compositional practices and music listening choice behavior u](https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=osu1523284232353463&disposition=inline) | Hubert Léveillé Gauvin / The Ohio State University (orient.  |  |
| 131 | 1 | [AABA, Refrain, Chorus, Bridge, Prechorus - Song Forms and their Historical Development](https://d-nb.info/1069484245/34) | Ralf von Appen; Markus Frei-Hauenschild (Samples, GfPM, 2015 |  |
| 18 | 2 | [Quantitative Analysis of Songs with Over a Billion Streams](https://hrcak.srce.hr/336418) | Habjanec / Bagić Babac |  |
| 132 | 3 | [MTO 28.2: Stroud, Codetta and Anthem Postchorus Types - Music Theory Online](https://www.mtosmt.org/issues/mto.22.28.2/mto.22.28.2.stroud.html) | Stroud / Music Theory Online |  |

### Episódio 7 · Contexto e função social — 14 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 19 | 1 | [Wine and Music (I): On the Crossmodal Matching of Wine and Music](https://flavourjournal.biomedcentral.com/articles/10.1186/s13411-015-0045-x) | Spence / Wang |  |
| 20 | 1 | [Should We Turn off the Music? Music with Lyrics Interferes with Cognitive Tasks](https://pmc.ncbi.nlm.nih.gov/articles/PMC10162369/) | Souza / Barbosa |  |
| 80 | 1 | [The psychological functions of music listening](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2013.00511/full) | Thomas Schäfer, Peter Sedlmeier, Christine Städtler, David H |  |
| 81 | 1 | [Practical Approaches to Balancing Music and Safety in the Operating Room: A Systematic and Narrative Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC13155495/) | S. K. Chandawarkar, I. Amjad (Plast Reconstr Surg Glob Open) |  |
| 82 | 1 | [Wine psychology: basic & applied](https://pmc.ncbi.nlm.nih.gov/articles/PMC7221102/) | Charles Spence / University of Oxford (Cognitive Research: P |  |
| 84 | 1 | [Auditory Distraction During Reading: A Bayesian Meta-Analysis of a Continuing Controversy](https://pmc.ncbi.nlm.nih.gov/articles/PMC6139986/) | Martin R. Vasilev, Julie A. Kirkby, Bernhard Angele (Perspec |  |
| 85 | 1 | [Effects of music interventions on stress-related outcomes: a systematic review and two meta-analyses](https://pure.uva.nl/ws/files/58927620/Effects_of_music_interventions_on_stress_related_outcomes_a_systematic_review_and_two_meta_analyses.pdf) | Martina de Witte, Anouk Spruit, Susan van Hooren, Xavier Moo |  |
| 87 | 1 | [Constitution on the Sacred Liturgy Sacrosanctum Concilium (cap. VI, "Sacred Music", arts. 112–121)](https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19631204_sacrosanctum-concilium_en.html) | Concílio Vaticano II / Santa Sé (vatican.va) |  |
| 88 | 1 | [Instruction on Music in the Liturgy Musicam Sacram](https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_instr_19670305_musicam-sacram_en.html) | Sagrada Congregação dos Ritos / Santa Sé (vatican.va) |  |
| 89 | 1 | [Effect of music on driving performance and physiological and psychological indicators: A systematic review and](https://pmc.ncbi.nlm.nih.gov/articles/PMC10790125/) | M. Ghojazadeh et al. (Health Promotion Perspectives) |  |
| 90 | 1 | [Sensorimotor coupling in music and the psychology of the groove (manuscrito do autor)](https://zenodo.org/records/997607) | Petr Janata, Stefan T. Tomic, Jason M. Haberman (J Exp Psych |  |
| 91 | 1 | [Syncopation, Body-Movement and Pleasure in Groove Music](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0094446) | Maria A. G. Witek, Eric F. Clarke, Mikkel Wallentin, Morten  |  |
| 83 | 2 | [How Does Background Music Affect Dining Duration, Tips and Bill Amounts in Restaurants? A Field Experiment](https://pmc.ncbi.nlm.nih.gov/articles/PMC11673941/) | M. Malcman, O. H. Azar, T. Shavit, M. Rosenboim (Behavioral  |  |
| 86 | 2 | [Music listening and stress recovery in healthy individuals: A systematic review with meta-analysis of experime](https://pmc.ncbi.nlm.nih.gov/articles/PMC9205498/) | K. Adiasto et al. / Radboud University (PLoS ONE) |  |

### Episódio 8+ · Tradições do mundo — 49 fontes

| # | P | Título | Autor / instituição | Nota |
|---|---|---|---|---|
| 22 | 1 | [Epic Tunes from the Collection by Kirsha Danilov and Traditions of Northern Bylina Melodies](https://musalm.ru/en/2016-3-3-2.html) | Bogdanova / Chernaya | texto em russo |
| 29 | 1 | [Composition and Improvisation in Cross-Cultural Perspective — Gamelan](https://www.open.edu/openlearn/history-the-arts/music/composition-and-improvisation-cross-cultural-perspective/content-section-0) | Open University / OpenLearn |  |
| 31 | 1 | [Music of the Shakuhachi](https://folkways-media.si.edu/docs/folkways/artwork/FW04218.pdf) | Yasuada Shinpu / Smithsonian Folkways |  |
| 33 | 1 | [Crossing Paths: Musical and Ritual Interactivity between the Ḥamadsha and Gnawa in Sidi Ali, Morocco](https://elischolar.library.yale.edu/yjmr/vol2/iss2/10) | Christopher J. Witulski |  |
| 92 | 1 | [Beyond the Classroom: World Music from the Musician's Point of View](https://ecampusontario.pressbooks.pub/beyondtheclassroom/open/download?type=pdf) | Howard Spring, Ryan Bruce / University of Guelph (eCampusOnt |  |
| 93 | 1 | [Arabic Maqam](https://www.maqamworld.com/en/maqam.php) | Johnny Farraj / MaqamWorld |  |
| 95 | 1 | [Znamenny Chant for the 21st Century](https://orthodoxartsjournal.org/znamenny-chant-for-the-21st-century/) | Vladimir Morosan / Orthodox Arts Journal |  |
| 96 | 1 | [Russia (World Centres of Polyphony)](https://polyphony.ge/en/russia/) | International Research Center for Traditional Polyphony – Tb |  |
| 97 | 1 | [Oberek (Obertas)](https://polishmusic.usc.edu/research/dances/oberek/) | Maja Trochimczyk / Polish Music Center, USC Thornton School  |  |
| 99 | 1 | [Fado, urban popular song of Portugal](https://ich.unesco.org/en/RL/fado-urban-popular-song-of-portugal-00563) | UNESCO – Intangible Cultural Heritage |  |
| 101 | 1 | [Flamenco](https://ich.unesco.org/en/RL/flamenco-00363) | UNESCO – Intangible Cultural Heritage |  |
| 102 | 1 | [La terminología musical del flamenco: el sistema modal y los modos en la música flamenca](https://ia803103.us.archive.org/25/items/revista_de_flamencologia-30/RDF_30-05-LA_TERMINOLOGIA_MUSICAL_DEL_FLAMENCO-LOLA_FERNANDEZ_MARIN.pdf) | Lola Fernández Marín / Revista de Flamencología n. 30 (Cáted |  |
| 104 | 1 | [Tango](https://ich.unesco.org/en/RL/tango-00258) | UNESCO – Intangible Cultural Heritage |  |
| 105 | 1 | [Review-essay of Link & Wendland, Tracing Tangueros (MTO 25.3)](https://mtosmt.org/issues/mto.19.25.3/mto.19.25.3.turciescobar.html) | John Turci-Escobar / Society for Music Theory |  |
| 106 | 1 | [Modes in Klezmer Music: A Corpus Study Based on Beregovski's Jewish Instrumental Folk Music (MTO 31.3)](https://www.mtosmt.org/issues/mto.25.31.3/mto.25.31.3.malin.html) | Yonatan Malin, Daniel Shanahan / Society for Music Theory |  |
| 107 | 1 | [Rebetiko](https://ich.unesco.org/en/RL/rebetiko-01291) | UNESCO – Intangible Cultural Heritage |  |
| 108 | 1 | [Modality vs. Chordal Harmony: Hybrid Aspects of Rebetiko During the Interwar Period](https://ejournals.lib.auth.gr/smb/article/view/7945) | Spiros Th. Delegos / Series Musicologica Balcanica 1.2 (Aris |  |
| 109 | 1 | [Qawwali Routes: Notes on a Sufi Music's Transformation in Diaspora](https://pdfs.semanticscholar.org/fdd7/73824c60bf1db8974d3160b82da6eb5cdc0c.pdf) | Sonia Gaind-Krishnan / NYU (Religions 11(12):685, MDPI) |  |
| 110 | 1 | [Rāgs Around the Clock: A Handbook for North Indian Classical Music, with Online Recordings in the Khayāl Style](https://books.openbookpublishers.com/10.11647/obp.0313.pdf) | David Clarke, com música de Vijay Rajput / Open Book Publish |  |
| 111 | 1 | [Gamelan](https://ich.unesco.org/en/RL/gamelan-01607) | UNESCO – Intangible Cultural Heritage |  |
| 112 | 1 | [Temporal and Density Flow in Javanese Gamelan](https://sumarsam.faculty.wesleyan.edu/files/2023/01/4_Temporal_and_Density_Flow.pdf) | Sumarsam / Wesleyan University (site docente) |  |
| 113 | 1 | [Shakuhachi: The History and Practice of Suizen](https://japanhouse.illinois.edu/education/insights/shakuhachi) | Ben Macke / Japan House, University of Illinois Urbana-Champ |  |
| 114 | 1 | [Kora: in search of the origins of West Africa's famed stringed musical instrument](https://theconversation.com/kora-in-search-of-the-origins-of-west-africas-famed-stringed-musical-instrument-216287) | Eric Charry / Wesleyan University (The Conversation) |  |
| 116 | 1 | [Michael Veal on Tony Allen (entrevista)](https://www.afropop.org/articles/michael-veal-on-tony-allen) | Banning Eyre com Michael Veal (Yale) / Afropop Worldwide |  |
| 117 | 1 | [Gnawa](https://ich.unesco.org/en/RL/gnawa-01170) | UNESCO – Intangible Cultural Heritage |  |
| 118 | 1 | [Byzantine chant](https://ich.unesco.org/en/RL/byzantine-chant-01508) | UNESCO – Intangible Cultural Heritage |  |
| 119 | 1 | [Georgian polyphonic singing](https://ich.unesco.org/en/RL/georgian-polyphonic-singing-00008) | UNESCO – Intangible Cultural Heritage |  |
| 120 | 1 | [Bistritsa Babi, archaic polyphony, dances and rituals from the Shoplouk region](https://ich.unesco.org/en/RL/bistritsa-babi-archaic-polyphony-dances-and-rituals-from-the-shoplouk-region-00095) | UNESCO – Intangible Cultural Heritage |  |
| 121 | 1 | [Andalusian Nuba](https://jewish-music.huji.ac.il/en/content/andalusian-nuba) | Essica Marks / Jewish Music Research Centre, Hebrew Universi |  |
| 122 | 1 | [Morna, musical practice of Cabo Verde](https://ich.unesco.org/en/RL/morna-musical-practice-of-cabo-verde-01469) | UNESCO – Intangible Cultural Heritage |  |
| 123 | 1 | [Ensaio sobre a Música Brasileira (texto da 3ª ed., com comentário de Cláudia Neiva de Matos)](https://www.ufrgs.br/cdrom/mandrade/mandrade.pdf) | Mário de Andrade / cópia hospedada pela UFRGS |  |
| 21 | 2 | [Turkey: The Turkish Ney](https://folkways-media.si.edu/docs/folkways/artwork/UNES08204.pdf) | Kudsi Erguner / Smithsonian Folkways |  |
| 24 | 2 | [Songs of a Russian Gypsy](https://folkways-media.si.edu/docs/folkways/artwork/MON00404.pdf) | Alya / Sasha Polinoff / Smithsonian Folkways | encarte de 6 págs.; única fonte sobre romance cigano russo |
| 26 | 2 | [Oberek (niestylizowany)](https://tance.edu.pl/tance/oberek-2/) | Tańce Edu PL |  |
| 27 | 2 | [Saetas](https://www.juntadeandalucia.es/aaiicc/flamenco/content/saetas) | Instituto Andaluz del Flamenco / Junta de Andalucía |  |
| 34 | 2 | [Lost Voices of Hagia Sophia: Medieval Byzantine Chant Sung in the Virtual Acoustics of Hagia Sophia](https://openaccess.city.ac.uk/id/eprint/23941/1/Lost%20Voices%20of%20Hagia%20Sophia%20booklet-CR420-CDBR.pdf) | Lingas / Pentcheva et al. |  |
| 35 | 2 | [Georgian Traditional Polyphony: Modern Trends and Perspectives of Development](https://polyphony.ge/wp-content/uploads/2025/01/Modern-Trends-and-Perspectives.pdf) | Tsurtsumia / Jordania / Tbilisi State Conservatoire |  |
| 36 | 2 | [O papel da morna na afirmação da identidade nacional em Cabo Verde](http://hdl.handle.net/10362/15256) | Gabriel Moacyr Rodrigues / Universidade NOVA de Lisboa |  |
| 94 | 2 | [Mevlevi Sema ceremony](https://ich.unesco.org/en/RL/mevlevi-sema-ceremony-00100) | UNESCO – Intangible Cultural Heritage |  |
| 98 | 2 | [Traditional Polish lullabies](https://www.folklore.ee/pubte/eraamat/eestipoola2/sikora.zebrowska.pdf) | Kazimierz Sikora, Barbara Żebrowska / Estonia and Poland 2 ( |  |
| 100 | 2 | [Artur Paredes](https://www.museudofado.pt/en/fado/persolanity/artur-paredes-en) | Museu do Fado (Lisboa), com base em P. Caldeira Cabral |  |
| 103 | 2 | [La saeta en la Semana Santa cartagenera](https://revistas.um.es/rmu/article/download/216691/170661/767551) | Juan Ruipérez Vera / Revista Murciana de Antropología n. 19  |  |
| 115 | 2 | [John Collins: Ghana, Then and Now (entrevista)](https://www.afropop.org/articles/john-collins-ghana-then-and-now-part-1) | Banning Eyre com John Collins (University of Ghana) / Afropo |  |
| 135 | 2 | [The Oud Across Arabic Culture (Bilād al-Shām, Iraq, and Egypt) Seifed-Din Shehadeh Abdoun, Do - The Chrysalis ](http://www.chrysalis-foundation.org/Abdoun_umd_0117E_12513.pdf) | Seifed-Din Shehadeh Abdoun (tese, U. Maryland) |  |
| 23 | 3 | [The Genre-Related and Stylistic Explication of the Song Tradition of the Belgorod Region](https://russianmusicology.com/index.php/RM/article/view/1172) | Zhirov et al. | texto em russo |
| 25 | 3 | [Asymilacja ludowych pierwowzorów w polskiej pieśni artystycznej — zarys problematyki](https://czasopisma.ujd.edu.pl/index.php/EM/article/view/519) | Katarzyna Suska-Zagórska |  |
| 28 | 3 | [UNESCO Collection Week 16: Lesser-known Music from North India and Pakistan](https://folkways.si.edu/news-and-press/unesco-collection-week-16-lesser-known-music-from-north-india-and-pakistan) | Shalini Ayyagari / Smithsonian Folklife |  |
| 30 | 3 | [The Reception of Western Music in the Enka of the Meiji and Taisho Periods](https://www.jstage.jst.go.jp/article/toyoongakukenkyu1936/1989/53/1989_53_1/_article) | Atsuko Gondo | texto em japonês — única fonte verificada sobre enka |
| 32 | 3 | [The Japanese Koto](https://folkways-media.si.edu/docs/folkways/artwork/COOK01132.pdf) | Shinichi Yuize / Smithsonian Folkways | encarte curto (2 págs.) — única fonte sobre koto |
