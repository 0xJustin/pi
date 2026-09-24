---
name: code-here
description: Opens a repo worktree, folder or file:line from the cluster in Justin's VS Code on the Mac (the window connected over Remote-SSH), so he can review a change with VS Code's Source Control and side-by-side diffs. Use when presenting a code change for review, or when the user asks to open, look at or review code, a worktree or a file in VS Code.
---

# Open in VS Code

```bash
code-here [PATH | FILE:LINE ...]
```

`~/.local/bin/code-here` (a link to `scripts/code-here`) finds the live VS Code Remote-SSH connection on this host and asks that VS Code
to open the paths. With no argument it opens the current git worktree root.

## When

- **Presenting a change for review:** open the worktree the change is in (its root, not a subfolder), and
  name that repo and worktree in the reply. One call per worktree touched.
- **Pointing at a specific line** (a bug, a review comment): `code-here path/to/file.py:120`.
- Only open what the reply is about; do not open windows speculatively.

## Rules

- Pass worktree roots: `git -C <dir> rev-parse --show-toplevel`. `~` and `~/song_workspace` sit inside a
  stray repo rooted at `$HOME`; never open `$HOME` as a repo.
- `no VS Code window is connected`: tell the user to connect VS Code with Remote-SSH to this host
  (`hostname -s`), then rerun. Nothing else to fix on the cluster side.
- It opens folders in a new window by VS Code's default; `-r` as the first argument reuses the current
  window.
- It only opens things; it never edits, stages or commits.
