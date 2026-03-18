#!/usr/bin/env python3
"""
Parse Shakespeare scene files and build a work queue for audio generation.

Reads all 01_cenas_identificadas.md files from Shakespeare play subfolders,
extracts individual scenes, and generates a JSON work queue with pre-built
prompts ready for NotebookLM audio generation.
"""

import json
import os
import re
import sys
from pathlib import Path


# Paths
BASE_DIR = Path(__file__).parent
TEMPLATE_PATH = BASE_DIR.parent / "leitura_formativa" / "02_analise_profunda_cena.md"
METHODOLOGY_PATH = BASE_DIR.parent / "leitura_formativa" / "metodologia_olavo_carvalho.md"
OUTPUT_PATH = BASE_DIR / "audio_work_queue.json"
PROGRESS_PATH = BASE_DIR / "audio_progress.json"

AUTHOR = "William Shakespeare"


def load_template():
    """Load the audio script prompt template."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_methodology():
    """Load the methodology context text."""
    with open(METHODOLOGY_PATH, "r", encoding="utf-8") as f:
        return f.read()


def extract_title_from_h1(content: str) -> str:
    """Extract the book title from the H1 header."""
    match = re.search(r"^#\s+(.+?)(?:\s*—.*)?$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown"


def extract_scenes(content: str) -> list[dict]:
    """
    Extract individual scenes from a cenas_identificadas.md file.
    
    Each scene starts with ### N. Title and contains:
    - Location
    - Summary
    - COF Justification
    """
    scenes = []
    
    # Split by H3 headers (### N. Title)
    pattern = r"###\s+(\d+)\.\s+(.+?)(?=\n)"
    headers = list(re.finditer(pattern, content))
    
    for i, header in enumerate(headers):
        scene_num = header.group(1).strip()
        scene_title = header.group(2).strip()
        
        # Get content between this header and the next (or end of file)
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        scene_body = content[start:end].strip()
        
        # Extract location
        loc_match = re.search(r"\*\*Localização:\*\*\s*(.+?)(?:\n|$)", scene_body)
        location = loc_match.group(1).strip() if loc_match else ""
        
        # Extract summary
        sum_match = re.search(r"\*\*Resumo:\*\*\s*(.+?)(?=\n-\s*\*\*|\n###|\Z)", scene_body, re.DOTALL)
        summary = sum_match.group(1).strip() if sum_match else ""
        
        # Extract COF justification
        just_match = re.search(r"\*\*Justificativa COF:\*\*\s*(.+?)(?=\n###|\Z)", scene_body, re.DOTALL)
        justification = just_match.group(1).strip() if just_match else ""
        
        scenes.append({
            "number": scene_num,
            "title": scene_title,
            "location": location,
            "summary": summary,
            "justification": justification,
            "full_text": f"### {scene_num}. {scene_title}\n{scene_body}"
        })
    
    return scenes


def build_focus_prompt(scene: dict, book_title: str, template: str) -> str:
    """
    Build the focus prompt for audio_overview_create by filling in the template.
    """
    scene_context = (
        f"Título da Cena: {scene['title']}\n"
        f"Localização: {scene['location']}\n"
        f"Resumo: {scene['summary']}\n"
        f"Justificativa COF: {scene['justification']}"
    )
    
    prompt = template.replace("{{INSERT_SCENE_NUMBER}}", scene["number"])
    prompt = prompt.replace("{{INSERT_AUTHOR_NAME}}", AUTHOR)
    prompt = prompt.replace("{{INSERT_BOOK_TITLE}}", book_title)
    prompt = prompt.replace("{{INSERT_SELECTED_SCENE_OR_DESCRIPTION_HERE}}", scene_context)
    
    return prompt


def process_all_plays(single_play: str = None) -> list[dict]:
    """
    Process all plays (or a single one) and build the work queue.
    """
    template = load_template()
    work_queue = []
    
    # Get all play directories
    play_dirs = sorted([
        d for d in BASE_DIR.iterdir()
        if d.is_dir() and (d / "01_cenas_identificadas.md").exists()
    ])
    
    if single_play:
        play_dirs = [d for d in play_dirs if d.name == single_play]
        if not play_dirs:
            print(f"Error: Play '{single_play}' not found.")
            sys.exit(1)
    
    for play_dir in play_dirs:
        scene_file = play_dir / "01_cenas_identificadas.md"
        content = scene_file.read_text(encoding="utf-8")
        
        book_title = extract_title_from_h1(content)
        scenes = extract_scenes(content)
        
        print(f"  {play_dir.name}: {len(scenes)} scenes found ('{book_title}')")
        
        for scene in scenes:
            focus_prompt = build_focus_prompt(scene, book_title, template)
            
            work_queue.append({
                "play_dir": play_dir.name,
                "book_title": book_title,
                "scene_number": scene["number"],
                "scene_title": scene["title"],
                "location": scene["location"],
                "focus_prompt": focus_prompt,
                "status": "pending",
                "notebook_id": None,
                "audio_id": None,
            })
    
    return work_queue


def main():
    single_play = sys.argv[1] if len(sys.argv) > 1 else None
    
    mode_label = f"play '{single_play}'" if single_play else "all plays"
    print(f"\n📚 Parsing scenes for {mode_label}...\n")
    
    work_queue = process_all_plays(single_play)
    
    # Save work queue
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(work_queue, f, ensure_ascii=False, indent=2)
    
    # Initialize progress file if it doesn't exist
    if not PROGRESS_PATH.exists():
        progress = {
            "total_scenes": len(work_queue),
            "completed": 0,
            "errors": 0,
            "last_updated": None,
            "plays_processed": [],
        }
        with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Work queue saved: {OUTPUT_PATH}")
    print(f"   Total scenes: {len(work_queue)}")
    print(f"   Plays: {len(set(item['play_dir'] for item in work_queue))}")


if __name__ == "__main__":
    main()
