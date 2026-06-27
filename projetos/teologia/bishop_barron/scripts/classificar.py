#!/usr/bin/env python3
"""
Classifica os vídeos do canal Bishop Barron (data/barron_videos.tsv) por assunto
e gera um catálogo em Markdown com tabelas (título | link) prontas para copiar os
links e colar no NotebookLM.

Entrada : data/barron_videos.tsv  (id \t title \t duration \t view_count \t upload_date)
Saída   : CATALOGO_BISHOP_BARRON.md

Classificação single-label, por ORDEM DE PRIORIDADE (primeira regra que casa vence).
A ordem é deliberada: séries/formatos muito identificáveis primeiro, temas amplos
depois, para minimizar o balde "A classificar". Heurística sobre o TÍTULO apenas.
"""
import csv
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
TSV = BASE / "data" / "barron_videos.tsv"
OVERRIDES = BASE / "data" / "overrides.tsv"   # id -> categoria (classificação manual/LLM)
OUT = BASE / "CATALOGO_BISHOP_BARRON.md"
YT = "https://www.youtube.com/watch?v="

# Ordem de exibição (estudo-friendly). Categorias do keyword-classifier + as 5
# novas vindas dos overrides. Qualquer categoria não listada aqui cai antes de
# "Outros" automaticamente.
ORDEM_EXIBICAO = [
    "Sermões Dominicais & Homilias",
    "Homilias, Reflexões & Vida Cristã",
    "Bíblia & Escritura",
    "Cristologia, Trindade & Doutrina",
    "Filosofia, Fé & Razão",
    "Ateísmo, Secularismo & Apologética",
    "Vida Espiritual, Oração, Sacramentos & Liturgia",
    "Santos, Doutores & Figuras da Igreja",
    "Igreja, Vaticano & Atualidade Eclesial",
    "Moral, Ética, Política & Cultura Contemporânea",
    "Literatura, Poesia & Grandes Livros",
    "Cinema, TV & Cultura (comentários)",
    "Discursos & Palestras (universidades, academias, keynotes)",
    "«Bishop Barron Presents» — Diálogos & Entrevistas",
    "Word on Fire Show / Podcast & Q&A",
    "Série «Catolicismo» (Catholicism)",
    "Série «Pivotal Players»",
    "Viagens, Peregrinações & Lugares",
    "Institucional, Anúncios & Bastidores (Word on Fire)",
    "Outros / A classificar",
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

# Cada categoria: (nome, lista de regex aplicadas em minúsculas). Ordem = prioridade.
CATEGORIAS = [
    ("Sermões Dominicais & Homilias", [
        r"sunday sermon", r"\bhomily\b", r"\bsermon\b", r"gospel for",
        r"gospel reflection", r"sunday gospel",
    ]),
    ("Série «Catolicismo» (Catholicism)", [
        r"\bcatholicism\b.*(episode|series|presents|pivotal|trailer|clip)",
        r"catholicism:", r"the catholicism", r"catholicism project",
    ]),
    ("Série «Pivotal Players»", [
        r"pivotal players?",
    ]),
    ("«Bishop Barron Presents» — Diálogos & Entrevistas", [
        r"bishop barron presents", r"\bin conversation\b", r"\binterview\b",
        r"\bdialogue with\b",
    ]),
    ("Word on Fire Show / Podcast & Q&A", [
        r"word on fire show", r"\bwofs?\b", r"\bwof \d", r"podcast",
        r"ask (bishop|fr|father)", r"\bq ?& ?a\b", r"questions? and answers?",
        r"answers your questions", r"reddit", r"mailbag",
    ]),
    ("Cinema, TV & Cultura (comentários)", [
        r"\bfilm\b", r"\bmovie\b", r"cinema", r"spoilers?", r"\bhbo\b",
        r"netflix", r"\boscar", r"the departed", r'"[^"]+" (commentary|review)',
        r"commentary by bishop", r'on the (hbo|movie|film|series)', r"\brome\b",
        r"game of thrones", r"\btv\b", r"television", r"breaking bad", r"fargo",
        r"star wars", r"the matrix", r"avatar", r"barbie", r"oppenheimer",
        r"superhero", r"\bjoker\b",
    ]),
    ("Literatura, Poesia & Grandes Livros", [
        r"\bdante\b", r"tolkien", r"\bc\.? ?s\.? ?lewis\b", r"flannery",
        r"shakespeare", r"\bnovel\b", r"\bpoet", r"\bpoem\b", r"literature",
        r"chesterton", r"\bbook\b", r"\bnovelist\b", r"\bliterary\b",
        r"divine comedy", r"\bhomer\b", r"dostoevsky", r"\bwaugh\b",
    ]),
    ("Filosofia, Fé & Razão", [
        r"aquinas", r"thomas aquinas", r"\bphilosoph", r"metaphysic",
        r"\breason\b", r"faith and reason", r"faith & reason", r"\bplato\b",
        r"aristotle", r"\bbeing\b", r"existence of god", r"god's existence",
        r"natural law", r"\blogos\b", r"\bnihilism\b", r"\bthomist",
        r"\bkierkegaard\b", r"augustine'?s? confession", r"nietzsche",
        r"\bmarx", r"\bhegel\b", r"nominalism", r"\bheidegger\b",
        r"\bsartre\b", r"\bcamus\b", r"transcendent",
    ]),
    ("Ateísmo, Secularismo & Apologética", [
        r"atheis", r"agnostic", r"new atheism", r"dawkins", r"hitchens",
        r"sam harris", r"\bnones\b", r"secular", r"\bscientism\b",
        r"science and (faith|religion)", r"why .* (catholic|believe)",
        r"\bskeptic", r"materialism", r"jordan peterson", r"debate",
    ]),
    ("Bíblia & Escritura", [
        r"\bbible\b", r"scripture", r"\bgenesis\b", r"\bexodus\b", r"\bpsalm",
        r"\bisaiah\b", r"\bst\.? paul\b", r"\bapostle\b", r"\bgospel of\b",
        r"\bbook of\b", r"old testament", r"new testament", r"\bjob\b",
        r"\brevelation\b", r"\bromans\b", r"\bproverbs\b", r"\bbiblical\b",
    ]),
    ("Santos, Doutores & Figuras da Igreja", [
        r"\bst\.? ", r"\bsaint", r"john paul", r"benedict xvi",
        r"mother teresa", r"\bnewman\b", r"fulton sheen", r"\bmary\b",
        r"\bvirgin\b", r"\bapostles?\b", r"\bmartyr",
    ]),
    ("Vida Espiritual, Oração, Sacramentos & Liturgia", [
        r"\bprayer\b", r"\bpray\b", r"\bmass\b", r"eucharist", r"sacrament",
        r"\blent", r"\badvent\b", r"\brosary\b", r"confession", r"\bgrace\b",
        r"\bbaptism\b", r"\bliturgy\b", r"\bchristmas\b", r"\beaster\b",
        r"holy week", r"\bsoul\b", r"\bvirtue", r"spiritual",
    ]),
    ("Moral, Ética, Política & Cultura Contemporânea", [
        r"\babortion\b", r"\bmarriage\b", r"\bgender\b", r"\bidentity\b",
        r"\bpolitic", r"\bculture\b", r"\bwoke\b", r"\bfreedom\b",
        r"\bliberty\b", r"\bjustice\b", r"\bsuffering\b", r"\bevil\b",
        r"\bsex", r"\bsociety\b", r"\bsocial\b", r"\bdeath\b", r"euthanasia",
    ]),
    # Categoria genérica eclesial — DEPOIS das temáticas específicas para não
    # "roubar" vídeos. NÃO usar \bbishop\b aqui: casaria com "Bishop Barron".
    ("Igreja, Vaticano & Atualidade Eclesial", [
        r"vatican", r"\bsynod\b", r"\bconclave\b", r"\bpope\b",
        r"\bcardinal\b", r"\bdiocese\b", r"\bchurch\b",
        r"\bcatholic\b", r"evangeli", r"\bvocation", r"\bseminar",
    ]),
]

def classify(vid: str, title: str) -> str:
    if vid in _OV:                      # override manual/LLM tem prioridade
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
            # yt-dlp gravou o separador como os 2 chars literais "\t", não tab real
            parts = line.rstrip("\n").split("\\t")
            if len(parts) < 2:
                continue
            vid, title = parts[0], parts[1]
            dur = parts[2] if len(parts) > 2 else "NA"
            rows.append((vid, title, dur))

    buckets = {}
    for vid, title, dur in rows:
        cat = classify(vid, title)
        buckets.setdefault(cat, []).append((vid, title, dur))

    # ordem de exibição explícita; qualquer categoria fora da lista entra antes de "Outros"
    ordem = list(ORDEM_EXIBICAO)
    for cat in buckets:
        if cat not in ordem:
            ordem.insert(len(ordem) - 1, cat)

    def fmt_dur(d):
        try:
            s = int(float(d)); return f"{s//60}:{s%60:02d}"
        except Exception:
            return "—"

    total = len(rows)
    lines = []
    lines.append("# Catálogo — Vídeos do Bishop Robert Barron (YouTube)\n")
    lines.append(f"Canal: <https://www.youtube.com/@BishopBarron/videos> · "
                 f"**{total} vídeos** catalogados · "
                 "extração de metadados públicos (títulos + links), sem download de vídeo.\n")
    lines.append("> Para criar o notebook: em cada seção, copie a coluna **Link** "
                 "dos vídeos desejados e cole no NotebookLM (Adicionar fonte → "
                 "Link do YouTube). Respeite o limite de fontes do seu plano.\n")
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
