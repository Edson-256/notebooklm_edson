#!/usr/bin/env python3
"""
Stitcher (Fase 2, bookkeeping) — consome a saida dos agentes autores (workflow don-quijote-cenas)
e monta deterministicamente:
  - _cenas_manifest.json  (numeracao GLOBAL continua seq_global 1..N; cena_local por capitulo)
  - _anchors.json         ({ "<seq_global>": {inicio, fim} })

A INTELIGENCIA (quais cenas, por que, ancoras) vem dos agentes. Aqui so:
  - ordena tudo por 'cap' global e por 'cena_local';
  - atribui seq_global sequencial;
  - mapeia cada cena ao ARQUIVO FISICO em DQ-capitulos/ que contem a ancora 'inicio' (resolve
    capitulos splitados _p1/_p2);
  - VERIFICA que 'inicio' e 'fim' casam verbatim no arquivo (regex \\s+ tolerante a quebras),
    reportando divergencias (para re-autoria manual — nao inventa).

Aceita 1+ arquivos de entrada (--input), mesclando por 'cap' — assim lotes sucessivos (calibracao
+ resto) re-montam um manifesto global consistente. Cada input e o retorno do workflow: um objeto
{ "units": [ {cap, parte, cap_natural, files, cenas:[...]}, ... ] } (ou uma lista de units).

Uso:
    python3 scripts/stitch_cenas.py --input raw1.json [raw2.json ...] [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
CAP_DIR = PROJ / "DQ-capitulos"
MANIFEST = PROJ / "_cenas_manifest.json"
ANCHORS = PROJ / "_anchors.json"

MANIFEST_META = {
    "obra": "Don Quijote de la Mancha",
    "autor": "Miguel de Cervantes Saavedra",
    "slug": "don-quijote",
    "language_name": "modern European Spanish (es-ES)",
}
PILARES = {"intuicao", "sinceridade", "memoria", "meio"}


# classes de vogal/consoante acentuada (base -> variantes) p/ matching tolerante a acento:
# alguns agentes copiaram a ancora SEM os acentos do castelhano original; casamos assim mesmo
# e AUTO-CURAMOS a ancora para o texto verbatim real do arquivo.
ACCENT_CLASS = {
    "a": "aáàäâã", "e": "eéèëê", "i": "iíìïî", "o": "oóòöôõ",
    "u": "uúùüû", "n": "nñ", "c": "cç", "y": "yý",
}


def _strip_accents(ch: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c))


def _char_pattern(ch: str) -> str:
    base = _strip_accents(ch).lower()
    if base in ACCENT_CLASS:
        return "[" + ACCENT_CLASS[base] + "]"
    return re.escape(ch)


def anchor_regex(anchor: str):
    parts = ["".join(_char_pattern(c) for c in tok) for tok in anchor.split()]
    return re.compile(r"\s+".join(parts), re.IGNORECASE)


def find_span(files_text: dict, anchor: str, min_tokens: int = 4):
    """Retorna (basename, texto_verbatim_casado) do 1o arquivo que contem a ancora; senao (None, None).
    Se a ancora completa nao casar (deslize de transcricao do agente: 1 palavra trocada/omitida),
    tenta PREFIXOS progressivamente menores ate min_tokens — basta localizar a posicao. O texto
    verbatim devolvido e sempre o que esta REALMENTE no arquivo (auto-cura)."""
    toks = anchor.split()
    if not toks:
        return None, None
    for n in range(len(toks), min_tokens - 1, -1):
        rx = anchor_regex(" ".join(toks[:n]))
        for basename, text in files_text.items():
            m = rx.search(text)
            if m:
                return basename, m.group(0)
    return None, None


def load_units(paths):
    units = []
    for p in paths:
        data = json.loads(Path(p).read_text(encoding="utf-8"))
        batch = data["units"] if isinstance(data, dict) and "units" in data else data
        units.extend(batch)
    return units


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", nargs="+", required=True, help="1+ JSONs de saida do workflow")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    idx = json.loads((CAP_DIR / "_capitulos_index.json").read_text(encoding="utf-8"))
    width = idx.get("width", 3)
    files_by_cap = {}
    for c in idx["capitulos"]:
        files_by_cap.setdefault(c["cap"], []).append(c["arquivo"])

    units = load_units(args.input)
    # dedup por cap (ultimo vence), depois ordena
    by_cap = {}
    for u in units:
        if u.get("cenas"):
            by_cap[u["cap"]] = u
    ordered = [by_cap[k] for k in sorted(by_cap)]

    cenas_out, anchors_out = [], {}
    problems, warnings = [], []
    seq = 0

    for u in ordered:
        cap = u["cap"]
        basenames = files_by_cap.get(cap, [])
        if not basenames:
            problems.append(f"cap {cap}: sem arquivo em _capitulos_index.json")
            continue
        files_text = {b: (CAP_DIR / b).read_text(encoding="utf-8") for b in basenames}

        local_expected = 1
        for cena in sorted(u["cenas"], key=lambda c: c["cena_local"]):
            seq += 1
            cl = cena["cena_local"]
            if cl != local_expected:
                warnings.append(f"cap {cap}: cena_local {cl} != esperado {local_expected} (renumerando)")
            local_expected += 1

            if cena["pilar_foco"] not in PILARES:
                problems.append(f"cap {cap} cena {cl}: pilar invalido '{cena['pilar_foco']}'")

            src_ini, ini_verbatim = find_span(files_text, cena.get("inicio", ""))
            src_fim, fim_verbatim = find_span(files_text, cena.get("fim", ""))
            if src_ini is None:
                problems.append(f"seq {seq} (cap {cap} cena {cl}): ANCORA inicio nao casou: {cena.get('inicio','')!r}")
            if src_fim is None:
                problems.append(f"seq {seq} (cap {cap} cena {cl}): ANCORA fim nao casou: {cena.get('fim','')!r}")
            if src_ini and src_fim and src_ini != src_fim:
                warnings.append(f"seq {seq} (cap {cap} cena {cl}): inicio em {src_ini} mas fim em {src_fim} "
                                f"(cena cruza split; source_chapter={src_ini})")
            source_chapter = src_ini or src_fim or basenames[0]
            # AUTO-CURA: grava o texto verbatim real do arquivo (com acentos), nao o que o agente digitou
            inicio_final = ini_verbatim if ini_verbatim is not None else cena.get("inicio", "")
            fim_final = fim_verbatim if fim_verbatim is not None else cena.get("fim", "")

            cenas_out.append({
                "seq_global": seq,
                "cap": cap,
                "cena_local": local_expected - 1,
                "titulo": cena["titulo"],
                "localizacao": cena["localizacao"],
                "source_chapter": source_chapter,
                "pilar_foco": cena["pilar_foco"],
                "resumo": cena["resumo"],
                "justificativa_cof": cena["justificativa_cof"],
            })
            anchors_out[str(seq)] = {"inicio": inicio_final, "fim": fim_final}

    # relatorio
    print(f"\n  Unidades com cenas: {len(ordered)} | cenas totais: {len(cenas_out)} | seq 1..{seq}")
    if warnings:
        print(f"\n  AVISOS ({len(warnings)}):")
        for w in warnings:
            print("   -", w)
    if problems:
        print(f"\n  PROBLEMAS ({len(problems)}) — corrigir antes de gerar audio:")
        for p in problems:
            print("   -", p)

    if args.dry_run:
        print("\n  [dry-run] nada escrito.\n")
        return 1 if problems else 0

    manifest = dict(MANIFEST_META)
    manifest["width"] = width
    manifest["cenas"] = cenas_out
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    ANCHORS.write_text(json.dumps(anchors_out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Escrito: {MANIFEST}")
    print(f"  Escrito: {ANCHORS}\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
