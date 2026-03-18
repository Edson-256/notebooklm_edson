#!/usr/bin/env python3
"""
Ben-Hur Audio Runner (fire-and-forget)
Dispara criação dos áudios no NotebookLM sem esperar processamento.
Adaptado do Shakespeare Runner v3 para o projeto Ben-Hur (81 cenas).

Uso:
    python3 projetos/ben-hur/ben_hur_runner.py              # Fire-and-forget
    python3 projetos/ben-hur/ben_hur_runner.py --dry-run    # Mostrar plano
    python3 projetos/ben-hur/ben_hur_runner.py --max-scenes 5
    python3 projetos/ben-hur/ben_hur_runner.py --download   # Baixar áudios prontos
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
BENHUR_DIR = Path(__file__).parent                 # projetos/ben-hur/
LOGS_DIR = PROJECT_DIR / "logs"
NOTEBOOK_ID = "1ecdbff9-2511-4a7f-99a0-10d3eadc1042"
SOURCE_ID = "37da47f1-7f92-4c3c-b831-faab6e7cdc3d"
PROFILE = "default"
INTERVAL_SECONDS = 120  # 2 minutos entre cenas (fire-and-forget)
POLL_INTERVAL = 30      # 30 segundos entre checks de status (modo --download)
MAX_WAIT_MINUTES = 30   # Timeout para aguardar áudio pronto (modo --download)
MAX_RETRIES = 3         # Tentativas por cena
MAX_FOCUS_CHARS = 2500  # Limite NLM Pro para --focus

BOOK_TITLE = "Ben-Hur: A Tale of the Christ"
BOOK_AUTHOR = "Lew Wallace"
BOOK_SLUG = "ben_hur"

# ── Estado global ──────────────────────────────────────────────────────
shutdown_requested = False
session_stats = {
    'started_at': None,
    'scenes_attempted': 0,
    'scenes_created': 0,
    'scenes_failed': 0,
    'current_scene': None,
}
session_results = []  # Log detalhado de cada cena processada


def handle_shutdown(signum, frame):
    """Handler para Ctrl+C — sai no próximo ponto seguro."""
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
                 'para', 'entre', 'com', 'no', 'na', 'nos', 'nas', 'ao', 'à'}
    words = re.findall(r'\w+', title.lower())
    words = [unicodedata.normalize('NFKD', w).encode('ascii', 'ignore').decode('ascii')
             for w in words]
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return '_'.join(keywords[:2])[:30]


# ── Prompts customizados ──────────────────────────────────────────────

def load_scene_prompt(scene_number: int) -> Optional[str]:
    """Carrega prompt customizado da cena em prompts_cenas/."""
    prompts_dir = BENHUR_DIR / "prompts_cenas"
    if not prompts_dir.exists():
        return None

    prefix = f"{scene_number:02d}_"
    for p in prompts_dir.iterdir():
        if p.name.startswith(prefix) and p.suffix == '.md':
            content = p.read_text(encoding='utf-8').strip()
            if len(content) > MAX_FOCUS_CHARS:
                content = content[:MAX_FOCUS_CHARS - 3] + "..."
            return content
    return None


# ── Extração de cenas ──────────────────────────────────────────────────

def extract_scenes(filepath: Path) -> List[Dict]:
    content = filepath.read_text(encoding='utf-8')
    pattern = (
        r'### (\d+)\.\s+(.+?)\n'
        r'\s*-\s+\*\*Localização:\*\*\s+(.+?)\n'
        r'\s*-\s+\*\*Resumo:\*\*\s+(.+?)\n'
        r'\s*-\s+\*\*Justificativa.*?:\*\*\s+(.+?)(?=\n###|\Z)'
    )
    scenes = []
    for m in re.finditer(pattern, content, re.DOTALL):
        scenes.append({
            'number': int(m.group(1)),
            'title': m.group(2).strip(),
            'location': m.group(3).strip(),
            'summary': m.group(4).strip(),
            'justification': m.group(5).strip(),
        })
    return scenes


# ── Progresso real ─────────────────────────────────────────────────────

def get_processed_scenes() -> set:
    """Retorna set de números de cenas já criadas ou baixadas."""
    metadata_file = BENHUR_DIR / "audios" / "metadata.json"
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
    """Executa comando nlm."""
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


def create_audio(focus_topic: str) -> Optional[str]:
    """Cria áudio e retorna artifact_id. Sempre usa source_id do Ben-Hur."""
    try:
        cmd = [
            "create", "audio", NOTEBOOK_ID,
            "--format", "deep_dive",
            "--language", "pt-BR",
            "--length", "long",
            "--focus", focus_topic,
            "--profile", PROFILE,
            "--confirm",
            "--source-ids", SOURCE_ID,
        ]

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
    """Verifica status de um artifact."""
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
    """Aguarda áudio ficar pronto com polling."""
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
    """Baixa o áudio gerado."""
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
    """Salva/atualiza metadata.json com uma nova entrada."""
    audios_dir = BENHUR_DIR / "audios"
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
        'source_id': SOURCE_ID,
        'total_cenas': len(merged),
        'ultima_atualizacao': datetime.now().isoformat(),
        'audios': merged,
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )


def save_session_log():
    """Salva log da sessão em JSON para auditoria."""
    if not session_results:
        return
    LOGS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = LOGS_DIR / f"benhur_session_{ts}.json"
    log_data = {
        'project': 'ben-hur',
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
    """Fire-and-forget: cria áudio, salva artifact_id, segue."""
    keyword = extract_keyword(scene['title'])
    filename = f"bh_{scene['number']:02d}_{keyword}.mp3"

    custom_prompt = load_scene_prompt(scene['number'])
    if custom_prompt:
        focus_topic = custom_prompt
        prompt_type = "custom"
    else:
        focus_topic = f"{BOOK_TITLE} - {scene['location']}: {scene['title']}"
        prompt_type = "fallback"

    log(f"   Prompt: {prompt_type} ({len(focus_topic)} chars)")

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
        artifact_id = create_audio(focus_topic)
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
            'source_id': SOURCE_ID,
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
    """Retorna áudios com status 'created' pendentes de download."""
    metadata_file = BENHUR_DIR / "audios" / "metadata.json"
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
    """Modo --download: baixa todos os áudios com status 'created' que já estejam prontos."""
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
            output_path = BENHUR_DIR / "audios" / audio['arquivo']
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
    """Imprime resumo da sessão."""
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
    parser = argparse.ArgumentParser(description='Ben-Hur Audio Runner')
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar plano sem executar')
    parser.add_argument('--max-scenes', type=int, default=0,
                        help='Limitar numero de cenas (0 = todas)')
    parser.add_argument('--livro', type=int, default=0,
                        help='Processar apenas cenas de um livro (1-8)')
    parser.add_argument('--no-wait', action='store_true',
                        help='Sem intervalo entre cenas (apenas para testes)')
    parser.add_argument('--download', action='store_true',
                        help='Baixar audios ja criados (status=created)')
    args = parser.parse_args()

    print()
    print("  Ben-Hur Audio Runner (fire-and-forget)")
    print("  =======================================")
    print(f"  {BOOK_TITLE} — {BOOK_AUTHOR}")
    print("  Dispara criacao e segue | ~2min por cena")
    print()

    # Verificar autenticação
    log("Verificando autenticacao nlm...")
    if not check_auth():
        log("ERRO: nlm nao autenticado. Execute: nlm login --profile default")
        return 1

    log("Auth OK")

    # Modo download
    if args.download:
        return download_pending_audios()

    # Extrair cenas
    scenes_file = BENHUR_DIR / "01_cenas_identificadas.md"
    if not scenes_file.exists():
        log(f"Arquivo nao encontrado: {scenes_file}")
        return 1

    all_scenes = extract_scenes(scenes_file)
    if not all_scenes:
        log("Nenhuma cena encontrada no arquivo")
        return 1

    # Filtrar por livro se solicitado
    LIVRO_RANGES = {
        1: (1, 14), 2: (15, 21), 3: (22, 27), 4: (28, 44),
        5: (45, 60), 6: (61, 66), 7: (67, 71), 8: (72, 81),
    }
    if args.livro:
        if args.livro not in LIVRO_RANGES:
            log(f"Livro invalido: {args.livro} (use 1-8)")
            return 1
        start, end = LIVRO_RANGES[args.livro]
        all_scenes = [s for s in all_scenes if start <= s['number'] <= end]
        log(f"Filtro: Livro {args.livro} (cenas {start}-{end})")

    # Determinar pendentes
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
    print_progress_bar(done, 81)  # sempre mostra progresso sobre o total de 81
    print()

    if not pending:
        log("Todas as cenas ja foram processadas!")
        return 0

    queue = pending
    if args.max_scenes > 0:
        queue = queue[:args.max_scenes]

    # Estimar tempo
    interval = 0 if args.no_wait else INTERVAL_SECONDS
    est_minutes = len(queue) * (interval // 60 + 1)
    est_hours = est_minutes / 60

    # Contar prompts customizados
    prompts_found = sum(1 for s in queue if load_scene_prompt(s['number']))

    log(f"Fila: {len(queue)} cenas | Prompts custom: {prompts_found}/{len(queue)} | Estimativa: ~{est_hours:.1f}h")
    print()

    if args.dry_run:
        log("PLANO DE EXECUCAO (dry-run):")
        print()
        for i, scene in enumerate(queue, 1):
            has_prompt = "P" if load_scene_prompt(scene['number']) else "-"
            print(f"  {i:3d}. [{has_prompt}] cena {scene['number']:2d} - {scene['title'][:55]}")
        print()
        print("  Legenda: P=prompt customizado, -=fallback")
        print()
        log(f"Total: {len(queue)} cenas")
        return 0

    # Processar
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
