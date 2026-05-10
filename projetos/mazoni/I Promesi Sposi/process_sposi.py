import os
import glob
import re

base_dir = '/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/mazoni/I Promesi Sposi'
capitoli_dir = os.path.join(base_dir, 'capitoli')
prompts_dir = os.path.join(base_dir, 'prompts')
cenas_dir = os.path.join(base_dir, 'cenas')

os.makedirs(prompts_dir, exist_ok=True)
os.makedirs(cenas_dir, exist_ok=True)

chapter_files = sorted(glob.glob(os.path.join(capitoli_dir, '*.md')))

def extract_scenes_from_chapter(chap_path):
    chap_filename = os.path.basename(chap_path)
    chap_name = chap_filename.replace('.md', '')
    
    with open(chap_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    text_lines = [l for l in lines if l.strip() and not l.startswith('#')]
    if not text_lines: return
    
    scenes = []
    current_scene_lines = []
    current_length = 0
    MAX_SCENE_CHARS = 5000
    
    for line in text_lines:
        if current_length + len(line) > MAX_SCENE_CHARS and current_scene_lines:
            scenes.append(current_scene_lines)
            current_scene_lines = [line]
            current_length = len(line)
            if len(scenes) == 10:  # Max 10 scenes per chapter
                break
        else:
            current_scene_lines.append(line)
            current_length += len(line)
            
    if current_scene_lines and len(scenes) < 10:
        scenes.append(current_scene_lines)
    
    scene_idx = 1
    for scene_lines in scenes:
        scene_text = "".join(scene_lines).strip()
        
        scene_id_str = f"cena{scene_idx:03d}"
        scene_filename = f"{chap_name}_{scene_id_str}.md"
        scene_path = os.path.join(cenas_dir, scene_filename)
        
        with open(scene_path, 'w', encoding='utf-8') as f:
            f.write(scene_text)
            
        # Ensure bounding strings are short
        first_line = scene_lines[0].strip()
        if len(first_line) > 200:
            first_line = first_line[:200] + "..."
            
        last_line = scene_lines[-1].strip()
        if len(last_line) > 200:
            last_line = "..." + last_line[-200:]
        
        prompt_id_str = f"prompt{scene_idx:03d}"
        prompt_filename = f"{chap_name}_{prompt_id_str}.md"
        prompt_path = os.path.join(prompts_dir, prompt_filename)
        
        prompt_content = f"""Act as a Senior Humanities Tutor specializing in the "Seminário de Filosofia" (COF) pedagogical approach. Your goal is to orchestrate an instructional audio deep-dive based on a specific scene from Alessandro Manzoni's *I Promessi Sposi*.

**Context & Anchoring:**
- **Scene Identifier:** {chap_name}_{scene_id_str}
- **Host Introduction:** Begin the audio by stating: "This is audio [X] of [Y Total]."
- **Previously On:** [INSERT BRIEF RECAP bridging the narrative from the immediate previous scene or summarize key developments to ensure continuity].

**Passage Selection (Focus of this Audio):**
The sources uploaded to NotebookLM contain the full chapters. For this specific audio, you must find and focus **EXCLUSIVELY** on the scene from chapter `{chap_name}` that is bounded by the following text:

**Starts at:** "{first_line}"
**Ends at:** "{last_line}"

**Task:**
Analyze the bounded scene. Use this passage to demonstrate the practical application of the four pillars of the "Methodology for Reading Novels".

**Script Structure & Instructions:**
1. **Introduction:** Briefly explain that we are performing a "Formative Reading" to break the "Individual Capsule" and map the world through Manzoni's eyes.
2. **The Preliminary Attitude:** Describe how to "believe in the work" and achieve "impregnation" using this scene.
3. **Practical Application of the 4 Pillars:**
   - **Primacy of Intuition:** Show how to experience the scene directly. What is the "Inner Form" of this moment?
   - **Existential Sincerity:** Analyze the raw human drama or moral dilemma. Forget modern political agendas.
   - **Affective and Imaginative Memory:** Explain how to store this scene as a living image to be evoked in real life.
   - **Literature as a Means:** How does this scene serve as a stepping stone toward a higher philosophical understanding?
4. **The Vicarious Experience:** Instruct the listener on how to "inhabit the skin" of the characters in this passage.

**Technical & Linguistic Constraints:**
- **Language:** The final NotebookLM audio output MUST be entirely in **Italian**.
- **Linguistic Logic:** The text may contain archaic Italian. Only explain terms if they are absolutely essential to understanding the scene; otherwise, omit linguistic technicalities to maintain flow.
- **Pedagogical Strategy:** For abstract or complex situations, use modern analogies and practical applications to promote "Deep and Vicarious Understanding".
- Use a pedagogical, calm, and insightful tone. Avoid academic jargon unless necessary for the analogy.
"""
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
            
        scene_idx += 1

for chap_file in chapter_files:
    extract_scenes_from_chapter(chap_file)

print(f"Processing complete for {len(chapter_files)} chapters.")
