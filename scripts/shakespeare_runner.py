#!/usr/bin/env python3
"""
Shakespeare Audio Runner (v3 — fire-and-forget)
Dispara criação dos áudios no NotebookLM sem esperar processamento.
Modo rápido: ~2 min por cena (vs ~20 min na v2 que fazia wait+download).

Uso:
    python3 scripts/shakespeare_runner.py              # Fire-and-forget
    python3 scripts/shakespeare_runner.py --dry-run    # Mostrar plano
    python3 scripts/shakespeare_runner.py --max-scenes 5
    python3 scripts/shakespeare_runner.py --obra hamlet
    python3 scripts/shakespeare_runner.py --download   # Baixar áudios prontos
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
PROJECT_DIR = Path(__file__).parent.parent
SHAKESPEARE_DIR = PROJECT_DIR / "projetos" / "w_shakespeare"
LOGS_DIR = PROJECT_DIR / "logs"
NOTEBOOK_ID = "62400b1d-e3bd-45d2-8428-d2d8d6b7128d"
PROFILE = "default"
INTERVAL_SECONDS = 120  # 2 minutos entre cenas (fire-and-forget)
POLL_INTERVAL = 30      # 30 segundos entre checks de status (modo --download)
MAX_WAIT_MINUTES = 30   # Timeout para aguardar áudio pronto (modo --download)
MAX_RETRIES = 3         # Tentativas por cena
MAX_FOCUS_CHARS = 2500  # Limite NLM Pro para --focus

# ── Source IDs ─────────────────────────────────────────────────────────
# Mapeamento: diretório da obra → source_id no notebook Shakespeare
SOURCE_ID_MAP = {
    'a_midsummer_nights_dream': '6c222d1e-fed8-4268-b5b6-be6b55234d7f',
    'alls_well_that_ends_well': '663d6327-818d-4f2e-858e-e1c960190cb2',
    'antony_and_cleopatra': '317c0f1b-9229-4925-8da6-001f85f60868',
    'as_you_like_it': '6e85b783-b43c-426f-9436-95a23df8a3bc',
    'coriolanus': 'c12faae3-c7f5-4a94-ac3b-36eb1b894f11',
    'cymbeline': 'fec24009-60a2-454d-9e9a-7b3c765af260',
    'hamlet': '523f75db-6ff4-4591-84d1-a968d6d5f700',
    'julius_caesar': '9141e180-c437-4ef2-883c-dfc4350bf0a8',
    'king_lear': '40ab96fe-8af6-43e8-ba45-601b07c5025d',
    'loves_labours_lost': '691aa402-913d-4cfd-9af1-c8d2d4aa81f9',
    'macbeth': '20570f58-69c0-4193-ab9b-41321efc808a',
    'measure_for_measure': '41567869-ebb1-4daa-b70b-300e8f33a75a',
    'much_ado_about_nothing': 'fe7c3ffd-e4f3-4be0-9fe0-579e8120d3be',
    'othello': '40fca337-a3f3-4106-8fe7-a29737c78557',
    'pericles': '2eccf318-ab7d-480a-92af-0ce932e3391f',
    'romeo_and_juliet': 'cdc366df-cdf4-47bf-adfd-6484434cb2b8',
    'sonnets': '930a83ee-e9f4-4730-88f0-e7e9508322a6',
    'the_comedy_of_errors': '928a4ece-1347-4c65-b378-de6cd10e02b3',
    'the_merchant_of_venice': '0235815d-58e4-4885-ba16-d973f7bd385b',
    'the_merry_wives_of_windsor': '85ad991d-2976-40f4-b486-eda1496c8cce',
    'the_rape_of_lucrece': '45fc0662-b75a-41d1-8326-dd29f4eb67b8',
    'the_taming_of_the_shrew': '3ecefd3a-31ec-48d0-92e7-41a66bdfe491',
    'the_tempest': '64c5dab6-b866-4f3b-a291-bdc320b048f8',
    'the_two_gentlemen_of_verona': '7cd6a972-3fb2-47ed-9f2f-2c3d90a064bd',
    'the_two_noble_kinsmen': '301cfe24-af06-4739-bcce-9e78b689db93',
    'the_winters_tale': '57728e3d-2be2-4990-ad85-ca1db354b989',
    'timon_of_athens': '43f3c6ec-c987-4769-9cb0-7d294aac09c9',
    'titus_andronicus': '17b8d379-e394-4acc-b5b9-99ec9c64d16a',
    'troilus_and_cressida': '8cbaafda-117f-4333-bda5-11b1d989869b',
    'twelfth_night': '196e25a2-8d4a-4a5b-b0e1-c5eacfd176ea',
    'venus_and_adonis': 'f50a0cb8-bf4e-413a-b7ff-e2a47350165d',
    'history_of_henry_iv_part_i': 'b4709f1f-0ac7-41b8-b6bb-bce7dab38aa3',
    'history_of_henry_iv_part_ii': 'dacb70ae-25af-45a8-a59c-11142275614c',
    'history_of_henry_v': 'db28eb9f-bd35-4836-86cc-590946c8d2c1',
    'history_of_henry_vi_part_i': '6af74aa5-34fb-438b-9646-e8be192b05b8',
    'history_of_henry_vi_part_ii': 'bde0aee6-6a60-4832-976e-49dd5e4adb3f',
    'history_of_henry_vi_part_iii': 'd8b8c2bd-806f-4f7e-9baa-f46f6cb5280f',
    'history_of_henry_viii': '9e8994c3-863b-41f1-8860-117820714efc',
    'history_of_king_john': 'fd1e7f91-d707-4ded-a6cb-3fff35135843',
    'history_of_richard_ii': '509fd4ef-c06a-406c-959d-510e5f3c8e7a',
    'history_of_richard_iii': '06f628ac-15d8-40c7-ab1b-a62354eacb3e',
}

# Source ID da metodologia Olavo de Carvalho (sempre incluído)
METODOLOGIA_SOURCE_ID = '52edb813-6935-4123-bf35-4137283eb8dc'

# ── Estado global ──────────────────────────────────────────────────────
shutdown_requested = False
session_stats = {
    'started_at': None,
    'scenes_attempted': 0,
    'scenes_created': 0,
    'scenes_failed': 0,
    'current_obra': None,
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

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')


def extract_keyword(title: str) -> str:
    stopwords = {'o', 'a', 'os', 'as', 'do', 'da', 'dos', 'das', 'de', 'e',
                 'para', 'entre', 'com', 'no', 'na', 'nos', 'nas', 'ao', 'à'}
    words = re.findall(r'\w+', title.lower())
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return '_'.join(keywords[:2])[:30]


OBRA_SLUG_MAP = {
    'a_midsummer_nights_dream': 'midsummer_dream',
    'alls_well_that_ends_well': 'alls_well',
    'antony_and_cleopatra': 'antony_cleopatra',
    'as_you_like_it': 'as_you_like_it',
    'the_comedy_of_errors': 'comedy_errors',
    'the_merchant_of_venice': 'merchant_venice',
    'the_merry_wives_of_windsor': 'merry_wives',
    'the_taming_of_the_shrew': 'taming_shrew',
    'the_two_gentlemen_of_verona': 'two_gentlemen',
    'the_two_noble_kinsmen': 'two_kinsmen',
    'the_winters_tale': 'winters_tale',
    'history_of_henry_iv_part_i': 'henry4_p1',
    'history_of_henry_iv_part_ii': 'henry4_p2',
    'history_of_henry_v': 'henry5',
    'history_of_henry_vi_part_i': 'henry6_p1',
    'history_of_henry_vi_part_ii': 'henry6_p2',
    'history_of_henry_vi_part_iii': 'henry6_p3',
    'history_of_henry_viii': 'henry8',
    'history_of_king_john': 'king_john',
    'history_of_richard_ii': 'richard2',
    'history_of_richard_iii': 'richard3',
    'romeo_and_juliet': 'romeo_juliet',
    'julius_caesar': 'julius_caesar',
    'much_ado_about_nothing': 'much_ado',
    'loves_labours_lost': 'loves_labour',
    'measure_for_measure': 'measure_measure',
    'the_rape_of_lucrece': 'lucrece',
    'the_tempest': 'tempest',
    'timon_of_athens': 'timon_athens',
    'titus_andronicus': 'titus_andronicus',
    'troilus_and_cressida': 'troilus_cressida',
    'twelfth_night': 'twelfth_night',
    'venus_and_adonis': 'venus_adonis',
}


# ── Prompts customizados ──────────────────────────────────────────────

def load_scene_prompt(obra_dir: Path, scene_number: int) -> Optional[str]:
    """Carrega prompt customizado da cena em prompts_cenas/."""
    prompts_dir = obra_dir / "prompts_cenas"
    if not prompts_dir.exists():
        return None

    # Procura arquivo que começa com o número da cena (ex: 04_titulo.md)
    prefix = f"{scene_number:02d}_"
    for p in prompts_dir.iterdir():
        if p.name.startswith(prefix) and p.suffix == '.md':
            content = p.read_text(encoding='utf-8').strip()
            # Truncar se exceder limite NLM Pro
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

def get_processed_scenes(obra_dir: Path) -> set:
    """Retorna set de números de cenas já criadas ou baixadas (não precisa reprocessar)."""
    metadata_file = obra_dir / "audios" / "metadata.json"
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


def scan_all_obras(filter_obra: Optional[str] = None) -> List[Dict]:
    """Escaneia todas as obras e retorna estado real."""
    obras = []
    for obra_dir in sorted(SHAKESPEARE_DIR.iterdir()):
        if not obra_dir.is_dir():
            continue
        if filter_obra and obra_dir.name != filter_obra:
            continue

        scenes_file = obra_dir / "01_cenas_identificadas.md"
        if not scenes_file.exists():
            continue

        all_scenes = extract_scenes(scenes_file)
        processed = get_processed_scenes(obra_dir)
        pending = [s for s in all_scenes if s['number'] not in processed]

        source_id = SOURCE_ID_MAP.get(obra_dir.name)

        obras.append({
            'dir': obra_dir,
            'name': obra_dir.name,
            'title': obra_dir.name.replace('_', ' ').title(),
            'slug': OBRA_SLUG_MAP.get(obra_dir.name, obra_dir.name),
            'source_id': source_id,
            'total': len(all_scenes),
            'processed': len(processed),
            'pending_scenes': pending,
        })
    return obras


def build_round_robin_queue(obras: List[Dict]) -> List[Dict]:
    """Gera fila de cenas em round-robin entre obras."""
    queue = []
    pending_lists = {o['name']: list(o['pending_scenes']) for o in obras if o['pending_scenes']}
    obra_info = {o['name']: o for o in obras}

    while pending_lists:
        for obra_name in sorted(pending_lists.keys()):
            scenes = pending_lists[obra_name]
            if not scenes:
                continue
            scene = scenes.pop(0)
            info = obra_info[obra_name]
            queue.append({
                'obra_dir': info['dir'],
                'obra_name': obra_name,
                'obra_title': info['title'],
                'obra_slug': info['slug'],
                'source_id': info['source_id'],
                'scene': scene,
            })
        pending_lists = {k: v for k, v in pending_lists.items() if v}

    return queue


# ── Geração de áudio ──────────────────────────────────────────────────

def run_nlm(args: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Executa comando nlm."""
    cmd = ["nlm"] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def check_auth() -> bool:
    try:
        # Garantir que o perfil correto está ativo (alguns subcomandos não aceitam --profile)
        run_nlm(["login", "switch", PROFILE], timeout=15)
        result = run_nlm(["login", "--check", "--profile", PROFILE], timeout=30)
        return result.returncode == 0
    except Exception as e:
        log(f"Erro ao verificar auth: {e}")
        return False


def create_audio(focus_topic: str, source_id: Optional[str] = None) -> Optional[str]:
    """Cria áudio e retorna artifact_id. Usa --source-ids se disponível."""
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

        # Focar no source da obra + metodologia COF
        if source_id:
            source_ids = f"{source_id},{METODOLOGIA_SOURCE_ID}"
            cmd.extend(["--source-ids", source_ids])

        result = run_nlm(cmd, timeout=180)

        if result.returncode != 0:
            # Log completo do erro para diagnóstico
            stderr = result.stderr.strip()
            stdout = result.stdout.strip()
            if stderr:
                log(f"   nlm stderr: {stderr[:500]}")
            if stdout:
                log(f"   nlm stdout: {stdout[:300]}")
            return None

        output = result.stdout

        # Regex flexível para capturar artifact ID (compatível com múltiplos formatos)
        match = re.search(r'(?:Artifact|Audio)\s*(?:ID)?[:\s]+([a-f0-9-]{20,})', output, re.IGNORECASE)
        if match:
            return match.group(1)

        # Fallback: qualquer UUID no output
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
    max_polls = MAX_WAIT_MINUTES * 2  # check a cada 30s

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

def save_metadata(obra_dir: Path, obra_slug: str, book_title: str, audio_entry: Dict):
    """Salva/atualiza metadata.json de uma obra com uma nova entrada."""
    audios_dir = obra_dir / "audios"
    audios_dir.mkdir(exist_ok=True)
    metadata_path = audios_dir / "metadata.json"

    existing_audios = []
    if metadata_path.exists():
        try:
            data = json.loads(metadata_path.read_text(encoding='utf-8'))
            existing_audios = data.get('audios', [])
        except Exception:
            pass

    # Merge por cena_numero
    by_num = {a['cena_numero']: a for a in existing_audios}
    by_num[audio_entry['cena_numero']] = audio_entry
    merged = sorted(by_num.values(), key=lambda a: a['cena_numero'])

    metadata = {
        'obra': book_title,
        'obra_slug': obra_slug,
        'obra_dir': obra_dir.name,
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
    """Salva log da sessão em JSON para auditoria."""
    if not session_results:
        return
    LOGS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_path = LOGS_DIR / f"session_{ts}.json"
    log_data = {
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

def process_scene(item: Dict) -> bool:
    """Fire-and-forget: cria áudio, salva artifact_id, segue. Retorna True se criado."""
    scene = item['scene']
    obra_dir = item['obra_dir']
    obra_slug = item['obra_slug']
    obra_title = item['obra_title']
    source_id = item.get('source_id')

    keyword = extract_keyword(scene['title'])
    filename = f"ws_{obra_slug}_{scene['number']:02d}_{keyword}.mp3"

    # Carregar prompt customizado ou fallback para focus_topic simples
    custom_prompt = load_scene_prompt(obra_dir, scene['number'])
    if custom_prompt:
        focus_topic = custom_prompt
        prompt_type = "custom"
    else:
        focus_topic = f"{obra_title} - {scene['location']}: {scene['title']}"
        prompt_type = "fallback"

    log(f"   Prompt: {prompt_type} ({len(focus_topic)} chars)")
    if source_id:
        log(f"   Source: {source_id[:12]}... + metodologia COF")

    session_stats['current_obra'] = item['obra_name']
    session_stats['current_scene'] = scene['number']
    session_stats['scenes_attempted'] += 1

    result_entry = {
        'obra': item['obra_name'],
        'cena': scene['number'],
        'titulo': scene['title'],
        'prompt_type': prompt_type,
        'prompt_chars': len(focus_topic),
        'source_id': source_id,
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

        # Fire-and-forget: apenas criar áudio
        log(f"   Disparando criacao...")
        artifact_id = create_audio(focus_topic, source_id)
        if not artifact_id:
            continue

        log(f"   Artifact: {artifact_id[:12]}... (fire-and-forget)")
        result_entry['artifact_id'] = artifact_id

        # Salvar metadata com status 'created' (download posterior)
        (obra_dir / "audios").mkdir(exist_ok=True)
        audio_entry = {
            'arquivo': filename,
            'cena_numero': scene['number'],
            'titulo_completo': scene['title'],
            'localizacao': scene['location'],
            'artifact_id': artifact_id,
            'data_geracao': datetime.now().isoformat(),
            'focus_topic': focus_topic[:200] + '...' if len(focus_topic) > 200 else focus_topic,
            'prompt_type': prompt_type,
            'source_id': source_id,
            'status': 'created',
        }
        save_metadata(obra_dir, obra_slug, obra_title, audio_entry)

        result_entry['status'] = 'created'
        session_results.append(result_entry)

        session_stats['scenes_created'] += 1
        return True

    # Todas as tentativas falharam
    session_results.append(result_entry)
    session_stats['scenes_failed'] += 1
    return False


# ── Download posterior ───────────────────────────────────────────────

def scan_created_artifacts() -> List[Dict]:
    """Escaneia metadata de todas as obras e retorna áudios com status 'created'."""
    pending = []
    for obra_dir in sorted(SHAKESPEARE_DIR.iterdir()):
        if not obra_dir.is_dir():
            continue
        metadata_file = obra_dir / "audios" / "metadata.json"
        if not metadata_file.exists():
            continue
        try:
            data = json.loads(metadata_file.read_text(encoding='utf-8'))
            for audio in data.get('audios', []):
                if audio.get('status') == 'created' and audio.get('artifact_id'):
                    pending.append({
                        'obra_dir': obra_dir,
                        'obra_name': obra_dir.name,
                        'obra_slug': data.get('obra_slug', obra_dir.name),
                        'obra_title': data.get('obra', obra_dir.name),
                        'audio': audio,
                    })
        except Exception:
            continue
    return pending


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

    for i, item in enumerate(pending, 1):
        if shutdown_requested:
            break

        audio = item['audio']
        artifact_id = audio['artifact_id']
        obra_dir = item['obra_dir']

        log(f"[{i}/{len(pending)}] {item['obra_name']} | cena {audio['cena_numero']}: {audio['titulo_completo'][:40]}")

        # Verificar status no servidor
        status = poll_status(artifact_id)

        if status == "completed":
            output_path = obra_dir / "audios" / audio['arquivo']
            if download_audio(artifact_id, output_path):
                # Atualizar metadata para 'downloaded'
                audio['status'] = 'downloaded'
                audio['output_path'] = str(output_path)
                audio['tamanho_bytes'] = output_path.stat().st_size
                save_metadata(obra_dir, item['obra_slug'], item['obra_title'], audio)
                downloaded += 1
            else:
                failed += 1
        elif status == "failed":
            log(f"   Processamento falhou no servidor — remover e recriar")
            audio['status'] = 'server_failed'
            save_metadata(obra_dir, item['obra_slug'], item['obra_title'], audio)
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
    """Imprime barra de progresso."""
    pct = done / total if total > 0 else 0
    filled = int(width * pct)
    bar = "#" * filled + "." * (width - filled)
    print(f"  [{bar}] {done}/{total} ({pct:.1%})")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Shakespeare Audio Runner')
    parser.add_argument('--dry-run', action='store_true',
                        help='Mostrar plano sem executar')
    parser.add_argument('--max-scenes', type=int, default=0,
                        help='Limitar numero de cenas (0 = todas)')
    parser.add_argument('--obra', type=str, default=None,
                        help='Processar apenas uma obra')
    parser.add_argument('--no-wait', action='store_true',
                        help='Sem intervalo entre cenas (apenas para testes)')
    parser.add_argument('--download', action='store_true',
                        help='Baixar audios ja criados (status=created)')
    args = parser.parse_args()

    print()
    print("  Shakespeare Audio Runner v3 (fire-and-forget)")
    print("  =============================================")
    print("  Dispara criacao e segue | ~2min por cena")
    print()

    # Verificar autenticação
    log("Verificando autenticacao nlm...")
    if not check_auth():
        log("ERRO: nlm nao autenticado. Execute: nlm login --profile default")
        return 1

    log("Auth OK")

    # Modo download: baixar áudios já criados
    if args.download:
        return download_pending_audios()

    # Escanear estado real
    log("Escaneando estado real das obras...")
    obras = scan_all_obras(filter_obra=args.obra)

    if not obras:
        if args.obra:
            log(f"Obra '{args.obra}' nao encontrada ou sem cenas")
        else:
            log("Nenhuma obra encontrada")
        return 1

    # Verificar source mapping
    missing_sources = [o['name'] for o in obras if not o['source_id']]
    if missing_sources:
        log(f"AVISO: {len(missing_sources)} obras sem source_id mapeado (usarao notebook inteiro)")

    total_scenes = sum(o['total'] for o in obras)
    total_processed = sum(o['processed'] for o in obras)
    total_pending = sum(len(o['pending_scenes']) for o in obras)
    obras_with_pending = [o for o in obras if o['pending_scenes']]

    print()
    log("Estado atual:")
    print(f"  Obras totais:      {len(obras)}")
    print(f"  Cenas totais:      {total_scenes}")
    print(f"  Ja processadas:    {total_processed}")
    print(f"  Pendentes:         {total_pending}")
    print(f"  Obras pendentes:   {len(obras_with_pending)}")
    print()
    print_progress_bar(total_processed, total_scenes)
    print()

    if total_pending == 0:
        log("Todas as cenas ja foram processadas!")
        return 0

    # Gerar fila round-robin
    queue = build_round_robin_queue(obras_with_pending)

    if args.max_scenes > 0:
        queue = queue[:args.max_scenes]

    # Estimar tempo
    interval = 0 if args.no_wait else INTERVAL_SECONDS
    est_minutes = len(queue) * (interval // 60 + 5)
    est_hours = est_minutes / 60

    # Contar prompts customizados na fila
    prompts_found = 0
    for item in queue:
        if load_scene_prompt(item['obra_dir'], item['scene']['number']):
            prompts_found += 1

    log(f"Fila: {len(queue)} cenas | Prompts custom: {prompts_found}/{len(queue)} | Estimativa: ~{est_hours:.1f}h")
    print()

    if args.dry_run:
        log("PLANO DE EXECUCAO (dry-run):")
        print()
        for i, item in enumerate(queue, 1):
            s = item['scene']
            has_prompt = "P" if load_scene_prompt(item['obra_dir'], s['number']) else "-"
            has_source = "S" if item['source_id'] else "-"
            print(f"  {i:3d}. [{has_prompt}{has_source}] {item['obra_name']}: cena {s['number']} - {s['title'][:45]}")
        print()
        print("  Legenda: P=prompt customizado, S=source targeting, -=ausente")
        print()
        log(f"Total: {len(queue)} cenas")
        return 0

    # Processar
    session_stats['started_at'] = datetime.now()

    for i, item in enumerate(queue, 1):
        if shutdown_requested:
            break

        scene = item['scene']
        remaining = len(queue) - i
        log(f"[{i}/{len(queue)}] {item['obra_name']} | cena {scene['number']}: {scene['title'][:45]}")

        success = process_scene(item)

        if success:
            log(f"   OK ({session_stats['scenes_created']}/{len(queue)} criadas, {remaining} restantes)")
        else:
            if not shutdown_requested:
                log(f"   FALHOU (continuando...)")

        # Intervalo entre cenas
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
