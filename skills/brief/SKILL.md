---
name: brief
description: Write a self-contained prompt (a brief) for a child problem-tree node, so the user can start a fresh agent session on it by pasting the brief's path. Use when the user says "write a brief", "brief this", "hand this off", or asks for a prompt for a new session on a node. Never launch or prompt the child session yourself.
---

# Brief

The user runs one session per piece of work, loosely. When work surfaces a child node that deserves
its own session, this session writes the child's prompt to a file; the user starts the session and
pastes the path. You write the file and stop.

1. Node: find the child's node, or open a task for it with
   `python3 ~/brain/.claude/tools/problem-tree/new.py ~/brain/02-Projects/connectome_simulation/connectome_body_eval/problems task --parent <id> --discovered-from <this session's node> --title "…"`.
   Fill its `## What` and `before:` if they are empty.
2. Brief: write `~/brain/02-Projects/connectome_simulation/connectome_body_eval/briefs/<node-id>.md`
   (overwrite an older brief for the same node only after saying so). No checkboxes; the tree is
   the only task list. Shape:

   ```markdown
   ---
   type: note
   domain: neuroscience
   source: agent
   node: <node-id>
   parent_node: <this session's node id>
   parent_session: <$PI_SESSION_FILE, or the Claude session id, or null>
   written: YYYY-MM-DD
   cwd: ~/…
   repo: <repo, branch or worktree the work belongs in>
   ---
   # Brief: <node-id> — <title>

   ## Goal            one or two sentences
   ## Why             the before: evidence, as ~/ paths
   ## What the parent knows
                       decisions, files and lines, commands, dead ends — only what this session
                       actually established; say what is unverified
   ## Constraints     point to AGENTS.md rules instead of restating them; name the repo/worktree
   ## Done means      the after: evidence expected; the three-line ## Outcome
   ## Report back     what the parent session needs to hear when this is done
   ## First move      1. Add this session to the node's `sessions:` list —
                          `{harness: pi, ref: <$PI_SESSION_ID>}` (Claude: `{harness: claude, ref: <session uuid>}`),
                          appending, never replacing other entries.
                       2. Read the node and the files above, propose a plan, and stop for the user.
   ```

3. Reply with the brief's `~/` path on its own line (plain, pasteable) and the node(s) you opened or
   updated, each with its short parenthetical. Do not start, split, or prompt any session or pane.
