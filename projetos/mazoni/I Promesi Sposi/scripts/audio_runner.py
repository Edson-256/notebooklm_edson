#!/usr/bin/env python3
"""
Promessi Sposi (italiano) — Audio Runner (fire-and-forget).

Modelado em projetos/cof_v2/scripts/06_audio_runner.py mas simplificado:
- Multi-source: cada cena usa a source do capítulo dela (auto-mapeado por título).
- Manifest construído do filesystem (cenas/ + prompts/ pareados).
- Limite free de 3 áudios/dia → --max 3 default.
- --bootstrap lê studio NLM e popula metadata para áudios criados manualmente.

Uso:
    python audio_runner.py --bootstrap          # uma vez, após auth, p/ refletir runs manuais
    python audio_runner.py --dry-run            # ver plano
    python audio_runner.py --max 3              # disparar próximo lote (cron usa isso)
    python audio_runner.py --download           # baixar status=created → downloaded
"""
from __future__ import annotations

import argparse
import json
import re
import signal
import subprocess
import sys
import unicodedata
import time
from datetime import datetime
from pathlib import Path

# ── Configuração do projeto ────────────────────────────────────────────
PROJECT_DIR = Path(__file__).resolve().parent.parent     # I Promesi Sposi/
REPO_DIR = PROJECT_DIR.parents[2]                        # notebooklm_edson/
LOGS_DIR = REPO_DIR / "logs"

NOTEBOOK_ID = "aacfd630-2c19-43ee-9135-c06b042a6351"
PROFILE = "italiano"
LANGUAGE = "it-IT"
AUDIO_FORMAT = "deep_dive"

OBRA_TITLE = "I Promessi Sposi"
OBRA_SLUG = "promessi"
FILENAME_PREFIX = "promessi"

CENAS_DIR = PROJECT_DIR / "cenas"
PROMPTS_DIR = PROJECT_DIR / "prompts"
AUDIOS_DIR = PROJECT_DIR / "audios"
METADATA_FILE = AUDIOS_DIR / "metadata.json"

INTERVAL_SECONDS = 120
MAX_FOCUS_CHARS = 10000
MAX_RETRIES = 3
DEFAULT_MAX_DAILY = 3

# ── Estado ─────────────────────────────────────────────────────────────
shutdown_requested = False
session_stats = {"started_at": None, "items_attempted": 0, "items_created": 0, "items_failed": 0}
session_results: list[dict] = []


def handle_shutdown(signum, frame):
    global shutdown_requested
    if shutdown_requested:
        print("\nForçando saída.")
        sys.exit(1)
    shutdown_requested = True
    print("\nCtrl+C: finalizando após item atual. (Ctrl+C de novo p/ forçar)")


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ── Manifest (cenas + prompts → items com seq_global) ──────────────────

SCENE_RE = re.compile(r"_cena(\d+)\.md$")
PROMPT_RE = re.compile(r"_prompt(\d+)\.md$")
SCENE_ID_RE = re.compile(r"Scene Identifier:\s*\**\s*([\w\.\- ]+?cena\d+)", re.IGNORECASE)


def book_id_of_cena(cena_filename: str) -> str:
    """Extrai a identidade do capítulo (prefixo) p/ casar com a source.

    Promessi:  C_00-Promesi.Sposi_cena001.md → 'C_00-Promesi.Sposi'
    Notre Dame: L01-C01-LA_GRANDSALLE_cena001.md → 'L01-C01-LA_GRANDSALLE'
    """
    return re.split(r"_cena\d+\.md$", cena_filename)[0]


def build_manifest() -> list[dict]:
    """Lê cenas/ e prompts/, pareia, ordena, atribui seq_global 1..N."""
    cenas = sorted(CENAS_DIR.glob("*.md"))
    prompts = sorted(PROMPTS_DIR.glob("*.md"))
    if not cenas:
        log(f"ERRO: {CENAS_DIR} vazia"); sys.exit(1)
    if len(cenas) != len(prompts):
        log(f"ERRO: {len(cenas)} cenas vs {len(prompts)} prompts (devem ser iguais)")
        sys.exit(1)

    items = []
    for seq, (cena, prompt) in enumerate(zip(cenas, prompts), start=1):
        items.append({
            "seq_global": seq,
            "scene_identifier": cena.stem,
            "cena_filename": cena.name,
            "prompt_filename": prompt.name,
            "prompt_path": prompt,
            "book_id": book_id_of_cena(cena.name),
        })
    return items


def load_prompt(item: dict) -> str:
    content = item["prompt_path"].read_text(encoding="utf-8").strip()
    if len(content) > MAX_FOCUS_CHARS:
        content = content[: MAX_FOCUS_CHARS - 3] + "..."
    return content


def slugify(text: str) -> str:
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "_", norm).strip("_").lower()[:40] or "item"


def filename_for(item: dict) -> str:
    return f"{FILENAME_PREFIX}_{item['seq_global']:03d}_{slugify(item['scene_identifier'])}.mp3"


# ── Metadata ───────────────────────────────────────────────────────────

def load_metadata() -> dict:
    if not METADATA_FILE.exists():
        return {"obra": OBRA_TITLE, "obra_slug": OBRA_SLUG,
                "notebook_id": NOTEBOOK_ID, "profile": PROFILE, "audios": []}
    return json.loads(METADATA_FILE.read_text(encoding="utf-8"))


def save_metadata(md: dict) -> None:
    AUDIOS_DIR.mkdir(exist_ok=True)
    md["obra"] = OBRA_TITLE
    md["obra_slug"] = OBRA_SLUG
    md["notebook_id"] = NOTEBOOK_ID
    md["profile"] = PROFILE
    md["total_itens_processados"] = len(md.get("audios", []))
    md["ultima_atualizacao"] = datetime.now().isoformat()
    md["audios"] = sorted(md["audios"], key=lambda a: a["seq_global"])
    METADATA_FILE.write_text(json.dumps(md, indent=2, ensure_ascii=False), encoding="utf-8")


def upsert_entry(entry: dict) -> None:
    md = load_metadata()
    by_seq = {a["seq_global"]: a for a in md.get("audios", [])}
    if entry["seq_global"] in by_seq and by_seq[entry["seq_global"]].get("status") not in (None, "lost_in_studio"):
        log(f"   AVISO: sobrescrevendo entrada existente para seq={entry['seq_global']} (status anterior: {by_seq[entry['seq_global']].get('status')})")
    by_seq[entry["seq_global"]] = entry
    md["audios"] = list(by_seq.values())
    save_metadata(md)


def get_processed_seqs() -> set[int]:
    """Inclui created/downloaded (em progresso) e skipped_legacy (deliberadamente pulado)."""
    return {a["seq_global"] for a in load_metadata().get("audios", [])
            if a.get("status") in ("created", "downloaded", "skipped_legacy")}


# ── nlm wrappers ───────────────────────────────────────────────────────

def run_nlm(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout)


def check_auth() -> bool:
    try:
        run_nlm(["login", "switch", PROFILE], timeout=15)
        r = run_nlm(["login", "--check", "--profile", PROFILE], timeout=30)
        return r.returncode == 0
    except Exception as e:
        log(f"Erro auth: {e}"); return False


def build_source_map() -> dict[str, str] | None:
    """Mapeia book_id (título sem .md) → source_id. Multi-source: cada cena usa
    a fonte do seu capítulo."""
    r = run_nlm(["source", "list", NOTEBOOK_ID, "--json", "--profile", PROFILE], timeout=30)
    if r.returncode != 0:
        log(f"   nlm source list falhou: {r.stderr.strip()[:200]}"); return None
    try:
        sources = json.loads(r.stdout)
    except json.JSONDecodeError:
        return None
    if not sources:
        log("ERRO: notebook não tem fontes"); return None
    smap: dict[str, str] = {}
    for s in sources:
        title = (s.get("title") or "").rstrip()
        # Strip extensão .md (case-insensitive)
        key = re.sub(r"\.md$", "", title, flags=re.IGNORECASE)
        if key:
            smap[key] = s["id"]
    return smap


def resolve_source_for_item(item: dict, smap: dict[str, str]) -> str | None:
    """Acha a source pelo book_id da cena. Aceita match exato; senão tenta
    normalizar variações pontuais (Promesi.Sposi vs Promesi Sposi)."""
    bid = item["book_id"]
    if bid in smap:
        return smap[bid]
    # Tentar variações: trocar '.' por ' ' e vice-versa
    candidates = {bid.replace(".", " "), bid.replace(" ", ".")}
    for c in candidates:
        if c in smap:
            return smap[c]
    return None


_UUID_RE = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")


def create_audio(focus: str, source_id: str) -> str | None:
    cmd = ["create", "audio", NOTEBOOK_ID,
           "--format", AUDIO_FORMAT, "--language", LANGUAGE, "--length", "long",
           "--focus", focus, "--source-ids", source_id,
           "--profile", PROFILE, "--confirm"]
    try:
        r = run_nlm(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        log("   Timeout (180s)"); return None
    if r.returncode != 0:
        log(f"   nlm err: {(r.stderr or r.stdout).strip()[:300]}")
        return None
    m = re.search(r"(?:Artifact|Audio)\s*(?:ID)?[:\s]+([a-f0-9-]{20,})", r.stdout, re.IGNORECASE)
    if m: return m.group(1)
    m = _UUID_RE.search(r.stdout)
    return m.group(0) if m else None


def poll_status(artifact_id: str) -> str | None:
    try:
        r = run_nlm(["studio", "status", NOTEBOOK_ID, "--json", "--profile", PROFILE], timeout=30)
        if r.returncode != 0: return None
        for a in json.loads(r.stdout):
            if a.get("id") == artifact_id:
                return a.get("status")
    except Exception:
        return None
    return None


def download_artifact(artifact_id: str, out: Path) -> bool:
    for attempt, wait in enumerate([0, 90, 240], 1):
        if wait:
            log(f"   Aguardando {wait}s antes de tentativa {attempt}/3...")
            time.sleep(wait)
        try:
            r = run_nlm(["download", "audio", NOTEBOOK_ID, "--id", artifact_id,
                         "--output", str(out), "--no-progress"], timeout=300)
        except Exception as e:
            log(f"   Erro download {attempt}: {e}"); continue
        if r.returncode == 0 and out.exists():
            log(f"   Download OK: {out.stat().st_size/1024/1024:.1f} MB")
            return True
        log(f"   Download falhou {attempt}: {(r.stderr or r.stdout)[:200]}")
    return False


# ── Bootstrap (importa áudios já criados manualmente do studio) ────────

def bootstrap_from_studio(items: list[dict]) -> int:
    """Lê studio, casa artifact↔seq via Scene Identifier no custom_instructions."""
    if not check_auth():
        log("ERRO: auth inválida"); return 1
    r = run_nlm(["studio", "status", NOTEBOOK_ID, "--json", "--profile", PROFILE], timeout=60)
    if r.returncode != 0:
        log(f"studio status falhou: {r.stderr[:200]}"); return 1
    studio = json.loads(r.stdout)
    audios = [a for a in studio if a.get("type") == "audio"]
    log(f"Studio: {len(audios)} áudios encontrados")

    by_identifier = {it["scene_identifier"]: it for it in items}
    md = load_metadata()
    existing_artifact_ids = {a.get("artifact_id") for a in md.get("audios", [])}
    matched = unmatched = already = 0

    for art in audios:
        if art["id"] in existing_artifact_ids:
            already += 1; continue
        ci = art.get("custom_instructions", "") or ""
        m = SCENE_ID_RE.search(ci)
        if not m:
            log(f"   sem Scene Identifier no custom_instructions: artifact {art['id'][:12]}...")
            unmatched += 1; continue
        ident = m.group(1).strip()
        item = by_identifier.get(ident)
        if not item:
            log(f"   identifier '{ident}' não bate com nenhuma cena local")
            unmatched += 1; continue
        # OK, match
        status_studio = art.get("status")
        entry = {
            "seq_global": item["seq_global"],
            "scene_identifier": ident,
            "cena_filename": item["cena_filename"],
            "prompt_filename": item["prompt_filename"],
            "artifact_id": art["id"],
            "data_geracao": datetime.now().isoformat(),
            "source": "bootstrap",
            "status": "created" if status_studio == "completed" else f"studio_{status_studio}",
            "arquivo": filename_for(item),
        }
        md.setdefault("audios", []).append(entry)
        matched += 1
        log(f"   OK seq={item['seq_global']:3d} ← artifact {art['id'][:12]} (studio: {status_studio})")

    save_metadata(md)
    log(f"\nBootstrap concluído: matched={matched} já_em_metadata={already} sem_match={unmatched}")
    return 0


# ── Run principal (fire-and-forget) ────────────────────────────────────

def run_create(args, items: list[dict]) -> int:
    smap: dict[str, str] | None = None
    if not args.skip_auth_check:
        if not check_auth():
            log("ERRO: nlm nao autenticado. Execute: nlm login --profile " + PROFILE)
            return 1
        log("Auth OK")
        smap = build_source_map()
        if not smap:
            log("ERRO: source map não pôde ser construído"); return 1
        log(f"Sources: {len(smap)} fontes mapeadas")
        # Sanity: toda cena tem source?
        missing_books = sorted({it["book_id"] for it in items if it["book_id"] not in smap
                                and not (it["book_id"].replace(".", " ") in smap
                                         or it["book_id"].replace(" ", ".") in smap)})
        if missing_books:
            log(f"ERRO: {len(missing_books)} book_id sem source no notebook:")
            for b in missing_books[:5]:
                log(f"  - {b!r}")
            return 1

    processed = get_processed_seqs()
    pending = [it for it in items if it["seq_global"] not in processed]
    print()
    log(f"Total: {len(items)} | Processados: {len(processed)} | Pendentes: {len(pending)}")
    if not pending:
        log("Tudo processado."); return 0

    queue = pending[: args.max_items] if args.max_items > 0 else pending
    log(f"Fila: {len(queue)} itens (limite diário free = {DEFAULT_MAX_DAILY})")
    print()

    if args.dry_run:
        for i, it in enumerate(queue, 1):
            sid = (smap and resolve_source_for_item(it, smap)) or "(skip-auth)"
            print(f"  {i:3d}. seq={it['seq_global']:3d}  {it['scene_identifier']}")
            print(f"       prompt={it['prompt_filename']}  source={sid[:8] if sid != '(skip-auth)' else sid}...")
        return 0

    if smap is None:
        log("ERRO: --skip-auth-check requer --dry-run"); return 1

    session_stats["started_at"] = datetime.now()
    interval = 0 if args.no_wait else INTERVAL_SECONDS

    for i, it in enumerate(queue, 1):
        if shutdown_requested: break
        sid = resolve_source_for_item(it, smap)
        if not sid:
            log(f"[{i}/{len(queue)}] seq={it['seq_global']}: sem source para book_id={it['book_id']!r} — PULANDO")
            session_stats["items_failed"] += 1
            continue
        log(f"[{i}/{len(queue)}] seq={it['seq_global']}: {it['scene_identifier']}")
        log(f"   Source: {sid[:8]}... ({it['book_id']})")
        prompt = load_prompt(it)
        log(f"   Prompt: {it['prompt_filename']} ({len(prompt)} chars)")

        ok = False
        for attempt in range(1, MAX_RETRIES + 1):
            if attempt > 1:
                log(f"   Tentativa {attempt}/{MAX_RETRIES}")
                time.sleep(30 * attempt)
            artifact_id = create_audio(prompt, sid)
            if artifact_id:
                log(f"   Artifact: {artifact_id[:12]}...")
                upsert_entry({
                    "seq_global": it["seq_global"],
                    "scene_identifier": it["scene_identifier"],
                    "cena_filename": it["cena_filename"],
                    "prompt_filename": it["prompt_filename"],
                    "arquivo": filename_for(it),
                    "artifact_id": artifact_id,
                    "source_id": sid,
                    "book_id": it["book_id"],
                    "data_geracao": datetime.now().isoformat(),
                    "prompt_chars": len(prompt),
                    "language": LANGUAGE,
                    "audio_format": AUDIO_FORMAT,
                    "status": "created",
                })
                session_stats["items_created"] += 1
                ok = True; break

        if not ok:
            log("   FALHOU"); session_stats["items_failed"] += 1

        if i < len(queue) and not shutdown_requested and not args.no_wait:
            log(f"   Aguardando {interval//60}min...")
            for _ in range(interval):
                if shutdown_requested: break
                time.sleep(1)

    print()
    print("=" * 60)
    print(f"  Criados: {session_stats['items_created']}  Falhas: {session_stats['items_failed']}")
    print("=" * 60)
    return 0 if session_stats["items_failed"] == 0 else 1


def run_download(items: list[dict]) -> int:
    if not check_auth():
        log("ERRO: nlm nao autenticado. Execute: nlm login --profile " + PROFILE); return 1
    md = load_metadata()
    pending = [a for a in md.get("audios", []) if a.get("status") == "created" and a.get("artifact_id")]
    if not pending:
        log("Nada pendente."); return 0
    log(f"Baixando {len(pending)} artifacts")
    by_seq = {it["seq_global"]: it for it in items}

    ok = fail = still = 0
    for a in pending:
        if shutdown_requested: break
        seq = a["seq_global"]
        log(f"seq={seq}: {a['scene_identifier']}")
        st = poll_status(a["artifact_id"])
        if st == "completed":
            out = AUDIOS_DIR / a["arquivo"]
            if download_artifact(a["artifact_id"], out):
                a["status"] = "downloaded"
                a["output_path"] = str(out)
                a["tamanho_bytes"] = out.stat().st_size
                upsert_entry(a); ok += 1
            else:
                fail += 1
        elif st in ("failed", None):
            log(f"   status studio: {st!r}")
            if st is None:
                a["status"] = "lost_in_studio"; upsert_entry(a)
            fail += 1
        else:
            log(f"   ainda processando ({st})"); still += 1

    print(f"\nBaixados: {ok}  Ainda processando: {still}  Falhas: {fail}")
    return 0 if fail == 0 else 1


# ── CLI ────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description=f"{OBRA_TITLE} audio runner")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max", type=int, default=DEFAULT_MAX_DAILY, dest="max_items",
                   help=f"max itens nesta sessão (default {DEFAULT_MAX_DAILY})")
    p.add_argument("--no-wait", action="store_true", help="sem intervalo entre disparos (teste)")
    p.add_argument("--bootstrap", action="store_true",
                   help="importar áudios já criados no studio para metadata.json")
    p.add_argument("--download", action="store_true",
                   help="baixar áudios com status=created")
    p.add_argument("--skip-auth-check", action="store_true",
                   help="pular check de auth (só com --dry-run)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    print(f"\n  {OBRA_TITLE} — Audio Runner")
    print(f"  notebook={NOTEBOOK_ID[:8]}... profile={PROFILE} lang={LANGUAGE}\n")

    items = build_manifest()
    log(f"Manifest: {len(items)} cenas pareadas com prompts")

    if args.bootstrap:
        return bootstrap_from_studio(items)
    if args.download:
        return run_download(items)
    return run_create(args, items)


if __name__ == "__main__":
    sys.exit(main())
