#!/usr/bin/env python3
"""
Batch Audio Overview Generator
Gera audio overviews para múltiplos notebooks de uma vez
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import sys

# Configuração dos notebooks para processar
NOTEBOOKS = [
    {
        "id": "85d38ec1-7659-4307-aedf-3bc773a4d4ba",
        "name": "Docker",
        "format": "deep_dive",
        "language": "pt-BR",
        "length": "default"
    },
    {
        "id": "3d1e250c-47e7-42f6-9df7-86c2b6623f4a",
        "name": "Claude Code",
        "format": "deep_dive",
        "language": "pt-BR",
        "length": "default"
    },
    {
        "id": "cb7a2fcd-e7fd-49d0-bdae-f2b315600051",
        "name": "Beads BD Software",
        "format": "brief",
        "language": "pt-BR",
        "length": "short"
    }
]

PROFILE = "default"
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log(message, level="INFO"):
    """Log message com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_auth():
    """Verifica se está autenticado"""
    try:
        result = subprocess.run(
            ["nlm", "login", "--check", "--profile", PROFILE],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        log(f"Erro ao verificar autenticação: {e}", "ERROR")
        return False

def generate_audio(notebook):
    """Gera audio overview para um notebook"""
    log(f"🎙️  Gerando audio para: {notebook['name']}")
    log(f"   ID: {notebook['id']}")
    log(f"   Formato: {notebook['format']}, Idioma: {notebook['language']}, Duração: {notebook['length']}")

    try:
        cmd = [
            "nlm", "audio", "create",
            notebook["id"],
            "--format", notebook["format"],
            "--language", notebook["language"],
            "--length", notebook["length"],
            "--profile", PROFILE,
            "--confirm"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos de timeout
        )

        if result.returncode == 0:
            log(f"✅ Audio criado com sucesso: {notebook['name']}", "SUCCESS")
            return True
        else:
            log(f"❌ Erro ao criar audio: {notebook['name']}", "ERROR")
            log(f"   Output: {result.stderr}", "ERROR")
            return False

    except subprocess.TimeoutExpired:
        log(f"⏱️  Timeout ao gerar audio: {notebook['name']}", "ERROR")
        return False
    except Exception as e:
        log(f"❌ Exceção ao gerar audio: {e}", "ERROR")
        return False

def save_report(results):
    """Salva relatório de execução"""
    report_file = LOG_DIR / f"audio_generation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "profile": PROFILE,
        "total": len(results),
        "success": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    log(f"📄 Relatório salvo em: {report_file}")
    return report

def main():
    print("=" * 60)
    print("🎙️  NotebookLM Batch Audio Overview Generator")
    print("=" * 60)
    print()

    # Verificar autenticação
    log("🔐 Verificando autenticação...")
    if not check_auth():
        log("❌ ERRO: Você precisa fazer login primeiro!", "ERROR")
        log(f"Execute: nlm login --profile {PROFILE}", "INFO")
        sys.exit(1)

    log("✅ Autenticado com sucesso!")
    print()

    # Processar notebooks
    log(f"📚 Processando {len(NOTEBOOKS)} notebooks...")
    print()

    results = []
    for i, notebook in enumerate(NOTEBOOKS, 1):
        log(f"[{i}/{len(NOTEBOOKS)}] Processando: {notebook['name']}")

        success = generate_audio(notebook)

        results.append({
            "notebook_id": notebook["id"],
            "notebook_name": notebook["name"],
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

        # Aguardar um pouco entre requisições
        if i < len(NOTEBOOKS):
            log("⏳ Aguardando 30 segundos antes do próximo...")
            time.sleep(30)

        print()

    # Gerar relatório
    print("=" * 60)
    log("📊 Gerando relatório...")
    report = save_report(results)

    print()
    print("=" * 60)
    print("📈 RESUMO")
    print("=" * 60)
    print(f"Total: {report['total']}")
    print(f"✅ Sucesso: {report['success']}")
    print(f"❌ Falhas: {report['failed']}")
    print("=" * 60)
    print()

    if report['failed'] > 0:
        log("⚠️  Alguns notebooks falharam. Verifique o relatório para detalhes.", "WARNING")
        sys.exit(1)
    else:
        log("🎉 Todos os audio overviews foram gerados com sucesso!", "SUCCESS")

if __name__ == "__main__":
    main()
