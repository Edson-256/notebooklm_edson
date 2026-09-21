# I Promessi Sposi — fechamento da série (4 áudios "faltantes" + desligar o cron)

## Diagnóstico (2026-09-21)

O relatório do StudioM4 ("⬇️ Baixados: 351/355", "Criados: 0", "Pendentes: 0") **não indica falha**.
Em `audios/metadata.json`:

| status           | qtd |
|------------------|-----|
| `downloaded`     | 351 |
| `skipped_legacy` |   4 |

Os 4 são as seqs **1–4** (`C_00-Promesi.Sposi_cena001..004`). O `skip_reason` registrado:

> Áudios antigos no studio usaram prompt genérico (Methodology) sem Scene Identifier — não casam
> com cenas específicas. Usuário optou por continuar a partir de seq 14 (seqs 5–13 estão prontos
> com prompts cena-by-cena).

Ou seja: **não há nada em `status=created` esperando download**. `--download` sozinho devolve
"Nada pendente." Fechar a série exige escolher entre dois caminhos.

## Caminho A — baixar os artifacts legacy que já existem no studio

Rápido (minutos), mas o conteúdo é o prompt genérico: 4 arquivos que **não** correspondem cena a cena.

```bash
cd "/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/mazoni/I Promesi Sposi"
python3 scripts/audio_runner.py --fetch-legacy
```

- Salva em `audios/legacy/promessi_legacy_NN_<id8>.m4a` e registra em `metadata.json` na chave
  `legacy_downloads`.
- **Não** mexe no status `skipped_legacy` das seqs 1–4 — o manifesto continua dizendo a verdade.
- Idempotente: arquivo já presente é pulado.

## Caminho B — recriar as cenas 1–4 com os prompts corretos (recomendado)

Coerente com o resto da série; custa 2 dias por causa da cota free (3 áudios/dia).

```bash
cd "/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/mazoni/I Promesi Sposi"
python3 scripts/audio_runner.py --only-seqs 1-4 --redo --dry-run   # confere o plano
python3 scripts/audio_runner.py --only-seqs 1-4 --redo --max 3     # dia 1: cria 3
python3 scripts/audio_runner.py --download                          # dia 2: baixa os 3
python3 scripts/audio_runner.py --only-seqs 4 --redo --max 1        # dia 2: cria a última
python3 scripts/audio_runner.py --download                          # dia 3: baixa a última
```

`--redo` só é aceito junto de `--only-seqs`; ele libera as seqs alvo do filtro de processados
(inclusive `skipped_legacy`). A entrada antiga do `metadata.json` é sobrescrita (o runner loga um
AVISO ao fazê-lo).

## Desativar o cron

```bash
cd "/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/mazoni/I Promesi Sposi"
./scripts/cron_disable.sh --status    # ver a linha atual
./scripts/cron_disable.sh             # desativa (comenta, com backup em logs/)
./scripts/cron_disable.sh --enable    # reativa quando quiser
```

**Ordem importa:** no Caminho B, o cron (ou o `--download` manual) ainda é necessário no dia seguinte
a cada criação. Desative **depois** de baixar tudo. No Caminho A, pode desativar imediatamente.

Desativar este cron também encerra o auto-commit de `audios/metadata.json` que o wrapper dispara via
`scripts/git_state_commit.sh` (ver CLAUDE.md, seção do escritor automático). Os outros wrappers
(aristoteles, cof_v2, don-quijote, notre-dame) continuam ativos.
