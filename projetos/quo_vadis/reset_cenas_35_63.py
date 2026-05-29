#!/usr/bin/env python3
"""
Remove cenas 35-63 do metadata.json para permitir re-geração.

Contexto: o bug de numeração local→global (commit c27e4bb) gerou os áudios
físicos dessas 29 cenas com conteúdo de 103-131 (duplicatas já corrigidas).
O conteúdo real de 35-63 nunca foi gerado.

Uso:
    python3 projetos/quo_vadis/reset_cenas_35_63.py           # executa
    python3 projetos/quo_vadis/reset_cenas_35_63.py --dry-run # só mostra
"""
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

METADATA = Path(__file__).parent / "audios" / "metadata.json"
RESET_RANGE = range(35, 64)  # 35 a 63 inclusive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    data = json.loads(METADATA.read_text(encoding='utf-8'))
    audios = data['audios']

    to_remove = [a for a in audios if a['cena_numero'] in RESET_RANGE]
    to_keep   = [a for a in audios if a['cena_numero'] not in RESET_RANGE]

    print(f"Total atual:   {len(audios)} entradas")
    print(f"A remover:     {len(to_remove)} (cenas 35-63)")
    print(f"A manter:      {len(to_keep)}")
    print()
    for a in to_remove:
        print(f"  cena {a['cena_numero']:03d}: {a['arquivo']}  [{a.get('status')}]")
    print()

    if args.dry_run:
        print("dry-run: nada alterado.")
        return

    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = METADATA.with_name(f"metadata.json.bak_reset_{ts}")
    shutil.copy2(METADATA, bak)
    print(f"Backup: {bak.name}")

    data['audios'] = to_keep
    data['total_cenas'] = len(to_keep)
    data['ultima_atualizacao'] = datetime.now().isoformat()
    METADATA.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"metadata.json atualizado: {len(to_keep)} entradas")
    print()
    print("Próximo passo:")
    print("  Batch 1 (18 cenas): python3 quo_vadis_runner.py --from-scene 35 --to-scene 52")
    print("  Aguardar 40min, depois: python3 quo_vadis_runner.py --download")
    print("  Batch 2 (11 cenas): python3 quo_vadis_runner.py --from-scene 53 --to-scene 63")
    print("  Aguardar 40min, depois: python3 quo_vadis_runner.py --download")


if __name__ == "__main__":
    main()
