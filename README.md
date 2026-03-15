# NotebookLM Michalk — Sistema de Geração de Áudios Educativos

Sistema automatizado de geração de **áudios educativos deep-dive** a partir de notebooks do Google NotebookLM, utilizando a CLI `nlm` e arquitetura fire-and-forget.

**Conta:** `edson@michalkcare.com` (técnica/científica/médica)
**Perfil nlm:** `profissional`
**Plano Google:** NotebookLM Pro (50 áudios/dia)

---

## Sumário

- [1. Visão Geral](#1-visão-geral)
- [2. Arquitetura dos Scripts](#2-arquitetura-dos-scripts)
- [3. Processo de Download](#3-processo-de-download)
- [4. Interface de Linha de Comando (CLI)](#4-interface-de-linha-de-comando-cli)
- [5. Estatísticas de Execução](#5-estatísticas-de-execução)
- [6. Organização de Diretórios](#6-organização-de-diretórios)
- [7. Limites do NotebookLM Pro](#7-limites-do-notebooklm-pro)
- [8. Guia de Replicação para Novos Livros](#8-guia-de-replicação-para-novos-livros)
- [9. Resolução de Problemas](#9-resolução-de-problemas)
- [10. Tempos de Referência](#10-tempos-de-referência)

---

## 1. Visão Geral

### Objetivo

Gerar podcasts educacionais (audio overviews) de alta densidade técnica a partir de livros e materiais científicos carregados no Google NotebookLM. Cada capítulo/seção do livro é convertido em um episódio de áudio de 15–45 minutos, narrado em português brasileiro por dois apresentadores de IA do NotebookLM.

### Projetos Ativos

| Projeto | Livro | Notebook ID | Capítulos | Status |
|---------|-------|-------------|-----------|--------|
| **DeVita CME** | DeVita Cancer 12ª ed. | `25aa1a74-f3e3-43d6-85db-32d2f5c21495` | 108 | 98% concluído |
| **Cálculo** | Munem-Foulis Vol. 1 | `0c022710-25e0-44e2-9bfa-0d6daa219c17` | 52 | Em andamento |

### Pré-requisitos

| Componente | Versão | Localização |
|------------|--------|-------------|
| Python | 3.14+ | `/opt/homebrew/bin/python3` |
| nlm CLI | 0.4.0+ | `~/.local/bin/nlm` |
| Beads (bd) | latest | Sistema de tarefas |
| uv | latest | Gerenciador de pacotes Python |

---

## 2. Arquitetura dos Scripts

### 2.1 Arquitetura Fire-and-Forget (Duas Fases)

O sistema utiliza uma estratégia de **fire-and-forget** para maximizar throughput. O Google NotebookLM leva 8–15 minutos para processar cada áudio. Esperar inline tornaria o processo impraticável (~6.5h para 20 áudios). Com fire-and-forget, 20 áudios levam ~40 minutos.

```
┌──────────────────────────────────────────────────────────────┐
│  FASE 1 — CRIAÇÃO (fire-and-forget)                          │
│                                                              │
│  Para cada capítulo/seção:                                   │
│    1. Carregar prompt customizado (~2500 chars)               │
│    2. nlm create audio --focus PROMPT --source-ids SOURCE     │
│    3. Extrair artifact_id do output (regex)                  │
│    4. Salvar artifact_id no JSON de metadados                │
│    5. Aguardar 2 minutos (rate limiting)                     │
│    6. Próximo capítulo                                       │
│                                                              │
│  Resultado: todos os artifacts criados com status="created"  │
└──────────────────────────────────────────────────────────────┘
                          │
                   (aguardar ~15 min)
                          │
┌──────────────────────────────────────────────────────────────┐
│  FASE 2 — DOWNLOAD (execução separada)                       │
│                                                              │
│  1. nlm studio status → consultar status de todos artifacts  │
│  2. Para cada artifact com status "completed":               │
│     a. nlm download audio --id ARTIFACT_ID → salvar .m4a     │
│     b. Atualizar metadados: status → "downloaded"            │
│  3. Marcar artifacts com status "failed" → "error"           │
│  4. Pular artifacts ainda em processamento                   │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Fluxo de Estados

```
                    create_audio()
[pending] ──────────────────────────► [generating]
                                           │
                                    sucesso │ falha
                                           │
                              ┌────────────┼────────────┐
                              ▼                         ▼
                         [created]                  [failed]
                              │
                       download_audio()
                              │
                    ┌─────────┼──────────┐
                    ▼         ▼          ▼
              [downloaded] [error]  [still processing]
                                    (tentar depois)
```

### 2.3 Mapa de Scripts

O projeto possui três camadas de scripts, organizadas por nível de especialização:

```
tools/
├── audio_generator.py                   ← Gerador genérico (qualquer notebook)
└── generate_audio.sh                    ← Helper Bash para geração rápida

projetos/devita_cme/scripts/
├── generate_devita_audio.py             ← Gerador especializado DeVita (Fase 1)
├── download_audios.py                   ← Download dedicado DeVita (Fase 2)
└── next_batch.py                        ← Orquestrador de batches DeVita

projetos/calculo/
└── calculo_runner.py                    ← Runner unificado Munem-Foulis (Fases 1 e 2)

projetos/w_shakespeare/scripts/
├── shakespeare_runner.py                ← Runner fire-and-forget Shakespeare
└── run_shakespeare_batch.sh             ← Wrapper para execução via cron
```

#### `tools/audio_generator.py` — Gerador Genérico

Script multi-propósito que funciona com qualquer notebook. Diferente dos especializados, este **aguarda o processamento inline** (polling a cada 30s por até 30 min) e faz download imediato. Ideal para gerações unitárias.

- Classe `AudioGenerator`: create → poll → download → delete
- Modos: `--topic` (single) ou `--topics-file` (batch via JSON)
- Verifica autenticação antes de iniciar
- Salva `metadata.json` cumulativo por notebook

#### `projetos/devita_cme/scripts/generate_devita_audio.py` — Criação DeVita

Dispara criação de áudios para capítulos específicos do DeVita.

- Carrega prompts customizados de `prompts/chapters/ch{NNN}_*.txt`
- Fallback para prompt genérico se não existir prompt customizado
- Extrai `artifact_id` via regex (dois padrões de fallback)
- Gera log JSON de cada sessão de geração
- Intervalo de 120s entre criações

#### `projetos/devita_cme/scripts/download_audios.py` — Download DeVita

Fase 2 dedicada: verifica studio e baixa somente os completos.

- Consulta `nlm studio status` para mapear `artifact_id → status`
- Só baixa artifacts com status `completed`
- Marca `failed` como `error` no índice
- Proteção contra re-download (verifica se arquivo já existe)
- Suporta download seletivo por capítulo (`--chapters`)

#### `projetos/devita_cme/scripts/next_batch.py` — Orquestrador de Batch

Camada de conveniência que seleciona os próximos N capítulos pendentes e delega execução.

- Exibe dashboard de progresso (total, baixados, pendentes, erros)
- Seleciona automaticamente os próximos capítulos `pending`
- Delega criação para `generate_devita_audio.py`
- Delega download para `download_audios.py` (via `--download`)
- Padrão: dry-run (preview). Requer `--go` para executar

#### `projetos/calculo/calculo_runner.py` — Runner Unificado Cálculo

Script que unifica Fases 1 e 2 para o projeto Munem-Foulis.

- Lê `section_index.json` com 52 seções mapeadas
- Prompt template focado em ponte "ensino médio → cálculo"
- Seleção por IDs específicos (`--sections 1,2,3`) ou automática (`--max-sections N`)
- Dashboard visual com ícones por capítulo e seção
- Intervalo de 120s entre criações

### 2.4 Sistema de Prompts

Cada projeto utiliza prompts customizados que maximizam a qualidade do áudio gerado:

**DeVita CME — Template Mestre** (`projetos/devita_cme/prompts/master_template.md`):

```
Dois especialistas médicos brasileiros em diálogo:
  - Oncologista clínico + Oncologista cirúrgico
  - Revisão sistemática do DeVita Cancer 12ª ed.

ENFATIZE: raciocínio fisiopatológico, evolução das evidências,
pontos de decisão cirúrgica, controvérsias ativas, comparações
terapêuticas, conceitos contraintuitivos, mudanças da 12ª edição,
implicações para o contexto brasileiro.

IDENTIFIQUE LACUNAS: 3-5 "pontos para aprofundar"
```

**Cálculo Munem-Foulis — Template**:

```
Expert Mathematics Educator criando Deep Dive em PT-BR.
Público-alvo: estudantes iniciando Cálculo com base sólida do ensino médio.

Estrutura: hook real → ponte ensino médio → cálculo →
definições/teoremas sem jargão → exemplo verbal → recapitulação
```

### 2.5 Comando `nlm` — Anatomia da Chamada

```bash
nlm create audio NOTEBOOK_ID \
    --format deep_dive \          # Formato: deep_dive | brief | critique | debate
    --language pt-BR \            # Idioma BCP-47
    --length long \               # Duração: short | default (15-20min) | long (25-30min)
    --focus "PROMPT_TEXT" \        # Prompt customizado (max 2500 chars)
    --source-ids "UUID1,UUID2" \  # Focar em sources específicos
    --profile profissional \      # Perfil de autenticação
    --confirm                     # Pular confirmação interativa
```

---

## 3. Processo de Download

### 3.1 Fluxo Detalhado

```
1. Consultar Studio
   $ nlm studio status NOTEBOOK_ID --json --profile profissional

   Retorna lista de artifacts com status:
   ├── "completed"      → pronto para download
   ├── "in_progress"    → ainda processando (aguardar)
   ├── "failed"         → Google falhou ao processar
   └── "not_found"      → artifact expirado ou inexistente

2. Download do Áudio
   $ nlm download audio NOTEBOOK_ID \
       --id ARTIFACT_ID \
       -o /caminho/para/arquivo.m4a \
       --no-progress

3. Atualização de Metadados
   O script atualiza o JSON de índice:
   ├── status: "created" → "downloaded"
   ├── audio_file: nome do arquivo salvo
   ├── download_at: timestamp ISO
   └── tamanho_bytes: tamanho do arquivo em disco

4. Tratamento de Falhas
   ├── status "failed" no studio → marca "error" no índice
   ├── timeout no download (300s) → mantém status, retry manual
   └── arquivo já existe → pula (proteção contra duplicação)
```

### 3.2 Comandos de Download por Projeto

```bash
# DeVita — download de todos os pendentes
python3 projetos/devita_cme/scripts/download_audios.py

# DeVita — download de capítulos específicos
python3 projetos/devita_cme/scripts/download_audios.py --chapters 3,32,93

# DeVita — via orquestrador
python3 projetos/devita_cme/scripts/next_batch.py --download

# Cálculo Munem-Foulis
python3 projetos/calculo/calculo_runner.py --download
```

### 3.3 Formato de Saída

| Projeto | Prefixo | Formato | Padrão de Nome |
|---------|---------|---------|----------------|
| DeVita | `mk_devita_` | `.m4a` | `mk_devita_ch{NNN}_{slug}.m4a` |
| Cálculo | `mf_` | `.m4a` | `mf_cap{NN}_s{NN}_{slug}.m4a` |
| Genérico | `mk_` | `.mp3` | `mk_{slug}_{YYYYMMDD}.mp3` |

---

## 4. Interface de Linha de Comando (CLI)

### 4.1 DeVita CME — Geração de Áudios

```bash
# Criar áudios para capítulos específicos
python3 projetos/devita_cme/scripts/generate_devita_audio.py --chapters 13,26,37

# Dry-run (preview sem executar)
python3 projetos/devita_cme/scripts/generate_devita_audio.py --chapters 13,26,37 --dry-run

# Download de áudios prontos
python3 projetos/devita_cme/scripts/generate_devita_audio.py --download
```

| Flag | Descrição |
|------|-----------|
| `--chapters N,N,N` | Números dos capítulos (obrigatório na criação) |
| `--download` | Modo download: baixa áudios prontos no NLM |
| `--dry-run` | Preview: mostra o que seria feito sem executar |

### 4.2 DeVita CME — Download Dedicado

```bash
# Baixar todos os pendentes
python3 projetos/devita_cme/scripts/download_audios.py

# Baixar capítulos específicos
python3 projetos/devita_cme/scripts/download_audios.py --chapters 3,32

# Preview
python3 projetos/devita_cme/scripts/download_audios.py --dry-run
```

| Flag | Descrição |
|------|-----------|
| `--chapters N,N,N` | Capítulos específicos (opcional; sem = todos) |
| `--dry-run` | Preview sem executar |

### 4.3 DeVita CME — Orquestrador de Batch

```bash
# Status geral do projeto
python3 projetos/devita_cme/scripts/next_batch.py --status

# Preview do próximo batch (5 capítulos)
python3 projetos/devita_cme/scripts/next_batch.py

# Executar próximo batch
python3 projetos/devita_cme/scripts/next_batch.py --go

# Batch de 10 capítulos
python3 projetos/devita_cme/scripts/next_batch.py -n 10 --go

# Download via orquestrador
python3 projetos/devita_cme/scripts/next_batch.py --download
```

| Flag | Descrição |
|------|-----------|
| `-n N` / `--count N` | Tamanho do batch (default: 5) |
| `--go` | Executa a criação (default: dry-run) |
| `--download` | Baixa áudios prontos |
| `--status` | Mostra dashboard de progresso |

### 4.4 Cálculo Munem-Foulis

```bash
# Status geral com dashboard visual
python3 projetos/calculo/calculo_runner.py --status

# Criar até 5 áudios pendentes
python3 projetos/calculo/calculo_runner.py --max-sections 5

# Criar seções específicas
python3 projetos/calculo/calculo_runner.py --sections 6,7,8

# Preview
python3 projetos/calculo/calculo_runner.py --dry-run

# Download de áudios prontos
python3 projetos/calculo/calculo_runner.py --download
```

| Flag | Descrição |
|------|-----------|
| `--max-sections N` | Máximo de seções pendentes a processar (default: 50) |
| `--sections N,N,N` | IDs específicos de seções |
| `--download` | Modo download |
| `--dry-run` | Preview |
| `--status` | Dashboard visual por capítulo |

### 4.5 Gerador Genérico

```bash
# Áudio single para qualquer notebook
python3 tools/audio_generator.py \
    --notebook NOTEBOOK_ID \
    --topic "Tema do deep-dive" \
    --notebook-name "Nome do Notebook" \
    --profile profissional

# Batch via arquivo JSON de tópicos
python3 tools/audio_generator.py \
    --notebook NOTEBOOK_ID \
    --topics-file topicos.json \
    --notebook-name "Nome" \
    --profile profissional

# Modo teste (sem gerar áudio)
python3 tools/audio_generator.py \
    --notebook NOTEBOOK_ID \
    --topic "Tema" \
    --test
```

### 4.6 Helper Bash

```bash
# Geração rápida com defaults
./tools/generate_audio.sh NOTEBOOK_ID

# Com parâmetros customizados
./tools/generate_audio.sh NOTEBOOK_ID deep_dive pt-BR long profissional
```

### 4.7 Comandos nlm Diretos (Referência)

```bash
# Autenticação
nlm login --profile profissional                    # Re-autenticar
nlm login --check --profile profissional            # Verificar

# Criação
nlm create audio NOTEBOOK_ID --format deep_dive --language pt-BR --confirm

# Status
nlm studio status NOTEBOOK_ID --json --profile profissional

# Download
nlm download audio NOTEBOOK_ID --id ARTIFACT_ID -o arquivo.m4a

# Sources
nlm source list NOTEBOOK_ID --json --profile profissional

# Deletar artifact
nlm delete artifact NOTEBOOK_ID ARTIFACT_ID --confirm
```

---

## 5. Estatísticas de Execução

### 5.1 DeVita CME — Progresso

| Métrica | Valor | % |
|---------|-------|---|
| **Total de capítulos** | 108 | 100% |
| Baixados com sucesso | 98 | 91% |
| Gerados (não baixados) | 8 | 7% |
| Erros (ch3, ch32) | 2 | 2% |
| Pendentes | 0 | 0% |

| Detalhe | Valor |
|---------|-------|
| Arquivos de áudio | 108 `.m4a` |
| Tamanho total em disco | ~4.6 GB |
| Prompts customizados | 105 |
| Análises de gaps | 25 |
| Período de geração | 2026-03-04 a 2026-03-12 |

### 5.2 Cálculo Munem-Foulis — Progresso

| Métrica | Valor | % |
|---------|-------|---|
| **Total de seções** | 52 | 100% |
| Baixados com sucesso | 5 | 10% |
| Criados (não baixados) | 20 | 38% |
| Falhas | 15 | 29% |
| Pendentes | 12 | 23% |

| Detalhe | Valor |
|---------|-------|
| Capítulos cobertos | 13 (Cap. 0–12) |
| PDFs fonte | 13 |
| Imagens extraídas | 99+ |
| Período de geração | 2026-03-08 a 2026-03-10 |

### 5.3 Template de Métricas para Novos Projetos

```
| Métrica               | Valor | % |
|-----------------------|-------|---|
| Total de unidades     |       |   |
| Baixados com sucesso  |       |   |
| Gerados (não baixados)|       |   |
| Erros                 |       |   |
| Pendentes             |       |   |

| Detalhe                | Valor |
|------------------------|-------|
| Tamanho total em disco |       |
| Prompts customizados   |       |
| Período de geração     |       |
```

---

## 6. Organização de Diretórios

### 6.1 Estrutura Raiz

```
notebooklm_michalk/
├── CLAUDE.md                              # Instruções do projeto
├── AGENTS.md                              # Workflow para agentes de IA
├── README.md                              # Este arquivo
├── como_usar_skill.md                     # Guia de uso do skill de áudio
├── notebooklm-config.json                 # Configuração MCP
│
├── projetos/                              # ← TODOS os projetos de áudio
│   │
│   ├── devita_cme/                        # Projeto DeVita Cancer
│   │   ├── chapter_index.json             #   Índice mestre (108 capítulos)
│   │   ├── tracker.md                     #   Progresso em tabela markdown
│   │   ├── audio/                         #   Áudios baixados (~4.6 GB, 108 .m4a)
│   │   ├── prompts/
│   │   │   ├── master_template.md         #   Template base de prompt
│   │   │   ├── como_continuar.md          #   Quick start guide
│   │   │   └── chapters/                  #   105 prompts customizados
│   │   ├── gaps/                          #   Análises de lacunas (25 arquivos)
│   │   ├── logs/                          #   Logs de geração JSON
│   │   ├── docs/                          #   Plano mestre, prompts originais
│   │   └── scripts/
│   │       ├── generate_devita_audio.py   #   Fase 1: criação
│   │       ├── download_audios.py         #   Fase 2: download
│   │       ├── next_batch.py              #   Orquestrador de batch
│   │       └── update_tracker.py          #   Atualiza tracker.md
│   │
│   ├── calculo/                           # Projeto Cálculo Munem-Foulis
│   │   ├── section_index.json             #   Índice mestre (52 seções)
│   │   ├── calculo_runner.py              #   Runner unificado (Fases 1+2)
│   │   └── munem_vol1/
│   │       ├── audios/                    #   Áudios baixados (37 .m4a)
│   │       ├── capitulos/                 #   PDFs fonte (13 capítulos)
│   │       └── imagens/                   #   Imagens extraídas (557)
│   │
│   ├── w_shakespeare/                     # Projeto Shakespeare (19 obras)
│   │   ├── scripts/
│   │   │   ├── shakespeare_runner.py      #   Runner fire-and-forget
│   │   │   └── run_shakespeare_batch.sh   #   Wrapper para cron
│   │   └── {obra_name}/audios/            #   Áudios por obra
│   │
│   └── cirurgia_oncologica/               # Cirurgia Oncológica (stub)
│       └── prompt_retalho.md
│
├── docs/                                  # Documentação geral
│   ├── estrategia_geracao_audios.md       #   Estratégia global (detalhada)
│   └── notebooklm/
│       ├── notebooks_conta_michalk.md     #   43 notebooks mapeados
│       ├── audio_overview_guide.md        #   Guia de geração de áudio
│       ├── guia_uso_notebooklm.md         #   Guia de uso do MCP
│       ├── como_authenticar.md            #   Métodos de autenticação
│       └── limites_audio_overview.md      #   Limites do plano Pro
│
├── tools/                                 # Utilitários genéricos + testes
│   ├── audio_generator.py                 #   Gerador multi-propósito
│   ├── generate_audio.sh                  #   Helper Bash
│   ├── test_mcp_client.py                 #   Teste de conexão MCP
│   ├── test_audio_generation.py           #   Teste de geração de áudio
│   ├── list_all_mcp_tools.py              #   Listagem de ferramentas MCP
│   └── dashboard.html                     #   Dashboard de analytics
│
└── logs/                                  # Logs globais
```

### 6.2 Estrutura-Padrão por Projeto (Template)

Para criar um novo projeto de livro, crie uma pasta em `projetos/` com esta estrutura:

```
projetos/{nome_projeto}/
├── {chapter|section}_index.json     # Índice mestre com metadados
├── {nome}_runner.py                 # Script runner (ou em scripts/)
├── tracker.md                       # Progresso em markdown (opcional)
├── audio/                           # Áudios baixados (.m4a)
├── prompts/
│   ├── master_template.md           # Template base do prompt
│   └── chapters/                    # Um prompt por capítulo/seção
│       ├── ch001_*.txt
│       └── ...
├── gaps/                            # Análises de lacunas (opcional)
└── scripts/                         # Scripts especializados
    ├── generate_{nome}_audio.py     # Fase 1: criação
    ├── download_audios.py           # Fase 2: download
    └── next_batch.py                # Orquestrador
```

### 6.3 Estrutura do JSON de Índice

**DeVita (`chapter_index.json`)**:

```json
{
  "notebook_id": "25aa1a74-...",
  "chapters": [
    {
      "chapter_num": 1,
      "title": "Adolescents and Young Adults with Cancer",
      "source_id": "uuid-do-pdf-no-notebook",
      "source_type": "pdf",
      "status": "downloaded",
      "artifact_id": "uuid-do-artifact-no-studio",
      "audio_file": "mk_devita_ch001_adolescents_and_young_adults.m4a",
      "audio_generated_at": "2026-03-08T...",
      "download_at": "2026-03-08T...",
      "listened": false,
      "gaps_identified": false,
      "notes": ""
    }
  ]
}
```

**Cálculo (`section_index.json`)**:

```json
{
  "notebook_id": "0c022710-...",
  "total_sections": 52,
  "sections": [
    {
      "id": 1,
      "chapter": 0,
      "section": 1,
      "title": "Números Reais",
      "chapter_title": "Revisão",
      "source_id": "uuid-do-pdf",
      "slug": "cap00_s01_numeros_reais",
      "status": "downloaded",
      "artifact_id": "uuid-do-artifact",
      "created_at": "2026-03-08T...",
      "output_path": "munem_vol1/audios/mf_cap00_s01_numeros_reais.m4a"
    }
  ]
}
```

---

## 7. Limites do NotebookLM Pro

| Recurso | Limite | Observações |
|---------|--------|-------------|
| Gerações de áudio por dia | 50 | Hard limit da plataforma |
| Caracteres no `--focus` (prompt) | 2.500 | Prompts maiores são truncados |
| Sources por notebook | 250 | DeVita usa 108 |
| Palavras por source | 1.000.000 | Dobro do plano básico |
| Duração máxima do áudio | ~45 min | Formato `deep_dive` + `long` |
| Intervalo mínimo recomendado | 2 min | Evita rate-limiting |

---

## 8. Guia de Replicação para Novos Livros

### Passo a Passo

**1. Preparar o Notebook no NotebookLM**

- Acessar [notebooklm.google.com](https://notebooklm.google.com) com a conta `edson@michalkcare.com`
- Criar um notebook e fazer upload dos PDFs (um por capítulo/seção)
- Anotar o Notebook ID da URL: `https://notebooklm.google.com/notebook/{NOTEBOOK_ID}`

**2. Obter Source IDs**

```bash
nlm source list NOTEBOOK_ID --json --profile profissional
```

Salvar o mapeamento `source_id → capítulo` no JSON de índice.

**3. Criar Estrutura de Diretórios**

```bash
mkdir -p projetos/{nome_projeto}/{audio,prompts/chapters,scripts,gaps,logs,docs}
```

**4. Criar o JSON de Índice**

Utilizar como base o formato do DeVita (`chapter_index.json`) ou Cálculo (`section_index.json`). Cada entrada precisa no mínimo de:

- Identificador numérico
- Título
- `source_id` (do passo 2)
- `status: "pending"`

**5. Criar Prompts Customizados**

Criar um arquivo `.txt` ou `.md` por capítulo em `prompts/chapters/`:

```
prompts/chapters/ch001_titulo_do_capitulo.txt
prompts/chapters/ch002_outro_capitulo.txt
```

Cada prompt deve ter no máximo 2.500 caracteres e definir:

- Tom e formato da conversa
- Público-alvo
- Ênfases e omissões específicas
- Contexto do capítulo

**6. Adaptar o Script Runner**

Copiar `projetos/calculo/calculo_runner.py` ou `projetos/devita_cme/scripts/generate_devita_audio.py` e adaptar:

- `NOTEBOOK_ID`
- `PROFILE`
- Caminhos de arquivos (`INDEX_FILE`, `AUDIO_DIR`, `PROMPTS_DIR`)
- `PROMPT_TEMPLATE` (se usar template)
- `make_filename()` (padrão de nomenclatura)
- `load_prompt()` (carregamento de prompts)

**7. Testar**

```bash
# Dry-run
python3 projetos/{nome_projeto}/scripts/generate_audio.py --chapters 1 --dry-run

# Criar 1 áudio de teste
python3 projetos/{nome_projeto}/scripts/generate_audio.py --chapters 1

# Aguardar ~15 min, depois baixar
python3 projetos/{nome_projeto}/scripts/download_audios.py
```

**8. Escalar**

- Respeitar limite de 50 áudios/dia
- Usar intervalo mínimo de 2 minutos entre criações
- Verificar autenticação antes de batches longos: `nlm login --check --profile profissional`

### Configurações-Chave para Customizar

| Configuração | Onde Alterar | Impacto |
|--------------|--------------|---------|
| `NOTEBOOK_ID` | Constante no script | Define qual notebook usar |
| `PROFILE` | Constante no script | Autenticação Google |
| `INTERVAL_SECONDS` | Constante no script | Tempo entre criações (min: 120) |
| `--format` | Chamada `nlm create` | `deep_dive`, `brief`, `critique`, `debate` |
| `--length` | Chamada `nlm create` | `short`, `default`, `long` |
| `--language` | Chamada `nlm create` | Código BCP-47 (ex: `pt-BR`, `en`) |
| `--source-ids` | Chamada `nlm create` | Focar em sources específicos |

---

## 9. Resolução de Problemas

### Autenticação Expirada

```
✗ Authentication Error
  RPC Error 16: Authentication expired
→ Run nlm login to re-authenticate
```

**Solução:**

```bash
nlm login --profile profissional   # Abre browser para re-autenticar
nlm login --check --profile profissional   # Verificar
```

### Rate-Limit ou Rejeição do Google

**Causa:** Muitas criações em sequência rápida ou limite diário atingido.

```bash
# Aguardar 30-60 min e testar com comando mínimo
nlm create audio NOTEBOOK_ID --format deep_dive --language pt-BR --confirm --profile profissional
```

### Artifact Não Encontrado no Download

O Google pode ter expirado o artifact. Solução: alterar o status no JSON de índice para `"pending"` e re-gerar.

### `nlm` Não Encontrado

```bash
export PATH="$HOME/.local/bin:$PATH"
which nlm   # Deve retornar ~/.local/bin/nlm
```

### Áudio Gerado Mas Download Falha

```bash
# Verificar status no studio
nlm studio status NOTEBOOK_ID --json --profile profissional

# Tentar download manual
nlm download audio NOTEBOOK_ID --id ARTIFACT_ID -o arquivo.m4a --no-progress
```

---

## 10. Tempos de Referência

| Operação | Tempo |
|----------|-------|
| `nlm create audio` (request) | 5–15 segundos |
| Processamento no servidor Google | 8–15 minutos |
| Download de um áudio (~40 MB) | 15–60 segundos |
| Intervalo entre criações (fire-and-forget) | 2 minutos |
| 20 capítulos fire-and-forget | ~40 minutos |
| 50 capítulos fire-and-forget (limite diário) | ~1.7 horas |
| 20 capítulos com wait+download inline (v2 antiga) | ~6.5 horas |

---

## Notebooks Disponíveis (43 mapeados)

Referência completa: [`docs/notebooklm/notebooks_conta_michalk.md`](docs/notebooklm/notebooks_conta_michalk.md)

### Principais por Área

| Área | Notebook | ID | Sources |
|------|----------|----|---------|
| Oncologia | DeVita Cancer (por capítulo) | `25aa1a74-...` | 108 |
| Oncologia | Cirurgia Oncológica | `231e5405-...` | 59 |
| Oncologia | NCCN Guidelines | `edac906a-...` | 22 |
| Matemática | Cálculo Munem-Foulis Vol. 1 | `0c022710-...` | 52 |
| Ciências Básicas | Fisiologia | `d23c673d-...` | 112 |
| Ciências Básicas | Patologia | `813ca0d8-...` | 92 |
| Ciências Básicas | Farmacologia | `41afa80d-...` | 78 |
| Ciências Básicas | Bioquímica | `6bdd6956-...` | 55 |
| Tecnologia | n8n v2.0 | `c18d2cc4-...` | 81 |

---

## Quick Start

```bash
# 1. Verificar autenticação
nlm login --check --profile profissional

# 2. Ver status do DeVita
python3 projetos/devita_cme/scripts/next_batch.py --status

# 3. Ver status do Cálculo
python3 projetos/calculo/calculo_runner.py --status

# 4. Gerar próximo batch DeVita (preview)
python3 projetos/devita_cme/scripts/next_batch.py

# 5. Executar geração
python3 projetos/devita_cme/scripts/next_batch.py --go

# 6. Baixar áudios (~15 min depois)
python3 projetos/devita_cme/scripts/next_batch.py --download
```
