#!/usr/bin/env python3
"""
Audio runner híbrido (CLI + manual via UI do NotebookLM).

Estado das cenas em _raw/audio_metadata.json:
- pending     → ainda não foi gerada (nenhum áudio existe)
- created     → áudio criado no NLM Studio (artifact_id conhecido); aguarda download
- downloaded  → áudio baixado para audios/, renomeado, master atualizado

Comandos:

  --status
      Mostra progresso (pending/created/downloaded).

  --list-pending N
      Lista próximas N cenas pending (em ordem de priority_rank).
      Imprime: cena_id + caminho do prompt + audio_title esperado.

  --show-prompt CENA_ID
      Imprime o prompt de uma cena específica (para copiar/colar na UI do NLM).

  --create N
      Dispara N novos áudios via CLI (nlm studio create), usando o audio_title
      como --title. Marca cenas como 'created' no metadata. Respeita limite
      diário de 20/dia do NLM CLI (silencioso — fica em standby).

  --harvest
      Vai no studio (nlm studio status), lista todos os artifacts cujo título
      bate com padrão 'aristoteles_*'. Para cada um, se não está em metadata
      ainda (gerado manualmente via UI), cria entrada 'created'. Em seguida,
      baixa os 'created' usando 'nlm download audio --id ... -o <path>' e
      marca como 'downloaded'.

  --claim ARTIFACT_ID CENA_ID
      Caso manual: você gerou um áudio na UI mas o título não bate. Esse comando
      associa o artifact à cena_id, renomeia no NLM e baixa.

Usage examples:
  python scripts/07_audio_runner.py --status
  python scripts/07_audio_runner.py --list-pending 10
  python scripts/07_audio_runner.py --show-prompt 05_etica/01_etica_nicomaco/L01-C01_cena01
  python scripts/07_audio_runner.py --harvest          # cron ou ad-hoc
  python scripts/07_audio_runner.py --create 5         # piloto manual via CLI
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = PROJECT_ROOT / "_raw" / "cenas_master.json"
NOTEBOOK_META = PROJECT_ROOT / "_raw" / "notebook_aristoteles.json"
AUDIO_META = PROJECT_ROOT / "_raw" / "audio_metadata.json"
AUDIOS_DIR = PROJECT_ROOT / "audios"
LOG_PATH = PROJECT_ROOT / "_raw" / "audio_log.jsonl"

DEFAULT_DAILY_LIMIT = 20  # NLM CLI silent limit
PROFILE = "default"  # conta pessoal edson.michalkiewicz@gmail.com (notebook em CLAUDE.md)

AUDIO_FORMAT = "deep_dive"   # prompts pedem deep-dive
LANGUAGE = "pt-BR"           # prompts exigem áudio 100% em português brasileiro
AUDIO_LENGTH = "long"
MAX_FOCUS_CHARS = 10000      # teto empírico do focus do NLM
INTERVAL_SECONDS = 120       # espaçamento entre criações (reduz rate-limit)
MAX_RETRIES = 3
# create_audio devolve isto em rate-limit (API code 8) → cena fica pending p/ amanhã
_RATE_LIMITED = object()
_POLL_MISSING = "__poll_missing__"  # artifact sumiu do studio
_POLL_ERROR = "__poll_error__"      # consulta falhou (rede/auth)
_UUID_RE = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")


# ───────────────────────────── helpers ─────────────────────────────

def load_master() -> dict:
    if not MASTER_PATH.exists():
        sys.exit("ERRO: _raw/cenas_master.json não encontrado. "
                 "Rode 04_define_cenas_master.py primeiro.")
    return json.loads(MASTER_PATH.read_text(encoding="utf-8"))


def load_notebook_meta() -> dict:
    if not NOTEBOOK_META.exists():
        sys.exit("ERRO: _raw/notebook_aristoteles.json não encontrado. "
                 "Rode 06_create_notebook_and_upload.py primeiro.")
    return json.loads(NOTEBOOK_META.read_text(encoding="utf-8"))


def load_audio_meta() -> dict:
    if not AUDIO_META.exists():
        return {"updated_at": None, "audios": {}}
    return json.loads(AUDIO_META.read_text(encoding="utf-8"))


def save_audio_meta(meta: dict) -> None:
    meta["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    AUDIO_META.parent.mkdir(parents=True, exist_ok=True)
    AUDIO_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def append_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_nlm(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    import os
    env = os.environ.copy()
    env["NLM_PROFILE"] = PROFILE
    return subprocess.run(["nlm", *args], env=env, capture_output=True, text=True, timeout=timeout)


def ensure_profile() -> None:
    # 'nlm download audio' não aceita --profile; sem switch explícito o
    # download falha silenciosamente com 'Error: Download failed for audio.'
    # mesmo com artifact completed. Garante que o profile ativo é o correto.
    try:
        run_nlm(["login", "switch", PROFILE], timeout=15)
    except Exception as exc:  # noqa: BLE001
        print(f"AVISO: nlm login switch {PROFILE} falhou: {exc}")


def _sync_to_dell(slug: str, file: Path) -> bool:
    """Chama sync_to_dell.py --project <slug> --apply --no-notify após cada download.

    --no-notify silencia o Telegram por-arquivo: o runner manda UM resumo
    consolidado por sessão. Retorna True se a transferência saiu rc=0.
    """
    sync_script = (Path(__file__).resolve().parents[5]
                   / "dell_server/podcast_system/sync/sync_to_dell.py")
    if not sync_script.exists():
        return False
    try:
        import os
        env = os.environ.copy()
        secrets = Path.home() / ".secrets"
        if secrets.exists():
            for line in secrets.read_text().splitlines():
                line = line.strip()
                if line.startswith("export ") and "=" in line:
                    k, v = line[len("export "):].split("=", 1)
                    env.setdefault(k.strip(), v.strip())
        r = subprocess.run(
            [sys.executable, str(sync_script), "--project", slug, "--apply", "--no-notify"],
            timeout=120, env=env, capture_output=True,
        )
        return r.returncode == 0
    except Exception:
        return False


def _write_lastrun(slug: str, *, reset: bool = False, **fields) -> None:
    """Grava resumo da sessão em logs/<slug>_lastrun.json (best-effort)."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
        from tg_notify import write_lastrun
        write_lastrun(slug, reset=reset, **fields)
    except Exception:
        pass


def get_state(audio_meta: dict, cena_id: str) -> str:
    rec = audio_meta["audios"].get(cena_id)
    if not rec:
        return "pending"
    return rec.get("status", "pending")


def extract_focus(prompt_text: str) -> str:
    """Remove o cabeçalho 'AUDIO TITLE — rename...' (entre as cercas ═) e
    devolve só o corpo instrucional. Esse cabeçalho serve ao fluxo manual de
    UI; no CLI casamos o áudio pelo artifact_id, então é ruído no --focus."""
    lines = prompt_text.splitlines()
    fences = [i for i, l in enumerate(lines) if l.strip().startswith("═")]
    if len(fences) >= 2:
        body = "\n".join(lines[fences[1] + 1:]).strip()
        if body:
            return body
    return prompt_text.strip()


def create_audio(notebook_id: str, focus: str, source_id: str):
    """Dispara um Audio Overview (fire-and-forget). Devolve artifact_id (str),
    _RATE_LIMITED (rate-limit code 8 → adiar) ou None (erro real)."""
    cmd = ["create", "audio", notebook_id,
           "--format", AUDIO_FORMAT, "--length", AUDIO_LENGTH,
           "--language", LANGUAGE, "--focus", focus[:MAX_FOCUS_CHARS],
           "--source-ids", source_id, "--profile", PROFILE, "--confirm"]
    try:
        r = run_nlm(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        print("   Timeout (180s) ao criar áudio")
        return None
    if r.returncode != 0:
        err = ((r.stderr or "") + " " + (r.stdout or "")).strip()
        print(f"   nlm err: {err[:300]}")
        low = err.lower()
        if "rate limited" in low or "code 8" in low or "wait a few minutes" in low:
            return _RATE_LIMITED
        return None
    m = re.search(r"(?:Artifact|Audio)\s*(?:ID)?[:\s]+([a-f0-9-]{20,})",
                  r.stdout, re.IGNORECASE)
    if m:
        return m.group(1)
    m = _UUID_RE.search(r.stdout)
    return m.group(0) if m else None


def poll_status(notebook_id: str, artifact_id: str) -> str:
    """Status do artifact no studio. _POLL_MISSING se sumiu da lista,
    _POLL_ERROR se a consulta falhou (rede/auth)."""
    try:
        r = run_nlm(["studio", "status", notebook_id, "--json"], timeout=30)
    except Exception:
        return _POLL_ERROR
    if r.returncode != 0:
        return _POLL_ERROR
    try:
        arts = json.loads(r.stdout)
    except Exception:
        return _POLL_ERROR
    if isinstance(arts, dict):
        arts = arts.get("value", arts.get("artifacts", []))
    for a in arts:
        if (a.get("artifact_id") or a.get("id")) == artifact_id:
            return a.get("status", "unknown")
    return _POLL_MISSING


# ───────────────────────────── commands ─────────────────────────────

def cmd_status(master: dict, audio_meta: dict) -> int:
    total = len(master["cenas"])
    counts = {"pending": 0, "created": 0, "downloaded": 0}
    for c in master["cenas"]:
        s = get_state(audio_meta, c["cena_id"])
        counts[s] = counts.get(s, 0) + 1
    print(f"Total cenas: {total}")
    print(f"  pending:     {counts['pending']:5d}  (sem áudio)")
    print(f"  created:     {counts['created']:5d}  (no studio, aguardando download)")
    print(f"  downloaded:  {counts['downloaded']:5d}  ({counts['downloaded']/total*100:.1f}%)")
    if counts["pending"]:
        days = (counts["pending"] + DEFAULT_DAILY_LIMIT - 1) // DEFAULT_DAILY_LIMIT
        print(f"\n@ {DEFAULT_DAILY_LIMIT}/dia CLI: ~{days} dias para gerar todas")
    _write_lastrun("aristoteles", pending=counts["pending"])  # merge p/ msg consolidada
    return 0


def cmd_list_pending(master: dict, audio_meta: dict, n: int) -> int:
    pending = [c for c in master["cenas"]
               if get_state(audio_meta, c["cena_id"]) == "pending"]
    print(f"Próximas {min(n, len(pending))} cenas pending (de {len(pending)} totais):\n")
    for c in pending[:n]:
        prompt_rel = c["prompt_path"]
        print(f"  • cena_id:     {c['cena_id']}")
        print(f"    prompt:      {prompt_rel}")
        print(f"    audio_title: {c['audio_title']}")
        print(f"    chars:       {c['chars']}")
        print()
    return 0


def cmd_show_prompt(cena_id: str) -> int:
    master = load_master()
    cena = next((c for c in master["cenas"] if c["cena_id"] == cena_id), None)
    if not cena:
        print(f"ERRO: cena_id '{cena_id}' não encontrada.")
        return 2
    prompt_path = PROJECT_ROOT / cena["prompt_path"]
    if not prompt_path.exists():
        print(f"ERRO: prompt não existe em {prompt_path}")
        return 2
    print(prompt_path.read_text(encoding="utf-8"))
    return 0


def cmd_create(master: dict, audio_meta: dict, notebook_meta: dict, n: int,
               *, dry_run: bool) -> int:
    notebook_id = notebook_meta["notebook_id"]
    # Mapa obra → source_id principal (para Parva e Magna que compartilham obra_slug,
    # cada sub-obra tem source_id próprio via match por título)
    source_by_title = {}
    for src in notebook_meta.get("sources", []):
        # title é tipo "01. Categories (Aristotle, tr. Edghill)"
        # extraímos o idx do início para mapear por obra_idx
        import re
        m = re.match(r"^(\d+)\.", src.get("title", ""))
        if m:
            source_by_title[int(m.group(1))] = src.get("source_id")

    pending = [c for c in master["cenas"]
               if get_state(audio_meta, c["cena_id"]) == "pending"]
    batch = pending[:n]
    print(f"=== Criando {len(batch)} áudios via CLI (de {len(pending)} pending) ===")

    ok = 0
    failed = 0
    deferred = 0
    for i, cena in enumerate(batch, 1):
        title = cena["audio_title"]
        source_id = source_by_title.get(cena["obra_idx"])
        prompt_path = PROJECT_ROOT / cena["prompt_path"]
        prompt_text = prompt_path.read_text(encoding="utf-8")
        focus = extract_focus(prompt_text)

        print(f"[{i}/{len(batch)}] {cena['cena_id']}")
        print(f"   title={title}")
        print(f"   source_id={source_id}  focus={len(focus)} chars")

        if not source_id:
            print(f"   FAIL: sem source_id para obra_idx={cena.get('obra_idx')}")
            failed += 1
            continue

        if dry_run:
            print("   → dry_run")
            continue

        # Cria com retry/backoff. Rate-limit (code 8) → adia (fica pending).
        backoff = [0, 180, 300]
        artifact_id = None
        rate_limited = False
        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                wait = backoff[min(attempt - 1, len(backoff) - 1)]
                print(f"   Tentativa {attempt}/{MAX_RETRIES} (aguardando {wait}s)...")
                time.sleep(wait)
            result = create_audio(notebook_id, focus, source_id)
            if result is _RATE_LIMITED:
                rate_limited = True
                continue
            rate_limited = False
            artifact_id = result
            break

        if artifact_id:
            rec = audio_meta["audios"].setdefault(cena["cena_id"], {})
            rec["artifact_id"] = artifact_id
            rec["audio_title"] = title
            rec["audio_filename"] = cena["audio_filename"]
            rec["status"] = "created"
            rec["created_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            save_audio_meta(audio_meta)
            append_log({"ts": rec["created_at"], "action": "created",
                        "cena_id": cena["cena_id"], "artifact_id": artifact_id})
            print(f"   ✓ created (artifact={artifact_id[:8]}...)")
            ok += 1
        elif rate_limited:
            print("   ⏸ ADIADO (rate-limit NotebookLM — fica pending p/ amanhã)")
            deferred += 1
        else:
            print("   FAIL (erro ao criar)")
            append_log({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "action": "create_fail", "cena_id": cena["cena_id"]})
            failed += 1

        # Espaçamento entre criações (reduz rate-limit), exceto na última.
        if i < len(batch):
            time.sleep(INTERVAL_SECONDS)

    print(f"\nResultado: ok={ok}, adiados={deferred}, failed={failed}")
    _write_lastrun("aristoteles", created=ok, create_failed=failed)
    return 0


def cmd_harvest(master: dict, audio_meta: dict, notebook_meta: dict,
                *, dry_run: bool) -> int:
    notebook_id = notebook_meta["notebook_id"]
    print(f"Listando artifacts no studio (notebook {notebook_id[:8]}...)...")
    r = run_nlm(["studio", "status", notebook_id, "--json"], timeout=60)
    if r.returncode != 0:
        print(f"ERRO: nlm studio status falhou: {r.stderr[:300]}")
        return 1
    try:
        artifacts = json.loads(r.stdout)
    except Exception as exc:  # noqa: BLE001
        print(f"ERRO parse JSON: {exc}")
        return 1

    # artifacts é uma lista com title + id + tipo (audio_overview)
    if isinstance(artifacts, dict):
        artifacts = artifacts.get("value", artifacts.get("artifacts", []))

    # Filtra apenas áudios cujo título começa com 'aristoteles_'
    audio_arts = [a for a in artifacts
                  if a.get("title", "").startswith("aristoteles_")]
    print(f"  → {len(audio_arts)} artifacts 'aristoteles_*' encontrados no studio")
    print(f"  → {len(artifacts) - len(audio_arts)} outros artifacts ignorados")

    # Mapeia title → cena (para matchar manual gerado com cena_id)
    by_title: dict[str, dict] = {}
    for c in master["cenas"]:
        by_title[c["audio_title"]] = c

    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    _write_lastrun("aristoteles", reset=True)  # harvest = 1ª fase do cron
    new_created = 0
    new_downloaded = 0
    unmatched = 0
    downloaded_names: list[str] = []
    transferred = transfer_failed = still_proc = 0

    for art in audio_arts:
        title = art.get("title", "")
        artifact_id = art.get("artifact_id") or art.get("id")
        cena = by_title.get(title)
        if not cena:
            print(f"  ⚠ '{title}' não bate com nenhuma cena (talvez renomeada com typo?)")
            unmatched += 1
            continue
        cena_id = cena["cena_id"]
        state = get_state(audio_meta, cena_id)
        rec = audio_meta["audios"].setdefault(cena_id, {})
        rec["artifact_id"] = artifact_id
        rec["audio_title"] = title
        rec["audio_filename"] = cena["audio_filename"]

        if state == "pending":
            rec["status"] = "created"
            rec["created_at"] = rec.get("created_at") or time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            new_created += 1
            print(f"  ↑ {cena_id} marcado como 'created' (artifact={artifact_id[:8]})")

        # Tenta baixar se 'created' ou ainda não baixado
        out_path = AUDIOS_DIR / cena["audio_filename"]
        if rec.get("status") in ("created",) or not out_path.exists():
            if dry_run:
                print(f"  ↓ {cena_id} dry_run download")
                continue
            print(f"  ↓ baixando {cena['audio_filename']}...")
            dr = run_nlm(["download", "audio", notebook_id,
                          "--id", artifact_id, "-o", str(out_path),
                          "--no-progress"], timeout=600)
            if dr.returncode != 0:
                print(f"     FAIL: {dr.stderr[:200]}")
                append_log({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "action": "download_fail", "cena_id": cena_id,
                            "error": dr.stderr[:300]})
                continue
            rec["status"] = "downloaded"
            rec["downloaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            rec["bytes"] = out_path.stat().st_size if out_path.exists() else 0
            new_downloaded += 1
            append_log({"ts": rec["downloaded_at"], "action": "downloaded",
                        "cena_id": cena_id, "bytes": rec["bytes"]})
            downloaded_names.append(out_path.name)
            if _sync_to_dell("aristoteles", out_path):
                transferred += 1
            else:
                transfer_failed += 1

    # ── Download de áudios criados via CLI (--create) ──────────────────
    # Esses têm título auto-gerado (não 'aristoteles_*'), então o laço por
    # título acima não os pega. Casamos pelo artifact_id guardado no metadata.
    cli_downloaded = 0
    for cena in master["cenas"]:
        cena_id = cena["cena_id"]
        rec = audio_meta["audios"].get(cena_id)
        if not rec or rec.get("status") != "created" or not rec.get("artifact_id"):
            continue
        artifact_id = rec["artifact_id"]
        out_path = AUDIOS_DIR / cena["audio_filename"]
        st = poll_status(notebook_id, artifact_id)
        if st == _POLL_ERROR:
            print(f"  ⚠ {cena_id}: consulta studio falhou (rede/auth) — tenta depois")
            continue
        if st == _POLL_MISSING:
            print(f"  ⚠ {cena_id}: artifact {artifact_id[:8]} sumiu do studio")
            rec["status"] = "lost_in_studio"
            continue
        if st != "completed":
            print(f"  … {cena_id}: ainda processando ({st})")
            still_proc += 1
            continue
        if dry_run:
            print(f"  ↓ {cena_id} dry_run download (CLI)")
            continue
        print(f"  ↓ baixando {cena['audio_filename']} (CLI)...")
        dr = run_nlm(["download", "audio", notebook_id, "--id", artifact_id,
                      "-o", str(out_path), "--no-progress"], timeout=600)
        if dr.returncode != 0 or not out_path.exists():
            print(f"     FAIL: {(dr.stderr or dr.stdout)[:200]}")
            append_log({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "action": "download_fail", "cena_id": cena_id,
                        "error": (dr.stderr or "")[:300]})
            continue
        rec["status"] = "downloaded"
        rec["downloaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        rec["bytes"] = out_path.stat().st_size
        cli_downloaded += 1
        append_log({"ts": rec["downloaded_at"], "action": "downloaded",
                    "cena_id": cena_id, "bytes": rec["bytes"]})
        downloaded_names.append(out_path.name)
        if _sync_to_dell("aristoteles", out_path):
            transferred += 1
        else:
            transfer_failed += 1

    if not dry_run:
        save_audio_meta(audio_meta)

    print(f"\n=== Harvest concluído ===")
    print(f"  novos 'created':       {new_created}")
    print(f"  baixados (título UI):  {new_downloaded}")
    print(f"  baixados (CLI):        {cli_downloaded}")
    print(f"  unmatched:             {unmatched}")
    print(f"  transferidos dell:     {transferred}")
    _write_lastrun("aristoteles", downloaded=downloaded_names,
                   still_processing=still_proc, dl_failed=0,
                   transferred=transferred, transfer_failed=transfer_failed)
    return 0


def cmd_claim(master: dict, audio_meta: dict, notebook_meta: dict,
              artifact_id: str, cena_id: str, *, dry_run: bool) -> int:
    cena = next((c for c in master["cenas"] if c["cena_id"] == cena_id), None)
    if not cena:
        print(f"ERRO: cena_id '{cena_id}' não encontrada.")
        return 2
    notebook_id = notebook_meta["notebook_id"]
    title = cena["audio_title"]
    print(f"Claim: artifact={artifact_id[:8]}... → cena={cena_id}")
    print(f"   renomear no NLM para: {title}")

    if dry_run:
        print("   dry_run")
        return 0

    # Renomeia
    r = run_nlm(["studio", "rename", artifact_id, title], timeout=30)
    if r.returncode != 0:
        print(f"   FAIL rename: {r.stderr[:300]}")
        return 1
    print("   ✓ renomeado")

    # Marca em metadata e baixa
    rec = audio_meta["audios"].setdefault(cena_id, {})
    rec["artifact_id"] = artifact_id
    rec["audio_title"] = title
    rec["audio_filename"] = cena["audio_filename"]
    rec["status"] = "created"
    rec["created_at"] = rec.get("created_at") or time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = AUDIOS_DIR / cena["audio_filename"]
    print(f"   ↓ baixando para {out_path.relative_to(PROJECT_ROOT)}...")
    dr = run_nlm(["download", "audio", notebook_id, "--id", artifact_id,
                  "-o", str(out_path), "--no-progress"], timeout=600)
    if dr.returncode != 0:
        print(f"   FAIL download: {dr.stderr[:300]}")
        save_audio_meta(audio_meta)
        return 1
    rec["status"] = "downloaded"
    rec["downloaded_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec["bytes"] = out_path.stat().st_size if out_path.exists() else 0
    save_audio_meta(audio_meta)
    print("   ✓ downloaded")
    return 0


# ───────────────────────────── main ─────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--list-pending", type=int, metavar="N")
    parser.add_argument("--show-prompt", metavar="CENA_ID")
    parser.add_argument("--create", type=int, metavar="N")
    parser.add_argument("--harvest", action="store_true")
    parser.add_argument("--claim", nargs=2, metavar=("ARTIFACT_ID", "CENA_ID"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.show_prompt:
        return cmd_show_prompt(args.show_prompt)

    master = load_master()
    audio_meta = load_audio_meta()

    if args.status:
        return cmd_status(master, audio_meta)
    if args.list_pending is not None:
        return cmd_list_pending(master, audio_meta, args.list_pending)

    # Comandos que precisam do notebook_meta
    if args.create is not None or args.harvest or args.claim:
        notebook_meta = load_notebook_meta()
        ensure_profile()
        if args.create is not None:
            return cmd_create(master, audio_meta, notebook_meta, args.create,
                              dry_run=args.dry_run)
        if args.harvest:
            return cmd_harvest(master, audio_meta, notebook_meta, dry_run=args.dry_run)
        if args.claim:
            return cmd_claim(master, audio_meta, notebook_meta,
                             args.claim[0], args.claim[1], dry_run=args.dry_run)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
