---
name: wrap-up
description: End-of-task bookkeeping before a thread is retired — worklog lines, problem-tree nodes current and validated, evidence in the vault, this session's uncommitted work listed for commit, scratch removed. Use when the user says "wrap up", "do the bookkeeping", or is about to retire the thread.
---

# Wrap-up

Make sure everything this session did is recorded where the next reader looks, so nothing lives
only in the conversation. Work from your own actions this session; never touch another session's
files or dirty work.

Wrap-up never touches the daily note; that is `closeout`, run only when the user closes out the day.

1. Worklog: every meaningful chunk has a line in
   ~/song_workspace/agent_project_information/worklogs/<today>.md, with the node id first.
2. Tree: every node you opened or changed is current — status, evidence, `## Outcome`. Any action
   item you wrote elsewhere names its node. Run validate.py --tree; report warnings, don't fix them.
   Close nothing `done` without the user's go-ahead.
   Child of a brief: if a node lists this session under `sessions:` and has a brief at
   ~/brain/02-Projects/connectome_simulation/connectome_body_eval/briefs/<id>.md, make its
   `## Outcome` answer the brief's *Report back*. Find the parent by matching the brief's
   `parent_session` against `herdr agent list` (read only): name its tab/pane, or say it is closed
   and give `pi --session <path>`. Print one line for the user to paste there:
   `<id> (<title>): <done|partial|blocked>, <one line>. Read ~/brain/…/problems/<id>.md`
3. Evidence: every number you gave in a reply has its figure or file in the vault
   (media/problems/<id>/ or the note that cites it).
4. Git: for each repo and the vault, list the files this session changed that are still
   uncommitted. Ask for the commits (one per step); never stage others' files.
5. Scratch: delete what you created under /tmp or tmp/ (installs, test copies); list what you removed.
6. Report, in one short table: nodes opened / updated / closed; commits made; what is left
   uncommitted and why; files with no git history.
7. End the reply with exactly one of these lines, verbatim:
   - `WRAP-UP COMPLETE: this thread can be retired.` — only when steps 1–5 all passed and nothing
     waits on the user.
   - `WRAP-UP INCOMPLETE: <what is left, e.g. commits awaiting approval>.` — otherwise.
