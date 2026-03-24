<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 10: Advanced Drizzle ORM. Covers relational queries with `db.query`, cross-schema JOINs (dermato.sessao → core.patient), typed query results, transactions, and the repository pattern for organizing database access.
</context>
<instructions>
Think step-by-step:
1. Show how `db.query.sessao.findMany({ with: { patient: true } })` loads related data.
2. Demonstrate cross-schema JOINs and how TypeScript infers the result type automatically.
3. Present the repository pattern as "a clean interface between your app and the database."
4. Structure as slide deck outline with query code in Speaker Notes.
</instructions>
<constraints>
- Assume the learner completed M9 (Drizzle basics).
- Keep query examples to 5-8 lines.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
