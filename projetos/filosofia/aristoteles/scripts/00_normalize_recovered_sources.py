#!/usr/bin/env python3
"""
Normaliza os quatro textos-fonte recuperados em 2026-08-21 para o formato
canônico do Internet Classics Archive (MIT), que é o que o resto do pipeline
(02_clean_raw.py → 03_segment_capitulos.py) já sabe ler:

    <cabeçalho de proveniência>
    ----------------------------------------------------------------------

    BOOK ONE

    Part I

    <parágrafos>

Por que normalizar em vez de ensinar novos marcadores ao segmentador: as outras
28 obras do corpus já estão nesse formato. Convertendo a fonte, as quatro obras
recuperadas passam pela MESMA segmentação e geram prompts com o MESMO
`capitulo_marker` ("Part IX") das obras que já foram ao ar. Nenhum ouvinte
percebe diferença de padrão entre um áudio e outro.

Entrada:  _fontes_recuperadas_temp/  (conferido — ver README_CONFERENCIA.md)
Saída:    obras/{cat}/{obra}/_raw/{arquivo}.txt   (sobrescreve, com backup .bak-<data>)

Uso:
  python3 scripts/00_normalize_recovered_sources.py --dry-run
  python3 scripts/00_normalize_recovered_sources.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMP = PROJECT_ROOT / "_fontes_recuperadas_temp"

SEP = "-" * 70

ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII",
         9: "IX", 10: "X", 11: "XI", 12: "XII", 13: "XIII", 14: "XIV", 15: "XV",
         16: "XVI", 17: "XVII", 18: "XVIII", 19: "XIX", 20: "XX", 21: "XXI",
         22: "XXII", 23: "XXIII", 24: "XXIV", 25: "XXV", 26: "XXVI", 27: "XXVII",
         28: "XXVIII", 29: "XXIX", 30: "XXX", 31: "XXXI", 32: "XXXII",
         33: "XXXIII", 34: "XXXIV"}


def header(titulo_en: str, translator: str, url: str, proveniencia: str) -> str:
    return (f"Provided by {proveniencia}.\n"
            f"Recovered 2026-08-21 — see docs/FONTES_INCOMPLETAS_recuperar.md.\n"
            f"    {url}\n\n"
            f"{titulo_en}\nBy Aristotle\n\nTranslated by {translator}\n\n"
            f"{SEP}\n\n")


# --------------------------------------------------------------------------
# Política — captura Wayback 1997 do MIT. Livros em palavras (BOOK ONE),
# capítulos como algarismo romano centrado numa linha só.
# --------------------------------------------------------------------------
def normalize_politica(t: str) -> str:
    out: list[str] = []
    started = False
    for ln in t.splitlines():
        s = ln.strip()
        mb = re.fullmatch(r"BOOK (ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT)", s)
        if mb:
            started = True
            out += ["", s, ""]
            continue
        if not started:
            continue                      # descarta "350 BC / POLITICS / by Aristotle"
        mc = re.fullmatch(r"[IVXL]+", s)
        if mc and re.match(r"^\s{4,}", ln):
            out += ["", f"Part {s}", ""]
            continue
        if re.fullmatch(r"-?THE END-?\.?", s) or s == ".":
            break
        out.append(ln.rstrip())
    return "\n".join(out)


# --------------------------------------------------------------------------
# Wikisource — livros já como "BOOK I"; capítulos como "N <texto>" (Eudemo,
# Magna Moralia) ou "N" sozinho na linha (Geração dos Animais).
# --------------------------------------------------------------------------
def normalize_wikisource(t: str, *, inline_chapters: bool,
                         first_chapter_implicit: bool = False) -> str:
    body = t.split("\n\n", 1)[1]          # descarta o cabeçalho de proveniência local
    out: list[str] = []
    prev_blank = True
    pending_book = False
    for ln in body.splitlines():
        s = ln.strip()
        if re.fullmatch(r"BOOK [IVX]+", s):
            out += ["", s, ""]
            prev_blank = True
            pending_book = first_chapter_implicit
            continue
        if prev_blank and s:
            if inline_chapters:
                m = re.match(r"^(\d{1,2}) (\S.*)$", s)
                if m and 1 <= int(m.group(1)) <= 40:
                    out += ["", f"Part {m.group(1)}", "", m.group(2)]
                    prev_blank = False
                    pending_book = False
                    continue
            else:
                if re.fullmatch(r"\d{1,2}", s):
                    out += ["", f"Part {s}", ""]
                    prev_blank = True
                    pending_book = False
                    continue
            if pending_book:              # capítulo 1 sem marcador no impresso
                out += ["", "Part 1", ""]
                pending_book = False
        out.append(s)
        prev_blank = not s
    return "\n".join(out)


JOBS = [
    dict(nome="Política", src=TEMP / "01_politica_jowett.txt",
         dest="obras/06_politica/01_politica/_raw/politics.txt",
         titulo_en="Politics", translator="Benjamin Jowett",
         url="https://web.archive.org/web/19970416151218if_/http://classics.mit.edu/Aristotle/politics.mb.txt",
         proveniencia="The Internet Classics Archive (captura Wayback de 1997-04-16)",
         fn=normalize_politica, livros=8),
    dict(nome="Ética a Eudemo", src=TEMP / "sem_bekker/02_etica_eudemo_solomon.txt",
         dest="obras/05_etica/02_etica_eudemo/_raw/eudemian_ethics.txt",
         titulo_en="Eudemian Ethics", translator="J. Solomon",
         url="https://en.wikisource.org/wiki/Eudemian_Ethics",
         proveniencia="Wikisource — The Works of Aristotle vol. IX (ed. Ross), Clarendon 1925",
         fn=lambda t: normalize_wikisource(t, inline_chapters=True), livros=4),
    dict(nome="Magna Moralia", src=TEMP / "sem_bekker/03_magna_moralia_stock.txt",
         dest="obras/05_etica/03_magna_moralia/_raw/magna_moralia.txt",
         titulo_en="Magna Moralia", translator="St. George Stock",
         url="https://en.wikisource.org/wiki/Index:Works_of_Aristotle_v9_(ed._Ross).djvu",
         proveniencia="Wikisource — The Works of Aristotle vol. IX (ed. Ross), Clarendon 1925",
         fn=lambda t: normalize_wikisource(t, inline_chapters=True,
                                           first_chapter_implicit=True), livros=2),
    dict(nome="Geração dos Animais", src=TEMP / "sem_bekker/04_geracao_animais_platt.txt",
         dest="obras/03_psicologia_biologia/07_geracao_animais/_raw/on_the_generation_of_animals.txt",
         titulo_en="On the Generation of Animals", translator="Arthur Platt",
         url="https://en.wikisource.org/wiki/On_the_Generation_of_Animals",
         proveniencia="Wikisource — The Works of Aristotle vol. V (ed. Smith & Ross), Clarendon 1912",
         fn=lambda t: normalize_wikisource(t, inline_chapters=False), livros=5),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    stamp = time.strftime("%Y%m%d")
    rc = 0
    for j in JOBS:
        raw = j["src"].read_text(encoding="utf-8")
        body = j["fn"](raw)
        body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"
        full = header(j["titulo_en"], j["translator"], j["url"], j["proveniencia"]) + body

        books = re.findall(r"(?m)^BOOK [A-Z]+$", body)
        caps: dict[str, int] = {}
        cur = None
        for ln in body.splitlines():
            if re.fullmatch(r"BOOK [A-Z]+", ln):
                cur = ln
                caps[cur] = 0
            elif re.fullmatch(r"Part [IVXL\d]+", ln) and cur:
                caps[cur] += 1
        print(f"=== {j['nome']}: {len(books)} livros (esperado {j['livros']}), "
              f"{sum(caps.values())} capítulos, {len(full)} bytes")
        for b, n in caps.items():
            print(f"      {b:<12} {n:>3} capítulos")
        if len(books) != j["livros"]:
            print("      ✗ CONTAGEM DE LIVROS DIVERGE — não gravado")
            rc = 1
            continue
        if args.dry_run:
            continue
        dest = PROJECT_ROOT / j["dest"]
        if dest.exists():
            shutil.copy2(dest, dest.with_suffix(f".txt.bak-{stamp}"))
        dest.write_text(full, encoding="utf-8")
        print(f"      → gravado em {j['dest']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
