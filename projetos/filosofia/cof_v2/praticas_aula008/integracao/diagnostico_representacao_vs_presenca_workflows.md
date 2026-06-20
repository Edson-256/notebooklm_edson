# Gabarito — onde os workflows favorecem a representação sobre a presença

> **Status: gabarito/roteiro a preencher localmente.** Os sistemas reais (pipeline de laudo,
> relatório de cirurgia em n8n, m_dermato image-first, HMP, OncoBase) **não estão neste
> repositório**. Este documento é o **roteiro de análise** — as perguntas a fazer a cada
> sistema — para ser preenchido onde os sistemas de fato vivem. **Não inventar** o
> comportamento dos sistemas: onde não se observou, deixar como lacuna.

## Critério de leitura (o que procurar)

Em cada sistema, localizar os pontos onde o **desenho** induz a tomar a **representação**
(dado/laudo/imagem) **pela presença** (o paciente). Sinais típicos:

- decisão tomada a partir de um campo/laudo **sem caminho de volta** ao exame da presença;
- **ausência de dado** que o sistema apresenta (ou o operador lê) como **normalidade**;
- automação/sugestão de IA cuja **fluência** desencoraja a verificação;
- campos estruturados que **forçam** o real numa categoria (a lacuna estrutural some).

## Roteiro por sistema (preencher local)

Para **cada** sistema abaixo, responder:
1. Onde a representação **substitui** a presença no fluxo de decisão?
2. Onde uma **lacuna estrutural** é apresentada como dado positivo (ou como normal)?
3. Onde a **fluência** do sistema (autopreenchimento, sugestão) desencoraja reverter à presença?
4. Que **ponto de retorno à presença** poderia ser inserido sem quebrar o fluxo?

| Sistema | (1) substituição | (2) lacuna→positivo | (3) fluência | (4) retorno à presença |
|---|---|---|---|---|
| Pipeline de laudo | <preencher> | <preencher> | <preencher> | <preencher> |
| Relatório de cirurgia (n8n) | | | | |
| m_dermato (image-first) | | | | |
| HMP | | | | |
| OncoBase | | | | |

## Saída esperada

Uma lista priorizada de **pontos de retorno à presença** a inserir nos workflows — pequenas
fricções deliberadas que reabrem o exame do paciente onde o desenho hoje fecha na
representação. Alimenta de volta o passo 6 do piloto (mudança de conduta nomeável).
