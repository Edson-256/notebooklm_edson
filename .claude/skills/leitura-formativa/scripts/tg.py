#!/usr/bin/env python3
"""
Telegram (StudioM4_bot) para a skill leitura-formativa. Sem dependencias externas (urllib).

Credenciais: STUDIOM4_TELEGRAM_BOT_TOKEN / STUDIOM4_TELEGRAM_CHAT_ID, do ambiente ou de ~/.secrets
(linhas 'export KEY=VAL'). Falha em silencio (retorna False) se nao houver credencial — nunca
derruba o runner.

Formato do relatorio (pedido pelo usuario):
    <projeto> YYYY-MM-DD - HH:MM
     arquivos criados:
     - 01_cap-01_cena-01_Fulano.m4a
     - 02_cap-01_cena-02_Cicrano.m4a
     arquivos baixados: 02
"""
from __future__ import annotations
import os, json, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

_TOKEN_KEYS = ("STUDIOM4_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
_CHAT_KEYS = ("STUDIOM4_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")


def _from_secrets() -> dict:
    p = Path.home() / ".secrets"
    out = {}
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.startswith("export ") and "=" in line:
                k, v = line[len("export "):].split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _creds():
    sec = None
    def pick(keys):
        nonlocal sec
        for k in keys:
            if os.environ.get(k):
                return os.environ[k]
        if sec is None:
            sec = _from_secrets()
        for k in keys:
            if sec.get(k):
                return sec[k]
        return None
    return pick(_TOKEN_KEYS), pick(_CHAT_KEYS)


def send(text: str) -> bool:
    token, chat = _creds()
    if not token or not chat:
        return False
    try:
        data = urllib.parse.urlencode({"chat_id": chat, "text": text,
                                       "disable_web_page_preview": "true"}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status == 200
    except Exception:
        return False


def report(project_label: str, *, created=None, downloaded=None,
           deferred: int = 0, failed: int = 0, now: str | None = None) -> bool:
    """created/downloaded: listas de nomes de arquivo (ou None se a fase nao se aplica)."""
    stamp = now or datetime.now().strftime("%Y-%m-%d - %H:%M")
    lines = [f"{project_label} {stamp}"]
    if created is not None:
        lines.append(f" arquivos criados: {len(created)}")
        lines += [f"  - {n}" for n in created]
        if deferred:
            lines.append(f" adiados (rate-limit): {deferred}")
        if failed:
            lines.append(f" falhas: {failed}")
    if downloaded is not None:
        if isinstance(downloaded, int):
            lines.append(f" arquivos baixados: {downloaded:02d}")
        else:
            lines.append(f" arquivos baixados: {len(downloaded):02d}")
            lines += [f"  - {n}" for n in downloaded]
    return send("\n".join(lines))


if __name__ == "__main__":
    import sys
    ok = send(" ".join(sys.argv[1:]) or "teste StudioM4_bot (leitura-formativa)")
    print("enviado" if ok else "FALHOU (sem credencial ou erro de rede)")
    sys.exit(0 if ok else 1)
