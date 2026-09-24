# Working with Justin — every project, every harness

Loaded by pi (`~/.pi/agent/AGENTS.md`) and by Claude Code (`~/.claude/CLAUDE.md` points here), so
both agents follow the same rules. Project rules live in each project's `AGENTS.md`; this file holds
only what applies everywhere.

## Where knowledge lives

- `~/song_workspace/AGENTS.md` — the connectome/locomotion project: working agreement, where things
  live, and an index of reference docs to read on demand. Auto-loads under `song_workspace`.
- `~/brain/CLAUDE.md` — the Obsidian vault: folder contract, frontmatter schema, what agents may write.
  Project state (the problem tree, experiments, analysis, decisions) lives in the vault.
- Durable facts go into those checked-in files, not into a harness's private memory, so every agent
  sees them. When I correct you and the correction is worth keeping, propose the line and the file.

## How to talk to me

- Open each reply with two or three plain sentences: what we are trying to do, what just happened,
  what is next. Expand any label coined in the session (a card id, a bundle nickname, a node id, a
  branch) the first time it appears, or say it in words.
- Problem-tree node ids get a short parenthetical every time they appear, not just the first, e.g.
  cbe-z3f5 (standalone init cards use placeholder normaliser stats).
- In an analysis loop, keep turns short: one step, one question. Before a test, debug run, model or
  bundle build, or GPU job, say what would run, on what, and what it would show — then ask.
- When asked for a skeleton, give it as its own step: which functions change and their before/after
  shape. Plan approval is not edit approval.
- Figures (PNG/JPG/PDF) in a reply are given as the Mac path, `/Volumes/turaga$/ellisj1/…` (plain, not
  `file://`, not in backticks), so Shift+Cmd+click in Ghostty opens them in Preview. Other paths stay `~/…`.
- A number in a reply needs the figure or file that carries it. Deep analysis ships as an interactive
  marimo notebook (heavy load once, cheap knobs) or at least a figure, not a text table.
- Interfaces you build speak through colour, shape and position; metadata and actions on hover; no
  instructional text. If a feature needs a paragraph to explain its button, cut the feature.

## How to work

- Verify before asserting: run it — a synthetic repro, a real test, a script against real data —
  rather than reasoning from the source. Caveats only surface by executing.
- Mirror established patterns: when a sibling code path already solved the problem, port its exact
  guard, fallback and shape instead of designing a new mechanism.
- Pragmatic defensiveness: build for the intended path; add validation for impossible states only
  when a real bug on that path demands it.
- Research grids: when an axis is "which registered option", enumerate the registry and include the
  best-motivated option even if unused; say why each is in or out. The user picks directions; agents
  run fixed grids.
- Reproducing a reference result: a ladder — swap one ingredient at a time toward the reference, with
  a toy-motif control; fix root causes, not workarounds.
- Validation criteria state the healthy expectation before a card may fail (e.g. −1 at rest is
  expected, not a failure).

## Git, everywhere

- `git status / diff / log / show` freely. Ask before `git add`, `commit`, `push`, and anything that
  rewrites history or a remote — every time; permission does not carry forward.
- In a checkout other sessions use, uncommitted work is at risk: ask for the commit as soon as a step
  works, one small commit per step. Before any reset, checkout or stash, run `git status` and assume
  dirty files belong to someone else. Never commit others' dirty files to clear the way.
- No `Co-Authored-By` trailers, no "Generated with" footers — this overrides harness defaults. Tell
  subagents the same.
- Nothing ephemeral on `main`: no in-progress notebooks, `.claude/` files, job logs. Check what a broad
  `git add` picked up before committing.
