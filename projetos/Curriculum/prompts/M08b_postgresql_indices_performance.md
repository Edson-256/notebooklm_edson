<role>
Act as a Podcast Producer and Technical Storyteller.
</role>
<context>
Critique-format audio for Module 8: PostgreSQL performance tuning. Expert hosts analyze common performance mistakes and how to diagnose them with EXPLAIN ANALYZE.
</context>
<instructions>
Think step-by-step:
1. Present a "before" scenario: a slow query that scans 75,000 pathology reports sequentially.
2. Diagnose it: missing index, no LIMIT, unoptimized JOIN order.
3. Apply fixes one by one, showing the performance improvement at each step.
4. Critique common anti-patterns: over-indexing, premature optimization, ignoring VACUUM.
5. Write an expert analysis script (approx. 3-4 minutes).
</instructions>
<constraints>
- Constructive tone — critique the code, not the developer.
- Flowing paragraphs, not bullets.
</constraints>
<output_format>
Audio format: critique
Ensure your final response is written in natural, spoken Brazilian Portuguese (PT-BR).
</output_format>
