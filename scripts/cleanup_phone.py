#!/usr/bin/env python3
"""
cleanup_phone.py — Remove do iCloud áudios já marcados como ouvidos.

Uso:
    python scripts/cleanup_phone.py              # remove ouvidos do iCloud
    python scripts/cleanup_phone.py --dry-run    # mostra o que removeria
    python scripts/cleanup_phone.py --project devita  # só um projeto
"""

import argparse
import sys

from audio_sync_config import ICLOUD_AUDIO, PROJECTS, get_project
from sync_to_phone import scan_all_projects, generate_index, AudioEntry


def cleanup_listened(entries: list[AudioEntry], project_id: str | None = None,
                     dry_run: bool = False) -> tuple[int, int]:
    """Remove do iCloud os áudios marcados como listened. Retorna (removed, kept)."""
    removed = kept = 0

    for entry in entries:
        if project_id and entry.project_id != project_id:
            continue

        icloud_file = ICLOUD_AUDIO / entry.icloud_folder / entry.filename

        if not icloud_file.exists():
            continue

        if entry.listened:
            if dry_run:
                print(f"  [DRY] Remover {entry.icloud_folder}/{entry.filename}")
            else:
                icloud_file.unlink()
                print(f"  Removido {entry.icloud_folder}/{entry.filename}")
            removed += 1
        else:
            kept += 1

    return removed, kept


def main():
    parser = argparse.ArgumentParser(description="Remove áudios ouvidos do iCloud")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria sem remover")
    parser.add_argument("--project", "-p", help="Limpa só um projeto específico")
    args = parser.parse_args()

    if args.project:
        proj = get_project(args.project)
        if not proj:
            print(f"  Projeto '{args.project}' não encontrado.", file=sys.stderr)
            print(f"  Projetos: {', '.join(p['id'] for p in PROJECTS)}", file=sys.stderr)
            sys.exit(1)

    entries = scan_all_projects(require_source=False)

    print(f"\n=== Cleanup iCloud {'(DRY RUN)' if args.dry_run else ''} ===")
    removed, kept = cleanup_listened(entries, project_id=args.project, dry_run=args.dry_run)
    print(f"\n  Removidos: {removed}  |  Mantidos (não ouvidos): {kept}")

    if not args.dry_run and removed > 0:
        generate_index(entries)
        print("  Índice atualizado.")

    print()


if __name__ == "__main__":
    main()
