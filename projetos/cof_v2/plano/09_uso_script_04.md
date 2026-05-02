# Como usar `scripts/04_generate_prompt_batch.py`

Script que **gera prompts e guias** (em `prompts/<id>.md` e `guias/<id>.md`)
para cada item do plano. **Não dispara áudio no NotebookLM** — só prepara
o material textual.

## Pré-requisitos

- `_raw/dell_md/` populado (rsync do dell-server) — necessário para `resolve_body`.
- `plano/01_inventario_completo.json` atualizado (782 itens, 40 lotes de 20).

## Opções de uso

| Opção | O que faz | Exemplo |
|---|---|---|
| `--list` | Mostra todos os 40 lotes com pendentes/preparados por lote | `python3 scripts/04_generate_prompt_batch.py --list` |
| `--stats` | Conta itens por status (pending/prepared/sent/done/error) | `python3 scripts/04_generate_prompt_batch.py --stats` |
| `--batch N` | Processa o lote N (1–40), 20 itens | `python3 scripts/04_generate_prompt_batch.py --batch 1` |
| `--from N --to M` | Processa lotes consecutivos N até M (inclusivo) | `python3 scripts/04_generate_prompt_batch.py --from 1 --to 3` |
| `--item ID` | Processa um único item (útil para regenerar/testar) | `python3 scripts/04_generate_prompt_batch.py --item aula-144` |
| `--dry-run` | Mostra o que faria, **não escreve arquivos** | `python3 scripts/04_generate_prompt_batch.py --batch 1 --dry-run` |
| `--regenerate` | Sobrescreve arquivos já preparados | `python3 scripts/04_generate_prompt_batch.py --batch 1 --regenerate` |

## Comportamento padrão

- **Idempotente**: se `prompts/<id>.md` E `guias/<id>.md` já existem, o item
  é pulado (status `skipped`). Use `--regenerate` para sobrescrever.
- **Tracking**: cada execução atualiza `plano/_progresso.json` com
  `{"<id>": {"status": "prepared", "updated_at": "..."}}`.
- **Erros não param o lote**: itens com erro são reportados mas o lote segue
  para os próximos.

## Fluxo recomendado

```bash
cd ~/dev/notebooklm_edson/projetos/cof_v2

# 1. Ver estado geral
python3 scripts/04_generate_prompt_batch.py --list

# 2. Testar 1 item antes de gastar tokens em 20
python3 scripts/04_generate_prompt_batch.py --item aula-001
# Inspecionar: prompts/aula-001.md e guias/aula-001.md
# Se tiver problema, ajustar o script e regenerar:
python3 scripts/04_generate_prompt_batch.py --item aula-001 --regenerate

# 3. Rodar lote 1 (20 itens)
python3 scripts/04_generate_prompt_batch.py --batch 1

# 4. Verificar progresso
python3 scripts/04_generate_prompt_batch.py --stats
ls prompts/ | wc -l   # deve ter 20
ls guias/ | wc -l     # deve ter 20

# 5. Continuar com próximos lotes quando houver cota
python3 scripts/04_generate_prompt_batch.py --batch 2
# ...
python3 scripts/04_generate_prompt_batch.py --batch 40
```

## Estimativa de consumo

- **Por item**: ~3 KB de prompt + ~1.5 KB de guia. Praticamente sem chamada
  a LLM externa neste script — toda lógica é determinística (templates +
  regex). **Custo de tokens é zero** para a etapa de preparação.
- O **consumo de tokens** acontece quando você dispara o áudio no NotebookLM
  com o prompt gerado — etapa posterior, em runner separado.

## O que cada item gera

### `prompts/<id>.md`

Prompt completo com:
- Metadata (`[ID]`, `[CATEGORIA]`, `[FORMATO]`, `[POSIÇÃO MESTRA]`,
  `[ANTERIOR]`, `[PRÓXIMA]`)
- Identificação inicial obrigatória ("Esta é a aula NNN do COF, apresentada
  em DD de mês de YYYY")
- Intro sequencial (lembra o anterior)
- Desenvolvimento conforme formato (Deep Dive / Brief / Critique / Debate)
- Escopo estrito (não vazar para outras aulas)
- Outro sequencial (gancho da próxima)
- Tom/linguagem (PT-BR didático)

Tamanho típico: ~2.500–3.500 chars (cabe folgado no `--focus` do `nlm`,
limite ~10k chars).

### `guias/<id>.md`

Guia do estudante com:
- Metadata + posição na série
- Síntese (placeholder — preencher após áudio)
- Conceitos-chave (placeholder)
- Autores e obras citadas (preenchido por regex automático sobre o body —
  só nomes que **realmente aparecem**, sem invenção)
- Sugestões de leitura (placeholder)
- Conexões com outras partes do COF (placeholder)
- Exercícios de fixação (placeholder)
- Posição na trajetória (placeholder)

A heurística de autores cobre ~30 nomes comuns no COF (Olavo, Aristóteles,
Voegelin, Lavelle, etc.). Falsos-positivos e omissões são esperados;
revisar manualmente após gerar.

## Conferindo antes de disparar áudios

Após rodar todos os 40 lotes:

```bash
ls prompts/ | wc -l    # deve ser 782
ls guias/ | wc -l      # deve ser 782
python3 scripts/04_generate_prompt_batch.py --stats
```

Antes de disparar áudios:
- **Capturar `_sources_map.json`**: mapeamento `<arquivo .md em compiladas/>`
  → `<source_id no notebook NLM>`. Ainda não automatizado.
- **Definir runner** (`cof_v2_audio_runner.py`) seguindo
  `~/dev/notebooklm_edson/docs/regras_pipeline_audio_por_cena.md`.

## Limitações conhecidas (revisar manualmente quando aparecer)

- **Gancho da próxima aula**: a heurística pode pegar boilerplate ("Curso
  Online de Filosofia | Aula 02 3 Seminário de Filosofia [COF20090321]").
  Nesse caso, editar manualmente em `prompts/<id>.md` antes de disparar.
- **Autores no guia**: regex tem ~30 nomes; complementar/corrigir após
  ler a transcrição.
- **Fragmentação de Apostilas/Artigos/Teoria do Estado**: a heurística atual
  só fragmentou bem Apostilas (7 fragmentos). Artigos e Teoria do Estado
  ficaram como 1 item cada. Revisar após gerar prompt para decidir se
  precisa subdividir mais.
- **Aulas extracurriculares**: o body é extraído do bloco `## FONTE: ...`
  do Unif_; se um curso usa marcador diferente, vai falhar (só esses 22
  cursos com padrão conhecido funcionam).
