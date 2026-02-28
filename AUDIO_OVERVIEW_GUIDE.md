# 🎙️ Guia: Gerar Audio Overview com NotebookLM CLI

## ✅ Status da Atualização

**Pacote atualizado com sucesso!**
- ❌ Versão antiga: `notebooklm-mcp` v2.0.11 (sem suporte a áudio)
- ✅ Versão nova: `notebooklm-mcp-cli` v0.3.15 (com suporte completo a áudio)

---

## 🚀 Como Gerar Audio Overview

### Passo 1: Autenticar

Você precisa fazer login com sua conta Google **UMA VEZ**:

```bash
nlm login
```

Isso irá:
1. Abrir um navegador automaticamente
2. Solicitar login na sua conta Google
3. Salvar as credenciais no perfil `default`

**Para a conta profissional:**
```bash
nlm login --profile profissional
```

### Passo 2: Criar Audio Overview

Uma vez autenticado, você pode gerar o audio do notebook Docker:

```bash
nlm audio create 85d38ec1-7659-4307-aedf-3bc773a4d4ba \
  --format deep_dive \
  --length default \
  --confirm
```

#### Opções Disponíveis:

**Formatos (`--format`):**
- `deep_dive` (padrão) - Discussão aprofundada
- `brief` - Resumo breve
- `critique` - Análise crítica
- `debate` - Debate entre hosts

**Duração (`--length`):**
- `short` - Curto (5-10 min)
- `default` - Padrão (15-20 min)
- `long` - Longo (25-30 min)

**Idioma (`--language`):**
- `pt-BR` - Português Brasil
- `en` - Inglês
- `es` - Espanhol

**Foco (`--focus`):**
- Especifique um tópico específico para destacar

**Fontes (`--source-ids`):**
- IDs de fontes específicas (separados por vírgula)
- Se omitido, usa todas as fontes do notebook

### Passo 3: Baixar o Áudio

Após a criação (leva alguns minutos), baixe o arquivo:

```bash
nlm download 85d38ec1-7659-4307-aedf-3bc773a4d4ba
```

---

## 📋 Exemplos Práticos

### Exemplo 1: Audio Overview em Português do Notebook Docker
```bash
# Fazer login (uma vez)
nlm login

# Criar audio em português, formato deep dive
nlm audio create 85d38ec1-7659-4307-aedf-3bc773a4d4ba \
  --format deep_dive \
  --language pt-BR \
  --length default \
  --confirm

# Aguardar processamento e baixar
nlm download 85d38ec1-7659-4307-aedf-3bc773a4d4ba
```

### Exemplo 2: Audio Breve com Foco em Containers
```bash
nlm audio create 85d38ec1-7659-4307-aedf-3bc773a4d4ba \
  --format brief \
  --length short \
  --focus "Docker containers e orchestração" \
  --language pt-BR \
  --confirm
```

### Exemplo 3: Debate sobre Docker vs Alternativas
```bash
nlm audio create 85d38ec1-7659-4307-aedf-3bc773a4d4ba \
  --format debate \
  --length long \
  --language pt-BR \
  --confirm
```

---

## 🔧 Comandos Úteis

### Verificar Status da Autenticação
```bash
nlm login --check
```

### Listar Todos os Notebooks
```bash
nlm notebook list
```

### Ver Detalhes de um Notebook
```bash
nlm notebook get 85d38ec1-7659-4307-aedf-3bc773a4d4ba
```

### Gerenciar Perfis (Múltiplas Contas)
```bash
# Criar perfil para conta profissional
nlm login --profile profissional

# Listar perfis
nlm login profile list

# Mudar perfil padrão
nlm login switch profissional

# Usar perfil específico em comando
nlm audio create NOTEBOOK_ID --profile profissional
```

---

## 🎯 IDs dos Seus Notebooks Principais

Para referência rápida:

| Notebook | ID |
|----------|-----|
| Docker | `85d38ec1-7659-4307-aedf-3bc773a4d4ba` |
| Claude Code | `3d1e250c-47e7-42f6-9df7-86c2b6623f4a` |
| Beads BD Software | `cb7a2fcd-e7fd-49d0-bdae-f2b315600051` |
| Suma Teológica | `a9fcadbd-87f0-4802-ba5f-670932cd074f` |
| Shakespeare | `19bde485-a9c1-4809-8884-e872b2b67b44` |

Veja lista completa em: `notebooks_conta_pessoal.md`

---

## 📚 Documentação Adicional

Para ver todas as opções disponíveis:
```bash
nlm --ai  # Documentação completa para IA
nlm --help  # Ajuda geral
nlm audio --help  # Ajuda do comando audio
```

---

## ⚠️ Importante

1. **Autenticação é manual**: O CLI precisa que você faça login manualmente UMA VEZ
2. **Processamento leva tempo**: Audio overviews levam alguns minutos para serem gerados
3. **Perfis persistentes**: Após o login, as credenciais ficam salvas
4. **Múltiplas contas**: Use `--profile` para gerenciar conta pessoal e profissional

---

## 🎉 Pronto!

Agora você tem acesso completo às funcionalidades de Audio Overview do NotebookLM via linha de comando!
