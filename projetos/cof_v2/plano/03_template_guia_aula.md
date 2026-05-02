# Template do guia de aula (instanciado por item)

Cada item gera `guias/<id>.md`. O guia acompanha o áudio gerado e serve como
"caderno do estudante" para expansão e aprofundamento.

---

```markdown
# Guia da {{tipo_humano}} {{numero_humano}} — {{titulo}}

**Data:** {{data_humana}} (se aplicável)
**Formato do áudio:** {{formato_audio}}
**Fonte original:** {{file_source}}
**Posição na série:** {{ordem_global}}/678 — anterior=[[{{anterior.id}}]], próxima=[[{{proxima.id}}]]

## Síntese

{{sintese}}

> Texto curto (até 300 palavras) que captura a tese central da {{tipo}} e o
> caminho argumentativo que Olavo percorre. Gerado por análise da transcrição.

## Conceitos-chave

{{lista_conceitos}}

> 5 a 8 conceitos centrais usados nesta {{tipo}}. Para cada um, uma frase de
> definição funcional dentro do contexto.

## Autores e obras citadas

{{lista_autores_obras}}

> **Apenas autores/obras realmente mencionados na transcrição.** Não inferir,
> não inventar. Se Olavo cita "Aristóteles" sem nomear obra específica,
> registrar "Aristóteles (sem obra específica nomeada nesta {{tipo}})".

> Formato:
> - **Autor (anos)** — *Obra* — contexto da citação na aula

## Sugestões de leitura para aprofundar

{{sugestoes}}

> Derivadas das obras citadas no item anterior. Se Olavo recomenda explicitamente
> uma ordem de leitura, preservar essa ordem. Caso contrário, ordem do mais
> acessível ao mais técnico.

## Conexões com outras aulas/cursos do COF

{{conexoes}}

> Quando Olavo remete a outras aulas/cursos do próprio COF (ex: "como vimos
> na aula 14"), registrar com link `[[aula-014]]`. **Apenas remissões
> explícitas no texto** — não inventar conexões temáticas.

## Exercícios de fixação

{{exercicios}}

> 3 a 5 perguntas de revisão. Tipos misturados:
> - Conceito (ex: "Defina, com palavras de Olavo, o que é 'imagem do mundo'")
> - Aplicação (ex: "Dê um exemplo, fora do COF, de…")
> - Reflexão pessoal (ex: "Em que aspecto da sua própria conduta…")

## Posição na trajetória

{{trajetoria}}

> Parágrafo curto situando esta {{tipo}} na sequência:
> - O que ela RESOLVE do ponto onde estávamos.
> - O que ela ABRE para a próxima.
> - Por que vem nesta ordem.

---

*Guia gerado automaticamente para acompanhamento do áudio
{{audio_artifact_id_quando_disponivel}}. Reservado o direito de revisão
manual antes do uso pedagógico.*
```

---

## Princípios de geração (aplicáveis pela IA que processa o lote)

1. **Não inventar fontes.** Se a transcrição não menciona explicitamente uma
   obra ou autor, não incluir nas seções de citações/sugestões. Vale a regra
   geral do projeto: "relatar fatos observados, não fabricar".

2. **Síntese é redutora, não interpretativa.** Capturar o que Olavo diz, não
   o que a IA acha que ele quis dizer.

3. **Citações ipsis litteris** quando relevantes — usar `> "frase"` para
   destacar. Manter a voz original quando ajuda o ouvinte a fixar conceito.

4. **Conexões só explícitas.** Olavo é dono do encadeamento; a IA não cria
   pontes que ele não fez.

5. **Tom didático, não sermão.** Guia é instrumento; deixe o conteúdo do
   Olavo falar.

## Saída

Salvar em `projetos/cof_v2/guias/<item.id>.md`. Estrutura final do diretório
após execução de todos os 34 lotes:

```
projetos/cof_v2/
├── prompts/         # 678 arquivos .md (prompts instanciados)
├── guias/           # 678 arquivos .md (guias instanciados)
└── plano/_progresso.json   # tracking: prepared / sent_to_nlm / artifact_received / downloaded
```
