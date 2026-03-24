<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 7: PostgreSQL 16 fundamentals for application developers. Covers relational modeling, schema namespaces (core.*, dermato.*, raw.*), data types (uuid, timestamptz, jsonb), foreign keys across schemas, and pgvector for semantic search with 1536-dimensional embeddings.
</context>
<instructions>
Think step-by-step:
1. Present schemas as "rooms in a building" — each has a purpose, and you reference across rooms via foreign keys.
2. Cover essential data types for medical applications: uuid (PKs), timestamptz (audit trails), jsonb (flexible metadata).
3. Introduce pgvector as "teaching the database to understand meaning, not just text."
4. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Do not cover query optimization or indexing (reserved for M8).
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
