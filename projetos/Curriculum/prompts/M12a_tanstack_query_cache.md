<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 12: TanStack Query (React Query) v5. Covers the server state vs. client state distinction, useQuery for data fetching with automatic caching, useMutation for writes with optimistic updates, query invalidation strategies, and staleTime/gcTime configuration.
</context>
<instructions>
Think step-by-step:
1. Present the core insight: "Server state is someone else's data — it can change without you knowing."
2. Use the "newspaper subscription" analogy: TanStack Query checks for fresh editions (refetching) while keeping today's paper (cache).
3. Cover the query lifecycle: fresh → stale → garbage collected.
4. Show optimistic updates as "assuming success and rolling back if wrong."
5. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Assume the learner completed M11 (Zustand for client state).
- Keep code examples to 5-7 lines.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
