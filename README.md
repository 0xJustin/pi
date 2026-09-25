# pi config

Backup of my [pi](https://github.com/earendil-works/pi) coding-agent configuration
(from `~/.pi/agent/`). Secrets are **not** included.

## Layout

| Path | What |
|------|------|
| `settings.json` | Theme, default provider/model, installed packages |
| `models-store.json` | Registered model definitions (no keys) |
| `notion.json` | Notion integration config — **token redacted** |
| `AGENTS.md` | Cross-project working agreement |
| `trust.json` | Trusted working directories |
| `agents/` | Subagents: planner, reviewer, scout, worker |
| `prompts/` | Prompt templates (scout-and-plan, implement, implement-and-review) |
| `skills/` | Skills: `closeout`, `repo-map`, `show-plot`, `code-here`, `brief`, `wrap-up` (scripts + SKILL.md) |
| `extensions/` | `herdr-agent-state.ts` |
| `herdr-plugins/` | herdr plugins, linked with `herdr plugin link <dir>`: `tab-done` (● on tabs with an unseen finished turn), `code-here` (open the focused pane's worktree in VS Code), `pane-node` (pane label and agent name = the ids of the problem-tree nodes whose `sessions:` list the pane's session) |
| `npm/` | Extension package manifest + lockfile |

## Restore

Copy files into `~/.pi/agent/`, then supply secrets that were excluded:

- `auth.json` — provider API keys (e.g. Anthropic `sk-ant-...`)
- `notion.json` — replace `REPLACE_WITH_YOUR_NOTION_TOKEN` with your real token

Then reinstall extension deps:

```bash
cd ~/.pi/agent/npm && npm install
```

## Not included (see `.gitignore`)

`auth.json`, `sessions/`, `web-search-cache/`, `bin/` binaries,
`npm/node_modules/`, skill `.venv/` and `.cache/`.
