#!/usr/bin/env python3
"""
Track and manage Shakespeare audio generation progress.

Usage:
    python3 generate_audios.py status              # Progress summary
    python3 generate_audios.py list [play]          # List pending scenes
    python3 generate_audios.py mark PLAY NUM        # Mark scene as done
    python3 generate_audios.py batch N              # Show next N scenes
    python3 generate_audios.py ref PLAY             # Generate 02_audios_gerados.md
    python3 generate_audios.py prompt PLAY NUM      # Print focus_prompt for a scene
    python3 generate_audios.py daily                # Show today's generation count
"""

import json
import sys
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).parent
QUEUE_PATH = BASE_DIR / "audio_work_queue.json"
PROGRESS_PATH = BASE_DIR / "audio_progress.json"
DAILY_LOG_PATH = BASE_DIR / "audio_daily_log.json"

NOTEBOOK_ID = "62400b1d-e3bd-45d2-8428-d2d8d6b7128d"
BATCH_SIZE = 20  # cenas por execução (sem limite diário, roda 2x/dia)


def load_queue():
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def load_daily_log():
    if not DAILY_LOG_PATH.exists():
        return {}
    with open(DAILY_LOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_daily_log(log):
    with open(DAILY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def get_today_count():
    log = load_daily_log()
    today = date.today().isoformat()
    return log.get(today, 0)


def increment_today():
    log = load_daily_log()
    today = date.today().isoformat()
    log[today] = log.get(today, 0) + 1
    save_daily_log(log)
    return log[today]


def update_progress(queue):
    completed = sum(1 for item in queue if item["status"] == "done")
    triggered = sum(1 for item in queue if item["status"] == "triggered")
    errors = sum(1 for item in queue if item["status"] == "error")
    pending = sum(1 for item in queue if item["status"] == "pending")

    # Find current play (first play with pending scenes)
    current_play = None
    for item in queue:
        if item["status"] == "pending":
            current_play = item["play_dir"]
            break

    progress = {
        "total_scenes": len(queue),
        "completed": completed,
        "triggered": triggered,
        "errors": errors,
        "pending": pending,
        "current_play": current_play,
        "last_updated": datetime.now().isoformat(),
        "notebook_id": NOTEBOOK_ID,
    }

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    return progress


def cmd_status():
    queue = load_queue()
    progress = update_progress(queue)
    today_count = get_today_count()

    print(f"\n📊 Audio Generation Progress")
    print(f"   Total scenes:   {progress['total_scenes']}")
    print(f"   ✅ Completed:   {progress['completed']}")
    print(f"   🔄 Triggered:   {progress['triggered']}")
    print(f"   ❌ Errors:      {progress['errors']}")
    print(f"   ⏳ Pending:     {progress['pending']}")
    print(f"   📖 Current:     {progress['current_play'] or 'All done!'}")
    print(f"   📅 Today:       {today_count}")
    print(f"   🔗 Notebook:    {NOTEBOOK_ID}")

    # Show per-play breakdown
    plays = {}
    for item in queue:
        p = item["play_dir"]
        if p not in plays:
            plays[p] = {"done": 0, "pending": 0, "triggered": 0, "error": 0, "total": 0}
        plays[p][item["status"]] = plays[p].get(item["status"], 0) + 1
        plays[p]["total"] += 1

    print(f"\n   Per-play summary:")
    for play, stats in plays.items():
        if stats["done"] == stats["total"]:
            icon = "✅"
        elif stats["done"] > 0 or stats["triggered"] > 0:
            icon = "🔄"
        else:
            icon = "⏳"
        print(f"     {icon} {play}: {stats['done']}/{stats['total']} done")


def cmd_list(play_filter=None):
    queue = load_queue()
    filtered = [
        item for item in queue
        if item["status"] == "pending"
        and (play_filter is None or item["play_dir"] == play_filter)
    ]

    print(f"\n⏳ Pending scenes{f' for {play_filter}' if play_filter else ''}:")
    current_play = None
    for item in filtered:
        if item["play_dir"] != current_play:
            current_play = item["play_dir"]
            print(f"\n  📖 {current_play} ({item['book_title']})")
        print(f"     Scene {item['scene_number']}: {item['scene_title']}")

    print(f"\n   Total pending: {len(filtered)}")


def cmd_mark(play_dir, scene_num, status="done"):
    queue = load_queue()

    for item in queue:
        if item["play_dir"] == play_dir and item["scene_number"] == str(scene_num):
            old_status = item["status"]
            item["status"] = status
            item["notebook_id"] = NOTEBOOK_ID
            item["completed_at"] = datetime.now().isoformat()
            save_queue(queue)
            update_progress(queue)

            if status == "done" or status == "triggered":
                increment_today()

            print(f"✅ {play_dir} scene {scene_num}: {old_status} → {status}")
            return

    print(f"❌ Scene not found: {play_dir} #{scene_num}")


def cmd_batch(n=6):
    queue = load_queue()
    today_count = get_today_count()

    pending = [item for item in queue if item["status"] == "pending"]

    batch = pending[:n]

    print(f"\n📦 Next {len(batch)} scenes (today so far: {today_count}):")
    for i, item in enumerate(batch, 1):
        print(f"   {i}. {item['play_dir']} | Scene {item['scene_number']}: {item['scene_title']}")
        print(f"      Location: {item.get('location', 'N/A')}")


def cmd_prompt(play_dir, scene_num):
    queue = load_queue()
    for item in queue:
        if item["play_dir"] == play_dir and item["scene_number"] == str(scene_num):
            print(item["focus_prompt"])
            return
    print(f"❌ Scene not found: {play_dir} #{scene_num}")


def cmd_daily():
    log = load_daily_log()
    today = date.today().isoformat()
    count = log.get(today, 0)
    print(f"\n📅 Today ({today}): {count} audios generated (schedule: 2x/day, {BATCH_SIZE}/run)")


def generate_reference_file(play_dir):
    """Generate 02_audios_gerados.md for a specific play."""
    queue = load_queue()
    play_items = [item for item in queue if item["play_dir"] == play_dir]

    if not play_items:
        print(f"❌ No items found for {play_dir}")
        return

    book_title = play_items[0]["book_title"]
    output_path = BASE_DIR / play_dir / "02_audios_gerados.md"

    lines = [
        f"# {book_title} — Áudios Gerados\n",
        f"> **Notebook:** `{NOTEBOOK_ID}`  ",
        f"> **Gerado em:** {datetime.now().strftime('%d/%m/%Y')}  ",
        "> **Metodologia:** Seminário de Filosofia (COF) — Olavo de Carvalho\n",
        "---\n",
        "## Status dos Áudios\n",
        "| # | Cena | Status | Data |",
        "|---|------|--------|------|",
    ]

    for item in play_items:
        status_icon = "✅" if item["status"] == "done" else "❌" if item["status"] == "error" else "🔄" if item["status"] == "triggered" else "⏳"
        dt = item.get("completed_at", "-")
        if dt and dt != "-":
            dt = dt[:10]
        lines.append(f"| {item['scene_number']} | {item['scene_title']} | {status_icon} {item['status']} | {dt} |")

    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"📄 Generated: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_audios.py <command> [args]")
        print("Commands: status, list [play], mark PLAY NUM, batch N, prompt PLAY NUM, daily, ref PLAY")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        cmd_status()
    elif cmd == "list":
        play = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_list(play)
    elif cmd == "mark":
        if len(sys.argv) < 4:
            print("Usage: mark PLAY_DIR SCENE_NUM [STATUS]")
            sys.exit(1)
        status = sys.argv[4] if len(sys.argv) > 4 else "done"
        cmd_mark(sys.argv[2], sys.argv[3], status)
    elif cmd == "batch":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
        cmd_batch(n)
    elif cmd == "prompt":
        if len(sys.argv) < 4:
            print("Usage: prompt PLAY_DIR SCENE_NUM")
            sys.exit(1)
        cmd_prompt(sys.argv[2], sys.argv[3])
    elif cmd == "daily":
        cmd_daily()
    elif cmd == "ref":
        if len(sys.argv) < 3:
            print("Usage: ref PLAY_DIR")
            sys.exit(1)
        generate_reference_file(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
