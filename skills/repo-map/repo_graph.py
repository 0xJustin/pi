#!/usr/bin/env python3
"""Tier-1 module-level import-dependency graph for a single Python package.

Unlike ``repo_map.py`` (aider's ranked *signatures*, whose edges come from bare
identifier-name matching and are noisy across packages), this resolves **real
Python imports** with the ast module, so every edge is a genuine
``module -> module`` dependency inside ONE package. It emits:

  * ``<name>.modules.mmd``  — Mermaid, module-level (detailed), clustered by subpackage
  * ``<name>.clusters.mmd`` — Mermaid, subpackage-level (the broad map)
  * ``<name>.dot`` / ``.png`` — Graphviz module-level (PNG if ``dot`` is installed)
  * ``<name>.json``         — nodes (module, file, cluster, in_degree, pagerank) + edges

Scope is bounded to ``~/brain`` and ``~/song_workspace`` (same as repo_map.py).
Point ``path`` at the *package directory* (the one holding ``__init__.py``), e.g.
``staging/synaptix/synaptix`` or ``drosophilax/src/drosophilax``.
"""
from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ALLOWED_ROOTS = [(Path.home() / "brain").resolve(), (Path.home() / "song_workspace").resolve()]
SKIP_DIR_NAMES = {"__pycache__", ".venv", ".git", ".claude", "node_modules", "dist", "build"}


def resolve_bounded(path_str: str) -> Path:
    target = Path(path_str).expanduser().resolve()
    for root in ALLOWED_ROOTS:
        if target == root or root in target.parents:
            return target
    allowed = ", ".join(str(r) for r in ALLOWED_ROOTS)
    raise SystemExit(f"Refusing: {target} is outside the allowed roots ({allowed}).")


def _skip(rel_parts) -> bool:
    return any(p.startswith(".") or p in SKIP_DIR_NAMES or p.endswith("egg-info") for p in rel_parts)


def discover_modules(pkg_dir: Path) -> dict[str, Path]:
    """``module_name -> file`` for every module in the package (``base = pkg.parent``)."""
    base = pkg_dir.parent
    mods: dict[str, Path] = {}
    for p in pkg_dir.rglob("*.py"):
        rel = p.relative_to(base)
        if _skip(rel.parts[:-1]):
            continue
        mod = ".".join(rel.with_suffix("").parts)
        if mod.endswith(".__init__"):
            mod = mod[: -len(".__init__")]
        mods[mod] = p
    return mods


def _resolve_relative(module: str, level: int, cur_mod: str) -> str:
    if not level:
        return module
    base = cur_mod.split(".")
    base = base[:-level] if level <= len(base) else []
    return ".".join(base + ([module] if module else []))


def build_edges(mods: dict[str, Path]) -> set[tuple[str, str]]:
    """Intra-package ``src_mod -> dst_mod`` edges from resolved imports."""
    edges: set[tuple[str, str]] = set()
    for cur_mod, p in mods.items():
        try:
            tree = ast.parse(p.read_text())
        except (SyntaxError, UnicodeDecodeError):
            continue
        for n in ast.walk(tree):
            targets: list[str] = []
            if isinstance(n, ast.Import):
                targets = [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                base = _resolve_relative(n.module or "", n.level, cur_mod)
                targets = [base] + [f"{base}.{a.name}" for a in n.names]
            for t in targets:
                parts = t.split(".")
                for i in range(len(parts), 0, -1):
                    cand = ".".join(parts[:i])
                    if cand in mods and cand != cur_mod:
                        edges.add((cur_mod, cand))
                        break
    return edges


def cluster_of(module: str, pkg_name: str, depth: int) -> str:
    """Subpackage bucket: first ``depth`` components below the top package."""
    parts = module.split(".")
    if parts[0] != pkg_name:
        return parts[0]
    sub = parts[1 : 1 + depth]
    return f"{pkg_name}." + ".".join(sub) if sub else f"{pkg_name} (root)"


def pagerank(nodes, edges):
    try:
        import networkx as nx
    except ImportError:
        return {n: 0.0 for n in nodes}
    g = nx.DiGraph()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)
    try:
        return nx.pagerank(g) if g.number_of_edges() else {n: 0.0 for n in nodes}
    except Exception:
        return {n: 0.0 for n in nodes}


def _mid(module: str) -> str:
    return "n_" + module.replace(".", "_").replace("-", "_")


def _short(module: str, pkg_name: str) -> str:
    return module[len(pkg_name) + 1 :] if module.startswith(pkg_name + ".") else module


def restrict_pathway(edges, focus, to, mods):
    """Keep only nodes on a path involving the focus/to modules (prefix match)."""
    def match(sel):
        return {m for m in mods if sel and (m == sel or m.startswith(sel + "."))}

    keep = set()
    if focus:
        seeds = match(focus)
        # forward + backward reachability from seeds over the edge set
        fwd, bwd = defaultdict(set), defaultdict(set)
        for u, v in edges:
            fwd[u].add(v); bwd[v].add(u)
        def walk(seed, adj):
            seen, stack = set(), [seed]
            while stack:
                x = stack.pop()
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y); stack.append(y)
            return seen
        for s in seeds:
            keep |= {s} | walk(s, fwd) | walk(s, bwd)
    return keep


def render_mermaid_modules(mods, edges, clusters, pr, pkg_name, keep=None) -> str:
    nodes = keep if keep is not None else set(mods)
    by_cluster = defaultdict(list)
    for m in nodes:
        by_cluster[clusters[m]].append(m)
    lines = ["```mermaid", "flowchart LR"]
    for ci, (cl, members) in enumerate(sorted(by_cluster.items())):
        lines.append(f'  subgraph c{ci}["{cl}"]')
        for m in sorted(members):
            lines.append(f'    {_mid(m)}["{_short(m, pkg_name)}"]')
        lines.append("  end")
    for u, v in sorted(edges):
        if u in nodes and v in nodes:
            lines.append(f"  {_mid(u)} --> {_mid(v)}")
    lines.append("```")
    return "\n".join(lines)


def render_mermaid_clusters(edges, clusters, node_pr) -> str:
    cl_edges = defaultdict(int)
    for u, v in edges:
        cu, cv = clusters[u], clusters[v]
        if cu != cv:
            cl_edges[(cu, cv)] += 1
    cl_weight = defaultdict(float)
    for n, r in node_pr.items():
        cl_weight[clusters[n]] += r
    lines = ["```mermaid", "flowchart LR"]
    seen = set()
    for (cu, cv) in cl_edges:
        seen.add(cu); seen.add(cv)
    for cl in sorted(set(clusters.values()) | seen):
        cid = "g_" + cl.replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "")
        lines.append(f'  {cid}["{cl}"]')
    for (cu, cv), w in sorted(cl_edges.items()):
        a = "g_" + cu.replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "")
        b = "g_" + cv.replace(".", "_").replace(" ", "_").replace("(", "").replace(")", "")
        lines.append(f"  {a} -->|{w}| {b}")
    lines.append("```")
    return "\n".join(lines)


def render_dot(mods, edges, clusters, pr, pkg_name, keep=None) -> str:
    nodes = keep if keep is not None else set(mods)
    by_cluster = defaultdict(list)
    for m in nodes:
        by_cluster[clusters[m]].append(m)
    out = ["digraph G {", "  rankdir=LR;", '  node [shape=box, style=rounded, fontsize=10];']
    for ci, (cl, members) in enumerate(sorted(by_cluster.items())):
        out.append(f'  subgraph cluster_{ci} {{ label="{cl}"; style=rounded; color="#8888aa";')
        for m in sorted(members):
            pw = 1 + 3 * (pr.get(m, 0.0) / (max(pr.values()) or 1))
            out.append(f'    "{m}" [label="{_short(m, pkg_name)}", penwidth={pw:.2f}];')
        out.append("  }")
    for u, v in sorted(edges):
        if u in nodes and v in nodes:
            out.append(f'  "{u}" -> "{v}";')
    out.append("}")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="Package directory (holds __init__.py), under ~/brain or ~/song_workspace")
    ap.add_argument("--out", required=True, help="Output directory (created if missing)")
    ap.add_argument("--name", default=None, help="Artifact basename (default: package name)")
    ap.add_argument("--cluster-depth", type=int, default=1, help="Subpackage grouping depth (default: 1)")
    ap.add_argument("--focus", default=None, help="Restrict module graph to a pathway through this module prefix")
    ap.add_argument("--png", action="store_true", help="Also render PNG via graphviz `dot` if available")
    args = ap.parse_args()

    pkg_dir = resolve_bounded(args.path)
    pkg_name = pkg_dir.name
    name = args.name or pkg_name
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    mods = discover_modules(pkg_dir)
    if not mods:
        raise SystemExit(f"No modules found under {pkg_dir}")
    edges = build_edges(mods)
    clusters = {m: cluster_of(m, pkg_name, args.cluster_depth) for m in mods}
    pr = pagerank(list(mods), edges)
    indeg = defaultdict(int)
    for _, v in edges:
        indeg[v] += 1

    keep = None
    if args.focus:
        keep = restrict_pathway(edges, args.focus, None, mods)
        if not keep:
            print(f"warning: focus '{args.focus}' matched nothing", file=sys.stderr)

    (out / f"{name}.modules.mmd").write_text(
        render_mermaid_modules(mods, edges, clusters, pr, pkg_name, keep))
    (out / f"{name}.clusters.mmd").write_text(
        render_mermaid_clusters(edges, clusters, pr))
    dot = render_dot(mods, edges, clusters, pr, pkg_name, keep)
    (out / f"{name}.dot").write_text(dot)

    graph = {
        "package": pkg_name,
        "package_dir": str(pkg_dir),
        "n_modules": len(mods),
        "n_edges": len(edges),
        "clusters": sorted(set(clusters.values())),
        "nodes": [
            {"module": m, "file": str(mods[m]), "cluster": clusters[m],
             "in_degree": indeg[m], "pagerank": round(pr.get(m, 0.0), 5)}
            for m in sorted(mods)
        ],
        "edges": sorted([list(e) for e in edges]),
    }
    (out / f"{name}.json").write_text(json.dumps(graph, indent=2))

    if args.png and shutil.which("dot"):
        png = out / f"{name}.png"
        subprocess.run(["dot", "-Tpng", "-o", str(png)], input=dot, text=True, check=False)

    print(f"package   : {pkg_name}  ({len(mods)} modules, {len(edges)} intra edges)")
    print(f"clusters  : {len(set(clusters.values()))}")
    print(f"out dir   : {out}")
    print("top modules by pagerank:")
    for m in sorted(mods, key=lambda x: -pr.get(x, 0.0))[:12]:
        print(f"  {pr.get(m,0.0):.4f}  in={indeg[m]:<3} {m}")


if __name__ == "__main__":
    main()
