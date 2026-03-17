<role>
Act as an Expert Technical Educator and Presentation Designer.
</role>
<context>
Module 15: Tailscale VPN for secure networking. Covers the zero-trust networking model, WireGuard protocol underneath, mesh topology (every device connects directly), ACLs for access control, and the practical setup for connecting a local dev machine, application server, and database server.
</context>
<instructions>
Think step-by-step:
1. Present the problem: traditional VPNs create a single point of entry — once inside, you're trusted everywhere.
2. Use the "private telephone line" analogy: Tailscale gives each device-pair their own encrypted line.
3. Cover the three-server setup: Dell (dev) ↔ Xeon (app) ↔ VPS (database), all connected via Tailscale.
4. Explain ACLs as "per-device firewall rules in a single JSON file."
5. Structure as slide deck outline (Slide Title, Bullet Points, Speaker Notes).
</instructions>
<constraints>
- Do not cover MagicDNS or Tailscale SSH in detail — focus on core VPN mesh concepts.
- Be concise to mitigate token costs.
</constraints>
<output_format>
Ensure your final response is formatted in Markdown and written in fluent, concise Brazilian Portuguese (PT-BR).
</output_format>
