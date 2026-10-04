# Pauta para o council_llm — lacunas do glossário técnico de escuta

- **Pedido do Edson:** 2026-10-03. Origem: sessão `notebooklm_edson`, tarefas `notebooklm_edson-bwni` (bolero mexicano)
  e `notebooklm_edson-mmf9` (base do glossário, concluída com 105 fontes).
- **Contexto:** `../04_consolidacao/CONSOLIDACAO.md` (mapa de confusões e divergências) e `ja_carregadas.tsv` (as 105
  fontes já no notebook — **não repetir**).
- **Onde entregar:** no repo `council_llm`, sem escrever neste repo, que tem outra sessão ativa e um cron que faz commits.
  Avise a sessão `notebooklm-edson-c1` com o caminho do arquivo. Ela consolida, pede a aprovação do Edson e sobe ao notebook.
- **Idioma:** instruções em inglês, relatório em pt-BR (regra do ecossistema).

---

## PROMPT (para cada modelo do council)

```text
# ROLE
You are a research librarian with expertise in ethnomusicology of Latin America and Iberia, Brazilian popular
music, and French popular music. You are filling GAPS in an existing source library for a cascading technical
glossary of musical genres (written in Brazilian Portuguese, three layers per entry: plain words · technical
term translated · theory). The user is a Brazilian surgical oncologist, scientifically literate, a layman in
music theory, who recognizes genres by sound but cannot yet name what he hears.

# WHAT IS ALREADY COVERED — do not return these
A list of 105 sources already loaded is in ja_carregadas.tsv (family, title, URL). Do not return any of them or
another copy of the same text. Known dead ends (do not return): "Bolero" by Margarita Sánchez-Gallinal (revista
Archipiélago, UNAM) is a POEM, not a study; the UFRGS handle 10183/102212 is a philosophy thesis, not about
"campeirismo musical".

# THE GAPS (find sources for these only)
G1. Mexican bolero — the trío romántico (Trío Los Panchos and successors), the requinto guitar and its
    introductions/fills, the accompaniment pattern, vocal harmony in thirds, Agustín Lara's song bolero; and
    HOW IT DIFFERS BY EAR from the Cuban bolero (cinquillo/tresillo, son-bolero, filin). Leads to verify:
    TESIUNAM (UNAM theses repository), UNICACH theses (Palomeque, Sarmiento — unverified), CENIDIM/INBA,
    El Colegio de México, Revista Musical Chilena, Latin American Music Review, Pablo Dueñas (history).
G2. Toada × moda de viola (Brazilian música caipira) — any rhythmic or formal criterion that separates the
    two by ear (viola pattern, meter, tempo, text structure). Leads: Brazilian theses on viola caipira
    (USP, UNICAMP, UNESP, UFU, UFG), Revista do IEB, Per Musi, Música Popular em Revista.
G3. Cateretê/catira × cururu — side-by-side description of the two viola "batidas" (ideally notated), and
    of the dance (palmas, sapateado) vs the cururu desafio.
G4. Valse musette (Paris bal musette) × Brazilian valsa / seresta — tempo, accompaniment pattern
    ("pompe"), accordion vs violão/regional, vocal style. Leads: Philharmonie de Paris / Cité de la musique
    educational pages, Volume! (OpenEdition), French theses (theses.fr, HAL), Brazilian theses on valsa
    and seresta.
G5. Chamamé in Argentina (Corrientes) × chamamé as played in Rio Grande do Sul and Mato Grosso do Sul — is
    there ANY source that says what audibly differs (tempo, accordion type, sapucay, rhythm emphasis)? If no
    source makes the distinction, say so explicitly. Also: chimarrita (RS/Azores origin) — any musical
    description.
G6. Samba de breque — a musical (not only historical) description: where the breaks fall, how the spoken
    insert relates to the meter; Moreira da Silva. Leads: Brazilian theses (UNIRIO, UFRJ, UNICAMP), Itaú
    Cultural encyclopedia (signed entries), Música Popular em Revista.
G7. Vanera × xote (gaúcho) — side-by-side rhythmic description, if any exists.

# SOURCE QUALITY RULES (strict)
1. Prefer authored and institutional sources: theses, peer-reviewed articles, university/conservatory
   material, national musicology institutes, heritage dossiers, national libraries, signed encyclopedia entries.
2. EXCLUDE: blogs, SEO pages, sellers, Scribd/dokumen.pub/pdfcoffee and any unauthorized copy, Wikipedia,
   AI-generated pages, exoticizing generalizations.
3. Every item must be VERIFIED: you opened the URL and it is what the title says (check the PDF's first page:
   wrong-handle errors happened before). Never invent title, author, year or URL. Unconfirmed → "Não verificado".
4. Mark whether the FULL TEXT is openly readable; paid books go to a separate list.
5. Quote, for each source, ONE short passage (≤ 40 words) that shows it actually covers the gap — e.g. the
   sentence that describes the rhythm or the difference. This is how the result will be checked.
6. If a gap has no good open source, say so — an honest "lacuna confirmada" is a valid result.

# OUTPUT (write in Brazilian Portuguese, pt-BR)
Part A — Resumo: per gap G1–G7, one line: coberta / parcialmente / lacuna confirmada.
Part B — Tabela: | id | lacuna | prioridade (1-3) | titulo | autor_instituicao | tipo | ano | idioma | url | formato | acesso | trecho_que_prova (≤40 palavras, na língua original) | por_que_importa |
Part C — Não verificado (what you tried) · Descartadas relevantes (why) · Livros pagos (≤ 6).
Part D — The table again as a single semicolon-separated CSV block with full URLs.
```

## Para o council (orientação de processo)

- Se o council tiver um modo de deliberação, o mais útil aqui é um modelo verificar o trabalho do outro, sobretudo
  conferindo `url` contra `trecho_que_prova`. Gerar mais candidatos ajuda menos. Fonte inventada ou com o link
  errado é o defeito mais caro: aconteceu duas vezes na rodada anterior.
- Um relatório único consolidado basta, com a indicação de qual modelo achou cada fonte.
