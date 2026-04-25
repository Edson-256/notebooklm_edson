# Regras de engenharia — pipelines de áudio por cena (NotebookLM)

> **Para a IA:** ao iniciar um novo projeto que dispare áudios do NotebookLM
> por "cena/episódio/módulo" (ex.: Ben-Hur, Quo Vadis, novos livros, cursos),
> leia este arquivo antes de escrever ou adaptar o runner. As regras abaixo
> nasceram de bugs reais e não são opcionais.

## Contexto

Um "runner" desta família (`<obra>_runner.py`) tipicamente:

1. Carrega uma lista de cenas/episódios.
2. Para cada cena, encontra um prompt customizado em disco.
3. Dispara `nlm create audio ... --focus <prompt>` com sources específicas.
4. Registra `artifact_id` num `metadata.json` para retomada e download posterior.

Os bugs graves que já apareceram (Quo Vadis, abr/2026) foram **todos por
incompatibilidade entre identificadores** — não por falha do NotebookLM.

---

## Regra 1 — Uma única chave canônica por cena

**Definir desde o início:** o ID de uma cena é um número **global**, contínuo,
único, do início ao fim da obra (`1..N`). Esse é o único ID usado em:

- nome de arquivo de prompt (`001_titulo.md`, `134_titulo.md`)
- chave em `metadata.json` (`cena_numero`)
- nome do `.mp3` final (`obra_001_keyword.mp3`)
- filtros em CLI (`--max-scenes`, `--from`, `--to`)

Qualquer outra numeração (capítulo, parte, episódio dentro de temporada,
cena local) **vive em campo separado** (`local_num`, `parte`, `capitulo`),
nunca substituindo o ID global.

> ❌ Nunca: "número de cena = 1-35 na Parte 1 e 1-33 na Parte 2".
> ✅ Sempre: "número global 1-134; campos `parte=2, local_num=1` à parte".

## Regra 2 — Não derivar IDs de markdown narrativo via regex

Markdown como `01_cenas_identificadas.md` é para humanos: a numeração pode
reiniciar por seção, ter erros de digitação, mudar de formato no meio.
Regex sobre esse arquivo é frágil e silencioso quando falha.

**A fonte canônica de cenas é um JSON estruturado** (`_prompts_manifest.json`
ou equivalente), gerado uma única vez a partir do markdown e mantido como
fonte da verdade. O runner lê **só** desse JSON.

Schema mínimo recomendado:

```json
[
  {
    "audio": 1,                 // ID GLOBAL — a única chave canônica
    "filename": "001_xxx.md",   // bate com prompts_cenas/
    "title": "...",
    "part_num": 1,              // metadados extras
    "local_num": 1,
    "localization": "Parte 1, Capítulo 1 (cena 1/2)",
    "chapter_file": "QV-P1-C01.md"
  },
  ...
]
```

## Regra 3 — Sanity-checks no startup do runner (fail loud)

Antes de processar a primeira cena, validar:

```python
ids = [s["audio"] for s in scenes]
assert len(ids) == len(set(ids)), f"IDs duplicados! {len(ids)} vs {len(set(ids))} únicos"
assert ids == sorted(ids),         "IDs fora de ordem"
assert ids == list(range(1, len(ids)+1)), "IDs não-contínuos (esperado 1..N)"

for s in scenes:
    prompt = prompts_dir / f"{s['audio']:03d}_{slug(s['title'])}.md"
    assert prompt.exists(), f"Prompt faltando para cena {s['audio']}: {prompt.name}"
```

Se qualquer assert falhar, **abortar antes de criar áudio**. Quota da NLM
custa caro e áudio gerado com prompt errado é inutilizável.

## Regra 4 — Dry-run obrigatório na primeira execução de uma série nova

Sempre rodar `--dry-run` primeiro e **inspecionar** a saída cena por cena:

- Os títulos exibidos batem com a obra/seção esperada?
- O nome do prompt que será carregado bate com o título?
- A localização (`Parte 3, Capítulo 28`) condiz com o ID global?

O `--dry-run` deve imprimir lado a lado: `ID | título | nome do prompt`.
Divergências saltam aos olhos. Só rodar real quando o dry-run estiver limpo.

## Regra 5 — `metadata.json` indexado pelo ID canônico, sempre

- `cena_numero` no metadata = ID global.
- Inserção `metadata[cena_numero] = entry` deve **avisar** se já existe
  entrada com aquele número (loga "sobrescrevendo"). Sobrescrever silencioso
  esconde o bug clássico de duas cenas diferentes colidindo no mesmo ID.
- Ao salvar, conferir que `entry.cena_numero == prompt_carregado.global_id ==
  título_correspondente.global_id`. Os três têm que coincidir.

## Regra 6 — Reutilizar runner: copiar e adaptar com auditoria

Quando começar um projeto novo (Crime e Castigo, Os Irmãos Karamazov, etc.):

1. Copiar `quo_vadis_runner.py` como ponto de partida.
2. Trocar **só** as constantes (`NOTEBOOK_ID`, `BOOK_TITLE`, `BOOK_SLUG`,
   `TOTAL_SCENES`, `PARTE_RANGES`, `PROMPTS_MANIFEST_FILE`).
3. **Não** mexer em `extract_scenes`, `load_scene_prompt`, `save_metadata` —
   essas funções já estão certas para o esquema canônico. Tocar nelas
   reintroduz bugs.
4. Antes do primeiro run real: dry-run + sanity checks da Regra 3.

## Regra 7 — Backup antes de "consertar" metadata

Se um bug exigir reparar `metadata.json` (renumeração, retitulação),
**sempre** gravar `metadata.json.bak_YYYY-MM-DD` antes de sobrescrever, e
adicionar `metadata_repaired: <data + motivo>` nas entradas modificadas.
Reparos sem rastro tornam impossível auditar quais áudios físicos existem
de verdade no servidor.

## Regra 8 — `nlm` é fire-and-forget, não retry-safe

`nlm create audio` retorna um `artifact_id` mas o áudio leva ~2min para
processar no servidor. Não confundir "criação disparada" com "áudio pronto":

- `status: created` no metadata = artifact_id obtido, áudio em processamento.
- `status: downloaded` = `.mp3` baixado e validado em disco.
- Só conta como "processada" para fins de pular cena no próximo run quem
  estiver em `created` ou `downloaded` (já está no metadata corrente).
- **Não** disparar a mesma cena duas vezes só porque ainda não baixou —
  isso queima quota e gera duplicatas no servidor.

## Regra 9 — Quota e ritmo

NotebookLM Audio Overview tem limites empíricos (não publicados). Observado:

- `--focus` aceita até ~10.000 caracteres (truncar acima disso).
- Dezenas de áudios disparados em sequência funcionam; centenas geram
  rate-limit silencioso (artifact criado mas processamento nunca completa).
- Default seguro: 2min entre disparos (`INTERVAL_SECONDS = 120`).
- Em lotes grandes, dividir em sessões de ~10-20 áudios e baixar antes de
  disparar mais.

## Regra 10 — Logging que serve para auditoria, não decoração

Cada disparo deve registrar em `logs/<obra>_session_<timestamp>.json`:

- `cena_numero` (global)
- `title` enviado
- `prompt_filename` carregado (não só "custom")
- `prompt_chars` (tamanho enviado ao `--focus`)
- `source_ids` enviados
- `artifact_id` retornado
- `status` final da tentativa

Sem `prompt_filename` no log, não dá para auditar depois "qual prompt
gerou esse áudio?". O bug do Quo Vadis só foi reconstituído porque o nome
do prompt podia ser inferido do `cena_numero` — não conte com sorte.

---

## Checklist resumida (cole no topo do runner novo)

```
[ ] ID canônico = global 1..N, único, contínuo
[ ] Cenas vêm de _prompts_manifest.json (JSON), não de regex em .md
[ ] Sanity-checks no startup: IDs únicos, contínuos, prompts existem
[ ] Dry-run antes do primeiro run real, com ID|título|prompt lado a lado
[ ] Metadata indexado por ID canônico; warn em sobrescrita
[ ] Não tocar em extract_scenes/load_scene_prompt/save_metadata ao copiar
[ ] Backup .bak_YYYY-MM-DD antes de reparar metadata
[ ] Status created ≠ downloaded; não redisparar o que já está em metadata
[ ] 2min entre disparos; lotes de 10-20; sem força bruta
[ ] Logging com prompt_filename, não só "custom"
```

---

## Referências

- Bug que motivou estas regras: Quo Vadis, 2026-04-25, beads
  `notebooklm_edson-ind`. Numeração local por parte (P1: 1-35, P2: 1-33,
  P3: 1-63, EP: 1-3) colidiu com numeração global de prompts (1-134),
  causando 29 áudios criados com prompt errado e `metadata.json` com
  títulos descasados dos áudios físicos.
- Runner de referência (corrigido): `projetos/quo_vadis/quo_vadis_runner.py`.
- Manifest de referência: `projetos/quo_vadis/_prompts_manifest.json`.
