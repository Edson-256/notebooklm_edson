#!/usr/bin/env python3
r"""Regenera SÓ `capitulos/` de Notre-Dame de Paris a partir de Notre-Dame_de_Paris.md.

Motivo (2026-08-18): `process_notre_dame.py` usa o regex
    r'^###\s+[IVXLC]+\s+[-–]\s+(.*)'
para achar fronteira de capítulo. Mas 16 dos 59 cabeçalhos estão malformados no
arquivo-fonte — vêm como `– TÍTULO EM CAIXA ALTA`, sem `###` e sem numeral romano.
Esses 16 não viravam fronteira e seu texto era CONCATENADO ao capítulo anterior
(L02-C02 continha II–VII; L04-C01 continha o Livro IV inteiro; L09-C01 idem para o IX).
Além disso, o cabeçalho malformado do Livre VIII cap. I vinha imediatamente após
`# LIVRE HUITIÈME`, quando chap_num ainda era 0, e a guarda `if book_num > 0 and
chap_num > 0` DESCARTAVA aquele texto — o capítulo se perdia por completo, e todo o
Livro VIII ficava deslocado em -1 (L08-C01 era, de fato, o capítulo II).

Este script aceita as duas formas de cabeçalho e regenera os 59 capítulos.

⚠️ ESCOPO DELIBERADAMENTE LIMITADO: NÃO mexe em `cenas/`, `prompts/`, `audios/` nem
`audios/metadata.json`. Os 175 áudios de deep dive já foram gerados com os nomes de
cena ANTIGOS; re-fatiar cenas invalidaria essa rastreabilidade. Ver
`capitulos/_RENUMERACAO_L08.md` para o mapa de/para.

Uso:
    python3 scripts/resplit_capitulos.py --dry-run     # só relatório
    python3 scripts/resplit_capitulos.py --out capitulos_fix
    python3 scripts/resplit_capitulos.py --out capitulos   # sobrescreve (git guarda o antes)
"""
import argparse
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'Notre-Dame_de_Paris.md')

BOOK_RE = re.compile(r'^# LIVRE\s+(.*)')
# Cabeçalho bem-formado: "### I – LA GRAND'SALLE"
CHAP_OK_RE = re.compile(r'^###\s+([IVXLC]+)\s+[-–]\s+(.*)')
# Cabeçalho malformado: "– CLAUDE FROLLO" (sem ###, sem romano, TÍTULO EM CAIXA ALTA)
CHAP_BAD_RE = re.compile(r'^[-–]\s+(.+?)\s*$')


def is_upper_title(text):
    """True se o texto não tem NENHUMA minúscula alfabética.

    É o que separa um cabeçalho de capítulo malformado ("– SOURD") de uma linha de
    diálogo francês, que também começa com travessão mas traz prosa em caixa mista
    ("– Vous avez raison, dit-il."). Acentos são normalizados antes do teste.
    """
    stripped = unicodedata.normalize('NFD', text)
    letters = [c for c in stripped if c.isalpha() and unicodedata.category(c) != 'Mn']
    if not letters:
        return False
    return not any(c.islower() for c in letters)


def clean_title(title):
    title = re.sub(r'\{.*?\}', '', title)
    title = re.sub(r'[^A-Za-z0-9\s-]', '', title)
    return title.strip().replace(' ', '_')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='capitulos_fix')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    with open(SRC, encoding='utf-8') as f:
        lines = f.readlines()

    chapters = []          # (book, chap, title, roman_or_None, malformed, lines)
    book = 0
    chap = 0
    title = ''
    roman = None
    malformed = False
    buf = []

    def flush():
        if book > 0 and chap > 0 and buf:
            chapters.append((book, chap, title, roman, malformed, list(buf)))

    for line in lines:
        bm = BOOK_RE.match(line)
        if bm:
            flush()
            book += 1
            chap = 0
            buf = []
            continue

        cm = CHAP_OK_RE.match(line)
        if cm:
            flush()
            chap += 1
            roman, title = cm.group(1), cm.group(2).strip()
            malformed = False
            buf = [line]
            continue

        bad = CHAP_BAD_RE.match(line)
        if bad and is_upper_title(bad.group(1)):
            flush()
            chap += 1
            roman, title = None, bad.group(1).strip()
            malformed = True
            buf = [line]
            continue

        # Só acumula DENTRO de um capítulo já aberto (front matter do livro é descartado
        # de propósito — mas agora nenhum capítulo cai nessa vala, porque o cabeçalho
        # malformado passou a abrir capítulo).
        if book > 0 and chap > 0:
            buf.append(line)

    flush()

    per_book = {}
    for b, c, t, r, mf, ls in chapters:
        per_book.setdefault(b, []).append((c, t, r, mf, len(''.join(ls))))

    print(f'fonte: {SRC}')
    print(f'capítulos detectados: {len(chapters)} (esperado 59)')
    print(f'  bem-formados: {sum(1 for x in chapters if not x[4])}'
          f' · malformados recuperados: {sum(1 for x in chapters if x[4])}')
    for b in sorted(per_book):
        items = per_book[b]
        marks = ''.join('*' if it[3] else '.' for it in items)
        print(f'  L{b:02d}: {len(items):2d} caps  [{marks}]')
    print('  (* = capítulo recuperado de cabeçalho malformado)')

    if len(chapters) != 59:
        print(f'\n✗ ABORTADO: esperava 59 capítulos, achei {len(chapters)}.', file=sys.stderr)
        return 1

    if a.dry_run:
        print('\n(dry-run — nada escrito)')
        return 0

    outdir = os.path.join(BASE, a.out)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    for b, c, t, r, mf, ls in chapters:
        name = clean_title(t) or 'Chapter'
        path = os.path.join(outdir, f'L{b:02d}-C{c:02d}-{name}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(''.join(ls))

    print(f'\n✓ {len(chapters)} capítulos escritos em {outdir}/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
