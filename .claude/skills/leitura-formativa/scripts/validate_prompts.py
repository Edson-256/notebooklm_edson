#!/usr/bin/env python3
"""
Valida os prompts de um projeto ANTES de deixar o runner rodar desatendido (cron/launchd).

Motivacao (2026-08-09, projeto o-idiota): prompts escritos a mao ou por agentes nao passam
pela checagem do 03_build_prompts.py. Dois defeitos ja mordidos em producao:
  - prompt > MAX_FOCUS_CHARS -> antes truncava em silencio; hoje o runner RECUSA a cena,
    mas num cron desatendido isso vira "cena pulada" que ninguem ve.
  - DUAS versoes do mesmo prompt (nome antigo + nome novo) -> load_prompt pega a primeira
    em ordem alfabetica, que pode ser a versao velha e generica.

Uso:
    python3 validate_prompts.py --project projetos/literatura/<slug>
    python3 validate_prompts.py --project ... --strict   # avisos viram erro (exit 1)
"""
from __future__ import annotations
import argparse, json, re, sys
from collections import defaultdict
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("ERRO: requer Python 3.11+ (tomllib).", file=sys.stderr); sys.exit(2)

MAX_FOCUS_CHARS = 10000
MIN_ESPERADO = 3000          # abaixo disso quase certamente e o template generico antigo

SECOES = ["## Series context", "## Scene data", "## Scene anchors",
          "## Resumo da cena", "## Aplicação da leitura formativa",
          "### Analogias modernas", "### A viagem imaginativa",
          "## Anti-padrões", "## Encerramento", "## Delivery requirements"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    proj = Path(args.project).expanduser()
    cfg = tomllib.loads((proj / "projeto.toml").read_text(encoding="utf-8"))
    man = json.loads((proj / cfg["paths"]["manifest"]).read_text(encoding="utf-8"))
    anchors_p = proj / cfg["paths"]["anchors"]
    anchors = json.loads(anchors_p.read_text(encoding="utf-8")) if anchors_p.is_file() else {}
    pdir = proj / cfg["paths"]["prompts"]
    cenas = sorted(man["cenas"], key=lambda c: c["seq_global"])
    width = man.get("width", 2)
    total = len(cenas)

    # indexa arquivos por prefixo prompt_NN_
    por_seq = defaultdict(list)
    for f in sorted(pdir.glob("prompt_*.md")):
        m = re.match(r"prompt_(\d+)_", f.name)
        if m:
            por_seq[int(m.group(1))].append(f)

    erros, avisos = [], []
    for c in cenas:
        seq = c["seq_global"]
        fs = por_seq.get(seq, [])
        if not fs:
            erros.append(f"cena {seq}: prompt AUSENTE"); continue
        if len(fs) > 1:
            erros.append(f"cena {seq}: {len(fs)} arquivos p/ a mesma cena (o runner usaria "
                         f"'{fs[0].name}') -> {[x.name for x in fs]}")
        f = fs[0]
        t = f.read_text(encoding="utf-8").strip()
        n = len(t)

        if n > MAX_FOCUS_CHARS:
            erros.append(f"cena {seq}: {n} chars (+{n-MAX_FOCUS_CHARS}) — seria RECUSADA")
        elif n < MIN_ESPERADO:
            erros.append(f"cena {seq}: só {n} chars — parece o template genérico antigo")
        elif n > MAX_FOCUS_CHARS - 100:
            avisos.append(f"cena {seq}: {n} chars — a <100 do teto, margem apertada")

        faltando = [s for s in SECOES if s not in t]
        if faltando:
            erros.append(f"cena {seq}: seções ausentes: {', '.join(faltando)}")

        if "Hard scope rule" not in t:
            erros.append(f"cena {seq}: SEM 'Hard scope rule' (áudio pode invadir a cena seguinte)")

        if "pt-BR" not in t:
            erros.append(f"cena {seq}: SEM diretiva de idioma pt-BR")

        if f"audio {seq} of {total}" not in t:
            avisos.append(f"cena {seq}: não declara 'audio {seq} of {total}'")

        a = anchors.get(str(seq), {})
        for campo, rotulo in (("inicio", "Begins at"), ("fim", "Ends at")):
            val = a.get(campo)
            if val and val[:40] not in t:
                erros.append(f"cena {seq}: âncora '{rotulo}' do prompt não bate com _anchors.json")

        n_analogias = len(re.findall(r"^- ", t[t.find("### Analogias modernas"):
                                       t.find("### A viagem imaginativa")], re.M)) \
            if "### Analogias modernas" in t and "### A viagem imaginativa" in t else 0
        if n_analogias and n_analogias != 5:
            avisos.append(f"cena {seq}: {n_analogias} analogias (esperado 5)")

    orfaos = sorted(set(por_seq) - {c["seq_global"] for c in cenas})
    for s in orfaos:
        avisos.append(f"prompt_{s:0{width}d}_* existe mas não há cena {s} no manifesto")

    print(f"\n  {cfg['obra']['titulo']} — {total} cenas | {sum(len(v) for v in por_seq.values())} arquivos de prompt")
    if erros:
        print(f"\n  ERROS ({len(erros)}) — corrigir ANTES de agendar:")
        for e in erros: print(f"    ✗ {e}")
    if avisos:
        print(f"\n  avisos ({len(avisos)}):")
        for a in avisos: print(f"    ! {a}")
    if not erros and not avisos:
        print("\n  ✓ tudo certo: tamanhos, seções, âncoras, escopo e idioma.")
    elif not erros:
        print("\n  ✓ sem erros bloqueantes.")
    print()
    return 1 if erros or (args.strict and avisos) else 0


if __name__ == "__main__":
    sys.exit(main())
