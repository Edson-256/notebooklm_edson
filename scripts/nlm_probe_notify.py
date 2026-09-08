#!/usr/bin/env python3
"""
Avisa quando a cota REPOE — o unico momento do experimento que exige atencao.

A sonda roda de hora em hora e, enquanto a conta estiver bloqueada, so acumula
recusas silenciosas. O dado que interessa e o instante em que uma criacao volta a
ser aceita depois de uma sequencia de recusas: e ele que da o intervalo real de
reposicao (notebooklm_edson-g5e7). Sem alerta, esse instante so seria notado na
proxima vez que alguem rodasse o relatorio a mao.

Chamado no fim de cron_probe.sh. Nao faz nada quando nao ha novidade.
"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nlm_usage_log import events

STATE = os.path.expanduser("~/dev/notebooklm_edson/logs/.nlm_probe_notified")

def notify(title: str, msg: str) -> None:
    try:
        subprocess.run(["terminal-notifier", "-title", title, "-message", msg,
                        "-sound", "Glass", "-group", "nlm-cota"],
                       capture_output=True, timeout=15)
    except Exception:
        try:
            subprocess.run(["osascript", "-e",
                            f'display notification "{msg}" with title "{title}" sound name "Glass"'],
                           capture_output=True, timeout=15)
        except Exception:
            pass

def main():
    prof = sys.argv[1] if len(sys.argv) > 1 else "espanhol"
    evs = sorted(events(prof), key=lambda r: r.get("epoch", 0))
    if len(evs) < 2:
        return
    last = evs[-1]
    if last["event"] != "created":
        return

    # Conta a sequencia de recusas imediatamente anterior a esta criacao.
    streak, first_refusal = 0, None
    for e in reversed(evs[:-1]):
        if e["event"] == "rate_limited":
            streak += 1
            first_refusal = e
        else:
            break
    if streak == 0:
        return  # criacao normal, sem bloqueio antes: nada a anunciar

    # Nao repetir o alerta para a mesma criacao.
    marker = str(last["epoch"])
    try:
        if open(STATE).read().strip() == marker:
            return
    except FileNotFoundError:
        pass

    gap = last["epoch"] - first_refusal["epoch"]
    h, m = divmod(gap // 60, 60)
    msg = (f"Cota repos apos {streak} recusas. Intervalo desde a 1a recusa: {h}h{m:02d}m "
           f"({first_refusal['ts'][11:16]} -> {last['ts'][11:16]}).")
    notify("NotebookLM: cota repos", msg)
    print(f"[alerta] {msg}")
    try:
        with open(STATE, "w") as fh:
            fh.write(marker)
    except Exception:
        pass

if __name__ == "__main__":
    main()
