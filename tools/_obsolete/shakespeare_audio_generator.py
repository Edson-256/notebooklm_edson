#!/usr/bin/env python3
"""
Shakespeare Audio Generator
Gera áudios educacionais de cenas do Shakespeare aplicando metodologia Olavo de Carvalho
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
SHAKESPEARE_DIR = PROJECT_DIR / "projetos" / "w_shakespeare"
NOTEBOOK_ID = "62400b1d-e3bd-45d2-8428-d2d8d6b7128d"  # William Shakespeare notebook
PROFILE = "default"
MAX_PROMPT_SIZE = 2500
INTERVAL_SECONDS = 600  # 10 minutos

# Template de prompt
PROMPT_TEMPLATE = """Act as a Senior Humanities Tutor. Create an instructional audio deep-dive in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology (found in sources) to this specific scene.
Focus on "Education of the Imaginary" and breaking the "Individual Capsule" via vicarious experience.

Structure the audio to cover:
1. Context & Preliminary Attitude (suspending external judgments).
2. The 4 Pillars: Primacy of Intuition, Existential Sincerity, Affective Memory, Literature as a Means.
3. Vicarious Experience: Instruct the listener on how to inhabit the main character's skin.

Input Data:
Scene Number: {scene_number}
Book: {book_title}
Author: William Shakespeare

Context:
{scene_context}"""


def log(message: str, level: str = "INFO"):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def slugify(text: str) -> str:
    """Converte texto para slug em lowercase snake_case"""
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')

    # Remover pontuação e converter para lowercase
    text = re.sub(r'[^\w\s-]', '', text.lower())

    # Substituir espaços por underscore
    text = re.sub(r'[-\s]+', '_', text)

    return text.strip('_')


def extract_keyword_from_title(title: str) -> str:
    """Extrai palavra-chave do título da cena"""
    # Remover artigos e preposições comuns
    stopwords = ['o', 'a', 'os', 'as', 'do', 'da', 'dos', 'das', 'de', 'e',
                 'para', 'entre', 'com', 'no', 'na', 'nos', 'nas', 'ao', 'à']

    # Limpar e separar palavras
    words = re.findall(r'\w+', title.lower())

    # Filtrar stopwords
    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    # Pegar até 2 palavras principais
    keyword = '_'.join(keywords[:2])

    # Limitar tamanho
    return keyword[:30]


def get_obra_slug(obra_dir: str) -> str:
    """Converte nome do diretório em slug da obra"""
    # Mapeamento manual para casos especiais
    mapping = {
        'a_midsummer_nights_dream': 'midsummer_dream',
        'alls_well_that_ends_well': 'alls_well',
        'antony_and_cleopatra': 'antony_cleopatra',
        'as_you_like_it': 'as_you_like_it',
        'the_comedy_of_errors': 'comedy_errors',
        'the_merchant_of_venice': 'merchant_venice',
        'the_merry_wives_of_windsor': 'merry_wives',
        'the_taming_of_the_shrew': 'taming_shrew',
        'the_two_gentlemen_of_verona': 'two_gentlemen',
        'the_two_noble_kinsmen': 'two_kinsmen',
        'the_winters_tale': 'winters_tale',
        'history_of_henry_iv_part_i': 'henry4_p1',
        'history_of_henry_iv_part_ii': 'henry4_p2',
        'history_of_henry_v': 'henry5',
        'history_of_henry_vi_part_i': 'henry6_p1',
        'history_of_henry_vi_part_ii': 'henry6_p2',
        'history_of_henry_vi_part_iii': 'henry6_p3',
        'history_of_henry_viii': 'henry8',
        'history_of_king_john': 'king_john',
        'history_of_richard_ii': 'richard2',
        'history_of_richard_iii': 'richard3',
        'romeo_and_juliet': 'romeo_juliet',
        'julius_caesar': 'julius_caesar',
        'much_ado_about_nothing': 'much_ado',
        'loves_labours_lost': 'loves_labour',
        'measure_for_measure': 'measure_measure',
        'the_rape_of_lucrece': 'lucrece',
        'the_tempest': 'tempest',
        'timon_of_athens': 'timon_athens',
        'titus_andronicus': 'titus_andronicus',
        'troilus_and_cressida': 'troilus_cressida',
        'twelfth_night': 'twelfth_night',
        'venus_and_adonis': 'venus_adonis',
    }

    return mapping.get(obra_dir, obra_dir)


class SceneExtractor:
    """Extrai cenas dos arquivos markdown"""

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text(encoding='utf-8')

    def extract_scenes(self) -> List[Dict]:
        """Extrai todas as cenas do arquivo"""
        scenes = []

        # Regex para encontrar cenas (versão corrigida)
        # Procura por: ### N. Título\n- **Localização:**\n- **Resumo:**\n- **Justificativa
        pattern = r'### (\d+)\.\s+(.+?)\n\s*-\s+\*\*Localização:\*\*\s+(.+?)\n\s*-\s+\*\*Resumo:\*\*\s+(.+?)\n\s*-\s+\*\*Justificativa.*?:\*\*\s+(.+?)(?=\n###|\Z)'

        matches = re.finditer(pattern, self.content, re.DOTALL)

        for match in matches:
            scene = {
                'number': int(match.group(1)),
                'title': match.group(2).strip(),
                'location': match.group(3).strip(),
                'summary': match.group(4).strip(),
                'justification': match.group(5).strip()
            }
            scenes.append(scene)

        return scenes


class AudioGenerator:
    """Gera áudios via nlm CLI"""

    def __init__(self, notebook_id: str, profile: str = "default"):
        self.notebook_id = notebook_id
        self.profile = profile

    def build_prompt(self, scene: Dict, book_title: str) -> str:
        """Constrói prompt respeitando limite de caracteres"""
        # Construir contexto da cena
        context = f"""Localização: {scene['location']}
Título: {scene['title']}

Resumo: {scene['summary']}

Justificativa COF: {scene['justification']}"""

        # Gerar prompt completo
        prompt = PROMPT_TEMPLATE.format(
            scene_number=scene['number'],
            book_title=book_title,
            scene_context=context
        )

        # Verificar tamanho
        if len(prompt) > MAX_PROMPT_SIZE:
            # Truncar justificativa se necessário
            available = MAX_PROMPT_SIZE - (len(PROMPT_TEMPLATE) - len("{scene_context}"))
            available -= len(f"Scene Number: {scene['number']}\nBook: {book_title}\nAuthor: William Shakespeare\n\nContext:\n")

            context_base = f"""Localização: {scene['location']}
Título: {scene['title']}

Resumo: {scene['summary']}

Justificativa COF: """

            justification_limit = available - len(context_base) - 50
            truncated_justification = scene['justification'][:justification_limit] + "..."

            context = context_base + truncated_justification

            prompt = PROMPT_TEMPLATE.format(
                scene_number=scene['number'],
                book_title=book_title,
                scene_context=context
            )

        return prompt

    def generate_audio(self, focus_topic: str) -> Optional[str]:
        """Gera áudio via nlm CLI"""
        try:
            # Comando nlm - usando focus topic curto
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

            log(f"🎙️  Gerando áudio...")
            log(f"   Focus topic: {focus_topic}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                # Extrair artifact ID do output
                output = result.stdout
                artifact_match = re.search(r'Artifact ID:\s+([a-f0-9-]+)', output)

                if artifact_match:
                    artifact_id = artifact_match.group(1)
                    log(f"✅ Áudio iniciado: {artifact_id}")
                    return artifact_id
                else:
                    log(f"⚠️  Áudio criado mas artifact ID não encontrado", "WARNING")
                    log(f"   Output: {output[:500]}", "DEBUG")
                    return None
            else:
                log(f"❌ Erro ao gerar áudio", "ERROR")
                log(f"   STDOUT: {result.stdout[:500]}", "ERROR")
                log(f"   STDERR: {result.stderr[:500]}", "ERROR")
                return None

        except Exception as e:
            log(f"❌ Exceção ao gerar áudio: {e}", "ERROR")
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
            log(f"⚠️  Erro ao verificar status: {e}", "WARNING")
            return None

    def wait_for_audio_completion(self, artifact_id: str, max_wait_minutes: int = 30) -> bool:
        """Aguarda conclusão do áudio com polling"""
        log(f"⏳ Aguardando processamento do áudio (max {max_wait_minutes} min)...")

        max_iterations = max_wait_minutes * 2  # Check every 30s

        for i in range(max_iterations):
            status = self.check_audio_status(artifact_id)

            if status == "completed":
                log(f"✅ Áudio processado com sucesso!")
                return True
            elif status == "failed":
                log(f"❌ Processamento do áudio falhou", "ERROR")
                return False
            elif status == "in_progress":
                if (i + 1) % 4 == 0:  # Log a cada 2 minutos
                    elapsed = (i + 1) * 30 // 60
                    log(f"   Ainda processando... ({elapsed} min)")
                time.sleep(30)
            else:
                log(f"⚠️  Status desconhecido: {status}", "WARNING")
                time.sleep(30)

        log(f"⏰ Timeout após {max_wait_minutes} minutos", "WARNING")
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
                log(f"🗑️  Artifact deletado: {artifact_id[:8]}...")
                return True
            else:
                log(f"⚠️  Falha ao deletar artifact: {result.stderr}", "WARNING")
                return False

        except Exception as e:
            log(f"⚠️  Exceção ao deletar artifact: {e}", "WARNING")
            return False

    def download_audio(self, artifact_id: str, output_path: Path, delete_after: bool = True) -> bool:
        """Baixa áudio gerado e opcionalmente deleta artifact"""
        try:
            log(f"📥 Baixando áudio para: {output_path}")

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
                log(f"✅ Download concluído: {size_mb:.1f} MB")

                # Deletar artifact após download bem-sucedido
                if delete_after:
                    self.delete_artifact(artifact_id)

                return True
            else:
                log(f"❌ Falha no download: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            log(f"❌ Exceção no download: {e}", "ERROR")
            return False


def process_obra(obra_dir: Path, max_scenes: Optional[int] = None, start_from: int = 1) -> List[Dict]:
    """Processa uma obra e gera áudios"""
    log(f"\n{'='*60}")
    log(f"📚 Processando obra: {obra_dir.name}")
    log(f"{'='*60}")

    # Verificar arquivo de cenas
    scenes_file = obra_dir / "01_cenas_identificadas.md"
    if not scenes_file.exists():
        log(f"⚠️  Arquivo de cenas não encontrado: {scenes_file}", "WARNING")
        return []

    # Criar diretórios
    audios_dir = obra_dir / "audios"
    audios_dir.mkdir(exist_ok=True)

    logs_dir = obra_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Extrair cenas
    extractor = SceneExtractor(scenes_file)
    all_scenes = extractor.extract_scenes()

    # Filtrar a partir da cena start_from
    scenes = [s for s in all_scenes if s['number'] >= start_from]

    if max_scenes:
        scenes = scenes[:max_scenes]

    if start_from > 1:
        log(f"📋 Total de cenas: {len(all_scenes)} | Iniciando da cena {start_from} | Processando: {len(scenes)}")
    else:
        log(f"📋 Encontradas {len(scenes)} cenas para processar")

    # Processar cada cena
    generator = AudioGenerator(NOTEBOOK_ID, PROFILE)
    results = []

    obra_slug = get_obra_slug(obra_dir.name)
    book_title = obra_dir.name.replace('_', ' ').title()

    for i, scene in enumerate(scenes, 1):
        log(f"\n[{i}/{len(scenes)}] Processando cena {scene['number']}: {scene['title']}")

        # Gerar slug da palavra-chave
        keyword = extract_keyword_from_title(scene['title'])

        # Nome do arquivo
        filename = f"ws_{obra_slug}_{scene['number']:02d}_{keyword}.mp3"
        output_path = audios_dir / filename

        # Construir focus topic (título da cena + localização)
        focus_topic = f"{book_title} - {scene['location']}: {scene['title']}"

        # Gerar áudio
        artifact_id = generator.generate_audio(focus_topic)

        if artifact_id:
            # Aguardar conclusão do processamento
            audio_ready = generator.wait_for_audio_completion(artifact_id, max_wait_minutes=30)

            # Tentar download se estiver pronto
            download_success = False
            if audio_ready:
                download_success = generator.download_audio(artifact_id, output_path)

            result = {
                'arquivo': filename,
                'cena_numero': scene['number'],
                'titulo_completo': scene['title'],
                'localizacao': scene['location'],
                'artifact_id': artifact_id,
                'data_geracao': datetime.now().isoformat(),
                'focus_topic': focus_topic,
                'status': 'downloaded' if download_success else 'pending_download',
                'output_path': str(output_path)
            }

            if download_success and output_path.exists():
                result['tamanho_bytes'] = output_path.stat().st_size

            results.append(result)

            # Salvar metadata incremental
            save_metadata(obra_dir, obra_slug, book_title, results)

            # Aguardar intervalo antes da próxima cena
            if i < len(scenes):
                log(f"⏱️  Aguardando {INTERVAL_SECONDS//60} minutos antes da próxima cena...")
                time.sleep(INTERVAL_SECONDS)
        else:
            log(f"❌ Falha ao gerar áudio da cena {scene['number']}", "ERROR")

    return results


def save_metadata(obra_dir: Path, obra_slug: str, book_title: str, audios: List[Dict]):
    """Salva metadata.json, preservando áudios anteriores (append)"""
    metadata_path = obra_dir / "audios" / "metadata.json"

    # Carregar audios existentes para fazer append
    existing_audios = []
    if metadata_path.exists():
        try:
            existing = json.load(open(metadata_path, encoding='utf-8'))
            existing_audios = existing.get('audios', [])
        except Exception:
            existing_audios = []

    # Mesclar: manter existentes e adicionar/atualizar novos por cena_numero
    existing_by_num = {a['cena_numero']: a for a in existing_audios}
    for audio in audios:
        existing_by_num[audio['cena_numero']] = audio
    merged = sorted(existing_by_num.values(), key=lambda a: a['cena_numero'])

    metadata = {
        'obra': book_title,
        'obra_slug': obra_slug,
        'obra_dir': obra_dir.name,
        'notebook_id': NOTEBOOK_ID,
        'total_cenas': len(merged),
        'ultima_atualizacao': datetime.now().isoformat(),
        'audios': merged
    }

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    log(f"💾 Metadata salvo: {metadata_path} ({len(merged)} áudios total)")


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Shakespeare Audio Generator')
    parser.add_argument('--obra', type=str, help='Nome do diretório da obra')
    parser.add_argument('--scenes', type=int, help='Número máximo de cenas a processar')
    parser.add_argument('--start-from', type=int, default=1, dest='start_from',
                        help='Número da cena a partir da qual começar (default: 1)')
    parser.add_argument('--test', action='store_true', help='Modo de teste (3 cenas)')

    args = parser.parse_args()

    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🎭 Shakespeare Audio Generator - Metodologia Olavo       ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Verificar autenticação
    log("🔐 Verificando autenticação...")
    result = subprocess.run(
        ["nlm", "login", "--check", "--profile", PROFILE],
        capture_output=True
    )

    if result.returncode != 0:
        log("❌ ERRO: Não autenticado!", "ERROR")
        log(f"Execute: nlm login --profile {PROFILE}", "INFO")
        return 1

    log("✅ Autenticado com sucesso!")

    # Modo teste
    max_scenes = 3 if args.test else args.scenes

    # Processar obra específica ou primeira em ordem alfabética
    if args.obra:
        obra_dir = SHAKESPEARE_DIR / args.obra
        if not obra_dir.exists():
            log(f"❌ Obra não encontrada: {args.obra}", "ERROR")
            return 1

        results = process_obra(obra_dir, max_scenes, start_from=args.start_from)
    else:
        # Processar primeira obra (ordem alfabética) para teste
        obras = sorted([d for d in SHAKESPEARE_DIR.iterdir()
                       if d.is_dir() and (d / "01_cenas_identificadas.md").exists()])

        if not obras:
            log("❌ Nenhuma obra encontrada!", "ERROR")
            return 1

        log(f"📚 Processando primeira obra em ordem alfabética: {obras[0].name}")
        results = process_obra(obras[0], max_scenes, start_from=args.start_from)

    # Resumo
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                    RESUMO DA EXECUÇÃO                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"Total de áudios gerados: {len(results)}")
    print(f"Sucesso: {sum(1 for r in results if r['status'] == 'downloaded')}")
    print(f"Pendente: {sum(1 for r in results if r['status'] == 'pending_download')}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
