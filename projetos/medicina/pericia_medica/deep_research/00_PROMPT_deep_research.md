# Prompt de deep research — complementar a biblioteca de Perícia Médica

- **Tarefa:** `notebooklm_edson-ll06` · criado 2026-09-26
- **Uso:** o mesmo prompt vai ao ChatGPT (Deep Research), ao agente Claude na nuvem e — em versão
  condensada, porque o campo do NotebookLM é curto — ao Deep Research do NotebookLM (Gemini).
- **Idioma:** instruções em inglês, saída em pt-BR (regra do ecossistema).
- **Anexos opcionais para o ChatGPT:** `_acervo_atual_84_livros.txt` e
  `_notebook_irmao_e5f0fdb9_31_fontes.tsv` (a lista do que já temos). O prompt abaixo já traz um
  resumo; anexar ajuda a evitar repetição.

---

## PROMPT COMPLETO (copiar daqui até o fim da seção)

```text
# ROLE
You are a research librarian specialized in Brazilian medico-legal and social-security law and in
evidence-based forensic/occupational medicine. You are building the "current, primary-source"
layer of a reference library used by a Brazilian medical expert witness (perito médico) who works
in judicial (cível, trabalhista, federal/JEF) and social-security (INSS/RGPS) cases.

# CONTEXT — WHAT THE LIBRARY ALREADY HAS (do NOT recommend these)
The library is a Google NotebookLM notebook. It already holds 84 textbooks (157 sources), mostly
foreign-language standard references, many without a publication date:
- Brazilian perícia/legal: Perícia Médica — Consulta Rápida; Perícia Médica Previdenciária
  (Trezub & Patsis); Perícia Médica Previdenciária (Vinicius Nunes Silva); Perícias Médicas:
  Teoria e Prática (Epiphanio); CPC Comentado 7th ed. 2021 (Marinoni/Arenhart/Mitidiero);
  Medicina Legal 11th ed. (Genival Veloso de França); Manual de Medicina Legal (Delton Croce Jr.);
  Medicina Legal I–II (Del-Campo); Odontologia Legal (Vanrell); Entomologia Forense (Scaglia).
- Forensic (EN): Gradwohl's; Knight's Forensic Pathology; Simpson's Forensic Medicine; Spitz &
  Fisher; Modi; Parikh; Taylor's Medical Jurisprudence.
- Toxicology/pharmacology, occupational medicine (CURRENT OEM 5th ed.; Hunter's; Textbook of
  Clinical OEM; ergonomics), orthopaedic examination (Magee, McRae, Reider, Apley, Kendall,
  Daniels & Worthingham), PM&R (Braddom; DeLisa), neurology (Adams & Victor; DeJong; Blumenfeld),
  neuropsychology (Lezak; Compendium of Neuropsychological Tests), psychiatry (Kaplan & Sadock;
  DSM-5 Handbook of Differential Diagnosis; Fish's), pain (Bonica; Wall & Melzack; Explain Pain),
  semiology, radiology (Brant & Helms; Greenspan; Resnick), pathology, physiology, anatomy,
  epidemiology/methods (Gordis; Rothman; Fletcher; Hulley; Cochrane DTA Handbook; Greenhalgh).
- A sister notebook (31 web sources) already has: CFM Resolution 2.056/2013; CPC arts. 464–480
  commented (Aurum, Projuris); AMB draft guidelines for civil medico-legal reports (Jan 2025) and
  AMB administrative report protocol (Jul 2025); AMB causal-nexus protocol; Penteado's 10 criteria
  for causal nexus; CREMEB "Nexo entre Doença e Trabalho"; CFM/CREMESP/CREMEGO perícia booklets;
  USP thesis on malingering in perícias; Cremepe on medical record analysis.

The gap is therefore NOT textbook knowledge. The gap is the CURRENT, OFFICIAL, PRIMARY layer:
norms in force today, their latest consolidated text, official manuals and protocols, binding
case law, and recent high-quality evidence syntheses.

# TASK
Find the sources that fill that gap, verify each one exists and is current as of today, and
return a prioritized, deduplicated list ready to be loaded into NotebookLM.

Cover these domains (the examples are search leads to VERIFY, not facts — confirm whether each
exists, is in force, and what, if anything, replaced it):

D1. Social security (INSS/RGPS) and disability benefits — the consolidated text of the benefits
    law and its regulation; the official manual(s)/guidelines of the federal medical-expert
    service (Perícia Médica Federal) for incapacity assessment; any official decision-support
    guidelines by condition; rules on remote/document-based assessment (e.g., Atestmed or
    successors); BPC/LOAS and disability assessment (biopsychosocial model, Índice de
    Funcionalidade Brasileiro and its current regulatory status); retirement of persons with
    disability; relevant joint ordinances/normative instructions currently in force.
D2. Judicial expert practice — CPC provisions on expert evidence (current text); CNJ resolutions
    on court experts (registration, fees, conduct); rules specific to Justiça Federal/JEF and
    Justiça do Trabalho; binding or qualified precedents on perícia médica (STF/STJ repetitive
    themes, TNU súmulas and representative themes, TST precedents) — only binding/qualified ones.
D3. Professional ethics and regulation — the Medical Ethics Code currently in force and its
    amendments; CFM resolutions on medical expert work, the assistant expert (assistente técnico),
    certificates/atestados, medical records, telemedicine; CFM/AMB material on the specialty
    "Medicina Legal e Perícia Médica"; relevant CFM opinions (pareceres).
D4. Occupational medicine and causal nexus — the official list of work-related diseases currently
    in force (Ministry of Health); NTEP/FAP rules; CAT; the Regulatory Norms (NRs) most used in
    litigation (e.g., occupational health program, unhealthy/hazardous work, ergonomics) in their
    current wording; official protocols for work-related mental disorders and burnout
    (ICD-11 QD85) and for musculoskeletal disorders (LER/DORT).
D5. Impairment and damage rating — the latest edition/status of the AMA Guides to the Evaluation
    of Permanent Impairment; the Brazilian table for insurance/traffic-accident indemnity
    (DPVAT/SPVAT or successor) as currently in force; the Portuguese national incapacity tables
    (labour and civil law) often cited in Brazil; WHO ICF and WHODAS 2.0 official documents.
D6. Classifications — ICD-11 official reference and the status of its adoption in Brazil;
    official Portuguese-language ICD-11 resources; DSM-5-TR (reference only).
D7. Evidence syntheses published in the last ~10 years that directly inform expert opinions:
    symptom/performance validity and malingering (consensus statements), causation assessment in
    occupational disease, chronic pain and fibromyalgia in disability evaluation, return-to-work
    and fitness-for-work, work-related mental disorders. Prefer consensus statements, systematic
    reviews and guidelines from recognized bodies (e.g., WHO, ILO, Cochrane, national societies).
D8. Forensic/criminal protocols (brief) — current UN Istanbul Protocol and Minnesota Protocol;
    official Brazilian norms on corpo de delito and IML procedures in force.

# SOURCE QUALITY RULES (strict)
1. Prefer PRIMARY and OFFICIAL: planalto.gov.br, in.gov.br (Diário Oficial), gov.br (INSS, MPS,
   MS, MTE), portal.cfm.org.br / sistemas.cfm.org.br, cnj.jus.br, stf.jus.br, stj.jus.br,
   cjf.jus.br (TNU), tst.jus.br, WHO/ILO/UN, peer-reviewed journals (PubMed/SciELO-indexed).
2. For legislation, point to the CONSOLIDATED ("compilado") official text, not a third-party copy.
3. EXCLUDE: law-firm marketing, blogs, course sellers, Scribd/Passei Direto/slide decks,
   unsourced summaries, paywalled items with no legal open copy (mark them instead, see below).
4. Every item must be VERIFIED: you must have actually opened the URL. Never invent a norm number,
   date or URL. If you cannot confirm something, put it in the "Não verificado" section, not in
   the main list.
5. State the validity status: "em vigor", "alterada por X (data)", "revogada por X", or "status
   incerto". Flag anything revoked or replaced since 2019.
6. Target 40–80 items in total, prioritized. The notebook has room for about 140 more sources,
   and each source can hold up to 500,000 words (one URL or one PDF per source).

# OUTPUT (write the whole report in Brazilian Portuguese, pt-BR)
Part A — Resumo executivo (≤ 15 linhas): as lacunas mais graves que você encontrou e as 10 fontes
mais importantes a adicionar.

Part B — Tabela principal, one row per source, grouped by domain D1–D8, with EXACTLY these columns
(keep the column names in Portuguese as written):
| id | dominio | prioridade (1-3) | titulo_oficial | emissor_autor | tipo | numero | data | vigencia | url | formato | acesso | por_que_importa | substitui_ou_atualiza |
- id: D1-01, D1-02, ...
- tipo: lei | decreto | resolução | portaria | instrução normativa | manual oficial | precedente | diretriz | revisão sistemática | consenso | classificação | outro
- formato: HTML | PDF | outro   · acesso: aberto | pago | cadastro
- por_que_importa: one sentence on how a perito uses it.

Part C — "Não verificado": items you believe exist but could not confirm, with what you tried.

Part D — Fontes descartadas relevantes: notable items you rejected and why (e.g., revoked,
unofficial copy only, paywalled).

Part E — The same main table again as a single CSV block (semicolon-separated, UTF-8, header
row included), so it can be merged automatically with other researchers' results.
```

---

## VERSÃO CONDENSADA — NotebookLM Deep Research

Campo curto e busca voltada a documentos brasileiros, então esta versão vai em pt-BR (desvio
consciente da regra "prompt em inglês": aqui o texto é consulta de busca, não instrução ao modelo).

```text
Fontes oficiais e atuais (em vigor em 2026) para perito médico no Brasil, que complementem livros-texto: texto compilado da Lei 8.213/1991 e do Decreto 3.048/1999; manuais e diretrizes oficiais da Perícia Médica Federal/INSS para avaliação de incapacidade; Atestmed e perícia documental; BPC/LOAS e avaliação biopsicossocial da deficiência (IFBr-M); CPC arts. 156-158 e 464-480; resoluções do CNJ sobre peritos e honorários; súmulas e temas da TNU, STJ e STF sobre perícia médica; Código de Ética Médica vigente e resoluções do CFM sobre perícia, assistente técnico, atestado, prontuário e telemedicina; Lista de Doenças Relacionadas ao Trabalho vigente, NTEP/FAP, NR-7, NR-15, NR-17; protocolos oficiais de LER/DORT e de transtornos mentais relacionados ao trabalho e burnout (CID-11 QD85); AMA Guides (edição atual), tabela SPVAT/DPVAT, Tabela Nacional de Incapacidades de Portugal, CIF e WHODAS 2.0; CID-11 no Brasil; consensos sobre simulação e validade de sintomas, nexo causal ocupacional, dor crônica e fibromialgia na avaliação de incapacidade; Protocolo de Istambul e Protocolo de Minnesota. Priorizar planalto.gov.br, in.gov.br, gov.br, cfm.org.br, cnj.jus.br, stf, stj, cjf (TNU), tst, OMS, OIT e artigos revisados por pares. Excluir blogs e escritórios de advocacia.
```
