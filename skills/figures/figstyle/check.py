"""Mechanical checks on a drawn figure: what can be measured without judgment. Looking at the image is still required."""
import itertools, re
import matplotlib.colors as mcolors
import matplotlib.text as mtext
from .palette import BG, allowed

ID_PATTERNS = [
    (r"\b(?=[a-z0-9]*\d)(?=[a-z0-9]*[a-z])[a-z0-9]{7,}\b", "a run or hash id"),
    (r"\b[a-z]+-(?=[a-z0-9]*\d)[a-z0-9]{4}\b", "a node id"),
    (r"\b[A-Za-z0-9]+_[A-Za-z0-9_]+\b", "a snake_case name"),
    (r"\S+\.(py|npz|npy|csv|json|pkl|pt|ckpt|h5|parquet|mp4|png|yaml)\b", "a file name"),
    (r"\b(ckpt|checkpoint)\b", "a checkpoint name"),
]


def _lum(c):
    rgb = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in mcolors.to_rgb(c)]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def _contrast(a, b):
    la, lb = sorted([_lum(a), _lum(b)])
    return (lb + 0.05) / (la + 0.05)


def _in_range(v, lim):
    lo, hi = sorted(lim)
    return lo - 1e-9 * (hi - lo) <= v <= hi + 1e-9 * (hi - lo)


def _ticklabels(ax, which):
    axis, lim, k = (ax.xaxis, ax.get_xlim(), 0) if which == "x" else (ax.yaxis, ax.get_ylim(), 1)
    if not axis.get_visible():
        return []
    return [t for t in axis.get_ticklabels() if t.get_visible() and t.get_text().strip() and _in_range(t.get_position()[k], lim)]


def _texts(fig):
    """(text, owning axes or None, kind) for every text that is drawn."""
    out = []
    for ax in fig.axes:
        if not ax.get_visible():
            continue
        if ax.axison:
            out += [(t, ax, "tick label") for w in "xy" for t in _ticklabels(ax, w)]
            out += [(a.label, ax, "axis label") for a in (ax.xaxis, ax.yaxis) if a.get_visible()]
            out += [(a.get_offset_text(), ax, "offset") for a in (ax.xaxis, ax.yaxis) if a.get_visible()]
        out += [(t, ax, "title") for t in (ax.title, ax._left_title, ax._right_title)]
        out += [(t, ax, "text") for t in ax.texts]
        if ax.get_legend():
            out += [(t, ax, "legend") for t in ax.get_legend().get_texts()]
    out += [(t, None, "figure text") for t in fig.texts]
    for lg in fig.legends:
        out += [(t, None, "legend") for t in lg.get_texts()]
    return [(t, a, k) for t, a, k in out if t.get_visible() and t.get_text().strip() and t.get_alpha() != 0]


def _labels(ax):
    """Title and y label of this panel and of every panel sharing its y axis (small multiples label once)."""
    sib = ax.get_shared_y_axes().get_siblings(ax)
    return [x for a in [ax, *sib] for x in (a.get_title(), a.get_title("left"), a.get_ylabel()) if x]


def _name(ax):
    if ax is None:
        return "the figure"
    t = ax.get_title() or ax.get_title("left") or ax.get_ylabel()
    if t:
        return f"panel '{t}'"
    shared = _labels(ax)
    return f"a panel under '{shared[0]}'" if shared else f"panel {ax.get_figure().axes.index(ax) + 1}"


def _has_data(ax):
    return any(a.get_visible() for a in [*ax.lines, *ax.collections, *ax.images, *ax.patches])


def check(fig, placed_width=None, min_pt=12, edges=True):
    """Issues as sentences. `placed_width`: inches the figure will occupy on the slide (default: its own width).
    `edges=False` skips the figure-edge test (for bbox_inches="tight")."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    scale = (placed_width or fig.get_figwidth()) / fig.get_figwidth()
    texts = [(t, a, k, mtext.Text.get_window_extent(t, r)) for t, a, k in _texts(fig)]
    issues = []
    q = lambda t: repr(t.get_text()[:40])

    # text running off the figure
    W, H = fig.bbox.width, fig.bbox.height
    for t, a, k, b in texts if edges else []:
        off = [s for s, v in (("left", -b.x0), ("right", b.x1 - W), ("bottom", -b.y0), ("top", b.y1 - H)) if v > 1]
        if off:
            issues.append(f"{k} {q(t)} in {_name(a)} runs off the {' and '.join(off)} edge")

    # text on text
    for (t1, a1, k1, b1), (t2, a2, k2, b2) in itertools.combinations(texts, 2):
        w = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
        h = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
        if w > 1.5 and h > 1.5:
            issues.append(f"{k1} {q(t1)} overlaps {k2} {q(t2)} ({_name(a1)})")

    # text running into another panel's plotting area
    panels = [ax for ax in fig.axes if ax.get_visible() and ax.axison]
    for t, a, k, b in texts:
        for ax in panels:
            if ax is a or (a is not None and (ax.bbox.bounds == a.bbox.bounds or
                                              (ax.bbox.x0 <= a.bbox.x0 and ax.bbox.x1 >= a.bbox.x1 and
                                               ax.bbox.y0 <= a.bbox.y0 and ax.bbox.y1 >= a.bbox.y1))):
                continue   # own panel, a twin, or the panel this inset sits in
            if b.overlaps(ax.bbox) and min(b.x1, ax.bbox.x1) - max(b.x0, ax.bbox.x0) > 1.5 \
                    and min(b.y1, ax.bbox.y1) - max(b.y0, ax.bbox.y0) > 1.5:
                issues.append(f"{k} {q(t)} from {_name(a)} runs into {_name(ax)}")

    # axes without labels or units
    for ax in panels:
        if not _has_data(ax):
            continue
        if _ticklabels(ax, "x") and not ax.get_xlabel():
            issues.append(f"{_name(ax)}: x axis has numbers but no label")
        if _ticklabels(ax, "y") and not any("(" in x for x in _labels(ax)) and not ax.get_ylabel():
            issues.append(f"{_name(ax)}: y axis has numbers but no label (put it in the panel title with units)")
        for lab in [ax.get_xlabel()] + ([ax.get_ylabel()] if ax.get_ylabel() else []):
            if lab and "(" not in lab:
                issues.append(f"{_name(ax)}: label {lab!r} has no unit in parentheses (fine if dimensionless)")

    # size at slide scale, contrast, internal ids
    small = [(t, t.get_fontsize() * scale) for t, a, k, b in texts if t.get_fontsize() * scale < min_pt]
    if small:
        t, s = min(small, key=lambda x: x[1])
        issues.append(f"{len(small)} texts under {min_pt} pt on the slide; smallest {s:.1f} pt ({q(t)})")
    bg = fig.get_facecolor()
    for t, a, k, b in texts:
        need = 3.0 if t.get_fontsize() * scale >= 18 else 4.5
        c = _contrast(t.get_color(), bg)
        if c < need:
            issues.append(f"{k} {q(t)} is faint on the background ({c:.1f}:1, needs {need}:1)")
        for pat, what in ID_PATTERNS:
            if re.search(pat, t.get_text()):
                issues.append(f"{k} {q(t)} looks like {what}; name what it stands for")
                break

    # color means a physical quantity
    seen = {}
    def note(c, where):
        if c is None or (isinstance(c, str) and c == "none") or mcolors.to_rgba(c)[3] == 0:
            return
        if not allowed(c):
            seen.setdefault(mcolors.to_hex(c), set()).add(where)
    for ax in fig.axes:
        for ln in ax.lines:
            if ln.get_visible():
                note(ln.get_color(), _name(ax))
        for col in ax.collections:
            if col.get_visible() and col.get_array() is None:
                for c in [*col.get_facecolor(), *col.get_edgecolor()]:
                    note(tuple(c), _name(ax))
        for p in ax.patches:
            if p.get_visible():
                note(p.get_facecolor(), _name(ax)); note(p.get_edgecolor(), _name(ax))
    for p in [*fig.patches, *fig.lines]:
        note(p.get_facecolor() if hasattr(p, "get_facecolor") else p.get_color(), "the figure")
    for t, a, k, b in texts:
        note(t.get_color(), _name(a))
    for hx, where in seen.items():
        issues.append(f"color {hx} in {', '.join(sorted(where))} is not a quantity hue or a gray")
    if mcolors.to_hex(bg) != mcolors.to_hex(BG):
        issues.append(f"figure background {mcolors.to_hex(bg)} is not the slide background {BG}")
    return issues
