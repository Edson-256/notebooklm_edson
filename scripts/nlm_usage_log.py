#!/usr/bin/env python3
"""
nlm_usage_log — registro estruturado de consumo de cota do Gemini Notebook (ex-NotebookLM).

POR QUE ISTO EXISTE
-------------------
Em 2026-09-02 o Google trocou o modelo de cota: a reposição passou a ser a cada
~5h até um teto SEMANAL, e o limite virou baseado em compute (pesa complexidade do
prompt, modelo e recurso), não contagem de artefatos. Nenhum desses números é
publicado, e a interface desta conta NÃO expõe painel de uso (verificado na UI em
2026-09-08). Logo, a única forma de conhecer os tetos é medir o que a API responde.

O log dos wrappers não serve para isso: ele mistura num mesmo "falhou" três coisas
distintas — teto de janela, teto semanal e falha transitória de rede (que de fato
ocorreu entre 05 e 07/09, com 100% de timeout nos downloads). Este módulo separa
os casos em JSONL, uma linha por evento, para que a análise seja aritmética e não
interpretação de texto de log.

USO
---
    import sys; sys.path.insert(0, "/Users/edsonmichalkiewicz/dev/notebooklm_edson/scripts")
    from nlm_usage_log import record
    record("espanhol", "don-quijote", "created", artifact="74a7fb8b", seq=184)
    record("espanhol", "don-quijote", "rate_limited", detail="RESOURCE_EXHAUSTED")

Eventos: created | rate_limited | failed | probe_blocked | probe_skipped
"""
import json, os, datetime, fcntl

LOG_PATH = os.path.expanduser("~/dev/notebooklm_edson/logs/nlm_usage.jsonl")

# Semana ISO: o teto semanal do Google reseta em dia desconhecido. Gravamos a chave
# ISO (ano-semana) só como agrupador de análise; se a medição mostrar que o reset
# cai noutro dia, reagrupa-se pelos timestamps, que ficam preservados em cada linha.
def _now():
    return datetime.datetime.now().astimezone()

def record(profile: str, project: str, event: str, detail: str = "", **extra) -> None:
    """Grava um evento. Nunca levanta exceção: telemetria não pode derrubar produção."""
    try:
        now = _now()
        iso_year, iso_week, _ = now.isocalendar()
        row = {
            "ts": now.isoformat(timespec="seconds"),
            "epoch": int(now.timestamp()),
            "profile": profile,
            "project": project,
            "event": event,
            "iso_week": f"{iso_year}-W{iso_week:02d}",
        }
        if detail:
            row["detail"] = detail[:300]
        row.update(extra)
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        # append + flock: os runners podem rodar concorrentes (ver notebooklm_edson-aa1h)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fcntl.flock(fh, fcntl.LOCK_UN)
    except Exception:
        pass

def events(profile: str = "", since_epoch: int = 0) -> list:
    """Lê o log. Usado pela sonda para decidir e pelo relatório para agregar."""
    out = []
    try:
        with open(LOG_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if profile and r.get("profile") != profile:
                    continue
                if r.get("epoch", 0) < since_epoch:
                    continue
                out.append(r)
    except FileNotFoundError:
        pass
    return out
