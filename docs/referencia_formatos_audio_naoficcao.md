# Referência — Leque de formatos de áudio para não-ficção (multiperspectiva)

> **Status:** documento de **referência reutilizável** para futuros projetos de áudio
> educacional de **não-ficção** (NotebookLM). Surgiu do projeto Northrop Frye
> (crítica literária), mas o modelo é geral. Não confundir com a skill
> `leitura-formativa` (que é para **ficção** — "educação da imaginação").
> Base conceitual: `leitura_nao_ficcional/leitura_nao_ficcional_COF.md` (método COF).
> Criado em 2026-06-08.

## Princípio pedagógico

Em vez de **um** áudio por capítulo, produzir **vários áudios complementares** sobre o
mesmo trecho — cada um executando uma **operação cognitiva distinta**. Ganhos:

- **Recuperação variada + múltiplas perspectivas** fixam melhor que uma exposição única.
- **Palatável para iniciante:** uma escada de profundidade crescente evita afogar quem
  está começando no assunto.
- **Persistência do conhecimento:** revisitar o mesmo conteúdo de ângulos diferentes
  reforça a retenção (efeito de repetição espaçada/variada).

## O leque (6 formatos)

Cada formato mapeia uma operação do framework de leitura não-ficcional do COF.

| # | Formato | O que faz | Operação COF | Duração | Nível |
|---|---------|-----------|--------------|---------|-------|
| **A** | **Pórtico** (orientação) | O mapa: o que é, por que importa, *status quaestionis* em linguagem simples, termos que vão aparecer | Inspecional (Adler) | 6–10 min | iniciante |
| **B** | **Reconstrução Interna** (aula) | Habita o sistema do autor por dentro: reconstrói o argumento com caridade, define os termos técnicos, segue a arquitetura — **sem julgar ainda** | §3 + analítico | 18–28 min | núcleo |
| **C** | **A Arena** (fichamento dialético) | Campo de forças: o que a época dizia (*Videtur quod*) → onde travou (*Sed contra*) → o salto do autor (*Respondeo*) | Status quaestionis | 12–18 min | médio |
| **D** | **O Filtro** (conceito × símbolo) | Teste-mestre: as categorias do autor captam um **nexo real** (*conceptus*) ou são engenharia autorreferente? Objeção vs. defesa caridosa, em tensão | Operação-mestra | 12–18 min | médio/avançado |
| **E** | **Meditatio** (confronto) | Confronta a teoria com a experiência real de leitura/vida — reflexivo, provocativo | §3 meditatio | 10–15 min | reflexivo |
| **F** | **Léxico** (glossário) | Episódio curto definindo os termos que o autor redefine | Precisão semântica | 4–7 min | apoio |

### Eixo ortogonal — estilo de voz
O **Deep Dive de 2 vozes** (nativo do NotebookLM) é naturalmente palatável para iniciante
e ótimo para ouvir no carro; serve bem para **A, C, D**. O **B** (aula) pede voz expositiva
mais linear. Variar o estilo de propósito é outra fonte de "perspectiva diferente".

## Estratégia de empilhamento (2+ áudios por capítulo)

- **Stack mínimo (padrão, maioria dos capítulos):** **A → B → D**
  (orienta → reconstrói → testa criticamente). Três passagens, profundidade crescente.
- **Capítulos densos:** + **C** (Arena) + **E** (Meditatio) + **F** (Léxico).
- **Obra de entrada / leve:** **A + Diálogo + E** — menos reconstrução pesada.

## Como atribuir formatos por obra (matriz)

Nem toda obra recebe todos os formatos. Declarar por projeto/obra qual stack se aplica,
conforme a densidade e o modelo dominante. Exemplo (projeto Frye):

| Obra | Stack |
|---|---|
| The Educated Imagination (entrada) | A · Diálogo COF×autor · E |
| Anatomy of Criticism (o sistema) | A · B · C · D · E · F (completo) |
| Fearful Symmetry (gênese via Blake) | A · B (camada dupla) · D |
| Fools of Time (aplicado) | A · B · D · E (meditatio forte) |
| Creation and Recreation (pórtico) | A · B · D · §2 (antropologia) |
| The Great Code (ápice teológico) | A · B · C · D(máx) · níveis de significado · E |
| Notebooks (oficina genética) | formato próprio "laboratório", em paralelo com a obra-mãe |

## Notas de aplicação
- **Idioma:** por padrão prompts em inglês, saída em pt-BR (regra global). Confirmar por projeto.
- **Cada formato = um template de prompt próprio** (a construir no projeto específico).
- **Operação-mestra transversal:** o filtro **conceito vs. símbolo autojustificativo** atravessa
  todos os formatos — é o eixo de valor da leitura não-ficcional pelo COF.
- Relacionado: `leitura_nao_ficcional/leitura_nao_ficcional_COF.md`,
  `projetos/critica-literaria/frye/` (os 4 modelos de leitura de Frye).
