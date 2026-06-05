#!/usr/bin/env python3
"""Telegram notification helper for audio pipeline cron jobs.

CLI usage (from bash cron scripts):
    python3 tg_notify.py send "literal message"
    python3 tg_notify.py report \\
        --project "Promessi Sposi" --profile "italiano" \\
        --status ok --dl 2 --created 3 --failed 0 --pending 120
    python3 tg_notify.py report \\
        --project "COF v2" --profile "default" --status failed \\
        --rc 1 --summary "ERRO: rate limit"
    python3 tg_notify.py report \\
        --project "Notre Dame" --profile "frances" --status auth_expired

Module usage (from Python):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from tg_notify import send
    send("mensagem")

Credentials (StudioM4_bot — mesmo bot do lifecycle purge):
    Resolve, em ordem de precedência, das env vars
        STUDIOM4_TELEGRAM_BOT_TOKEN / STUDIOM4_TELEGRAM_CHAT_ID   (nomes do ~/.secrets)
        TELEGRAM_BOT_TOKEN          / TELEGRAM_CHAT_ID            (nomes legados)
    Se nenhuma estiver no ambiente (caso típico de cron, que não dá
    `source ~/.secrets`), faz fallback lendo ~/.secrets diretamente.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

# Pares de nomes aceitos, em ordem de precedência.
_TOKEN_NAMES = ("STUDIOM4_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")
_CHAT_NAMES = ("STUDIOM4_TELEGRAM_CHAT_ID", "TELEGRAM_CHAT_ID")


def _parse_secrets_file(path: Path) -> dict:
    """Lê um arquivo estilo shell (KEY=val / export KEY=val) SEM executá-lo."""
    out: dict = {}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return out
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        out[key] = val
    return out


def _resolve_credentials() -> tuple:
    """Resolve (token, chat_id) do ambiente; se faltar, do ~/.secrets."""
    def pick(names, source):
        for n in names:
            v = (source.get(n) or "").strip()
            if v:
                return v
        return ""

    token = pick(_TOKEN_NAMES, os.environ)
    chat_id = pick(_CHAT_NAMES, os.environ)
    if not token or not chat_id:
        secrets = _parse_secrets_file(Path.home() / ".secrets")
        token = token or pick(_TOKEN_NAMES, secrets)
        chat_id = chat_id or pick(_CHAT_NAMES, secrets)
    return token, chat_id


def send(text: str, parse_mode: str = "HTML") -> bool:
    """Send a Telegram message. Returns True on success, False otherwise."""
    token, chat_id = _resolve_credentials()
    if not token or not chat_id:
        print("tg_notify: credenciais Telegram ausentes (env STUDIOM4_TELEGRAM_* "
              "ou ~/.secrets)", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"tg_notify: erro ao enviar: {e}", file=sys.stderr)
        return False


def _format_report(args) -> str:
    now = datetime.now().strftime("%d/%m %H:%M")
    project = args.project
    profile = args.profile or ""
    status = args.status
    run_cmd = (getattr(args, "run_cmd", "") or "").strip()

    def with_rerun(lines: list) -> str:
        if run_cmd:
            lines.append(f"▶️ Rodar manual: <code>{run_cmd}</code>")
        return "\n".join(lines)

    if status == "ok":
        dl = int(args.dl or 0)
        dl_proc = int(args.dl_proc or 0)
        created = int(args.created or 0)
        failed = int(args.failed or 0)
        pending = args.pending if args.pending else None

        dl_line = f"⬇️ Downloads: {dl}"
        if dl_proc > 0:
            dl_line += f"  ⏳ proc: {dl_proc}"
        elif dl == 0:
            dl_line += " (nada pendente)"

        created_line = f"🎙 Criados: {created}"
        if failed > 0:
            created_line += f"  ⚠️ Falhas: {failed}"

        # "Sucesso" mas sem nada criado nem baixado = suspeito (rate-limit,
        # nada pendente, etc). Sinaliza como aviso e sugere re-rodar manual.
        zero_activity = (created == 0 and dl == 0 and dl_proc == 0)
        head = (f"⚠️ <b>{project}</b> — rodou mas 0 criados/baixados ({now})"
                if zero_activity else f"✅ <b>{project}</b> — {now}")

        lines = [head, dl_line, created_line]
        if pending is not None:
            lines.append(f"📊 Pendentes: {pending}")
        return with_rerun(lines) if zero_activity else "\n".join(lines)

    elif status == "auth_expired":
        lines = [
            f"🔐 <b>{project}</b> — AUTH EXPIRADO ({now})",
            f"Rode: <code>nlm login --profile {profile}</code>",
        ]
        return with_rerun(lines)

    else:  # failed
        rc = args.rc or "?"
        summary = (args.summary or f"exit code {rc}").strip()
        lines = [f"❌ <b>{project}</b> FALHOU rc={rc} — {now}", summary[:300]]
        return with_rerun(lines)


def _cmd_send(args):
    sys.exit(0 if send(args.text) else 1)


def _cmd_report(args):
    sys.exit(0 if send(_format_report(args)) else 1)


def main():
    ap = argparse.ArgumentParser(description="Telegram notification helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send", help="Envia mensagem literal")
    p_send.add_argument("text", help="Texto a enviar (HTML suportado)")
    p_send.set_defaults(func=_cmd_send)

    p_rep = sub.add_parser("report", help="Envia relatório de cron estruturado")
    p_rep.add_argument("--project",  required=True, help="Nome do projeto")
    p_rep.add_argument("--profile",  default="",    help="Perfil NLM usado")
    p_rep.add_argument("--status",   required=True,
                       choices=["ok", "failed", "auth_expired"])
    p_rep.add_argument("--dl",       default="0",   help="Áudios baixados nesta fase")
    p_rep.add_argument("--dl-proc",  default="0",   dest="dl_proc",
                       help="Ainda processando no NLM studio")
    p_rep.add_argument("--created",  default="0",   help="Áudios criados nesta fase")
    p_rep.add_argument("--failed",   default="0",   help="Falhas na criação")
    p_rep.add_argument("--pending",  default="",    help="Total pendente no projeto")
    p_rep.add_argument("--rc",       default="",    help="Exit code (status=failed)")
    p_rep.add_argument("--summary",  default="",    help="Resumo de erro (status=failed)")
    p_rep.add_argument("--run-cmd",  default="",    dest="run_cmd",
                       help="Comando para re-rodar manualmente (incluído em "
                            "falha/auth/0-criados como lembrete)")
    p_rep.set_defaults(func=_cmd_report)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
