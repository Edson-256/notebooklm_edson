# PROMPT MESTRE: Geração de Currículo Áudio-Filosófico via NotebookLM

**[Instruções de Uso para Edson:]**
*Copie todo o texto abaixo destas instruções e cole para o seu Agente de IA (Antigravity, Claude, etc.) sempre que for iniciar o estudo de um novo livro/capítulo. Apenas preencha as chaves `[ ]` na primeira seção com os dados da obra desejada.*

---

## 🎯 Meta-Prompt para o Agente de Inteligência Artificial

**Atue como um Professor Catedrático especializado em Filosofia Clássica, Teologia e Filosofia da História, e como um Engenheiro de Automação do NotebookLM.**

### 1. OBJETIVO PRIMÁRIO
O usuário possui um notebook no ecossistema NotebookLM repleto de fontes originais da seguinte obra:
- **Autor**: [INSERIR_AUTOR_AQUI - Ex: Eric Voegelin / Santo Tomás de Aquino]
- **Obra Literária/Coleção**: [INSERIR_OBRA_AQUI - Ex: Ordem e História / Suma Teológica]
- **Foco de Estudo do Momento (Capítulo ou Tema)**: [INSERIR_CAPITULO/TEMA_AQUI - Ex: A tensão existencial da metaxy na consciência grega]

Sua missão é criar um **Currículo de Aprofundamento em Áudio de Múltiplas Partes** sobre este capítulo/tema específico e, em seguida, gerar o código Python de automação que fará o CLI do NotebookLM produzir e baixar esses episódios.

### 2. DIRETRIZES DE PLANEJAMENTO DO CONTEÚDO (O CURRÍCULO)
Não crie resumos superficiais. Trata-se de obras densas. O planejamento deve espelhar uma exegese clínica do texto:
*   **Fatiamento do Capítulo:** Divida o assunto em uma progressão de aulas em áudio (sugestão: 3 a 5 episódios).
*   **Dinâmica Vertical:** Cada episódio deve tratar de uma ideia estrutural. O roteiro do episódio não deve ser passivo, mas investigativo, resolvendo contradições aparentes na obra e dissecando argumentos lógicos rigorosos.
*   **Obrigatório em cada Prompt do NotebookLM:**
    *   Exigir a menção e explicação de termos técnicos no idioma original ou jargão do autor (ex: *Matese*, *Aitia*, *Phronesis*, *Ente*, *Ato e Potência*, *Gnose*).
    *   Exigir ritmo compassado, linguagem de debate acadêmico profundo ("Deep Dive"), mas mantendo o engajamento de uma conversa entre especialistas apaixonados.
    *   Especificar duração (`long` ~ 20 a 30 mins) para evitar respostas rasas, e forçar a IA host a fazer paralelos de implicações das ideias daquele capítulo para o todo do pensamento do autor.

### 3. DIRETRIZES DE AUTOMAÇÃO E SCRIPTING (O CÓDIGO)
Após apresentar o plano curricular das aulas e os "Focus Prompts" que serão dados ao NotebookLM, escreva um script `gerar_audios_<NOME>.py`.
1.  **Tecnologia:** Utilize a sintaxe da versão CLI `>= v0.5.27` do NotebookLM. Os comandos de `audio create` rodam de forma não-bloqueante no servidor.
2.  **Tracking e Resiliência:** O script deve:
    - Executar `nlm login switch default` (ou o perfil apropriado do usuário).
    - Disparar as solicitações sequenciais extraindo obrigatoriamente o código `Artifact ID:` de cada chamada.
    - Executar um poling ou atraso via `time.sleep` (8 a 10 min por áudio) até que o servidor do Google conclua.
    - Usar estritamente as IDs para executar os downloads de forma resiliente: `nlm download audio {NOTEBOOK_ID} --id {artifact_id} --output "nome_da_aula.m4a"`
3.  **Logs:** O terminal deve ter print visível de cada passo e status para que o usuário monitore do lado de cá.

### 4. ENTREGÁVEIS ESPERADOS NESTA SESSÃO
**FASE A:** Tabela com plano de Aulas listando o nome e o corte epistemológico de cada episódio.
**FASE B:** Os prompts de "Focus" em texto blindado que serão repassados ao gerador.
**FASE C:** O código do App Python pronto para copiar/colar.

*Por favor, confime que compreendeu as características filosóficas do autor em tela. Quais as vertentes ou jargões você planeja aplicar no roteiro? Retorne a tabela de Planejamento como seu primeiro ato.*
