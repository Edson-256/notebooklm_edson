#!/usr/bin/env python3
"""
Shakespeare Progress Viewer
Mostra progresso detalhado do processamento das 351 cenas
"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
SHAKESPEARE_DIR = PROJECT_DIR / "w_shakespeare"
PROGRESS_FILE = PROJECT_DIR / "logs" / "shakespeare_progress.json"


def get_obra_info(obra_dir: Path) -> dict:
    """Obtém informações da obra"""
    import re

    # Contar total de cenas
    scenes_file = obra_dir / "01_cenas_identificadas.md"
    total_scenes = 0
    if scenes_file.exists():
        content = scenes_file.read_text(encoding='utf-8')
        matches = re.findall(r'^### \d+\.', content, re.MULTILINE)
        total_scenes = len(matches)

    # Contar cenas processadas
    metadata_file = obra_dir / "audios" / "metadata.json"
    processed = 0
    total_size = 0

    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

            for audio in metadata.get('audios', []):
                if audio.get('status') == 'downloaded':
                    processed += 1
                    total_size += audio.get('tamanho_bytes', 0)
        except:
            pass

    return {
        'name': obra_dir.name,
        'total': total_scenes,
        'processed': processed,
        'pending': total_scenes - processed,
        'size_mb': total_size / (1024 * 1024) if total_size > 0 else 0
    }


def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🎭 Shakespeare Audio Generator - Dashboard de Progresso  ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Carregar progresso
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            progress = json.load(f)

        if progress.get('last_run'):
            last_run = datetime.fromisoformat(progress['last_run'])
            print(f"📅 Última execução: {last_run.strftime('%d/%m/%Y às %H:%M')}")
            print()

    # Coletar informações de todas as obras
    obras_info = []
    total_scenes = 0
    total_processed = 0
    total_size = 0

    for obra_dir in sorted(SHAKESPEARE_DIR.iterdir()):
        if obra_dir.is_dir():
            info = get_obra_info(obra_dir)
            if info['total'] > 0:
                obras_info.append(info)
                total_scenes += info['total']
                total_processed += info['processed']
                total_size += info['size_mb']

    # Estatísticas gerais
    percent = (total_processed / total_scenes * 100) if total_scenes > 0 else 0
    remaining = total_scenes - total_processed
    days_remaining = (remaining + 19) // 20  # 20 cenas/dia

    print("📊 ESTATÍSTICAS GERAIS")
    print("━" * 60)
    print(f"   Total de obras: {len(obras_info)}")
    print(f"   Total de cenas: {total_scenes}")
    print(f"   Cenas processadas: {total_processed} ({percent:.1f}%)")
    print(f"   Cenas pendentes: {remaining}")
    print(f"   Espaço em disco: {total_size:.1f} MB ({total_size/1024:.2f} GB)")
    print(f"   Estimativa conclusão: ~{days_remaining} dias")
    print()

    # Barra de progresso visual
    bar_length = 50
    filled = int(bar_length * percent / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {percent:.1f}%")
    print()

    # Obras por status
    completed = [o for o in obras_info if o['pending'] == 0]
    in_progress = [o for o in obras_info if 0 < o['pending'] < o['total']]
    not_started = [o for o in obras_info if o['processed'] == 0]

    print("📚 OBRAS POR STATUS")
    print("━" * 60)
    print(f"   ✅ Completas: {len(completed)}")
    print(f"   🔄 Em progresso: {len(in_progress)}")
    print(f"   📋 Não iniciadas: {len(not_started)}")
    print()

    # Top 5 obras com mais cenas processadas
    if total_processed > 0:
        print("🏆 TOP 5 OBRAS MAIS PROCESSADAS")
        print("━" * 60)
        top_5 = sorted(obras_info, key=lambda x: x['processed'], reverse=True)[:5]
        for i, obra in enumerate(top_5, 1):
            if obra['processed'] > 0:
                pct = obra['processed'] / obra['total'] * 100
                print(f"   {i}. {obra['name'][:40]:40} {obra['processed']:2}/{obra['total']:2} ({pct:5.1f}%)")
        print()

    # Próximas obras a serem processadas
    if not_started:
        print("📋 PRÓXIMAS OBRAS (Ainda não iniciadas)")
        print("━" * 60)
        for obra in not_started[:5]:
            print(f"   • {obra['name']:40} ({obra['total']} cenas)")
        if len(not_started) > 5:
            print(f"   ... e mais {len(not_started) - 5} obras")
        print()

    # Detalhes completos (modo verbose)
    import sys
    if '--verbose' in sys.argv or '-v' in sys.argv:
        print("📖 DETALHAMENTO COMPLETO POR OBRA")
        print("━" * 60)
        for obra in obras_info:
            status_icon = "✅" if obra['pending'] == 0 else "🔄" if obra['processed'] > 0 else "📋"
            pct = obra['processed'] / obra['total'] * 100 if obra['total'] > 0 else 0
            size_info = f"{obra['size_mb']:.1f}MB" if obra['size_mb'] > 0 else "---"
            print(f"{status_icon} {obra['name']:40} {obra['processed']:2}/{obra['total']:2} ({pct:5.1f}%) {size_info:>8}")


if __name__ == "__main__":
    main()
