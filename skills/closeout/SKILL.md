---
name: closeout
description: End-of-day rollup. Reads today's agent worklog from song_workspace/agent_project_information/worklogs/ and folds it into today's Obsidian daily note in ~/brain. Use when the user asks to "close out the day", "closeout", or "log today's work to Obsidian".
---

# Closeout

Quick-and-dirty end-of-day skill: takes today's `agent_project_information/worklogs/YYYY-MM-DD.md`
(one line per completed task, written by any agent during the day) and appends it as a
clearly-marked "Agent Work Log" section to the matching Obsidian daily note in `~/brain`.

**Note:** `~/brain/CLAUDE.md` states the daily-notes practice has stopped (a physical
planner is used instead). This skill creates/edits daily notes anyway, but only ever
touches the single `## Agent Work Log` section it owns (marked with
`<!-- source: agent -->`) — it never rewrites the rest of the note. If the user's own
daily-note conventions have changed, confirm before running with `--apply`.

## Usage

Always dry-run first (default) and show the user the diff before writing:

```bash
python3 ~/.pi/agent/skills/closeout/close_day.py
```

Only write after the user confirms:

```bash
python3 ~/.pi/agent/skills/closeout/close_day.py --apply
```

Options:
- `--date YYYY-MM-DD` — close out a different day (default: today).
- `--force` — replace an already-written Agent Work Log section for that date (default:
  refuses to touch it twice).

## What it does

1. Reads `~/song_workspace/agent_project_information/worklogs/<date>.md`. If missing/empty,
   reports that and stops — nothing to do.
2. Resolves the vault daily note path: `~/brain/01-Daily/<year>/<month>/<date>-<weekday>.md`
   (matches the vault's own daily-note naming).
3. If the note doesn't exist, creates it with minimal frontmatter
   (`type: daily`, `domain: neuroscience`, `source: agent`) — **check the `domain` is
   right for that day's actual work** and fix it by hand afterward if not.
4. If the note exists, appends the section (or replaces it with `--force`); never touches
   anything else in the note.

## After running

Point the user at the note path it printed so they can review/edit in Obsidian. This is
intentionally not fancier than that — it's a rollup, not a summarizer.
