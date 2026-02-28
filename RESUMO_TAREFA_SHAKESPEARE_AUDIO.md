# 📋 RESUMO DA TAREFA: Automação de Áudios Shakespeare

## 🎯 Objetivo Geral
Criar sistema automatizado (cron job) para gerar áudios educacionais de cenas das obras de Shakespeare aplicando a metodologia de leitura formativa de Olavo de Carvalho.

---

## 📊 Escopo e Dimensões

### Volume de Dados
- **41 obras** de Shakespeare com cenas identificadas
- **~10 cenas por obra** em média
- **Total estimado: ~410 cenas** para processar
- **Meta inicial: 20 áudios/dia**
- **Tempo total estimado: ~21 dias** para processar todas as cenas

### Notebook Alvo
- **ID**: `19bde485-a9c1-4809-8884-e872b2b67b44`
- **Nome**: William Shakespeare: The Complete Plays
- **Fontes**: 45 documentos

---

## ⚙️ Especificações Técnicas

### 1. Frequência e Timing
- ✅ **Frequência**: 20 áudios por dia
- ✅ **Intervalo obrigatório**: 10 minutos entre cada geração
- ✅ **Horário sugerido**: Distribuído ao longo do dia (ex: das 6h às 23h)
- ✅ **Cálculo**: 20 áudios × 10 min = 200 min (~3h20min de processamento/dia)

### 2. Limites Técnicos (Conta Pro)
Baseado em `limites_audio_overview.md`:

| Limite | Valor | Status |
|--------|-------|--------|
| Prompt máximo | 2.500 caracteres | ✅ Respeitado |
| Duração áudio | Até 45 min | ✅ Modo padrão (~20min) |
| Fontes por notebook | 250 | ✅ 45 fontes (OK) |
| Capacidade por fonte | 1.000.000 palavras | ✅ (OK) |
| Gerações por dia | 50 | ✅ 20 < 50 (OK) |

### 3. Formato do Áudio
- **Formato**: `deep_dive`
- **Duração**: `default` (~15-20 minutos)
- **Idioma**: `pt-BR` (Português Brasileiro)
- **Perfil**: `default` (conta pessoal)

---

## 📂 Estrutura de Dados

### Arquivos de Entrada

#### 1. Template de Prompt
**Arquivo**: `leitura_formativa/02_analise_profunda_cena.md`

```
Act as a Senior Humanities Tutor. Create an instructional audio deep-dive
in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology...

Input Data:
Scene Number: {{INSERT_SCENE_NUMBER}}
Book: {{INSERT_BOOK_TITLE}}
Author: {{INSERT_AUTHOR_NAME}}
Context: {{INSERT_SELECTED_SCENE_OR_DESCRIPTION_HERE}}
```

**⚠️ Ajuste necessário**: Template atual tem ~1.200 caracteres. Sobram ~1.300 para o contexto da cena.

#### 2. Metodologia de Referência
**Arquivo**: `leitura_formativa/metodologia_olavo_carvalho.md`

**4 Pilares aplicados**:
1. Primazia da Intuição
2. Sinceridade Existencial
3. Memória Afetiva e Imaginativa
4. Literatura como Meio, não Fim

#### 3. Cenas para Processar
**Localização**: `w_shakespeare/{OBRA}/01_cenas_identificadas.md`

**Estrutura de cada cena**:
```markdown
### N. Título da Cena
- **Localização:** Ato X, Cena Y
- **Resumo:** [Descrição da cena]
- **Justificativa COF:** [Análise segundo metodologia]
```

**Exemplo (Hamlet)**:
- 9 cenas identificadas
- Cada cena com localização, resumo e justificativa COF
- Formato consistente em todas as 41 obras

---

## 🔄 Fluxo de Processamento

### Etapas do Sistema

```
1. LEITURA DO ARQUIVO
   ↓
   - Ler w_shakespeare/{obra}/01_cenas_identificadas.md
   - Extrair cenas numeradas (### N. Título)

2. PREPARAÇÃO DO PROMPT
   ↓
   - Carregar template 02_analise_profunda_cena.md
   - Substituir placeholders:
     * {{INSERT_SCENE_NUMBER}} → Número da cena
     * {{INSERT_BOOK_TITLE}} → Nome da obra
     * {{INSERT_AUTHOR_NAME}} → William Shakespeare
     * {{INSERT_SELECTED_SCENE_OR_DESCRIPTION_HERE}} → Resumo + Justificativa
   - Validar: prompt ≤ 2.500 caracteres

3. GERAÇÃO DO ÁUDIO
   ↓
   - Executar: nlm audio create [NOTEBOOK_ID] \
                --format deep_dive \
                --language pt-BR \
                --length default \
                --focus "[PROMPT_GERADO]" \
                --confirm

4. REGISTRO E LOG
   ↓
   - Salvar metadata: obra, cena, artifact_id, timestamp
   - Registrar em arquivo de progresso
   - Atualizar fila de processamento

5. INTERVALO OBRIGATÓRIO
   ↓
   - Aguardar 10 minutos antes da próxima cena
   - Monitorar status do áudio anterior
```

---

## 📁 Sistema de Controle

### Arquivos de Estado

#### 1. `audio_work_queue.json`
Lista de todas as cenas a processar:
```json
{
  "total_scenes": 410,
  "processed": 0,
  "remaining": 410,
  "queue": [
    {
      "id": "hamlet_scene_1",
      "work": "hamlet",
      "scene_number": 1,
      "title": "O Contraste entre o Teatro Social...",
      "status": "pending"
    }
  ]
}
```

#### 2. `audio_progress.json`
Histórico de processamento:
```json
{
  "last_run": "2026-02-27T06:00:00",
  "daily_count": 15,
  "total_generated": 120,
  "sessions": [
    {
      "date": "2026-02-27",
      "audios_generated": 20,
      "success": 19,
      "failed": 1
    }
  ]
}
```

#### 3. `audio_daily_log.json`
Log detalhado do dia:
```json
{
  "date": "2026-02-27",
  "entries": [
    {
      "timestamp": "2026-02-27T06:00:00",
      "work": "hamlet",
      "scene": 1,
      "artifact_id": "abc-123",
      "status": "success",
      "prompt_size": 2450
    }
  ]
}
```

---

## 🤖 Automação: Cron Job

### Configuração do Cron

```bash
# Executar 20x por dia, começando às 6h, a cada 72 minutos
# (72 min = tempo para 1 áudio + intervalo de 10min + margem)

# Exemplo de distribuição horária:
0 6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23 * * * cd /Users/edsonmichalkiewicz/dev/notebooklm_edson && python3 scripts/shakespeare_audio_generator.py
```

**Ou agendamento mais espaçado:**
```bash
# Processar 1 cena a cada hora (apenas como exemplo)
0 * * * * cd /Users/edsonmichalkiewicz/dev/notebooklm_edson && python3 scripts/shakespeare_audio_generator.py --scenes 1
```

### Script Principal
**Nome**: `scripts/shakespeare_audio_generator.py`

**Responsabilidades**:
1. ✅ Verificar autenticação
2. ✅ Consultar fila de trabalho
3. ✅ Validar limite diário (20 áudios/dia)
4. ✅ Processar próxima cena da fila
5. ✅ Construir prompt respeitando limite de 2.500 chars
6. ✅ Gerar áudio via nlm CLI
7. ✅ Aguardar 10 minutos
8. ✅ Atualizar logs e progresso
9. ✅ Enviar notificações de erro (se houver)

---

## 🛡️ Tratamento de Erros

### Cenários e Respostas

| Erro | Ação |
|------|------|
| Prompt > 2.500 chars | Truncar contexto, manter template |
| Falha na geração | Registrar, mover para fila de retry |
| Limite diário atingido | Parar execução, aguardar próximo dia |
| Autenticação expirada | Enviar notificação, pausar sistema |
| Timeout no áudio | Aguardar 30min, verificar status |

---

## 📈 Métricas e Monitoramento

### Dashboard Sugerido

```
SHAKESPEARE AUDIO GENERATOR - STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Progresso Geral: ████████░░░░░░░░░░░░ 120/410 (29%)

Hoje (27/02/2026):
  ✅ Áudios gerados: 15/20
  ⏱️  Próxima execução: 18:00

Últimas 24h:
  ✅ Sucesso: 19
  ❌ Falhas: 1
  ⏳ Tempo médio: 18 min/áudio

Estimativa de conclusão: 18 de março de 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## ✅ Checklist de Validação

Antes de iniciar a automação:

- [ ] Autenticação válida (`nlm login --check`)
- [ ] Template de prompt ≤ 2.500 caracteres
- [ ] Fila de trabalho criada com todas as 410 cenas
- [ ] Cron job configurado com intervalo correto
- [ ] Sistema de logs implementado
- [ ] Notificações de erro configuradas
- [ ] Backup dos arquivos de estado
- [ ] Teste manual com 1 cena bem-sucedido

---

## 🚀 Próximos Passos (Após Aprovação)

1. **Extrair todas as cenas** dos 41 arquivos `01_cenas_identificadas.md`
2. **Criar fila de trabalho** (`audio_work_queue.json`)
3. **Implementar script Python** (`shakespeare_audio_generator.py`)
4. **Testar com 3 cenas** manualmente
5. **Configurar cron job**
6. **Monitorar primeira execução**
7. **Ajustar conforme necessário**

---

## 📝 Observações Importantes

### ⚠️ Limites de Prompt
O template base tem ~1.200 caracteres. Para respeitar o limite de 2.500:
- **Espaço disponível para contexto**: ~1.300 caracteres
- **Estratégia**: Incluir Resumo + Justificativa COF completos se couber
- **Fallback**: Se ultrapassar, usar apenas Resumo ou truncar Justificativa

### 🎯 Qualidade vs Quantidade
- Priorizar **qualidade** dos prompts sobre velocidade
- Se necessário, **reduzir para 15 áudios/dia** para permitir prompts mais ricos
- Monitorar feedback dos primeiros áudios gerados

### 🔄 Escalabilidade
Esta estrutura pode ser replicada para outros notebooks:
- Platão
- Aristóteles
- Tomás de Aquino
- Outros autores literários

---

## 🎬 Exemplo Prático

### Entrada (Hamlet - Cena 1)
```markdown
### 1. O Contraste entre o Teatro Social e a Dor Interior
- **Localização:** Ato I, Cena 2.
- **Resumo:** Cláudio discursa diplomaticamente. A Rainha pede a Hamlet
  que pare de sofrer. Hamlet responde que sua dor não "parece", ela "é"...
- **Justificativa COF:** Recusa de Hamlet em participar da "falsidade
  biográfica" e do fingimento coletivo...
```

### Prompt Gerado (Exemplo)
```
Act as a Senior Humanities Tutor. Create an instructional audio deep-dive
in fluent Brazilian Portuguese (PT-BR).
Apply Olavo de Carvalho's "Seminário de Filosofia" (COF) methodology...

Input Data:
Scene Number: 1
Book: Hamlet, Prince of Denmark
Author: William Shakespeare

Context:
Localização: Ato I, Cena 2
Título: O Contraste entre o Teatro Social e a Dor Interior

Cláudio discursa diplomaticamente. A Rainha pede a Hamlet que pare de
sofrer. Hamlet responde que sua dor não "parece", ela "é"...

Justificativa COF: Recusa de Hamlet em participar da "falsidade biográfica"
e do fingimento coletivo...
```

### Comando Executado
```bash
nlm audio create 19bde485-a9c1-4809-8884-e872b2b67b44 \
  --format deep_dive \
  --language pt-BR \
  --length default \
  --focus "$(cat prompt_gerado.txt)" \
  --confirm
```

---

## ❓ Perguntas para Validação

Antes de implementar, confirme:

1. ✅ **Volume**: 20 áudios/dia está OK? Ou prefere começar com menos?
2. ✅ **Horário**: Prefere horário específico ou distribuído ao longo do dia?
3. ✅ **Prioridade**: Alguma obra para processar primeiro (ex: Hamlet, Macbeth)?
4. ✅ **Notificações**: Quer receber email/notificação diária do progresso?
5. ✅ **Armazenamento**: Onde salvar os áudios baixados? Ou apenas registrar IDs?

---

**Status**: ⏸️ Aguardando aprovação para iniciar implementação
