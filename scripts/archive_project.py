#!/usr/bin/env python3
"""
archive_project.py — Archiva áudios de um projeto no Google Drive e libera espaço no Mac.

Usa rclone para upload seguro com verificação de integridade.

Pré-requisito:
    brew install rclone
    rclone config  # criar remote "gdrive"

Uso:
    python scripts/archive_project.py devita              # archiva DeVita
    python scripts/archive_project.py devita --dry-run    # mostra o que faria
    python scripts/archive_project.py devita --upload-only # sobe para GDrive sem deletar local
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from audio_sync_config import GDRIVE_REMOTE, GDRIVE_FOLDER_ID, PROJECTS, get_project


def _get_audio_dir(project: dict) -> Path | None:
    """Retorna o diretório de áudios de um projeto."""
    repo = project["repo"]
    ptype = project["type"]

    if ptype == "obra_multi":
        # Shakespeare: múltiplos diretórios — retorna diretório pai
        return repo / "projetos" / "w_shakespeare"
    elif ptype == "obra_single":
        meta_file = project["metadata_file"]
        return (repo / meta_file).parent
    elif ptype in ("chapter_index", "section_index_lehninger"):
        return repo / project["audio_dir"]
    elif ptype == "section_index_calculo":
        return repo / project["audio_base"] / "munem_vol1" / "audios"
    return None


def _count_audio_files(audio_dir: Path) -> tuple[int, int]:
    """Conta arquivos de áudio e tamanho total."""
    count = 0
    total_bytes = 0
    for ext in ("*.mp3", "*.m4a", "*.wav", "*.ogg"):
        for f in audio_dir.rglob(ext):
            count += 1
            total_bytes += f.stat().st_size
    return count, total_bytes


def _check_rclone():
    """Verifica se rclone está instalado e configurado."""
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True)
        if GDRIVE_REMOTE + ":" not in result.stdout:
            print(f"  Remote '{GDRIVE_REMOTE}' não encontrado no rclone.", file=sys.stderr)
            print(f"  Remotes disponíveis: {result.stdout.strip()}", file=sys.stderr)
            print(f"  Execute: rclone config", file=sys.stderr)
            return False
        return True
    except FileNotFoundError:
        print("  rclone não instalado. Execute: brew install rclone", file=sys.stderr)
        return False


def upload_to_gdrive(project: dict, audio_dir: Path, dry_run: bool = False) -> bool:
    """Upload áudios para Google Drive via rclone."""
    remote_path = f"{GDRIVE_REMOTE}:NotebookLM_Archive/{project['id']}"

    cmd = [
        "rclone", "copy",
        str(audio_dir),
        remote_path,
        "--include", "*.mp3",
        "--include", "*.m4a",
        "--include", "*.wav",
        "--include", "*.ogg",
        "--checksum",
        "--progress",
    ]
    if dry_run:
        cmd.append("--dry-run")

    print(f"  rclone copy -> {remote_path}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def remove_local_audio(audio_dir: Path, project: dict, dry_run: bool = False) -> int:
    """Remove arquivos de áudio locais (preserva metadata)."""
    removed = 0
    for ext in ("*.mp3", "*.m4a", "*.wav", "*.ogg"):
        for f in audio_dir.rglob(ext):
            if dry_run:
                print(f"  [DRY] Remover {f.name}")
            else:
                f.unlink()
            removed += 1
    return removed


def mark_archived(project: dict):
    """Marca no metadata que o projeto foi arquivado."""
    repo = project["repo"]
    now = datetime.now(timezone.utc).isoformat()
    ptype = project["type"]

    if ptype in ("obra_multi", "obra_single"):
        if ptype == "obra_multi":
            meta_files = sorted(repo.glob(project["metadata_glob"]))
        else:
            meta_files = [repo / project["metadata_file"]]

        for meta_path in meta_files:
            if not meta_path.exists():
                continue
            data = json.loads(meta_path.read_text())
            for audio in data.get("audios", []):
                audio["archived"] = True
                audio["archived_at"] = now
            meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    elif ptype == "chapter_index":
        meta_path = repo / project["metadata_file"]
        data = json.loads(meta_path.read_text())
        for ch in data.get("chapters", []):
            ch["archived"] = True
            ch["archived_at"] = now
        meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    elif ptype.startswith("section_index"):
        meta_path = repo / project["metadata_file"]
        data = json.loads(meta_path.read_text())
        for sec in data.get("sections", []):
            sec["archived"] = True
            sec["archived_at"] = now
        meta_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Archive áudios de um projeto no Google Drive")
    parser.add_argument("project_id", help="ID do projeto (ex: devita, w_shakespeare)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o que faria")
    parser.add_argument("--upload-only", action="store_true", help="Só upload, não deleta local")
    args = parser.parse_args()

    project = get_project(args.project_id)
    if not project:
        print(f"  Projeto '{args.project_id}' não encontrado.", file=sys.stderr)
        print(f"  Projetos: {', '.join(p['id'] for p in PROJECTS)}", file=sys.stderr)
        sys.exit(1)

    audio_dir = _get_audio_dir(project)
    if not audio_dir or not audio_dir.exists():
        print(f"  Diretório de áudios não encontrado: {audio_dir}", file=sys.stderr)
        sys.exit(1)

    count, total_bytes = _count_audio_files(audio_dir)
    size_mb = total_bytes / (1024 * 1024)
    print(f"\n=== Archive: {project['label']} ===")
    print(f"  Áudios: {count} arquivos ({size_mb:.0f} MB)")
    print(f"  Origem: {audio_dir}")

    if count == 0:
        print("  Nenhum áudio para arquivar.")
        return

    if not _check_rclone():
        sys.exit(1)

    # Upload
    print(f"\n--- Upload para Google Drive {'(DRY RUN)' if args.dry_run else ''} ---")
    success = upload_to_gdrive(project, audio_dir, dry_run=args.dry_run)
    if not success:
        print("  Upload falhou. Áudios locais NÃO foram removidos.", file=sys.stderr)
        sys.exit(1)

    if args.upload_only:
        print("  Upload concluído (--upload-only, áudios locais preservados).")
        if not args.dry_run:
            mark_archived(project)
            print("  Metadata marcado como archived.")
        return

    # Remove local
    if not args.dry_run:
        print("\n--- Removendo áudios locais ---")
        removed = remove_local_audio(audio_dir, project)
        mark_archived(project)
        print(f"  {removed} arquivos removidos do Mac.")
        print(f"  {size_mb:.0f} MB liberados.")
        print("  Metadata preservado (archived: true).")
    else:
        print(f"\n--- [DRY] Removeria {count} arquivos ({size_mb:.0f} MB) do Mac ---")

    print()


if __name__ == "__main__":
    main()
