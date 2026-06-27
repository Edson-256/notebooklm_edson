#!/usr/bin/env python3
"""
Classifica os vídeos do canal Jordan B. Peterson (data/jbp_videos.tsv) por assunto
e gera CATALOGO_JORDAN_PETERSON.md (tabelas título | link prontas p/ NotebookLM).

Estágio 1: override por id (data/overrides.tsv) — prioridade absoluta.
Estágio 2: keyword single-label por ORDEM DE PRIORIDADE (1ª regex que casa vence).
Heurística sobre o TÍTULO apenas. NÃO usar \bpeterson\b/\bjordan\b como keyword.
"""
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TSV = BASE / "data" / "jbp_videos.tsv"
OVERRIDES = BASE / "data" / "overrides.tsv"
OUT = BASE / "CATALOGO_JORDAN_PETERSON.md"
YT = "https://www.youtube.com/watch?v="

# Ordem = prioridade. Formato muito identificável (Podcast) primeiro; temas
# específicos antes dos genéricos; "Palestras" genérico perto do fim.
CATEGORIAS = [
    ("Podcast — Entrevistas & Convidados (The JBP Podcast)", [
        r"\| ?ep ?\d", r"answer the call", r"\bpodcast\b", r"\| ?s\d+ ?e\d+",
    ]),
    ("Série Bíblica, Deus & Religião", [
        r"biblical series", r"book of exodus", r"\bexodus\b", r"\bgenesis\b",
        r"sermon on the mount", r"\bgospels?\b", r"\bgospel\b", r"\bbible\b",
        r"\bgod\b", r"\bchrist\b", r"\bjesus\b", r"religio", r"\bsacred\b",
        r"\bscripture", r"\bprayer\b", r"\bsoul\b", r"\bdivine\b",
        r"jonathan pageau", r"\bcain and abel\b", r"\bresurrection\b",
        r"\btheolog", r"\bspirit", r"\bmoses\b", r"\babraham\b",
    ]),
    ("Maps of Meaning, Mito & Arquétipos", [
        r"maps of meaning", r"\bmytholog", r"\bmyth\b", r"\barchetyp",
        r"\bsymbol", r"\bhero\b", r"\bdragon\b", r"\bstory\b.*\bmeaning\b",
    ]),
    ("Personalidade & Psicologia", [
        r"\bpersonality\b", r"psycholog", r"big five", r"\btraits?\b",
        r"temperament", r"\bjung\b", r"\bfreud\b", r"\biq\b",
        r"\bintelligence\b", r"\bneuropsych", r"\bdepression\b",
        r"\banxiety\b", r"\bmental health\b", r"\bemotion",
    ]),
    ("Cultura, Política & Ideologia", [
        r"\bwoke\b", r"ideolog", r"\bgender\b", r"marxis", r"\btrans\b",
        r"postmodern", r"\bclimate\b", r"trudeau", r"\btrump\b", r"\bcanada\b",
        r"free speech", r"censorship", r"\bwest\b", r"\bfeminis",
        r"\bpolitic", r"\bwar\b", r"\belection\b", r"\bdei\b", r"\bcommunis",
        r"\bsocialis", r"\btotalitarian", r"\bcorporat", r"\bwef\b", r"\bun\b",
    ]),
    ("Autodesenvolvimento, Sentido & Vida", [
        r"rules? for life", r"\bhow to\b", r"responsibilit", r"\bmeaning\b",
        r"\bsuffering\b", r"\bhabit", r"\bproductiv", r"\bgoals?\b",
        r"\bpurpose\b", r"\bdiscipline\b", r"\bself\b", r"\bsuccess\b",
        r"\bmotivat", r"\brelationship", r"\bmarriage\b", r"\bdating\b",
        r"\bparent", r"\bfear\b", r"\bcourage\b",
    ]),
    ("Palestras, Conferências & Discursos", [
        r"\blecture", r"\bharvard\b", r"\buniversity\b", r"\bbiology\b",
        r"\bneuroscience\b", r"\baddress\b", r"\bspeech\b", r"\bkeynote\b",
        r"\bseminar", r"\bdebate\b", r"\bconference\b", r"\bcollege\b",
    ]),
    ("Q&A / AMA & Mensagens diretas", [
        r"\bama\b", r"q ?& ?a", r"monthly q", r"\bmessage\b", r"\bannouncement",
    ]),
]

def load_overrides():
    ov = {}
    if OVERRIDES.exists():
        for line in OVERRIDES.open(encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if len(p) == 2:
                ov[p[0]] = p[1]
    return ov

_OV = load_overrides()

NOVAS = []  # categorias introduzidas só por override (entram antes de "Outros")
ORDEM_EXIBICAO = [c[0] for c in CATEGORIAS]

def classify(vid: str, title: str) -> str:
    if vid in _OV:
        return _OV[vid]
    t = title.lower()
    for nome, padroes in CATEGORIAS:
        for p in padroes:
            if re.search(p, t):
                return nome
    return "Outros / A classificar"

def main():
    rows = []
    with TSV.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\\t")   # separador literal "\t"
            if len(parts) < 2:
                continue
            vid, title = parts[0], parts[1]
            dur = parts[2] if len(parts) > 2 else "NA"
            rows.append((vid, title, dur))

    buckets = {}
    for vid, title, dur in rows:
        buckets.setdefault(classify(vid, title), []).append((vid, title, dur))

    ordem = list(ORDEM_EXIBICAO)
    for cat in buckets:
        if cat not in ordem and cat != "Outros / A classificar":
            ordem.append(cat)
    ordem.append("Outros / A classificar")

    def fmt_dur(d):
        try:
            s = int(float(d)); return f"{s//60}:{s%60:02d}"
        except Exception:
            return "—"

    total = len(rows)
    lines = []
    lines.append("# Catálogo — Vídeos de Jordan B. Peterson (YouTube)\n")
    lines.append(f"Canal: <https://www.youtube.com/@JordanBPeterson/videos> · "
                 f"**{total} vídeos** catalogados · metadados públicos (títulos + links).\n")
    lines.append("> Para criar o notebook: em cada seção, copie a coluna **Link** "
                 "dos vídeos desejados e cole no NotebookLM. Respeite o limite de "
                 "fontes do seu plano (Plus/Pro = 300; grátis = 50).\n")
    lines.append("## Índice por assunto\n")
    for cat in ordem:
        n = len(buckets.get(cat, []))
        if n:
            anchor = re.sub(r"[^a-z0-9]+", "-", cat.lower()).strip("-")
            lines.append(f"- [{cat}](#{anchor}) — {n}")
    lines.append("")

    for cat in ordem:
        items = buckets.get(cat, [])
        if not items:
            continue
        items.sort(key=lambda x: x[1].lower())
        lines.append(f"\n## {cat}\n")
        lines.append(f"_{len(items)} vídeos_\n")
        lines.append("| # | Título | Duração | Link |")
        lines.append("|---|--------|---------|------|")
        for i, (vid, title, dur) in enumerate(items, 1):
            safe = title.replace("|", "\\|")
            lines.append(f"| {i} | {safe} | {fmt_dur(dur)} | {YT}{vid} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Total: {total}")
    for cat in ordem:
        n = len(buckets.get(cat, []))
        if n:
            print(f"  {n:5d}  {cat}")
    print(f"\nGerado: {OUT}")

if __name__ == "__main__":
    main()
