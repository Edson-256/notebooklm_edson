# PILOTO — conhecimento por presença × representação no diagnóstico

> **O que é.** A instância de referência do item 5 (técnica filosófica): um problema clínico
> real levado pelos **7 passos**, terminando em artefatos expressivos **universais e sem
> PII**. É a prova viva de que o estudo filosófico e o trabalho são uma coisa só — o que o
> 6º passo (exame de consciência) exige da Aula-008.
>
> **Problema-condutor:** *o conhecimento por presença (o paciente dado em pessoa,
> irredutível, inesgotável) vs. o conhecimento por representação (prontuário, laudo, CID,
> imagem — seleção finita e guardável da presença) no ato de diagnosticar.*
>
> **Restrição inegociável:** zero PII. Só o universal/anonimizado. Não fabricar caso, dado
> nem citação (Art. 1).

---

## A distinção-chave (consolidada)

- **Presença** = o paciente irredutível e inesgotável; o real dado em pessoa, que nenhum
  registro esgota.
- **Representação** = prontuário / laudo / CID / imagem — uma **seleção finita e guardável**
  da presença. Indispensável, e perigosa quando tomada *pela* presença.
- **As lacunas da representação são estruturais** (ela é, por definição, seleção), não
  defeitos a "preencher" inventando — preencher por suposição é o Art. 1 violado.
- **Máxima operacional:** **na dúvida, a presença corrige a representação, nunca o
  contrário.**

---

## Os 7 passos aplicados

### 1. Anamnese
*Como aprendi a "ver" um diagnóstico? De onde vêm meus pressupostos?* Levantar a própria
pré-compreensão: a formação médica, os protocolos, o hábito do dado primeiro. (Abrir com
`templates/diario_anamnese.md`.)

### 2. Meditação
Pôr-se diante de um paciente **real, privado, sem registro identificável** — a coisa mesma,
antes da categoria. Conhecimento por presença (item 6) do problema concreto. Nenhuma nota
identificável: registra-se só a estrutura do que se viu (`templates/diario_presenca.md`).

### 3. Exame dialético (status quaestionis)
Levantar o estado da questão via NLM no notebook COF (`5508086a-…`): Lavelle (presença /
participação — notebook `1e63d07b-…`), Olavo; fenomenologia médica / Canguilhem (o normal e
o patológico) **se** essas fontes subirem ao notebook. Stack **A·B·C·D**. Focus:
`templates/nlm_focus_piloto.md`. (Sem fontes, marcar como lacuna a investigar — não
inventar.)

### 4. Pesquisa histórico-filológica
A genealogia dos termos-chave: *diagnóstico* (διά-γνωσις = "conhecer através/distinguir"),
*presença*, *representação*. O que cada palavra carregava na origem e como deslizou
(cruza item 2).

### 5. Hermenêutica
O que a **medicina de dados** (OncoBase, fluxo image-first, IA assistiva) **ganha** —
escala, reprodutibilidade, memória — e o que **arrisca encobrir**: tomar a representação
pela presença, deixar o nexo real escapar entre os campos da ficha.

### 6. Exame de consciência
Voltar o problema sobre mim: *onde eu mesmo trato representação como presença?* O **Art. 1
(anti-invenção)** é aqui a guarda epistemológica — não confundir **símbolo** (um dado
construído, eventualmente fabricado) com **conceito** (um nexo real). Formular como
**perguntas/lugares a investigar**, não como afirmações fechadas: a IA não fabrica a
resposta clínica; ela emerge na consulta e entra pelo inbox de captura.

Perguntas-guarda (a investigar, não a afirmar):
- Onde decido a partir do laudo sem reverter ao exame da presença?
- Onde um dado ausente vira, na minha cabeça, um dado normal?
- Onde a fluência do sistema (preenchimento automático, sugestão da IA) substitui o ver?

### 7. Técnica expressiva
Produzir os artefatos **universais, sem PII**, no template de seis campos:

- **Ensaio curto** — a distinção e a máxima, em linguagem comunicável.
- **Focus-prompt NLM** — `templates/nlm_focus_piloto.md` (formato A Pórtico ou C Arena),
  para gerar o áudio localmente (ver `00_INDICE_E_SISTEMA.md` §6).
- **Letra SUNO** — `templates/suno_style_presenca.md` ("o paciente como presença / a
  tentação do dado"): a presença destilada em imagem, nenhum dado identificável.

---

## Os seis campos (o piloto como prática)

| Campo | Conteúdo |
|---|---|
| **Núcleo vivido** | Diagnosticar olhando o paciente **antes** do dado; flagrar onde o registro tenta substituir a presença. |
| **Cadência + gatilho** | 1 ciclo (este dossiê) agora; captura contínua no inbox quando a tensão presença/representação aparecer na consulta (sem PII). |
| **Artefato cognitivo** | Este dossiê dos 7 passos + o focus-prompt NLM dos passos 3 e 7. |
| **Artefato criativo** | A letra SUNO do passo 7. |
| **Ancoragem COF** | Conhecimento por presença (item 6) + técnica filosófica (item 5) + auto-imagem/autoconhecimento (item 7, o eu que decide); cumpre o passo 6 (não arquivar longe da vida). |
| **Loop de compartilhamento** | Antes de tudo **ético**: muda a conduta clínica. Depois transmissível (áudio, canção) sem expor ninguém. |

---

## Critério de sucesso

Não um texto bonito, mas **uma mudança de conduta nomeável** no diagnóstico (passo 6) +
artefatos universais gerados (passo 7) — e os comandos de geração prontos para rodar
localmente (`00_INDICE_E_SISTEMA.md` §6).

## Tarefas-satélite ligadas

- **T-procedência** ("círculo de latência"): comando `nlm` em `00_INDICE_E_SISTEMA.md` §6.
- **T-workflows**: gabarito em `diagnostico_representacao_vs_presenca_workflows.md`
  (preencher onde os sistemas reais vivem; eles não estão neste repo).
