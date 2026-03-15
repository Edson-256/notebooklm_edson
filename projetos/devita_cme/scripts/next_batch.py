#!/usr/bin/env python3
"""
Seleciona os próximos N capítulos pendentes do DeVita e gera áudios.
Usa fire-and-forget: cria primeiro, baixa depois (separado).

Uso:
    python next_batch.py              # próximos 5 (dry-run)
    python next_batch.py --go         # executa criação
    python next_batch.py --download   # baixa áudios já prontos no NLM
    python next_batch.py -n 3 --go    # próximos 3, executa
    python next_batch.py --status     # mostra progresso geral
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CHAPTER_INDEX = PROJECT_DIR / "chapter_index.json"
GENERATOR_SCRIPT = Path(__file__).parent / "generate_devita_audio.py"
PROMPTS_DIR = PROJECT_DIR / "prompts" / "chapters"

DONE_STATUSES = {"generated", "downloaded", "listened", "completed"}


def load_index():
    with open(CHAPTER_INDEX, encoding="utf-8") as f:
        return json.load(f)


def has_prompt(ch_num):
    return any(p.name.startswith(f"ch{ch_num:03d}") for p in PROMPTS_DIR.iterdir())


def show_status(index):
    chapters = index["chapters"]
    total = len(chapters)
    downloaded = sum(1 for c in chapters if c["status"] in ("downloaded", "listened", "completed"))
    generated_only = sum(1 for c in chapters if c["status"] == "generated")
    pending = sum(1 for c in chapters if c["status"] == "pending")
    errors = sum(1 for c in chapters if c["status"] == "error")

    print(f"\n  DeVita CME — Progresso")
    print(f"  {'=' * 40}")
    print(f"  Total:      {total}")
    print(f"  Baixados:   {downloaded} ({downloaded*100//total}%)")
    if generated_only:
        print(f"  Sem baixar: {generated_only} (usar --download)")
    print(f"  Pendente:   {pending}")
    if errors:
        print(f"  Erros:      {errors}")
    print(f"  {'=' * 40}\n")


def get_pending(index):
    return sorted(
        [c for c in index["chapters"] if c["status"] == "pending"],
        key=lambda c: c["chapter_num"],
    )


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Próximo batch de capítulos DeVita")
    parser.add_argument("-n", "--count", type=int, default=5,
                        help="Quantos capítulos no batch (default: 5)")
    parser.add_argument("--go", action="store_true",
                        help="Executa a criação de áudios (fire-and-forget)")
    parser.add_argument("--download", action="store_true",
                        help="Baixa áudios já prontos no NLM")
    parser.add_argument("--status", action="store_true",
                        help="Mostra progresso geral e sai")
    args = parser.parse_args()

    index = load_index()

    if args.status:
        show_status(index)
        return 0

    # Modo download: delega para generate_devita_audio.py --download
    if args.download:
        show_status(index)
        print("  Baixando áudios prontos...\n")
        cmd = [sys.executable, str(GENERATOR_SCRIPT), "--download"]
        result = subprocess.run(cmd)

        # Atualizar tracker
        tracker_script = Path(__file__).parent / "update_tracker.py"
        if tracker_script.exists():
            print("\n  Atualizando tracker.md...")
            subprocess.run([sys.executable, str(tracker_script)])

        return result.returncode

    show_status(index)

    pending = get_pending(index)
    if not pending:
        print("  Todos os capítulos já foram processados!")
        return 0

    batch = pending[:args.count]
    chapter_nums = ",".join(str(c["chapter_num"]) for c in batch)

    print(f"  Próximo batch ({len(batch)} capítulos):\n")
    for c in batch:
        prompt_tag = "prompt" if has_prompt(c["chapter_num"]) else "genérico"
        print(f"    #{c['chapter_num']:3d}  {c['title']:<55s}  [{prompt_tag}]")

    remaining = len(pending) - len(batch)
    print(f"\n  Restam {remaining} capítulos após este batch.\n")

    if not args.go:
        print("  Modo preview. Use --go para executar.\n")
        print(f"  Comandos:")
        print(f"    python {GENERATOR_SCRIPT.name} --chapters {chapter_nums}   # criar")
        print(f"    python {Path(__file__).name} --download                     # baixar (~15 min depois)\n")
        return 0

    # Executar criação (fire-and-forget — NÃO baixa automaticamente)
    print(f"  Iniciando criação de {len(batch)} áudios...\n")
    cmd = [sys.executable, str(GENERATOR_SCRIPT), "--chapters", chapter_nums]
    result = subprocess.run(cmd)

    # Atualizar tracker
    tracker_script = Path(__file__).parent / "update_tracker.py"
    if tracker_script.exists():
        print("\n  Atualizando tracker.md...")
        subprocess.run([sys.executable, str(tracker_script)])

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
