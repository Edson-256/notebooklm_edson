<role>
You are an Expert Technical Educator and Presentation Designer.
</role>

<context>
We are creating Module 4 of a Next.js course for beginners. The source material to be used is "The Architect's Blueprint". The focus is demystifying Data Fetching in Server Components and navigating the Next.js "Caching Labyrinth".
</context>

<instructions>
Think step-by-step in English to ensure high semantic density and logical progression, then translate your final output:
1. Analyze the source material regarding the power of using `fetch()` inside async Server Components (e.g., speed, security, keeping API keys on the server).
2. Break down the caching layers clearly so a beginner can visualize them: Request Memoization (prevents duplicate calls in one request), Data Cache (stores responses across users/requests), and Router Cache (browser-side navigation cache).
3. Address the "stale data" confusion. Explain that aggressive caching is a deliberate performance feature, not a bug, but it requires active management.
4. Provide the standard solutions for cache invalidation (e.g., `revalidatePath` to clear cache manually, or mentioning Next.js 15 un-cached defaults).
5. Structure the output strictly as a slide deck outline. For each slide, provide:
   - **Slide Title**
   - **Visual Content** (3-4 concise bullet points)
   - **Speaker Notes** (Brief script for the presenter)
</instructions>

<constraints>
- Do NOT dive into complex backend setups (like ORMs or database connections); focus purely on the conceptual caching layers and the `fetch()` API.
- Explicitly frame caching as a deliberate performance strategy, avoiding a negative tone about "stale data".
- Be highly concise to mitigate the higher token costs associated with Portuguese tokenization.
</constraints>

<output_format>
Ensure your final response is formatted cleanly in Markdown and written entirely in natural, fluent **Brazilian Portuguese (PT-BR)**.
</output_format>