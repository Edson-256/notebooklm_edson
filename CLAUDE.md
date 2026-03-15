# NotebookLM Michalk - Audios Educativos Técnicos/Científicos

## Sobre Este Projeto

Projeto para geração de **áudios educativos deep-dive** a partir de notebooks do **Google NotebookLM** (conta técnica/científica/médica) usando o **MCP (Model Context Protocol)** e a CLI `nlm`.

O foco é conteúdo **técnico, científico e médico** — diferente do projeto `notebooklm_edson` que foca em literatura e humanidades.

## Memory and Task System (Beads)

Este projeto usa **Beads (`bd`)** como sistema exclusivo para rastreamento de tarefas e memória persistente. Não crie ou mantenha arquivos como `TODO.md` ou `PLAN.md`.

### Mandatory Task Creation Rules

**CRITICAL:** Siga estas regras sem exceção:

1. **Nova Requisição do Usuário -> Criar Tarefa:** Quando o usuário solicitar uma nova tarefa, IMEDIATAMENTE crie no Beads usando `bd create "Descrição da tarefa" --json`. Faça isso ANTES de iniciar qualquer trabalho.
2. **Conclusão de Tarefa -> Fechar Tarefa:** Quando uma tarefa for concluída, IMEDIATAMENTE feche usando `bd close <id> --reason "Concluído: resumo breve"`.
3. **Nunca Pule:** Não pule a criação de tarefas mesmo para tarefas "simples". Todas as requisições do usuário devem ser rastreadas no Beads.

### Mandatory Workflow

1. **Início de Sessão:** Sempre comece executando `bd ready --json`.
2. **Execução:**
   * Ao iniciar uma tarefa, marque: `bd update <id> --status in_progress`.
   * Se a tarefa for complexa, divida criando sub-tarefas usando `bd create`.
3. **Descobertas:** Se encontrar um bug ou refatoração necessária, crie um registro imediato:
   * `bd create "Título do issue" --type bug --deps discovered-from:<current-task-id>`.
4. **Conclusão:** `bd close <id> --reason "Explicação breve"`.
5. **Fim de Sessão:** Execute `bd sync` para garantir que o banco de dados local seja gravado.

### Command Preferences

* **Formato de Saída:** Sempre use `--json` em comandos de leitura.
* **Dependências:** Use `bd dep add B A --type blocks` quando necessário.

### Self-Recovery

* Se suspeitar de problemas no banco, execute `bd doctor`.

---

## Notebooks Disponíveis (Conta Michalk - edson@michalkcare.com)

> **Perfil nlm:** `profissional`
> **Total:** 43 notebooks
> **Lista completa:** `docs/notebooklm/notebooks_conta_michalk.md`

### Medicina & Ciencias da Saude
- **Cirurgia Oncologica**: `231e5405-f082-4ac0-8020-894442a52b1d` (59 fontes)
- **DeVita - Cancer - por capitulo**: `25aa1a74-f3e3-43d6-85db-32d2f5c21495` (108 fontes)
- **NCCN Guidelines**: `edac906a-e1f7-45b1-9244-54c1d1b114df` (22 fontes)
- **Cirurgia Geral & Emergencias**: `a35737a9-fb79-4ad7-a026-81a6f22ea901` (26 fontes)
- **Cancer > Varias fontes**: `874cf376-9a99-4ec1-844c-ead09d838c48` (175 fontes)
- **Clinica Medica**: `0656b073-b93c-4841-975e-b49057f27328` (35 fontes)
- **Kaplan Psiquiatria**: `5c808f34-7d23-4857-943e-5e71c91fdcfa` (66 fontes)
- **CBHPM - Codigos e Auditoria**: `c69eb7af-4767-473a-ab2f-cf347506b511` (146 fontes)

### Ciencias Basicas
- **Fisiologia**: `d23c673d-ab72-42a6-8edc-83c42a8cd633` (112 fontes)
- **Bioquimica**: `6bdd6956-95e4-42ec-a55c-cf65273a8002` (55 fontes)
- **Patologia**: `813ca0d8-eaa6-4ed0-bcac-439ed526853c` (92 fontes)
- **Farmacologia**: `41afa80d-95ad-4dee-8e83-b35411ae6fb6` (78 fontes)
- **Imunologia - Janeway**: `ecc2966d-a437-4565-a18a-dd30e9459799` (39 fontes)

### Tecnologia & Automacao
- **Automacao de IA com n8n/Supabase/Tailscale**: `2ad2647e-044f-497c-b690-f77896d0456d` (47 fontes)
- **Guia de n8n Versao 2.0**: `c18d2cc4-171c-4029-9655-b18f3846ba3f` (81 fontes)
- **Claude Code**: `0f2c151c-d4cd-4f47-bb2e-7b99afe9df82` (11 fontes)

---

## Uso do MCP NotebookLM

### Ferramentas Disponíveis

- `navigate_to_notebook`: Abre um notebook específico
- `chat_with_notebook`: Envia uma mensagem e recebe resposta do NotebookLM
- `get_chat_response`: Obtém a última resposta
- `set_default_notebook`: Define notebook padrão
- `get_default_notebook`: Mostra o notebook configurado

### Como Encontrar ID de um Notebook

1. Acesse [NotebookLM](https://notebooklm.google.com/)
2. Abra o notebook desejado
3. O ID está na URL após `notebook/`

---

## Estrutura do Projeto

```
notebooklm_michalk/
├── CLAUDE.md                          # Este arquivo (instruções do projeto)
├── AGENTS.md                          # Instruções de workflow para agentes
├── README.md                          # Documentação técnica completa
├── como_usar_skill.md                 # Guia de uso do skill de áudio
├── notebooklm-config.json             # Configuração do MCP
│
├── projetos/                          # ← TODOS os projetos de áudio
│   ├── devita_cme/                    # DeVita Cancer (108 capítulos)
│   │   ├── chapter_index.json
│   │   ├── tracker.md
│   │   ├── audio/                     # 108 áudios .m4a
│   │   ├── scripts/                   # generate, download, next_batch
│   │   ├── prompts/                   # master_template + chapters/
│   │   ├── gaps/                      # Análises de lacunas
│   │   ├── logs/                      # Logs de geração
│   │   └── docs/                      # Plano mestre, prompts originais
│   │
│   ├── calculo/                       # Cálculo Munem-Foulis Vol 1 (52 seções)
│   │   ├── section_index.json
│   │   ├── calculo_runner.py
│   │   ├── munem_vol1/               # PDFs, imagens, áudios
│   │   ├── prompts/
│   │   └── docs/
│   │
│   ├── w_shakespeare/                 # Shakespeare (19 obras)
│   │   ├── scripts/                   # shakespeare_runner.py, batch.sh
│   │   └── {obra_name}/audios/        # Áudios por obra
│   │
│   └── cirurgia_oncologica/           # Cirurgia Oncológica (stub)
│       └── prompts/
│
├── docs/                              # Documentação geral
│   └── notebooklm/                    # Docs do NotebookLM/MCP
│
├── tools/                             # Utilitários genéricos
│   ├── audio_generator.py             # Gerador genérico de áudios
│   ├── generate_audio.sh              # Helper shell
│   ├── dashboard.html
│   ├── list_all_mcp_tools.py
│   ├── test_audio_generation.py
│   └── test_mcp_client.py
│
└── logs/                              # Logs globais
```

### Como Adicionar um Novo Projeto

Para criar um novo projeto de áudio, basta criar uma pasta em `projetos/`:

```bash
# Usar o skill: /notebooklm-audio-project <nome> <notebook_id> [--profile profissional|default]
# Ou manualmente: criar pasta em projetos/ seguindo o padrão do DeVita
```

---

## Geração de Áudios

### Diferenças em relação ao projeto `notebooklm_edson`

| Aspecto | notebooklm_edson (literário) | notebooklm_michalk (técnico) |
|---------|------------------------------|------------------------------|
| Conteúdo | Obras literárias (Shakespeare, Austen...) | Material técnico/científico/médico |
| Unidade | Cenas de livros | Tópicos/capítulos/conceitos |
| Prompt | Metodologia COF (Olavo de Carvalho) | Deep-dive técnico-educativo |
| Foco | Experiência vicária, imaginário | Mecanismos, evidência, aplicação prática |
| Prefixo | `ws_` (William Shakespeare) | `mk_` (Michalk) |

### Uso do Gerador

```bash
# Gerar áudio para um notebook específico
python tools/audio_generator.py --notebook <NOTEBOOK_ID> --topic "Tema do deep-dive"

# Modo teste
python tools/audio_generator.py --notebook <NOTEBOOK_ID> --topic "Tema" --test
```

---

## Objetivos do Projeto

1. **Gerar áudios educativos deep-dive** para conteúdo técnico/científico/médico
2. **Organizar notebooks** da conta Michalk com IDs e metadados
3. **Automatizar** a geração em batch quando houver múltiplos tópicos
4. **Rastrear progresso** via Beads

---

## Quick Start

```bash
# 1. Verificar tarefas prontas
bd ready --json

# 2. Levantar notebooks da conta
# (acessar NotebookLM e documentar IDs)

# 3. Gerar um áudio de teste
python tools/audio_generator.py --notebook <ID> --topic "Tema" --test

# 4. Sincronizar
bd sync
```

---

## Notas Importantes

- **Conta:** edson@michalkcare.com (conta técnica/científica)
- **Perfil nlm:** `profissional` (usar `--profile profissional` em todos os comandos nlm)
- **Autenticação:** Consulte `docs/notebooklm/como_authenticar.md`
- **Backup:** O Beads sincroniza para `issues.jsonl` no Git
