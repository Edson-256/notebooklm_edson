<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 8: PostgreSQL performance. Covers B-tree and GIN indexes, EXPLAIN ANALYZE for query plans, Common Table Expressions (CTEs) for readable complex queries, HNSW indexes for pgvector, and vacuuming/maintenance basics.
</context>
<instructions>
Think step-by-step:
1. Present indexes as "the index at the back of a textbook" — without it, you read every page.
2. Show EXPLAIN ANALYZE as "an X-ray of your query" — reveals sequential scans, index usage, and cost.
3. Introduce CTEs as "naming your intermediate results" for readability.
4. Structure as slide deck outline with example EXPLAIN output in Speaker Notes.
</instructions>
<constraints>
- Assume the learner completed M7 (PostgreSQL basics).
- Keep query examples to 5-7 lines.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
