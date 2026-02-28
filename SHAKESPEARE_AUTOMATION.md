# 🎭 Shakespeare Audio Generator - Sistema de Automação

Sistema completo para geração automatizada de 351 áudios educacionais de cenas de Shakespeare aplicando metodologia Olavo de Carvalho (COF).

## 📊 Status Atual

- **Total de cenas:** 351 (41 obras)
- **Processadas:** 2 (Hamlet)
- **Pendentes:** 349
- **Configuração:** 20 cenas/dia (distribuído entre todas as obras)
- **Previsão:** ~18 dias para conclusão

## 🚀 Instalação do Cron Job

### Instalação Automática (Recomendado)

```bash
cd /Users/edsonmichalkiewicz/dev/notebooklm_edson
./scripts/install_cron.sh
```

O instalador irá:
1. Testar o script em modo dry-run
2. Configurar cron job para executar diariamente às 06:00
3. Criar backup do crontab atual
4. Mostrar instruções de uso

### Instalação Manual

Se preferir instalar manualmente:

```bash
# Editar crontab
crontab -e

# Adicionar esta linha:
0 6 * * * cd /Users/edsonmichalkiewicz/dev/notebooklm_edson && /usr/bin/python3 scripts/daily_shakespeare_batch.py >> logs/cron_shakespeare.log 2>&1
```

## 📋 Scripts Disponíveis

### 1. Daily Batch Processor
**Arquivo:** `scripts/daily_shakespeare_batch.py`

Processa 20 cenas por dia de forma distribuída (round-robin).

```bash
# Executar batch do dia
python3 scripts/daily_shakespeare_batch.py

# Simular execução (não processa)
python3 scripts/daily_shakespeare_batch.py --dry-run
```

**Características:**
- Distribui 20 cenas entre todas as obras
- Previne execução duplicada no mesmo dia
- Salva progresso em `logs/shakespeare_progress.json`
- Logs detalhados de cada execução

### 2. Progress Dashboard
**Arquivo:** `scripts/show_progress.py`

Mostra progresso detalhado do processamento.

```bash
# Visualizar progresso geral
python3 scripts/show_progress.py

# Modo verbose (detalhes por obra)
python3 scripts/show_progress.py --verbose
```

**Informações mostradas:**
- Estatísticas gerais (total, processadas, pendentes)
- Barra de progresso visual
- Obras por status (completas, em progresso, não iniciadas)
- Top 5 obras mais processadas
- Espaço em disco utilizado
- Estimativa de conclusão

### 3. Single Work Processor
**Arquivo:** `scripts/shakespeare_audio_generator.py`

Processa cenas de uma obra específica.

```bash
# Processar todas as cenas do Hamlet
python3 scripts/shakespeare_audio_generator.py --obra hamlet

# Processar primeiras 5 cenas do Macbeth
python3 scripts/shakespeare_audio_generator.py --obra macbeth --scenes 5

# Modo teste (3 cenas)
python3 scripts/shakespeare_audio_generator.py --obra romeo_and_juliet --test
```

## 📁 Estrutura de Arquivos

```
w_shakespeare/
├── hamlet/
│   ├── 01_cenas_identificadas.md    # Cenas catalogadas
│   ├── prompts_cenas/                # Prompts individuais (COF)
│   └── audios/
│       ├── metadata.json             # Tracking de áudios
│       └── ws_hamlet_01_*.mp3        # Áudios gerados
├── macbeth/
│   └── ...
└── [demais obras...]

logs/
├── shakespeare_progress.json         # Progresso global
└── cron_shakespeare.log             # Logs do cron job
```

## 📊 Monitoramento

### Ver Logs em Tempo Real

```bash
# Logs do cron job
tail -f logs/cron_shakespeare.log

# Progresso global
cat logs/shakespeare_progress.json | jq

# Dashboard ao vivo
watch -n 60 python3 scripts/show_progress.py
```

### Verificar Cron Job Instalado

```bash
# Listar cron jobs
crontab -l

# Verificar próxima execução
crontab -l | grep shakespeare
```

## 🔧 Manutenção

### Remover Cron Job

```bash
# Editar crontab
crontab -e

# Deletar ou comentar a linha do shakespeare
# (salvar e fechar o editor)
```

### Resetar Progresso

```bash
# Apagar arquivo de progresso (começar do zero)
rm logs/shakespeare_progress.json

# Apagar áudios de uma obra
rm -rf w_shakespeare/hamlet/audios/*.mp3
rm w_shakespeare/hamlet/audios/metadata.json
```

### Forçar Execução Imediata

```bash
# Executar batch imediatamente (ignora verificação de data)
# Editar daily_shakespeare_batch.py e comentar a verificação de data
# OU simplesmente executar manualmente:
python3 scripts/daily_shakespeare_batch.py
```

## ⚙️ Configurações

### Alterar Quantidade Diária

Editar `scripts/daily_shakespeare_batch.py`:

```python
DAILY_LIMIT = 20  # Alterar para quantidade desejada
```

### Alterar Horário do Cron

Editar crontab:

```bash
# Formato: MIN HORA DIA MÊS DIASEMANA
0 6 * * *     # 06:00 todos os dias
0 18 * * *    # 18:00 todos os dias
0 */6 * * *   # A cada 6 horas
```

### Alterar Intervalo Entre Cenas

Editar `scripts/shakespeare_audio_generator.py`:

```python
INTERVAL_SECONDS = 600  # 10 minutos (alterar conforme necessário)
```

## 🎯 Fluxo de Processamento

1. **Cron dispara às 06:00**
2. **Script verifica:**
   - Se já rodou hoje (previne duplicação)
   - Quais obras têm cenas pendentes
3. **Distribui 20 cenas** (round-robin entre obras)
4. **Para cada obra:**
   - Carrega prompt da cena
   - Gera áudio via NotebookLM MCP
   - Aguarda processamento (polling inteligente)
   - Faz download do áudio
   - Deleta artifact do NotebookLM
   - Atualiza metadata
   - Aguarda 10 minutos antes da próxima
5. **Salva progresso global**
6. **Gera relatório de execução**

## 📈 Estimativas

### Tempo de Processamento
- **Por cena:** ~15 min (geração + processamento + download)
- **Por batch (20 cenas):** ~5-6 horas
- **Total (351 cenas):** ~18 dias

### Espaço em Disco
- **Por áudio:** ~40-45 MB
- **Total estimado:** ~15 GB

## 🆘 Troubleshooting

### Cron não está executando

```bash
# Verificar se cron service está ativo
launchctl list | grep cron

# Verificar permissões de Full Disk Access
# System Preferences → Security & Privacy → Full Disk Access → cron
```

### Áudios não estão sendo gerados

```bash
# Testar autenticação MCP
nlm whoami

# Verificar notebook
nlm studio status 62400b1d-e3bd-45d2-8428-d2d8d6b7128d

# Executar manualmente para ver erros
python3 scripts/daily_shakespeare_batch.py
```

### Progresso não está sendo salvo

```bash
# Verificar permissões do diretório logs
ls -la logs/

# Criar diretório se não existir
mkdir -p logs
```

## 📚 Metodologia COF

Todos os prompts aplicam a metodologia do Seminário de Filosofia (COF) de Olavo de Carvalho:

1. **Primazia da Intuição:** Mergulhar na dinâmica da cena
2. **Sinceridade Existencial:** Avaliar autenticidade dos personagens
3. **Memória Afetiva:** Conectar com experiências pessoais
4. **Literatura como Meio:** Expandir consciência através da experiência vicária

## 📝 Licença e Créditos

- **Metodologia:** Olavo de Carvalho (Seminário de Filosofia)
- **Textos:** William Shakespeare (domínio público)
- **Áudios:** NotebookLM (Google)
- **Automação:** Sistema proprietário Edson Michalkiewicz

---

**🎭 Shakespeare Audio Generator v1.0**
*Educação do Imaginário através da Literatura*


📊 Monitoramento Recomendado

  Amanhã após às 12:00:
  # Ver progresso do primeiro batch
  python3 scripts/show_progress.py

  # Ver logs de execução
  tail -100 logs/cron_shakespeare.log

  📖 Documentação Completa

  Consulte SHAKESPEARE_AUTOMATION.md para:
  - Instruções detalhadas de uso
  - Troubleshooting
  - Configurações avançadas
  - Manutenção do sistema