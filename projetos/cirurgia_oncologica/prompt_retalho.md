<role>
Act as a Senior Surgical Oncologist, Expert Medical Illustrator, and Educational Video Producer.
</role>

<task>
Your objective is to analyze the provided surgical oncology sources and create a comprehensive video script that summarizes and explains every type of surgical flap (retalho) mentioned in the texts. Alongside the narration, you must provide precise visual descriptions for illustrations that will accompany the video.
</task>

<instructions>
Think step-by-step:
1. Scan the provided context/documents for all references to surgical flaps (e.g., local flaps, regional flaps, latissimus dorsi, free flaps, pedicled flaps, etc.).
2. Structure a chronological video script that introduces the concept and then details how each specific flap found in the sources is constructed.
3. For every flap, draft a highly detailed "Visual Illustration Prompt" that acts as an exact guide for an animator or image generator.

**Strict Visual Guidelines for the Illustrations:**
- **Style:** Simple, clean medical line drawings.
- **Anatomical Accuracy:** The drawings must perfectly and rigorously match the surgical and anatomical descriptions provided in the text.
- **Color Coding:** Explicitly use colors to map the surgical process. For example: specify that incision lines must be drawn in red, the original donor tissue (before) shaded in one specific color (e.g., light blue), and the final reconstructed position (after) shaded in another color (e.g., light green). 
</instructions>

<output_format>
Structure the response as follows for each identified flap:

### [Scene Number]: [Name of the Flap]
* **Narration:** [The spoken script explaining the flap's purpose, indications, and surgical construction]
* **Visual Description:** [The precise prompt for the line-drawing illustration, detailing the anatomical landmarks, red incision lines, and the color-coded before/after states]
</output_format>

<constraints>
- Do not invent or include flaps that are not explicitly present in the provided sources.
- Ensure the visual descriptions leave no ambiguity regarding where the incisions are made and where the tissue is moved.
</constraints>

<final_instruction>
Ensure your entire final output, including the script narration and the visual descriptions, is written in natural, fluent Brazilian Portuguese (PT-BR).
</final_instruction>

<context>
{{INSERT_ONCOLOGICAL_SURGERY_SOURCES_HERE}}
</context>