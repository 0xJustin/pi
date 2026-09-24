"""Prefix each tab label with MARK while any agent in the tab is `done` (finished, not yet seen)."""
import fcntl
import json
import os
import subprocess

MARK = "● "
HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")


def herdr(*args):
    out = subprocess.run([HERDR, *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["result"]


# Hooks fire in bursts; serialise so two runs never rename the same tab from stale lists.
with open(os.path.join(os.environ.get("HERDR_PLUGIN_STATE_DIR", "/tmp"), "lock"), "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    done_tabs = {a["tab_id"] for a in herdr("agent", "list")["agents"] if a["agent_status"] == "done"}
    for tab in herdr("tab", "list")["tabs"]:
        label = tab.get("label") or ""
        base = label.removeprefix(MARK)
        want = MARK + base if tab["tab_id"] in done_tabs else base
        if want != label and base:
            subprocess.run([HERDR, "tab", "rename", tab["tab_id"], want], capture_output=True)
