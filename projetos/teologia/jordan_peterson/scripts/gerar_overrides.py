#!/usr/bin/env python3
"""
Gera data/overrides.tsv (id -> categoria) da classificação MANUAL (LLM) dos 296
vídeos que o keyword-classifier deixou em "Outros". CODES: 1 código por linha de
data/outros.tsv, mesma ordem. CODE2CAT mapeia para nomes canônicos (os que
coincidem com CATEGORIAS do classificar.py são fundidos; INST é categoria nova).
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUTROS = BASE / "data" / "outros.tsv"
OUT = BASE / "data" / "overrides.tsv"

CODE2CAT = {
    "POD":  "Podcast — Entrevistas & Convidados (The JBP Podcast)",
    "REL":  "Série Bíblica, Deus & Religião",
    "MAP":  "Maps of Meaning, Mito & Arquétipos",
    "PSI":  "Personalidade & Psicologia",
    "CULT": "Cultura, Política & Ideologia",
    "AUTO": "Autodesenvolvimento, Sentido & Vida",
    "PAL":  "Palestras, Conferências & Discursos",
    "QA":   "Q&A / AMA & Mensagens diretas",
    "INST": "Anúncios, Tour & Institucional",
}

CODES = [
    "AUTO","INST","INST","POD","CULT","PSI","MAP","CULT","CULT","PSI",     # 1-10
    "CULT","CULT","CULT","PSI","CULT","CULT","CULT","CULT","CULT","POD",   # 11-20
    "CULT","POD","CULT","AUTO","CULT","POD","INST","POD","CULT","REL",     # 21-30
    "CULT","REL","CULT","REL","REL","CULT","CULT","CULT","CULT","AUTO",    # 31-40
    "CULT","CULT","CULT","PSI","POD","CULT","POD","REL","CULT","CULT",     # 41-50
    "PSI","CULT","CULT","CULT","REL","REL","INST","CULT","PSI","POD",      # 51-60
    "PSI","POD","CULT","CULT","POD","PSI","REL","CULT","MAP","CULT",       # 61-70
    "CULT","CULT","PSI","CULT","CULT","CULT","CULT","CULT","CULT","CULT",  # 71-80
    "CULT","CULT","CULT","CULT","REL","REL","REL","CULT","CULT","CULT",    # 81-90
    "CULT","CULT","CULT","REL","CULT","CULT","CULT","POD","CULT","CULT",   # 91-100
    "CULT","POD","POD","CULT","PSI","CULT","CULT","CULT","AUTO","CULT",    # 101-110
    "CULT","CULT","CULT","POD","PSI","REL","REL","AUTO","AUTO","AUTO",     # 111-120
    "REL","AUTO","POD","INST","CULT","PSI","CULT","CULT","POD","CULT",     # 121-130
    "CULT","CULT","AUTO","CULT","CULT","MAP","CULT","CULT","CULT","CULT",  # 131-140
    "CULT","CULT","POD","POD","INST","CULT","MAP","CULT","CULT","CULT",    # 141-150
    "INST","CULT","CULT","CULT","CULT","CULT","CULT","CULT","REL","CULT",  # 151-160
    "INST","CULT","CULT","MAP","INST","CULT","AUTO","CULT","AUTO","CULT",  # 161-170
    "CULT","CULT","POD","POD","CULT","CULT","CULT","CULT","CULT","CULT",   # 171-180
    "CULT","AUTO","CULT","INST","PSI","AUTO","POD","CULT","POD","PSI",     # 181-190
    "PSI","AUTO","POD","AUTO","AUTO","INST","INST","AUTO","POD","POD",     # 191-200
    "INST","INST","POD","PAL","PAL","POD","PAL","REL","POD","POD",         # 201-210
    "PAL","INST","MAP","POD","POD","INST","PAL","CULT","CULT","INST",      # 211-220
    "CULT","CULT","INST","AUTO","POD","INST","REL","CULT","CULT","CULT",   # 221-230
    "AUTO","CULT","CULT","PAL","PAL","PAL","PAL","POD","CULT","POD",       # 231-240
    "POD","REL","CULT","POD","POD","MAP","CULT","POD","POD","POD",         # 241-250
    "POD","PSI","INST","INST","POD","REL","INST","CULT","POD","POD",       # 251-260
    "CULT","REL","CULT","INST","POD","CULT","CULT","CULT","CULT","INST",   # 261-270
    "PAL","POD","PSI","CULT","POD","POD","CULT","REL","INST","INST",       # 271-280
    "CULT","CULT","PAL","PAL","PAL","AUTO","PAL","MAP","INST","PSI",       # 281-290
    "AUTO","POD","POD","POD","PSI","AUTO",                                  # 291-296
]

def main():
    rows = []
    for line in OUTROS.open(encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            rows.append((p[0], p[1]))
    assert len(rows) == len(CODES), f"outros={len(rows)} != codes={len(CODES)}"
    with OUT.open("w", encoding="utf-8") as f:
        for (vid, _t), code in zip(rows, CODES):
            f.write(f"{vid}\t{CODE2CAT[code]}\n")
    print(f"Overrides escritos: {len(rows)} -> {OUT}")

if __name__ == "__main__":
    main()
