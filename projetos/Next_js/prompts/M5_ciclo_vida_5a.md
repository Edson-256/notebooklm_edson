<role>
You are an Expert Technical Educator and Presentation Designer.
</role>

<context>
We are creating Module 5 of a Next.js course for beginners. The source material to be used is "The Architect's Blueprint" and related Next.js documentation. The focus is the underlying mechanics: CLI Commands (`dev`, `build`, `start`), the SWC compiler, and a high-level overview of the Node.js process lifecycle.
</context>

<instructions>
Think step-by-step in English to ensure high semantic density and logical progression, then translate your final output:
1. Analyze the source material regarding what happens "under the hood" when a developer runs Next.js.
2. Clearly contrast the three main CLI commands: `next dev` (local server, Fast Refresh), `next build` (production optimization, HTML generation, caching), and `next start` (serving the optimized production build).
3. Explain the compiler evolution: the shift from Babel (JavaScript) to SWC (Rust), highlighting the massive speed increase (17x faster) and parallel processing.
4. Briefly introduce the Node.js process lifecycle (V8 engine initialization) and the concept of "Graceful Shutdown", framing it practically so a beginner understands why processes shouldn't just be "killed".
5. Structure the output strictly as a slide deck outline. For each slide, provide:
   - **Slide Title**
   - **Visual Content** (3-4 concise bullet points)
   - **Speaker Notes** (Brief script for the presenter)
</instructions>

<constraints>
- Do NOT dive into deep C++ code, raw Node.js internals, or complex custom server implementations; keep it high-level and focused on the developer experience.
- Explicitly frame `next build` as the critical step for testing and catching errors before deploying to users.
- Be highly concise to mitigate the higher token costs associated with Portuguese tokenization.
</constraints>

<output_format>
Ensure your final response is formatted cleanly in Markdown and written entirely in natural, fluent **Brazilian Portuguese (PT-BR)**.
</output_format>