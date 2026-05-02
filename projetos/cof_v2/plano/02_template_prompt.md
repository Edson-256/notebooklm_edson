# Template do prompt de áudio (instanciado por item)

Cada item gera um prompt assim. Os campos `{{...}}` são substituídos por
`scripts/04_generate_prompt_batch.py` na hora de processar o lote.

---

```
[ID]: {{item.id}}
[FORMATO]: {{item.formato_audio}}
[TÍTULO]: {{item.titulo}}
[FONTE NLM]: source_id={{source_id_resolvido}}
[POSIÇÃO]: {{item.ordem_global}}/678 — anterior={{item.anterior}}, próxima={{item.proxima}}

INSTRUÇÕES PARA O ÁUDIO

ORIGEM E IDENTIFICAÇÃO
Este áudio integra a série didática do Curso Online de Filosofia (COF) de
Olavo de Carvalho. Ao iniciar, anuncie de forma clara e direta:
"Esta é a {{tipo_humano}} {{numero_humano}} do Curso Online de Filosofia,
{{data_humana_se_aplicavel}}."
A audiência precisa saber exatamente que aula é antes de qualquer outra coisa.

OBJETIVO PEDAGÓGICO
Tornar o conteúdo filosófico denso desta {{tipo}} acessível ao ouvinte sem
perder o rigor conceitual. Trate o ouvinte como um estudante interessado mas
não-especialista. Filosofia é responsabilidade total — preserve essa serenidade
e o senso de que cada conceito é uma decisão moral antes de ser teórica.

INTRODUÇÃO SEQUENCIAL (1–2 minutos)
{{IF item.anterior}}
Antes de entrar no conteúdo de hoje, lembre brevemente o que foi visto na
{{tipo_humano}} {{anterior.numero}} ({{anterior.titulo_curto}}, {{anterior.data}}).
Reative o fio condutor: a partir de onde o pensamento estava, para onde
caminhamos hoje. Não resuma o anterior em detalhe — só recoloque o ouvinte
no ponto da formação.
{{ELSE}}
Esta é a primeira {{tipo_humano}} da série. Apresente brevemente o cenário
geral do COF e o que torna esta {{tipo_humano}} um ponto de partida natural.
{{ENDIF}}

DESENVOLVIMENTO ({{duracao_alvo}} aprox.)
Aplique rigorosamente o formato **{{item.formato_audio}}**:
{{IF formato == 'Deep Dive'}}
- Análise detalhada dos pontos-chave da {{tipo}}.
- Para cada conceito central: definição, exemplo, implicação prática, eventual
  digressão pertinente.
- Preserve as imagens e exemplos do próprio Olavo (eles são pedagógicos).
- Demonstre o encadeamento argumentativo, não só o resultado.
{{ELIF formato == 'The Brief'}}
- Sumário executivo: tese central + 3–5 pontos de apoio.
- Linguagem direta, sem digressões.
- Foco no "o quê" e no "por que importa", não no "como se prova".
{{ELIF formato == 'The Critique'}}
- Apresente a posição que está sendo criticada de forma honesta antes de
  reproduzir a crítica de Olavo.
- Distinga: o que Olavo mostra ser falso, o que ele mostra ser confuso, o
  que ele mostra ser perigoso.
- Termine com o que fica de pé depois da crítica (não só destruição).
{{ELIF formato == 'The Debate'}}
- Apresente as posições legítimas em jogo (não só a de Olavo).
- Mostre os argumentos mais fortes de cada lado.
- Posicione Olavo como uma das vozes — a mais relevante para o COF — sem
  reduzir o tema a sua resposta.
{{ENDIF}}

ESCOPO ESTRITO
Use apenas o conteúdo desta {{tipo}} (source_id={{source_id_resolvido}}).
NÃO inclua material de outras aulas além de referências breves para
continuidade. NÃO improvise contexto que não está na fonte. Se a fonte é
omissa em algum ponto, diga "este ponto é tratado em outra aula" e siga.

ENCERRAMENTO SEQUENCIAL (~30 segundos)
{{IF item.proxima}}
Antes de fechar, anuncie a continuidade: na {{tipo_humano}} {{proxima.numero}}
({{proxima.titulo_curto}}, {{proxima.data}}) avançaremos para
{{proxima.gancho_curto}}. Deixe uma pergunta aberta que ligue esta {{tipo}}
à próxima.
{{ELSE}}
Esta é a última {{tipo_humano}} da série nesta categoria. Faça um fechamento
que situe o conteúdo na obra do Olavo como um todo.
{{ENDIF}}

LINGUAGEM E TOM
- Português brasileiro.
- Didático mas adulto — não infantilize.
- Fiel ao rigor do COF: nada de simplificações que distorçam.
- Evite jargão acadêmico desnecessário; quando usar termo técnico, defina.
```

---

## Notas de implementação

- `{{tipo_humano}}` é "aula", "curso", "livro", ou "compilação" conforme
  `item.kind`.
- `{{numero_humano}}` é "número NNN" para aulas; o título para os outros.
- `{{data_humana_se_aplicavel}}` aparece só para aulas (com data).
- `{{anterior.titulo_curto}}` é o `titulo` do item anterior, truncado em 60
  caracteres se necessário.
- `{{proxima.gancho_curto}}` precisa ser **derivado da transcrição da próxima
  aula** — uma sentença que sintetize o tema central. O gerador do prompt deve
  ler o body da próxima aula e extrair (heurística: 1ª frase do conteúdo, ou
  parágrafo após `## Aula NNN`).
- Tamanho final do prompt: ~2.500–3.500 caracteres. Bem abaixo do limite de
  10.000 chars do `--focus` do `nlm`.

## Como o prompt é entregue ao NotebookLM

Via `nlm audio create <NOTEBOOK_ID> --format <formato> --focus "<prompt>" --source-ids <id_fonte>`.

O parâmetro `--format` aceita: `deep_dive`, `brief`, `critique`, `debate`
(verificar nomes exatos com `nlm audio create --help` antes de executar).
