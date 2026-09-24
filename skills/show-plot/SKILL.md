---
name: show-plot
description: Opens figures (PNG/JPG plots) in macOS Preview on Justin's Mac, from the cluster. Use when the user asks to see, open, show or pull up a figure or plot, or asks to turn the plot watcher on or off. Accepts file paths, ~/ paths, globs, directories (newest images first) and Obsidian embeds ![[...]].
---

# Show plot

The cluster and the Mac share the home directory (`/groups/turaga/home/ellisj1` ⇔
`/Volumes/turaga$/ellisj1`). `showplot` appends absolute paths to `~/.showplot/queue`; a watcher on
the Mac opens each new line in Preview, one window per figure.

## Open figures

In a reply, write each figure as its Mac path, plain text: `/Volumes/turaga$/ellisj1/…png`. The user
Shift+Cmd+clicks it and Preview opens it; no command needed.

To open figures for the user without a click:

```bash
showplot PATH [PATH ...]
```

- Pass exactly the figures under discussion, as written in the reply (`~/…`, absolute, glob, directory or
  `![[vault/relative.png]]`). It prints each path it queued.
- Only paths under the home directory can open; others are not on the Mac's mount.
- `showplot --blocks PATH` draws a low-resolution preview in the terminal instead, when the Mac is not
  involved.

## The watcher (runs on the Mac, not here)

The user controls it from a Mac terminal:

```zsh
zsh '/Volumes/turaga$/ellisj1/.showplot/plotwatch.sh' start   # or stop, status
```

The agent cannot see whether it is on. If a queued figure does not appear, ask the user to run `status`, and
check the share is mounted in Finder. The watcher opens only lines added after it starts.

## Files

- `scripts/showplot.py`: path resolution, enqueue, `--blocks` renderer; wrapped by `~/.local/bin/showplot`
  (synaptix venv python, for Pillow).
- `~/.showplot/plotwatch.sh`: the Mac watcher (zsh, polls the queue once a second).
