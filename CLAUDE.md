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

## Notebooks Disponíveis (Conta Michalk)

> **IMPORTANTE:** Os IDs dos notebooks desta conta ainda precisam ser levantados.
> Consulte `docs/notebooklm/notebooks_conta_michalk.md` quando disponível.

### Áreas de Conteúdo (a mapear)

- Medicina / Ciências da Saúde
- Tecnologia / Computação
- Ciência / Pesquisa

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
├── CLAUDE.md                       # Este arquivo (instruções do projeto)
├── AGENTS.md                       # Instruções de workflow para agentes
├── notebooklm-config.json          # Configuração do MCP
├── docs/
│   └── notebooklm/                 # Documentação do NotebookLM/MCP
│       ├── notebooks_conta_michalk.md  # IDs dos notebooks desta conta
│       ├── guia_uso_notebooklm.md
│       ├── como_authenticar.md
│       ├── limites_audio_overview.md
│       └── audio_overview_guide.md
├── scripts/                        # Scripts de automação
│   ├── audio_generator.py          # Gerador de áudios (principal)
│   └── generate_audio.sh           # Helper shell para geração rápida
├── tools/                          # Utilitários e testes
│   ├── test_mcp_client.py
│   ├── test_audio_generation.py
│   ├── list_all_mcp_tools.py
│   └── dashboard.html
└── logs/                           # Logs de execução
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
python scripts/audio_generator.py --notebook <NOTEBOOK_ID> --topic "Tema do deep-dive"

# Modo teste
python scripts/audio_generator.py --notebook <NOTEBOOK_ID> --topic "Tema" --test
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
python scripts/audio_generator.py --notebook <ID> --topic "Tema" --test

# 4. Sincronizar
bd sync
```

---

## Notas Importantes

- **Conta:** Esta é a conta técnica/científica (Michalk), diferente da conta pessoal (Edson)
- **Perfil nlm:** Pode precisar de um perfil separado para esta conta (`--profile michalk`)
- **Autenticação:** Consulte `docs/notebooklm/como_authenticar.md`
- **Backup:** O Beads sincroniza para `issues.jsonl` no Git
