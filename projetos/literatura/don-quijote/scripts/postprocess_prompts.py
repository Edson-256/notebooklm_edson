#!/usr/bin/env python3
"""
Pos-processa os prompts gerados pelo 03_build_prompts.py (Fase 3) para honrar as decisoes
especificas deste projeto que a skill generica nao cobre:

1) NUANCE DE IDIOMA: a skill JA gera a diretiva de output em es-ES (le 'language_name' do
   _cenas_manifest.json). Aqui so ACRESCENTAMOS a nuance de que o texto-base ja e castelhano do
   sec. XVII e NAO deve ser traduzido — narrar/comentar em es-ES moderno, citando Cervantes
   verbatim e glosando so o vocabulario/sintaxe arcaicos. (Diferente de Paradise Lost, que
   traduzia ingles->pt-BR; aqui narracao e citacao ficam no MESMO idioma.)
2) ANUNCIO: corrige "capitulo {cap}" (numero global 1-128, sem sentido p/ quem le a obra) para
   "Parte {I/II}, capitulo {cap_natural}" (ou "Parte {I/II}, Prologo"), lendo 'parte'/'cap_natural'
   de _capitulos_index.json via o 'source_chapter' de cada cena.

Idempotente: detecta marcador e nao duplica. Roda DEPOIS de 03_build_prompts.py.

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

# Diretiva es-ES que a skill generica ja escreve (03_build_prompts.py -> output_req()).
OUTPUT_REQ_ES = ("The ENTIRE audio MUST be spoken in fluent, natural **modern European Spanish "
                 "(es-ES)**. The English above is instruction only; never read it aloud or "
                 "switch languages.")

CASTILIAN_BLOCK = """

## Idioma (Don Quijote)
The source text is already 17th-century Castilian Spanish — do NOT translate it. Narrate and
comment in clear **modern es-ES**, and when you quote the original text (the scene anchors, or any
striking line), read Cervantes' own words verbatim, then briefly gloss any archaic vocabulary or
syntax in plain modern Spanish so a contemporary listener follows completely. Pronounce archaic
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
    patched_lang = patched_announce = missing_es = 0
    for f in files:
        t = f.read_text(encoding="utf-8")
        orig = t
        if MARK not in t:
            if OUTPUT_REQ_ES in t:
                t = t.replace(OUTPUT_REQ_ES, OUTPUT_REQ_ES + CASTILIAN_BLOCK, 1)
                patched_lang += 1
            else:
                missing_es += 1  # 03 nao gerou es-ES? (language_name faltando no manifesto)

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

    print(f"\nPrompts: {len(files)} | nuance castelhano: {patched_lang} | anuncio Parte/capitulo: {patched_announce}")
    if missing_es:
        print(f"  AVISO: {missing_es} prompt(s) SEM a diretiva es-ES esperada — confira se o manifesto "
              f"tem 'language_name' e re-rode 03_build_prompts.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
