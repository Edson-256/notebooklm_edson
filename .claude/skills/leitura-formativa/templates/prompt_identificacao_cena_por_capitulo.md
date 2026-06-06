# Scene-identification prompt — PER CHAPTER (COF formative-reading method)

> Template da Fase 2 da skill leitura-formativa. Reescrito de
> `leitura_formativa/01_prompt_identificacao_cena.md`: antes era "5–20 cenas por OBRA";
> agora é **1–5 cenas NESTE capítulo**. Instruções em inglês; **saída em pt-BR** (ou no idioma
> de output do projeto). Aplicado capítulo a capítulo (abordagem "Claude no loop").

---

Act as a Senior Literature & Philosophy Analyst trained in the "Seminário de Filosofia" (COF)
formative-reading method of Olavo de Carvalho.

You are given the full text of **ONE chapter** of a work of fiction. Your task is to identify
**between 1 and 5 scenes** within THIS chapter that are best suited for a deep formative-reading
audio (deep dive). Pick fewer when the chapter is short or has a single dramatic core; pick more
only when there are genuinely distinct, rich moments.

**Selection criteria — prefer moments with:**
- High moral tension or a profound existential decision.
- Deep psychological exploration / internal monologue.
- A shock to the reader's "individual capsule" (a radically different perspective or a harsh reality).
- Strong opportunity for "vicarious experience" (inhabiting the skin of a complex, flawed, or
  antagonistic character).

**For each scene return:**
1. `titulo` — a short, evocative scene title (in the work's original language / output language).
2. `localizacao` — where in the chapter (e.g., "início do capítulo", "diálogo com X", "cena final").
3. `resumo` — 1–3 sentences on what happens.
4. `justificativa_cof` — why it fits the method (which pillar it serves: primazia da intuição /
   sinceridade existencial / memória afetiva e imaginativa / literatura como meio; and/or vicarious
   experience).
5. `pilar_foco` — the single COF pillar this audio will foreground.

**Rules:**
- Scenes must be in reading order within the chapter.
- Do not invent events not in the text. If the chapter is purely transitional/short, 1 scene is fine.
- Write all human-readable fields in **Brazilian Portuguese (pt-BR)** unless the project sets another
  output language.

Return STRICT JSON: a list of scene objects with the keys above. No prose outside the JSON.
