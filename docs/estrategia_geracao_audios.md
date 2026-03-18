# Estrategia de Geracao de Audios via NotebookLM

Documento tecnico destinado a outra instancia de IA que precise replicar, manter ou expandir este sistema de geracao de audios educacionais via Google NotebookLM.

---

## 1. Visao Geral

Este sistema gera **audio overviews** (podcasts educacionais) a partir de notebooks do Google NotebookLM. Dois projetos independentes rodam em paralelo, cada um com sua propria conta Google e estrategia de conteudo:

| Aspecto | Projeto Pessoal (Shakespeare) | Projeto Profissional (DeVita) |
|---------|-------------------------------|-------------------------------|
| Diretorio | `~/dev/notebooklm_edson/` | `~/dev/notebooklm_michalk/` |
| Conta Google | `edson.michalkiewicz@gmail.com` | `edson@michalkcare.com` |
| Profile nlm | `default` | `profissional` |
| Notebook ID | `62400b1d-e3bd-45d2-8428-d2d8d6b7128d` | `25aa1a74-f3e3-43d6-85db-32d2f5c21495` |
| Conteudo | 41 pecas de Shakespeare (332 cenas) | 108 capitulos do DeVita Cancer 12a ed |
| Sources no notebook | 45 PDFs | 108 PDFs |
| Metodologia | Olavo de Carvalho (COF) | Educacao medica continuada |
| Plano Google | Pro (50 audios/dia) | Pro (50 audios/dia) |

---

## 2. Ferramenta: NLM CLI

A comunicacao com o NotebookLM e feita exclusivamente via **nlm CLI** (NotebookLM CLI), uma ferramenta de linha de comando.

### Instalacao

```bash
# Instalado via uv (Python package manager)
# Binario em: ~/.local/bin/nlm
# Versao atual: 0.4.0
nlm --version
```

### Autenticacao

Cada conta Google e um **profile** separado. A autenticacao usa sessao de browser Chromium controlada pelo CLI:

```bash
# Verificar se autenticacao esta valida
nlm login --check --profile default          # Conta pessoal
nlm login --check --profile profissional     # Conta profissional

# Re-autenticar (abre browser Chromium)
nlm login --profile default
nlm login --profile profissional

# Autenticacao manual via cookies (alternativa)
nlm login --manual --file cookies.json --profile default
```

**Arquivos de auth:** `~/.notebooklm-mcp/auth.json` (default), `~/.notebooklm-mcp/auth_michalk.json` (profissional)

**IMPORTANTE:** A autenticacao expira periodicamente. Antes de qualquer operacao em batch, sempre verificar com `nlm login --check`.

### Comandos Principais para Audio

```bash
# Criar audio (fire-and-forget — retorna artifact_id imediatamente)
nlm create audio NOTEBOOK_ID \
    --format deep_dive \
    --language pt-BR \
    --length long \
    --focus "PROMPT_TEXT" \
    --source-ids "SOURCE_UUID_1,SOURCE_UUID_2" \
    --profile PROFILE_NAME \
    --confirm

# Verificar status dos artifacts no Studio
nlm studio status NOTEBOOK_ID --json --profile PROFILE_NAME

# Baixar audio pronto
nlm download audio NOTEBOOK_ID \
    --id ARTIFACT_ID \
    --output /path/to/file.mp3 \
    --no-progress

# Deletar artifact do Studio
nlm delete artifact NOTEBOOK_ID ARTIFACT_ID --confirm

# Listar sources de um notebook
nlm source list NOTEBOOK_ID --json --profile PROFILE_NAME
```

### Parametros do `nlm create audio`

| Parametro | Valores | Descricao |
|-----------|---------|-----------|
| `--format` | `deep_dive`, `brief`, `critique`, `debate` | Formato do audio |
| `--length` | `short`, `default` (15-20min), `long` (25-30min) | Duracao alvo |
| `--language` | Codigo BCP-47 (ex: `pt-BR`, `en`) | Idioma |
| `--focus` | Texto livre (max 2500 chars no Pro) | Prompt de customizacao |
| `--source-ids` | UUIDs separados por virgula | Focar em sources especificos |
| `--profile` | Nome do profile | Conta a usar |
| `--confirm` | Flag | Pular confirmacao interativa |

---

## 3. Limites do NotebookLM Pro

| Recurso | Limite |
|---------|--------|
| Geracoes de audio por dia | 50 |
| Caracteres no --focus | 2.500 |
| Sources por notebook | 250 |
| Palavras por source | 1.000.000 |
| Duracao maxima do audio | ~45 minutos |

**Rate limiting:** O Google pode rejeitar criacoes se muitas forem disparadas em sequencia rapida. Intervalo minimo recomendado: **2 minutos** entre criacoes.

---

## 4. Arquitetura Fire-and-Forget (v3)

O script principal (`shakespeare_runner.py` v3) usa uma estrategia de **fire-and-forget**:

1. **Fase 1 — Criacao:** Dispara `nlm create audio`, salva o `artifact_id` no metadata, segue para a proxima cena. Intervalo de 2 minutos entre cenas.
2. **Fase 2 — Download:** Executado separadamente (via `--download`). Verifica quais artifacts ja estao prontos no servidor e baixa os que estiverem com status `completed`.

Essa separacao existe porque o Google leva **8-15 minutos** para processar cada audio. Esperar inline desperdicava tempo. Com fire-and-forget, 20 cenas levam ~40 min (vs ~6.5h na v2).

### Fluxo de Estados

```
[nao existe] → process_scene() → [created] → --download → [downloaded]
                                            → --download → [server_failed] (se Google falhou)
                                            → --download → [still processing] (tentar depois)
```

### Diagrama do Fluxo

```
┌──────────────────────────────────────────────────────────────┐
│  FASE 1: python3 shakespeare_runner.py --max-scenes 20       │
│                                                              │
│  Para cada cena (round-robin entre obras):                   │
│    1. Carrega prompt customizado de prompts_cenas/NN_*.md    │
│    2. Resolve source_id da obra via SOURCE_ID_MAP            │
│    3. nlm create audio (--source-ids obra,cof_metodologia)   │
│    4. Salva artifact_id em audios/metadata.json              │
│    5. Aguarda 2 minutos                                      │
│    6. Proxima cena                                           │
└──────────────────────────────────────────────────────────────┘
                          │
                    (esperar ~15 min)
                          │
┌──────────────────────────────────────────────────────────────┐
│  FASE 2: python3 shakespeare_runner.py --download            │
│                                                              │
│  Para cada artifact com status='created':                    │
│    1. nlm studio status → verifica se completed              │
│    2. Se completed → nlm download audio → status=downloaded  │
│    3. Se failed → marca server_failed                        │
│    4. Se in_progress → pula (tentar depois)                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 5. Projeto Shakespeare (Pessoal) — Detalhes

### Estrutura de Cada Obra

```
projetos/w_shakespeare/hamlet/
├── 01_cenas_identificadas.md     # Lista de cenas (fonte primaria)
├── prompts_cenas/                # Um prompt .md por cena
│   ├── 01_o_contraste_entre_o_teatro_social_e_a_dor_interior.md
│   ├── 02_a_irrupcao_do_sobrenatural.md
│   └── ...
├── audios/
│   ├── metadata.json             # Rastreamento de todas as cenas
│   ├── ws_hamlet_01_contraste_teatro.mp3
│   └── ...
└── logs/
```

### Formato do `01_cenas_identificadas.md`

Regex de parsing (em `extract_scenes()`):

```
### {NUMERO}. {TITULO}
- **Localizacao:** {ATO_CENA}
- **Resumo:** {RESUMO}
- **Justificativa (Integracao COF):** {JUSTIFICATIVA}
```

### Prompts Customizados

Cada cena tem um prompt de ~1500-2200 chars baseado na metodologia COF (Seminario de Filosofia de Olavo de Carvalho). Estrutura:

```
Act as a Senior Humanities Tutor. Create an instructional audio deep-dive in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology to this specific scene.
Focus on "Education of the Imaginary" and breaking the "Individual Capsule" via vicarious experience.

Structure the audio to cover:
1. Context & Preliminary Attitude (suspending external judgments).
2. The 4 Pillars: Primacy of Intuition, Existential Sincerity, Affective Memory, Literature as a Means.
3. Vicarious Experience: Instruct the listener on how to inhabit the main character's skin.

Input Data:
Scene Number: {N}
Book: {TITULO_INGLES}
Author: William Shakespeare
Topic: {TITULO_CENA_PT}

Context:
Localização: {ATO_CENA}
{RESUMO_EXPANDIDO}

Justification (COF Integration):
{JUSTIFICATIVA_COF}

Analysis Instructions:
{INSTRUCOES_ANALISE}
```

**Todos os 332 prompts ja existem** em `prompts_cenas/` de cada obra.

### Source Targeting

O notebook Shakespeare tem 45 sources (um PDF por peca + textos de metodologia). O script mapeia cada obra ao seu source_id para que o NotebookLM foque apenas no texto relevante:

```python
SOURCE_ID_MAP = {
    'hamlet': '523f75db-6ff4-4591-84d1-a968d6d5f700',
    'macbeth': '20570f58-69c0-4193-ab9b-41321efc808a',
    # ... 41 obras mapeadas
}
METODOLOGIA_SOURCE_ID = '52edb813-6935-4123-bf35-4137283eb8dc'
```

Cada criacao envia `--source-ids {obra_source},{metodologia_source}` para o NLM focar no texto da peca + a referencia metodologica do COF.

### Nomenclatura de Arquivos

**Padrao:** `ws_{obra_slug}_{cena_num:02d}_{keyword}.mp3`

- `ws_` = prefixo William Shakespeare
- `{obra_slug}` = nome abreviado (ex: `hamlet`, `midsummer_dream`, `henry4_p1`)
- `{cena_num}` = numero da cena com zero-padding
- `{keyword}` = 1-2 palavras-chave do titulo (max 30 chars)

Exemplos:
- `ws_hamlet_01_contraste_teatro.mp3`
- `ws_midsummer_dream_04_humilhacao_helena.mp3`
- `ws_henry4_p1_02_honra_falstaff.mp3`

### Distribuicao Round-Robin

O script processa 1 cena de cada obra antes de repetir, garantindo cobertura uniforme. Com 41 obras, um batch de 41 cenas cobre todas as obras uma vez.

### Metadata (`audios/metadata.json`)

```json
{
  "obra": "Hamlet",
  "obra_slug": "hamlet",
  "obra_dir": "hamlet",
  "notebook_id": "62400b1d-e3bd-45d2-8428-d2d8d6b7128d",
  "total_cenas": 3,
  "ultima_atualizacao": "2026-03-07T10:14:10.123456",
  "audios": [
    {
      "arquivo": "ws_hamlet_01_contraste_teatro.mp3",
      "cena_numero": 1,
      "titulo_completo": "O Contraste entre o Teatro Social e a Dor Interior",
      "localizacao": "Ato I, Cena 2.",
      "artifact_id": "ffb38774-7ebc-4735-80bf-7d5a1b314831",
      "data_geracao": "2026-03-01T02:58:26.873058",
      "focus_topic": "Act as a Senior Humanities Tutor...",
      "prompt_type": "custom",
      "source_id": "523f75db-6ff4-4591-84d1-a968d6d5f700",
      "status": "downloaded",
      "output_path": "/path/to/ws_hamlet_01_contraste_teatro.mp3",
      "tamanho_bytes": 46212097
    }
  ]
}
```

**Status possiveis:** `created` (disparado, aguardando), `downloaded` (baixado com sucesso), `server_failed` (Google falhou ao processar), `failed` (erro no script)

---

## 6. Projeto DeVita (Profissional) — Detalhes

### Estrutura

```
notebooklm_michalk/devita_cme/
├── chapter_index.json        # Indice mestre (108 capitulos)
├── prompts/
│   ├── master_template.md    # Template base
│   └── chapters/             # 61 prompts customizados
│       └── ch{NNN}_{topic}.txt
├── audio/                    # Audios baixados (~54 arquivos, ~2.3 GB)
├── gaps/                     # Analise de lacunas por capitulo
└── scripts/
    └── generate_devita_audio.py
```

### Script DeVita (`generate_devita_audio.py`)

Tambem fire-and-forget. Diferenca principal: **nao faz polling nem download** — apenas dispara a criacao.

```bash
# Uso
python3 devita_cme/scripts/generate_devita_audio.py --chapters 13,26,37 --dry-run
python3 devita_cme/scripts/generate_devita_audio.py --chapters 13,26,37
```

Parametros de audio:
- `--format deep_dive`
- `--language pt-BR`
- `--length long`
- `--source-ids {chapter_source_id}` (1 source, o PDF do capitulo)
- `--profile profissional`
- `INTERVAL_SECONDS = 120` (2 min)

### Nomenclatura

**Padrao:** `mk_devita_ch{NUM}_{topic}.m4a`
- `mk_` = prefixo Michalk
- Formato `.m4a` (nao `.mp3`)

---

## 7. Como Executar

### Pre-requisitos

1. Python 3.14+ (`/opt/homebrew/bin/python3`)
2. nlm CLI v0.4.0+ (`~/.local/bin/nlm`)
3. Autenticacao valida nos profiles `default` e/ou `profissional`

### Shakespeare — Criar Audios

```bash
cd ~/dev/notebooklm_edson

# 1. Verificar auth
nlm login --check --profile default

# 2. Dry-run (ver o que sera processado)
python3 scripts/shakespeare_runner.py --dry-run

# 3. Rodar (fire-and-forget, 20 cenas)
python3 scripts/shakespeare_runner.py --max-scenes 20

# 4. Apenas uma obra
python3 scripts/shakespeare_runner.py --obra hamlet

# 5. Ctrl+C para parar com seguranca (espera cena atual terminar)
```

### Shakespeare — Baixar Audios Prontos

```bash
# Baixar todos os artifacts com status='created' que ja estejam prontos
python3 scripts/shakespeare_runner.py --download
```

### DeVita — Criar Audios

```bash
cd ~/dev/notebooklm_michalk

# Dry-run
python3 devita_cme/scripts/generate_devita_audio.py --chapters 28,19,45 --dry-run

# Executar
python3 devita_cme/scripts/generate_devita_audio.py --chapters 28,19,45
```

---

## 8. Resolucao de Problemas

### "NotebookLM rejected audio creation"

**Causa:** Rate-limit do Google ou problema temporario do servico.
**Solucao:**
1. Aguardar 30-60 minutos
2. Re-autenticar: `nlm login --profile default`
3. Testar com comando manual minimo:
   ```bash
   nlm create audio NOTEBOOK_ID --format deep_dive --language pt-BR --confirm --profile default
   ```

### Auth expirada

```bash
nlm login --check --profile default
# Se falhar:
nlm login --profile default  # Abre browser para re-autenticar
```

### Artifact nao encontrado no download

O Google pode ter expirado o artifact (limite de retencao no Studio). Nesse caso, recriar o audio (mudar status de `created` para `failed` no metadata.json e re-rodar o script).

### nlm nao encontrado no PATH

```bash
export PATH="$HOME/.local/bin:$PATH"
which nlm  # Deve retornar ~/.local/bin/nlm
```

---

## 9. Tempos de Referencia

| Operacao | Tempo |
|----------|-------|
| `nlm create audio` (request) | 5-15 segundos |
| Processamento no servidor Google | 8-15 minutos |
| Download de um audio (~40 MB) | 15-60 segundos |
| Intervalo entre criacoes (fire-and-forget) | 2 minutos |
| 20 cenas fire-and-forget | ~40 minutos |
| 20 cenas com wait+download (v2 antiga) | ~6.5 horas |
| 50 cenas fire-and-forget (limite diario) | ~1.7 horas |

---

## 10. Expansao para Novos Notebooks

Para replicar esta estrategia em outro notebook:

1. **Obter notebook_id:** Na URL do NotebookLM apos `/notebook/`
2. **Listar sources:** `nlm source list NOTEBOOK_ID --json --profile PROFILE`
3. **Criar mapeamento source_id:** Associar cada source ao conteudo correspondente
4. **Criar prompts:** Um arquivo `.md` ou `.txt` por topico (max 2500 chars)
5. **Configurar script:**
   - Copiar `shakespeare_runner.py` como base
   - Adaptar `SOURCE_ID_MAP`, `NOTEBOOK_ID`, `PROFILE`
   - Adaptar `extract_scenes()` para o formato do seu indice
   - Adaptar `load_scene_prompt()` para o caminho dos seus prompts
6. **Testar:** `--dry-run` primeiro, depois `--max-scenes 1`
7. **Escalar:** Respeitar limite de 50 audios/dia e intervalo minimo de 2 min

---

## 11. Arquivos-Chave

| Arquivo | Descricao |
|---------|-----------|
| `scripts/shakespeare_runner.py` | Script principal v3 (fire-and-forget + download) |
| `projetos/w_shakespeare/{obra}/01_cenas_identificadas.md` | Lista de cenas de cada obra |
| `projetos/w_shakespeare/{obra}/prompts_cenas/{NN}_{titulo}.md` | Prompt customizado por cena |
| `projetos/w_shakespeare/{obra}/audios/metadata.json` | Estado de cada cena (created/downloaded) |
| `logs/session_*.json` | Log detalhado de cada sessao de geracao |
| `docs/notebooklm/notebooks_conta_pessoal.md` | IDs dos 36 notebooks pessoais |
| `docs/notebooklm/como_authenticar.md` | Guia de autenticacao |
| `leitura_formativa/metodologia_olavo_carvalho.md` | Metodologia COF completa |
