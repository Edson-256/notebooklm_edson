#!/usr/bin/env python3
"""
Adiciona ao notebook os vídeos listados em data/add_3cats.tsv (id \\t título),
em lotes via `nlm source add -y ... -y ...`. Resumível: pula o que já está lá.
"""
import subprocess, json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
LISTA = BASE / "data" / "add_3cats.tsv"
LOG = BASE / "data" / "add_to_notebook.log"
NB = "1ddd8d90-f423-40e7-a2b5-a4931d52b079"
PROFILE = "default"
BATCH = 20

def log(msg):
    print(msg, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")

def current():
    r = subprocess.run(["nlm","source","list",NB,"--json","--profile",PROFILE],
                       capture_output=True, text=True)
    try: data = json.loads(r.stdout)
    except Exception: return [], (set(), set())
    titles, vids = set(), set()
    for s in data:
        t = (s.get("title") or "").strip(); titles.add(t)
        if "watch?v=" in t: vids.add(t.split("watch?v=")[-1].split("&")[0])
    return data, (titles, vids)

def main():
    rows = [l.rstrip("\n").split("\t") for l in LISTA.open(encoding="utf-8")]
    rows = [(r[0], r[1]) for r in rows if len(r) >= 2]
    log(f"== Alvo: {len(rows)} vídeos. Notebook {NB} ==")
    data, (titles, vids) = current()
    log(f"Já presentes: {len(data)}")
    pend = [(vid,t) for vid,t in rows if vid not in vids and t.strip() not in titles]
    log(f"Pendentes: {len(pend)}")
    added = 0
    for i in range(0, len(pend), BATCH):
        lote = pend[i:i+BATCH]
        args = ["nlm","source","add",NB,"--profile",PROFILE]
        for vid,_t in lote: args += ["-y", f"https://www.youtube.com/watch?v={vid}"]
        log(f"-- Lote {i//BATCH+1}: enviando {len(lote)} (no notebook ~{len(data)+added}) ...")
        r = subprocess.run(args, capture_output=True, text=True)
        log(((r.stdout or "")+(r.stderr or "")).strip()[-500:])
        added += len(lote)
    data2,_ = current()
    log(f"== FIM. Fontes no notebook: {len(data2)} ==")

if __name__ == "__main__":
    main()
