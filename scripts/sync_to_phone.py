#!/usr/bin/env python3
"""
sync_to_phone.py — Sincroniza áudios dos projetos para iCloud Drive.

Uso:
    python scripts/sync_to_phone.py              # sync normal
    python scripts/sync_to_phone.py --dry-run     # mostra o que faria
    python scripts/sync_to_phone.py --status      # resumo por projeto
    python scripts/sync_to_phone.py --migrate     # renomeia pastas antigas no iCloud
"""

import argparse
import json
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from audio_sync_config import ICLOUD_AUDIO, ICLOUD_MIGRATION, PROJECTS


@dataclass
class AudioEntry:
    filename: str
    source_path: Path
    project_id: str
    icloud_folder: str
    metadata_path: Path
    listened: bool = False
    synced: bool = False


# ─── Metadata Parsers ────────────────────────────────────────────────────────


def _parse_obra(meta_path: Path, project: dict, require_source: bool = True) -> list[AudioEntry]:
    """Parse metadata.json com audios[] (Shakespeare, Ben-Hur)."""
    entries = []
    data = json.loads(meta_path.read_text())
    for audio in data.get("audios", []):
        if audio.get("status") != "downloaded":
            continue
        # Resolve source path: try output_path first, then relative to metadata
        source = None
        if audio.get("output_path"):
            candidate = Path(audio["output_path"])
            if candidate.exists():
                source = candidate
        if source is None:
            candidate = meta_path.parent / audio["arquivo"]
            if candidate.exists():
                source = candidate
        if require_source and source is None:
            continue
        entries.append(AudioEntry(
            filename=audio["arquivo"],
            source_path=source or meta_path.parent / audio["arquivo"],
            project_id=project["id"],
            icloud_folder=project["icloud_folder"],
            metadata_path=meta_path,
            listened=audio.get("listened", False),
            synced=audio.get("synced_to_icloud", False),
        ))
    return entries


def _parse_chapter_index(project: dict, require_source: bool = True) -> list[AudioEntry]:
    """Parse chapter_index.json (DeVita)."""
    meta_path = project["repo"] / project["metadata_file"]
    audio_dir = project["repo"] / project["audio_dir"]
    if not meta_path.exists():
        return []
    entries = []
    data = json.loads(meta_path.read_text())
    for ch in data.get("chapters", []):
        if ch.get("status") != "downloaded" or not ch.get("audio_file"):
            continue
        source = audio_dir / ch["audio_file"]
        if require_source and not source.exists():
            continue
        entries.append(AudioEntry(
            filename=ch["audio_file"],
            source_path=source,
            project_id=project["id"],
            icloud_folder=project["icloud_folder"],
            metadata_path=meta_path,
            listened=ch.get("listened", False),
            synced=ch.get("synced_to_icloud", False),
        ))
    return entries


def _parse_section_index_calculo(project: dict, require_source: bool = True) -> list[AudioEntry]:
    """Parse section_index.json (Cálculo — output_path relativo ou absoluto)."""
    meta_path = project["repo"] / project["metadata_file"]
    audio_base = project["repo"] / project["audio_base"]
    if not meta_path.exists():
        return []
    entries = []
    data = json.loads(meta_path.read_text())
    for sec in data.get("sections", []):
        if sec.get("status") != "downloaded" or not sec.get("output_path"):
            continue
        raw_path = sec["output_path"]
        # Tenta: path relativo ao audio_base, absoluto, ou fallback por nome
        source = audio_base / raw_path
        if not source.exists() and raw_path.startswith("/"):
            source = Path(raw_path)
        if not source.exists():
            # Fallback: busca pelo nome do arquivo no diretório de áudios
            fname = Path(raw_path).name
            fallback = audio_base / "munem_vol1" / "audios" / fname
            if fallback.exists():
                source = fallback
        if require_source and not source.exists():
            continue
        entries.append(AudioEntry(
            filename=source.name,
            source_path=source,
            project_id=project["id"],
            icloud_folder=project["icloud_folder"],
            metadata_path=meta_path,
            listened=sec.get("listened", False),
            synced=sec.get("synced_to_icloud", False),
        ))
    return entries


def _parse_section_index_lehninger(project: dict, require_source: bool = True) -> list[AudioEntry]:
    """Parse section_index.json (Lehninger — audio_status + audio_file)."""
    meta_path = project["repo"] / project["metadata_file"]
    audio_dir = project["repo"] / project["audio_dir"]
    if not meta_path.exists():
        return []
    entries = []
    data = json.loads(meta_path.read_text())
    for sec in data.get("sections", []):
        if sec.get("audio_status") != "downloaded" or not sec.get("audio_file"):
            continue
        source = audio_dir / sec["audio_file"]
        if require_source and not source.exists():
            continue
        entries.append(AudioEntry(
            filename=sec["audio_file"],
            source_path=source,
            project_id=project["id"],
            icloud_folder=project["icloud_folder"],
            metadata_path=meta_path,
            listened=sec.get("listened", False),
            synced=sec.get("synced_to_icloud", False),
        ))
    return entries


# ─── Scanner ─────────────────────────────────────────────────────────────────


def scan_all_projects(require_source: bool = True) -> list[AudioEntry]:
    """Varre todos os projetos e retorna lista unificada de AudioEntry.

    Args:
        require_source: Se True, só retorna entries com arquivo fonte no Mac.
                       Se False, retorna todos os entries do metadata (para mark_listened).
    """
    all_entries = []
    for project in PROJECTS:
        ptype = project["type"]
        if ptype == "obra_multi":
            for meta_path in sorted(project["repo"].glob(project["metadata_glob"])):
                all_entries.extend(_parse_obra(meta_path, project, require_source))
        elif ptype == "obra_single":
            meta_path = project["repo"] / project["metadata_file"]
            if meta_path.exists():
                all_entries.extend(_parse_obra(meta_path, project, require_source))
        elif ptype == "chapter_index":
            all_entries.extend(_parse_chapter_index(project, require_source))
        elif ptype == "section_index_calculo":
            all_entries.extend(_parse_section_index_calculo(project, require_source))
        elif ptype == "section_index_lehninger":
            all_entries.extend(_parse_section_index_lehninger(project, require_source))
    return all_entries


# ─── Sync ────────────────────────────────────────────────────────────────────


def sync_to_icloud(entries: list[AudioEntry], dry_run: bool = False) -> tuple[int, int, int]:
    """Copia áudios pendentes para iCloud. Retorna (synced, skipped, errors)."""
    synced = skipped = errors = 0
    now = datetime.now(timezone.utc).isoformat()

    # Agrupa por metadata_path para batch update
    updates: dict[Path, list[tuple[str, str]]] = {}

    for entry in entries:
        dest_dir = ICLOUD_AUDIO / entry.icloud_folder
        dest_file = dest_dir / entry.filename

        if dest_file.exists():
            # Garante que metadata reflete o sync mesmo que arquivo já exista
            if not entry.synced:
                updates.setdefault(entry.metadata_path, []).append((entry.filename, now))
            skipped += 1
            continue

        if dry_run:
            print(f"  [DRY] {entry.icloud_folder}/{entry.filename}")
            synced += 1
            continue

        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry.source_path, dest_file)
            updates.setdefault(entry.metadata_path, []).append((entry.filename, now))
            synced += 1
        except (OSError, shutil.Error) as e:
            print(f"  [ERRO] {entry.filename}: {e}", file=sys.stderr)
            errors += 1

    # Atualiza metadata em batch
    if not dry_run:
        _batch_update_metadata(updates, field_name="synced_to_icloud", field_value=True,
                               timestamp_field="synced_at")

    return synced, skipped, errors


def _batch_update_metadata(updates: dict[Path, list[tuple[str, str]]],
                           field_name: str, field_value, timestamp_field: str):
    """Atualiza campo em entries de metadata por filename."""
    for meta_path, file_timestamps in updates.items():
        filenames = {f for f, _ in file_timestamps}
        timestamps = {f: t for f, t in file_timestamps}

        data = json.loads(meta_path.read_text())

        # Detecta o formato e atualiza
        if "audios" in data:
            for audio in data["audios"]:
                if audio.get("arquivo") in filenames:
                    audio[field_name] = field_value
                    audio[timestamp_field] = timestamps[audio["arquivo"]]
                    if "listened" not in audio:
                        audio["listened"] = False
        elif "chapters" in data and isinstance(data["chapters"], list):
            for ch in data["chapters"]:
                if ch.get("audio_file") in filenames:
                    ch[field_name] = field_value
                    ch[timestamp_field] = timestamps[ch["audio_file"]]
                    if "listened" not in ch:
                        ch["listened"] = False
        elif "sections" in data:
            for sec in data["sections"]:
                fname = sec.get("audio_file") or (Path(sec.get("output_path", "")).name if sec.get("output_path") else None)
                if fname in filenames:
                    sec[field_name] = field_value
                    sec[timestamp_field] = timestamps[fname]
                    if "listened" not in sec:
                        sec["listened"] = False

        meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


# ─── Index ───────────────────────────────────────────────────────────────────


def generate_index(entries: list[AudioEntry]):
    """Gera _index.txt na pasta iCloud com lista organizada por projeto."""
    lines = []
    lines.append(f"# Índice de Áudios — gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"# Total: {len(entries)} áudios rastreados\n")

    # Agrupa por projeto
    by_project: dict[str, list[AudioEntry]] = {}
    for e in entries:
        by_project.setdefault(e.project_id, []).append(e)

    for project in PROJECTS:
        pid = project["id"]
        if pid not in by_project:
            continue
        pentries = by_project[pid]
        listened = sum(1 for e in pentries if e.listened)
        synced_count = sum(1 for e in pentries if (ICLOUD_AUDIO / e.icloud_folder / e.filename).exists())

        lines.append(f"## {project['label']} ({synced_count}/{len(pentries)} no iCloud, {listened} ouvidos)")
        for e in sorted(pentries, key=lambda x: x.filename):
            status = "X" if e.listened else " "
            in_icloud = "+" if (ICLOUD_AUDIO / e.icloud_folder / e.filename).exists() else "-"
            lines.append(f"  [{status}] {in_icloud} {e.filename}")
        lines.append("")

    # Arquivos manuais (não rastreados por metadata)
    tracked_files = {(e.icloud_folder, e.filename) for e in entries}
    manual_files: dict[str, list[str]] = {}
    if ICLOUD_AUDIO.exists():
        for subdir in sorted(ICLOUD_AUDIO.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith(("_", ".")):
                continue
            for f in sorted(subdir.iterdir()):
                if f.is_file() and f.suffix in (".mp3", ".m4a", ".wav", ".ogg"):
                    if (subdir.name, f.name) not in tracked_files:
                        manual_files.setdefault(subdir.name, []).append(f.name)

    if manual_files:
        total_manual = sum(len(v) for v in manual_files.values())
        lines.append(f"## Manuais — não rastreados ({total_manual} arquivos)")
        for folder, files in sorted(manual_files.items()):
            lines.append(f"  ### {folder}/")
            for f in files:
                lines.append(f"    {f}")
        lines.append("")

    index_path = ICLOUD_AUDIO / "_index.txt"
    index_path.write_text("\n".join(lines) + "\n")
    return index_path


# ─── Migration ───────────────────────────────────────────────────────────────


def _is_case_only_rename(old_name: str, new_name: str) -> bool:
    """Verifica se a renomeação é apenas mudança de case (macOS case-insensitive)."""
    return old_name.lower().rstrip() == new_name.lower()


def migrate_icloud_folders(dry_run: bool = False):
    """Renomeia pastas antigas no iCloud para padrão normalizado."""
    if not ICLOUD_AUDIO.exists():
        print(f"Pasta iCloud não encontrada: {ICLOUD_AUDIO}")
        return

    migrated = 0
    for old_name, new_name in ICLOUD_MIGRATION.items():
        if old_name == new_name:
            continue
        old_path = ICLOUD_AUDIO / old_name

        if not old_path.exists():
            continue

        # macOS case-insensitive: precisa two-step rename
        if _is_case_only_rename(old_name, new_name):
            if dry_run:
                print(f"  [DRY] Renomear (case) {old_name}/ -> {new_name}/")
            else:
                tmp_path = ICLOUD_AUDIO / f"{new_name}_tmp_migrate"
                old_path.rename(tmp_path)
                tmp_path.rename(ICLOUD_AUDIO / new_name)
                print(f"  Renomeado (case) {old_name}/ -> {new_name}/")
            migrated += 1
            continue

        new_path = ICLOUD_AUDIO / new_name
        if new_path.exists():
            # Mescla: move arquivos do antigo para o novo
            if dry_run:
                files = list(old_path.iterdir())
                print(f"  [DRY] Mesclar {old_name}/ -> {new_name}/ ({len(files)} arquivos)")
            else:
                for f in old_path.iterdir():
                    dest = new_path / f.name
                    if not dest.exists():
                        shutil.move(str(f), str(dest))
                # Remove pasta vazia
                for leftover in old_path.iterdir():
                    if leftover.name == ".DS_Store":
                        leftover.unlink()
                try:
                    old_path.rmdir()
                except OSError:
                    pass
                print(f"  Mesclado {old_name}/ -> {new_name}/")
            migrated += 1
        else:
            if dry_run:
                print(f"  [DRY] Renomear {old_name}/ -> {new_name}/")
            else:
                shutil.move(str(old_path), str(new_path))
                print(f"  Renomeado {old_name}/ -> {new_name}/")
            migrated += 1

    # Limpa backup folders (Louis Lavelle-backup-*)
    for item in ICLOUD_AUDIO.iterdir():
        if item.is_dir() and "-backup-" in item.name:
            base_name = item.name.split("-backup-")[0]
            normalized = ICLOUD_MIGRATION.get(base_name, base_name.lower().replace(" ", "_"))
            target = ICLOUD_AUDIO / normalized
            if dry_run:
                print(f"  [DRY] Mesclar backup {item.name}/ -> {normalized}/")
            else:
                target.mkdir(exist_ok=True)
                for f in item.iterdir():
                    dest = target / f.name
                    if not dest.exists():
                        shutil.move(str(f), str(dest))
                try:
                    # Remove .DS_Store and empty dir
                    for leftover in item.iterdir():
                        if leftover.name == ".DS_Store":
                            leftover.unlink()
                    item.rmdir()
                except OSError:
                    pass
                print(f"  Mesclado backup {item.name}/ -> {normalized}/")
            migrated += 1

    if migrated == 0:
        print("  Nenhuma migração necessária — pastas já normalizadas.")
    return migrated


# ─── Status ──────────────────────────────────────────────────────────────────


def show_status(entries: list[AudioEntry]):
    """Mostra resumo por projeto."""
    by_project: dict[str, list[AudioEntry]] = {}
    for e in entries:
        by_project.setdefault(e.project_id, []).append(e)

    total_all = 0
    synced_all = 0
    listened_all = 0

    print("\n  Projeto                 Total   iCloud  Ouvidos  Pendentes")
    print("  " + "-" * 62)

    for project in PROJECTS:
        pid = project["id"]
        pentries = by_project.get(pid, [])
        total = len(pentries)
        in_icloud = sum(1 for e in pentries if (ICLOUD_AUDIO / e.icloud_folder / e.filename).exists())
        listened = sum(1 for e in pentries if e.listened)
        pending = total - in_icloud

        total_all += total
        synced_all += in_icloud
        listened_all += listened

        label = project["label"][:22].ljust(22)
        print(f"  {label}  {total:>5}   {in_icloud:>5}    {listened:>5}      {pending:>5}")

    print("  " + "-" * 62)
    print(f"  {'TOTAL':22}  {total_all:>5}   {synced_all:>5}    {listened_all:>5}      {total_all - synced_all:>5}")
    print()


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Sync áudios para iCloud Drive")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria sem copiar")
    parser.add_argument("--status", action="store_true", help="Mostra resumo por projeto")
    parser.add_argument("--migrate", action="store_true", help="Renomeia pastas antigas no iCloud")
    args = parser.parse_args()

    if args.migrate:
        print("\n=== Migração de pastas iCloud ===")
        migrate_icloud_folders(dry_run=args.dry_run)
        if not args.dry_run:
            print("  Migração concluída.\n")
        return

    print("\n=== Scan de projetos ===")
    entries = scan_all_projects()
    print(f"  {len(entries)} áudios encontrados em {len(PROJECTS)} projetos")

    if args.status:
        show_status(entries)
        return

    print(f"\n=== Sync para iCloud {'(DRY RUN)' if args.dry_run else ''} ===")
    synced, skipped, errors = sync_to_icloud(entries, dry_run=args.dry_run)
    print(f"  Copiados: {synced}  |  Já existiam: {skipped}  |  Erros: {errors}")

    if not args.dry_run:
        index_path = generate_index(entries)
        print(f"  Índice gerado: {index_path.name}")

    print()


if __name__ == "__main__":
    main()
