#!/usr/bin/env python3
"""
Fase 3 — Gera os prompts deep-dive (1 por cena) a partir do _cenas_manifest.json + _anchors.json.

Padrao (aprovado): INSTRUCOES EM INGLES, OUTPUT EM pt-BR ('pensar em ingles, produzir em portugues').
Template sequencial: persona -> ancora de serie (N de TOTAL) -> abertura 'cena X, cap Y' + recap da
cena anterior -> ancoras (1a/ultima frase reais) -> o que acontece (resumo) -> pilar COF em foco
(nomeado, NAO redefinido apos o ep.1) -> diretiva de output pt-BR -> gancho da proxima cena.
A metodologia da leitura formativa e explicada SO no episodio 1.

Uso:
    python3 03_build_prompts.py --project projetos/literatura/<slug> [--dry-run]
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata
from pathlib import Path

PILAR_NOME = {
    "intuicao": "Primazia da Intuição (feel the scene before reasoning about it)",
    "sinceridade": "Sinceridade Existencial (seek the human truth, not ready-made ideas)",
    "memoria": "Memória Afetiva e Imaginativa (keep living images, not summaries)",
    "meio": "Literatura como Meio (read to grow as a person, not to 'have read')",
}

PERSONA = ("Act as a senior humanities tutor recording an instructional \"deep dive\" audio for a "
           "layperson (no academic background in literature or philosophy). Tone: warm, "
           "conversational, vivid, like an experienced teacher talking to a curious adult.")

METHODOLOGY = """Because this is the FIRST episode, spend the opening minutes introducing the listener, in plain language with everyday analogies:
- **What formative reading is**, versus reading for entertainment — one changes the soul of the reader, the other doesn't.
- **Who Olavo de Carvalho was** (very briefly) and his central idea: intelligence works on the material the imagination supplies; a poor inner repertoire of human types yields poor judgment of real life.
- **The four pillars**, one sentence each: (1) Primazia da Intuição; (2) Sinceridade Existencial; (3) Memória Afetiva e Imaginativa; (4) Literatura como Meio.
- **Vicarious experience** — "wearing the skin" of a character, even one we dislike, to enlarge our own soul.
- **A practical note:** the series is sequential and the method will NOT be re-explained in later episodes; invite the listener to start from the beginning.
"""

OUTPUT_REQ = ("The ENTIRE audio MUST be spoken in fluent, natural **Brazilian Portuguese (pt-BR)**. "
              "The English above is instruction only; never read it aloud or switch languages.")


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.strip()).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^\w\-]", "", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def build_prompt(c, total, width, anchors, prev, nxt, obra, autor):
    seq = c["seq_global"]
    a = anchors.get(str(seq), {})
    lines = [PERSONA, "", "## Series context",
             f"This is audio **{seq} of {total}** on *{obra}* ({autor}), examined through the "
             f"formative-reading method taught by Olavo de Carvalho in the Seminário de Filosofia (COF)."]
    if seq == 1:
        lines += ["", METHODOLOGY]
    else:
        lines += ["", "The method was explained in episode 1 — **do NOT re-explain it here.** "
                  "Simply name the pillar in focus and apply it."]
    # opening
    lines += ["", "## Opening (first ~30 seconds)",
              f"Announce clearly: \"Este é o áudio da **cena {seq}**, **capítulo {c['cap']}**.\""]
    if prev is not None:
        lines += [f"Then recap the previous scene in one or two sentences (do not dwell): "
                  f"\"{prev['titulo']}\" — {prev['resumo']}"]
    # scene data + anchors
    lines += ["", "## Scene data",
              f"- **Scene:** {seq} of {total}",
              f"- **Location:** {c['localizacao']}",
              f"- **Title:** \"{c['titulo']}\""]
    if a:
        lines += ["", "## Scene anchors (delimit the passage WITHIN the chapter)",
                  f"- **Begins at:** \"{a.get('inicio','')}\"",
                  f"- **Ends at:** \"{a.get('fim','')}\""]
    lines += ["", "## What happens", c["resumo"],
              "", "## Pillar in focus",
              f"**{PILAR_NOME[c['pilar_foco']]}.** {c['justificativa_cof']} "
              "Lead the listener to *experience* this, not merely understand it.",
              "", "## Output requirement", OUTPUT_REQ,
              "", "## Closing (last ~30 seconds)"]
    if nxt is not None:
        lines += [f"Briefly tease the next scene: \"{nxt['titulo']}\" — {nxt['resumo']}"]
    else:
        lines += ["This is the final episode. Close the series: invite the listener to let the whole "
                  "arc resonate, and to reread the novella now with formed eyes."]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Fase 3: gera prompts deep-dive a partir do manifesto")
    ap.add_argument("--project", required=True)
    ap.add_argument("--manifest", default="_cenas_manifest.json")
    ap.add_argument("--anchors", default="_anchors.json")
    ap.add_argument("--out", default="prompts_cenas")
    ap.add_argument("--max-chars", type=int, default=10000)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    proj = Path(args.project).expanduser()
    man = json.loads((proj / args.manifest).read_text(encoding="utf-8"))
    anchors = json.loads((proj / args.anchors).read_text(encoding="utf-8")) if (proj / args.anchors).is_file() else {}
    cenas = sorted(man["cenas"], key=lambda c: c["seq_global"])
    total = len(cenas)
    width = man.get("width", 2)
    obra, autor = man["obra"], man["autor"]

    outdir = proj / args.out
    if not args.dry_run:
        outdir.mkdir(parents=True, exist_ok=True)

    truncated = []
    for i, c in enumerate(cenas):
        prev = cenas[i - 1] if i > 0 else None
        nxt = cenas[i + 1] if i < total - 1 else None
        body = build_prompt(c, total, width, anchors, prev, nxt, obra, autor)
        fn = (f"prompt_{c['seq_global']:0{width}d}_cap-{c['cap']:0{width}d}"
              f"_cena-{c['cena_local']:0{width}d}_{slugify(c['titulo'])}.md")
        if len(body) > args.max_chars:
            truncated.append(fn)
        if args.dry_run:
            print(f"  {fn}  ({len(body)} chars)")
        else:
            (outdir / unicodedata.normalize("NFC", fn)).write_text(body, encoding="utf-8")

    print(f"\n  {obra}: {total} prompts {'(dry-run)' if args.dry_run else 'gerados em ' + str(outdir)}")
    if truncated:
        print(f"  AVISO: {len(truncated)} prompt(s) acima de {args.max_chars} chars (revisar): " + ", ".join(truncated))
    else:
        print(f"  Todos abaixo de {args.max_chars} chars (sem truncamento).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
