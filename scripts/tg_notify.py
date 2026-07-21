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


# Identidade do bot — 1ª linha de toda mensagem (visível no preview da
# notificação). O bot StudioM4 é compartilhado com outros projetos; esta linha
# diz que a mensagem veio do pipeline de áudio de leitura formativa.
BOT_IDENTITY = "🎧 <b>[Leitura Formativa · StudioM4]</b>"


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
        "text": f"{BOT_IDENTITY}\n{text}",
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


# ── Estado por sessão (lastrun) ─────────────────────────────────────────
# Uma rodada do cron roda o runner em DUAS fases (processos separados):
#   fase download  → grava downloaded[]/transferred/still_processing
#   fase criação   → grava created/pending
# Cada fase faz merge no mesmo JSON; o cron lê tudo e manda UMA mensagem.

def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _lastrun_path(slug: str) -> Path:
    return _repo_root() / "logs" / f"{slug}_lastrun.json"


def write_lastrun(slug: str, *, reset: bool = False, **fields) -> None:
    """Merge campos no logs/<slug>_lastrun.json. reset=True zera antes (fase 1).

    Nunca levanta exceção — notificação é best-effort.
    """
    try:
        path = _lastrun_path(slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if not reset and path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        data["slug"] = slug
        data.update({k: v for k, v in fields.items() if v is not None})
        data["updated_at"] = datetime.now().isoformat(timespec="seconds")
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    except Exception:
        pass


def load_lastrun(slug: str) -> dict:
    path = _lastrun_path(slug)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


_MAX_NAMES = 20  # corta listas muito longas para não estourar a mensagem


def _format_state_report(project: str, path: str, profile: str, status: str,
                         state: dict, *, rc: str = "", summary: str = "",
                         run_cmd: str = "") -> str:
    """Renderiza UMA mensagem consolidada. Padrão obrigatório (notebooklm_edson-d4p0):
    título da obra + caminho do projeto + data + Criados/Pendentes/Baixados até o momento,
    em toda mensagem (inclusive falha/auth_expired)."""
    now = datetime.now().strftime("%d/%m %H:%M")
    run_cmd = (run_cmd or "").strip()
    path = (path or "").strip()

    def header(icon_title: str) -> list:
        lines = [icon_title]
        if path:
            lines.append(f"📂 <code>{path}</code>")
        return lines

    def with_rerun(lines: list) -> str:
        if run_cmd:
            lines.append(f"▶️ Rodar manual: <code>{run_cmd}</code>")
        return "\n".join(lines)

    if status == "auth_expired":
        lines = header(f"🔐 <b>{project}</b> — AUTH EXPIRADO ({now})")
        lines.append(f"Rode: <code>nlm login --profile {profile}</code>")
        return with_rerun(lines)
    if status == "failed":
        rc = rc or "?"
        summary = (summary or f"exit code {rc}").strip()
        lines = header(f"❌ <b>{project}</b> FALHOU rc={rc} — {now}")
        lines.append(summary[:300])
        return with_rerun(lines)

    # status == ok ────────────────────────────────────────────────────────
    created = int(state.get("created", 0) or 0)
    pending = state.get("pending", None)
    create_failed = int(state.get("create_failed", 0) or 0)

    downloaded = list(state.get("downloaded", []) or [])
    still = int(state.get("still_processing", 0) or 0)
    dl_failed = int(state.get("dl_failed", 0) or 0)
    downloaded_total = state.get("downloaded_total", None)
    manifest_total = state.get("manifest_total", None)

    transferred = int(state.get("transferred", 0) or 0)
    transfer_failed = int(state.get("transfer_failed", 0) or 0)

    zero_activity = (created == 0 and len(downloaded) == 0)
    head_icon = "⚠️" if zero_activity else "✅"
    head_suffix = " — rodou, 0 criados/baixados" if zero_activity else ""
    lines = header(f"{head_icon} <b>{project}</b>{head_suffix} ({now})")

    # 1. Criação (desta sessão) + Pendentes (total ainda por criar)
    crt = f"🎙 Criados: {created}"
    if create_failed:
        crt += f"  ⚠️ Falhas: {create_failed}"
    lines.append(crt)
    if pending is not None and str(pending) != "":
        lines.append(f"📊 Pendentes: {pending}")

    # 2. Download (progresso acumulado do livro/curso inteiro)
    if downloaded_total is not None and manifest_total is not None:
        dl = f"⬇️ Baixados até o momento: {downloaded_total}/{manifest_total}"
    else:
        dl = f"⬇️ Baixados: {len(downloaded)}"
    extras = []
    if still:
        extras.append(f"faltam {still} processando")
    if dl_failed:
        extras.append(f"⚠️ {dl_failed} falha(s)")
    if extras:
        dl += "  ·  " + " · ".join(extras)
    lines.append(dl)
    shown = downloaded[:_MAX_NAMES]
    for name in shown:
        lines.append(f"   • <code>{name}</code>")
    if len(downloaded) > _MAX_NAMES:
        lines.append(f"   … +{len(downloaded) - _MAX_NAMES} arquivo(s)")

    # 3. Transferência para o dell (servidor de podcast)
    tx = f"📤 Dell: {transferred} transferido(s)"
    if transfer_failed:
        tx += f"  ·  🔴 {transfer_failed} falhou"
    elif transferred and transferred >= len(downloaded):
        tx += "  ·  sincronizado"
    elif transferred == 0 and not downloaded:
        tx = "📤 Dell: nada a transferir"
    lines.append(tx)

    return with_rerun(lines) if zero_activity else "\n".join(lines)


def send_report(slug: str, project: str, profile: str = "", status: str = "ok",
                *, path: str = "", rc: str = "", summary: str = "", run_cmd: str = "") -> bool:
    """Lê logs/<slug>_lastrun.json e envia a mensagem consolidada (3 seções).

    Para runners SEM cron (manuais) que mandam o resumo eles mesmos.
    """
    state = load_lastrun(slug)
    msg = _format_state_report(project, path, profile, status, state,
                               rc=rc, summary=summary, run_cmd=run_cmd)
    return send(msg)


def _cmd_send(args):
    sys.exit(0 if send(args.text) else 1)


def _cmd_report(args):
    sys.exit(0 if send(_format_report(args)) else 1)


def _cmd_report_state(args):
    state = load_lastrun(args.slug)
    msg = _format_state_report(
        args.project, args.path, args.profile, args.status, state,
        rc=args.rc, summary=args.summary, run_cmd=args.run_cmd,
    )
    sys.exit(0 if send(msg) else 1)


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

    p_st = sub.add_parser("report-state",
                          help="Relatório consolidado (3 seções) lendo logs/<slug>_lastrun.json")
    p_st.add_argument("--slug",     required=True, help="Slug do projeto (chave do lastrun.json)")
    p_st.add_argument("--project",  required=True, help="Título completo da obra (não a TAG curta)")
    p_st.add_argument("--path",     default="",    help="Caminho do projeto relativo ao repo (notebooklm_edson-d4p0)")
    p_st.add_argument("--profile",  default="",    help="Perfil NLM usado")
    p_st.add_argument("--status",   required=True,
                      choices=["ok", "failed", "auth_expired"])
    p_st.add_argument("--rc",       default="",    help="Exit code (status=failed)")
    p_st.add_argument("--summary",  default="",    help="Resumo de erro (status=failed)")
    p_st.add_argument("--run-cmd",  default="",    dest="run_cmd",
                      help="Comando para re-rodar manualmente")
    p_st.set_defaults(func=_cmd_report_state)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
