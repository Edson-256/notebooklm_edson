#!/usr/bin/env python3
"""
Audio Generator - Conteúdo Técnico/Científico/Médico
Gera áudios educacionais deep-dive via NotebookLM para material técnico
"""

import subprocess
import json
import time
import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import unicodedata

# Configurações
PROJECT_DIR = Path(__file__).parent.parent
AUDIOS_DIR = PROJECT_DIR / "audios"
LOGS_DIR = PROJECT_DIR / "logs"
PROFILE = "default"
MAX_FOCUS_SIZE = 500
INTERVAL_SECONDS = 600  # 10 minutos entre áudios

# Template de prompt para conteúdo técnico/científico/médico
PROMPT_TEMPLATE = """Act as a Senior Science & Medical Educator. Create an instructional audio deep-dive in fluent Brazilian Portuguese (PT-BR).

Structure the audio to cover:
1. Contextualização: Situar o tópico dentro do campo de conhecimento, explicando sua relevância prática e teórica.
2. Mecanismos e Fundamentos: Explicar os mecanismos subjacentes, processos fisiológicos, princípios técnicos ou bases científicas.
3. Evidência e Aplicação: Apresentar a evidência científica relevante e como se aplica na prática clínica/técnica.
4. Conexões Interdisciplinares: Relacionar com outras áreas do conhecimento quando pertinente.
5. Síntese e Implicações: Resumir os pontos-chave e suas implicações para a prática profissional.

Approach:
- Use linguagem acessível mas precisa, sem simplificar conceitos importantes.
- Inclua exemplos concretos e casos ilustrativos quando possível.
- Mantenha rigor científico enquanto torna o conteúdo envolvente para o ouvinte.

Input Data:
Topic: {topic}
Notebook: {notebook_name}
{extra_context}"""


def log(message: str, level: str = "INFO"):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def slugify(text: str) -> str:
    """Converte texto para slug em lowercase snake_case"""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')


class AudioGenerator:
    """Gera áudios via nlm CLI"""

    def __init__(self, notebook_id: str, profile: str = "default"):
        self.notebook_id = notebook_id
        self.profile = profile

    def generate_audio(self, focus_topic: str) -> Optional[str]:
        """Gera áudio via nlm CLI"""
        try:
            # Truncar focus topic se necessário
            if len(focus_topic) > MAX_FOCUS_SIZE:
                focus_topic = focus_topic[:MAX_FOCUS_SIZE]

            cmd = [
                "nlm", "create", "audio",
                self.notebook_id,
                "--format", "deep_dive",
                "--language", "pt-BR",
                "--length", "default",
                "--focus", focus_topic,
                "--profile", self.profile,
                "--confirm"
            ]

            log(f"Gerando audio...")
            log(f"   Focus topic: {focus_topic}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                output = result.stdout
                artifact_match = re.search(r'Artifact ID:\s+([a-f0-9-]+)', output)

                if artifact_match:
                    artifact_id = artifact_match.group(1)
                    log(f"Audio iniciado: {artifact_id}")
                    return artifact_id
                else:
                    log(f"Audio criado mas artifact ID nao encontrado", "WARNING")
                    log(f"   Output: {output[:500]}", "DEBUG")
                    return None
            else:
                log(f"Erro ao gerar audio", "ERROR")
                log(f"   STDOUT: {result.stdout[:500]}", "ERROR")
                log(f"   STDERR: {result.stderr[:500]}", "ERROR")
                return None

        except Exception as e:
            log(f"Excecao ao gerar audio: {e}", "ERROR")
            return None

    def check_audio_status(self, artifact_id: str) -> Optional[str]:
        """Verifica status do áudio"""
        try:
            cmd = [
                "nlm", "studio", "status",
                self.notebook_id,
                "--json"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                artifacts = json.loads(result.stdout)
                for artifact in artifacts:
                    if artifact.get('id') == artifact_id:
                        return artifact.get('status')
            return None

        except Exception as e:
            log(f"Erro ao verificar status: {e}", "WARNING")
            return None

    def wait_for_audio_completion(self, artifact_id: str, max_wait_minutes: int = 30) -> bool:
        """Aguarda conclusão do áudio com polling"""
        log(f"Aguardando processamento do audio (max {max_wait_minutes} min)...")

        max_iterations = max_wait_minutes * 2  # Check every 30s

        for i in range(max_iterations):
            status = self.check_audio_status(artifact_id)

            if status == "completed":
                log(f"Audio processado com sucesso!")
                return True
            elif status == "failed":
                log(f"Processamento do audio falhou", "ERROR")
                return False
            elif status == "in_progress":
                if (i + 1) % 4 == 0:
                    elapsed = (i + 1) * 30 // 60
                    log(f"   Ainda processando... ({elapsed} min)")
                time.sleep(30)
            else:
                log(f"Status desconhecido: {status}", "WARNING")
                time.sleep(30)

        log(f"Timeout apos {max_wait_minutes} minutos", "WARNING")
        return False

    def delete_artifact(self, artifact_id: str) -> bool:
        """Deleta artifact do NotebookLM após download"""
        try:
            cmd = [
                "nlm", "delete", "artifact",
                self.notebook_id,
                artifact_id,
                "--confirm"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                log(f"Artifact deletado: {artifact_id[:8]}...")
                return True
            else:
                log(f"Falha ao deletar artifact: {result.stderr}", "WARNING")
                return False

        except Exception as e:
            log(f"Excecao ao deletar artifact: {e}", "WARNING")
            return False

    def download_audio(self, artifact_id: str, output_path: Path, delete_after: bool = True) -> bool:
        """Baixa áudio gerado e opcionalmente deleta artifact"""
        try:
            log(f"Baixando audio para: {output_path}")

            cmd = [
                "nlm", "download", "audio",
                self.notebook_id,
                "--id", artifact_id,
                "--output", str(output_path),
                "--no-progress"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                log(f"Download concluido: {size_mb:.1f} MB")

                if delete_after:
                    self.delete_artifact(artifact_id)

                return True
            else:
                log(f"Falha no download: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            log(f"Excecao no download: {e}", "ERROR")
            return False


def generate_single_audio(notebook_id: str, topic: str, notebook_name: str = "",
                          extra_context: str = "", output_dir: Path = None,
                          profile: str = "default") -> Optional[Dict]:
    """Gera um único áudio para um tópico"""

    if output_dir is None:
        output_dir = AUDIOS_DIR / slugify(notebook_name or "default")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome do arquivo
    topic_slug = slugify(topic)[:50]
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"mk_{topic_slug}_{timestamp}.mp3"
    output_path = output_dir / filename

    # Build focus topic
    focus_topic = topic
    if extra_context:
        focus_topic = f"{topic} - {extra_context}"

    # Gerar áudio
    generator = AudioGenerator(notebook_id, profile)
    artifact_id = generator.generate_audio(focus_topic)

    if not artifact_id:
        log(f"Falha ao gerar audio para: {topic}", "ERROR")
        return None

    # Aguardar e baixar
    audio_ready = generator.wait_for_audio_completion(artifact_id, max_wait_minutes=30)

    download_success = False
    if audio_ready:
        download_success = generator.download_audio(artifact_id, output_path)

    result = {
        'arquivo': filename,
        'topic': topic,
        'notebook_id': notebook_id,
        'notebook_name': notebook_name,
        'artifact_id': artifact_id,
        'data_geracao': datetime.now().isoformat(),
        'focus_topic': focus_topic,
        'status': 'downloaded' if download_success else 'pending_download',
        'output_path': str(output_path)
    }

    if download_success and output_path.exists():
        result['tamanho_bytes'] = output_path.stat().st_size

    # Salvar metadata
    save_metadata(output_dir, notebook_id, notebook_name, [result])

    return result


def generate_batch(notebook_id: str, topics: List[str], notebook_name: str = "",
                   profile: str = "default") -> List[Dict]:
    """Gera áudios em batch para uma lista de tópicos"""
    output_dir = AUDIOS_DIR / slugify(notebook_name or "default")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i, topic in enumerate(topics, 1):
        log(f"\n[{i}/{len(topics)}] Processando: {topic}")

        result = generate_single_audio(
            notebook_id=notebook_id,
            topic=topic,
            notebook_name=notebook_name,
            output_dir=output_dir,
            profile=profile
        )

        if result:
            results.append(result)

        # Intervalo entre áudios
        if i < len(topics):
            log(f"Aguardando {INTERVAL_SECONDS // 60} minutos antes do proximo...")
            time.sleep(INTERVAL_SECONDS)

    return results


def save_metadata(output_dir: Path, notebook_id: str, notebook_name: str, audios: List[Dict]):
    """Salva metadata.json, preservando áudios anteriores"""
    metadata_path = output_dir / "metadata.json"

    existing_audios = []
    if metadata_path.exists():
        try:
            existing = json.load(open(metadata_path, encoding='utf-8'))
            existing_audios = existing.get('audios', [])
        except Exception:
            existing_audios = []

    # Mesclar por topic
    existing_by_topic = {a['topic']: a for a in existing_audios}
    for audio in audios:
        existing_by_topic[audio['topic']] = audio
    merged = sorted(existing_by_topic.values(), key=lambda a: a['data_geracao'])

    metadata = {
        'notebook_id': notebook_id,
        'notebook_name': notebook_name,
        'total_audios': len(merged),
        'ultima_atualizacao': datetime.now().isoformat(),
        'audios': merged
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    log(f"Metadata salvo: {metadata_path} ({len(merged)} audios total)")


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Audio Generator - Conteúdo Técnico/Científico')
    parser.add_argument('--notebook', type=str, required=True, help='ID do notebook NotebookLM')
    parser.add_argument('--notebook-name', type=str, default='', help='Nome do notebook (para organização)')
    parser.add_argument('--topic', type=str, help='Tópico para gerar áudio (modo single)')
    parser.add_argument('--topics-file', type=str, help='Arquivo JSON com lista de tópicos (modo batch)')
    parser.add_argument('--context', type=str, default='', help='Contexto adicional para o prompt')
    parser.add_argument('--profile', type=str, default='default', help='Perfil nlm para autenticação')
    parser.add_argument('--test', action='store_true', help='Modo de teste (não gera áudio)')

    args = parser.parse_args()

    print("=" * 60)
    print("  Audio Generator - Conteudo Tecnico/Cientifico")
    print("=" * 60)
    print()

    # Verificar autenticação
    log("Verificando autenticacao...")
    result = subprocess.run(
        ["nlm", "login", "--check", "--profile", args.profile],
        capture_output=True
    )

    if result.returncode != 0:
        log("ERRO: Nao autenticado!", "ERROR")
        log(f"Execute: nlm login --profile {args.profile}", "INFO")
        return 1

    log("Autenticado com sucesso!")

    if args.test:
        log("MODO TESTE - nenhum audio sera gerado")
        log(f"Notebook: {args.notebook}")
        log(f"Topic: {args.topic or '(batch mode)'}")
        return 0

    # Modo single ou batch
    if args.topic:
        result = generate_single_audio(
            notebook_id=args.notebook,
            topic=args.topic,
            notebook_name=args.notebook_name,
            extra_context=args.context,
            profile=args.profile
        )

        if result:
            log(f"Audio gerado: {result['arquivo']} ({result['status']})")
        else:
            log("Falha ao gerar audio", "ERROR")
            return 1

    elif args.topics_file:
        topics_path = Path(args.topics_file)
        if not topics_path.exists():
            log(f"Arquivo de topicos nao encontrado: {args.topics_file}", "ERROR")
            return 1

        with open(topics_path, 'r', encoding='utf-8') as f:
            topics = json.load(f)

        if not isinstance(topics, list):
            log("Arquivo de topicos deve ser uma lista JSON", "ERROR")
            return 1

        results = generate_batch(
            notebook_id=args.notebook,
            topics=topics,
            notebook_name=args.notebook_name,
            profile=args.profile
        )

        print()
        print("=" * 60)
        print("  RESUMO DA EXECUCAO")
        print("=" * 60)
        print(f"Total de audios gerados: {len(results)}")
        print(f"Sucesso: {sum(1 for r in results if r['status'] == 'downloaded')}")
        print(f"Pendente: {sum(1 for r in results if r['status'] == 'pending_download')}")
        print()

    else:
        log("Especifique --topic ou --topics-file", "ERROR")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
