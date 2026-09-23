#!/usr/bin/env python3
"""Generate an Aider-style ranked repo map for a repo/subtree.

Reuses aider's own `RepoMap` (tree-sitter tags + personalized PageRank ranking +
token-budgeted rendering, https://github.com/Aider-AI/aider/blob/main/aider/repomap.py)
via the isolated venv installed alongside this script. This wrapper only bounds scope
to a fixed allowlist of roots, redirects aider's tag cache out of the target tree (it
otherwise writes `.aider.tags.cache.v*/` directly into whatever repo you point it at),
and picks which files to hand it.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ALLOWED_ROOTS = [(Path.home() / "brain").resolve(), (Path.home() / "song_workspace").resolve()]
CENTRAL_CACHE_ROOT = Path(__file__).resolve().parent / ".cache"
DEFAULT_EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".sh"}
SKIP_DIR_NAMES = {"node_modules", "__pycache__", "site-packages", "dist", "build"}


def resolve_bounded(path_str: str) -> Path:
    target = Path(path_str).expanduser().resolve()
    for root in ALLOWED_ROOTS:
        if target == root or root in target.parents:
            return target
    allowed = ", ".join(str(r) for r in ALLOWED_ROOTS)
    raise SystemExit(f"Refusing: {target} is outside the allowed roots ({allowed}).")


def collect_files(root: Path, exts: set[str]) -> list[str]:
    files = []
    for p in root.rglob("*"):
        if not p.is_file() or p.suffix not in exts:
            continue
        rel_dirs = p.relative_to(root).parts[:-1]
        if any(part.startswith(".") or part in SKIP_DIR_NAMES for part in rel_dirs):
            continue
        files.append(str(p))
    return files


def cache_dir_for(root: Path) -> Path:
    digest = hashlib.sha1(str(root).encode()).hexdigest()[:10]
    return CENTRAL_CACHE_ROOT / f"{root.name}__{digest}"


def build_repo_map(
    root: Path,
    files: list[str],
    *,
    tokens: int,
    focus: list[str],
    mentions: list[str],
    refresh: bool,
) -> str:
    from aider.io import InputOutput
    from aider.models import Model
    from aider.repomap import RepoMap
    from diskcache import Cache

    cache_dir = cache_dir_for(root)
    cache_dir.mkdir(parents=True, exist_ok=True)

    class BoundedRepoMap(RepoMap):
        # Aider's default caches to `<root>/.aider.tags.cache.v*`; redirect to a
        # central, per-tool cache dir so mapped repos (esp. the ~/brain vault) never
        # get an uninvited directory written into them.
        def load_tags_cache(self):
            self.TAGS_CACHE = Cache(str(cache_dir))

    io = InputOutput()
    model = Model("gpt-4o")  # only used for local tiktoken counting; no network calls
    rm = BoundedRepoMap(map_tokens=tokens, root=str(root), main_model=model, io=io)

    focus_abs = {str((root / f).resolve()) if not Path(f).is_absolute() else f for f in focus}
    out = rm.get_repo_map(
        chat_files=list(focus_abs),
        other_files=[f for f in files if f not in focus_abs],
        mentioned_idents=set(mentions) if mentions else None,
        force_refresh=refresh,
    )
    return out or "(no map produced -- no recognized source files, or nothing fit the token budget)"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Repo or subdirectory to map (must be under ~/brain or ~/song_workspace)")
    parser.add_argument("--tokens", type=int, default=2048, help="Token budget for the rendered map (default: 2048)")
    parser.add_argument(
        "--focus", nargs="*", default=[],
        help="File(s) to personalize ranking toward -- like files already open/edited (relative to path, or absolute)",
    )
    parser.add_argument("--mention", nargs="*", default=[], help="Identifier(s) to bias ranking toward")
    parser.add_argument(
        "--ext", default=None,
        help="Comma-separated extensions to include, e.g. .py,.ts (default: .py,.js,.jsx,.ts,.tsx,.sh)",
    )
    parser.add_argument("--refresh", action="store_true", help="Force re-ranking instead of reusing the tag cache")
    args = parser.parse_args()

    root = resolve_bounded(args.path)
    exts = {e if e.startswith(".") else f".{e}" for e in args.ext.split(",")} if args.ext else DEFAULT_EXTS
    files = collect_files(root, exts)
    if not files:
        print(f"No files with extensions {sorted(exts)} found under {root}.", file=sys.stderr)
        return

    out = build_repo_map(root, files, tokens=args.tokens, focus=args.focus, mentions=args.mention, refresh=args.refresh)
    print(f"# Repo map: {root}  ({len(files)} files scanned, budget {args.tokens} tokens)\n")
    print(out)


if __name__ == "__main__":
    main()
