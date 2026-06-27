#!/usr/bin/env python3
"""
Gera data/overrides.tsv (id \\t categoria) a partir da classificação MANUAL (LLM)
dos 526 vídeos que o classificador por palavra-chave deixou em "Outros".

A lista CODES abaixo tem 1 código por linha de data/outros.tsv, NA MESMA ORDEM.
Cada código é mapeado para o nome canônico da categoria (CODE2CAT). Categorias
cujo nome coincide com as do classificador por keyword são FUNDIDAS no mesmo
balde; as 5 novas (HOM, CRI, DIS, VIA, INST) viram seções próprias.
"""
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUTROS = BASE / "data" / "outros.tsv"
OUT = BASE / "data" / "overrides.tsv"

CODE2CAT = {
    "HOM":  "Homilias, Reflexões & Vida Cristã",
    "CRI":  "Cristologia, Trindade & Doutrina",
    "DIS":  "Discursos & Palestras (universidades, academias, keynotes)",
    "VIA":  "Viagens, Peregrinações & Lugares",
    "INST": "Institucional, Anúncios & Bastidores (Word on Fire)",
    "CIN":  "Cinema, TV & Cultura (comentários)",
    "LIT":  "Literatura, Poesia & Grandes Livros",
    "FIL":  "Filosofia, Fé & Razão",
    "ATE":  "Ateísmo, Secularismo & Apologética",
    "BIB":  "Bíblia & Escritura",
    "SAN":  "Santos, Doutores & Figuras da Igreja",
    "ESP":  "Vida Espiritual, Oração, Sacramentos & Liturgia",
    "MOR":  "Moral, Ética, Política & Cultura Contemporânea",
    "IGR":  "Igreja, Vaticano & Atualidade Eclesial",
    "PRE":  "«Bishop Barron Presents» — Diálogos & Entrevistas",
    "QA":   "Word on Fire Show / Podcast & Q&A",
}

CODES = [
    "MOR","IGR","CIN","HOM","INST","INST","CIN","HOM","HOM","IGR",       # 1-10
    "INST","INST","HOM","HOM","DIS","INST","INST","VIA","IGR","IGR",     # 11-20
    "MOR","FIL","MOR","CIN","CIN","DIS","FIL","HOM","MOR","IGR",         # 21-30
    "ESP","MOR","IGR","IGR","MOR","INST","HOM","PRE","MOR","DIS",        # 31-40
    "ESP","PRE","HOM","INST","HOM","MOR","VIA","MOR","PRE","MOR",        # 41-50
    "PRE","FIL","PRE","SAN","IGR","ESP","PRE","PRE","ATE","PRE",         # 51-60
    "IGR","ATE","PRE","MOR","PRE","MOR","IGR","CRI","HOM","ESP",         # 61-70
    "PRE","PRE","PRE","PRE","PRE","ESP","DIS","PRE","FIL","PRE",         # 71-80
    "INST","MOR","PRE","PRE","PRE","IGR","PRE","PRE","SAN","HOM",        # 81-90
    "INST","INST","HOM","HOM","ATE","ESP","PRE","INST","MOR","INST",     # 91-100
    "MOR","FIL","VIA","VIA","ESP","VIA","VIA","VIA","VIA","VIA",         # 101-110
    "INST","MOR","CRI","CIN","HOM","CIN","INST","FIL","MOR","VIA",       # 111-120
    "MOR","HOM","HOM","PRE","MOR","PRE","ATE","MOR","INST","IGR",        # 121-130
    "SAN","FIL","INST","IGR","FIL","ESP","MOR","MOR","FIL","PRE",        # 131-140
    "PRE","INST","MOR","MOR","MOR","DIS","FIL","HOM","DIS","FIL",        # 141-150
    "CIN","HOM","INST","HOM","CIN","MOR","FIL","DIS","IGR","MOR",        # 151-160
    "INST","INST","MOR","INST","HOM","SAN","MOR","HOM","MOR","HOM",      # 161-170
    "MOR","CIN","INST","MOR","CIN","MOR","ESP","IGR","ESP","BIB",        # 171-180
    "BIB","ESP","ESP","ESP","ESP","ESP","DIS","DIS","MOR","HOM",         # 181-190
    "MOR","INST","HOM","INST","LIT","IGR","CRI","IGR","ATE","IGR",       # 191-200
    "IGR","DIS","FIL","INST","DIS","MOR","ATE","MOR","HOM","BIB",        # 201-210
    "ESP","DIS","MOR","ESP","HOM","ESP","ESP","FIL","INST","CRI",        # 211-220
    "IGR","MOR","MOR","BIB","ESP","INST","FIL","INST","HOM","MOR",       # 221-230
    "INST","CRI","PRE","HOM","FIL","FIL","CIN","SAN","IGR","INST",       # 231-240
    "ESP","ESP","DIS","VIA","INST","FIL","CIN","FIL","MOR","CIN",        # 241-250
    "ATE","IGR","INST","IGR","CIN","FIL","FIL","MOR","ESP","INST",       # 251-260
    "HOM","MOR","FIL","ESP","MOR","CIN","CRI","CRI","ATE","SAN",         # 261-270
    "INST","ATE","INST","INST","INST","IGR","VIA","VIA","VIA","SAN",     # 271-280
    "INST","CIN","FIL","IGR","ESP","DIS","CRI","CIN","ESP","DIS",        # 281-290
    "DIS","ATE","CIN","IGR","IGR","INST","BIB","HOM","HOM","MOR",        # 291-300
    "CRI","MOR","INST","INST","IGR","IGR","CIN","CIN","CRI","MOR",       # 301-310
    "MOR","ESP","CIN","ESP","CIN","INST","CRI","VIA","VIA","CRI",        # 311-320
    "CRI","BIB","MOR","CIN","MOR","FIL","CIN","CRI","SAN","CIN",         # 321-330
    "CIN","MOR","LIT","VIA","VIA","VIA","FIL","IGR","CIN","HOM",         # 331-340
    "HOM","BIB","INST","MOR","SAN","MOR","INST","INST","MOR","HOM",      # 341-350
    "INST","INST","INST","CIN","CRI","INST","CIN","INST","MOR","BIB",    # 351-360
    "MOR","CIN","BIB","BIB","CRI","INST","BIB","INST","CIN","CIN",       # 361-370
    "INST","MOR","INST","IGR","FIL","FIL","INST","INST","CIN","QA",      # 371-380
    "CIN","QA","INST","CRI","QA","HOM","BIB","QA","QA","MOR",            # 381-390
    "CRI","CRI","CRI","BIB","IGR","BIB","FIL","MOR","CIN","LIT",         # 391-400
    "IGR","CIN","CIN","MOR","MOR","SAN","IGR","ESP","MOR","MOR",         # 401-410
    "CIN","ESP","CIN","MOR","CIN","IGR","CRI","CIN","MOR","ESP",         # 411-420
    "BIB","MOR","MOR","ATE","BIB","BIB","ESP","FIL","LIT","MOR",         # 421-430
    "MOR","CIN","VIA","MOR","MOR","MOR","CRI","CIN","IGR","CIN",         # 431-440
    "MOR","CRI","MOR","BIB","CIN","MOR","BIB","CIN","MOR","CIN",         # 441-450
    "MOR","MOR","MOR","MOR","IGR","FIL","IGR","CIN","CRI","CRI",         # 451-460
    "BIB","BIB","MOR","CRI","FIL","MOR","HOM","MOR","FIL","MOR",         # 461-470
    "HOM","MOR","CIN","INST","CRI","IGR","MOR","CIN","MOR","VIA",        # 471-480
    "VIA","VIA","QA","CRI","CRI","CIN","FIL","CIN","CRI","CRI",          # 481-490
    "VIA","VIA","VIA","VIA","VIA","VIA","VIA","MOR","VIA","VIA",         # 491-500
    "CRI","FIL","VIA","MOR","FIL","VIA","VIA","FIL","MOR","MOR",         # 501-510
    "HOM","MOR","BIB","ATE","CIN","ATE","MOR","ATE","CIN","CIN",         # 511-520
    "LIT","CIN","FIL","CIN","LIT","BIB",                                  # 521-526
]

def main():
    rows = []
    for line in OUTROS.open(encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            rows.append((p[0], p[1]))
    assert len(rows) == len(CODES), f"outros={len(rows)} != codes={len(CODES)}"
    with OUT.open("w", encoding="utf-8") as f:
        for (vid, _title), code in zip(rows, CODES):
            f.write(f"{vid}\t{CODE2CAT[code]}\n")
    print(f"Overrides escritos: {len(rows)} -> {OUT}")

if __name__ == "__main__":
    main()
