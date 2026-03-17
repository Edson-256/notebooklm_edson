# Currículo: Stack Completa para Aplicações Médicas Full-Stack

## Nível Básico (Fundamentos)

| Módulo | Tecnologia | Título | Formato Áudio |
|--------|-----------|--------|---------------|
| M01 | TypeScript | Tipos, Interfaces e o Poder da Tipagem Estática | deep_dive |
| M02 | TypeScript | Generics, Utility Types e Patterns para React | deep_dive |
| M03 | Tailwind CSS | Utility-First: Estilização Rápida e Responsiva | brief |
| M04 | Tailwind CSS | Design Tokens, Temas Customizados e Dark Mode | deep_dive |
| M05 | shadcn/ui | Componentes Acessíveis: Filosofia Copy-Paste vs NPM | debate |
| M06 | shadcn/ui | Customização de Componentes e Sistema de Design | deep_dive |

## Nível Intermediário (Dados e Estado)

| Módulo | Tecnologia | Título | Formato Áudio |
|--------|-----------|--------|---------------|
| M07 | PostgreSQL 16 | Modelagem Relacional, Schemas e pgvector | deep_dive |
| M08 | PostgreSQL 16 | Índices, Performance e CTEs | critique |
| M09 | Drizzle ORM | Schema-as-Code: Multi-Schema e Migrações | debate |
| M10 | Drizzle ORM | Queries Relacionais, Joins Cross-Schema e Repositório | deep_dive |
| M11 | Zustand | Estado Global Simples: Stores, Slices e Immer | brief |
| M12 | TanStack Query | Server State: Cache, Revalidação e Mutações Otimistas | deep_dive |
| M13 | React Hook Form + Zod | Formulários Performáticos com Validação Type-Safe | deep_dive |

## Nível Avançado (Infraestrutura, Autenticação e Interação)

| Módulo | Tecnologia | Título | Formato Áudio |
|--------|-----------|--------|---------------|
| M14 | NextAuth.js | Autenticação com Credentials Provider e Sessões | deep_dive |
| M15 | Tailscale | VPN Mesh: Rede Zero-Trust sem Exposição Pública | brief |
| M16 | Docker | Containers, Compose e Ambientes Reprodutíveis | deep_dive |
| M17 | dnd-kit | Drag-and-Drop Acessível e Planejamento Cirúrgico | deep_dive |
| M18 | HTML Overlay | Anotações sobre Imagens: Pins, SVG e react-konva | critique |

## Fluxo Pedagógico

```
Básico (M01-M06): Linguagem → Estilo → Componentes
     ↓
Intermediário (M07-M13): Banco → ORM → Estado → Formulários
     ↓
Avançado (M14-M18): Auth → Rede → Infra → Interação Avançada
```

## Convenção de Arquivos

- `M[XX]a_*.md` → Prompt para geração de **slides/apresentação**
- `M[XX]b_*.md` → Prompt para geração de **áudio educativo**

## Formatos de Áudio Utilizados

| Formato | Módulos | Justificativa |
|---------|---------|---------------|
| `deep_dive` | M01, M02, M04, M06, M07, M10, M12, M13, M14, M16, M17 | Temas densos que exigem explicação detalhada |
| `brief` | M03, M11, M15 | Conceitos diretos, melhor absorvidos rapidamente |
| `debate` | M05, M09 | Decisões arquiteturais com trade-offs reais |
| `critique` | M08, M18 | Análise comparativa de abordagens e anti-patterns |
