#!/usr/bin/env python3
"""
Gera os 81 prompts customizados para Ben-Hur baseado no template COF do Shakespeare.
Lê 01_cenas_identificadas.md e cria arquivos em prompts_cenas/
"""

import re
import unicodedata
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
SCENES_FILE = PROJECT_DIR / "projetos" / "ben-hur" / "01_cenas_identificadas.md"
OUTPUT_DIR = PROJECT_DIR / "projetos" / "ben-hur" / "prompts_cenas"

PROMPT_TEMPLATE = """Act as a Senior Humanities Tutor. Create an instructional audio deep-dive in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology to this specific scene.
Focus on "Education of the Imaginary" and breaking the "Individual Capsule" via vicarious experience.

Structure the audio to cover:
1. Context & Preliminary Attitude (suspending external judgments).
2. The 4 Pillars: Primacy of Intuition, Existential Sincerity, Affective Memory, Literature as a Means.
3. Vicarious Experience: Instruct the listener on how to inhabit the main character's skin.

Input Data:
Scene Number: {scene_number}
Book: Ben-Hur: A Tale of the Christ
Author: Lew Wallace
Topic: {title}

Context:
{localizacao}
{resumo}

Justification (COF Integration):
{justificativa}

Analysis Instructions:
Explique como aplicar a técnica de leitura do COF nesta cena. Comente como desenvolver a primazia da intuição, mergulhando na dinâmica da cena; como avaliar a ruptura ou busca da sinceridade existencial; a ligação com a memória afetiva e imaginativa e, por fim, a literatura como expansão da consciência (meios e não fim). Oriente o ouvinte a praticar a "experiência vicariante", vestindo a pele dos personagens para iluminar a psicologia humana, sem atalhos moralistas.
""".strip()


def slugify(text: str) -> str:
    """Converte título em slug para nome de arquivo."""
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = nfkd.encode('ASCII', 'ignore').decode('ASCII')
    # Lowercase e substitui espaços/pontuação por underscore
    slug = re.sub(r'[^a-z0-9]+', '_', ascii_text.lower())
    # Remove underscores no início/fim
    slug = slug.strip('_')
    # Limita tamanho
    return slug[:60]


def parse_scenes(content: str) -> list[dict]:
    """Extrai as 81 cenas do arquivo markdown."""
    scenes = []

    # Pattern para cada cena: ### N. Título
    scene_pattern = re.compile(
        r'### (\d+)\. (.+?)\n'
        r'- \*\*Localização:\*\* (.+?)\n'
        r'- \*\*Resumo:\*\* (.+?)\n'
        r'- \*\*Justificativa COF:\*\* (.+?)(?=\n\n|\n---|\n### |\Z)',
        re.DOTALL
    )

    for match in scene_pattern.finditer(content):
        scenes.append({
            'number': int(match.group(1)),
            'title': match.group(2).strip(),
            'localizacao': match.group(3).strip(),
            'resumo': match.group(4).strip(),
            'justificativa': match.group(5).strip(),
        })

    return scenes


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    content = SCENES_FILE.read_text(encoding='utf-8')
    scenes = parse_scenes(content)

    print(f"Encontradas {len(scenes)} cenas")

    for scene in scenes:
        prompt = PROMPT_TEMPLATE.format(
            scene_number=scene['number'],
            title=scene['title'],
            localizacao=f"Localização: {scene['localizacao']}",
            resumo=scene['resumo'],
            justificativa=scene['justificativa'],
        )

        filename = f"{scene['number']:02d}_{slugify(scene['title'])}.md"
        filepath = OUTPUT_DIR / filename

        filepath.write_text(prompt + '\n', encoding='utf-8')
        print(f"  ✅ {filename}")

    print(f"\n✅ {len(scenes)} prompts gerados em {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
