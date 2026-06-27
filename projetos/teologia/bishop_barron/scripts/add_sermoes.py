#!/usr/bin/env python3
"""
Adiciona ao notebook os Sermões Dominicais & Homilias do Bishop Barron, do mais
recente ao mais antigo, até LIMITE fontes. Lotes via `nlm source add -y ... -y ...`.

Resumível: lê as fontes já presentes (por título resolvido OU pela própria URL,
que o NLM usa como título enquanto processa) e pula o que já está lá.
"""
import subprocess
import sys
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ORDEM = BASE / "data" / "sermoes_ordem.tsv"
LOG = BASE / "data" / "add_sermoes.log"
NB = "b2da3845-1123-4859-bc14-46f2f2b6a29a"
PROFILE = "default"
LIMITE = 300
BATCH = 20

def log(msg):
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")

def current_sources():
    r = subprocess.run(["nlm", "source", "list", NB, "--json", "--profile", PROFILE],
                       capture_output=True, text=True)
    try:
        data = json.loads(r.stdout)
    except Exception:
        return [], set()
    titles = set()
    vids = set()
    for s in data:
        t = s.get("title") or ""
        titles.add(t.strip())
        if "watch?v=" in t:
            vids.add(t.split("watch?v=")[-1].split("&")[0])
    return data, (titles, vids)

def main():
    rows = [l.rstrip("\n").split("\t") for l in ORDEM.open(encoding="utf-8")]
    target = rows[:LIMITE]                      # 300 mais recentes
    log(f"== Alvo: {len(target)} sermões (mais recentes). Notebook {NB} ==")

    data, (titles, vids) = current_sources()
    log(f"Fontes já presentes: {len(data)}")

    # filtra os que faltam (por id ou por título exato)
    pendentes = [(vid, t) for vid, t in target
                 if vid not in vids and t.strip() not in titles]
    log(f"Pendentes a adicionar: {len(pendentes)}")

    added = 0
    for i in range(0, len(pendentes), BATCH):
        lote = pendentes[i:i+BATCH]
        args = ["nlm", "source", "add", NB, "--profile", PROFILE]
        for vid, _t in lote:
            args += ["-y", f"https://www.youtube.com/watch?v={vid}"]
        n = i // BATCH + 1
        log(f"-- Lote {n}: enviando {len(lote)} (já no notebook ~{len(data)+added}) ...")
        r = subprocess.run(args, capture_output=True, text=True)
        out = (r.stdout or "") + (r.stderr or "")
        ok = out.count("Added source") + out.count("added.")
        log(out.strip()[-600:])
        added += len(lote)

    # verificação final
    data2, _ = current_sources()
    log(f"== FIM. Fontes no notebook agora: {len(data2)} (meta {LIMITE}) ==")

if __name__ == "__main__":
    main()
