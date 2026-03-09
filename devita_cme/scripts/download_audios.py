#!/usr/bin/env python3
"""
Baixa áudios gerados do NotebookLM para capítulos do DeVita.

Lê chapter_index.json, encontra capítulos com status "generated" que têm
artifact_id mas não têm audio_file local, e baixa cada um usando nlm CLI.

Uso:
    python download_audios.py              # baixa todos os pendentes de download
    python download_audios.py --chapters 1,3,5  # baixa capítulos específicos
    python download_audios.py --dry-run    # mostra o que faria
"""

import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
CHAPTER_INDEX = PROJECT_DIR / "chapter_index.json"
AUDIO_DIR = PROJECT_DIR / "audio"
NOTEBOOK_ID = "25aa1a74-f3e3-43d6-85db-32d2f5c21495"

# Status que indicam áudio gerado no NLM mas não baixado localmente
NEEDS_DOWNLOAD = {"generated", "generating"}


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}")


def load_index():
    with open(CHAPTER_INDEX, encoding="utf-8") as f:
        return json.load(f)


def save_index(index):
    with open(CHAPTER_INDEX, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def slugify(title):
    """Converte título em slug para nome de arquivo.

    Exemplos:
        'Adrenal Tumors' -> 'adrenal_tumors'
        'Cancer of the Colon' -> 'cancer_of_the_colon'
        'Non–small-cell Lung Cancer' -> 'non_small_cell_lung_cancer'
        'Immunotherapy Agents_ Monoclonal Antibodies' -> 'immunotherapy_agents_monoclonal_antibodies'
    """
    # Normalizar unicode (en-dash -> hyphen etc)
    s = unicodedata.normalize("NFKD", title)
    s = s.lower()
    # Remover underscores do título original (ex: "Agents_ Monoclonal")
    s = s.replace("_", " ")
    # Substituir tudo que não é alfanumérico por espaço
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    # Colapsar espaços múltiplos e trim
    s = re.sub(r"\s+", "_", s.strip())
    # Limitar tamanho para nomes razoáveis
    if len(s) > 60:
        s = s[:60].rsplit("_", 1)[0]
    return s


def make_filename(chapter):
    """Gera nome de arquivo no padrão mk_devita_ch###_slug.m4a"""
    ch_num = chapter["chapter_num"]
    slug = slugify(chapter["title"])
    return f"mk_devita_ch{ch_num:03d}_{slug}.m4a"


def download_audio(chapter):
    """Baixa áudio de um capítulo usando nlm CLI"""
    ch_num = chapter["chapter_num"]
    title = chapter["title"]
    artifact_id = chapter.get("artifact_id")

    if not artifact_id:
        log(f"Capítulo {ch_num} sem artifact_id — pulando", "WARN")
        return {"success": False, "error": "no_artifact_id"}

    filename = make_filename(chapter)
    output_path = AUDIO_DIR / filename

    if output_path.exists():
        log(f"Arquivo já existe: {filename} — pulando")
        return {"success": True, "filename": filename, "skipped": True}

    log(f"Baixando #{ch_num}: {title}")
    log(f"  Artifact: {artifact_id}")
    log(f"  Destino:  {filename}")

    cmd = [
        "nlm", "download", "audio",
        NOTEBOOK_ID,
        "--id", artifact_id,
        "-o", str(output_path),
        "--no-progress",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode == 0 and output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            log(f"  OK — {size_mb:.1f} MB")
            return {"success": True, "filename": filename}
        else:
            log(f"  ERRO (rc={result.returncode})", "ERROR")
            if result.stdout:
                log(f"  STDOUT: {result.stdout[:200]}", "ERROR")
            if result.stderr:
                log(f"  STDERR: {result.stderr[:200]}", "ERROR")
            return {"success": False, "error": result.stderr or result.stdout}

    except subprocess.TimeoutExpired:
        log("  Timeout (120s)", "ERROR")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        log(f"  Exceção: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def get_downloadable(index, chapter_nums=None):
    """Retorna capítulos que precisam de download."""
    chapters = []
    for ch in index["chapters"]:
        # Filtrar por números específicos se fornecidos
        if chapter_nums and ch["chapter_num"] not in chapter_nums:
            continue
        # Precisa download: tem artifact_id, status gerado, sem audio_file
        if (ch.get("artifact_id")
                and not ch.get("audio_file")
                and ch["status"] in NEEDS_DOWNLOAD):
            chapters.append(ch)
    return sorted(chapters, key=lambda c: c["chapter_num"])


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Download de áudios DeVita")
    parser.add_argument("--chapters", type=str, default=None,
                        help="Números dos capítulos (ex: 1,3,5). Se omitido, baixa todos pendentes.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que seria feito sem executar")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    index = load_index()

    chapter_nums = None
    if args.chapters:
        chapter_nums = [int(x.strip()) for x in args.chapters.split(",")]

    targets = get_downloadable(index, chapter_nums)

    if not targets:
        log("Nenhum áudio pendente de download.")
        return 0

    log(f"Áudios para baixar: {len(targets)}\n")
    for ch in targets:
        filename = make_filename(ch)
        log(f"  #{ch['chapter_num']:3d}  {ch['title'][:50]:<50s}  → {filename}")

    if args.dry_run:
        log("\nDRY RUN — nada será executado")
        return 0

    print()
    ok_count = 0
    fail_count = 0

    for i, ch in enumerate(targets, 1):
        log(f"\n[{i}/{len(targets)}] Baixando...")
        result = download_audio(ch)

        if result["success"]:
            # Atualizar índice
            for c in index["chapters"]:
                if c["chapter_num"] == ch["chapter_num"]:
                    c["audio_file"] = result["filename"]
                    c["status"] = "downloaded"
                    break
            save_index(index)
            ok_count += 1
        else:
            fail_count += 1

    # Resumo
    print()
    print("=" * 60)
    print("  RESUMO DO DOWNLOAD")
    print("=" * 60)
    print(f"  Sucesso: {ok_count}/{len(targets)}")
    print(f"  Falha:   {fail_count}/{len(targets)}")
    print()

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
