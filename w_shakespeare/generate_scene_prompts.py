#!/usr/bin/env python3
"""
Generate individual prompt files for each scene from Shakespeare works.
Processes 01_cenas_identificadas.md files and creates prompts_cenas/ directory with individual prompts.
"""

import os
import re
from pathlib import Path

# Base directory
BASE_DIR = Path("/Users/edsonmichalkiewicz/dev/notebooklm_edson/w_shakespeare")
MAX_CHARS = 2500

# Template for prompts
PROMPT_TEMPLATE = """Act as a Senior Humanities Tutor. Create an instructional audio deep-dive in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology to this specific scene.
Focus on "Education of the Imaginary" and breaking the "Individual Capsule" via vicarious experience.

Structure the audio to cover:
1. Context & Preliminary Attitude (suspending external judgments).
2. The 4 Pillars: Primacy of Intuition, Existential Sincerity, Affective Memory, Literature as a Means.
3. Vicarious Experience: Instruct the listener on how to inhabit the main character's skin.

Input Data:
Scene Number: {number}
Book: {book_title}
Author: William Shakespeare
Topic: {scene_title}

Context:
Localização: {location}
{summary}

Justification (COF Integration):
{justification}

Analysis Instructions:
Explique como aplicar a técnica de leitura do COF nesta cena. Comente como desenvolver a primazia da intuição, mergulhando na dinâmica da cena; como avaliar a ruptura ou busca da sinceridade existencial; a ligação com a memória afetiva e imaginativa e, por fim, a literatura como expansão da consciência (meios e não fim). Oriente o ouvinte a praticar a "experiência vicariante", vestindo a pele dos personagens para iluminar a psicologia humana, sem atalhos moralistas.
"""

def slugify(text):
    """Convert text to lowercase with underscores."""
    # Remove special characters and replace spaces with underscores
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')

def extract_book_title(content):
    """Extract book title from markdown header."""
    match = re.search(r'\*\*Obra:\*\*\s*\*?([^*\n]+)', content)
    if match:
        return match.group(1).strip()
    # Fallback: look for first heading
    match = re.search(r'^#\s+(.+?)(?:\s*—|$)', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"

def parse_scenes(content):
    """Parse scenes from markdown content."""
    scenes = []

    # Split by scene headers (### N. Title)
    scene_pattern = r'###\s+(\d+)\.\s+(.+?)(?=\n###|\Z)'
    matches = re.finditer(scene_pattern, content, re.DOTALL)

    for match in matches:
        number = match.group(1)
        rest = match.group(2)

        # Extract title (first line)
        lines = rest.strip().split('\n')
        title = lines[0].strip()

        # Extract location
        location_match = re.search(r'-\s*\*\*Localização:\*\*\s*(.+?)(?=\n|$)', rest)
        location = location_match.group(1).strip() if location_match else ""

        # Extract summary (between Resumo: and Justificativa)
        summary_match = re.search(r'-\s*\*\*Resumo:\*\*\s*(.+?)(?=-\s*\*\*Justificativa)', rest, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ""

        # Extract justification (try multiple patterns)
        justification_match = re.search(r'-\s*\*\*Justificativa\s*(?:\([^)]*\)|COF):\*\*\s*(.+?)(?=\n###|\Z)', rest, re.DOTALL)
        justification = justification_match.group(1).strip() if justification_match else ""

        scenes.append({
            'number': number,
            'title': title,
            'location': location,
            'summary': summary,
            'justification': justification
        })

    return scenes

def truncate_to_limit(prompt_text, max_chars=MAX_CHARS):
    """Truncate prompt to fit within character limit."""
    if len(prompt_text) <= max_chars:
        return prompt_text, False

    # Try to truncate at a sentence boundary
    truncated = prompt_text[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.8:  # If we can keep at least 80%
        return truncated[:last_period + 1], True
    return truncated + "...", True

def create_prompt_file(work_dir, scene, book_title, scene_num):
    """Create individual prompt file for a scene."""
    # Generate filename
    filename_base = slugify(scene['title'])[:50]  # Limit length
    filename = f"{scene_num:02d}_{filename_base}.md"

    # Create prompt content
    prompt = PROMPT_TEMPLATE.format(
        number=scene['number'],
        book_title=book_title,
        scene_title=scene['title'],
        location=scene['location'],
        summary=scene['summary'],
        justification=scene['justification']
    )

    # Check and truncate if needed
    prompt, was_truncated = truncate_to_limit(prompt)

    # Create prompts_cenas directory if needed
    prompts_dir = work_dir / "prompts_cenas"
    prompts_dir.mkdir(exist_ok=True)

    # Write file
    output_path = prompts_dir / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

    return output_path, was_truncated

def process_work(work_dir):
    """Process a single Shakespeare work."""
    work_name = work_dir.name
    scenes_file = work_dir / "01_cenas_identificadas.md"

    if not scenes_file.exists():
        return None, f"Missing 01_cenas_identificadas.md"

    # Read content
    with open(scenes_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract book title
    book_title = extract_book_title(content)

    # Parse scenes
    scenes = parse_scenes(content)

    if not scenes:
        return None, "No scenes found"

    # Create prompt files
    created_files = []
    truncated_count = 0

    for i, scene in enumerate(scenes, 1):
        try:
            output_path, was_truncated = create_prompt_file(work_dir, scene, book_title, i)
            created_files.append(output_path)
            if was_truncated:
                truncated_count += 1
        except Exception as e:
            return None, f"Error creating prompt {i}: {str(e)}"

    return {
        'work': work_name,
        'book_title': book_title,
        'scenes_count': len(scenes),
        'files_created': len(created_files),
        'truncated': truncated_count
    }, None

def main():
    """Main processing function."""
    import sys

    # Parse command line arguments
    start_idx = 25
    end_idx = 35

    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == '--start' and i+1 < len(sys.argv):
                start_idx = int(sys.argv[i+1])
            elif arg == '--end' and i+1 < len(sys.argv):
                end_idx = int(sys.argv[i+1])

    # Get works alphabetically with specified slice
    works = sorted([d for d in BASE_DIR.iterdir() if d.is_dir() and not d.name.startswith('.')])[start_idx:end_idx]

    results = []
    errors = []
    total_prompts = 0

    print(f"Processing Shakespeare works {start_idx+1}-{end_idx} (indices [{start_idx}:{end_idx}])...\n")

    for work_dir in works:
        print(f"Processing: {work_dir.name}...")
        result, error = process_work(work_dir)

        if error:
            errors.append({'work': work_dir.name, 'error': error})
            print(f"  ❌ Error: {error}")
        else:
            results.append(result)
            total_prompts += result['files_created']
            print(f"  ✓ Created {result['files_created']} prompts")
            if result['truncated'] > 0:
                print(f"    ⚠ {result['truncated']} prompts were truncated")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Works processed: {len(results)}")
    print(f"Total prompts generated: {total_prompts}")
    print(f"Errors encountered: {len(errors)}\n")

    if results:
        print("Details by work:")
        for r in results:
            print(f"  - {r['work']}: {r['files_created']} prompts")
            print(f"    Title: {r['book_title']}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e['work']}: {e['error']}")

if __name__ == "__main__":
    main()
