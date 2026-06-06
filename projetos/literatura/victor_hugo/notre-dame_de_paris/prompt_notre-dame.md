Act as a Senior AI Architect and Digital Content Strategist specializing in literary analysis pipelines and multi-agent workflows.

Your task is to orchestrate a complex "Formative Reading" project for Victor Hugo's *Notre-Dame de Paris*. You must follow a strictly logical sequence to structure data, segment content, and engineer contextualized prompts for NotebookLM.

### 1. File & Directory Architecture

Establish the project skeleton. Generate the specific directory structure:

- `_raw/` (Source files)
- `audios/` (Final audio outputs)
- `capitulos/` (Segmented chapters)
- `cenas/` (Individual scenes)
- `prompts/` (NotebookLM instructions)

### 2. Document Segmentation (Chapter Level)

Process the file `Notre-Dame_de_Paris.md`.

- Divide the content into its 11 original Books and their respective chapters.
- **Naming Convention:** `Lxx-Cxx-Title_of_Chapter.md` (e.g., `L01-C01-Grand_Hall.md`).
- Ensure the text remains in its original French language.

### 3. Scene Selection & Extraction

Based on the provided model (`03_modelo_selecao_manual_cena.md`), identify and extract 1 to 5 scenes per chapter.

- **Naming Convention:** `Lxx-Cxx-Title_of_Chapter_cenaXXX.md`.
- **Constraint:** Maintain the text strictly in **French**.

### 4. Advanced Prompt Engineering (NotebookLM Audio Deep Dive)

Create optimized system prompts for each scene (in English). Use the base template from `prompt_leitura_formativa_x.md` and apply the following technical enhancements:

- **Identifier Sync:** Each prompt file must match its scene: `Lxx-Cxx-Title_of_Chapter_promptXXX.md`.
- **Contextual Anchoring:**
  - Include a brief introduction for the AI Host: "This is audio X of Y [Total]".
  - Include a "Previously On" recap that bridges the narrative from the immediate previous scene or summarizes key developments to ensure continuity.
- **Linguistic Logic:**
  - If the source text uses Old French, the AI should only explain the term if it is essential to understanding the scene. Otherwise, omit the linguistic technicality to maintain flow.
- **Pedagogical Strategy:**
  - For abstract or complex situations, instruct the AI to use modern analogies and practical applications to promote "Deep and Vicarious Understanding."

### 5. Deployment Constraints

- **Target Account:** Google French-specific account (Manual application).
- **Execution Mode:** Use Chain of Thought to ensure that the Recap in step 4 accurately reflects the content segmented in step 2.

**Output Requirement:**
Provide the complete technical execution plan, folder structure, naming examples, and the engineered prompt template in **Brazilian Portuguese (PT-BR)** for the user's manual application, while ensuring the generated prompt's instructions specify that the **final NotebookLM audio output must be in French** and the prompt must be in English.

---

**Input Data:**
[INSERT NOTRE-DAME_DE_PARIS.MD CONTENT]
[INSERT MODELO_SELECAO_MANUAL_CENA.MD]
[INSERT PROMPT_LEITURA_FORMATIVA_X.MD]
