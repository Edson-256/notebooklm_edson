#!/usr/bin/env python3
"""
Download all Shakespeare works individually from Project Gutenberg.
Each play/poem is downloaded as a complete, standalone text from its own ebook page.
"""

import urllib.request
import os
import time
from pathlib import Path

BACKUP_DIR = Path(__file__).parent

# Map: (Gutenberg ebook number, output filename)
# Using the 1500-series where available (recommended by Gutenberg for everyday reading)
# Falls back to other editions when 1500-series doesn't have a specific work
WORKS = [
    # Plays
    (1529, "All's Well That Ends Well.md"),
    (1534, "Antony and Cleopatra.md"),
    (1523, "As You Like It.md"),
    (23046, "The Comedy of Errors.md"),      # 1504 also exists
    (1535, "Coriolanus.md"),
    (1538, "Cymbeline.md"),                   # need to verify this number
    (1524, "Hamlet.md"),
    (1516, "King Henry IV Part 1.md"),
    (1518, "King Henry IV Part 2.md"),
    (1521, "King Henry V.md"),
    (1500, "King Henry VI Part 1.md"),         # need to verify
    (1501, "King Henry VI Part 2.md"),
    (1502, "King Henry VI Part 3.md"),         # need to verify
    (1541, "King Henry VIII.md"),              # need to verify
    (1511, "King John.md"),
    (1532, "King Lear.md"),
    (1510, "Love's Labour's Lost.md"),
    (1522, "Julius Caesar.md"),
    (1533, "Macbeth.md"),
    (1530, "Measure for Measure.md"),
    (1515, "The Merchant of Venice.md"),
    (23044, "The Merry Wives of Windsor.md"),
    (1514, "A Midsummer Night's Dream.md"),
    (1519, "Much Ado about Nothing.md"),
    (1531, "Othello.md"),
    (1517, "Pericles.md"),                     # need to verify
    (1512, "King Richard II.md"),
    (1503, "King Richard III.md"),
    (1513, "Romeo and Juliet.md"),
    (1508, "The Taming of the Shrew.md"),
    (23042, "The Tempest.md"),                  # or 1540
    (1507, "Titus Andronicus.md"),
    (1106, "Titus Andronicus_alt.md"),          # alternative, will skip if 1507 works
    (1528, "Troilus and Cressida.md"),
    (1526, "Twelfth Night.md"),
    (1509, "The Two Gentlemen of Verona.md"),   # need to verify
    (1542, "The Two Noble Kinsmen.md"),         # need to verify
    (1539, "The Winter's Tale.md"),
    (23045, "Measure for Measure_alt.md"),      # alternative, skip
    (110, "Timon of Athens.md"),                # need to verify number

    # Poems
    (1041, "Sonnets.md"),
    (1045, "Venus and Adonis.md"),
    (1505, "The Rape of Lucrece.md"),
    (1044, "A Lover's Complaint.md"),           # need to verify
    (1525, "The Passionate Pilgrim.md"),        # need to verify
    (1520, "The Phoenix and the Turtle.md"),    # need to verify
]

# Remove duplicates/alternatives
WORKS_CLEAN = [(num, name) for num, name in WORKS if not name.endswith("_alt.md")]


def download_work(ebook_number, filename):
    """Download a single work from Project Gutenberg."""
    url = f"https://www.gutenberg.org/cache/epub/{ebook_number}/pg{ebook_number}.txt"
    output_path = BACKUP_DIR / filename

    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"  ⏭️  {filename} already exists ({output_path.stat().st_size // 1024}K)")
        return True

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8-sig", errors="replace")

        # Strip Gutenberg header/footer
        start_marker = "*** START OF"
        end_marker = "*** END OF"

        start_idx = content.find(start_marker)
        if start_idx != -1:
            start_idx = content.find("\n", start_idx) + 1
        else:
            start_idx = 0

        end_idx = content.find(end_marker)
        if end_idx == -1:
            end_idx = len(content)

        clean_content = content[start_idx:end_idx].strip()

        # Save as markdown
        md_content = f"# {filename.replace('.md', '')}\n\n{clean_content}\n"
        output_path.write_text(md_content, encoding="utf-8")

        size = output_path.stat().st_size // 1024
        print(f"  ✅ {filename} ({size}K)")
        return True

    except Exception as e:
        print(f"  ❌ {filename} (ebook #{ebook_number}): {e}")
        return False


def main():
    print(f"\n📚 Downloading {len(WORKS_CLEAN)} Shakespeare works from Project Gutenberg\n")

    success = 0
    failed = []

    for ebook_num, filename in WORKS_CLEAN:
        result = download_work(ebook_num, filename)
        if result:
            success += 1
        else:
            failed.append((ebook_num, filename))
        time.sleep(0.5)  # Be nice to Gutenberg servers

    print(f"\n✅ Downloaded: {success}/{len(WORKS_CLEAN)}")
    if failed:
        print(f"❌ Failed: {len(failed)}")
        for num, name in failed:
            print(f"   #{num}: {name}")


if __name__ == "__main__":
    main()
