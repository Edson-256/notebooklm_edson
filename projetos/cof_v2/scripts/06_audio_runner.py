#!/usr/bin/env python3
"""
COF v2 Audio Runner (fire-and-forget) — análogo ao quo_vadis_runner.py.

Lê _sources_map.json (782 itens, seq_global 1–782) e dispara áudios no
NotebookLM com prompt customizado por item. Status:
    created    → artifact_id obtido, áudio em processamento no servidor
    downloaded → .mp3 baixado e validado em audios/<filename>.mp3

Uso (sempre dry-run primeiro!):
    python3 scripts/06_audio_runner.py --dry-run
    python3 scripts/06_audio_runner.py --dry-run --from 1 --to 10
    python3 scripts/06_audio_runner.py --max 5
    python3 scripts/06_audio_runner.py --kind aula --from 1 --to 50
    python3 scripts/06_audio_runner.py --download

Regras canônicas (docs/regras_pipeline_audio_por_cena.md):
    - ID canônico = seq_global (1-782), única chave em metadata e filename
    - Manifest = _sources_map.json (não regex em markdown)
    - Sanity-checks no startup: IDs 1..N, prompts existem, source_ids existem
    - Dry-run obrigatório antes do primeiro run real
    - 2min entre disparos; lotes pequenos (10-20)
    - Logging com prompt_filename, source_ids, artifact_id
"""
from __future__ import annotations

import argparse
import json
import re
import signal
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

# ── Configurações ──────────────────────────────────────────────────────
COF_DIR = Path(__file__).resolve().parent.parent      # projetos/cof_v2/
PROJECT_DIR = COF_DIR.parent.parent                   # notebooklm_edson/
LOGS_DIR = PROJECT_DIR / "logs"
NOTEBOOK_ID = "5508086a-da53-4947-bce4-a1d7d83cf0e2"
SOURCES_MAP_FILE = COF_DIR / "_sources_map.json"
AUDIOS_DIR = COF_DIR / "audios"
METADATA_FILE = AUDIOS_DIR / "metadata.json"
PROFILE = "default"

INTERVAL_SECONDS = 120     # 2 min entre disparos
POLL_INTERVAL = 30
MAX_WAIT_MINUTES = 30
MAX_RETRIES = 3
MAX_FOCUS_CHARS = 10000

OBRA_TITLE = "Curso Online de Filosofia (COF)"
OBRA_SLUG = "cof"
TOTAL_ITEMS = 782

# audio_format do inventário → flag --format do nlm
FORMAT_MAP = {
    "Deep Dive": "deep_dive",
    "The Brief": "brief",
    "The Debate": "debate",
    "The Critique": "critique",
}

# ── Estado ─────────────────────────────────────────────────────────────
shutdown_requested = False
session_stats = {
    "started_at": None,
    "items_attempted": 0,
    "items_created": 0,
    "items_failed": 0,
    "current_item": None,
}
session_results: list[dict] = []


def handle_shutdown(signum, frame):
    global shutdown_requested
    if shutdown_requested:
        print("\n\nForcando saida imediata...")
        save_session_log()
        print_summary()
        sys.exit(1)
    shutdown_requested = True
    print("\n\nCtrl+C detectado. Finalizando apos o item atual...")
    print("   (Pressione Ctrl+C novamente para forcar saida)")


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ── Utilidades ─────────────────────────────────────────────────────────

def log(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {message}")


def slugify_keyword(text: str) -> str:
    """Gera keyword curta para filename. Pega 1-2 palavras significativas."""
    stop = {"o", "a", "os", "as", "do", "da", "dos", "das", "de", "e", "para",
            "entre", "com", "no", "na", "nos", "nas", "ao", "à", "um", "uma",
            "que", "se", "por", "em", "aula", "olavo", "carvalho"}
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    words = re.findall(r"\w+", norm.lower())
    keep = [w for w in words if w not in stop and len(w) > 2]
    return "_".join(keep[:2])[:30] or "item"


# ── Manifest ───────────────────────────────────────────────────────────

def load_items(args) -> list[dict]:
    """Lê _sources_map.json, aplica filtros (--from/--to/--kind), retorna lista
    ordenada por seq_global. Cada item já vem com source_id e prompt_path."""
    if not SOURCES_MAP_FILE.exists():
        log(f"ERRO: {SOURCES_MAP_FILE} nao existe. Rode scripts/06_build_sources_map.py primeiro.")
        sys.exit(1)
    data = json.loads(SOURCES_MAP_FILE.read_text(encoding="utf-8"))
    items_dict = data["items"]

    items = []
    for seq_str, it in items_dict.items():
        items.append({
            "seq_global": int(it["seq_global"]),
            "slug": it["slug"],
            "kind": it["kind"],
            "titulo": it["titulo"],
            "audio_format": it.get("audio_format") or "Deep Dive",
            "source_id": it["source_id"],
            "source_title": it["source_title"],
            "prompt_path": it.get("prompt_path"),
            "guide_path": it.get("guide_path"),
        })
    items.sort(key=lambda x: x["seq_global"])

    if args.kind:
        items = [it for it in items if it["kind"] == args.kind]
    if args.from_seq is not None:
        items = [it for it in items if it["seq_global"] >= args.from_seq]
    if args.to_seq is not None:
        items = [it for it in items if it["seq_global"] <= args.to_seq]
    if args.only_seq:
        wanted = {int(s) for s in args.only_seq.split(",")}
        items = [it for it in items if it["seq_global"] in wanted]

    return items


def sanity_check(all_items: list[dict]) -> None:
    """Aborta se manifest tiver problema. Roda contra a lista COMPLETA, não filtrada."""
    if not all_items:
        log("ERRO: nenhum item carregado de _sources_map.json")
        sys.exit(1)
    seqs = [it["seq_global"] for it in all_items]
    if len(seqs) != len(set(seqs)):
        log(f"ERRO: seq_global duplicados ({len(seqs)} vs {len(set(seqs))} unicos)")
        sys.exit(1)
    if seqs != sorted(seqs):
        log("ERRO: seq_global fora de ordem")
        sys.exit(1)
    if seqs != list(range(1, len(seqs) + 1)):
        log(f"ERRO: seq_global nao-continuos (esperado 1..{len(seqs)})")
        sys.exit(1)
    if len(seqs) != TOTAL_ITEMS:
        log(f"AVISO: esperava {TOTAL_ITEMS} itens, encontrei {len(seqs)}")

    missing_prompts = [it for it in all_items if not it["prompt_path"]]
    missing_sids = [it for it in all_items if not it["source_id"]]
    if missing_prompts:
        log(f"ERRO: {len(missing_prompts)} itens sem prompt_path")
        for it in missing_prompts[:5]:
            log(f"  seq={it['seq_global']} {it['slug']}")
        sys.exit(1)
    if missing_sids:
        log(f"ERRO: {len(missing_sids)} itens sem source_id")
        sys.exit(1)

    # Verificar que arquivos de prompt existem em disco
    not_on_disk = []
    for it in all_items:
        p = COF_DIR / it["prompt_path"]
        if not p.exists():
            not_on_disk.append(it)
    if not_on_disk:
        log(f"ERRO: {len(not_on_disk)} prompts referenciados não existem em disco")
        for it in not_on_disk[:5]:
            log(f"  seq={it['seq_global']} {it['prompt_path']}")
        log("  → reconstruir _sources_map.json: scripts/06_build_sources_map.py")
        sys.exit(1)

    bad_format = [it for it in all_items if it["audio_format"] not in FORMAT_MAP]
    if bad_format:
        log(f"ERRO: {len(bad_format)} itens com audio_format desconhecido")
        for it in bad_format[:5]:
            log(f"  seq={it['seq_global']} format={it['audio_format']!r}")
        sys.exit(1)


def load_prompt(item: dict) -> str:
    p = COF_DIR / item["prompt_path"] if not Path(item["prompt_path"]).is_absolute() else Path(item["prompt_path"])
    content = p.read_text(encoding="utf-8").strip()
    if len(content) > MAX_FOCUS_CHARS:
        content = content[: MAX_FOCUS_CHARS - 3] + "..."
    return content


# ── Metadata / progresso ───────────────────────────────────────────────

def load_metadata() -> dict:
    if not METADATA_FILE.exists():
        return {"obra": OBRA_TITLE, "obra_slug": OBRA_SLUG,
                "notebook_id": NOTEBOOK_ID, "audios": []}
    return json.loads(METADATA_FILE.read_text(encoding="utf-8"))


def get_processed_seqs() -> set[int]:
    md = load_metadata()
    return {a["cena_numero"] for a in md.get("audios", [])
            if a.get("status") in ("created", "downloaded")}


def save_metadata_entry(entry: dict) -> None:
    AUDIOS_DIR.mkdir(exist_ok=True)
    md = load_metadata()
    by_num = {a["cena_numero"]: a for a in md.get("audios", [])}
    if entry["cena_numero"] in by_num:
        log(f"   AVISO: sobrescrevendo entrada existente para seq={entry['cena_numero']}")
    by_num[entry["cena_numero"]] = entry
    md["obra"] = OBRA_TITLE
    md["obra_slug"] = OBRA_SLUG
    md["notebook_id"] = NOTEBOOK_ID
    md["total_itens_processados"] = len(by_num)
    md["ultima_atualizacao"] = datetime.now().isoformat()
    md["audios"] = sorted(by_num.values(), key=lambda a: a["cena_numero"])
    METADATA_FILE.write_text(json.dumps(md, indent=2, ensure_ascii=False), encoding="utf-8")


# ── nlm wrappers ───────────────────────────────────────────────────────

def run_nlm(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout)


def check_auth() -> bool:
    try:
        run_nlm(["login", "switch", PROFILE], timeout=15)
        result = run_nlm(["login", "--check", "--profile", PROFILE], timeout=30)
        return result.returncode == 0
    except Exception as e:
        log(f"Erro ao verificar auth: {e}")
        return False


_UUID_RE = re.compile(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}")


def create_audio(focus: str, source_id: str, fmt: str) -> str | None:
    cmd = [
        "create", "audio", NOTEBOOK_ID,
        "--format", fmt,
        "--language", "pt-BR",
        "--length", "long",
        "--focus", focus,
        "--source-ids", source_id,
        "--profile", PROFILE,
        "--confirm",
    ]
    try:
        result = run_nlm(cmd, timeout=180)
    except subprocess.TimeoutExpired:
        log("   Timeout ao criar audio (180s)")
        return None
    if result.returncode != 0:
        if result.stderr.strip():
            log(f"   nlm stderr: {result.stderr.strip()[:500]}")
        if result.stdout.strip():
            log(f"   nlm stdout: {result.stdout.strip()[:300]}")
        return None
    m = re.search(r"(?:Artifact|Audio)\s*(?:ID)?[:\s]+([a-f0-9-]{20,})",
                  result.stdout, re.IGNORECASE)
    if m:
        return m.group(1)
    m = _UUID_RE.search(result.stdout)
    return m.group(0) if m else None


def poll_status(artifact_id: str) -> str | None:
    try:
        result = run_nlm(["studio", "status", NOTEBOOK_ID, "--json",
                          "--profile", PROFILE], timeout=30)
        if result.returncode != 0:
            return None
        for a in json.loads(result.stdout):
            if a.get("id") == artifact_id:
                return a.get("status")
    except Exception:
        return None
    return None


def download_audio(artifact_id: str, output_path: Path) -> bool:
    try:
        result = run_nlm(["download", "audio", NOTEBOOK_ID,
                          "--id", artifact_id,
                          "--output", str(output_path),
                          "--no-progress"], timeout=300)
    except Exception as e:
        log(f"   Erro no download: {e}")
        return False
    if result.returncode == 0 and output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        log(f"   Download OK: {size_mb:.1f} MB")
        return True
    log(f"   Download falhou: {result.stderr[:300]}")
    return False


# ── Processamento ─────────────────────────────────────────────────────

def filename_for(item: dict) -> str:
    kw = slugify_keyword(item["titulo"])
    return f"cof_{item['seq_global']:03d}_{kw}.mp3"


def process_item(item: dict) -> bool:
    seq = item["seq_global"]
    fmt = FORMAT_MAP[item["audio_format"]]
    prompt_text = load_prompt(item)
    fname = filename_for(item)

    log(f"   Format: {fmt} | Source: {item['source_title'][:50]}")
    log(f"   Prompt: {Path(item['prompt_path']).name} ({len(prompt_text)} chars)")

    session_stats["current_item"] = seq
    session_stats["items_attempted"] += 1

    result_entry = {
        "seq_global": seq,
        "slug": item["slug"],
        "titulo": item["titulo"],
        "kind": item["kind"],
        "audio_format": item["audio_format"],
        "prompt_filename": Path(item["prompt_path"]).name,
        "prompt_chars": len(prompt_text),
        "source_id": item["source_id"],
        "source_title": item["source_title"],
        "status": "failed",
        "timestamp": datetime.now().isoformat(),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        if shutdown_requested:
            result_entry["status"] = "interrupted"
            session_results.append(result_entry)
            return False
        if attempt > 1:
            wait = 30 * attempt
            log(f"   Tentativa {attempt}/{MAX_RETRIES} (aguardando {wait}s)...")
            time.sleep(wait)

        log("   Disparando criacao...")
        artifact_id = create_audio(prompt_text, item["source_id"], fmt)
        if not artifact_id:
            continue

        log(f"   Artifact: {artifact_id[:12]}... (fire-and-forget)")
        result_entry["artifact_id"] = artifact_id
        result_entry["status"] = "created"

        focus_preview = prompt_text[:200] + "..." if len(prompt_text) > 200 else prompt_text
        save_metadata_entry({
            "arquivo": fname,
            "cena_numero": seq,
            "slug": item["slug"],
            "kind": item["kind"],
            "titulo_completo": item["titulo"],
            "audio_format": item["audio_format"],
            "nlm_format": fmt,
            "artifact_id": artifact_id,
            "data_geracao": datetime.now().isoformat(),
            "prompt_filename": Path(item["prompt_path"]).name,
            "prompt_chars": len(prompt_text),
            "focus_preview": focus_preview,
            "source_id": item["source_id"],
            "source_title": item["source_title"],
            "status": "created",
        })
        session_results.append(result_entry)
        session_stats["items_created"] += 1
        return True

    session_results.append(result_entry)
    session_stats["items_failed"] += 1
    return False


# ── Download posterior ────────────────────────────────────────────────

def download_pending() -> int:
    md = load_metadata()
    pending = [a for a in md.get("audios", [])
               if a.get("status") == "created" and a.get("artifact_id")]
    if not pending:
        log("Nenhum artifact pendente de download.")
        return 0
    log(f"Encontrados {len(pending)} artifacts para baixar")
    print()

    downloaded = failed = still = 0
    for i, audio in enumerate(pending, 1):
        if shutdown_requested:
            break
        seq = audio["cena_numero"]
        log(f"[{i}/{len(pending)}] seq={seq}: {audio['titulo_completo'][:50]}")
        status = poll_status(audio["artifact_id"])
        if status == "completed":
            out = AUDIOS_DIR / audio["arquivo"]
            if download_audio(audio["artifact_id"], out):
                audio["status"] = "downloaded"
                audio["output_path"] = str(out)
                audio["tamanho_bytes"] = out.stat().st_size
                save_metadata_entry(audio)
                downloaded += 1
            else:
                failed += 1
        elif status == "failed":
            log("   Processamento falhou no servidor")
            audio["status"] = "server_failed"
            save_metadata_entry(audio)
            failed += 1
        else:
            log(f"   Ainda processando (status: {status})")
            still += 1

    print()
    print("=" * 60)
    print("  RESUMO DO DOWNLOAD")
    print("=" * 60)
    print(f"  Baixados:          {downloaded}")
    print(f"  Ainda processando: {still}")
    print(f"  Falhas:            {failed}")
    print("=" * 60)
    return 0 if failed == 0 else 1


# ── Logs / resumos ─────────────────────────────────────────────────────

def save_session_log():
    if not session_results:
        return
    LOGS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = LOGS_DIR / f"cof_session_{ts}.json"
    data = {
        "project": OBRA_SLUG,
        "started_at": session_stats["started_at"].isoformat() if session_stats["started_at"] else None,
        "finished_at": datetime.now().isoformat(),
        "items_attempted": session_stats["items_attempted"],
        "items_created": session_stats["items_created"],
        "items_failed": session_stats["items_failed"],
        "results": session_results,
    }
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8")
    log(f"   Log da sessao: {path.name}")


def print_summary():
    s = session_stats
    elapsed = ""
    if s["started_at"]:
        delta = datetime.now() - s["started_at"]
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        elapsed = f" ({h}h{m:02d}m)"
    print()
    print("=" * 60)
    print(f"  RESUMO DA SESSAO{elapsed}")
    print("=" * 60)
    print(f"  Itens tentados:    {s['items_attempted']}")
    print(f"  Criados OK:        {s['items_created']}")
    print(f"  Falhas:            {s['items_failed']}")
    print("=" * 60)


def print_progress_bar(done: int, total: int, width: int = 40):
    pct = done / total if total > 0 else 0
    filled = int(width * pct)
    bar = "#" * filled + "." * (width - filled)
    print(f"  [{bar}] {done}/{total} ({pct:.1%})")


# ── Main ──────────────────────────────────────────────────────────────

def parse_args():
    ap = argparse.ArgumentParser(description="COF v2 Audio Runner (fire-and-forget)")
    ap.add_argument("--dry-run", action="store_true", help="Mostrar plano sem executar")
    ap.add_argument("--max", type=int, default=0, dest="max_items",
                    help="Limita N itens (0 = todos)")
    ap.add_argument("--from", type=int, default=None, dest="from_seq",
                    help="seq_global mínimo (inclusivo)")
    ap.add_argument("--to", type=int, default=None, dest="to_seq",
                    help="seq_global máximo (inclusivo)")
    ap.add_argument("--only", type=str, default="", dest="only_seq",
                    help="Lista de seq_global separados por vírgula (ex: 1,5,42)")
    ap.add_argument("--kind", type=str, default="",
                    choices=["", "aula", "extra_aula", "livro", "apostila", "artigo", "teoria_estado"],
                    help="Filtrar por kind")
    ap.add_argument("--no-wait", action="store_true",
                    help="Sem intervalo entre disparos (apenas testes)")
    ap.add_argument("--download", action="store_true",
                    help="Baixar áudios já criados (status=created)")
    ap.add_argument("--skip-auth-check", action="store_true",
                    help="Pular nlm login --check (use só se souber o que faz)")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    print()
    print("  COF v2 Audio Runner (fire-and-forget)")
    print("  =====================================")
    print(f"  {OBRA_TITLE}")
    print(f"  Notebook: {NOTEBOOK_ID}")
    print(f"  ~2 min/item · 782 itens totais")
    print()

    if args.download:
        return download_pending()

    log("Carregando _sources_map.json...")
    # Sanity-check roda contra TODOS os itens (não filtrados)
    full_data = json.loads(SOURCES_MAP_FILE.read_text(encoding="utf-8"))
    full_items = []
    for it in full_data["items"].values():
        full_items.append({
            "seq_global": int(it["seq_global"]),
            "slug": it["slug"], "kind": it["kind"], "titulo": it["titulo"],
            "audio_format": it.get("audio_format") or "Deep Dive",
            "source_id": it["source_id"], "source_title": it["source_title"],
            "prompt_path": it.get("prompt_path"), "guide_path": it.get("guide_path"),
        })
    full_items.sort(key=lambda x: x["seq_global"])
    sanity_check(full_items)
    log(f"Sanity OK: {len(full_items)} itens, ids 1..{len(full_items)} contínuos")

    if not args.skip_auth_check:
        log("Verificando autenticacao nlm...")
        if not check_auth():
            log("ERRO: nlm nao autenticado. Execute: nlm login --profile default")
            return 1
        log("Auth OK")

    items = load_items(args)
    if not items:
        log("Nenhum item bate com os filtros aplicados.")
        return 1

    processed = get_processed_seqs()
    pending = [it for it in items if it["seq_global"] not in processed]

    print()
    log("Estado atual:")
    print(f"  Itens no filtro:   {len(items)}")
    print(f"  Já processados:    {len(items) - len(pending)}")
    print(f"  Pendentes:         {len(pending)}")
    print()
    print_progress_bar(len(processed), TOTAL_ITEMS)
    print()

    if not pending:
        log("Tudo já processado dentro do filtro.")
        return 0

    queue = pending if args.max_items <= 0 else pending[: args.max_items]
    interval = 0 if args.no_wait else INTERVAL_SECONDS
    est_min = len(queue) * (interval // 60 + 1)
    est_h = est_min / 60

    log(f"Fila: {len(queue)} itens | Estimativa: ~{est_h:.1f}h")
    print()

    if args.dry_run:
        log("PLANO DE EXECUCAO (dry-run):")
        print()
        print(f"  {'#':>4} {'seq':>4} {'kind':<13} {'fmt':<10} {'titulo':<55} prompt")
        print("  " + "-" * 110)
        for i, it in enumerate(queue, 1):
            fmt = FORMAT_MAP[it["audio_format"]]
            print(f"  {i:4d} {it['seq_global']:4d} {it['kind']:<13} {fmt:<10} "
                  f"{it['titulo'][:55]:<55} {Path(it['prompt_path']).name}")
        print()
        log(f"Total: {len(queue)} itens")
        print()
        log("Quando estiver satisfeito com este plano, rode SEM --dry-run.")
        log("Sugestão: comece com --max 1 (1 item) ou --max 10 (lote pequeno).")
        return 0

    session_stats["started_at"] = datetime.now()

    for i, it in enumerate(queue, 1):
        if shutdown_requested:
            break
        remaining = len(queue) - i
        log(f"[{i}/{len(queue)}] seq={it['seq_global']} ({it['kind']}): {it['titulo'][:50]}")
        ok = process_item(it)
        if ok:
            log(f"   OK ({session_stats['items_created']}/{len(queue)} criados, {remaining} restantes)")
        elif not shutdown_requested:
            log("   FALHOU (continuando...)")
        if not shutdown_requested and i < len(queue) and not args.no_wait:
            log(f"   Aguardando {INTERVAL_SECONDS // 60}min...")
            for _ in range(INTERVAL_SECONDS):
                if shutdown_requested:
                    break
                time.sleep(1)

    save_session_log()
    print_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
