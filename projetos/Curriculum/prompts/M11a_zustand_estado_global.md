<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 11: Zustand for global state management. Covers the motivation (React Context re-rendering problems), store creation with `create()`, slices pattern for modularity, Immer middleware for immutable updates, and devtools integration.
</context>
<instructions>
Think step-by-step:
1. Present the problem: React Context causes unnecessary re-renders — "everyone in the room hears every conversation."
2. Use the "bulletin board" analogy: Zustand is a shared board where only interested components check for updates.
3. Show the slices pattern: splitting a large store into focused sub-stores.
4. Introduce Immer as "write mutations, get immutability for free."
5. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Do not cover server state (TanStack Query handles that — M12).
- Keep code snippets to 5-7 lines.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
