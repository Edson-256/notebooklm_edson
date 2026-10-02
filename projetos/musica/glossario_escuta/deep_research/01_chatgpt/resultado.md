
Concluí a triagem segundo os critérios do arquivo: fontes prioritariamente acadêmicas/institucionais, acesso efetivamente verificável e exclusão de Scribd, blogs, listicles e referências que não consegui confirmar com segurança. O objetivo original exige precisão técnica suficiente para sustentar compasso, padrões rítmicos, modos, instrumentos e reconhecimento auditivo. Markdown colado

O resultado principal reúne **63 fontes**, organizadas em F1–F10 + termos básicos. A cobertura mais consistente ficou em **flamenco, choro, forró, bossa nova e teoria musical básica**. Por exemplo, o material didático oficial andaluz fornece compás, modos e transcrições de flamenco; o dossiê do IPHAN oferece uma base extensa para choro; e a dissertação sobre João Gilberto analisa timing, prosódia, timbre e deslocamentos rítmicos. [Junta de Andalucía](https://www.juntadeandalucia.es/cultura/flamenco/sites/default/files/flamenco/docs/gestion_cultural_materiales_didacticos.pdf)

Algumas lacunas são importantes e foram **mantidas explicitamente como lacunas**, em vez de inferidas: principalmente **chamamé × vanera gaúcha**, **vanera × xote**, **cateretê × cururu**, detalhes das **batidas/ponteios e afinações da viola caipira**, e sobretudo a distinção musical rigorosa entre **bolero cubano × bolero mexicano**. Já para tango, a fonte aberta de Link & Wendland é excepcionalmente eficiente, documentando *marcato*, *síncopa*, 3-3-2, *arrastre*, *fraseo* e *yumba*. [CILAM](https://cilam.ucr.edu/diagonal/issues/2013/LinkandWendland.pdf)

Para os termos fundamentais, encontrei uma base especialmente apropriada para o modelo em cascata: Open Music Theory para compasso simples, síncope/tresillo, intervalos, escalas, modos e acordes, complementado por *Foundations of Aural Skills* para hemiola 3:2 e a percepção prática da ambiguidade 6/8–3/4. [Viva](https://viva.pressbooks.pub/openmusictheory/chapter/simple-meter-and-time-signatures/)

Os dez itens que eu carregaria primeiro no NotebookLM são **F4-01, F4-02, F5-02, F6-01, F2-01, F2-02, F9-01, F1-01, F7-01 e T-03**. Essa combinação fornece uma espinha dorsal técnica muito melhor que tentar inicialmente maximizar o número de fontes.

Preparei dois arquivos:

- relatorio_fontes_glossario_musical.md[**Relatório completo — Partes A–F**](sandbox:/mnt/data/relatorio_fontes_glossario_musical.md) — inclui resumo executivo, tabela principal, mapa de confusões, divergências, não verificados/descartados e livros pagos recomendados.
- fontes_glossario_musical_notebooklm.csv[**CSV UTF-8 para NotebookLM/automação**](sandbox:/mnt/data/fontes_glossario_musical_notebooklm.csv) — 63 linhas, separado por ponto e vírgula e com as colunas exatamente na estrutura solicitada.
