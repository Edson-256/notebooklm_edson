#!/usr/bin/env python3
"""
DeVita CME Audio Generator
Gera áudios deep-dive para capítulos específicos do DeVita 12ª ed.
Usa --source-ids para focar no capítulo correto e --focus para o prompt.
"""

import subprocess
import json
import time
import re
import sys
import unicodedata
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CHAPTER_INDEX = PROJECT_DIR / "chapter_index.json"
PROMPTS_DIR = PROJECT_DIR / "prompts" / "chapters"
AUDIO_DIR = PROJECT_DIR / "audio"
NOTEBOOK_ID = "25aa1a74-f3e3-43d6-85db-32d2f5c21495"
PROFILE = "profissional"
INTERVAL_SECONDS = 120  # 2 min entre gerações


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
    """Converte título em slug para nome de arquivo."""
    s = unicodedata.normalize("NFKD", title).lower().replace("_", " ")
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", "_", s.strip())
    if len(s) > 60:
        s = s[:60].rsplit("_", 1)[0]
    return s


def make_filename(chapter):
    """Gera nome de arquivo no padrão mk_devita_ch###_slug.m4a"""
    return f"mk_devita_ch{chapter['chapter_num']:03d}_{slugify(chapter['title'])}.m4a"


def download_audio(chapter):
    """Baixa áudio gerado do NotebookLM para arquivo local."""
    artifact_id = chapter.get("artifact_id")
    if not artifact_id:
        log("Sem artifact_id — download ignorado", "WARN")
        return None

    filename = make_filename(chapter)
    output_path = AUDIO_DIR / filename

    if output_path.exists():
        log(f"Arquivo já existe: {filename}")
        return filename

    log(f"Baixando áudio → {filename}")
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
            log(f"Download OK — {size_mb:.1f} MB")
            return filename
        else:
            log(f"Download FALHA (rc={result.returncode})", "ERROR")
            if result.stderr:
                log(f"  {result.stderr[:200]}", "ERROR")
            return None
    except Exception as e:
        log(f"Download exceção: {e}", "ERROR")
        return None


def load_prompt(chapter_num):
    """Carrega prompt customizado do capítulo"""
    # Procura por qualquer arquivo que comece com o número do capítulo
    for p in PROMPTS_DIR.iterdir():
        if p.name.startswith(f"ch{chapter_num:03d}"):
            return p.read_text(encoding="utf-8").strip()
    return None


def generate_audio(chapter):
    """Gera áudio para um capítulo usando nlm CLI"""
    ch_num = chapter["chapter_num"]
    title = chapter["title"]
    source_id = chapter["source_id"]

    log(f"=== Capítulo {ch_num}: {title} ===")

    # Carregar prompt customizado
    prompt = load_prompt(ch_num)
    if not prompt:
        log(f"Sem prompt customizado para ch{ch_num:03d}, usando título", "WARN")
        prompt = f"Deep-dive em português brasileiro sobre {title} do DeVita 12ª ed para oncologista cirúrgico"

    # Truncar prompt a 2500 chars (limite NLM Pro)
    if len(prompt) > 2500:
        prompt = prompt[:2497] + "..."
        log(f"Prompt truncado a 2500 chars", "WARN")

    cmd = [
        "nlm", "create", "audio",
        NOTEBOOK_ID,
        "--format", "deep_dive",
        "--language", "pt-BR",
        "--length", "long",
        "--focus", prompt,
        "--source-ids", source_id,
        "--profile", PROFILE,
        "--confirm"
    ]

    log(f"Gerando áudio (source: {source_id[:8]}...)")
    log(f"Focus ({len(prompt)} chars): {prompt[:100]}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0:
            output = result.stdout
            log(f"Comando executado com sucesso")
            log(f"Output: {output[:300]}")

            # Tentar extrair artifact ID
            artifact_match = re.search(r'(?:Artifact|Audio|ID)[:\s]+([a-f0-9-]{20,})', output, re.IGNORECASE)
            if artifact_match:
                artifact_id = artifact_match.group(1)
                log(f"Artifact ID: {artifact_id}")
                return {"success": True, "artifact_id": artifact_id, "output": output}

            return {"success": True, "artifact_id": None, "output": output}
        else:
            log(f"ERRO (rc={result.returncode})", "ERROR")
            log(f"STDOUT: {result.stdout[:300]}", "ERROR")
            log(f"STDERR: {result.stderr[:300]}", "ERROR")
            return {"success": False, "error": result.stderr}

    except subprocess.TimeoutExpired:
        log("Timeout (180s)", "ERROR")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        log(f"Exceção: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def update_chapter_status(index, ch_num, status, artifact_id=None, audio_file=None):
    """Atualiza status do capítulo no índice"""
    for ch in index["chapters"]:
        if ch["chapter_num"] == ch_num:
            ch["status"] = status
            if artifact_id:
                ch["artifact_id"] = artifact_id
            if audio_file:
                ch["audio_file"] = audio_file
            ch["audio_generated_at"] = datetime.now().isoformat()
            break
    save_index(index)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeVita CME Audio Generator")
    parser.add_argument("--chapters", type=str, required=True,
                        help="Números dos capítulos (ex: 13,26,37,62,81)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que seria feito sem executar")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    index = load_index()
    chapter_nums = [int(x.strip()) for x in args.chapters.split(",")]

    # Mapear capítulos
    targets = []
    for num in chapter_nums:
        for ch in index["chapters"]:
            if ch["chapter_num"] == num:
                targets.append(ch)
                break
        else:
            log(f"Capítulo {num} não encontrado no índice!", "ERROR")

    if not targets:
        log("Nenhum capítulo válido selecionado", "ERROR")
        return 1

    log(f"Capítulos selecionados: {len(targets)}")
    for t in targets:
        prompt = load_prompt(t["chapter_num"])
        prompt_status = f"({len(prompt)} chars)" if prompt else "(sem prompt)"
        log(f"  #{t['chapter_num']:3d} | {t['title']} | {prompt_status}")

    if args.dry_run:
        log("DRY RUN — nada será executado")
        return 0

    print()
    results = []
    for i, ch in enumerate(targets, 1):
        log(f"\n[{i}/{len(targets)}] Processando...")
        update_chapter_status(index, ch["chapter_num"], "generating")

        result = generate_audio(ch)
        results.append({"chapter": ch["title"], "num": ch["chapter_num"], **result})

        if result["success"]:
            update_chapter_status(index, ch["chapter_num"], "generated",
                                  result.get("artifact_id"))
            log(f"Geração OK: {ch['title']}")

            # Baixar áudio imediatamente
            # Recarregar capítulo com artifact_id atualizado
            index = load_index()
            ch_updated = next(
                (c for c in index["chapters"] if c["chapter_num"] == ch["chapter_num"]),
                ch
            )
            audio_file = download_audio(ch_updated)
            if audio_file:
                update_chapter_status(index, ch["chapter_num"], "downloaded",
                                      audio_file=audio_file)
                index = load_index()
                results[-1]["audio_file"] = audio_file
        else:
            update_chapter_status(index, ch["chapter_num"], "error")
            log(f"FALHA: {ch['title']}", "ERROR")

        # Intervalo entre gerações
        if i < len(targets):
            log(f"Aguardando {INTERVAL_SECONDS}s antes do próximo...")
            time.sleep(INTERVAL_SECONDS)

    # Resumo
    print()
    print("=" * 60)
    print("  RESUMO DA GERAÇÃO")
    print("=" * 60)
    ok = sum(1 for r in results if r["success"])
    fail = sum(1 for r in results if not r["success"])
    print(f"  Sucesso: {ok}/{len(results)}")
    print(f"  Falha:   {fail}/{len(results)}")
    print()
    for r in results:
        if not r["success"]:
            tag = "FALHA"
        elif r.get("audio_file"):
            tag = "BAIXADO"
        else:
            tag = "GERADO"
        print(f"  [{tag:7s}] #{r['num']:3d} {r['chapter']}")
    print()

    # Salvar log de resultados
    log_path = PROJECT_DIR / f"generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    log(f"Log salvo: {log_path}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
