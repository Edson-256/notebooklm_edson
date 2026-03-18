# NotebookLM + Claude MCP Integration

## 📋 Sobre Este Projeto

Este projeto integra o **Google NotebookLM** ao **Claude** através do **MCP (Model Context Protocol)**, permitindo consultar e interagir com 36 notebooks temáticos organizados em filosofia, teologia, literatura, tecnologia e medicina.

### Contas NotebookLM e Perfis `nlm`

**IMPORTANTE:** Este projeto (`notebooklm_edson`) usa exclusivamente a **conta pessoal**. Sempre use `--profile default` nos comandos `nlm`.

| Perfil NLM | Conta Google | Uso |
|------------|-------------|-----|
| `default` | `edson.michalkiewicz@gmail.com` (pessoal) | **Este projeto** — todos os notebooks Shakespeare e demais |
| `profissional` | `edson@michalkcare.com` | Projeto separado (`notebooklm_michalk`) |

Todos os scripts neste repositório devem usar `PROFILE = "default"`. Se um comando `nlm` retornar lista vazia ou `status: None`, verifique se o `--profile default` está sendo passado.

## 🧠 Memory and Task System (Beads)

Este projeto usa **Beads (`bd`)** como sistema exclusivo para rastreamento de tarefas e memória persistente. Não crie ou mantenha arquivos como `TODO.md` ou `PLAN.md`.

### 🎯 Mandatory Task Creation Rules

**CRITICAL:** Siga estas regras sem exceção:

1. **Nova Requisição do Usuário → Criar Tarefa:** Quando o usuário solicitar uma nova tarefa, IMEDIATAMENTE crie no Beads usando `bd create "Descrição da tarefa" --json`. Faça isso ANTES de iniciar qualquer trabalho.
2. **Conclusão de Tarefa → Fechar Tarefa:** Quando uma tarefa for concluída, IMEDIATAMENTE feche usando `bd close <id> --reason "Concluído: resumo breve"`.
3. **Nunca Pule:** Não pule a criação de tarefas mesmo para tarefas "simples". Todas as requisições do usuário devem ser rastreadas no Beads.

### 🔄 Mandatory Workflow

1. **Início de Sessão:** Sempre comece executando `bd ready --json`. Isso lista apenas as tarefas atualmente desbloqueadas e acionáveis.
2. **Execução:**
   * Ao iniciar uma tarefa, marque: `bd update <id> --status in_progress`.
   * Se a tarefa for complexa, divida criando sub-tarefas (issues filhos) usando `bd create`.

3. **Descobertas:** Se encontrar um bug ou refatoração necessária enquanto trabalha em outra coisa, **não apenas anote**. Crie um registro imediato:
   * Comando: `bd create "Título do issue" --type bug --deps discovered-from:<current-task-id>`. Isso preserva o contexto de onde o erro se originou.

4. **Conclusão:** Quando terminar, feche a tarefa com `bd close <id> --reason "Explicação breve"`.
5. **Fim de Sessão:** Antes de encerrar sua resposta final, execute `bd sync` para garantir que o banco de dados local seja gravado no arquivo Git `issues.jsonl`.

### ⚙️ Command Preferences

* **Formato de Saída:** Sempre use a flag `--json` em comandos de leitura (ex: `bd list`, `bd show`, `bd ready`). Isso garante dados estruturados fáceis de analisar.
* **Dependências:** Respeite a hierarquia. Se a tarefa B não pode ser feita antes de A, use `bd dep add B A --type blocks`.

### 🚑 Self-Recovery

* Se suspeitar que o banco está dessincronizado ou corrompido, execute `bd doctor` para diagnóstico e correção automática.

---

## 📚 Notebooks Disponíveis

### Principais Notebooks por Área

#### 🧬 Filosofia & Pensamento
- **Platão**: `619d8d71-fdfb-4a23-94ad-0ecaea086da6`
- **Aristóteles**: `de324f7f-25ca-438c-96d5-16ff36a2bddc`
- **Eric Voegelin**: `5f3f4f41-625d-4ce2-b715-908a1e4e1046`
- **Mário Ferreira dos Santos**: `100978fc-4c83-470d-a514-ac2d547313ab`
- **Louis Lavelle**: `1e63d07b-d9ee-4b13-b7fb-808c53072b79`
- **Complexidade (Edgar Morin)**: `f9c8fa28-2e90-4bb5-8024-4ed5f8d0e6ac`

#### ⛪ Teologia & Religião
- **Suma Teológica (Tomás Aquino)**: `a9fcadbd-87f0-4802-ba5f-670932cd074f`
- **Suma contra os Gentios**: `633d6888-2498-4c4e-a459-bfe715f1df0f`
- **Patrística**: `6b1a60d1-dca5-4a2b-bf4d-e6c3dcd074ff`
- **Daily Exegesis**: `47301284-7202-4fdf-9922-79851cccbe57`
- **Apologéticos**: `f01d0686-ea3a-47e8-82ae-067cc161a365`

#### 📖 Literatura
- **Shakespeare (Completo)**: `19bde485-a9c1-4809-8884-e872b2b67b44`
- **Jane Austen (Completo)**: `40b0bb3f-afa6-49b2-959f-d91fb0a91a3b`
- **Georges Bernanos**: `cd66e98f-bee1-429c-b8cd-3e0b678a48af`
- **Notre Dame de Paris (Victor Hugo)**: `da2bcdc2-2900-4c5f-8b78-03b5755b9b9d`
- **Ben-Hur**: `1ecdbff9-2511-4a7f-99a0-10d3eadc1042`

#### 💻 Tecnologia & Ferramentas
- **Claude Code**: `3d1e250c-47e7-42f6-9df7-86c2b6623f4a`
- **Beads BD Software**: `cb7a2fcd-e7fd-49d0-bdae-f2b315600051`
- **Docker**: `85d38ec1-7659-4307-aedf-3bc773a4d4ba`
- **n8n (Guia Completo)**: `1b562c95-0d1d-4d47-9561-dd268bc9fbe6`
- **Drafts Ecosystem**: `04f4aac0-924c-4803-8b28-9ae89cbcb30f`

#### 🏥 Medicina
- **Perícia Médica Brasileira**: `e5f0fdb9-3a07-4218-bf91-c8defc6ddfee`
- **APIs ClinicWeb e EHR**: `6d28620d-efb8-4c01-9e07-c4f56318c288`

#### 🧠 Psicanálise
- **Freud**: `bdb7eeaf-70db-4ff8-983b-1c51012c331b`
- **Jacques Lacan**: `2d678850-c015-431a-91ba-0a3a8297431e`

**Lista completa:** Consulte `docs/notebooklm/notebooks_conta_pessoal.md` para ver todos os 36 notebooks.

---

## 🔧 Uso do MCP NotebookLM

### Ferramentas Disponíveis

O servidor MCP oferece as seguintes ferramentas:

- `navigate_to_notebook`: Abre um notebook específico
- `chat_with_notebook`: Envia uma mensagem e recebe resposta do NotebookLM
- `get_chat_response`: Obtém a última resposta (útil para respostas longas)
- `set_default_notebook`: Define qual notebook usar se nenhum for especificado
- `get_default_notebook`: Mostra qual está configurado atualmente

### Como Encontrar ID de um Notebook

1. Acesse [NotebookLM](https://notebooklm.google.com/)
2. Abra o notebook desejado
3. O ID está na URL após `notebook/`
   - Exemplo: `https://notebooklm.google.com/notebook/1a2b3c-4d5e6f-7g8h9i`
   - ID: `1a2b3c-4d5e6f-7g8h9i`

### Exemplos de Uso

```bash
# Definir notebook padrão
set_default_notebook(notebook_id="3d1e250c-47e7-42f6-9df7-86c2b6623f4a")

# Consultar notebook de filosofia
chat_with_notebook(
  notebook_id="619d8d71-fdfb-4a23-94ad-0ecaea086da6",
  message="Qual é a teoria das formas de Platão?"
)
```

---

## 📂 Estrutura do Projeto

```
notebooklm_edson/
├── CLAUDE.md                       # Este arquivo (instruções do projeto)
├── AGENTS.md                       # Instruções de workflow para agentes
├── docs/
│   ├── notebooklm/                 # Documentação do NotebookLM/MCP/LLM CLI
│   │   ├── guia_uso_notebooklm.md
│   │   ├── como_authenticar.md
│   │   ├── notebooks_conta_pessoal.md
│   │   ├── meus_notebooks.md
│   │   ├── limites_audio_overview.md
│   │   ├── audio_overview_guide.md
│   │   └── install_log.md
│   └── shakespeare/                # Documentação do projeto Shakespeare
│       ├── estrategia_nomenclatura.md
│       ├── resumo_tarefa_audio.md
│       ├── automacao.md
│       └── padrao_nomes_arquivos.md
├── scripts/                        # Scripts de automação e batch
├── tools/                          # Utilitários e testes
│   ├── test_mcp_client.py
│   ├── test_audio_generation.py
│   ├── list_all_mcp_tools.py
│   └── dashboard.html
├── projetos/                       # Projetos de conteúdo
│   ├── w_shakespeare/              # Dados e áudios de Shakespeare
│   └── g_flynn/                    # Projeto Gone Girl
├── leitura_formativa/              # Metodologia de leitura formativa
└── logs/                           # Logs de execução
```

---

## 🎯 Objetivos do Projeto

1. **Integração Eficiente:** Consultar notebooks do NotebookLM diretamente do Claude
2. **Gestão de Conhecimento:** Organizar e acessar 36 notebooks temáticos
3. **Rastreamento de Tarefas:** Usar Beads para manter histórico de trabalho
4. **Automação:** Desenvolver scripts e ferramentas para melhorar o workflow

---

## 🚀 Quick Start

```bash
# 1. Verificar tarefas prontas
bd ready --json

# 2. Testar conexão MCP
python tools/test_mcp_client.py

# 3. Criar nova tarefa
bd create "Título da tarefa" --description "Detalhes" --json

# 4. Sincronizar no final
bd sync
```

---

## 📝 Notas Importantes

- **Versão do servidor MCP:** v0.1.15 (não lista notebooks automaticamente, use IDs manualmente)
- **Autenticação:** Consulte `docs/notebooklm/como_authenticar.md` para configuração
- **IDs dos notebooks:** Sempre use os IDs documentados em `docs/notebooklm/notebooks_conta_pessoal.md`
- **Backup:** O Beads sincroniza automaticamente para `issues.jsonl` no Git
