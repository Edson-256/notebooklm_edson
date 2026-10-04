# Prompt para abrir uma sessão nova no repo musica_composicao

Gerado em 2026-10-03 pela sessão notebooklm_edson. Uso: `cd ~/dev/_pessoal/musica_composicao && claude`, depois cole o
bloco abaixo.

---

```text
Atualize os verbetes do glossário de escuta (tarefa musica_composicao-fnid; verbetes em
catalogo/escuta/glossario/) com as fontes novas que entraram na base depois que os verbetes foram escritos.

CONTEXTO
- A base de fontes mora no repo notebooklm_edson (SÓ LEITURA para você — não escreva lá; outra sessão e um cron
  commitam nele):
  ~/dev/notebooklm_edson/projetos/musica/glossario_escuta/deep_research/
  - 04_consolidacao/selecionadas.json — todas as fontes; cada uma tem número "n" (o # que os verbetes citam),
    família, título, autor, url, nota e, quando foi subida como arquivo, o nome do arquivo em 05_arquivos_enviados/.
  - 04_consolidacao/CONSOLIDACAO.md — divergências conferidas e mapa de confusões (#1–#105).
  - 06_council/CONSOLIDACAO_council.md — as fontes #106–#138 (pesquisa do council_llm sobre as lacunas), com o
    trecho que prova cada uma e a situação de cada lacuna.
- Os números #1–#101 não mudaram. As fontes NOVAS são #102–#138:
  - #102 Wolff, milonga gaúcha (F2) · #103 Valenzuela, modo de mi (F4) · #104 Peter Manuel, flamenco jazz (F4)
  - #105 BN Digital, subgêneros do samba / samba de breque (F6) · #14 Chenette, hemíola (T) — este já existia como
    número, mas só agora tem texto
  - #106–#112 bolero mexicano × cubano (F7) · #113–#121 toada × moda de viola, cateretê × cururu (F1)
  - #122–#126 valsa/seresta e valse musette (F6/F8) · #127–#131 chamamé AR × RS/MS e chimarrita (F2)
  - #132–#135 samba de breque (F6) · #136–#137 vanera × xote (F2) · #138 Bergerot, encarte da valse musette (F8)
- O texto completo de cada fonte também está no NotebookLM (notebook 4ac56794, títulos "Gloss · <família> · …"),
  mas para citar, use o PDF/arquivo/URL e confira o trecho no texto.

O QUE FAZER
1. Leia selecionadas.json (#102–#138) e CONSOLIDACAO_council.md.
2. Para cada verbete afetado, acrescente o que as fontes novas sustentam, citando o #. Prioridade:
   - bolero: o lado mexicano deixa de ser lacuna (trío romántico, requinto — #106 é o principal); requinto com
     notação continua faltando.
   - toada × moda de viola: critério de caráter/andamento (moda recitativa e de métrica elástica; toada lenta e
     "simples") — NÃO é padrão de viola escrito; dizer isso.
   - chimarrita: ternária nos Açores × binária no RS (#127, #130).
   - chamamé Corrientes × RS: continua LACUNA CONFIRMADA (agora com busca dedicada) — manter declarado.
   - samba de breque: definição (#105) + o que #132–#135 sustentam; sem transcrição de breque.
   - valse musette: acompanhamento = contrabaixo + 1–2 guitarras, acordeão "sans vibration", "coup de plume" dos
     guitarristas manouches (#138).
   - hemíola: #14 (6/8 ↔ 3/4; 3-3-2 da música popular).
   - flamenco / modo de mi / cadência andaluza: #103, #104. Milonga: #102 (autor Daniel Wolff; Fernando Mattos é o
     compositor analisado).
3. Mesmo padrão de antes: afirmação → # da fonte; inferência rotulada como inferência; lacunas declaradas.
4. Se achar erro na base (trecho que não está na fonte, número trocado), NÃO corrija o repo notebooklm_edson:
   anote num arquivo do seu repo (catalogo/escuta/glossario/ERROS_BASE.md) e avise o Edson no fim.
5. Beads do musica_composicao: atualize musica_composicao-fnid (ou crie subtarefa) e encerre a sessão com /encerrar.
```
