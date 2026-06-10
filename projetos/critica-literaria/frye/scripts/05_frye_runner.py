#!/usr/bin/env python3
"""05_frye_runner.py — geração dual-conta dos áudios do Frye.

Modelo (decisão do usuário):
  - Notebook IDÊNTICO em duas contas. O PESSOAL (default) PERMANECE (referência/Q&A).
    O PROFISSIONAL (profissional) é o MOTOR descartável: gera os áudios usando a cota
    ociosa e é APAGADO ao fim do livro. Áudios salvos em /edson.

Subcomandos:
  setup     — cria os 2 notebooks + sobe a fonte em cada; grava IDs no state. (dry-run; --confirm)
  generate  — no notebook PROFISSIONAL: create_audio(--focus prompt) → poll → download. (--only/--max; --confirm)
  teardown  — apaga o notebook PROFISSIONAL (mantém o pessoal). (--confirm)
  status    — mostra o estado.

NÃO altera o overflow_runner do michalk; reusa o nlm_audio.py (cópia local).
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nlm_audio as nlm  # cópia local dos wrappers
import naming           # nomes ordenados (sequência de audição)

STATE_FILE = "_frye_run_state.json"
PROFILE_PESSOAL = "default"
PROFILE_PROFISSIONAL = "profissional"


# ── helpers ────────────────────────────────────────────────────────────
def load_cfg(proj: Path) -> dict:
    return tomllib.load(open(proj / "config.toml", "rb"))


def load_state(proj: Path) -> dict:
    p = proj / STATE_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def save_state(proj: Path, state: dict) -> None:
    (proj / STATE_FILE).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def build_audio_list(proj: Path, cfg: dict) -> list[dict]:
    """Monta a lista de áudios (unidade×formato) a partir do manifesto + prompts/."""
    man = json.loads((proj / cfg["paths"]["unidades"]).read_text(encoding="utf-8"))
    width = man["width"]
    prompts = proj / cfg["paths"]["prompts"]
    audios_dir = cfg["paths"]["audios"]
    out = []
    # camada-livro
    for fmt in man["camada_livro"]:
        st = naming.stem(None, fmt, [], width)
        out.append({"id": st, "cap": "L0", "seq": 0, "formato": fmt,
                    "prompt_path": str(prompts / f"prompt_{st}.md"),
                    "output_path": str(proj / audios_dir / f"{st}.m4a"),
                    "status": "pending", "artifact_id": ""})
    # por capítulo
    for c in man["capitulos"]:
        for fmt in c["formatos"]:
            st = naming.stem(c["cap"], fmt, c["formatos"], width)
            out.append({"id": st, "cap": c["cap"], "seq": c["seq"], "formato": fmt,
                        "prompt_path": str(prompts / f"prompt_{st}.md"),
                        "output_path": str(proj / audios_dir / f"{st}.m4a"),
                        "status": "pending", "artifact_id": ""})
    return out


def ensure_state(proj: Path, cfg: dict) -> dict:
    state = load_state(proj)
    if not state:
        state = {
            "obra": cfg["obra"]["titulo"], "slug": cfg["obra"]["slug"],
            "notebook_pessoal": "", "notebook_profissional": "",
            "audios": build_audio_list(proj, cfg),
        }
        save_state(proj, state)
    return state


def nb_title(cfg: dict, tag: str) -> str:
    return f"{tag} {cfg['obra']['titulo']}"


# ── setup ──────────────────────────────────────────────────────────────
def cmd_setup(proj: Path, cfg: dict, confirm: bool) -> int:
    state = ensure_state(proj, cfg)
    fonte = proj / "output" / f"{cfg['obra']['slug']}_fonte_nlm.md"
    if not fonte.exists():
        print(f"ERRO: fonte não existe: {fonte}"); return 1

    print("\n  SETUP (dual-conta):")
    print(f"    Pessoal      ({PROFILE_PESSOAL}): criar notebook PERMANENTE + subir fonte")
    print(f"    Profissional ({PROFILE_PROFISSIONAL}): criar notebook DESCARTÁVEL + subir fonte")
    print(f"    Fonte: {fonte.name} ({fonte.stat().st_size/1e6:.2f} MB)")
    if state.get("notebook_pessoal") or state.get("notebook_profissional"):
        print(f"    JÁ EXISTEM no state: pessoal={state['notebook_pessoal']} prof={state['notebook_profissional']}")
    if not confirm:
        print("\n  [dry-run] nada criado. Use --confirm para criar de verdade.\n"); return 0

    nlm.check_auth(PROFILE_PESSOAL)
    nlm.check_auth(PROFILE_PROFISSIONAL)

    if not state.get("notebook_pessoal"):
        nb = nlm.create_notebook(nb_title(cfg, "[FRYE]"), PROFILE_PESSOAL)
        print(f"    ✓ notebook pessoal: {nb}")
        nlm.add_source(nb, fonte, cfg["obra"]["titulo"], PROFILE_PESSOAL)
        print("    ✓ fonte subida (pessoal)")
        state["notebook_pessoal"] = nb
        save_state(proj, state)
    if not state.get("notebook_profissional"):
        nb = nlm.create_notebook(nb_title(cfg, "[FRYE-TEMP]"), PROFILE_PROFISSIONAL)
        print(f"    ✓ notebook profissional (temp): {nb}")
        nlm.add_source(nb, fonte, cfg["obra"]["titulo"], PROFILE_PROFISSIONAL)
        print("    ✓ fonte subida (profissional)")
        state["notebook_profissional"] = nb
        save_state(proj, state)
    print("\n  Setup concluído.\n")
    return 0


# ── generate ───────────────────────────────────────────────────────────
def _poll_until_ready(nb: str, art_id: str, poll_interval: int, poll_timeout: int) -> str:
    deadline = time.monotonic() + poll_timeout
    while time.monotonic() < deadline:
        arts = nlm.list_artifacts(nb, PROFILE_PROFISSIONAL)
        a = arts.get(art_id)
        st = nlm.STATUS_MAP.get((a or {}).get("status", ""), "generating") if a else "generating"
        if st == "completed":
            return "completed"
        if st == "failed":
            return "failed"
        time.sleep(poll_interval)
    return "timeout"


def cmd_generate(proj: Path, cfg: dict, *, only: str, max_n: int, confirm: bool,
                 interval: int, poll_interval: int, poll_timeout: int) -> int:
    state = ensure_state(proj, cfg)
    nb = state.get("notebook_profissional")

    pend = [a for a in state["audios"] if a["status"] != "downloaded"]
    if only:
        wanted = set(only.split(","))
        pend = [a for a in pend if a["id"] in wanted or a["formato"] in wanted or str(a["cap"]) in wanted]
    if max_n > 0:
        pend = pend[:max_n]

    print(f"\n  GENERATE no notebook profissional {nb}")
    print(f"    {len(pend)} áudio(s) nesta rodada:")
    for a in pend:
        print(f"      - {a['id']}  ({a['formato']})")
    if not confirm:
        print("\n  [dry-run] nada gerado. Use --confirm.\n"); return 0
    if not nb:
        print("ERRO: rode `setup --confirm` primeiro (sem notebook profissional)."); return 1

    af = cfg.get("notebooklm", {})
    fmt = af.get("format", "deep_dive"); length = af.get("length", "long")
    lang = cfg["obra"].get("idioma_saida", "pt-BR")

    # ── Fase 1: CRIAR todos (geram em paralelo no servidor) ──────────────
    created = [a for a in pend if a["status"] == "created" and a.get("artifact_id")]
    to_create = [a for a in pend if a not in created]
    quota_hit = False
    for i, a in enumerate(to_create, 1):
        focus = Path(a["prompt_path"]).read_text(encoding="utf-8")
        print(f"  [criar {i}/{len(to_create)}] {a['id']}…", flush=True)
        try:
            art = nlm.create_audio(nb, focus, PROFILE_PROFISSIONAL, fmt=fmt, length=length, language=lang)
        except nlm.QuotaExhausted:
            print("  ⛔ cota esgotada (code 8) — paro de criar; baixo o que já foi criado.", flush=True)
            quota_hit = True; break
        a["artifact_id"] = art or ""
        a["status"] = "created"
        save_state(proj, state)
        created.append(a)
        print(f"      artifact={art}", flush=True)
        if i < len(to_create):
            time.sleep(interval)

    # ── Fase 2: BAIXAR todos os criados (poll + download c/ retry) ───────
    done = 0
    for j, a in enumerate(created, 1):
        art = a["artifact_id"]
        print(f"\n  [baixar {j}/{len(created)}] {a['id']} — aguardando processar…", flush=True)
        st = _poll_until_ready(nb, art, poll_interval, poll_timeout)
        if st != "completed":
            print(f"      ⚠ poll: {st} — fica created p/ retomar."); continue
        ok = False
        for attempt, backoff in enumerate([0, 90, 240], 1):
            if backoff:
                time.sleep(backoff)
            try:
                sz = nlm.download_audio(nb, art, a["output_path"], PROFILE_PROFISSIONAL)
                a["status"] = "downloaded"; save_state(proj, state)
                print(f"      ✓ baixado ({sz/1e6:.1f} MB) → {Path(a['output_path']).name}", flush=True)
                ok = True; done += 1; break
            except nlm.NlmError as e:
                print(f"      tentativa {attempt} download falhou: {str(e)[:80]}")
        if not ok:
            print("      ⚠ download não concluído; fica created p/ retomar.")

    if done:
        _sync_to_dell(cfg)
    print(f"\n  Rodada: criados {len(created)} | baixados {done}"
          + ("  (parou por cota)" if quota_hit else ""), flush=True)
    return 0


def _sync_to_dell(cfg: dict) -> None:
    """Empurra os áudios baixados p/ o dell (feed de podcast). Best-effort, --no-notify."""
    lc = cfg.get("lifecycle", {})
    if not lc.get("dell_sync"):
        return
    slug = lc.get("dell_slug") or cfg["obra"]["slug"]
    script = Path.home() / "dev/dell_server/podcast_system/sync/sync_to_dell.py"
    if not script.exists():
        return
    try:
        subprocess.run([sys.executable, str(script), "--project", slug, "--apply", "--no-notify"],
                       timeout=900, capture_output=True)
        print(f"  dell sync: {slug}", flush=True)
    except Exception:
        pass


# ── teardown ───────────────────────────────────────────────────────────
def cmd_teardown(proj: Path, cfg: dict, confirm: bool) -> int:
    state = ensure_state(proj, cfg)
    nb = state.get("notebook_profissional")
    if not nb:
        print("  Nenhum notebook profissional no state — nada a apagar."); return 0
    pend = [a for a in state["audios"] if a["status"] != "downloaded"]
    print(f"\n  TEARDOWN: apagar notebook PROFISSIONAL {nb} (mantém o pessoal {state.get('notebook_pessoal')}).")
    if pend:
        print(f"    ⚠ ATENÇÃO: ainda há {len(pend)} áudio(s) NÃO baixados. Apagar agora os perde.")
    if not confirm:
        print("\n  [dry-run] nada apagado. Use --confirm.\n"); return 0
    nlm.delete_notebook(nb, PROFILE_PROFISSIONAL)
    state["notebook_profissional"] = ""
    save_state(proj, state)
    print("    ✓ notebook profissional apagado. Pessoal mantido.\n")
    return 0


def cmd_status(proj: Path, cfg: dict) -> int:
    state = ensure_state(proj, cfg)
    from collections import Counter
    c = Counter(a["status"] for a in state["audios"])
    print(f"\n  {state['obra']}")
    print(f"  notebook pessoal:      {state.get('notebook_pessoal') or '—'}")
    print(f"  notebook profissional: {state.get('notebook_profissional') or '—'}")
    print(f"  áudios: {dict(c)} (total {len(state['audios'])})\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=["setup", "generate", "teardown", "status"])
    ap.add_argument("projeto")
    ap.add_argument("--confirm", action="store_true")
    ap.add_argument("--only", default="", help="ids/formatos/caps separados por vírgula")
    ap.add_argument("--max", type=int, default=0, dest="max_n")
    ap.add_argument("--interval", type=int, default=120)
    ap.add_argument("--poll-interval", type=int, default=60, dest="poll_interval")
    ap.add_argument("--poll-timeout", type=int, default=2400, dest="poll_timeout")
    args = ap.parse_args()

    proj = Path(args.projeto).expanduser().resolve()
    cfg = load_cfg(proj)
    if args.cmd == "setup":
        return cmd_setup(proj, cfg, args.confirm)
    if args.cmd == "generate":
        return cmd_generate(proj, cfg, only=args.only, max_n=args.max_n, confirm=args.confirm,
                            interval=args.interval, poll_interval=args.poll_interval,
                            poll_timeout=args.poll_timeout)
    if args.cmd == "teardown":
        return cmd_teardown(proj, cfg, args.confirm)
    return cmd_status(proj, cfg)


if __name__ == "__main__":
    sys.exit(main())
