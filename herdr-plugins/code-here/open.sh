#!/bin/bash
# Run code-here in the focused pane's live directory (its foreground process's cwd, not its launch cwd).
set -euo pipefail
ctx=${HERDR_PLUGIN_CONTEXT_JSON:-'{}'}
pane=$(jq -r '.focused_pane_id // empty' <<<"$ctx")
dir=$("${HERDR_BIN_PATH:-herdr}" pane list | jq -r --arg p "$pane" 'first(.result.panes[] | select(.pane_id == $p) | .foreground_cwd // empty)')
dir=${dir:-$(jq -r '.focused_pane_cwd // empty' <<<"$ctx")}
cd "${dir:-$HOME}"
msg=$("$HOME/.local/bin/code-here" 2>&1) || "${HERDR_BIN_PATH:-herdr}" notification show "code-here" --body "$msg" >/dev/null
