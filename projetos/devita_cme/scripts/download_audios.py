#!/usr/bin/env python3
"""
Baixa áudios gerados do NotebookLM para capítulos do DeVita.

Verifica studio status antes de baixar — só baixa artifacts "completed".

Uso:
    python download_audios.py              # baixa todos os pendentes de download
    python download_audios.py --chapters 1,3,5  # baixa capítulos específicos
    python download_audios.py --dry-run    # mostra o que faria
"""

import json
import os
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
PROFILE = "profissional"
NLM_BIN = Path.home() / ".local" / "bin" / "nlm"

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
    s = unicodedata.normalize("NFKD", title).lower().replace("_", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", "_", s.strip())
    if len(s) > 60:
        s = s[:60].rsplit("_", 1)[0]
    return s


def make_filename(chapter):
    ch_num = chapter["chapter_num"]
    slug = slugify(chapter["title"])
    return f"mk_devita_ch{ch_num:03d}_{slug}.m4a"


def get_studio_status():
    """Consulta nlm studio status e retorna mapa artifact_id → status."""
    env = {**os.environ, "NLM_PROFILE": PROFILE}
    cmd = [str(NLM_BIN), "studio", "status", NOTEBOOK_ID, "--json", "--profile", PROFILE]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        if result.returncode != 0:
            log(f"Erro ao verificar studio: {result.stderr[:300]}", "ERROR")
            return None
        studio_data = json.loads(result.stdout)
    except Exception as e:
        log(f"Erro ao verificar studio: {e}", "ERROR")
        return None

    artifact_status = {}
    for item in studio_data:
        if isinstance(item, dict) and "id" in item:
            artifact_status[item["id"]] = item.get("status", "unknown")
    return artifact_status


def download_audio(chapter, env):
    """Baixa áudio de um capítulo usando nlm CLI."""
    artifact_id = chapter.get("artifact_id")
    if not artifact_id:
        log(f"  ch{chapter['chapter_num']}: sem artifact_id — pulando", "WARN")
        return {"success": False, "error": "no_artifact_id"}

    filename = make_filename(chapter)
    output_path = AUDIO_DIR / filename

    if output_path.exists():
        log(f"  Arquivo já existe: {filename} — pulando")
        return {"success": True, "filename": filename, "skipped": True}

    log(f"  Baixando #{chapter['chapter_num']}: {chapter['title'][:40]}")
    log(f"    Artifact: {artifact_id}")

    cmd = [
        str(NLM_BIN), "download", "audio",
        NOTEBOOK_ID,
        "--id", artifact_id,
        "-o", str(output_path),
        "--no-progress",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)

        if result.returncode == 0 and output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            log(f"    OK — {size_mb:.1f} MB")
            return {"success": True, "filename": filename}
        else:
            log(f"    ERRO (rc={result.returncode})", "ERROR")
            if result.stderr:
                log(f"    {result.stderr[:200]}", "ERROR")
            return {"success": False, "error": result.stderr or result.stdout}

    except subprocess.TimeoutExpired:
        log("    Timeout (300s)", "ERROR")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        log(f"    Exceção: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def get_downloadable(index, chapter_nums=None):
    """Retorna capítulos que precisam de download."""
    chapters = []
    for ch in index["chapters"]:
        if chapter_nums and ch["chapter_num"] not in chapter_nums:
            continue
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
        log(f"  #{ch['chapter_num']:3d}  {ch['title'][:50]:<50s}  -> {filename}")

    if args.dry_run:
        log("\nDRY RUN — nada será executado")
        return 0

    # Verificar studio status antes de baixar
    log("\nConsultando studio status...")
    artifact_status = get_studio_status()
    if artifact_status is None:
        log("Não foi possível consultar studio. Abortando.", "ERROR")
        return 1

    # Filtrar apenas os que estão completed no studio
    ready = []
    not_ready = []
    for ch in targets:
        aid = ch.get("artifact_id")
        status = artifact_status.get(aid, "not_found")
        if status == "completed":
            ready.append(ch)
        elif status == "failed":
            log(f"  ch{ch['chapter_num']}: servidor falhou — marcando error", "WARN")
            ch["status"] = "error"
            save_index(index)
        else:
            not_ready.append((ch, status))

    if not_ready:
        log(f"\n{len(not_ready)} áudio(s) ainda não prontos:")
        for ch, st in not_ready:
            log(f"  ch{ch['chapter_num']:3d}: {st}")

    if not ready:
        log("\nNenhum áudio pronto para download no momento.")
        log("Aguarde ~15 min após a criação e tente novamente.")
        return 0

    log(f"\n{len(ready)} áudio(s) prontos para download:\n")

    env = {**os.environ, "NLM_PROFILE": PROFILE}
    ok_count = 0
    fail_count = 0

    for i, ch in enumerate(ready, 1):
        log(f"\n[{i}/{len(ready)}]")
        result = download_audio(ch, env)

        if result["success"]:
            ch["audio_file"] = result.get("filename", make_filename(ch))
            ch["status"] = "downloaded"
            ch["download_at"] = datetime.now().isoformat()
            save_index(index)
            ok_count += 1
        else:
            fail_count += 1

    # Resumo
    print()
    print("=" * 60)
    print("  RESUMO DO DOWNLOAD")
    print("=" * 60)
    print(f"  Sucesso: {ok_count}/{len(ready)}")
    print(f"  Falha:   {fail_count}/{len(ready)}")
    if not_ready:
        print(f"  Não prontos: {len(not_ready)} (aguardar e tentar novamente)")
    print()

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
