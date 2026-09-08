# Experimento de cota — Gemini Notebook (ex-NotebookLM)

**Issue:** `notebooklm_edson-g5e7` · **Início:** 2026-09-08 · **Autorizado por:** Edson

## Por que existe

Em **02/09/2026** o Google trocou o modelo de cota do Gemini Notebook:

- a cota passou a repor **a cada ~5 horas**, e não mais uma vez por dia;
- existe um **teto semanal** por cima — bater nele trava até o reset da semana;
- o limite virou **baseado em compute** (pesa complexidade do prompt, modelo,
  tamanho e recurso usado), não contagem de artefatos. "3 áudios" deixou de ser
  uma unidade válida — nossos áudios são `--length long` e pesam mais que a média.

Fontes: [blog oficial](https://blog.google/innovation-and-ai/products/gemini-notebook/new-flexible-usage-limits/)
e [suporte](https://support.google.com/gemininotebook/answer/17670842) — *"the quota
refreshes every 5 hours until you reach your weekly limit"*. Multiplicadores por
tier: AI Plus 2×, AI Pro 4×, Ultra 5×/20×. **A cadência de reset não difere por
tier** — só a magnitude.

**Nenhum desses números é publicado, e a interface desta conta não tem painel de
uso** (verificado na UI em 2026-09-08: Configurações só oferece Ajuda, Feedback,
Discord, Idioma, Marcas-d'água, Licenças, Dispositivo, Gerenciar assinatura).
Logo, a única forma de conhecer os tetos é medir o que a API responde.

## Confirmação prévia (2026-09-07)

Teste pontual na conta free `espanhol`: os 3 áudios do dia já tinham sido criados
às 08:20; às 23:15, ~15h depois, uma 4ª criação **foi aceita** (artifact `74a7fb8b`),
sem `RESOURCE_EXHAUSTED`. O teto rígido de 3/dia não vale mais para a conta gratuita.
Um único sucesso prova reposição intra-dia, **não** que a cadência seja de 5h.

## Desenho

| | |
|---|---|
| **Conta sob estresse** | free `espanhol` (Don Quijote) — descartável, 219 cenas na fila |
| **Conta observada** | pro `default` (Aristóteles) — **instrumentação passiva, sem estresse** |
| **Cadência da sonda** | de hora em hora (`0 * * * *`) |
| **Lote por rodada** | 5 cenas (`PROBE_BATCH`), parando no 1º `RESOURCE_EXHAUSTED` |
| **Freio** | a própria API — `NLM_COTA_OVERRIDE=99` desliga o cap do `projeto.toml` |
| **Telemetria** | `logs/nlm_usage.jsonl`, uma linha por desfecho |

**Por que hora em hora e não a cada 5–6h:** disparar na mesma cadência que se quer
medir mede o próprio cron, não a API. A sonda horária encontra a fronteira real da
janela. Um cron a cada 6h ainda subamostraria ~1h de reposição por ciclo.

**Por que a conta pro não é estressada:** ela sustenta Aristóteles (264 cenas
pendentes), COF, Ivan Ilitch, Paradise Lost e O Idiota. Bater o teto semanal ali
pararia a produção principal por dias. Como o Aristóteles já dispara 20 áudios/dia
sozinho, basta registrar o desfecho de cada criação para obter a curva de graça.

## Como ler os resultados

```bash
python3 ~/dev/notebooklm_edson/scripts/nlm_usage_report.py
python3 ~/dev/notebooklm_edson/scripts/nlm_usage_report.py --profile espanhol
```

O relatório responde as duas perguntas: **(1)** intervalo entre uma recusa e a
próxima criação aceita — se a mediana ficar perto de 5h, confirma a janela
anunciada; **(2)** volume acumulado por semana ISO antes de as recusas virarem
persistentes — 3+ recusas consecutivas sinalizam teto semanal, não fim de janela.

## Estado alterado (e como reverter)

1. **crontab:** a linha `20 8 * * * .../cron_daily.sh` foi comentada e substituída
   por `0 * * * * .../cron_probe.sh`. Ambas estão no crontab, a original comentada.
   Para encerrar: apagar a linha da sonda e descomentar a original.
   ⚠️ Instalar crontab **sempre** a partir de `/tmp` com backup antes — instalar de
   outro caminho apaga tudo em silêncio retornando `rc=0`.
2. **`audio_runner.py` (leitura-formativa):** ganhou `NLM_COTA_OVERRIDE` e
   `NLM_STOP_ON_RATE_LIMIT`. **Sem as envs, o comportamento é idêntico ao anterior** —
   os outros projetos que usam este runner não mudam.
3. **`07_audio_runner.py` (Aristóteles):** só chamadas de telemetria. Não altera
   ritmo, cota nem controle de fluxo.
4. **`projeto.toml`:** intocado — segue `por_dia = 3`.

## Riscos aceitos

- Se o teto semanal for baixo, o **Don Quijote fica parado** até o reset. É o
  objetivo do experimento, não um efeito colateral.
- A fila de 219 cenas comporta ~2 semanas no ritmo esperado.
