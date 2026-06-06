#!/usr/bin/env python3
"""
Runner diário: pega as próximas N cenas pending de _raw/cenas_master.json e gera:
- obras/{cat}/{obra}/cenas/{slug}.md        — texto recortado da cena (sub-chunk)
- obras/{cat}/{obra}/prompts/{slug}.md      — prompt NotebookLM correspondente

Após cada cena bem-sucedida, atualiza status='done' + done_at no master.

Pensado para rodar via cron (1x por dia). Idempotente: re-execução pula cenas done.

Uso:
  python scripts/05_daily_cenas_runner.py             # padrão: 100 cenas
  python scripts/05_daily_cenas_runner.py --limit 5   # menor lote (teste)
  python scripts/05_daily_cenas_runner.py --dry-run   # mostra o que faria
  python scripts/05_daily_cenas_runner.py --status    # apenas relatório
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASTER_PATH = PROJECT_ROOT / "_raw" / "cenas_master.json"
LOG_PATH = PROJECT_ROOT / "_raw" / "cenas_log.jsonl"


# ---------------------------------------------------------------------------
# Template do prompt — as INSTRUÇÕES ficam em INGLÊS de propósito (paradigma
# "Pense em Inglês": o espaço latente do modelo é mais denso e o seguimento de
# instruções mais robusto em inglês — ver
# /Users/edsonmichalkiewicz/dev/_ref/prompts/engenharia_prompt/analise_comparativa_NLP.md
# §4.1). A camada de raciocínio é desacoplada da camada de apresentação: a SAÍDA
# de áudio deve ser inteiramente em PORTUGUÊS BRASILEIRO (pt-BR). As fontes estão
# em traduções inglesas Oxford/Loeb, então as âncoras de localização do trecho
# ({first_sentence}/{last_sentence}) também permanecem em inglês. O runner
# 07_audio_runner.py reforça isso passando --language pt-BR.
# ---------------------------------------------------------------------------

PROMPT_TEMPLATE = """\
═══════════════════════════════════════════════════════════════════════════════
 AUDIO TITLE — rename the generated audio in NLM Studio to exactly this:

    {audio_title}

 (Final filename on disk: {audio_filename})
═══════════════════════════════════════════════════════════════════════════════

Act as a Senior Humanities Tutor specializing in the formative reading of Aristotle. Your goal is to write a detailed, highly pedagogical study guide (Guia de Estudos) to accompany and support the listener of the deep-dive audio overview of a specific passage from Aristotle's *{obra_en}*.

**Context & Anchoring:**
- **Work:** {obra_en} ({obra_pt}), translated by {translator}.
- **Passage Identifier:** {livro_marker}, {capitulo_marker} (sub-cena {sub_cena_num} of {sub_cena_total}).
- **Audio Position in This Work:** This is audio {audio_in_obra_idx} of {audio_in_obra_total} for *{obra_en}*.

**Task:**
Generate a comprehensive, structured study guide (Guia de Estudos) in Brazilian Portuguese (pt-BR) for the passage below. The guide should be written in a clear, engaging, and didactic tone, aimed at helping a student deeply absorb Aristotle's arguments and relate them to real life.

**Study Guide Structure (MUST be written entirely in BRAZILIAN PORTUGUESE):**

1. **Título Principal:** "Guia de Estudos: {obra_pt} — {livro_marker}, Capítulo {capitulo_marker} (Cena {sub_cena_num}/{sub_cena_total})"
2. **A Pergunta Central (A Pergunta que Ancora a Discussão):** A single clear sentence summarizing the main question or problem Aristotle is addressing in this passage.
3. **Resumo Narrativo do Argumento (Linha de Raciocínio):** A detailed step-by-step walk through Aristotle's logic in plain, accessible language. Explain any technical Greek terms (e.g. *ousia*, *energeia*, *phronesis*, *arete*, *eudaimonia*) that appear in the passage.
4. **O Método em Ação:** Explain the methodological move Aristotle is making here (e.g., dialectical examination of common opinions, division by genus and species, searching for first principles, the four causes, the doctrine of the mean) and why this method is effective for this specific problem.
5. **Do Conceito à Vida (Aplicação Prática):** Describe a concrete modern example (a personal choice, a professional dilemma, or a recurring social situation) that illustrates the practical utility of Aristotle's distinction in this passage.
6. **Para Ruminar (Provocação Reflexiva):** 2-3 thought-provoking questions in Portuguese that encourage the student to reflect on how this passage applies to their own life and decisions.
7. **Ideia-Chave para Levar no Bolso:** A single powerful sentence summarizing the core insight of this passage to keep in mind throughout the day.

**Technical & Linguistic Constraints:**
- **Output Language:** Every single word of the final generated text MUST be in BRAZILIAN PORTUGUESE (pt-BR). Greek terms should be kept in Greek characters or transliterated, followed immediately by their translation/explanation in Portuguese.
- **Tone:** calm, pedagogical, encouraging, and clear. Avoid overly dense academic jargon; prefer clear explanations and intuitive examples.
- **Do not invent doctrine.** Stick strictly to the ideas present in this passage.

**Passage Selection (Focus of this Study Guide):**
The sources uploaded to NotebookLM contain the full text of *{obra_en}*. For this specific guide, focus EXCLUSIVELY on the passage from {livro_marker}, {capitulo_marker}, bounded by:

**Starts at:** "{first_sentence}"
**Ends at:** "{last_sentence}"
"""


def make_prompt(cena: dict) -> str:
    fonte = cena.get("fonte", "")
    translator = fonte.split("-", 1)[-1] if "-" in fonte else fonte or "Oxford"
    return PROMPT_TEMPLATE.format(
        audio_title=cena.get("audio_title", "?"),
        audio_filename=cena.get("audio_filename", "?"),
        obra_en=cena["obra_en"],
        obra_pt=cena["obra_pt"],
        translator=translator,
        livro_marker=cena.get("livro_marker") or f"Book {cena['livro_num']}",
        capitulo_marker=cena.get("capitulo_marker") or f"Chapter {cena['capitulo_num']}",
        sub_cena_num=cena["sub_cena_num"],
        sub_cena_total=cena["sub_cena_total"],
        audio_in_obra_idx=cena["audio_in_obra_idx"],
        audio_in_obra_total=cena["audio_in_obra_total"],
        first_sentence=cena["first_sentence"].replace('"', '\\"'),
        last_sentence=cena["last_sentence"].replace('"', '\\"'),
    )


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    body = text[end + 5:].lstrip("\n")
    return {}, body  # só precisamos do body aqui


def split_into_subcenas(body: str, max_chars: int = 8000,
                        min_to_split: int = 12000) -> list[str]:
    if len(body) <= min_to_split:
        return [body]
    paragraphs = re.split(r"\n\s*\n", body)
    chunks: list[list[str]] = []
    current: list[str] = []
    current_size = 0
    for p in paragraphs:
        p_size = len(p) + 2
        if current_size + p_size > max_chars and current:
            chunks.append(current)
            current = [p]
            current_size = p_size
        else:
            current.append(p)
            current_size += p_size
    if current:
        chunks.append(current)
    return ["\n\n".join(c).strip() + "\n" for c in chunks]


def get_chunk_for_cena(cena: dict) -> str:
    """Re-divide o capítulo para extrair o chunk específico desta sub-cena."""
    cap_path = PROJECT_ROOT / cena["capitulo_path"]
    text = cap_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(text)
    chunks = split_into_subcenas(body)
    idx = cena["sub_cena_num"] - 1
    if idx >= len(chunks):
        raise IndexError(
            f"sub_cena_num {cena['sub_cena_num']} > chunks gerados ({len(chunks)}) "
            f"em {cena['capitulo_path']} — re-rode 04_define_cenas_master.py --force"
        )
    return chunks[idx]


def write_cena_file(cena: dict, chunk_text: str) -> Path:
    path = PROJECT_ROOT / cena["cena_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = (
        "---\n"
        f"cena_id: {cena['cena_id']}\n"
        f"obra_pt: {json.dumps(cena['obra_pt'], ensure_ascii=False)}\n"
        f"obra_en: {json.dumps(cena['obra_en'], ensure_ascii=False)}\n"
        f"categoria: {cena['categoria']}\n"
        f"obra_slug: {cena['obra_slug']}\n"
        f"fonte: {cena['fonte']}\n"
        f"livro_num: {cena['livro_num']}\n"
        f"livro_marker: {json.dumps(cena.get('livro_marker', ''))}\n"
        f"capitulo_num: {cena['capitulo_num']}\n"
        f"capitulo_marker: {json.dumps(cena.get('capitulo_marker', ''))}\n"
        f"sub_cena_num: {cena['sub_cena_num']}\n"
        f"sub_cena_total: {cena['sub_cena_total']}\n"
        f"audio_in_obra_idx: {cena['audio_in_obra_idx']}\n"
        f"audio_in_obra_total: {cena['audio_in_obra_total']}\n"
        f"chars: {len(chunk_text)}\n"
        "---\n\n"
    )
    path.write_text(fm + chunk_text.rstrip() + "\n", encoding="utf-8")
    return path


def write_prompt_file(cena: dict) -> Path:
    path = PROJECT_ROOT / cena["prompt_path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    prompt = make_prompt(cena)
    path.write_text(prompt, encoding="utf-8")
    return path


def append_log(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def print_status(master: dict) -> None:
    from collections import Counter
    cenas = master["cenas"]
    status_count = Counter(c["status"] for c in cenas)
    total = len(cenas)
    done = status_count.get("done", 0)
    pending = status_count.get("pending", 0)
    failed = status_count.get("failed", 0)
    pct = (done / total * 100) if total else 0
    print(f"Total cenas: {total}")
    print(f"  done:    {done:5d}  ({pct:.1f}%)")
    print(f"  pending: {pending:5d}")
    print(f"  failed:  {failed:5d}")
    if pending:
        days = (pending + 99) // 100
        print(f"\nA 100/dia: ~{days} dias até concluir")
        # próximas 5
        nxt = [c for c in cenas if c["status"] == "pending"][:5]
        print("\nPróximas 5 cenas a processar:")
        for c in nxt:
            print(f"  {c['cena_id']}  ({c['chars']} chars)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100,
                        help="Quantas cenas processar nesta execução (default 100).")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true",
                        help="Apenas mostra progresso e sai.")
    parser.add_argument("--regen-prompts", action="store_true",
                        help="Re-renderiza TODOS os arquivos de prompt a partir do "
                             "master usando o template atual, sem mexer no status "
                             "das cenas nem nos arquivos de cena. Usado p.ex. ao "
                             "trocar o idioma do prompt (en → pt-BR).")
    args = parser.parse_args()

    if not MASTER_PATH.exists():
        print(f"ERRO: {MASTER_PATH} não encontrado. Rode 04_define_cenas_master.py primeiro.")
        return 2

    master = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    cenas = master["cenas"]

    if args.status:
        print_status(master)
        return 0

    if args.regen_prompts:
        total = len(cenas)
        print(f"=== Re-renderizando {total} prompts (template atual) ===")
        regen = 0
        missing = 0
        for c in cenas:
            if args.dry_run:
                continue
            try:
                write_prompt_file(c)
                regen += 1
            except KeyError as exc:
                missing += 1
                print(f"  {c.get('cena_id', '?'):60s}  → faltou campo {exc}")
        if args.dry_run:
            print(f"dry-run: re-renderizaria {total} prompts.")
        else:
            print(f"=== Concluído: {regen} prompts reescritos, {missing} com erro ===")
        return 0 if missing == 0 else 1

    pending = [c for c in cenas if c["status"] == "pending"]
    if not pending:
        print("Todas cenas processadas. Nada a fazer.")
        print_status(master)
        return 0

    batch = pending[:args.limit]
    print(f"=== Runner: processando {len(batch)} de {len(pending)} pendentes "
          f"(limit={args.limit}) ===")

    ok = 0
    failed = 0
    started = time.time()
    for i, cena in enumerate(batch, 1):
        prefix = f"[{i:3d}/{len(batch)}] {cena['cena_id']:60s}"
        if args.dry_run:
            print(f"{prefix}  → dry_run ({cena['chars']} chars)")
            continue
        try:
            chunk = get_chunk_for_cena(cena)
            write_cena_file(cena, chunk)
            write_prompt_file(cena)
            cena["status"] = "done"
            cena["done_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            append_log({"ts": cena["done_at"], "cena_id": cena["cena_id"],
                        "status": "ok", "chars": cena["chars"]})
            ok += 1
            print(f"{prefix}  → ok  ({cena['chars']} chars)")
        except Exception as exc:  # noqa: BLE001
            cena["status"] = "failed"
            cena["last_error"] = f"{type(exc).__name__}: {exc}"
            append_log({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "cena_id": cena["cena_id"], "status": "failed",
                        "error": cena["last_error"]})
            failed += 1
            print(f"{prefix}  → FAIL  {exc}")

    if not args.dry_run:
        MASTER_PATH.write_text(json.dumps(master, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    elapsed = time.time() - started
    print()
    print(f"=== Lote concluído em {elapsed:.1f}s — ok={ok}, failed={failed} ===")
    print_status(master)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
