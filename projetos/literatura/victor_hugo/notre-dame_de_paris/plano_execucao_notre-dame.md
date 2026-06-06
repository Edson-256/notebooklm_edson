# Plano de Execução Técnica: Leitura Formativa - *Notre-Dame de Paris*

Este documento detalha a orquestração do projeto de Leitura Formativa da obra *Notre-Dame de Paris*, de Victor Hugo, configurado para uso avançado no NotebookLM com foco em áudios de imersão ("Audio Deep Dive").

## 1. Arquitetura de Diretórios (Concluída)
A estrutura de pastas base foi criada no diretório do projeto:
- `_raw/` : Arquivos de origem e documentação bruta.
- `audios/` : Saídas finais de áudio geradas pelo NotebookLM.
- `capitulos/` : Capítulos individuais após a segmentação da obra completa.
- `cenas/` : Cenas individuais extraídas dos capítulos.
- `prompts/` : Instruções otimizadas para o NotebookLM.

## 2. Segmentação de Documentos (Nível de Capítulo)
O arquivo completo `Notre-Dame_de_Paris.md` deve ser dividido nos 11 Livros originais e seus respectivos capítulos. O texto deve ser mantido estritamente em **Francês**.

**Exemplos de Nomenclatura:**
- `L01-C01-Grand_Hall.md`
- `L01-C02-Pierre_Gringoire.md`
- `L02-C01-De_Charybde_en_Scylla.md`

## 3. Seleção e Extração de Cenas
Com base no modelo `03_modelo_selecao_manual_cena.md`, extraia de 1 a 5 cenas mais relevantes por capítulo. Assim como nos capítulos, o texto das cenas deve ser mantido no idioma original (**Francês**).

**Exemplos de Nomenclatura:**
- `L01-C01-Grand_Hall_cena001.md`
- `L01-C01-Grand_Hall_cena002.md`
- `L04-C03-Immanis_Pecoris_Custos_cena015.md`

## 4. Engenharia Avançada de Prompts (NotebookLM)
Para cada cena, crie um prompt de sistema correspondente na pasta `prompts/`. A instrução deve ser redigida em **Inglês**, mas forçar a saída de áudio para o **Francês**. 

**Exemplos de Nomenclatura:**
- `L01-C01-Grand_Hall_prompt001.md` (corresponde a `cena001.md`)

### Template de Prompt Base:

```markdown
Act as a Senior Humanities Tutor specializing in the "Seminário de Filosofia" (COF) pedagogical approach. Your goal is to orchestrate an instructional audio deep-dive based on a specific scene from Victor Hugo's *Notre-Dame de Paris*.

**Context & Anchoring:**
- **Scene Identifier:** [INSERT SCENE NAME, e.g., L01-C01-Grand_Hall_cena001]
- **Host Introduction:** Begin the audio by stating: "This is audio [X] of [Y Total]."
- **Previously On:** [INSERT BRIEF RECAP bridging the narrative from the immediate previous scene or summarize key developments to ensure continuity].

**Task:**
Analyze the provided scene. Use this passage to demonstrate the practical application of the four pillars of the "Methodology for Reading Novels".

**Script Structure & Instructions:**
1. **Introduction:** Briefly explain that we are performing a "Formative Reading" to break the "Individual Capsule" and map the world through Hugo's eyes.
2. **The Preliminary Attitude:** Describe how to "believe in the work" and achieve "impregnation" using this scene.
3. **Practical Application of the 4 Pillars:**
   - **Primacy of Intuition:** Show how to experience the scene directly. What is the "Inner Form" of this moment?
   - **Existential Sincerity:** Analyze the raw human drama or moral dilemma. Forget modern political agendas.
   - **Affective and Imaginative Memory:** Explain how to store this scene as a living image to be evoked in real life.
   - **Literature as a Means:** How does this scene serve as a stepping stone toward a higher philosophical understanding?
4. **The Vicarious Experience:** Instruct the listener on how to "inhabit the skin" of the characters in this passage.

**Technical & Linguistic Constraints:**
- **Language:** The final NotebookLM audio output MUST be entirely in **French**.
- **Linguistic Logic:** The text may contain Old French. Only explain terms if they are absolutely essential to understanding the scene; otherwise, omit linguistic technicalities to maintain flow.
- **Pedagogical Strategy:** For abstract or complex situations, use modern analogies and practical applications to promote "Deep and Vicarious Understanding".
- Use a pedagogical, calm, and insightful tone. Avoid academic jargon unless necessary for the analogy.

**Passage Selection (Focus of this Audio):**
The sources uploaded to NotebookLM contain the full chapters. For this specific audio, you must find and focus **EXCLUSIVELY** on the scene from chapter `[INSERT CHAPTER NAME]` that is bounded by the following text:

**Starts at:** "[INSERT FIRST SENTENCE OF SCENE]"
**Ends at:** "[INSERT LAST SENTENCE OF SCENE]"
```

## 5. Restrições e Deploy (Aplicação Manual)
- **Conta Alvo:** A conta do Google a ser utilizada deve ter configurações otimizadas para o idioma Francês.
- **Modo de Execução:** Utilize raciocínio estruturado ("Chain of Thought") ao montar os prompts. Ao redigir o trecho de "Previously On", certifique-se de que ele esteja perfeitamente alinhado com o contexto do capítulo fragmentado (Passo 2) e com a cena anterior para criar continuidade linear na série de áudios.
