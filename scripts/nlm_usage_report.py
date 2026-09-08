#!/usr/bin/env python3
"""
Relatorio do experimento de cota (notebooklm_edson-g5e7).

Le logs/nlm_usage.jsonl e responde as duas perguntas do experimento:
  1) Qual a cadencia real de reposicao? (intervalo entre um rate-limit e a
     proxima criacao aceita — se o modelo novo vale, deve ficar perto de 5h)
  2) Onde esta o teto semanal? (quantas criacoes ocorreram na semana ISO antes
     de a API passar a recusar de forma persistente)

Uso:  python3 scripts/nlm_usage_report.py [--profile espanhol]
"""
import sys, os, argparse, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nlm_usage_log import events

def fmt_delta(seconds: int) -> str:
    h, m = divmod(int(seconds) // 60, 60)
    return f"{h}h{m:02d}m"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="")
    args = ap.parse_args()

    rows = sorted(events(args.profile), key=lambda r: r.get("epoch", 0))
    if not rows:
        print("Sem eventos registrados ainda. O log so comeca a encher na primeira"
              " criacao/recusa apos a instrumentacao (2026-09-08).")
        return

    by_profile = collections.defaultdict(list)
    for r in rows:
        by_profile[r.get("profile", "?")].append(r)

    for prof, evs in sorted(by_profile.items()):
        created = [e for e in evs if e["event"] == "created"]
        limited = [e for e in evs if e["event"] == "rate_limited"]
        failed  = [e for e in evs if e["event"] == "failed"]
        print(f"\n=== perfil '{prof}' ===")
        print(f"  criados: {len(created)} | rate-limited: {len(limited)} | falhas reais: {len(failed)}")
        print(f"  janela observada: {evs[0]['ts'][:16]} -> {evs[-1]['ts'][:16]}")

        # (1) reposicao: rate-limit seguido de criacao aceita
        gaps = []
        for lim in limited:
            nxt = next((c for c in created if c["epoch"] > lim["epoch"]), None)
            if nxt:
                gaps.append(nxt["epoch"] - lim["epoch"])
        if gaps:
            print(f"  reposicao apos recusa (n={len(gaps)}): "
                  f"min {fmt_delta(min(gaps))} | mediana {fmt_delta(sorted(gaps)[len(gaps)//2])} "
                  f"| max {fmt_delta(max(gaps))}")
            print("    -> se a mediana ficar perto de 5h, confirma a janela anunciada pelo Google")
        else:
            print("  reposicao: ainda sem par (recusa -> criacao aceita) para medir")

        # (2) volume por semana ISO e por dia
        per_week = collections.Counter(e["iso_week"] for e in created)
        print("  criados por semana ISO:")
        for wk, n in sorted(per_week.items()):
            lim_wk = sum(1 for e in limited if e["iso_week"] == wk)
            print(f"    {wk}: {n} criados, {lim_wk} recusas")
        per_day = collections.Counter(e["ts"][:10] for e in created)
        print("  criados por dia:")
        for d, n in sorted(per_day.items()):
            print(f"    {d}: {n}")

        # (3) maior sequencia de recusas seguidas = candidato a teto semanal
        streak = best = 0
        best_start = None
        for e in evs:
            if e["event"] == "rate_limited":
                if streak == 0:
                    start = e["ts"]
                streak += 1
                if streak > best:
                    best, best_start = streak, start
            elif e["event"] == "created":
                streak = 0
        if best >= 3:
            print(f"  ATENCAO: {best} recusas consecutivas a partir de {best_start[:16]}"
                  f" -> candidato a TETO SEMANAL (nao apenas fim de janela)")

if __name__ == "__main__":
    main()
