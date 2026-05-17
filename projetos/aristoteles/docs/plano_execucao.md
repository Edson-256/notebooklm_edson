# Plano de Execução — Leitura Formativa de Aristóteles

> Adaptação do modelo `victor_hugo/notre-dame_de_paris/plano_execucao_notre-dame.md` para o corpus aristotelicum.

## Fase 1 — Aquisição do corpus ✅

**Concluída em 2026-05-16.**

- 33 obras baixadas via `scripts/01_download_corpus.py`
- Manifesto em `_raw/download_manifest.json`
- Índice canônico em `docs/corpus_index.md`

## Fase 2 — Limpeza dos textos brutos (TODO)

**Por que necessária:** Os textos do MIT vêm com cabeçalho da Internet Classics Archive e marcação "Part N" / "BOOK N". Os textos do Archive.org são OCR de DJVU e contêm:
- Página de rosto da biblioteca (Toronto/Oxford) no topo
- Números de página intercalados ao texto
- Caracteres acentuados corrompidos (a tradução é toda em inglês, então acentos são raros)
- Notas de rodapé em grego antigo coladas no texto

**Tarefas:**
1. Para obras do MIT: extrair apenas o corpo após o separador `---` e remover marcações de navegação.
2. Para obras do Archive.org (5 obras): limpar OCR (página de rosto, page numbers, notas em grego).
3. Validar que cada arquivo `.txt` começa com texto efetivo de Aristóteles.

Sugerido criar `scripts/02_clean_raw.py` com pipeline por categoria.

## Fase 3 — Segmentação por livros/capítulos

Cada obra de Aristóteles é dividida em **Livros (Books)** e dentro de cada livro em **Capítulos (Parts/Chapters)**. Algumas obras menores (Categorias, Poética) têm só capítulos.

**Nomenclatura proposta** (igual notre-dame):
- `obras/{categoria}/{obra}/capitulos/L01-C01-<titulo_kebab>.md`
- Para obras de 1 livro só: `obras/{categoria}/{obra}/capitulos/C01-<titulo_kebab>.md`

**Exemplo — Metafísica:**
```
obras/04_metafisica/01_metafisica/capitulos/
├── L01-C01-Sabedoria_e_Experiencia.md
├── L01-C02-Causas_e_Principios.md
├── ...
└── L14-C06-Numeros_e_Formas.md  (14 livros)
```

**Exemplo — Poética (livro único):**
```
obras/07_retorica_poetica/02_poetica/capitulos/
├── C01-Imitacao_Natureza_Poesia.md
├── C02-Generos_da_Imitacao.md
├── ...
```

## Fase 4 — Seleção de cenas e prompts

Mesmo modelo de notre-dame: extrair 1-5 trechos relevantes por capítulo (cenas), e para cada cena criar um prompt para o NotebookLM.

**Nomenclatura:**
- Cenas: `obras/{categoria}/{obra}/cenas/L01-C01-<titulo>_cena001.md`
- Prompts: `obras/{categoria}/{obra}/prompts/L01-C01-<titulo>_prompt001.md`

**Template de prompt base** — adaptar o template de notre-dame, mas:
- Substituir "Notre-Dame de Paris" por nome da obra de Aristóteles
- Idioma: **Inglês** (o áudio NotebookLM deve sair em inglês, dado que o texto base é traduzido para inglês)
- Linha pedagógica: adaptar para filosofia clássica — tutor deve aplicar leitura formativa (não exegese acadêmica)
- Para obras lógicas (Organon): focar na estrutura do argumento, não em "drama"
- Para obras biológicas: focar na observação e classificação aristotélica

Decisão pendente: gravar tudo em inglês (mais material disponível) ou tentar versão PT com obras já traduzidas (apenas Física, Sobre o Céu disponíveis em PT em `obrasdearistoteles.net`, que requer login)?

## Fase 5 — Geração de áudios via NotebookLM

Seguir o padrão de `quo_vadis_runner.py` / `ben_hur_runner.py`:
- Notebook ID: `de324f7f-25ca-438c-96d5-16ff36a2bddc` (Aristóteles, conta pessoal)
- Profile: `default`
- Limite: **20 áudios/dia** (silencioso na CLI nlm — planejar lotes de 18-19)
- "Completed" é prematuro: janela de 10-40min entre status e download viável
- Filenames: usar `.m4a` (não `.mp3`)

**Estimativa de volume:**
Se cada obra gerar ~10 cenas em média (variável: Política tem 8 livros, podem ser 40+ cenas), o total fica em ~330-500 cenas → ~17-25 dias para gerar tudo via NotebookLM.

## Fase 6 — Distribuição

Encadear com o **podcast ecosystem** (`reference_podcast_ecosystem` em MEMORY.md):
- Mac (criação) → dell-server (publicação Caddy + feed RSS) → DROBO (arquivo cold)
- Slug provável: `aristoteles` ou `corpus-aristotelicum`
- Feed: `https://edson:SENHA@dell-server.tail3f4f14.ts.net/aristoteles/feed.xml`

## Riscos / TODOs

- [ ] Validar que Notebook ID `de324f7f-25ca-438c-96d5-16ff36a2bddc` ainda existe e pertence à conta correta
- [ ] Decidir EN vs PT para o áudio
- [ ] Definir critério de seleção de cenas (1-5 por capítulo? por densidade conceitual?)
- [ ] Estabelecer ordem de execução por categoria (sugerido: Poética/Retórica primeiro como aquecimento, depois Ética → Política → Metafísica → Organon → Física/Biologia)
- [ ] Limpar OCR dos 5 textos Archive.org antes de segmentar
