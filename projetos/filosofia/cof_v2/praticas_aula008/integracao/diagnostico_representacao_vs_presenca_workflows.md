# Gabarito — onde os workflows favorecem a representação sobre a presença

> **Status (2026-06-20): preenchido a partir de LEITURA dos repositórios reais**
> (`~/dev/n8n`, `~/dev/m_dermato`, `~/dev/oncoBase`). Os achados de "que dado o sistema
> captura/produz" são **factuais** (lidos da documentação/specs). Os "pontos de atenção"
> são **hipóteses formuladas como perguntas** — *não* afirmações clínicas. A interpretação
> final e a decisão de mudar conduta são do usuário (médico). **Não inventar.** Onde não se
> observou, fica como lacuna. Alimenta o **passo 6 do piloto** (mudança de conduta nomeável).

## Critério de leitura (o que procurar)

Pontos onde o **desenho** induz a tomar a **representação** (dado/laudo/imagem/resumo de IA)
pela **presença** (o paciente irredutível). Sinais típicos:

- decisão a partir de um campo/laudo **sem caminho de volta** ao exame da presença;
- **ausência de dado** apresentada (ou lida) como **normalidade**;
- automação/IA cuja **fluência** desencoraja a verificação;
- campos estruturados que **forçam** o real numa categoria (a lacuna estrutural some).

## Achados por sistema (factual) + perguntas (hipóteses a confirmar)

### Relatório de cirurgia V3 — pele (`n8n/prj_ativos/12_relatorio_cirurgia_v3`)
- **Captura/produz (factual):** Jotform (~95 campos) → normalização → 4 subworkflows: narrativa cirúrgica (Gemini→ClinicWeb), pedido AP (determinístico), PDF (Google Docs), orientações pós-op (OpenAI→HTML). Persistência em `core.*`.
- **Representação criada:** o prontuário inserido no ClinicWeb é **narrativa gerada por IA** a partir dos campos, não o ditado do cirurgião; orientações ao paciente também geradas por IA.
- **Perguntas:** (a) achado atípico que não cabe nos dropdowns vira "benigno" por falta de opção? (b) há etapa explícita de **revisão/validação médica** da narrativa Gemini antes de entrar no prontuário? (c) o paciente/consultor vê "relatório IA" ou "relatório do médico"?

### Relatório de cirurgia V4 — universal + ditado (`.../13_relatorio_cirurgia_v4`, em design)
- **Captura/produz (factual):** ~50 campos + **ditado** (textarea/áudio) + categoria → IA formaliza com template → placeholders `[COMPLETAR: …]` onde falta.
- **Representação criada:** transcrição do ditado + formalização técnica por IA.
- **Perguntas:** (a) transcrição (Whisper) erra jargão anatômico sem validação? (b) a formalização IA remove nuance de risco ("tive que alargar a incisão" → "incisão estendida")? (c) relatório com placeholders entra íntegro no prontuário?

### Curativos (`.../20_curativos_relatorio`)
- **Captura/produz (factual):** Jotform → normalização → Gemini gera texto clínico → DOCX/email/ClinicWeb.
- **Perguntas:** (a) achado inesperado (sinal de infecção não previsto) tem campo, ou some na narrativa? (b) anexar **foto da ferida** ao relatório ajudaria a manter o vínculo com a presença?

### HMP — história médica pregressa (`.../30_hmp`, produção)
- **Captura/produz (factual):** Jotform 162 campos / 113 condicionais, 8 blocos → `raw.ingestion_event` + `core.document` (`doc_type:'hmp'`); dedup por `payload_hash + cpf_window 7d`.
- **Perguntas:** (a) **ausência por condicional não-disparada** (ex.: β-HCG) é indistinguível de "perguntado e negativo"? (b) dedup de 7 dias descarta a 2ª submissão — e se ela corrigia um erro? (c) atualização incremental de medicações exige refazer todo o HMP?

### Revisão de sistemas (`.../35_revisao_sistemas`, em design)
- **Captura/produz (factual):** Jotform curto (constitucionais + por sistemas) → `doc_type:'revisao_sistemas'`.
- **Perguntas:** (a) snapshot pontual capta estado clínico que muda em horas? (b) queixa nova fora dos sistemas listados tem onde entrar ("algo mais?")?

### Resumo de história clínica (`.../50_resumo-historia`, ativo)
- **Captura/produz (factual):** CPF → busca `core.patient/document` + `ehr.clinical_history` → classifica (atual/crônico/resolvido) → **GPT gera resumo HTML**.
- **Perguntas:** (a) a classificação "atual vs. resolvido" é juízo clínico feito por IA? (b) conflito entre fontes (OCR vs. prontuário) é sinalizado ou silenciado? (c) a **fluência do HTML** desencoraja voltar aos laudos crus?

### Patient enrichment (`.../75_patient_enrichment`)
- **Captura/produz (factual):** match nome `core.patient` ↔ API ClinicWeb (exato → fuzzy → revisão manual) para preencher CPF.
- **Perguntas:** (a) homônimos podem fundir pacientes distintos no fuzzy? (b) CPF errado no ClinicWeb propaga sem auditoria?

### m_dermato — image-first (`~/dev/m_dermato`, pré-Fase 0)
- **Captura/produz (factual, das specs):** fotos de lesão + anamnese; abas anamnese visual / planejamento cirúrgico / reconciliação AP. Fotos locais (LGPD).
- **Perguntas:** (a) a **foto** (uma perspectiva: luz/ângulo/distância) tende a virar substituta do exame presencial (sem palpação, sem visão sistêmica)? (b) há aba de **contexto geral** (outras lesões, comorbidades) ou a lesão fotografada isola o paciente?

### OncoBase (`~/dev/oncoBase`, produção parcial)
- **Captura/produz (factual):** ingestão de laudos por OCR (Docling) → dedup (hash/fingerprint) → classificação/split LLM → `core.document` (+ embeddings planejados), `ehr.clinical_history` append-only.
- **Perguntas:** (a) **erro de OCR** (ex.: "margens comprometidas" mal reconhecido) persiste como fato sem validação? (b) split LLM pode falhar em silêncio (`split_oversize_pending`)? (c) fingerprint/Metaphone pode colidir/fundir pacientes?

## Tabela-síntese (preenchida; hipóteses como perguntas)

| Sistema | (1) substituição representação→presença | (2) lacuna→positivo/normal | (3) fluência desencoraja verificar | (4) ponto de retorno à presença (sugestão) |
|---|---|---|---|---|
| OncoBase/laudo (OCR) | laudo OCR lido como o exame | erro OCR como texto válido | resumo/HTML fluente | sinalizar trechos com baixa confiança de OCR antes de persistir |
| Relatório cirurgia (V3/V4) | narrativa IA como o ato | placeholder/categoria fechada | texto técnico "pronto" | checkbox de **validação médica** da narrativa antes do ClinicWeb |
| m_dermato | foto como o exame | só a lesão fotografada | dx assistido por IA | aba de **contexto sistêmico** + nota "confirmar ao exame" |
| HMP / Rev. sistemas | formulário como a anamnese | ausência condicional = "normal" | dedup automática | distinguir "não perguntado" de "negado"; campo "algo mais?" |
| Resumo de história | resumo IA como o prontuário | conflito de fontes ocultado | HTML bem formatado | destacar conflitos entre fontes; link ao documento cru |

## Saída esperada

Lista priorizada de **pontos de retorno à presença** — pequenas fricções deliberadas que
reabrem o exame onde o desenho hoje fecha na representação. **Priorização e decisão são do
usuário**; este gabarito só organiza os fatos e as perguntas. Candidatos de maior alavancagem
(a confirmar): (1) validação médica explícita das narrativas de IA antes do prontuário
(V3/resumo); (2) distinguir "não perguntado" de "negado" no HMP; (3) sinalização de baixa
confiança de OCR no OncoBase. Cada item escolhido vira uma mudança de conduta nomeável no
**passo 6 do piloto**.
