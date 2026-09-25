"""Label each agent pane with the ids of the problem-tree nodes listing its session under `sessions:`.

Several nodes join with "+"; a closed node gets "-done". The agent's herdr name mirrors the label
("+" -> "_"), so `herdr agent prompt cbe-xmz5 ...` reaches it. Panes on no node are left alone.
"""
import fcntl
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

VAULT = Path.home() / "brain"
CONFIG = VAULT / ".claude/tools/problem-tree/config.yaml"
CLOSED = {"done", "dropped", "verified", "closed"}
HERDR = os.environ.get("HERDR_BIN_PATH", "herdr")


def herdr(*args):
    out = subprocess.run([HERDR, *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)["result"]


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---", path.read_text(), re.S)
    return yaml.safe_load(m.group(1)) if m else None


def node_refs():
    """session ref (path or uuid) -> [(opened, label)] of every node listing it."""
    refs = {}
    for glob in yaml.safe_load(CONFIG.read_text())["tree_globs"]:
        for p in VAULT.glob(f"{glob}/*.md"):
            fm = frontmatter(p)
            if not isinstance(fm, dict) or not fm.get("id"):
                continue
            label = fm["id"] + ("-done" if fm.get("status") in CLOSED else "")
            for s in fm.get("sessions") or []:
                if isinstance(s, dict) and s.get("ref"):
                    refs.setdefault(str(s["ref"]), []).append((str(fm.get("opened") or ""), label))
    return refs


# Hooks fire in bursts; serialise so two runs never rename from stale lists.
with open(os.path.join(os.environ.get("HERDR_PLUGIN_STATE_DIR", "/tmp"), "lock"), "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    refs = node_refs()
    labels = {p["pane_id"]: p.get("label") for p in herdr("pane", "list")["panes"]}
    for a in herdr("agent", "list")["agents"]:
        value = (a.get("agent_session") or {}).get("value") or ""
        # pi reports its session file; a node may list the file or the uuid at the end of its stem.
        hits = refs.get(value, []) + (refs.get(Path(value).stem.split("_")[-1], []) if "/" in value else [])
        if not hits:
            continue
        label = "+".join(dict.fromkeys(l for _, l in sorted(hits)))
        if labels.get(a["pane_id"]) != label:
            subprocess.run([HERDR, "pane", "rename", a["pane_id"], label], capture_output=True)
        name = label.replace("+", "_")[:32]
        if a.get("name") != name:  # fails harmlessly if another live agent already holds the name
            subprocess.run([HERDR, "agent", "rename", a["pane_id"], name], capture_output=True)
