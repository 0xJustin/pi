---
name: repo-map
description: Generate a ranked function/class map (repo_map.py) or an import-dependency graph with Mermaid/Graphviz diagrams (repo_graph.py) of a repo/subdirectory under ~/brain or ~/song_workspace. repo_map.py uses aider's tree-sitter + personalized-PageRank engine for a ranked signature overview; repo_graph.py resolves real Python imports into a trustworthy module-level architecture graph. Use when orienting in an unfamiliar/large part of a repo, or when you need a structural overview or an architecture diagram instead of grepping file by file.
---

# Repo Map

Reuses [aider](https://github.com/Aider-AI/aider)'s actual `RepoMap` class
(`aider/repomap.py`) via a dedicated isolated venv installed alongside this skill —
not a reimplementation. You get real tree-sitter multi-language parsing, real
personalized-PageRank ranking (biased toward files/identifiers you tell it you're
focused on), and real token-budgeted output, for free.

**Bounded to `~/brain` and `~/song_workspace`.** The script refuses any path outside
those two roots — it's a personal dev tool, not meant to wander the filesystem.

**Nested by design.** This is a skill, not an auto-loaded context file: only this
one-line description sits in every session until you actually invoke it, and even
then, point it at the smallest subdirectory that's actually relevant rather than a
whole repo, to keep the output itself small. `--tokens` bounds the output further.

## Usage

```bash
~/.pi/agent/skills/repo-map/.venv/bin/python ~/.pi/agent/skills/repo-map/repo_map.py <path> [options]
```

- `<path>` — repo or subdirectory to map (must resolve under `~/brain` or
  `~/song_workspace`). Prefer a subdirectory over a whole repo when you already know
  roughly where you're looking — smaller scan, smaller output, same idea as slicing.
- `--tokens N` — output token budget (default 2048).
- `--focus file1 file2 ...` — bias ranking toward these files, e.g. whatever you're
  currently editing. Mirrors aider's "files already in chat" personalization.
- `--mention name1 name2 ...` — bias ranking toward these identifier names.
- `--ext .py,.ts` — override the scanned extensions (default: `.py,.js,.jsx,.ts,.tsx,.sh`).
- `--refresh` — force re-ranking instead of reusing the cached tag scan.

Example, oriented toward a specific file you're about to edit:

```bash
~/.pi/agent/skills/repo-map/.venv/bin/python ~/.pi/agent/skills/repo-map/repo_map.py \
  /groups/turaga/home/ellisj1/song_workspace/staging/flylocomotion_data_dashboard_worktree/dashboard \
  --tokens 1024 --focus bundle.py
```

## Caching

Per-file tag scans (the expensive tree-sitter parse) are cached persistently in
`~/.pi/agent/skills/repo-map/.cache/`, keyed by resolved repo path — **not** written
into the target repo (aider's default behavior writes `.aider.tags.cache.v*/` directly
into whatever repo you point it at; this wrapper redirects that centrally on purpose,
so `~/brain` and every project repo stay clean). Cache invalidates per-file on mtime
change, same as aider's own logic — no manual invalidation needed.

## `repo_graph.py` — module-level import-dependency graph (tier 1)

A companion to `repo_map.py`. Where `repo_map.py` gives ranked *signatures* (and
its internal edges come from noisy bare-identifier matching — 403 mostly-false
cross-package edges on synaptix+drosophilax), `repo_graph.py` resolves **real
Python imports** with `ast` into a **trustworthy** `module -> module` graph inside
ONE package. Use it for interpretable architecture maps and pathway diagrams.

```bash
~/.pi/agent/skills/repo-map/.venv/bin/python \
  ~/.pi/agent/skills/repo-map/repo_graph.py <package_dir> --out <dir> [options]
```

- `<package_dir>` — the package directory that holds `__init__.py`
  (e.g. `.../staging/synaptix/synaptix`, `.../drosophilax/src/drosophilax`), under
  `~/brain` or `~/song_workspace`. **Map one package at a time**; cross-repo edges
  are wired by hand (import resolution is intra-package by design).
- `--out DIR` (required) — output directory (created if missing).
- `--name NAME` — artifact basename (default: package dir name).
- `--cluster-depth N` — subpackage grouping depth for clusters (default 1).
- `--focus module.prefix` — restrict the module graph to the forward+backward
  reachable pathway through that module prefix (for one-pathway diagrams).
- `--png` — also render a PNG via graphviz `dot` (if installed).

Emits, per package:
- `<name>.clusters.mmd` — **broad map**: subpackage→subpackage Mermaid (edge labels
  = number of crossing imports). The headline interpretable view.
- `<name>.modules.mmd` — detailed module-level Mermaid, clustered by subpackage.
- `<name>.dot` / `<name>.png` — Graphviz (node border weight ∝ PageRank).
- `<name>.json` — nodes (module, file, cluster, in_degree, pagerank) + edges.

Mermaid renders natively in the `~/brain` Obsidian vault. Rendered per-repo notes
live in `~/brain/02-Projects/Codebase-Maps/` (raw artifacts under `generated/`).
Staleness-free by regeneration — just re-run after code changes.

## One-time setup (already done; here for if this ever needs rebuilding)

```bash
cd ~/.pi/agent/skills/repo-map
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python aider-chat
```

Python 3.12 specifically — `aider-chat`'s dependency chain (numpy et al.) doesn't have
prebuilt wheels for 3.13 yet as of this writing, which forces a slow/fragile source
build. 3.12 has full wheel coverage.
