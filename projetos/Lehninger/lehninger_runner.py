#!/usr/bin/env python3
"""
Lehninger Biochemistry 8th ed — Audio & Slides Generator
Fire-and-forget audio generation + synchronized slide outline prompts.

Usage:
    # Phase 1: Create audios (fire-and-forget)
    python3 lehninger_runner.py --max-sections 10
    python3 lehninger_runner.py --sections 12.4,12.5,12.9
    python3 lehninger_runner.py --chapter 12
    python3 lehninger_runner.py --priority high --max-sections 20

    # Phase 2: Download ready audios
    python3 lehninger_runner.py --download

    # Generate slide prompts (synced with audio)
    python3 lehninger_runner.py --slides
    python3 lehninger_runner.py --slides --sections 12.4,12.5

    # Utilities
    python3 lehninger_runner.py --status
    python3 lehninger_runner.py --dry-run --max-sections 5
    python3 lehninger_runner.py --retry-failed
"""

import argparse
import json
import logging
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# === Constants ===
PROJECT_DIR = Path(__file__).parent
SECTION_INDEX = PROJECT_DIR / "section_index.json"
AUDIO_DIR = PROJECT_DIR / "audio"
SLIDES_DIR = PROJECT_DIR / "slides"
LOGS_DIR = PROJECT_DIR / "logs"
PROMPTS_DIR = PROJECT_DIR / "prompts"

NOTEBOOK_ID = "aa1d538c-3c72-41ad-a10d-239e41c622f5"
PROFILE = "profissional"
LANGUAGE = "pt-BR"
INTERVAL_SECONDS = 120
NLM = str(Path.home() / ".local" / "bin" / "nlm")

AUDIO_FORMAT_MAP = {
    "deep_dive": {"nlm_format": "deep_dive", "length": "long"},
    "brief": {"nlm_format": "brief", "length": "default"},
    "critique": {"nlm_format": "critique", "length": "long"},
    "debate": {"nlm_format": "debate", "length": "long"},
}

AUDIO_STRUCTURE_DESCRIPTIONS = {
    "deep_dive": """1. FOUNDATION (2-3 min): Baseline knowledge from 1995
2. CORE MECHANISMS (8-10 min): Key biochemical mechanisms with clinical analogies
3. WHAT CHANGED (5-7 min): Discoveries and new paradigms since 1995
4. ONCOLOGY BRIDGE (5-7 min): Connections to modern oncology
5. CLINICAL PEARLS (2-3 min): 3-5 actionable insights
6. GAPS TO EXPLORE (1-2 min): Points for deeper study""",
    "brief": """1. ESSENTIALS (3-4 min): 5-7 core concepts
2. QUICK UPDATE (2-3 min): Changes since 1995 with clinical impact
3. CLINICAL RELEVANCE (2-3 min): Connection to oncology practice
4. KEY TAKEAWAYS (1 min): Mental summary""",
    "critique": """1. THE 1995 PARADIGM (3-4 min): What was known and believed
2. THE REVOLUTION (8-10 min): Key breakthroughs and new techniques
3. CRITICAL ANALYSIS (5-7 min): What was wrong or incomplete
4. MODERN ONCOLOGY IMPACT (3-5 min): Impact on cancer care
5. WHAT'S STILL EVOLVING (2 min): Active research frontiers""",
    "debate": """1. FRAMING THE DEBATE (2-3 min): Central tension or question
2. MOLECULAR PERSPECTIVE (5-7 min): Mechanistic argument
3. CLINICAL PERSPECTIVE (5-7 min): Bedside/translational view
4. SYNTHESIS (3-5 min): Integrated understanding
5. OPEN QUESTIONS (2 min): Unresolved tensions""",
}

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("lehninger")


# === Index Management ===
def load_index() -> dict:
    with open(SECTION_INDEX) as f:
        return json.load(f)


def save_index(data: dict):
    with open(SECTION_INDEX, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info("Index saved.")


# === Prompt Building ===
def load_audio_template(audio_format: str) -> str:
    template_path = PROMPTS_DIR / "audio_templates" / f"{audio_format}.md"
    if not template_path.exists():
        log.error(f"Audio template not found: {template_path}")
        sys.exit(1)
    return template_path.read_text()


def load_slide_template() -> str:
    template_path = PROMPTS_DIR / "slide_template.md"
    if not template_path.exists():
        log.error(f"Slide template not found: {template_path}")
        sys.exit(1)
    return template_path.read_text()


def load_section_context(section_id: str) -> str:
    """Load section-specific context from prompts/sections/s{id}_*.txt"""
    sections_dir = PROMPTS_DIR / "sections"
    matches = list(sections_dir.glob(f"s{section_id}_*.txt"))
    if matches:
        return matches[0].read_text().strip()
    return ""


def build_audio_prompt(section: dict, chapters: dict) -> str:
    """Build the --focus prompt for nlm create audio (max 2500 chars)."""
    template = load_audio_template(section["audio_format"])
    chapter_title = chapters.get(str(section["chapter"]), "")
    section_context = load_section_context(section["id"])

    prompt = template.replace("{{SECTION_ID}}", section["id"])
    prompt = prompt.replace("{{SECTION_TITLE}}", section["section_title"])
    prompt = prompt.replace("{{CHAPTER_NUM}}", str(section["chapter"]))
    prompt = prompt.replace("{{CHAPTER_TITLE}}", chapter_title)
    prompt = prompt.replace("{{SECTION_SPECIFIC_CONTEXT}}", section_context)

    # Enforce 2500 char limit
    if len(prompt) > 2500:
        prompt = prompt[:2497] + "..."
        log.warning(f"Prompt truncated for {section['id']} ({len(prompt)} chars)")

    return prompt


def build_slide_prompt(section: dict, chapters: dict) -> str:
    """Build the slide outline prompt synchronized with audio structure."""
    template = load_slide_template()
    chapter_title = chapters.get(str(section["chapter"]), "")
    audio_format = section["audio_format"]
    structure_desc = AUDIO_STRUCTURE_DESCRIPTIONS.get(audio_format, "")

    prompt = template.replace("{{SECTION_ID}}", section["id"])
    prompt = prompt.replace("{{SECTION_TITLE}}", section["section_title"])
    prompt = prompt.replace("{{CHAPTER_NUM}}", str(section["chapter"]))
    prompt = prompt.replace("{{CHAPTER_TITLE}}", chapter_title)
    prompt = prompt.replace("{{AUDIO_FORMAT}}", audio_format)
    prompt = prompt.replace("{{AUDIO_STRUCTURE_DESCRIPTION}}", structure_desc)
    section_context = load_section_context(section["id"])
    prompt = prompt.replace("{{SECTION_SPECIFIC_CONTEXT}}", section_context)

    return prompt


# === Filename Generation ===
def slugify(text: str, max_len: int = 30) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text[:max_len].rstrip("_")


def audio_filename(section: dict) -> str:
    """Generate audio filename: mk_leh_XX.Y_slug.m4a"""
    slug = slugify(section["section_title"])
    return f"mk_leh_{section['id']}_{slug}.m4a"


def slide_filename(section: dict) -> str:
    """Generate slide filename: mk_leh_XX.Y_slug_slides.md"""
    slug = slugify(section["section_title"])
    return f"mk_leh_{section['id']}_{slug}_slides.md"


# === Audio Creation (Phase 1) ===
def create_audio(section: dict, chapters: dict, dry_run: bool = False) -> bool:
    """Fire-and-forget: create audio via nlm CLI."""
    prompt = build_audio_prompt(section, chapters)
    fmt_config = AUDIO_FORMAT_MAP[section["audio_format"]]

    cmd = [
        NLM, "create", "audio", NOTEBOOK_ID,
        "--format", fmt_config["nlm_format"],
        "--language", LANGUAGE,
        "--length", fmt_config["length"],
        "--focus", prompt,
        "--source-ids", section["source_id"],
        "--profile", PROFILE,
        "--confirm",
    ]

    log.info(
        f"[{section['id']}] {section['section_title']} "
        f"(format={section['audio_format']}, relevance={section['oncology_relevance']})"
    )

    if dry_run:
        log.info(f"  [DRY-RUN] Would create audio ({fmt_config['nlm_format']}, {fmt_config['length']})")
        log.info(f"  [DRY-RUN] Prompt length: {len(prompt)} chars")
        return True

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            log.error(f"  nlm create failed: {result.stderr.strip()}")
            section["audio_status"] = "failed"
            return False

        # Parse artifact_id from output
        output = result.stdout.strip()
        artifact_id = None
        for line in output.split("\n"):
            if "artifact" in line.lower() and ("id" in line.lower() or ":" in line):
                # Try to extract UUID
                uuid_match = re.search(
                    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                    line,
                )
                if uuid_match:
                    artifact_id = uuid_match.group()
                    break

        if not artifact_id:
            # Try whole output for UUID
            uuid_match = re.search(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                output,
            )
            if uuid_match:
                artifact_id = uuid_match.group()

        section["audio_artifact_id"] = artifact_id
        section["audio_status"] = "created"
        section["audio_created_at"] = datetime.now().isoformat()
        section["audio_file"] = audio_filename(section)
        log.info(f"  Created! artifact_id={artifact_id}")
        return True

    except subprocess.TimeoutExpired:
        log.error(f"  Timeout creating audio for {section['id']}")
        section["audio_status"] = "failed"
        return False
    except Exception as e:
        log.error(f"  Error: {e}")
        section["audio_status"] = "failed"
        return False


# === Audio Download (Phase 2) ===
def download_audios(data: dict):
    """Check studio status and download completed audios."""
    AUDIO_DIR.mkdir(exist_ok=True)

    # Get studio status
    log.info("Fetching studio status...")
    try:
        result = subprocess.run(
            [NLM, "studio", "status", NOTEBOOK_ID, "--json", "--profile", PROFILE],
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            log.error(f"Studio status failed: {result.stderr.strip()}")
            return
        studio_data = json.loads(result.stdout)
    except Exception as e:
        log.error(f"Failed to get studio status: {e}")
        return

    # Build artifact_id -> status map
    artifact_status = {}
    if isinstance(studio_data, list):
        for item in studio_data:
            aid = item.get("id") or item.get("artifact_id")
            status = item.get("status", "unknown")
            if aid:
                artifact_status[aid] = status

    # Process sections needing download
    downloaded = 0
    failed = 0
    still_processing = 0

    for section in data["sections"]:
        if section["audio_status"] != "created":
            continue

        artifact_id = section.get("audio_artifact_id")
        if not artifact_id:
            log.warning(f"[{section['id']}] No artifact_id, skipping")
            continue

        server_status = artifact_status.get(artifact_id, "not_found")

        if server_status == "completed":
            output_path = AUDIO_DIR / audio_filename(section)
            log.info(f"[{section['id']}] Downloading...")

            try:
                dl_result = subprocess.run(
                    [
                        NLM, "download", "audio", NOTEBOOK_ID,
                        "--id", artifact_id,
                        "--output", str(output_path),
                        "--no-progress",
                    ],
                    capture_output=True, text=True, timeout=120,
                )

                if dl_result.returncode == 0 and output_path.exists():
                    section["audio_status"] = "downloaded"
                    section["audio_file"] = output_path.name
                    section["audio_downloaded_at"] = datetime.now().isoformat()
                    section["audio_size_bytes"] = output_path.stat().st_size
                    downloaded += 1
                    log.info(
                        f"  Downloaded: {output_path.name} "
                        f"({section['audio_size_bytes'] / 1024 / 1024:.1f} MB)"
                    )
                else:
                    section["audio_status"] = "download_failed"
                    failed += 1
                    log.error(f"  Download failed: {dl_result.stderr.strip()}")

            except Exception as e:
                section["audio_status"] = "download_failed"
                failed += 1
                log.error(f"  Download error: {e}")

        elif server_status in ("in_progress", "processing", "pending"):
            still_processing += 1
            log.info(f"[{section['id']}] Still processing on server...")

        elif server_status in ("failed", "error"):
            section["audio_status"] = "server_failed"
            failed += 1
            log.warning(f"[{section['id']}] Server failed to generate audio")

        elif server_status == "not_found":
            log.warning(f"[{section['id']}] Artifact not found in studio (expired?)")

    save_index(data)
    log.info(
        f"\nDownload summary: {downloaded} downloaded, "
        f"{failed} failed, {still_processing} still processing"
    )


# === Slide Generation ===
def generate_slides(data: dict, section_ids: list[str] | None = None, dry_run: bool = False):
    """Generate synchronized slide prompt files."""
    SLIDES_DIR.mkdir(exist_ok=True)
    chapters = data["chapters"]
    generated = 0

    for section in data["sections"]:
        if section_ids and section["id"] not in section_ids:
            continue
        if section["slide_status"] == "generated" and not dry_run:
            continue

        prompt = build_slide_prompt(section, chapters)
        filename = slide_filename(section)
        output_path = SLIDES_DIR / filename

        if dry_run:
            log.info(f"[{section['id']}] Would generate slide prompt: {filename}")
            continue

        output_path.write_text(prompt, encoding="utf-8")
        section["slide_status"] = "generated"
        section["slide_file"] = filename
        generated += 1
        log.info(f"[{section['id']}] Slide prompt: {filename}")

    if not dry_run:
        save_index(data)
    log.info(f"\nSlide prompts generated: {generated}")


# === Status Report ===
def show_status(data: dict):
    """Print a summary of audio and slide status."""
    audio_counts = {}
    slide_counts = {}
    format_counts = {}
    relevance_counts = {"high": 0, "medium": 0, "low": 0}

    for s in data["sections"]:
        audio_counts[s["audio_status"]] = audio_counts.get(s["audio_status"], 0) + 1
        slide_counts[s["slide_status"]] = slide_counts.get(s["slide_status"], 0) + 1
        fmt = s["audio_format"]
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
        rel = s.get("oncology_relevance", "medium")
        relevance_counts[rel] = relevance_counts.get(rel, 0) + 1

    total = len(data["sections"])
    print(f"\n{'='*60}")
    print(f"  LEHNINGER 8ed — Status Report ({total} sections)")
    print(f"{'='*60}")

    print(f"\n  Audio Formats:")
    for fmt, count in sorted(format_counts.items()):
        print(f"    {fmt:12s}: {count:3d}")

    print(f"\n  Oncology Relevance:")
    for rel in ["high", "medium", "low"]:
        print(f"    {rel:12s}: {relevance_counts[rel]:3d}")

    print(f"\n  Audio Status:")
    for status, count in sorted(audio_counts.items()):
        print(f"    {status:16s}: {count:3d}")

    print(f"\n  Slide Status:")
    for status, count in sorted(slide_counts.items()):
        print(f"    {status:16s}: {count:3d}")

    # Per-chapter breakdown
    print(f"\n  Per Chapter:")
    chapters = data["chapters"]
    for ch_num in sorted(chapters.keys(), key=int):
        ch_sections = [s for s in data["sections"] if s["chapter"] == int(ch_num)]
        audio_done = sum(1 for s in ch_sections if s["audio_status"] == "downloaded")
        total_ch = len(ch_sections)
        print(f"    Ch {ch_num:>2s} ({total_ch} sections): {audio_done}/{total_ch} audios | {chapters[ch_num]}")

    print()


# === Filter Sections ===
def filter_sections(
    data: dict,
    section_ids: list[str] | None = None,
    chapter: int | None = None,
    priority: str | None = None,
    format_filter: str | None = None,
    retry_failed: bool = False,
    max_sections: int | None = None,
) -> list[dict]:
    """Filter and return sections to process."""
    sections = data["sections"]

    if section_ids:
        sections = [s for s in sections if s["id"] in section_ids]
    elif chapter:
        sections = [s for s in sections if s["chapter"] == chapter]
    else:
        # Only pending or retry-failed
        valid_statuses = {"pending"}
        if retry_failed:
            valid_statuses.update({"failed", "server_failed", "download_failed"})
        sections = [s for s in sections if s["audio_status"] in valid_statuses]

    if priority:
        sections = [s for s in sections if s.get("oncology_relevance") == priority]

    if format_filter:
        sections = [s for s in sections if s["audio_format"] == format_filter]

    # Sort: high relevance first, then by section id
    relevance_order = {"high": 0, "medium": 1, "low": 2}
    sections.sort(key=lambda s: (relevance_order.get(s.get("oncology_relevance", "medium"), 1), s["id"]))

    if max_sections:
        sections = sections[:max_sections]

    return sections


# === Main ===
def main():
    parser = argparse.ArgumentParser(
        description="Lehninger 8ed Audio & Slides Generator"
    )
    parser.add_argument("--max-sections", type=int, help="Max sections to process")
    parser.add_argument("--sections", help="Comma-separated section IDs (e.g. 12.4,12.5)")
    parser.add_argument("--chapter", type=int, help="Process all sections of a chapter")
    parser.add_argument("--priority", choices=["high", "medium", "low"], help="Filter by oncology relevance")
    parser.add_argument("--format-filter", choices=["deep_dive", "brief", "critique", "debate"], help="Filter by audio format")
    parser.add_argument("--download", action="store_true", help="Phase 2: download ready audios")
    parser.add_argument("--slides", action="store_true", help="Generate slide prompt files")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--retry-failed", action="store_true", help="Retry failed sections")
    parser.add_argument("--status", action="store_true", help="Show status report")
    args = parser.parse_args()

    # Load index
    data = load_index()

    # Status report
    if args.status:
        show_status(data)
        return

    # Download mode
    if args.download:
        download_audios(data)
        return

    # Parse section IDs
    section_ids = None
    if args.sections:
        section_ids = [s.strip() for s in args.sections.split(",")]

    # Slide generation mode
    if args.slides:
        generate_slides(data, section_ids, args.dry_run)
        return

    # Audio creation mode (default)
    sections = filter_sections(
        data,
        section_ids=section_ids,
        chapter=args.chapter,
        priority=args.priority,
        format_filter=args.format_filter,
        retry_failed=args.retry_failed,
        max_sections=args.max_sections,
    )

    if not sections:
        log.info("No sections to process.")
        show_status(data)
        return

    log.info(f"Processing {len(sections)} sections...")
    if args.dry_run:
        log.info("[DRY-RUN MODE]")

    # Ensure output dirs
    AUDIO_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # Session log
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_log = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "mode": "dry_run" if args.dry_run else "create",
        "sections_planned": [s["id"] for s in sections],
        "results": [],
    }

    success = 0
    failed = 0

    try:
        for i, section in enumerate(sections):
            log.info(f"\n--- [{i+1}/{len(sections)}] ---")

            if not args.dry_run:
                section["audio_status"] = "generating"
                save_index(data)

            ok = create_audio(section, data["chapters"], dry_run=args.dry_run)

            session_log["results"].append({
                "section_id": section["id"],
                "success": ok,
                "status": section["audio_status"],
            })

            if ok:
                success += 1
            else:
                failed += 1

            if not args.dry_run:
                save_index(data)

            # Wait between creations (except last or dry-run)
            if not args.dry_run and i < len(sections) - 1:
                log.info(f"  Waiting {INTERVAL_SECONDS}s before next...")
                time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        log.info("\n\nInterrupted by user. Progress saved.")

    # Save session log
    session_log["finished_at"] = datetime.now().isoformat()
    session_log["success"] = success
    session_log["failed"] = failed

    log_file = LOGS_DIR / f"session_{session_id}.json"
    if not args.dry_run:
        with open(log_file, "w") as f:
            json.dump(session_log, f, indent=2, ensure_ascii=False)

    log.info(f"\n{'='*40}")
    log.info(f"Done: {success} success, {failed} failed")
    if not args.dry_run:
        log.info(f"Log: {log_file}")
    log.info(f"{'='*40}")


if __name__ == "__main__":
    main()
