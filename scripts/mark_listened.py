#!/usr/bin/env python3
"""
mark_listened.py — Marca áudios como ouvidos no metadata.

Uso:
    python scripts/mark_listened.py ws_hamlet_01_contraste_teatro.mp3
    python scripts/mark_listened.py ws_hamlet_01.mp3 ws_hamlet_02.mp3
    python scripts/mark_listened.py --project ben_hur          # marca todos do projeto
    python scripts/mark_listened.py --list                     # lista não ouvidos
    python scripts/mark_listened.py --list --project devita    # lista não ouvidos do projeto
"""

import argparse
import json
import sys
from pathlib import Path

from audio_sync_config import PROJECTS, get_project
from sync_to_phone import scan_all_projects, AudioEntry


def find_entries_by_filenames(entries: list[AudioEntry], filenames: list[str]) -> list[AudioEntry]:
    """Encontra entries que correspondem aos filenames (match parcial ou exato)."""
    matched = []
    for entry in entries:
        for pattern in filenames:
            if entry.filename == pattern or entry.filename.startswith(pattern.rsplit(".", 1)[0]):
                matched.append(entry)
                break
    return matched


def mark_listened(entries: list[AudioEntry]):
    """Marca entries como listened=true nos respectivos metadata files."""
    # Agrupa por metadata_path
    by_meta: dict[Path, list[str]] = {}
    for e in entries:
        by_meta.setdefault(e.metadata_path, []).append(e.filename)

    for meta_path, filenames in by_meta.items():
        fname_set = set(filenames)
        data = json.loads(meta_path.read_text())

        updated = 0
        if "audios" in data:
            for audio in data["audios"]:
                if audio.get("arquivo") in fname_set:
                    audio["listened"] = True
                    updated += 1
        elif "chapters" in data and isinstance(data["chapters"], list):
            for ch in data["chapters"]:
                if ch.get("audio_file") in fname_set:
                    ch["listened"] = True
                    updated += 1
        elif "sections" in data:
            for sec in data["sections"]:
                fname = sec.get("audio_file") or (Path(sec.get("output_path", "")).name if sec.get("output_path") else None)
                if fname in fname_set:
                    sec["listened"] = True
                    updated += 1

        if updated > 0:
            meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    return len(entries)


def list_not_listened(entries: list[AudioEntry], project_id: str | None = None):
    """Lista áudios não ouvidos."""
    filtered = entries
    if project_id:
        filtered = [e for e in entries if e.project_id == project_id]

    not_listened = [e for e in filtered if not e.listened]

    if not not_listened:
        print("  Todos os áudios foram ouvidos!")
        return

    current_project = None
    for e in sorted(not_listened, key=lambda x: (x.project_id, x.filename)):
        if e.project_id != current_project:
            current_project = e.project_id
            proj = get_project(e.project_id)
            label = proj["label"] if proj else e.project_id
            print(f"\n  {label}:")
        print(f"    {e.filename}")

    print(f"\n  Total não ouvidos: {len(not_listened)}")


def main():
    parser = argparse.ArgumentParser(description="Marca áudios como ouvidos")
    parser.add_argument("filenames", nargs="*", help="Nomes dos arquivos de áudio")
    parser.add_argument("--project", "-p", help="Marca todos os áudios de um projeto")
    parser.add_argument("--list", "-l", action="store_true", help="Lista áudios não ouvidos")
    args = parser.parse_args()

    entries = scan_all_projects(require_source=False)

    if args.list:
        list_not_listened(entries, args.project)
        return

    if args.project and not args.filenames:
        # Marca todos do projeto
        project_entries = [e for e in entries if e.project_id == args.project]
        if not project_entries:
            print(f"  Projeto '{args.project}' não encontrado ou sem áudios.", file=sys.stderr)
            sys.exit(1)
        count = mark_listened(project_entries)
        print(f"  {count} áudios marcados como ouvidos no projeto '{args.project}'")
        return

    if not args.filenames:
        parser.print_help()
        sys.exit(1)

    matched = find_entries_by_filenames(entries, args.filenames)
    if not matched:
        print(f"  Nenhum áudio encontrado para: {', '.join(args.filenames)}", file=sys.stderr)
        print("  Use --list para ver áudios disponíveis.", file=sys.stderr)
        sys.exit(1)

    count = mark_listened(matched)
    for e in matched:
        print(f"  [OK] {e.filename}")
    print(f"\n  {count} áudio(s) marcado(s) como ouvido(s)")


if __name__ == "__main__":
    main()
