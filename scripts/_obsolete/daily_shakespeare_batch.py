#!/usr/bin/env python3
"""
Daily Shakespeare Batch Processor
Processa 20 cenas por dia de forma distribuída entre todas as obras
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configurações
PROJECT_DIR = Path(__file__).parent.parent
SHAKESPEARE_DIR = PROJECT_DIR / "projetos" / "w_shakespeare"
PROGRESS_FILE = PROJECT_DIR / "logs" / "shakespeare_progress.json"
BATCH_SIZE = 20  # cenas por execução (sem limite diário)
LOG_DIR = PROJECT_DIR / "logs"

def log(message: str):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def load_progress() -> Dict:
    """Carrega progresso do processamento"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        'last_run': None,
        'total_processed': 0,
        'obras': {}
    }


def save_progress(progress: Dict):
    """Salva progresso do processamento"""
    LOG_DIR.mkdir(exist_ok=True)
    progress['last_run'] = datetime.now().isoformat()

    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

    log(f"💾 Progresso salvo: {progress['total_processed']} cenas processadas")


def get_obra_scenes(obra_dir: Path) -> int:
    """Conta total de cenas da obra"""
    scenes_file = obra_dir / "01_cenas_identificadas.md"
    if not scenes_file.exists():
        return 0

    content = scenes_file.read_text(encoding='utf-8')
    # Contar ocorrências de "### N."
    import re
    matches = re.findall(r'^### \d+\.', content, re.MULTILINE)
    return len(matches)


def get_obra_processed(obra_dir: Path) -> int:
    """Conta cenas já processadas da obra"""
    metadata_file = obra_dir / "audios" / "metadata.json"
    if not metadata_file.exists():
        return 0

    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Contar apenas cenas com download concluído
        downloaded = sum(1 for audio in metadata.get('audios', [])
                        if audio.get('status') == 'downloaded')
        return downloaded
    except Exception as e:
        log(f"⚠️  Erro ao ler metadata de {obra_dir.name}: {e}")
        return 0


def get_pending_obras() -> List[Dict]:
    """Lista obras com cenas pendentes"""
    obras_pending = []

    for obra_dir in sorted(SHAKESPEARE_DIR.iterdir()):
        if not obra_dir.is_dir():
            continue

        total_scenes = get_obra_scenes(obra_dir)
        if total_scenes == 0:
            continue

        processed_scenes = get_obra_processed(obra_dir)
        pending_scenes = total_scenes - processed_scenes

        if pending_scenes > 0:
            obras_pending.append({
                'dir': obra_dir,
                'name': obra_dir.name,
                'total': total_scenes,
                'processed': processed_scenes,
                'pending': pending_scenes
            })

    return obras_pending


def process_daily_batch(dry_run: bool = False) -> Dict:
    """Processa batch diário de 20 cenas"""
    log("=" * 70)
    log("🎭 SHAKESPEARE DAILY BATCH - Processamento Diário")
    log("=" * 70)

    # Carregar progresso
    progress = load_progress()

    today = datetime.now().strftime("%Y-%m-%d")
    today_processed = progress.get('today', {}).get(today, 0)

    if today_processed > 0:
        log(f"ℹ️  Sessão anterior hoje: {today_processed} cenas já processadas.")

    # Obter obras com cenas pendentes
    pending_obras = get_pending_obras()

    if not pending_obras:
        log("✅ Todas as obras já foram processadas!")
        return progress

    # Mostrar estatísticas
    total_pending = sum(o['pending'] for o in pending_obras)
    log(f"\n📊 Estatísticas:")
    log(f"   Obras pendentes: {len(pending_obras)}")
    log(f"   Cenas pendentes: {total_pending}")
    log(f"   Cenas já processadas: {progress['total_processed']}")
    log(f"   Batch desta execução: {min(BATCH_SIZE, total_pending)} cenas ({today_processed} já feitas hoje)")

    # Distribuir cenas no batch
    scenes_to_process = []
    remaining = BATCH_SIZE

    # Round-robin: pega 1 cena de cada obra até completar 20
    while remaining > 0 and pending_obras:
        for obra in pending_obras[:]:
            if remaining == 0:
                break

            if obra['pending'] > 0:
                scenes_to_process.append({
                    'obra': obra['name'],
                    'start_from': obra['processed'] + 1
                })
                obra['pending'] -= 1
                obra['processed'] += 1
                remaining -= 1

            # Remove obra se não tem mais cenas pendentes
            if obra['pending'] == 0:
                pending_obras.remove(obra)

    # Agrupar por obra
    obras_to_process = {}
    for scene in scenes_to_process:
        obra_name = scene['obra']
        if obra_name not in obras_to_process:
            obras_to_process[obra_name] = {
                'scenes': [],
                'count': 0
            }
        obras_to_process[obra_name]['scenes'].append(scene['start_from'])
        obras_to_process[obra_name]['count'] += 1

    log(f"\n📋 Plano de processamento:")
    for obra_name, data in obras_to_process.items():
        log(f"   {obra_name}: {data['count']} cenas")

    if dry_run:
        log("\n🧪 DRY RUN - Não executando processamento")
        return progress

    # Processar cada obra
    log(f"\n🚀 Iniciando processamento...")
    total_success = 0

    for obra_name, data in obras_to_process.items():
        log(f"\n{'='*70}")
        log(f"📚 Processando: {obra_name} ({data['count']} cenas)")
        log(f"{'='*70}")

        # Calcular cena inicial (próxima após as já processadas)
        start_from = min(data['scenes'])

        # Executar script principal
        cmd = [
            "python3",
            str(PROJECT_DIR / "scripts" / "shakespeare_audio_generator.py"),
            "--obra", obra_name,
            "--scenes", str(data['count']),
            "--start-from", str(start_from)
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 2 horas timeout
            )

            if result.returncode == 0:
                log(f"✅ {obra_name} processado com sucesso")
                total_success += data['count']

                # Atualizar progresso
                if obra_name not in progress['obras']:
                    progress['obras'][obra_name] = {'processed': 0}
                progress['obras'][obra_name]['processed'] += data['count']
            else:
                log(f"❌ Erro ao processar {obra_name}")
                log(f"   STDERR: {result.stderr[:500]}")

        except subprocess.TimeoutExpired:
            log(f"⏰ Timeout ao processar {obra_name}")
        except Exception as e:
            log(f"❌ Exceção ao processar {obra_name}: {e}")

    # Atualizar progresso total e contador diário
    progress['total_processed'] += total_success
    if 'today' not in progress:
        progress['today'] = {}
    progress['today'][today] = today_processed + total_success
    save_progress(progress)

    # Resumo final
    new_today_total = today_processed + total_success
    log(f"\n{'='*70}")
    log(f"📊 RESUMO DO BATCH")
    log(f"{'='*70}")
    log(f"✅ Cenas processadas nesta execução: {total_success}")
    log(f"📅 Total de hoje: {new_today_total}")
    log(f"📈 Total acumulado: {progress['total_processed']}/351")

    remaining_total = 351 - progress['total_processed']
    runs_remaining = (remaining_total + BATCH_SIZE - 1) // BATCH_SIZE
    log(f"⏱️  Execuções restantes: ~{runs_remaining} (2x/dia = ~{(runs_remaining + 1) // 2} dias)")

    return progress


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Daily Shakespeare Batch Processor')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simular execução sem processar')

    args = parser.parse_args()

    try:
        process_daily_batch(dry_run=args.dry_run)
    except KeyboardInterrupt:
        log("\n⚠️  Processamento interrompido pelo usuário")
    except Exception as e:
        log(f"\n❌ Erro fatal: {e}")
        raise


if __name__ == "__main__":
    main()
