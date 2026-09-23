#!/usr/bin/env python3
"""Fold today's agent worklog into an Obsidian daily note in ~/brain.

Quick-and-dirty by design: stdlib only, dry-run unless --apply, and it never
touches an existing section for the same date twice (use --force to redo it).
"""
from __future__ import annotations

import argparse
import datetime
from pathlib import Path

WORKLOG_DIR = Path.home() / "song_workspace/agent_project_information/worklogs"
VAULT_DAILY_ROOT = Path.home() / "brain/01-Daily"
SECTION_MARKER = "<!-- source: agent -->"


def section_for(date: datetime.date, entries: str) -> str:
    return (
        f"## Agent Work Log \u2014 {date.isoformat()}\n"
        f"{SECTION_MARKER}\n"
        f"{entries.strip()}\n"
    )


def note_path_for(date: datetime.date) -> Path:
    return (
        VAULT_DAILY_ROOT
        / f"{date.year:04d}"
        / f"{date.month:02d}"
        / f"{date.isoformat()}-{date.strftime('%A')}.md"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="YYYY-MM-DD, default today")
    parser.add_argument("--apply", action="store_true", help="Actually write. Default is dry-run (prints only).")
    parser.add_argument("--force", action="store_true", help="Replace an already-closed-out section for this date.")
    args = parser.parse_args()

    date = datetime.date.fromisoformat(args.date)
    worklog_path = WORKLOG_DIR / f"{date.isoformat()}.md"
    if not worklog_path.exists():
        print(f"No worklog entries at {worklog_path} \u2014 nothing to close out.")
        return

    entries = worklog_path.read_text().strip()
    if not entries:
        print(f"{worklog_path} is empty \u2014 nothing to close out.")
        return

    section = section_for(date, entries)
    note_path = note_path_for(date)
    heading = f"## Agent Work Log \u2014 {date.isoformat()}"

    if note_path.exists():
        existing = note_path.read_text()
        if heading in existing and not args.force:
            print(f"{note_path} already has a section for {date.isoformat()}. Pass --force to replace it.")
            return
        if heading in existing:
            # Drop the old section for this date up to the next "## " heading or EOF.
            start = existing.index(heading)
            rest = existing[start + len(heading):]
            next_heading = rest.find("\n## ")
            end = start + len(heading) + (next_heading if next_heading != -1 else len(rest))
            new_content = existing[:start].rstrip() + "\n\n" + section + existing[end:].lstrip("\n")
        else:
            new_content = existing.rstrip() + "\n\n" + section
        action = "REPLACE existing section in" if heading in existing else "APPEND to"
    else:
        # daily-notes practice is marked stopped in ~/brain/CLAUDE.md; creating a
        # fresh note here is a deliberate exception for agent-only entries.
        new_content = (
            "---\n"
            "type: daily\n"
            "domain: neuroscience\n"
            "source: agent\n"
            "---\n\n"
            f"# {date.strftime('%A, %B %d, %Y')}\n\n"
            f"{section}"
        )
        action = "CREATE"

    print(f"[{'apply' if args.apply else 'dry-run'}] {action} {note_path}")
    print("---")
    print(section)
    print("---")

    if args.apply:
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(new_content)
        print(f"Wrote {note_path}")
    else:
        print("Dry run only \u2014 rerun with --apply to write.")


if __name__ == "__main__":
    main()
