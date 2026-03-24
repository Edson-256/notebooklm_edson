#!/usr/bin/env python3
"""
Curriculum Audio Generator — Stack Completa m_dermato
Gera áudios educativos (slides + áudio) para cada módulo do curriculum via nlm CLI.
Usa fire-and-forget: Fase 1 (criar) + Fase 2 (download).

Cada módulo tem 2 variantes:
  - "a" (slides/apresentação)
  - "b" (áudio educativo: deep_dive, brief, critique ou debate)

Uso:
    python3 curriculum_runner.py --max 5                  # Criar próximos 5 itens pendentes
    python3 curriculum_runner.py --max 10                 # Criar próximos 10
    python3 curriculum_runner.py --modules 1,2,3          # Módulos específicos (ambas variantes)
    python3 curriculum_runner.py --modules 1a,3b          # Variantes específicas
    python3 curriculum_runner.py --download               # Baixar prontos
    python3 curriculum_runner.py --dry-run --max 5        # Ver o que faria
    python3 curriculum_runner.py --status                 # Status geral
    python3 curriculum_runner.py --retry-failed           # Reprocessar falhas
"""

import subprocess
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

# === Configuração ===
PROJECT_DIR = Path(__file__).parent
INDEX_FILE = PROJECT_DIR / "module_index.json"
PROMPTS_DIR = PROJECT_DIR / "prompts"
AUDIO_DIR = PROJECT_DIR / "audios"
PROFILE = "profissional"
INTERVAL_SECONDS = 120  # 2 min entre gerações (rate limit Google)
NLM_BIN = Path.home() / ".local" / "bin" / "nlm"

# Mapeamento variante "a" → formato de áudio fixo (slides são sempre deep_dive)
VARIANT_A_FORMAT = "deep_dive"


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": " ", "WARN": "⚠", "ERROR": "✗"}.get(level, " ")
    print(f"[{ts}] {prefix} {msg}")


def load_index():
    with open(INDEX_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def check_auth():
    """Verifica se autenticação nlm está válida. Retorna True/False."""
    log("Verificando autenticação nlm...")
    try:
        result = subprocess.run(
            [str(NLM_BIN), "login", "--check", "--profile", PROFILE],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log("Autenticação OK")
            return True
        else:
            log("Autenticação EXPIRADA ou inválida!", "ERROR")
            log(f"Execute: nlm login --profile {PROFILE}", "ERROR")
            log(f"Output: {result.stderr[:200]}", "ERROR")
            return False
    except FileNotFoundError:
        log(f"nlm não encontrado em {NLM_BIN}", "ERROR")
        log("Execute: export PATH=\"$HOME/.local/bin:$PATH\"", "ERROR")
        return False
    except Exception as e:
        log(f"Erro ao verificar auth: {e}", "ERROR")
        return False


def resolve_notebook_id(data, tech):
    """Resolve notebook_id pelo mapeamento tech → notebook."""
    nmap = data.get("notebook_map", {})
    return nmap.get(tech)


def load_prompt(filename):
    """Carrega conteúdo do prompt e extrai o texto para --focus."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    # O prompt inteiro vai como --focus (max 2500 chars)
    if len(text) > 2500:
        text = text[:2497] + "..."
        log(f"Prompt {filename} truncado a 2500 chars", "WARN")
    return text


def extract_audio_format(prompt_text):
    """Extrai formato de áudio do prompt (Audio format: XXX)."""
    match = re.search(r'Audio format:\s*(\w+)', prompt_text)
    if match:
        return match.group(1)
    return None


def build_targets(data, args):
    """Constrói lista de targets [(module, variant)] a processar."""
    targets = []

    if args.modules:
        # Parse: "1,2,3" → ambas variantes; "1a,3b" → variantes específicas
        for item in args.modules.split(","):
            item = item.strip()
            match = re.match(r'^(\d+)([ab])?$', item)
            if not match:
                log(f"Formato inválido: '{item}' (use: 1, 2a, 3b)", "ERROR")
                continue
            mod_id = int(match.group(1))
            variant = match.group(2)

            mod = next((m for m in data["modules"] if m["id"] == mod_id), None)
            if not mod:
                log(f"Módulo {mod_id} não encontrado no índice", "ERROR")
                continue

            if variant:
                targets.append((mod, variant))
            else:
                targets.append((mod, "a"))
                targets.append((mod, "b"))
    else:
        # Pegar próximos pendentes em ordem
        for mod in data["modules"]:
            for v in ["a", "b"]:
                status_key = f"status_{v}"
                if mod.get(status_key, "pending") == "pending":
                    targets.append((mod, v))

        targets = targets[:args.max]

    # Filtrar targets sem notebook_id configurado
    valid = []
    for mod, v in targets:
        nb = resolve_notebook_id(data, mod["tech"])
        if nb:
            valid.append((mod, v))
        else:
            log(f"PULANDO {mod['module']}{v}: notebook não configurado para '{mod['tech']}'", "WARN")
    return valid


def create_audio(mod, variant, notebook_id, data):
    """Dispara criação de áudio via nlm CLI."""
    prompt_key = f"prompt_{variant}"
    prompt_file = mod[prompt_key]
    prompt_text = load_prompt(prompt_file)

    if not prompt_text:
        log(f"Prompt não encontrado: {prompt_file}", "ERROR")
        return {"success": False, "error": f"prompt not found: {prompt_file}"}

    # Determinar formato: variante "b" usa o formato do módulo, "a" usa deep_dive
    if variant == "b":
        audio_format = extract_audio_format(prompt_text) or mod.get("audio_format", "deep_dive")
    else:
        audio_format = VARIANT_A_FORMAT

    slug = f"mk_curriculum_{mod['module']}_{variant}"
    log(f"Criando: {slug} ({audio_format})")
    log(f"Prompt: {prompt_file} ({len(prompt_text)} chars)")

    cmd = [
        str(NLM_BIN), "create", "audio",
        notebook_id,
        "--format", audio_format,
        "--language", "pt-BR",
        "--length", "long",
        "--focus", prompt_text,
        "--profile", PROFILE,
        "--confirm"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0:
            output = result.stdout
            log("Comando OK")

            # Extrair artifact ID
            artifact_match = re.search(
                r'(?:Artifact|Audio|ID)[:\s]+([a-f0-9-]{20,})',
                output, re.IGNORECASE
            )
            artifact_id = artifact_match.group(1) if artifact_match else None

            if not artifact_id:
                uuid_match = re.search(
                    r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
                    output
                )
                if uuid_match:
                    artifact_id = uuid_match.group(1)
                    log(f"Artifact ID (regex): {artifact_id}")
                else:
                    log("Artifact ID não encontrado no output")
                    log(f"Output: {output[:500]}")
            else:
                log(f"Artifact ID: {artifact_id}")

            return {"success": True, "artifact_id": artifact_id, "format": audio_format}
        else:
            log(f"ERRO (rc={result.returncode})", "ERROR")
            log(f"STDOUT: {result.stdout[:300]}", "ERROR")
            log(f"STDERR: {result.stderr[:300]}", "ERROR")
            return {"success": False, "error": result.stderr[:300]}

    except subprocess.TimeoutExpired:
        log("Timeout (180s)", "ERROR")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        log(f"Exceção: {e}", "ERROR")
        return {"success": False, "error": str(e)}


def download_audios():
    """Fase 2: Baixa áudios com status 'created' que estão prontos."""
    data = load_index()

    # Coletar todos os items com status created
    created_items = []
    for mod in data["modules"]:
        for v in ["a", "b"]:
            if mod.get(f"status_{v}") == "created" and mod.get(f"artifact_id_{v}"):
                created_items.append((mod, v))

    if not created_items:
        log("Nenhum áudio pendente de download (status='created')")
        return

    log(f"Verificando {len(created_items)} áudios pendentes...")

    # Precisamos verificar cada notebook_id único
    notebooks_used = set()
    for mod, v in created_items:
        nb = mod.get(f"notebook_id_{v}") or resolve_notebook_id(data, mod["tech"])
        if nb:
            notebooks_used.add(nb)

    # Obter status de todos os studios
    artifact_status_map = {}
    env = {**os.environ, "NLM_PROFILE": PROFILE}
    for nb_id in notebooks_used:
        cmd = [str(NLM_BIN), "studio", "status", nb_id, "--json", "--profile", PROFILE]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
            if result.returncode == 0:
                studio_data = json.loads(result.stdout)
                for item in studio_data:
                    if isinstance(item, dict) and "id" in item:
                        artifact_status_map[item["id"]] = item.get("status", "unknown")
            else:
                log(f"Erro studio {nb_id[:8]}: {result.stderr[:200]}", "ERROR")
        except Exception as e:
            log(f"Erro studio {nb_id[:8]}: {e}", "ERROR")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = 0

    for mod, v in created_items:
        aid = mod.get(f"artifact_id_{v}")
        nb_id = mod.get(f"notebook_id_{v}") or resolve_notebook_id(data, mod["tech"])
        slug = f"mk_curriculum_{mod['module']}_{v}"
        status = artifact_status_map.get(aid, "not_found")

        if status == "completed":
            output_path = AUDIO_DIR / f"{slug}.m4a"
            log(f"  Baixando: {slug}...")

            dl_cmd = [
                str(NLM_BIN), "download", "audio", nb_id,
                "--id", aid,
                "-o", str(output_path),
                "--no-progress"
            ]

            try:
                dl_result = subprocess.run(dl_cmd, capture_output=True, text=True, timeout=300, env=env)
                if dl_result.returncode == 0 and output_path.exists():
                    size = output_path.stat().st_size
                    mod[f"status_{v}"] = "downloaded"
                    mod[f"output_path_{v}"] = str(output_path)
                    mod[f"tamanho_bytes_{v}"] = size
                    mod[f"download_at_{v}"] = datetime.now().isoformat()
                    downloaded += 1
                    log(f"  ✓ {slug} ({size / 1024 / 1024:.1f} MB)")
                else:
                    log(f"  ✗ Erro download: {dl_result.stderr[:200]}", "ERROR")
                    mod[f"status_{v}"] = "download_failed"
            except Exception as e:
                log(f"  ✗ Exceção: {e}", "ERROR")

        elif status == "failed":
            log(f"  ✗ {slug}: servidor falhou", "WARN")
            mod[f"status_{v}"] = "server_failed"
        elif status == "not_found":
            log(f"  ? {slug}: artifact não encontrado no studio", "WARN")
        else:
            log(f"  ⏳ {slug}: {status}")

    save_index(data)
    log(f"\nDownload: {downloaded} baixados de {len(created_items)} pendentes")


def show_status():
    """Mostra status geral de todos os módulos."""
    data = load_index()

    counts = {"pending": 0, "created": 0, "downloaded": 0,
              "failed": 0, "server_failed": 0, "download_failed": 0, "generating": 0}
    total_items = 0

    for mod in data["modules"]:
        for v in ["a", "b"]:
            s = mod.get(f"status_{v}", "pending")
            counts[s] = counts.get(s, 0) + 1
            total_items += 1

    print()
    print("=" * 65)
    print("  STATUS — Curriculum: Stack Completa m_dermato")
    print("=" * 65)
    for status, count in sorted(counts.items()):
        if count == 0:
            continue
        bar = "█" * int(count / total_items * 40)
        print(f"  {status:20s}: {count:3d}/{total_items} {bar}")

    # Verificar notebooks sem ID
    nmap = data.get("notebook_map", {})
    missing = [k for k, v in nmap.items() if not v]
    if missing:
        print()
        print(f"  ⚠  Notebooks sem ID: {', '.join(missing)}")
        print(f"     Módulos dessas techs serão pulados até configurar")

    failed = counts.get("failed", 0) + counts.get("server_failed", 0)
    if failed > 0:
        print(f"\n  ⚠  {failed} itens falharam. Use --retry-failed para reprocessar")

    # Detalhes por nível
    levels = {"basico": "BÁSICO", "intermediario": "INTERMEDIÁRIO", "avancado": "AVANÇADO"}
    for level_key, level_label in levels.items():
        mods = [m for m in data["modules"] if m["level"] == level_key]
        if not mods:
            continue
        print(f"\n  ── {level_label} ──")
        for mod in mods:
            sa = mod.get("status_a", "pending")
            sb = mod.get("status_b", "pending")
            icon_a = {"pending": "⬜", "created": "🟡", "downloaded": "✅",
                      "failed": "❌", "server_failed": "❌", "download_failed": "🔴",
                      "generating": "⏳"}.get(sa, "?")
            icon_b = {"pending": "⬜", "created": "🟡", "downloaded": "✅",
                      "failed": "❌", "server_failed": "❌", "download_failed": "🔴",
                      "generating": "⏳"}.get(sb, "?")
            fmt = mod.get("audio_format", "?")
            print(f"  {mod['module']} {icon_a}{icon_b}  {mod['title'][:45]:45s} [{fmt}]")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Curriculum Audio Generator")
    parser.add_argument("--max", type=int, default=10,
                        help="Máximo de itens a processar (default: 10)")
    parser.add_argument("--modules", type=str,
                        help="Módulos específicos (ex: 1,2,3 ou 1a,3b)")
    parser.add_argument("--download", action="store_true",
                        help="Modo download: baixar áudios prontos")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostrar o que seria feito sem executar")
    parser.add_argument("--retry-failed", action="store_true",
                        help="Reprocessar itens com status failed/server_failed")
    parser.add_argument("--status", action="store_true",
                        help="Mostrar status geral")
    args = parser.parse_args()

    data = load_index()

    # === Status ===
    if args.status:
        show_status()
        return 0

    # === Download ===
    if args.download:
        if not check_auth():
            return 1
        download_audios()
        return 0

    # === Retry failed ===
    if args.retry_failed:
        reset_count = 0
        for mod in data["modules"]:
            for v in ["a", "b"]:
                s = mod.get(f"status_{v}", "pending")
                if s in ("failed", "server_failed", "download_failed"):
                    mod[f"status_{v}"] = "pending"
                    mod.pop(f"error_{v}", None)
                    mod.pop(f"artifact_id_{v}", None)
                    reset_count += 1
        if reset_count:
            save_index(data)
            log(f"Reset: {reset_count} itens → pending")
        else:
            log("Nenhum item com status failed encontrado")
            return 0

    # === Verificar auth ===
    if not check_auth():
        return 1

    # === Construir targets ===
    targets = build_targets(data, args)
    if not targets:
        log("Nenhum item pendente para processar")
        show_status()
        return 0

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    log(f"Itens selecionados: {len(targets)}")
    for mod, v in targets:
        prompt_text = load_prompt(mod[f"prompt_{v}"])
        chars = len(prompt_text) if prompt_text else 0
        nb = resolve_notebook_id(data, mod["tech"])
        log(f"  {mod['module']}{v} | {mod['title'][:40]} | {chars} chars | nb:{nb[:8] if nb else 'N/A'}...")

    if args.dry_run:
        log("DRY RUN — nada será executado")
        return 0

    # === Processar ===
    print()
    results = []
    for i, (mod, v) in enumerate(targets, 1):
        nb_id = resolve_notebook_id(data, mod["tech"])
        slug = f"{mod['module']}{v}"
        log(f"\n[{i}/{len(targets)}] Processando {slug}...")

        mod[f"status_{v}"] = "generating"
        save_index(data)

        result = create_audio(mod, v, nb_id, data)
        results.append({"module": slug, "title": mod["title"], **result})

        if result["success"]:
            mod[f"status_{v}"] = "created"
            mod[f"artifact_id_{v}"] = result.get("artifact_id")
            mod[f"notebook_id_{v}"] = nb_id
            mod[f"created_at_{v}"] = datetime.now().isoformat()
            mod[f"format_used_{v}"] = result.get("format")
            log(f"✓ OK: {slug}")
        else:
            mod[f"status_{v}"] = "failed"
            mod[f"error_{v}"] = result.get("error", "unknown")
            log(f"✗ FALHA: {slug}", "ERROR")

        save_index(data)

        # Intervalo entre gerações
        if i < len(targets):
            log(f"Aguardando {INTERVAL_SECONDS}s...")
            try:
                time.sleep(INTERVAL_SECONDS)
            except KeyboardInterrupt:
                log("\nCtrl+C — parando com segurança")
                break

    # === Resumo ===
    print()
    print("=" * 65)
    print("  RESUMO DA GERAÇÃO")
    print("=" * 65)
    ok = sum(1 for r in results if r.get("success"))
    fail = sum(1 for r in results if not r.get("success"))
    print(f"  Sucesso: {ok}/{len(results)}")
    print(f"  Falha:   {fail}/{len(results)}")
    print()
    for r in results:
        icon = "✓" if r.get("success") else "✗"
        fmt = r.get("format", "?")
        print(f"  [{icon}] {r['module']:6s} {r['title'][:45]} ({fmt})")
    print()
    print(f"  Próximo passo: python3 curriculum_runner.py --download")
    print(f"  (aguardar ~15 min após última criação)")
    print()

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
