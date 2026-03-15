#!/usr/bin/env python3
"""Atualiza tracker.md com base no chapter_index.json"""

import json
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).parent.parent
CHAPTER_INDEX = PROJECT_DIR / "chapter_index.json"
TRACKER = PROJECT_DIR / "tracker.md"


def main():
    with open(CHAPTER_INDEX, encoding="utf-8") as f:
        index = json.load(f)

    chapters = index["chapters"]
    total = len(chapters)
    generated = sum(1 for c in chapters if c["status"] in ("generated", "downloaded", "listened", "completed"))
    listened = sum(1 for c in chapters if c.get("listened"))
    gaps_done = sum(1 for c in chapters if c.get("gaps_identified"))
    pending = sum(1 for c in chapters if c["status"] == "pending")
    errors = sum(1 for c in chapters if c["status"] == "error")

    pct = int(generated / total * 100) if total > 0 else 0
    today = datetime.now().strftime("%Y-%m-%d")

    lines = [
        f"# DeVita CME — Tracker de Progresso\n",
        f"**Atualizado:** {today}  |  **Progresso:** {generated}/{total}  |  **{pct}% concluído**\n",
        "## Resumo\n",
        "| Status | Quantidade |",
        "|--------|------------|",
        f"| Gerado | {generated} |",
        f"| Ouvido | {listened} |",
        f"| Gaps identificados | {gaps_done} |",
        f"| Pendente | {pending} |",
        f"| Erro | {errors} |",
        "",
        "## Todos os Capítulos\n",
        "| # | Título | Status | Gerado em | Ouvido | Gaps |",
        "|---|--------|--------|-----------|--------|------|",
    ]

    for ch in chapters:
        status_icon = {
            "pending": "Pendente",
            "generating": "Gerando...",
            "generated": "Gerado",
            "downloaded": "Baixado",
            "listened": "Ouvido",
            "completed": "Concluído",
            "error": "ERRO",
        }.get(ch["status"], ch["status"])

        gen_date = ch.get("audio_generated_at", "")
        if gen_date:
            gen_date = gen_date[:10]

        listened_mark = "Sim" if ch.get("listened") else "--"
        gaps_mark = "Sim" if ch.get("gaps_identified") else "--"

        lines.append(f"| {ch['chapter_num']} | {ch['title']} | {status_icon} | {gen_date} | {listened_mark} | {gaps_mark} |")

    lines.append("")

    TRACKER.write_text("\n".join(lines), encoding="utf-8")
    print(f"Tracker atualizado: {TRACKER}")
    print(f"  {generated}/{total} gerados ({pct}%)")


if __name__ == "__main__":
    main()
