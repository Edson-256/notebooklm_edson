#!/usr/bin/env python3
"""
Cálculo Munem-Foulis Audio Generator
Gera áudios deep-dive para seções do Cálculo Munem-Foulis via nlm CLI.
Usa fire-and-forget: Fase 1 (criar) + Fase 2 (download).

Uso:
    python3 calculo_runner.py --max-sections 5            # Criar 5 áudios
    python3 calculo_runner.py --sections 1,2,3            # Seções específicas
    python3 calculo_runner.py --download                   # Baixar prontos
    python3 calculo_runner.py --dry-run                    # Ver o que faria
    python3 calculo_runner.py --status                     # Ver status geral
"""

import subprocess
import json
import time
import re
import sys
import os
from pathlib import Path
from datetime import datetime

# === Configuração ===
PROJECT_DIR = Path(__file__).parent
INDEX_FILE = PROJECT_DIR / "section_index.json"
AUDIO_DIR = PROJECT_DIR / "munem_vol1" / "audios"
NOTEBOOK_ID = "0c022710-25e0-44e2-9bfa-0d6daa219c17"
PROFILE = "profissional"
INTERVAL_SECONDS = 120  # 2 min entre gerações
NLM_BIN = Path.home() / ".local" / "bin" / "nlm"

# === Prompt Template ===
PROMPT_TEMPLATE = """Act as an Expert Mathematics Educator creating a Deep Dive audio in Brazilian Portuguese (PT-BR). Target audience: students new to Calculus with solid high school math background.

Instructions: Start with a real-world hook. Bridge from high school math to this Calculus concept. Break down definitions, theorems and formulas without jargon — explain the "why". Walk through a key example verbally (audio-first, describe symbols in words). Recap for long-term retention. Be rigorous but conversational.

Constraints: Maintain accuracy per Munem-Foulis textbook. Calibrate for high school background. Script must be long and detailed for a Deep Dive session.

Section: Capítulo {chapter}: {chapter_title} — Seção {section}: {title}"""


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {level}: {msg}")


def load_index():
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_prompt(sec):
    """Constrói prompt customizado para a seção (max 2500 chars)."""
    prompt = PROMPT_TEMPLATE.format(
        chapter=sec["chapter"],
        chapter_title=sec["chapter_title"],
        section=sec["section"],
        title=sec["title"]
    )
    if len(prompt) > 2500:
        prompt = prompt[:2497] + "..."
        log(f"Prompt truncado a 2500 chars", "WARN")
    return prompt


def create_audio(sec):
    """Dispara criação de áudio via nlm CLI. Retorna resultado."""
    prompt = build_prompt(sec)

    cmd = [
        str(NLM_BIN), "create", "audio",
        NOTEBOOK_ID,
        "--format", "deep_dive",
        "--language", "pt-BR",
        "--length", "long",
        "--focus", prompt,
        "--source-ids", sec["source_id"],
        "--profile", PROFILE,
        "--confirm"
    ]

    log(f"Criando áudio: {sec['slug']}")
    log(f"Source: {sec['source_id'][:12]}...")
    log(f"Focus ({len(prompt)} chars): {prompt[:80]}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0:
            output = result.stdout
            log(f"Comando OK")

            # Tentar extrair artifact ID
            artifact_match = re.search(
                r'(?:Artifact|Audio|ID)[:\s]+([a-f0-9-]{20,})',
                output, re.IGNORECASE
            )
            artifact_id = artifact_match.group(1) if artifact_match else None

            if artifact_id:
                log(f"Artifact ID: {artifact_id}")
            else:
                # Tentar outro padrão
                uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', output)
                if uuid_match:
                    artifact_id = uuid_match.group(1)
                    log(f"Artifact ID (regex): {artifact_id}")
                else:
                    log(f"Artifact ID não encontrado no output")
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
    """Fase 2: Baixa áudios com status 'created' que já estão prontos."""
    data = load_index()
    created = [s for s in data["sections"] if s.get("status") == "created"]

    if not created:
        log("Nenhum áudio pendente de download (status='created')")
        return

    log(f"Verificando {len(created)} áudios pendentes...")

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
    for sec in created:
        aid = sec.get("artifact_id")
        if not aid:
            log(f"  {sec['slug']}: sem artifact_id, pulando", "WARN")
            continue

        status = artifact_status.get(aid, "not_found")

        if status == "completed":
            output_path = AUDIO_DIR / f"mf_{sec['slug']}.m4a"
            log(f"  Baixando: {sec['slug']}...")

            dl_cmd = [
                str(NLM_BIN), "download", "audio", NOTEBOOK_ID,
                "--id", aid,
                "-o", str(output_path),
                "--no-progress"
            ]

            try:
                dl_result = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=300, env=env)
                if dl_result.returncode == 0:
                    size = output_path.stat().st_size if output_path.exists() else 0
                    sec["status"] = "downloaded"
                    sec["output_path"] = str(output_path)
                    sec["tamanho_bytes"] = size
                    sec["download_at"] = datetime.now().isoformat()
                    downloaded += 1
                    log(f"  ✓ Baixado: {output_path.name} ({size/1024/1024:.1f} MB)")
                else:
                    log(f"  ✗ Erro download: {dl_result.stderr[:200]}", "ERROR")
                    sec["status"] = "download_failed"
            except Exception as e:
                log(f"  ✗ Exceção: {e}", "ERROR")

        elif status == "failed":
            log(f"  ✗ {sec['slug']}: servidor falhou", "WARN")
            sec["status"] = "server_failed"
        elif status == "not_found":
            log(f"  ? {sec['slug']}: artifact não encontrado no studio", "WARN")
        else:
            log(f"  ⏳ {sec['slug']}: {status}")

    save_index(data)
    log(f"\nDownload concluído: {downloaded} baixados de {len(created)} pendentes")


def show_status():
    """Mostra status geral de todas as seções."""
    data = load_index()
    counts = {}
    for sec in data["sections"]:
        s = sec.get("status", "pending")
        counts[s] = counts.get(s, 0) + 1

    print("\n" + "=" * 60)
    print("  STATUS GERAL — Cálculo Munem-Foulis")
    print("=" * 60)
    total = len(data["sections"])
    for status, count in sorted(counts.items()):
        bar = "█" * int(count / total * 40)
        print(f"  {status:20s}: {count:3d}/{total} {bar}")

    failed = counts.get("failed", 0)
    if failed > 0:
        print(f"\n  ⚠  {failed} seções falharam. Use --retry-failed para reprocessar:")
        print(f"     python3 calculo_runner.py --retry-failed --max-sections {failed}")
    print()

    # Detalhes por capítulo
    chapters = {}
    for sec in data["sections"]:
        ch = sec["chapter"]
        if ch not in chapters:
            chapters[ch] = {"title": sec["chapter_title"], "sections": []}
        chapters[ch]["sections"].append(sec)

    for ch_num in sorted(chapters.keys()):
        ch = chapters[ch_num]
        statuses = [s.get("status", "pending") for s in ch["sections"]]
        done = sum(1 for s in statuses if s in ("downloaded", "created"))
        total_ch = len(ch["sections"])
        print(f"  Cap. {ch_num:2d} — {ch['title'][:40]:40s} [{done}/{total_ch}]")
        for sec in ch["sections"]:
            icon = {"pending": "⬜", "created": "🟡", "downloaded": "✅",
                    "failed": "❌", "server_failed": "❌", "download_failed": "🔴",
                    "generating": "⏳"}.get(sec.get("status", "pending"), "?")
            print(f"         {icon} S{sec['section']} {sec['title'][:50]}")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cálculo Munem-Foulis Audio Generator")
    parser.add_argument("--max-sections", type=int, default=50,
                        help="Número máximo de seções a processar (default: 50)")
    parser.add_argument("--sections", type=str,
                        help="IDs específicos das seções (ex: 1,2,3)")
    parser.add_argument("--download", action="store_true",
                        help="Modo download: baixar áudios prontos")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar o que seria feito sem executar")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Reprocessar seções com status 'failed'")
    parser.add_argument("--status", action="store_true",
                        help="Mostrar status geral")
    args = parser.parse_args()

    if args.status:
        show_status()
        return 0

    if args.download:
        download_audios()
        return 0

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    data = load_index()

    # Resetar seções failed para pending se --retry-failed
    if args.retry_failed:
        failed_count = 0
        for sec in data["sections"]:
            if sec.get("status") == "failed":
                sec["status"] = "pending"
                sec.pop("error", None)
                failed_count += 1
        if failed_count:
            save_index(data)
            log(f"Reset: {failed_count} seções 'failed' → 'pending'")
        else:
            log("Nenhuma seção com status 'failed' encontrada")

    # Selecionar seções
    if args.sections:
        ids = [int(x.strip()) for x in args.sections.split(",")]
        targets = [s for s in data["sections"] if s["id"] in ids]
    else:
        # Pegar seções pendentes (não criadas ainda)
        targets = [s for s in data["sections"]
                    if s.get("status", "pending") == "pending"]
        targets = targets[:args.max_sections]

    if not targets:
        log("Nenhuma seção pendente para processar")
        return 0

    log(f"Seções selecionadas: {len(targets)}")
    for t in targets:
        prompt = build_prompt(t)
        log(f"  #{t['id']:2d} | Cap.{t['chapter']:2d} S{t['section']} | {t['title'][:50]} | ({len(prompt)} chars)")

    if args.dry_run:
        log("DRY RUN — nada será executado")
        return 0

    print()
    results = []
    for i, sec in enumerate(targets, 1):
        log(f"\n[{i}/{len(targets)}] Processando seção #{sec['id']}...")
        sec["status"] = "generating"
        save_index(data)

        result = create_audio(sec)
        results.append({"section_id": sec["id"], "slug": sec["slug"], **result})

        if result["success"]:
            sec["status"] = "created"
            sec["artifact_id"] = result.get("artifact_id")
            sec["created_at"] = datetime.now().isoformat()
            log(f"✓ OK: {sec['slug']}")
        else:
            sec["status"] = "failed"
            sec["error"] = result.get("error", "unknown")
            log(f"✗ FALHA: {sec['slug']}", "ERROR")

        save_index(data)

        # Intervalo entre gerações
        if i < len(targets):
            log(f"Aguardando {INTERVAL_SECONDS}s antes da próxima...")
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
        status = "✓" if r.get("success") else "✗"
        print(f"  [{status}] #{r['section_id']:2d} {r['slug']}")
    print()
    print(f"  Próximo passo: python3 calculo_runner.py --download")
    print(f"  (aguardar ~15 min após última criação)")
    print()

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
