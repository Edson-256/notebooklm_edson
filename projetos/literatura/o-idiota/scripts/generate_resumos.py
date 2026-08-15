#!/usr/bin/env python3
"""
Script to generate structured chapter summaries for 'O Idiota' using NotebookLM CLI.
Target folder: projetos/literatura/o-idiota/output/resumos_capitulos/C0xx.md
"""

import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE_DIR = Path("/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/o-idiota")
OUTPUT_DIR = BASE_DIR / "output" / "resumos_capitulos"
SOURCES_MAP_FILE = BASE_DIR / "_sources_map.json"
NOTEBOOK_ID = "4a5dcdd3-94fc-4a87-b7b3-3871379dadf8"
PROFILE = "profissional"

PART_NAMES = {
    "P1": "primeira parte",
    "P2": "segunda parte",
    "P3": "terceira parte",
    "P4": "quarta parte"
}

def clean_summary_text(text: str) -> str:
    """Removes citations, trailing model notes, and cleans markdown format."""
    # Remove citation tags like [1], [1, 2], [1-3], [1–4], etc.
    text = re.sub(r'\s*\[\d+(?:[–\-,\s]+\d+)*\]', '', text)
    
    # Remove trailing suggestion notes like --- \n 💡 Se você desejar... or Se você quiser...
    text = re.sub(r'\n+---\s*\n+💡.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\n+---\s*\n+Se você desejar.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\n+💡\s*Se você desejar.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\n+Gostaria de prosseguir.*$', '', text, flags=re.DOTALL)
    
    # Clean multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip() + "\n"

def process_chapter(title: str, source_id: str, max_retries: int = 3) -> bool:
    # Match OI-P1-C004 (IV)
    m = re.match(r'OI-(P\d+)-(C\d+)\s*\((.*?)\)', title)
    if not m:
        print(f"[WARN] Cannot parse title: {title}")
        return False
    
    part_code, chap_code, roman = m.groups()
    part_name = PART_NAMES.get(part_code, f"parte {part_code}")
    out_file = OUTPUT_DIR / f"{chap_code}.md"
    
    if out_file.exists() and out_file.stat().st_size > 500:
        print(f"[SKIP] {chap_code}.md already exists ({out_file.stat().st_size} bytes)")
        return True
    
    prompt = (
        f"Crie um resumo detalhado e estruturado deste capítulo seguindo rigorosamente o seguinte formato e tom:\n\n"
        f"Linha inicial:\n"
        f"Este texto corresponde ao **Capítulo {roman}** da {part_name} de *O Ídiota*, de Fiódor Dostoiévski. [Uma a duas frases de introdução/contextualização sintetizando o foco central do capítulo].\n\n"
        f"---\n\n"
        f"### **Resumo do Capítulo**\n\n"
        f"[Organize em tópicos principais com marcadores e subtópicos detalhados com títulos em negrito, cobrindo com profundidade e precisão todos os acontecimentos, diálogos centrais, reflexões e desdobramentos dramáticos do capítulo.]"
    )
    
    cmd = [
        "nlm", "query", "notebook",
        NOTEBOOK_ID,
        prompt,
        "-s", source_id,
        "-p", PROFILE,
        "--json"
    ]
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[START] {chap_code} (attempt {attempt})...")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if res.returncode != 0:
                print(f"[ERR] {chap_code} failed with code {res.returncode}: {res.stderr.strip()[:200]}")
                time.sleep(5 * attempt)
                continue
            
            data = json.loads(res.stdout)
            answer = data.get("answer", "")
            if not answer or len(answer) < 200:
                print(f"[WARN] {chap_code} got empty/short answer: {answer[:100]}")
                time.sleep(5 * attempt)
                continue
            
            cleaned = clean_summary_text(answer)
            out_file.write_text(cleaned, encoding="utf-8")
            print(f"[DONE] {chap_code}.md saved ({len(cleaned)} chars)")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {chap_code} timed out on attempt {attempt}")
            time.sleep(5 * attempt)
        except Exception as e:
            print(f"[EXCEPT] {chap_code} error: {e}")
            time.sleep(5 * attempt)
            
    print(f"[FAIL] Could not generate {chap_code}.md after {max_retries} attempts")
    return False

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not SOURCES_MAP_FILE.exists():
        print(f"Error: {SOURCES_MAP_FILE} not found")
        sys.exit(1)
        
    with open(SOURCES_MAP_FILE, "r", encoding="utf-8") as f:
        sources_map = json.load(f)
        
    print(f"Loaded {len(sources_map)} sources from {SOURCES_MAP_FILE}")
    
    # Concurrency: 3 workers
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(process_chapter, title, s_id): title
            for title, s_id in sources_map.items()
        }
        
        success_count = 0
        total_count = len(futures)
        for future in as_completed(futures):
            title = futures[future]
            try:
                if future.result():
                    success_count += 1
            except Exception as exc:
                print(f"[ERROR] Exception processing {title}: {exc}")
                
    print(f"\n==========================================")
    print(f"Finished: {success_count}/{total_count} chapter summaries generated.")
    print(f"Directory: {OUTPUT_DIR}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
