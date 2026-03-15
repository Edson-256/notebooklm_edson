#!/usr/bin/env python3
"""
DeVita CME Audio Generator
Gera áudios deep-dive para capítulos específicos do DeVita 12ª ed.
Usa fire-and-forget: Fase 1 (criar) + Fase 2 (download separado).

Uso:
    python3 generate_devita_audio.py --chapters 13,26,37    # Criar áudios
    python3 generate_devita_audio.py --download              # Baixar prontos
    python3 generate_devita_audio.py --dry-run --chapters 13 # Ver o que faria
"""

import subprocess
import json
import os
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
NLM_BIN = Path.home() / ".local" / "bin" / "nlm"


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


def load_prompt(chapter_num):
    """Carrega prompt customizado do capítulo."""
    for p in PROMPTS_DIR.iterdir():
        if p.name.startswith(f"ch{chapter_num:03d}"):
            return p.read_text(encoding="utf-8").strip()
    return None


def create_audio(chapter):
    """Dispara criação de áudio via nlm CLI. Retorna resultado."""
    ch_num = chapter["chapter_num"]
    title = chapter["title"]
    source_id = chapter["source_id"]

    log(f"=== Capítulo {ch_num}: {title} ===")

    prompt = load_prompt(ch_num)
    if not prompt:
        log(f"Sem prompt customizado para ch{ch_num:03d}, usando título", "WARN")
        prompt = f"Deep-dive em português brasileiro sobre {title} do DeVita 12ª ed para oncologista cirúrgico"

    if len(prompt) > 2500:
        prompt = prompt[:2497] + "..."
        log("Prompt truncado a 2500 chars", "WARN")

    cmd = [
        str(NLM_BIN), "create", "audio",
        NOTEBOOK_ID,
        "--format", "deep_dive",
        "--language", "pt-BR",
        "--length", "long",
        "--focus", prompt,
        "--source-ids", source_id,
        "--profile", PROFILE,
        "--confirm"
    ]

    log(f"Criando áudio (source: {source_id[:8]}...)")
    log(f"Focus ({len(prompt)} chars): {prompt[:100]}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0:
            output = result.stdout
            log("Comando OK")

            # Tentar extrair artifact ID
            artifact_match = re.search(
                r'(?:Artifact|Audio|ID)[:\s]+([a-f0-9-]{20,})',
                output, re.IGNORECASE
            )
            artifact_id = artifact_match.group(1) if artifact_match else None

            if artifact_id:
                log(f"Artifact ID: {artifact_id}")
            else:
                # Fallback: qualquer UUID no output
                uuid_match = re.search(
                    r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
                    output
                )
                if uuid_match:
                    artifact_id = uuid_match.group(1)
                    log(f"Artifact ID (regex): {artifact_id}")
                else:
                    log("Artifact ID não encontrado no output")
                    log(f"Output completo: {output[:500]}")

            return {"success": True, "artifact_id": artifact_id, "output": output}
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


def download_audios():
    """Fase 2: Baixa áudios com status 'generated' que já estão prontos no NLM."""
    index = load_index()
    generated = [
        ch for ch in index["chapters"]
        if ch.get("status") == "generated" and ch.get("artifact_id") and not ch.get("audio_file")
    ]

    if not generated:
        log("Nenhum áudio pendente de download (status='generated')")
        return

    log(f"Verificando {len(generated)} áudios pendentes...")

    # Obter status do studio
    env = {**os.environ, "NLM_PROFILE": PROFILE}
    cmd = [str(NLM_BIN), "studio", "status", NOTEBOOK_ID, "--json", "--profile", PROFILE]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
        if result.returncode != 0:
            log(f"Erro ao verificar studio: {result.stderr[:300]}", "ERROR")
            return
        studio_data = json.loads(result.stdout)
    except Exception as e:
        log(f"Erro ao verificar studio: {e}", "ERROR")
        return

    # Mapear artifact_id → status
    artifact_status = {}
    for item in studio_data:
        if isinstance(item, dict) and "id" in item:
            artifact_status[item["id"]] = item.get("status", "unknown")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    for ch in generated:
        aid = ch.get("artifact_id")
        status = artifact_status.get(aid, "not_found")

        if status == "completed":
            output_path = AUDIO_DIR / make_filename(ch)
            log(f"  Baixando: ch{ch['chapter_num']} {ch['title'][:40]}...")

            dl_cmd = [
                str(NLM_BIN), "download", "audio", NOTEBOOK_ID,
                "--id", aid,
                "-o", str(output_path),
                "--no-progress",
            ]

            try:
                dl_result = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=300, env=env)
                if dl_result.returncode == 0 and output_path.exists():
                    size = output_path.stat().st_size
                    ch["status"] = "downloaded"
                    ch["audio_file"] = output_path.name
                    ch["download_at"] = datetime.now().isoformat()
                    downloaded += 1
                    log(f"  OK: {output_path.name} ({size / 1024 / 1024:.1f} MB)")
                else:
                    log(f"  ERRO download (rc={dl_result.returncode}): {dl_result.stderr[:200]}", "ERROR")
            except Exception as e:
                log(f"  Exceção: {e}", "ERROR")

        elif status == "failed":
            log(f"  ch{ch['chapter_num']}: servidor falhou — marcando error", "WARN")
            ch["status"] = "error"
        elif status == "not_found":
            log(f"  ch{ch['chapter_num']}: artifact não encontrado no studio", "WARN")
        else:
            log(f"  ch{ch['chapter_num']}: {status} (ainda processando)")

    save_index(index)
    log(f"\nDownload concluído: {downloaded} baixados de {len(generated)} pendentes")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeVita CME Audio Generator")
    parser.add_argument("--chapters", type=str,
                        help="Números dos capítulos (ex: 13,26,37,62,81)")
    parser.add_argument("--download", action="store_true",
                        help="Modo download: baixar áudios prontos no NLM")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra o que seria feito sem executar")
    args = parser.parse_args()

    if args.download:
        download_audios()
        return 0

    if not args.chapters:
        parser.error("--chapters é obrigatório no modo criação (ou use --download)")

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
        log(f"\n[{i}/{len(targets)}] Processando ch{ch['chapter_num']}...")

        # Marcar como generating
        for c in index["chapters"]:
            if c["chapter_num"] == ch["chapter_num"]:
                c["status"] = "generating"
                break
        save_index(index)

        result = create_audio(ch)
        results.append({"chapter": ch["title"], "num": ch["chapter_num"], **result})

        if result["success"]:
            for c in index["chapters"]:
                if c["chapter_num"] == ch["chapter_num"]:
                    c["status"] = "generated"
                    c["artifact_id"] = result.get("artifact_id")
                    c["audio_generated_at"] = datetime.now().isoformat()
                    break
            save_index(index)
            log(f"OK: {ch['title']}")
        else:
            for c in index["chapters"]:
                if c["chapter_num"] == ch["chapter_num"]:
                    c["status"] = "error"
                    c["error"] = result.get("error", "unknown")
                    break
            save_index(index)
            log(f"FALHA: {ch['title']}", "ERROR")

        # Intervalo entre gerações
        if i < len(targets):
            log(f"Aguardando {INTERVAL_SECONDS}s antes do próximo...")
            try:
                time.sleep(INTERVAL_SECONDS)
            except KeyboardInterrupt:
                log("\nCtrl+C — parando com segurança")
                break

    # Resumo
    print()
    print("=" * 60)
    print("  RESUMO DA GERAÇÃO")
    print("=" * 60)
    ok = sum(1 for r in results if r.get("success"))
    fail = sum(1 for r in results if not r.get("success"))
    print(f"  Sucesso: {ok}/{len(results)}")
    print(f"  Falha:   {fail}/{len(results)}")
    print()
    for r in results:
        status = "OK" if r.get("success") else "FALHA"
        print(f"  [{status:5s}] #{r['num']:3d} {r['chapter']}")
    print()
    print(f"  Próximo passo: python3 {Path(__file__).name} --download")
    print(f"  (aguardar ~15 min após última criação)")
    print()

    # Salvar log de resultados
    log_path = PROJECT_DIR / f"generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    log(f"Log salvo: {log_path}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
