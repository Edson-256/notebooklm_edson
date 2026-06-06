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
- ✅ **Enriquecimento dos 782 guias concluído** (2026-05-02) via **OpenAI
  GPT-5-mini** com Structured Outputs (JSON schema strict). Provider
  alternativo foi necessário porque a API Anthropic continuava retornando
  "credit balance too low" mesmo após a compra de $25 via Stripe. O script
  `05_enrich_guias.py` ganhou flags `--provider openai|anthropic`,
  `--model`, e `--workers N` (paralelismo via `ThreadPoolExecutor`).
  - **Custo total real:** ~$6.41 (13M tok in + 1.57M tok out)
  - **Tempo:** ~1h com `--workers 12`
  - **Bugs corrigidos no `resolve_body`** (afetavam Anthropic também):
    1. extras com nome `Aula_NN` (regex agora usa `re.search(r'Aula[_\s-](\d+)')`)
    2. 7 livros do notebook: fallback para `compiladas/livros/`
    3. 12 extras com `numero_interno` global acumulado: fallback rank-based
       (posição do item entre os do mesmo `curso` ordenados)
- ✅ **Runner de áudio** (`06_audio_runner.py`) implementado e validado em
  dry-run (782 itens, sanity-check pass, formatos `deep_dive/brief/critique/debate`
  mapeados). **Pronto para rodar agora** que os guias estão enriquecidos.

**Notebook NLM:** `5508086a-da53-4947-bce4-a1d7d83cf0e2`
**Conta:** `default` (edson.michalkiewicz@gmail.com)

## ⚠️ Segurança — chaves de API expostas em sessão antiga

Foram expostas em conversa anterior (revogue se ainda ativas):

- Anthropic: `n8n-automation` (sk-ant-api03-Ad6…iwAA), `cof-enrich-haiku` (sk-ant-api03--bjA…wgAA)
- OpenAI: chave `sk-proj-0bJ5…GkhUA` usada no enrich em 2026-05-02 — rotacione no
  console da OpenAI se for sensível.

## Roteiro de retomada

### 1. Histórico — billing Anthropic (FYI, não bloqueia mais)

O erro "credit balance is too low" persistia mesmo após a compra real de $25 via
Stripe (recibo 2717-7300-3129, 2026-05-02). Suporte foi acionado num sábado.
**Workaround adotado:** usar OpenAI gpt-5-mini (rodou em 1h por $6.41). Quando
o suporte da Anthropic resolver, dá pra reusar `--provider anthropic` no
script — system prompt é idêntico nos dois caminhos.

### 2. Re-rodar enrichment (se necessário)

O `05_enrich_guias.py` é idempotente (pula já `enriched` no `_progresso.json`).

```bash
# OpenAI (atual)
export OPENAI_API_KEY='...'
.venv/bin/python scripts/05_enrich_guias.py --all \
  --provider openai --model gpt-5-mini --workers 12

# Anthropic (quando billing voltar)
export ANTHROPIC_API_KEY='...'
.venv/bin/python scripts/05_enrich_guias.py --all --provider anthropic

# Forçar re-geração de itens específicos
.venv/bin/python scripts/05_enrich_guias.py --item aula-001 \
  --provider openai --model gpt-5-mini --regenerate

# Ver progresso
.venv/bin/python scripts/05_enrich_guias.py --stats
```

### 3. Upload das 121 fontes no notebook NLM ✅

Concluído em sessão anterior. `_sources_map.json` gerado em 2026-05-02 via
`scripts/06_build_sources_map.py` (782 itens mapeados, 0 misses, 1 colisão de
slug documentada — `extra-consci-ncia-de-imortalidade-aula-04` aparece com
seq_global 630 e 631 porque o curso tem dois arquivos "aula 4" no original).

Para revalidar (após qualquer mudança nas fontes):

```bash
.venv/bin/python scripts/06_build_sources_map.py --refresh-nlm
.venv/bin/python scripts/06_build_sources_map.py --validate
```

### 4. Runner de áudio ✅ (implementado, guias prontos)

`scripts/06_audio_runner.py` pronto e validado em dry-run. Os 782 guias estão
enriquecidos (passo 2). Próximo passo é o disparo dos áudios. Segue todas as
10 regras de `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`.

**Antes do primeiro disparo real (obrigatório):**

```bash
# 1. Lista o plano sem disparar — confira título/prompt/format
.venv/bin/python scripts/06_audio_runner.py --dry-run --skip-auth-check

# 2. Filtra por kind/range para inspecionar amostras variadas
.venv/bin/python scripts/06_audio_runner.py --dry-run --skip-auth-check --kind livro --max 5
.venv/bin/python scripts/06_audio_runner.py --dry-run --skip-auth-check --only 1,500,782
```

**Para disparar em produção (em lotes pequenos!):**

```bash
# Ativa nlm e dispara um único item de teste primeiro
.venv/bin/python scripts/06_audio_runner.py --max 1
# Espera ~3min e baixa o primeiro áudio para inspeção
.venv/bin/python scripts/06_audio_runner.py --download

# Se o áudio sair coerente com o prompt, libera lotes maiores:
.venv/bin/python scripts/06_audio_runner.py --max 10
.venv/bin/python scripts/06_audio_runner.py --download
```

**Filtros úteis:**
- `--from N --to M`: range de seq_global
- `--kind <aula|livro|extra_aula|apostila|artigo|teoria_estado>`
- `--only 1,5,42`: lista explícita
- `--max N`: limite de itens nesta sessão

Estimativa total: ~39h para 782 itens com `INTERVAL_SECONDS=120`. Dividir em
sessões de 10–20 itens conforme regra 9 do pipeline.

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
    ├── 05_enrich_guias.py             # rodou em 2026-05-02 via OpenAI gpt-5-mini
    ├── 06_build_sources_map.py        # rodou em 2026-05-02 (782/782)
    └── 06_audio_runner.py             # pronto, validado em dry-run
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
Estou retomando o projeto cof_v2. Leia ~/dev/notebooklm_edson/projetos/filosofia/cof_v2/RETOMAR.md e me oriente o próximo passo. Estou no diretório certo.
```
