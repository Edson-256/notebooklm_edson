# Análise: pastas em `projetos/` vs notebooks da conta pessoal

> Data: 2026-04-21  
> Objetivo: identificar sub-pastas em `notebooklm_edson/projetos/` que não correspondem a notebooks da conta pessoal (`edson.michalkiewicz@gmail.com`) e verificar se foram copiadas da conta profissional (`notebooklm_michalk`).

## 1. Autenticação `nlm`

| Perfil | Conta | Status |
|---|---|---|
| `default` | edson.michalkiewicz@gmail.com | ✅ OK após reautenticação (40 notebooks) |
| `profissional` | edson@michalkcare.com | ✅ OK (73 notebooks) |

Lista atualizada de notebooks pessoais regravada em `docs/notebooklm/notebooks_conta_pessoal.md` (21/04/2026).

## 2. Inventário de sub-pastas em `projetos/`

| Pasta | Match em pessoal (40 atual) | Match em profissional (73 atual) | Veredito |
|---|---|---|---|
| `ben-hur` | ✅ "Ben-Hur" (`1ecdbff9…`) | — | **Pessoal** ✓ |
| `w_shakespeare` | ✅ "William Shakespeare" (`62400b1d…`) | — | **Pessoal** ✓ |
| `g_flynn` | ✅ "Gone Girl - Gillian Flynn" (`26d46e89…`) | ❌ | **Pessoal** ✓ (confirmado pelo usuário e pela lista atual) |
| `quo_vadis` | ⚠️ notebook ainda não criado | ❌ | **Pessoal** ✓ (confirmado pelo usuário; notebook a criar) |
| `calculo` | ❌ | ✅ "Calculo Munen-Foulis" | **Cópia do profissional** |
| `cirurgia_oncologica` | ❌ | ✅ "Cirurgia Oncológica" | **Cópia do profissional** |
| `Curriculum` | ❌ | ⚠️ sem notebook de mesmo nome; relacionado a "Curso RDD +" | **Cópia do profissional** |
| `devita_cme` | ❌ | ✅ "DeVita - Câncer - por capítulo" | **Cópia do profissional** |
| `Lehninger` | ❌ | ✅ "Lehninger 8ª ed" | **Cópia do profissional** |
| `Next_js` | ❌ | ✅ "Next.js" | **Cópia do profissional** |

## 3. Origem no repositório edson

Todas as 6 pastas "suspeitas" entraram no repo `notebooklm_edson` no **mesmo commit** — `616ea90` de **23/03/2026**, cuja mensagem é literalmente:

```
feat: adicionar projeto Ben-Hur (81 cenas + runner) e integrar projetos remotos
```

> *"integrar projetos remotos"* — evidência direta de importação em massa vinda de outro repositório.

`g_flynn` é mais antigo (commit `6dd7476` de 18/03, junto com `w_shakespeare`) — não veio desse batch.

## 4. Comparação de conteúdo: `edson/projetos/<pasta>` vs `michalk/projetos/<pasta>`

Método: `diff -rq` recursivo.

### `cirurgia_oncologica` — **idêntico**
```
(nenhuma diferença)
```
Só contém `prompt_retalho.md`, igual nos dois repos.

### `calculo` — **cópia; michalk é fonte**
- michalk tem a sub-pasta `munem_vol1/` a mais (áudios/recursos — presumivelmente .gitignored em edson).
- `section_index.json` difere: michalk tem campos `synced_to_icloud`, `synced_at`, `listened`, `archived`, `archived_at` (metadados de sync/arquivamento de 2026-03-24); edson tem a versão antiga sem esses campos.

### `Curriculum` — **idêntico (conteúdo); michalk tem áudios**
- michalk tem `audios/` a mais — demais arquivos iguais.

### `devita_cme` — **cópia; michalk é fonte**
- michalk tem `audio/` e `logs/` a mais.
- michalk tem `docs/devita_cme_plano_mestre.docx` a mais.
- `chapter_index.json` difere pelos mesmos campos de sync/archive (mesmo padrão do `calculo`).

### `Lehninger` — **cópia, com pequena divergência de código**
- michalk tem `audio/` e `logs/` a mais.
- `section_index.json` difere (campos de sync/archive — mesmo padrão).
- `como_usar.md` difere: versão em michalk é maior (inclui seções `=== CRIAÇÃO DE ÁUDIOS ===`, `--sections`, `--format-filter`, `=== DOWNLOAD ===`, `=== RETRY ===`, `=== SLIDES ===`). Versão em edson é a inicial/reduzida.
- `lehninger_runner.py` difere: michalk tem suporte a `retry-failed`, `env=env` para `NLM_PROFILE`, trata `download_failed` além de `created`. Edson não tem esses incrementos.

### `Next_js` — **IDÊNTICO a `_tech_para_med/next_js` em michalk**
- A pasta não existe em `michalk/projetos/Next_js`, mas existe em `michalk/projetos/_tech_para_med/next_js` (minúsculo, agrupada sob `_tech_para_med`).
- `diff -rq` retornou vazio — conteúdo 100% igual.

## 5. Resolução dos casos ambíguos (21/04, após reautenticação)

### `g_flynn` (Gone Girl — Gillian Flynn) — **Pessoal** ✓
- Confirmado pelo usuário.
- Corresponde ao notebook pessoal `Gone Girl - Gillian Flynn` (`26d46e89-53ba-4ced-a9bc-f2d271885cf3`), 2 fontes. Criado após 25/02, por isso não aparecia na lista antiga.

### `quo_vadis` (Quo Vadis — Henryk Sienkiewicz) — **Pessoal** ✓
- Confirmado pelo usuário — projeto pessoal novo, notebook ainda a ser criado em NotebookLM.

## 6. Padrão de divergência nas cópias

As diferenças em `section_index.json` / `chapter_index.json` seguem um padrão consistente: **michalk tem os metadados de sync/archive de 2026-03-24**; edson ficou congelado na versão pré-sync. Isso é coerente com o commit `69cdf4a` de edson (*"feat: sistema de sync/archive de áudios"*) ter sido desenvolvido depois da importação mas sem re-propagar o estado do michalk.

Em outras palavras: as cópias em edson são **snapshots parciais e defasados** do michalk.

## 7. Recomendações (sem executar sem autorização)

### Candidatos a remoção de `notebooklm_edson/projetos/`
Todos pertencem à conta profissional e já existem no repo `notebooklm_michalk`:
- `calculo` — versão em michalk é mais completa (tem `munem_vol1/` e metadados de sync mais novos).
- `cirurgia_oncologica` — idêntico ao michalk.
- `Curriculum` — idêntico ao michalk (michalk tem `audios/` a mais).
- `devita_cme` — michalk tem `.docx` e metadados novos; nada a recuperar de edson.
- `Lehninger` — michalk tem `lehninger_runner.py` e `como_usar.md` mais recentes.
- `Next_js` — em michalk está em `_tech_para_med/next_js` (conteúdo 100% igual).

### A manter em `notebooklm_edson`
- `ben-hur` — notebook `Ben-Hur`.
- `w_shakespeare` — notebook `William Shakespeare`.
- `g_flynn` — notebook `Gone Girl - Gillian Flynn`.
- `quo_vadis` — projeto novo, notebook a criar.

### Ação segura sugerida
Como é repositório Git, usar `git mv`/`git rm` conforme **CLAUDE.md global** (`~/dev/CLAUDE.md`: *"Use `git mv` em vez de `mv` para mover/renomear arquivos e diretórios dentro do repo"*). Para remover:

```bash
cd /Users/edsonmichalkiewicz/dev/notebooklm_edson
git rm -r projetos/calculo projetos/cirurgia_oncologica projetos/Curriculum \
          projetos/devita_cme projetos/Lehninger projetos/Next_js
git commit -m "cleanup: remover pastas duplicadas da conta profissional"
```

> `NÃO APAGAR SEM AUTORIZAÇÃO EXPRESSA.` Executar apenas quando o usuário confirmar.
