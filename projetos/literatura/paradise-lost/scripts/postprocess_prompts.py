#!/usr/bin/env python3
"""
Pós-processa os prompts gerados (Fase 3) para honrar as decisões deste projeto:

1) IDIOMA: narração em pt-BR CITANDO o verso em inglês. Injeta uma seção
   "## Verse & language (Paradise Lost)" logo após o "## Output requirement".
2) GÊNERO: corrige "novella" -> "epic poem" no fechamento do último episódio.
3) FIO CONDUTOR: no episódio 1, acrescenta o through-line COF (eu fechado -> paraíso interior)
   e o aviso de que esta é uma EPOPEIA EM VERSO mantida em inglês.

Idempotente: detecta marcador e não duplica.
"""
from __future__ import annotations
from pathlib import Path

PROMPTS = Path(__file__).resolve().parent.parent / "prompts_cenas"
MARK = "## Verse & language (Paradise Lost)"

OUTPUT_REQ_ANCHOR = ("The ENTIRE audio MUST be spoken in fluent, natural **Brazilian Portuguese "
                     "(pt-BR)**. The English above is instruction only; never read it aloud or "
                     "switch languages.")

LANG_BLOCK = """

## Verse & language (Paradise Lost)
This is an epic POEM in English blank verse. Narrate in **pt-BR**, but QUOTE the key English lines
**verbatim** — above all the two scene anchors, and any famous line of the passage — then immediately
gloss/translate each quote into pt-BR so a listener with no English follows completely. Keep each
quote short (1–3 lines); the bulk of the audio is your warm pt-BR commentary. Pronounce the English
lines clearly and slowly. Never read this English instruction aloud."""

EP1_ANCHOR = ("- **A practical note:** the series is sequential and the method will NOT be re-explained "
              "in later episodes; invite the listener to start from the beginning.")

EP1_EXTRA = """

## This work, and the spine of the whole series (say briefly in episode 1)
- *Paradise Lost* is an **epic poem in verse** (1667), not a novel; we keep the text in **English**
  and narrate in **pt-BR, quoting the verse**. Reassure the listener: no English is required.
- The method was forged for novels, but its heart — **vicarious experience** — meets its hardest,
  richest test here: we will wear the skin of **Satan**, the most magnificent antagonist in
  literature, precisely to feel from inside why his grandeur is a prison.
- Name the **through-line** that will return in every episode: the contrast between the **closed
  self** ("The mind is its own place"; "myself am Hell") and the **"paradise within"** Michael
  promises at the end. Breaking that "individual capsule" is exactly what formative reading is for."""


def main() -> int:
    files = sorted(PROMPTS.glob("prompt_*.md"))
    patched_lang = patched_ep1 = patched_genre = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        orig = t
        if MARK not in t and OUTPUT_REQ_ANCHOR in t:
            t = t.replace(OUTPUT_REQ_ANCHOR, OUTPUT_REQ_ANCHOR + LANG_BLOCK, 1)
            patched_lang += 1
        if f.name.startswith("prompt_01_") and "spine of the whole series" not in t and EP1_ANCHOR in t:
            t = t.replace(EP1_ANCHOR, EP1_ANCHOR + EP1_EXTRA, 1)
            patched_ep1 += 1
        if "reread the novella" in t:
            t = t.replace("reread the novella", "reread the whole epic poem")
            patched_genre += 1
        if t != orig:
            f.write_text(t, encoding="utf-8")
    print(f"Prompts: {len(files)} | idioma+verso: {patched_lang} | episódio 1: {patched_ep1} | "
          f"gênero(novella→epic): {patched_genre}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
