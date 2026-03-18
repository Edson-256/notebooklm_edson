# 📝 Estratégia de Nomenclatura - Áudios Shakespeare

## 🎯 Desafio
- ~400 áudios de cenas do Shakespeare
- Necessidade de identificação rápida da fonte
- Organização para estudo dirigido
- Compatibilidade com sistemas de arquivo

---

## 📋 Padrão Base (padrao_nomes_arquivos.md)

```
[AUTOR]_[OBRA]_[CENA]_[NÚMERO]
```

**Exemplo genérico**: `JGR_SertaoVeredas_Duelo_05`

---

## 🎭 Adaptação para Shakespeare

### **Formato Proposto (Opção 1 - Recomendada)**

```
WS_[OBRA_SLUG]_[NUM]_[PALAVRA_CHAVE]
```

#### Componentes:

1. **`WS`** - Iniciais do autor (William Shakespeare)
2. **`[OBRA_SLUG]`** - Abreviação da obra em CamelCase
3. **`[NUM]`** - Número da cena (zero-padded: 01, 02, ..., 99)
4. **`[PALAVRA_CHAVE]`** - 1-3 palavras-chave em CamelCase

#### Exemplos Práticos:

| Obra | Cena | Título Original | Nome do Arquivo |
|------|------|-----------------|-----------------|
| Hamlet | 1 | O Contraste entre o Teatro Social e a Dor Interior | `WS_Hamlet_01_TeatroSocial.mp3` |
| Hamlet | 2 | A Irrupção do Sobrenatural e o Chamado à Vocação | `WS_Hamlet_02_Fantasma.mp3` |
| Hamlet | 4 | A Tensão Escatológica e a Consciência da Morte | `WS_Hamlet_04_SerOuNaoSer.mp3` |
| Macbeth | 1 | A Inversão dos Valores no Imaginário | `WS_Macbeth_01_Bruxas.mp3` |
| Macbeth | 2 | A Inoculação da Ambição | `WS_Macbeth_02_Ambicao.mp3` |
| Romeo and Juliet | 1 | - | `WS_RomeoJuliet_01_Briga.mp3` |

---

### **Formato Alternativo (Opção 2 - Mais Descritivo)**

```
shakespeare_[obra_slug]_cena[num]_[palavra_chave]
```

#### Exemplos:

| Original | Nome do Arquivo |
|----------|-----------------|
| Hamlet, Cena 1 | `shakespeare_hamlet_cena01_teatro_social.mp3` |
| Hamlet, Cena 2 | `shakespeare_hamlet_cena02_fantasma.mp3` |
| Macbeth, Cena 1 | `shakespeare_macbeth_cena01_bruxas.mp3` |

**Vantagens:**
- ✅ Mais legível em lowercase
- ✅ Separação clara com underscores
- ✅ Fácil de filtrar por `grep`/`find`

**Desvantagens:**
- ❌ Nomes mais longos
- ❌ Menos compacto visualmente

---

### **Formato Alternativo (Opção 3 - Máximo Descritivo)**

```
WS_[OBRA_COMPLETA]_C[NUM]_[TITULO_COMPLETO_TRUNCADO]
```

#### Exemplos:

| Original | Nome do Arquivo |
|----------|-----------------|
| Hamlet, Cena 1 | `WS_Hamlet_C01_ContrasteTeatroSocialDorInterior.mp3` |
| Macbeth, Cena 1 | `WS_Macbeth_C01_InversaoValoresImaginario.mp3` |

**Vantagens:**
- ✅ Máxima informação no nome
- ✅ Auto-descritivo

**Desvantagens:**
- ❌ Nomes muito longos (podem ultrapassar limites)
- ❌ Difícil de ler visualmente

---

## 🎯 **RECOMENDAÇÃO FINAL**

### **Opção 1 (Equilibrada)**

```
WS_[OBRA_SLUG]_[NUM]_[PALAVRA_CHAVE].mp3
```

**Justificativa:**
- ✅ Compacto mas informativo
- ✅ Segue padrão estabelecido em `padrao_nomes_arquivos.md`
- ✅ Fácil de ordenar alfabeticamente
- ✅ Palavra-chave facilita busca mental
- ✅ Número permite ordenação cronológica/sequencial

---

## 📚 Mapeamento de Obras → Slugs

### Tragédias
| Obra Completa | Slug Sugerido |
|---------------|---------------|
| Hamlet, Prince of Denmark | `Hamlet` |
| Macbeth | `Macbeth` |
| Othello | `Othello` |
| King Lear | `KingLear` |
| Romeo and Juliet | `RomeoJuliet` |
| Julius Caesar | `JuliusCaesar` |
| Antony and Cleopatra | `AntonyCleopatra` |
| Coriolanus | `Coriolanus` |
| Titus Andronicus | `TitusAndronicus` |
| Timon of Athens | `TimonAthens` |

### Comédias
| Obra Completa | Slug Sugerido |
|---------------|---------------|
| A Midsummer Night's Dream | `MidsummerDream` |
| The Tempest | `Tempest` |
| Much Ado About Nothing | `MuchAdo` |
| As You Like It | `AsYouLikeIt` |
| Twelfth Night | `TwelfthNight` |
| The Merchant of Venice | `MerchantVenice` |
| The Taming of the Shrew | `TamingShrew` |
| All's Well That Ends Well | `AllsWell` |
| Measure for Measure | `MeasureMeasure` |
| The Comedy of Errors | `ComedyErrors` |
| The Two Gentlemen of Verona | `TwoGentlemen` |
| The Merry Wives of Windsor | `MerryWives` |
| Love's Labour's Lost | `LovesLabour` |
| Pericles | `Pericles` |
| Cymbeline | `Cymbeline` |
| The Winter's Tale | `WintersTale` |
| The Two Noble Kinsmen | `TwoKinsmen` |

### Histórias
| Obra Completa | Slug Sugerido |
|---------------|---------------|
| History of Henry IV, Part I | `Henry4P1` |
| History of Henry IV, Part II | `Henry4P2` |
| History of Henry V | `Henry5` |
| History of Henry VI, Part I | `Henry6P1` |
| History of Henry VI, Part II | `Henry6P2` |
| History of Henry VI, Part III | `Henry6P3` |
| History of Henry VIII | `Henry8` |
| History of King John | `KingJohn` |
| History of Richard II | `Richard2` |
| History of Richard III | `Richard3` |

### Poemas
| Obra Completa | Slug Sugerido |
|---------------|---------------|
| Sonnets | `Sonnets` |
| Venus and Adonis | `VenusAdonis` |
| The Rape of Lucrece | `Lucrece` |
| Troilus and Cressida | `TroilusCressida` |

---

## 🔑 Extração de Palavras-Chave

### Estratégia Automática

Para cada cena, extrair palavra-chave do título seguindo estas regras:

1. **Identificar substantivo principal** no título
2. **Usar localização** se mencionada (ex: "Banquete", "Muralha")
3. **Usar personagem** se for foco (ex: "Fantasma", "Bruxas")
4. **Usar conceito** se for abstrato (ex: "Ambicao", "Vinganca")

### Exemplos de Mapeamento

| Título Original | Palavra-Chave Extraída |
|-----------------|------------------------|
| O Contraste entre o Teatro Social e a Dor Interior | `TeatroSocial` |
| A Irrupção do Sobrenatural e o Chamado à Vocação | `Fantasma` |
| A Educação do Imaginário e a Vergonha da Inação | `Ator` |
| A Tensão Escatológica e a Consciência da Morte | `SerOuNaoSer` |
| A Captura da Consciência Pela Arte | `Ratoeira` |
| A Inversão dos Valores no Imaginário | `Bruxas` |
| A Inoculação da Ambição | `Ambicao` |

### Regras de Normalização

```python
def gerar_palavra_chave(titulo: str) -> str:
    """
    Extrai palavra-chave do título da cena
    """
    # Remover artigos e preposições
    stopwords = ['o', 'a', 'do', 'da', 'de', 'e', 'para', 'entre']

    # Pegar primeira palavra substantiva significativa
    palavras = titulo.lower().split()
    palavras_filtradas = [p for p in palavras if p not in stopwords]

    # Pegar até 2 palavras principais
    chave = ''.join([p.capitalize() for p in palavras_filtradas[:2]])

    # Limitar a 20 caracteres
    return chave[:20]
```

---

## 📁 Estrutura de Diretórios

### Proposta de Organização

```
projetos/w_shakespeare/
├── hamlet/
│   ├── 01_cenas_identificadas.md
│   ├── audios/
│   │   ├── WS_Hamlet_01_TeatroSocial.mp3
│   │   ├── WS_Hamlet_02_Fantasma.mp3
│   │   ├── WS_Hamlet_03_Ator.mp3
│   │   └── metadata.json
│   └── logs/
│       └── generation_log.json
├── macbeth/
│   ├── 01_cenas_identificadas.md
│   ├── audios/
│   │   ├── WS_Macbeth_01_Bruxas.mp3
│   │   ├── WS_Macbeth_02_Ambicao.mp3
│   │   └── metadata.json
│   └── logs/
│       └── generation_log.json
└── ...
```

### Arquivo metadata.json

```json
{
  "obra": "Hamlet, Prince of Denmark",
  "obra_slug": "Hamlet",
  "notebook_id": "19bde485-a9c1-4809-8884-e872b2b67b44",
  "audios": [
    {
      "arquivo": "WS_Hamlet_01_TeatroSocial.mp3",
      "cena_numero": 1,
      "titulo_cena": "O Contraste entre o Teatro Social e a Dor Interior",
      "localizacao": "Ato I, Cena 2",
      "artifact_id": "abc-123-def-456",
      "data_geracao": "2026-02-27T06:00:00",
      "duracao_segundos": 1200,
      "tamanho_bytes": 15000000,
      "status": "downloaded"
    }
  ]
}
```

---

## 🔍 Busca e Recuperação

### Por Nome de Arquivo
```bash
# Buscar todas as cenas de Hamlet
ls projetos/w_shakespeare/hamlet/audios/WS_Hamlet_*.mp3

# Buscar cena específica por número
ls projetos/w_shakespeare/*/audios/WS_*_04_*.mp3

# Buscar por palavra-chave
ls projetos/w_shakespeare/*/audios/WS_*_*_Fantasma.mp3
```

### Por Metadata
```bash
# Buscar artifact_id específico
jq '.audios[] | select(.artifact_id == "abc-123")' projetos/w_shakespeare/*/audios/metadata.json

# Buscar por localização (Ato I)
jq '.audios[] | select(.localizacao | contains("Ato I"))' projetos/w_shakespeare/*/audios/metadata.json
```

---

## ✅ Checklist de Implementação

- [ ] Criar tabela de mapeamento obra → slug (41 obras)
- [ ] Criar função de extração de palavras-chave
- [ ] Validar unicidade dos nomes gerados
- [ ] Criar estrutura de diretórios `audios/` e `logs/`
- [ ] Implementar geração de metadata.json
- [ ] Testar com 3 cenas
- [ ] Validar comprimento máximo dos nomes
- [ ] Garantir compatibilidade cross-platform (Windows/Mac/Linux)

---

## 🎯 Exemplo Completo (Hamlet - Primeiras 3 Cenas)

```
projetos/w_shakespeare/hamlet/audios/
├── WS_Hamlet_01_TeatroSocial.mp3      (18 min, 15 MB)
├── WS_Hamlet_02_Fantasma.mp3           (20 min, 17 MB)
├── WS_Hamlet_03_Ator.mp3               (19 min, 16 MB)
└── metadata.json                        (3 KB)
```

**Total estimado para ~400 áudios:**
- Tamanho médio: 16 MB/áudio
- Total: ~6.4 GB de áudios
- Metadata: ~400 KB

---

## ❓ Decisão Final

**Qual formato você prefere?**

**Opção A (Recomendada):**
```
WS_Hamlet_01_TeatroSocial.mp3
WS_Macbeth_02_Ambicao.mp3
```

**Opção B (Mais descritiva):**
```
shakespeare_hamlet_cena01_teatro_social.mp3
shakespeare_macbeth_cena02_ambicao.mp3
```

**Opção C (Customizada):**
```
[Seu formato preferido]
```

---

**Aguardando sua aprovação para:**
1. ✅ Formato de nomenclatura final
2. ✅ Confirmar extração automática de palavras-chave
3. ✅ Iniciar implementação do sistema
