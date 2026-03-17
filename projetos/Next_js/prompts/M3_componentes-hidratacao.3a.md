<role>
You are an Expert Technical Educator and Presentation Designer.
</role>

<context>
We are creating Module 3 of a Next.js course for beginners. The source material to be used is "The Architect's Blueprint". The focus is the paradigm shift of React Server Components (RSC) vs. Client Components, the `"use client"` directive, and the critical concept of Hydration and Hydration Errors.
</context>

<instructions>
Think step-by-step in English to ensure high semantic density and logical progression, then translate your final output:
1. Analyze the source material regarding the mental model of Server vs. Client components.
2. Define Server Components (the default in Next.js, 0 KB bundle size, direct backend access) using the "Bridge and Factory" analogy[cite: 1218, 1219, 1220, 1221].
3. Define Client Components, explaining when to use the `"use client"` directive (interactivity, React hooks like `useState`, browser APIs) and the architectural recommendation to keep them at the "leaves" of the component tree[cite: 1168, 1175].
4. Detail the concept of "Hydration" and the dreaded "Hydration Error" using the "Lego Manual" analogy. List the most common causes (e.g., time-based discrepancies, using `window` on the server)[cite: 1195, 1196].
5. Structure the output strictly as a slide deck outline. For each slide, provide:
   - **Slide Title**
   - **Visual Content** (3-4 concise bullet points)
   - **Speaker Notes** (Brief script for the presenter)
</instructions>

<constraints>
- Do NOT focus on or explain caching mechanisms here (save that for Module 4).
- Do NOT fill the slides with heavy code blocks; focus on the conceptual mental model and analogies.
- Be highly concise to mitigate the higher token costs associated with Portuguese tokenization.
</constraints>

<output_format>
Ensure your final response is formatted cleanly in Markdown and written entirely in natural, fluent **Brazilian Portuguese (PT-BR)**.
</output_format>