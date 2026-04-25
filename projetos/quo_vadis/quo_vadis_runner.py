#!/usr/bin/env python3
"""
Quo Vadis Audio Runner (fire-and-forget)
Dispara criação dos áudios no NotebookLM sem esperar processamento.
Adaptado do Ben-Hur Runner para 134 cenas em 3 partes + epílogo.

Uso:
    python3 projetos/quo_vadis/quo_vadis_runner.py              # Fire-and-forget
    python3 projetos/quo_vadis/quo_vadis_runner.py --dry-run    # Mostrar plano
    python3 projetos/quo_vadis/quo_vadis_runner.py --max-scenes 5
    python3 projetos/quo_vadis/quo_vadis_runner.py --parte 1    # Só a Parte 1
    python3 projetos/quo_vadis/quo_vadis_runner.py --download   # Baixar áudios prontos
"""

import subprocess
import json
import time
import re
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import unicodedata
import argparse

# ── Configurações ──────────────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent.parent.parent  # notebooklm_edson/
QV_DIR = Path(__file__).parent                      # projetos/quo_vadis/
LOGS_DIR = PROJECT_DIR / "logs"
NOTEBOOK_ID = "c7f86c97-bf9b-4087-bcc2-2945fb18ee93"
SOURCES_MAP_FILE = QV_DIR / "_sources_map.json"     # title → source_id
PROMPTS_MANIFEST_FILE = QV_DIR / "_prompts_manifest.json"  # fonte canônica de cenas
PROFILE = "default"
INTERVAL_SECONDS = 120  # 2 minutos entre cenas (fire-and-forget)
POLL_INTERVAL = 30      # 30 segundos entre checks (modo --download)
MAX_WAIT_MINUTES = 30
MAX_RETRIES = 3
MAX_FOCUS_CHARS = 10000  # Limite do NotebookLM Audio Overview --focus

BOOK_TITLE = "Quo Vadis"
BOOK_AUTHOR = "Henryk Sienkiewicz"
BOOK_SLUG = "quo_vadis"
TOTAL_SCENES = 134

# Intervalos de cenas por parte (numeração global 1-134)
PARTE_RANGES = {
    1: (1, 35),     # Primeira Parte — 35 cenas
    2: (36, 68),    # Segunda Parte  — 33 cenas
    3: (69, 131),   # Terceira Parte — 63 cenas
    0: (132, 134),  # Epílogo        — 3 cenas (--parte 0)
}

# ── Estado global ──────────────────────────────────────────────────────
shutdown_requested = False
session_stats = {
    'started_at': None,
    'scenes_attempted': 0,
    'scenes_created': 0,
    'scenes_failed': 0,
    'current_scene': None,
}
session_results = []


def handle_shutdown(signum, frame):
    global shutdown_requested
    if shutdown_requested:
        print("\n\nForcando saida imediata...")
        save_session_log()
        print_summary()
        sys.exit(1)
    shutdown_requested = True
    print("\n\nCtrl+C detectado. Finalizando apos a cena atual...")
    print("   (Pressione Ctrl+C novamente para forcar saida)")


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)


# ── Utilidades ─────────────────────────────────────────────────────────

def log(message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def extract_keyword(title: str) -> str:
    stopwords = {'o', 'a', 'os', 'as', 'do', 'da', 'dos', 'das', 'de', 'e',
                 'para', 'entre', 'com', 'no', 'na', 'nos', 'nas', 'ao', 'à',
                 'um', 'uma', 'que', 'se', 'por', 'em'}
    words = re.findall(r'\w+', title.lower())
    words = [unicodedata.normalize('NFKD', w).encode('ascii', 'ignore').decode('ascii')
             for w in words]
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return '_'.join(keywords[:2])[:30]


# ── Prompts customizados ──────────────────────────────────────────────

def load_scene_prompt(scene_number: int) -> Optional[str]:
    """Carrega prompt customizado da cena em prompts_cenas/."""
    prompts_dir = QV_DIR / "prompts_cenas"
    if not prompts_dir.exists():
        return None

    prefix = f"{scene_number:03d}_"  # 3 dígitos (134 cenas)
    for p in prompts_dir.iterdir():
        if p.name.startswith(prefix) and p.suffix == '.md':
            content = p.read_text(encoding='utf-8').strip()
            if len(content) > MAX_FOCUS_CHARS:
                content = content[:MAX_FOCUS_CHARS - 3] + "..."
            return content
    return None


# ── Resolução de sources por cena ─────────────────────────────────────

_sources_map_cache: Optional[Dict[str, str]] = None


def load_sources_map() -> Dict[str, str]:
    """Carrega mapeamento 'QV-P1-C01.md' → 'source-uuid' de _sources_map.json."""
    global _sources_map_cache
    if _sources_map_cache is not None:
        return _sources_map_cache

    if not SOURCES_MAP_FILE.exists():
        log(f"AVISO: {SOURCES_MAP_FILE.name} nao encontrado; usando todas as sources do notebook.")
        _sources_map_cache = {}
        return _sources_map_cache

    try:
        _sources_map_cache = json.loads(SOURCES_MAP_FILE.read_text(encoding='utf-8'))
    except Exception as e:
        log(f"AVISO: erro lendo {SOURCES_MAP_FILE.name}: {e}")
        _sources_map_cache = {}
    return _sources_map_cache


def resolve_source_ids(scene: Dict) -> List[str]:
    """
    Resolve source IDs para uma cena, baseado na localização.
    Ex: 'Parte 1, Capítulo 5 (cena 2/2) / Capítulo 6 (cena 1/1)' →
        ['<id de QV-P1-C05.md>', '<id de QV-P1-C06.md>'].
    Retorna lista vazia se não encontrar (caller usa default do notebook).
    """
    src_map = load_sources_map()
    if not src_map:
        return []

    location = scene.get('location', '')

    # Caso Epílogo
    if 'Epílogo' in location:
        ep_id = src_map.get('QV-EP.md')
        return [ep_id] if ep_id else []

    # Detectar parte
    part_match = re.search(r'Parte\s+(\d)', location)
    if not part_match:
        return []
    part_num = int(part_match.group(1))

    # Detectar capítulo(s) mencionados
    chap_nums = [int(n) for n in re.findall(r'Capítulo\s+(\d+)', location)]
    ids = []
    for c in chap_nums:
        key = f"QV-P{part_num}-C{c:02d}.md"
        sid = src_map.get(key)
        if sid:
            ids.append(sid)
    return ids


# ── Extração de cenas ──────────────────────────────────────────────────

def extract_scenes(filepath: Path) -> List[Dict]:
    """
    Lê cenas de _prompts_manifest.json (fonte canônica com numeração GLOBAL 1-134).

    Não usar regex sobre 01_cenas_identificadas.md: a numeração lá reinicia a cada
    parte (P1 1-35, P2 1-33, P3 1-63, EP 1-3) e colide com a numeração global usada
    em prompts_cenas/ e nas chaves do metadata.json.

    O argumento `filepath` é mantido só por compatibilidade da assinatura.
    """
    manifest = json.loads(PROMPTS_MANIFEST_FILE.read_text(encoding='utf-8'))
    scenes = []
    for entry in manifest:
        scenes.append({
            'number': int(entry['audio']),           # GLOBAL 1-134
            'local_number': int(entry['local_num']),
            'parte': int(entry['part_num']),         # 1, 2, 3 (epílogo: ver part_name)
            'parte_nome': entry.get('part_name', ''),
            'title': entry['title'].strip(),
            'location': entry['localization'].strip(),
            'summary': entry.get('resumo', '').strip(),
            'justification': entry.get('justificativa', '').strip(),
        })
    scenes.sort(key=lambda s: s['number'])
    return scenes


# ── Progresso real ─────────────────────────────────────────────────────

def get_processed_scenes() -> set:
    """Retorna set de números de cenas já criadas ou baixadas."""
    metadata_file = QV_DIR / "audios" / "metadata.json"
    if not metadata_file.exists():
        return set()
    try:
        data = json.loads(metadata_file.read_text(encoding='utf-8'))
        return {
            a['cena_numero']
            for a in data.get('audios', [])
            if a.get('status') in ('created', 'downloaded')
        }
    except Exception:
        return set()


# ── Geração de áudio ──────────────────────────────────────────────────

def run_nlm(args: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    cmd = ["nlm"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_auth() -> bool:
    try:
        run_nlm(["login", "switch", PROFILE], timeout=15)
        result = run_nlm(["login", "--check", "--profile", PROFILE], timeout=30)
        return result.returncode == 0
    except Exception as e:
        log(f"Erro ao verificar auth: {e}")
        return False


def create_audio(focus_topic: str, source_ids: List[str]) -> Optional[str]:
    """Cria áudio e retorna artifact_id. Se source_ids vazio, usa todas as sources do notebook."""
    try:
        cmd = [
            "create", "audio", NOTEBOOK_ID,
            "--format", "deep_dive",
            "--language", "pt-BR",
            "--length", "long",
            "--focus", focus_topic,
            "--profile", PROFILE,
            "--confirm",
        ]
        if source_ids:
            cmd.extend(["--source-ids", ",".join(source_ids)])

        result = run_nlm(cmd, timeout=180)

        if result.returncode != 0:
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            if stderr:
                log(f"   nlm stderr: {stderr[:500]}")
            if stdout:
                log(f"   nlm stdout: {stdout[:300]}")
            return None

        output = result.stdout

        match = re.search(r'(?:Artifact|Audio)\s*(?:ID)?[:\s]+([a-f0-9-]{20,})', output, re.IGNORECASE)
        if match:
            return match.group(1)

        match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', output)
        if match:
            return match.group(1)

        log(f"   Artifact ID nao encontrado: {output[:300]}")
        return None

    except subprocess.TimeoutExpired:
        log("   Timeout ao criar audio (180s)")
        return None
    except Exception as e:
        log(f"   Erro ao criar audio: {e}")
        return None


def poll_status(artifact_id: str) -> Optional[str]:
    try:
        result = run_nlm([
            "studio", "status", NOTEBOOK_ID, "--json",
            "--profile", PROFILE,
        ], timeout=30)

        if result.returncode != 0:
            return None

        artifacts = json.loads(result.stdout)
        for a in artifacts:
            if a.get('id') == artifact_id:
                return a.get('status')
        return None
    except Exception:
        return None


def wait_for_completion(artifact_id: str) -> bool:
    max_polls = MAX_WAIT_MINUTES * 2

    for i in range(max_polls):
        if shutdown_requested:
            return False

        status = poll_status(artifact_id)

        if status == "completed":
            return True
        elif status == "failed":
            log("   Processamento falhou no servidor")
            return False

        if (i + 1) % 4 == 0:
            elapsed = (i + 1) * POLL_INTERVAL // 60
            log(f"   Processando... ({elapsed}min)")

        time.sleep(POLL_INTERVAL)

    log(f"   Timeout apos {MAX_WAIT_MINUTES}min")
    return False


def download_audio(artifact_id: str, output_path: Path) -> bool:
    try:
        result = run_nlm([
            "download", "audio", NOTEBOOK_ID,
            "--id", artifact_id,
            "--output", str(output_path),
            "--no-progress",
        ], timeout=300)

        if result.returncode == 0 and output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            log(f"   Download OK: {size_mb:.1f} MB")
            return True
        else:
            log(f"   Download falhou: {result.stderr[:300]}")
            return False
    except Exception as e:
        log(f"   Erro no download: {e}")
        return False


# ── Metadata ──────────────────────────────────────────────────────────

def save_metadata(audio_entry: Dict):
    audios_dir = QV_DIR / "audios"
    audios_dir.mkdir(exist_ok=True)
    metadata_path = audios_dir / "metadata.json"

    existing_audios = []
    if metadata_path.exists():
        try:
            data = json.loads(metadata_path.read_text(encoding='utf-8'))
            existing_audios = data.get('audios', [])
        except Exception:
            pass

    by_num = {a['cena_numero']: a for a in existing_audios}
    by_num[audio_entry['cena_numero']] = audio_entry
    merged = sorted(by_num.values(), key=lambda a: a['cena_numero'])

    metadata = {
        'obra': BOOK_TITLE,
        'autor': BOOK_AUTHOR,
        'obra_slug': BOOK_SLUG,
        'notebook_id': NOTEBOOK_ID,
        'total_cenas': len(merged),
        'ultima_atualizacao': datetime.now().isoformat(),
        'audios': merged,
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )


def save_session_log():
    if not session_results:
        return
    LOGS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = LOGS_DIR / f"qv_session_{ts}.json"
    log_data = {
        'project': BOOK_SLUG,
        'started_at': session_stats['started_at'].isoformat() if session_stats['started_at'] else None,
        'finished_at': datetime.now().isoformat(),
        'scenes_attempted': session_stats['scenes_attempted'],
        'scenes_created': session_stats['scenes_created'],
        'scenes_failed': session_stats['scenes_failed'],
        'results': session_results,
    }
    log_path.write_text(
        json.dumps(log_data, indent=2, ensure_ascii=False, default=str),
        encoding='utf-8',
    )
    log(f"   Log da sessao: {log_path.name}")


# ── Processamento principal ──────────────────────────────────────────

def process_scene(scene: Dict) -> bool:
    keyword = extract_keyword(scene['title'])
    filename = f"qv_{scene['number']:03d}_{keyword}.mp3"

    custom_prompt = load_scene_prompt(scene['number'])
    if custom_prompt:
        focus_topic = custom_prompt
        prompt_type = "custom"
    else:
        focus_topic = f"{BOOK_TITLE} - {scene['location']}: {scene['title']}"
        prompt_type = "fallback"

    source_ids = resolve_source_ids(scene)
    src_info = f"{len(source_ids)} sources" if source_ids else "todas sources (default)"

    log(f"   Prompt: {prompt_type} ({len(focus_topic)} chars) | {src_info}")

    session_stats['current_scene'] = scene['number']
    session_stats['scenes_attempted'] += 1

    result_entry = {
        'cena': scene['number'],
        'titulo': scene['title'],
        'prompt_type': prompt_type,
        'prompt_chars': len(focus_topic),
        'status': 'failed',
        'timestamp': datetime.now().isoformat(),
    }

    for attempt in range(1, MAX_RETRIES + 1):
        if shutdown_requested:
            result_entry['status'] = 'interrupted'
            session_results.append(result_entry)
            return False

        if attempt > 1:
            wait = 30 * attempt
            log(f"   Tentativa {attempt}/{MAX_RETRIES} (aguardando {wait}s)...")
            time.sleep(wait)

        log(f"   Disparando criacao...")
        artifact_id = create_audio(focus_topic, source_ids)
        if not artifact_id:
            continue

        log(f"   Artifact: {artifact_id[:12]}... (fire-and-forget)")
        result_entry['artifact_id'] = artifact_id

        audio_entry = {
            'arquivo': filename,
            'cena_numero': scene['number'],
            'titulo_completo': scene['title'],
            'localizacao': scene['location'],
            'artifact_id': artifact_id,
            'data_geracao': datetime.now().isoformat(),
            'focus_topic': focus_topic[:200] + '...' if len(focus_topic) > 200 else focus_topic,
            'prompt_type': prompt_type,
            'source_ids': source_ids,
            'status': 'created',
        }
        save_metadata(audio_entry)

        result_entry['status'] = 'created'
        session_results.append(result_entry)

        session_stats['scenes_created'] += 1
        return True

    session_results.append(result_entry)
    session_stats['scenes_failed'] += 1
    return False


# ── Download posterior ───────────────────────────────────────────────

def scan_created_artifacts() -> List[Dict]:
    metadata_file = QV_DIR / "audios" / "metadata.json"
    if not metadata_file.exists():
        return []
    try:
        data = json.loads(metadata_file.read_text(encoding='utf-8'))
        return [
            audio for audio in data.get('audios', [])
            if audio.get('status') == 'created' and audio.get('artifact_id')
        ]
    except Exception:
        return []


def download_pending_audios():
    log("Escaneando artifacts pendentes de download...")
    pending = scan_created_artifacts()

    if not pending:
        log("Nenhum artifact pendente de download.")
        return 0

    log(f"Encontrados {len(pending)} artifacts para baixar")
    print()

    downloaded = 0
    failed = 0
    still_processing = 0

    for i, audio in enumerate(pending, 1):
        if shutdown_requested:
            break

        artifact_id = audio['artifact_id']

        log(f"[{i}/{len(pending)}] cena {audio['cena_numero']}: {audio['titulo_completo'][:45]}")

        status = poll_status(artifact_id)

        if status == "completed":
            output_path = QV_DIR / "audios" / audio['arquivo']
            if download_audio(artifact_id, output_path):
                audio['status'] = 'downloaded'
                audio['output_path'] = str(output_path)
                audio['tamanho_bytes'] = output_path.stat().st_size
                save_metadata(audio)
                downloaded += 1
            else:
                failed += 1
        elif status == "failed":
            log(f"   Processamento falhou no servidor — remover e recriar")
            audio['status'] = 'server_failed'
            save_metadata(audio)
            failed += 1
        elif status in ("in_progress", None):
            log(f"   Ainda processando (status: {status})")
            still_processing += 1
        else:
            log(f"   Status desconhecido: {status}")
            still_processing += 1

    print()
    print("=" * 60)
    print("  RESUMO DO DOWNLOAD")
    print("=" * 60)
    print(f"  Baixados:          {downloaded}")
    print(f"  Ainda processando: {still_processing}")
    print(f"  Falhas:            {failed}")
    print("=" * 60)

    return 0 if failed == 0 else 1


def print_summary():
    stats = session_stats
    elapsed = ""
    if stats['started_at']:
        delta = datetime.now() - stats['started_at']
        hours = delta.seconds // 3600
        mins = (delta.seconds % 3600) // 60
        elapsed = f" ({hours}h{mins:02d}m)"

    print()
    print("=" * 60)
    print(f"  RESUMO DA SESSAO{elapsed}")
    print("=" * 60)
    print(f"  Cenas tentadas:    {stats['scenes_attempted']}")
    print(f"  Criadas OK:        {stats['scenes_created']}")
    print(f"  Falhas:            {stats['scenes_failed']}")
    print("=" * 60)


def print_progress_bar(done: int, total: int, width: int = 40):
    pct = done / total if total > 0 else 0
    filled = int(width * pct)
    bar = "#" * filled + "." * (width - filled)
    print(f"  [{bar}] {done}/{total} ({pct:.1%})")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Quo Vadis Audio Runner')
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar plano sem executar')
    parser.add_argument('--max-scenes', type=int, default=0,
                        help='Limitar numero de cenas (0 = todas)')
    parser.add_argument('--parte', type=int, default=-1,
                        help='Processar apenas cenas de uma parte: 1, 2, 3 ou 0 (Epilogo)')
    parser.add_argument('--no-wait', action='store_true',
                        help='Sem intervalo entre cenas (apenas para testes)')
    parser.add_argument('--download', action='store_true',
                        help='Baixar audios ja criados (status=created)')
    args = parser.parse_args()

    print()
    print("  Quo Vadis Audio Runner (fire-and-forget)")
    print("  ========================================")
    print(f"  {BOOK_TITLE} — {BOOK_AUTHOR}")
    print("  Dispara criacao e segue | ~2min por cena")
    print()

    log("Verificando autenticacao nlm...")
    if not check_auth():
        log("ERRO: nlm nao autenticado. Execute: nlm login --profile default")
        return 1

    log("Auth OK")

    if args.download:
        return download_pending_audios()

    scenes_file = QV_DIR / "01_cenas_identificadas.md"
    if not scenes_file.exists():
        log(f"Arquivo nao encontrado: {scenes_file}")
        return 1

    all_scenes = extract_scenes(scenes_file)
    if not all_scenes:
        log("Nenhuma cena encontrada no arquivo")
        return 1

    if len(all_scenes) != TOTAL_SCENES:
        log(f"AVISO: esperava {TOTAL_SCENES} cenas, encontrei {len(all_scenes)}")

    # Filtrar por parte se solicitado
    if args.parte in PARTE_RANGES:
        start, end = PARTE_RANGES[args.parte]
        all_scenes = [s for s in all_scenes if start <= s['number'] <= end]
        pname = {0: 'Epilogo', 1: 'Primeira', 2: 'Segunda', 3: 'Terceira'}[args.parte]
        log(f"Filtro: {pname} Parte (cenas {start}-{end})")
    elif args.parte != -1:
        log(f"Parte invalida: {args.parte} (use 1, 2, 3 ou 0)")
        return 1

    processed = get_processed_scenes()
    pending = [s for s in all_scenes if s['number'] not in processed]

    total = len(all_scenes)
    done = len(processed)

    print()
    log("Estado atual:")
    print(f"  Cenas totais:      {total}")
    print(f"  Ja processadas:    {done}")
    print(f"  Pendentes:         {len(pending)}")
    print()
    print_progress_bar(done, TOTAL_SCENES)
    print()

    if not pending:
        log("Todas as cenas ja foram processadas!")
        return 0

    queue = pending
    if args.max_scenes > 0:
        queue = queue[:args.max_scenes]

    interval = 0 if args.no_wait else INTERVAL_SECONDS
    est_minutes = len(queue) * (interval // 60 + 1)
    est_hours = est_minutes / 60

    prompts_found = sum(1 for s in queue if load_scene_prompt(s['number']))

    log(f"Fila: {len(queue)} cenas | Prompts custom: {prompts_found}/{len(queue)} | Estimativa: ~{est_hours:.1f}h")
    print()

    if args.dry_run:
        log("PLANO DE EXECUCAO (dry-run):")
        print()
        for i, scene in enumerate(queue, 1):
            has_prompt = "P" if load_scene_prompt(scene['number']) else "-"
            srcs = resolve_source_ids(scene)
            src_tag = f"{len(srcs)}s" if srcs else "all"
            print(f"  {i:3d}. [{has_prompt}][{src_tag:>3}] cena {scene['number']:3d} - {scene['title'][:50]}")
        print()
        print("  Legenda: P=prompt customizado, -=fallback | Ns=N sources mapeadas, all=todas")
        print()
        log(f"Total: {len(queue)} cenas")
        return 0

    session_stats['started_at'] = datetime.now()

    for i, scene in enumerate(queue, 1):
        if shutdown_requested:
            break

        remaining = len(queue) - i
        log(f"[{i}/{len(queue)}] cena {scene['number']}: {scene['title'][:50]}")

        success = process_scene(scene)

        if success:
            log(f"   OK ({session_stats['scenes_created']}/{len(queue)} criadas, {remaining} restantes)")
        else:
            if not shutdown_requested:
                log(f"   FALHOU (continuando...)")

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
