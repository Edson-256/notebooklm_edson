#!/usr/bin/env python3
"""Split the complete Shakespeare text into individual play/poem files."""

import re
from pathlib import Path

BACKUP_DIR = Path(__file__).parent
INPUT_FILE = BACKUP_DIR / "complete_shakespeare.txt"

# Titles as they appear in the Gutenberg text, mapped to output filenames
# These match the source names from the NotebookLM notebook
TITLES = [
    ("THE SONNETS", "Sonnets.md"),
    ("ALL'S WELL THAT ENDS WELL", "All's Well That Ends Well.md"),
    ("THE TRAGEDY OF ANTONY AND CLEOPATRA", "Antony and Cleopatra.md"),
    ("AS YOU LIKE IT", "As You Like It.md"),
    ("THE COMEDY OF ERRORS", "The Comedy of Errors.md"),
    ("THE TRAGEDY OF CORIOLANUS", "Coriolanus.md"),
    ("CYMBELINE", "Cymbeline, King of Britain.md"),
    ("THE TRAGEDY OF HAMLET, PRINCE OF DENMARK", "The Tragedy of Hamlet, Prince of Denmark.md"),
    ("THE FIRST PART OF KING HENRY THE FOURTH", "History of Henry IV, Part I.md"),
    ("THE SECOND PART OF KING HENRY THE FOURTH", "History of Henry IV, Part II.md"),
    ("THE LIFE OF KING HENRY THE FIFTH", "History of Henry V.md"),
    ("THE FIRST PART OF HENRY THE SIXTH", "History of Henry VI, Part I.md"),
    ("THE SECOND PART OF KING HENRY THE SIXTH", "History of Henry VI, Part II.md"),
    ("THE THIRD PART OF KING HENRY THE SIXTH", "History of Henry VI, Part III.md"),
    ("KING HENRY THE EIGHTH", "History of Henry VIII.md"),
    ("THE LIFE AND DEATH OF KING JOHN", "History of King John.md"),
    ("THE TRAGEDY OF JULIUS CAESAR", "The Tragedy of Julius Caesar.md"),
    ("THE TRAGEDY OF KING LEAR", "The Tragedy of King Lear.md"),
    ("LOVE'S LABOUR'S LOST", "Love's Labour's Lost.md"),
    ("THE TRAGEDY OF MACBETH", "The Tragedy of Macbeth.md"),
    ("MEASURE FOR MEASURE", "Measure for Measure.md"),
    ("THE MERCHANT OF VENICE", "The Merchant of Venice.md"),
    ("THE MERRY WIVES OF WINDSOR", "The Merry Wives of Windsor.md"),
    ("A MIDSUMMER NIGHT'S DREAM", "A Midsummer Night's Dream.md"),
    ("MUCH ADO ABOUT NOTHING", "Much Ado about Nothing.md"),
    ("THE TRAGEDY OF OTHELLO, THE MOOR OF VENICE", "The Tragedy of Othello, Moor of Venice.md"),
    ("PERICLES, PRINCE OF TYRE", "Pericles, Prince of Tyre.md"),
    ("KING RICHARD THE SECOND", "History of Richard II.md"),
    ("KING RICHARD THE THIRD", "History of Richard III.md"),
    ("THE TRAGEDY OF ROMEO AND JULIET", "The Tragedy of Romeo and Juliet.md"),
    ("THE TAMING OF THE SHREW", "The Taming of the Shrew.md"),
    ("THE TEMPEST", "The Tempest.md"),
    ("THE LIFE OF TIMON OF ATHENS", "The Tragedy of Timon of Athens.md"),
    ("THE TRAGEDY OF TITUS ANDRONICUS", "Titus Andronicus.md"),
    ("TROILUS AND CRESSIDA", "Troilus and Cressida.md"),
    ("TWELFTH NIGHT; OR, WHAT YOU WILL", "Twelfth Night, Or What You Will.md"),
    ("THE TWO GENTLEMEN OF VERONA", "Two Gentlemen of Verona.md"),
    ("THE TWO NOBLE KINSMEN", "The Two Noble Kinsman.md"),
    ("THE WINTER'S TALE", "The Winter's Tale.md"),
    ("A LOVER'S COMPLAINT", "A Lover's Complaint.md"),
    ("THE PASSIONATE PILGRIM", "The Passionate Pilgrim.md"),
    ("THE PHOENIX AND THE TURTLE", "The Phoenix and the Turtle.md"),
    ("THE RAPE OF LUCRECE", "The Rape of Lucrece.md"),
    ("VENUS AND ADONIS", "Venus and Adonis.md"),
]


def main():
    content = INPUT_FILE.read_text(encoding="utf-8-sig")
    # Normalize line endings
    content = content.replace("\r\n", "\n")
    
    lines = content.split("\n")
    
    # Find the start positions of each work by looking for the title
    # appearing as a standalone line (often centered/indented)
    title_positions = []
    
    for gutenberg_title, filename in TITLES:
        # Search for the title line AFTER the table of contents (line ~80+)
        found = False
        for i, line in enumerate(lines):
            if i < 80:  # Skip TOC
                continue
            stripped = line.strip()
            if stripped == gutenberg_title:
                title_positions.append((i, gutenberg_title, filename))
                found = True
                break
        if not found:
            print(f"  ⚠️  NOT FOUND: {gutenberg_title}")
    
    # Sort by line position
    title_positions.sort(key=lambda x: x[0])
    
    print(f"Found {len(title_positions)} works\n")
    
    # Extract content for each work
    for idx, (start_line, title, filename) in enumerate(title_positions):
        # End is the start of the next work, or the Gutenberg footer
        if idx + 1 < len(title_positions):
            end_line = title_positions[idx + 1][0]
        else:
            # Find the end marker
            end_line = len(lines)
            for i, line in enumerate(lines):
                if "*** END OF THE PROJECT GUTENBERG EBOOK" in line:
                    end_line = i
                    break
        
        # Extract the text
        work_lines = lines[start_line:end_line]
        work_text = "\n".join(work_lines).strip()
        
        # Add a markdown header
        md_content = f"# {title.title()}\n\n{work_text}\n"
        
        # Save
        output_path = BACKUP_DIR / filename
        output_path.write_text(md_content, encoding="utf-8")
        
        line_count = len(work_lines)
        print(f"  ✅ {filename} ({line_count} lines)")
    
    print(f"\n📁 All files saved to: {BACKUP_DIR}")


if __name__ == "__main__":
    main()
