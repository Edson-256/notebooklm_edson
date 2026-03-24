<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 14: NextAuth.js v5 for authentication. Covers the authentication vs. authorization distinction, the Credentials provider for username/password, session management (JWT vs. database sessions), middleware-based route protection, and integration with Tailscale VPN for network-level security.
</context>
<instructions>
Think step-by-step:
1. Present authentication as "proving who you are" vs. authorization as "proving what you can do."
2. Use the "hospital badge" analogy: NextAuth issues badges (sessions) that grant access to different areas.
3. Cover the Credentials provider flow: form → API route → verify → session cookie.
4. Show middleware-based protection as "a guard at every door."
5. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Do not cover OAuth/social providers (not used in this project).
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
