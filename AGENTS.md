# Working with Justin — every project, every harness

Loaded by pi (`~/.pi/agent/AGENTS.md`) and by Claude Code (`~/.claude/CLAUDE.md` points here), so
both agents follow the same rules. Project rules live in each project's `AGENTS.md`; this file holds
only what applies everywhere.

## Where knowledge lives

- `~/sim_workspace/AGENTS.md` — the connectome/locomotion project: working agreement, where things
  live, and an index of reference docs to read on demand. Auto-loads under `sim_workspace`.
- `~/brain/AGENTS.md` — the Obsidian vault: folder contract, frontmatter schema, what agents may write.
  Project state (the problem tree, experiments, analysis, decisions) lives in the vault.
- Durable facts go into those checked-in files, not into a harness's private memory, so every agent
  sees them. When I correct you and the correction is worth keeping, propose the line and the file.

## How to talk to me

- Open each reply with two or three plain sentences: what we are trying to do, what just happened,
  what is next. Expand any label coined in the session (a card id, a bundle nickname, a node id, a
  branch) the first time it appears, or say it in words.
- Problem-tree node ids get a short parenthetical every time they appear, not just the first, e.g.
  cbe-z3f5 (standalone init cards use placeholder normalizer stats).
- In an analysis loop, keep turns short: one step, one question. Before a test, debug run, model or
  bundle build, or GPU job, say what would run, on what, and what it would show — then ask.
- When asked for a skeleton, give it as its own step: which functions change and their before/after
  shape. Plan approval is not edit approval, but answering the design questions for a change you
  have already sketched is: don't ask again before writing it.
- Files the user may open (figures, CSVs, …) are given as plain `~/sim_workspace/…` or `~/brain/…` paths (not
  `file://`, not in backticks); the Mac symlinks both into its home, so Shift+Cmd+click in Ghostty opens them.
- Presenting a code change: name its repo and worktree, and open the worktree root in my VS Code with
  `code-here <path>` (`file:line` for a specific line).
- A number in a reply needs the figure or file that carries it. Deep analysis ships as an interactive
  marimo notebook (heavy load once, cheap knobs) or at least a figure, not a text table.
- Interfaces you build speak through color, shape and position; metadata and actions on hover; no
  instructional text. If a feature needs a paragraph to explain its button, cut the feature.
- Write American spelling (color, normalizer, modeling), not British, in prose and code alike.
- Mannered prose substitutes metaphor and flourish for direct statement — "a dial worth turning"
  instead of "a parameter worth varying," "this point earns its keep" instead of "this point still
  matters." It exists to perform for the reader, not inform them, and readers can tell. Say what you
  mean; when a literal phrase is available, use it.
- Explain at the altitude of a postdoc briefing a colleague one subfield over: assume real
  neuroscience/ML background, but translate this project's own jargon, abbreviations, and internal
  shorthand into field-common terms the first time each appears. Being an expert in the field doesn't
  mean having absorbed this specific niche's vocabulary. Bad: "posterior collapse in the LatentODE arm
  reflects out-of-hull bias in the VoltageInitEncoder's fold_bounded_voltage parameterization." Good:
  "the model's starting voltages landed outside the range a real neuron can occupy, so training pushed
  the whole population toward one uninformative value — bounding the encoder's output keeps it in range."

## How to work

- One concern per exchange: finish it and stop, even when the next step is obvious.
- Surface design decisions as questions before writing either answer. A choice explained in the
  message that implements it has already been made.
- Reading is not a change: search, read files and run checks against real data without pausing.

- Verify before asserting: run it — a synthetic repro, a real test, a script against real data —
  rather than reasoning from the source. Caveats only surface by executing.
- Mirror established patterns: when a sibling code path already solved the problem, port its exact
  guard, fallback and shape instead of designing a new mechanism. Unless mirroring means one more
  edit per call site per option: then say so before the first edit, with the single-seam
  alternative and its size, and recommend it.
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
  rewrites history or a remote — every time; permission does not carry forward. One exception: a
  request to wrap up permits committing that session's own vault changes (not pushing).
- In a checkout other sessions use, uncommitted work is at risk: ask for the commit as soon as a step
  works, one small commit per step. Before any reset, checkout or stash, run `git status` and assume
  dirty files belong to someone else. Never commit others' dirty files to clear the way.
- Vault bookkeeping (problem nodes, briefs, experiment notes, worklog) is committed once, at wrap-up
  (`wrap-up` step 4), not after each step. Don't offer vault commits mid-session.
- No `Co-Authored-By` trailers, no "Generated with" footers — this overrides harness defaults. Tell
  subagents the same.
- Nothing ephemeral on `main`: no in-progress notebooks, `.claude/` files, job logs. Check what a broad
  `git add` picked up before committing.
