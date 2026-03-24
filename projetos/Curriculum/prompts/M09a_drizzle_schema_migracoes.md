<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 9: Drizzle ORM introduction. Covers the schema-as-code philosophy, pgSchema for multi-schema support, schemaFilter for safe migrations, column definitions with TypeScript inference, and the drizzle-kit CLI for migrations.
</context>
<instructions>
Think step-by-step:
1. Present the "Drizzle vs Prisma" decision: SQL-like syntax, multi-schema support, smaller bundle.
2. Use the "blueprint" analogy: your TypeScript schema file IS the source of truth.
3. Show pgSchema('dermato') and how schemaFilter prevents accidental drops on core.* tables.
4. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Do not cover advanced queries or joins (reserved for M10).
- Keep schema code snippets to 7-10 lines.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
