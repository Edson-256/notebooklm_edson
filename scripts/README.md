# 🤖 Scripts de Automação - NotebookLM Audio Overviews

Coleção de scripts para automatizar a geração de audio overviews dos seus notebooks NotebookLM.

## 📋 Scripts Disponíveis

### 1. `generate_audio.sh` - Gerador Simples
Script bash para gerar audio overview de um único notebook.

**Uso:**
```bash
./scripts/generate_audio.sh [NOTEBOOK_ID] [FORMAT] [LANGUAGE] [LENGTH] [PROFILE]
```

**Exemplos:**
```bash
# Usar valores padrão (Docker, deep_dive, pt-BR, default)
./scripts/generate_audio.sh

# Especificar notebook e formato
./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba brief pt-BR short

# Usar perfil profissional
./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba deep_dive pt-BR default profissional
```

**Parâmetros:**
- `NOTEBOOK_ID`: ID do notebook (padrão: Docker)
- `FORMAT`: deep_dive | brief | critique | debate (padrão: deep_dive)
- `LANGUAGE`: pt-BR | en | es (padrão: pt-BR)
- `LENGTH`: short | default | long (padrão: default)
- `PROFILE`: Nome do perfil de autenticação (padrão: default)

---

### 2. `batch_audio_generator.py` - Gerador em Lote
Script Python para gerar audio overviews de múltiplos notebooks de uma vez.

**Uso:**
```bash
python3 scripts/batch_audio_generator.py
```

**Configuração:**
Edite o arquivo para definir quais notebooks processar:

```python
NOTEBOOKS = [
    {
        "id": "85d38ec1-7659-4307-aedf-3bc773a4d4ba",
        "name": "Docker",
        "format": "deep_dive",
        "language": "pt-BR",
        "length": "default"
    },
    # Adicione mais notebooks aqui
]
```

**Recursos:**
- ✅ Processa múltiplos notebooks automaticamente
- ✅ Gera relatórios em JSON
- ✅ Logs com timestamp
- ✅ Tratamento de erros robusto
- ✅ Aguarda entre requisições para não sobrecarregar

**Logs:**
Os relatórios são salvos em `logs/audio_generation_YYYYMMDD_HHMMSS.json`

---

### 3. `setup_cron.sh` - Configurador de Agendamentos
Script interativo para configurar cron jobs e automatizar a geração de áudio.

**Uso:**
```bash
./scripts/setup_cron.sh
```

**Menu Interativo:**
1. Gerar audio toda segunda-feira às 8h
2. Gerar batch de notebooks todo domingo às 22h
3. Gerar audio diariamente às 6h
4. Configuração personalizada
5. Ver cron jobs atuais
6. Remover cron jobs

**Exemplos de Agendamentos:**

| Quando | Cron Expression | Descrição |
|--------|----------------|-----------|
| Toda segunda às 8h | `0 8 * * 1` | Semanal |
| Todo domingo às 22h | `0 22 * * 0` | Semanal |
| Diariamente às 6h | `0 6 * * *` | Diário |
| A cada 3 dias às 14h | `0 14 */3 * *` | Periódico |
| Primeira segunda do mês às 10h | `0 10 1-7 * 1` | Mensal |

---

## 🚀 Setup Inicial

### Passo 1: Tornar Scripts Executáveis
```bash
chmod +x scripts/*.sh
```

### Passo 2: Autenticar (Uma Vez)
```bash
# Conta pessoal
nlm login

# Conta profissional
nlm login --profile profissional
```

### Passo 3: Testar
```bash
# Testar geração simples
./scripts/generate_audio.sh

# Testar geração em lote
python3 scripts/batch_audio_generator.py
```

---

## 📚 Casos de Uso

### Caso 1: Audio Semanal Automático
Gerar audio overview do notebook de estudos toda segunda-feira:

```bash
./scripts/setup_cron.sh
# Escolher opção 1 e fornecer o ID do notebook
```

### Caso 2: Atualização Mensal de Todos os Notebooks
Processar todos os notebooks no último domingo de cada mês:

```bash
# Adicionar ao crontab manualmente:
0 22 22-28 * 0 cd /Users/edsonmichalkiewicz/dev/notebooklm_edson && python3 scripts/batch_audio_generator.py
```

### Caso 3: Geração Sob Demanda via Claude
Claude pode executar os scripts diretamente:

```bash
# Claude executa:
./scripts/generate_audio.sh 3d1e250c-47e7-42f6-9df7-86c2b6623f4a brief en short
```

---

## 🔧 Troubleshooting

### Erro: "Profile not found"
```bash
# Solução: Fazer login
nlm login --profile default
```

### Erro: "Permission denied"
```bash
# Solução: Tornar executável
chmod +x scripts/generate_audio.sh
```

### Cron não está executando
```bash
# Verificar logs do cron (macOS)
log show --predicate 'process == "cron"' --last 1h

# Verificar logs do cron (Linux)
grep CRON /var/log/syslog
```

### Script não encontra nlm
```bash
# Adicionar PATH completo no crontab
which nlm  # Ver o caminho completo

# Exemplo de cron com PATH completo:
0 8 * * 1 /Users/seu_usuario/.local/bin/nlm audio create NOTEBOOK_ID --confirm
```

---

## 📊 Estrutura de Logs

Os logs são salvos em `logs/` com a seguinte estrutura:

```json
{
  "timestamp": "2026-02-27T12:00:00",
  "profile": "default",
  "total": 3,
  "success": 2,
  "failed": 1,
  "results": [
    {
      "notebook_id": "85d38ec1-7659-4307-aedf-3bc773a4d4ba",
      "notebook_name": "Docker",
      "success": true,
      "timestamp": "2026-02-27T12:05:00"
    }
  ]
}
```

---

## 💡 Dicas

1. **Teste antes de agendar**: Execute os scripts manualmente primeiro
2. **Use perfis diferentes**: Separe conta pessoal e profissional
3. **Monitore os logs**: Verifique periodicamente se está funcionando
4. **Ajuste timeouts**: Notebooks grandes podem demorar mais
5. **Espaçamento entre jobs**: Aguarde pelo menos 30 segundos entre notebooks

---

## 🔒 Segurança

- ✅ Credenciais armazenadas localmente pelo nlm CLI
- ✅ Não expõe senhas ou tokens
- ✅ Usa autenticação OAuth do Google
- ⚠️ Mantenha os scripts em diretório seguro
- ⚠️ Não commite credenciais no Git

---

## 📝 Customização

### Adicionar Novo Notebook ao Batch
Edite `batch_audio_generator.py`:

```python
NOTEBOOKS.append({
    "id": "SEU_NOTEBOOK_ID",
    "name": "Nome do Notebook",
    "format": "deep_dive",
    "language": "pt-BR",
    "length": "default"
})
```

### Criar Script Personalizado
Use como template:

```bash
#!/bin/bash
nlm audio create YOUR_NOTEBOOK_ID \
    --format deep_dive \
    --language pt-BR \
    --length default \
    --confirm
```

---

## 🎯 Notebooks Prontos para Automação

IDs dos seus principais notebooks:

| Notebook | ID |
|----------|-----|
| Docker | `85d38ec1-7659-4307-aedf-3bc773a4d4ba` |
| Claude Code | `3d1e250c-47e7-42f6-9df7-86c2b6623f4a` |
| Beads BD Software | `cb7a2fcd-e7fd-49d0-bdae-f2b315600051` |
| Suma Teológica | `a9fcadbd-87f0-4802-ba5f-670932cd074f` |
| Shakespeare | `19bde485-a9c1-4809-8884-e872b2b67b44` |
| n8n | `1b562c95-0d1d-4d47-9561-dd268bc9fbe6` |

---

**Boa automação! 🚀**
