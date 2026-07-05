#!/usr/bin/env python3
"""
Pos-processa os prompts gerados pelo 03_build_prompts.py generico (Fase 3) para honrar as
decisoes deste projeto:

1) IDIOMA: 03_build_prompts.py tem a diretiva de output HARDCODED em pt-BR (OUTPUT_REQ). Aqui
   ela e SUBSTITUIDA por uma diretiva es-ES — diferente do Paradise Lost (que ACRESCENTA um bloco
   de citacao/traducao porque original=ingles != output=pt-BR), aqui narracao e citacao ficam no
   MESMO idioma (o castelhano de Cervantes narrado/comentado em es-ES moderno), entao nao ha gloss
   nem traducao a fazer.
2) ANUNCIO: corrige "capitulo {cap}" (numero global 1-128, sem sentido para quem le a obra) para
   "Parte {I/II}, capitulo {cap_natural}" (ou "Parte {I/II}, Prologo"), lendo os campos extras
   'parte'/'cap_natural' de _capitulos_index.json via o 'source_chapter' de cada cena.

Idempotente: detecta marcador e nao duplica. Roda DEPOIS que existirem prompts (Fase 3); nao ha
nada para processar antes da autoria de cenas.

Uso:
    python3 postprocess_prompts.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
PROMPTS = PROJ / "prompts_cenas"
MANIFEST = PROJ / "_cenas_manifest.json"
CAP_INDEX = PROJ / "DQ-capitulos" / "_capitulos_index.json"

MARK = "## Idioma (Don Quijote)"

OUTPUT_REQ_PT = ("The ENTIRE audio MUST be spoken in fluent, natural **Brazilian Portuguese "
                 "(pt-BR)**. The English above is instruction only; never read it aloud or "
                 "switch languages.")

OUTPUT_REQ_ES = """The ENTIRE audio MUST be spoken in fluent, natural **modern European Spanish (es-ES)**.
The English above is instruction only; never read it aloud or switch languages.

## Idioma (Don Quijote)
The source text is already 17th-century Castilian Spanish — do NOT translate it. Narrate and
comment in clear **modern es-ES**, and when you quote the original text (the scene anchors, or
any striking line), read Cervantes' own words verbatim, then briefly gloss any archaic vocabulary
or syntax in plain modern Spanish so a contemporary listener follows completely. Pronounce archaic
forms naturally, without exaggeration."""

# 'Announce clearly: "Este é o áudio da **cena N**, **capítulo <cap global>**."' -> parte-aware.
ANNOUNCE_RE = re.compile(
    r'Announce clearly: "Este é o áudio da \*\*cena (\d+)\*\*, \*\*capítulo (\d+)\*\*\."'
)


def build_announce(seq: int, parte_label: str, cap_natural) -> str:
    if cap_natural == "Prólogo":
        lugar = f"{parte_label}, Prólogo"
    else:
        lugar = f"{parte_label}, capítulo {cap_natural}"
    return (f'Announce clearly: "Éste es el audio de la **escena {seq}**, **{lugar}** '
            f'de *Don Quijote de la Mancha*."')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not MANIFEST.is_file():
        print(f"AVISO: {MANIFEST} nao existe ainda (autoria de cenas nao comecou) — nada a fazer.")
        return 0
    if not PROMPTS.is_dir() or not any(PROMPTS.glob("prompt_*.md")):
        print(f"AVISO: {PROMPTS} nao tem prompts ainda (rode 03_build_prompts.py primeiro) — nada a fazer.")
        return 0

    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    idx = json.loads(CAP_INDEX.read_text(encoding="utf-8"))
    cap_by_arquivo = {c["arquivo"]: c for c in idx["capitulos"]}
    cenas_by_seq = {c["seq_global"]: c for c in man["cenas"]}

    parte_label = {"P1": "Parte I", "P2": "Parte II"}

    files = sorted(PROMPTS.glob("prompt_*.md"))
    patched_lang = patched_announce = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        orig = t
        if MARK not in t and OUTPUT_REQ_PT in t:
            t = t.replace(OUTPUT_REQ_PT, OUTPUT_REQ_ES, 1)
            patched_lang += 1

        m = ANNOUNCE_RE.search(t)
        if m:
            seq = int(m.group(1))
            cena = cenas_by_seq.get(seq)
            if cena:
                cap_info = cap_by_arquivo.get(cena["source_chapter"])
                if cap_info:
                    new_announce = build_announce(
                        seq, parte_label.get(cap_info["parte"], cap_info["parte"]),
                        cap_info["cap_natural"])
                    t = t[:m.start()] + new_announce + t[m.end():]
                    patched_announce += 1

        if t != orig:
            if not args.dry_run:
                f.write_text(t, encoding="utf-8")
            print(f"  {'[dry-run] ' if args.dry_run else ''}{f.name}")

    print(f"\nPrompts: {len(files)} | idioma es-ES: {patched_lang} | anuncio Parte/capitulo: {patched_announce}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
