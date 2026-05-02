# Roteiro para retomar — projeto COF v2

Você fez logout/login no Claude Code. Use este checklist na próxima sessão para
voltar exatamente de onde paramos.

## Onde paramos

- ✅ **Plano e templates** completos em `plano/` (9 arquivos)
- ✅ **121 fontes compiladas** em `compiladas/` (aulas anuais, livros, extras,
  temáticas)
- ✅ **781 prompts gerados** em `prompts/<id>.md`
- ✅ **781 guias com placeholders** em `guias/<id>.md` (autores citados já
  preenchidos via regex; síntese/conceitos/exercícios em branco)
- ✅ **121 fontes uploadadas no notebook NLM** (concluído)
- ✅ **`_sources_map.json` gerado** mapeando os 782 itens (seq_global 1–782) →
  source_id no notebook (script `06_build_sources_map.py`)
- ⏸️ **Enriquecimento dos guias via Haiku 4.5** — ainda bloqueado: API
  Anthropic retorna "credit balance too low" mesmo após compra real de $25
  via Stripe (recibo 2717-7300-3129, 2026-05-02). Hipótese: chave atual
  (`n8n-automation`, sufixo `iwAA`) está em workspace sem os créditos.
  Solução: criar `cof-enrich-haiku-v2` em workspace **Default**.
- ⏸️ **Runner de áudio** ainda não implementado (próximo passo)

**Notebook NLM:** `5508086a-da53-4947-bce4-a1d7d83cf0e2`
**Conta:** `default` (edson.michalkiewicz@gmail.com)

## ⚠️ Antes de tudo — segurança

Duas chaves de API foram expostas em conversa anterior:

- `n8n-automation` (sk-ant-api03-Ad6…iwAA)
- `cof-enrich-haiku` (sk-ant-api03--bjA…wgAA)

**Revogue ambas** em [console.anthropic.com](https://console.anthropic.com)
→ Chaves de API → ⋮ → Excluir chave de API.

Depois crie uma chave nova (`cof-enrich-haiku-v2`) **somente quando o billing
estiver resolvido** (passo 2).

## Roteiro de retomada

### 1. Resolver billing da API (a causa raiz da pausa)

O erro persistente "credit balance is too low" indica que os $25 visíveis em
"Créditos" são promocionais e **não destravam a API até cadastrar cartão**.

- [ ] Acesse [console.anthropic.com](https://console.anthropic.com) → menu
  esquerdo **"Faturamento"**
- [ ] Verifique se há **método de pagamento (cartão)** cadastrado. Se não,
  adicione.
- [ ] Verifique seu **tier de uso** (Free Trial / Build Tier 1 / 2 / …). Se
  for Free Trial, faça upgrade — geralmente comprar $5 com cartão promove
  para Build Tier 1.
- [ ] Se já tem cartão e mesmo assim falha: abra ticket de suporte mostrando
  prints. Pode ser bug de alocação de créditos entre workspaces.

### 2. Criar chave nova de API (após resolver billing)

- [ ] Console → Chaves de API → **+ Criar chave**
- [ ] Nome: `cof-enrich-haiku-v2`
- [ ] Workspace: **Default** (mesmo onde estão os créditos)
- [ ] Copie e teste pelo terminal:

```bash
cd ~/dev/notebooklm_edson/projetos/cof_v2
# No SEU prompt do Claude Code (com prefixo !):
! export ANTHROPIC_API_KEY='<chave nova>'

# Depois peça para mim no chat:
"testa a API com a chave nova"
```

### 3. Enriquecer os 781 guias com Haiku 4.5

Quando a API responder OK:

```bash
# Teste 1 item para validar saída
.venv/bin/python scripts/05_enrich_guias.py --item aula-001

# Inspecionar guias/aula-001.md (deve estar preenchido com síntese,
# conceitos, exercícios)

# Se OK, rodar todos os 781 (~$16, ~30 min com --rps 2)
.venv/bin/python scripts/05_enrich_guias.py --all
```

O script é **idempotente** (pula já enriched). Pode rodar em pedaços:

```bash
.venv/bin/python scripts/05_enrich_guias.py --batch 1
.venv/bin/python scripts/05_enrich_guias.py --from 1 --to 10
```

Acompanhar:

```bash
.venv/bin/python scripts/05_enrich_guias.py --stats
```

### 4. Upload das 121 fontes no notebook NLM ✅

Concluído em sessão anterior. `_sources_map.json` gerado em 2026-05-02 via
`scripts/06_build_sources_map.py` (782 itens mapeados, 0 misses, 1 colisão de
slug documentada — `extra-consci-ncia-de-imortalidade-aula-04` aparece com
seq_global 630 e 631 porque o curso tem dois arquivos "aula 4" no original).

Para revalidar (após qualquer mudança nas fontes):

```bash
.venv/bin/python scripts/06_build_sources_map.py --refresh-nlm
.venv/bin/python scripts/06_build_sources_map.py --validate
```

### 5. Implementar runner de áudio

`scripts/06_audio_runner.py` (a fazer) — análogo ao `quo_vadis_runner.py`,
respeitando as regras de
`~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`:

- ID canônico = `seq_global` do inventário (1–782)
- Manifest JSON como fonte da verdade
- Sanity-checks no startup
- Dry-run obrigatório antes do primeiro disparo
- 2min entre disparos
- Lotes de 10–20 itens
- Logging com `prompt_filename` no log

## Estado dos arquivos no repo

```
projetos/cof_v2/
├── RETOMAR.md                     # ← este arquivo
├── CLAUDE.md                      # contexto geral do projeto
├── _raw/                          # gitignored (~28 MB)
│   ├── dell_md/                   # 712 arquivos do disco do dell
│   ├── livros_notebook/           # 7 PDFs do notebook antigo
│   └── tematicas_notebook/        # 4 compilações temáticas
├── compiladas/                    # gitignored (~52 MB) - 121 fontes prontas
│   ├── aulas/                     # 25 anuais + 4 temáticas
│   ├── livros/                    # 70 livros
│   └── extracurriculares/         # 22 cursos
├── prompts/                       # gitignored - 781 .md
├── guias/                         # gitignored - 781 .md (placeholders)
├── plano/                         # commitado
│   ├── 00_PLANO_GERAL.md
│   ├── 01_inventario_completo.json    # 782 itens, fonte canônica
│   ├── 02_template_prompt.md
│   ├── 03_template_guia_aula.md
│   ├── 04_lotes_execucao.md           # 40 lotes
│   ├── 05_aulas_por_ano.md
│   ├── 06_extracurriculares.md
│   ├── 07_livros.md
│   ├── 08_tematicas.md
│   ├── 09_uso_script_04.md
│   └── _progresso.json                # gitignored
├── _sources_map.json             # commitado — fonte da verdade pro runner
├── _sources_map_raw.json         # gitignored — cache da listagem nlm
└── scripts/                       # commitado
    ├── 01_convert_to_md.py        # rodou no dell
    ├── 02_compile_year_groups.py
    ├── 03_collect_books_extras.py
    ├── 04_generate_prompt_batch.py    # rodou tudo
    ├── 05_enrich_guias.py             # bloqueado em billing/workspace
    └── 06_build_sources_map.py        # rodou em 2026-05-02 (782/782)
```

## Beads / sessão

- Issue ativa relevante: `notebooklm_edson-491` (já fechada)
- Para criar nova issue na retomada: `bd create --title="Enriquecer guias COF v2 com Haiku" --type=task --priority=2`

## Referências

- Plano completo: `plano/00_PLANO_GERAL.md`
- Como usar script 04: `plano/09_uso_script_04.md`
- Regras anti-bug pipeline áudio: `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`

## Comando para colar na próxima sessão

Cole isto no Claude Code novo e ele entra no contexto certo:

```
Estou retomando o projeto cof_v2. Leia ~/dev/notebooklm_edson/projetos/cof_v2/RETOMAR.md e me oriente o próximo passo. Estou no diretório certo.
```
