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

Environment variables required:
    TELEGRAM_BOT_TOKEN  — bot token from @BotFather
    TELEGRAM_CHAT_ID    — target chat or channel ID
"""
import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime


def send(text: str, parse_mode: str = "HTML") -> bool:
    """Send a Telegram message. Returns True on success, False otherwise."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("tg_notify: TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID ausentes", file=sys.stderr)
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

        lines = [f"✅ <b>{project}</b> — {now}"]
        lines.append(dl_line)
        lines.append(created_line)
        if pending is not None:
            lines.append(f"📊 Pendentes: {pending}")
        return "\n".join(lines)

    elif status == "auth_expired":
        return (
            f"🔐 <b>{project}</b> — AUTH EXPIRADO ({now})\n"
            f"Rode: <code>nlm login --profile {profile}</code>"
        )

    else:  # failed
        rc = args.rc or "?"
        summary = (args.summary or f"exit code {rc}").strip()
        return f"❌ <b>{project}</b> FALHOU rc={rc} — {now}\n{summary[:300]}"


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
    p_rep.set_defaults(func=_cmd_report)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
