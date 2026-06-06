import os
import re

base_dir = '/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/victor_hugo/notre-dame_de_paris'
file_path = os.path.join(base_dir, 'Notre-Dame_de_Paris.md')

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

book_num = 0
chap_num = 0
current_book_title = ""
current_chap_title = ""
current_chap_lines = []

def clean_title(title):
    title = re.sub(r'\{.*?\}', '', title)
    title = re.sub(r'[^A-Za-z0-9\s-]', '', title)
    title = title.strip().replace(' ', '_')
    return title

def save_chapter():
    if book_num > 0 and chap_num > 0 and current_chap_lines:
        title = clean_title(current_chap_title)
        if not title:
            title = "Chapter"
        chap_name = f"L{book_num:02d}-C{chap_num:02d}-{title}"
        
        # Save chapter
        chap_path = os.path.join(base_dir, 'capitulos', f"{chap_name}.md")
        with open(chap_path, 'w', encoding='utf-8') as f:
            f.write("".join(current_chap_lines))
        
        # Extract scenes (divide chapter text by limiting characters)
        text_lines = [l for l in current_chap_lines if l.strip() and not l.startswith('#')]
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
                if len(scenes) == 5:  # Max 5 scenes per chapter
                    break
            else:
                current_scene_lines.append(line)
                current_length += len(line)
                
        if current_scene_lines and len(scenes) < 5:
            scenes.append(current_scene_lines)
        
        scene_idx = 1
        for scene_lines in scenes:
            scene_text = "".join(scene_lines).strip()
            
            scene_id_str = f"cena{scene_idx:03d}"
            scene_filename = f"{chap_name}_{scene_id_str}.md"
            scene_path = os.path.join(base_dir, 'cenas', scene_filename)
            
            with open(scene_path, 'w', encoding='utf-8') as f:
                f.write(scene_text)
                
            # Extract first and last sentences for the prompt anchor
            first_line = scene_lines[0].strip()
            last_line = scene_lines[-1].strip()
            
            # Write prompt
            prompt_id_str = f"prompt{scene_idx:03d}"
            prompt_filename = f"{chap_name}_{prompt_id_str}.md"
            prompt_path = os.path.join(base_dir, 'prompts', prompt_filename)
            
            prompt_content = f"""Act as a Senior Humanities Tutor specializing in the "Seminário de Filosofia" (COF) pedagogical approach. Your goal is to orchestrate an instructional audio deep-dive based on a specific scene from Victor Hugo's *Notre-Dame de Paris*.

**Context & Anchoring:**
- **Scene Identifier:** {chap_name}_{scene_id_str}
- **Host Introduction:** Begin the audio by stating: "This is audio [X] of [Y Total]."
- **Previously On:** [INSERT BRIEF RECAP bridging the narrative from the immediate previous scene or summarize key developments to ensure continuity].

**Passage Selection (Focus of this Audio):**
The sources uploaded to NotebookLM contain the full chapters. For this specific audio, you must find and focus **EXCLUSIVELY** on the scene from chapter `{chap_name}` that is bounded by the following text:

**Starts at:** "{first_line}"
**Ends at:** "{last_line}"

**Task:**
Analyze the bounded scene through the Formative Reading approach already established in this series. Apply the technique directly — do not re-explain it.

**Script Structure & Instructions:**
1. **Brief Anchor (1–2 sentences max):** Recall that this series uses the Formative Reading technique — impregnation, the four pillars, and vicarious experience — introduced in the opening audios. Do not re-explain the concepts; go directly into the scene.
2. **Primacy of Intuition:** What is the "Inner Form" of this moment? Let the scene speak first, before any analysis.
3. **Existential Sincerity:** What raw human drama or moral tension is at stake? What is Hugo revealing about the human condition here?
4. **Affective and Imaginative Memory:** How to carry this scene as a living image. In what real-life situations does this moment recur?
5. **Literature as a Means:** What philosophical horizon does this scene open? What truth does it point toward beyond itself?
6. **Vicarious Inhabitation:** Draw the listener fully into the skin of the characters — no methodological instruction, pure immersion.

**Technical & Linguistic Constraints:**
- **Language:** The final NotebookLM audio output MUST be entirely in **French**.
- **Linguistic Logic:** The text may contain Old French. Only explain terms if they are absolutely essential to understanding the scene; otherwise, omit linguistic technicalities to maintain flow.
- **Pedagogical Strategy:** For abstract or complex situations, use modern analogies and practical applications to promote "Deep and Vicarious Understanding".
- Use a pedagogical, calm, and insightful tone. Avoid academic jargon unless necessary for the analogy.
"""
            with open(prompt_path, 'w', encoding='utf-8') as f:
                f.write(prompt_content)
                
            scene_idx += 1

# Match lines like "# LIVRE PREMIER" or "# LIVRE DIXIÈME"
book_match = re.compile(r'^# LIVRE\s+(.*)')
# Match lines like "### I – LA GRAND’SALLE"
chap_match = re.compile(r'^###\s+[IVXLC]+\s+[-–]\s+(.*)')

for line in lines:
    bm = book_match.match(line)
    if bm:
        save_chapter()
        book_num += 1
        chap_num = 0
        current_book_title = bm.group(1).strip()
        current_chap_lines = []
        continue
        
    cm = chap_match.match(line)
    if cm:
        save_chapter()
        chap_num += 1
        current_chap_title = cm.group(1).strip()
        current_chap_lines = [line]
        continue
        
    if book_num > 0 and chap_num > 0:
        current_chap_lines.append(line)

# Save the last chapter
save_chapter()
print(f"Processing complete. Processed {book_num} books.")
