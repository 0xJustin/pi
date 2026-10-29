"""Colors. Fixed hues for the quantities that recur across figures and talks, from Paul Tol's "light" scheme used as
published, picked so every pair stays apart under simulated deuteranopia, protanopia and tritanopia (worst-pair
CIELAB distance >= 19). Anything else (an ephemeral quantity, a category, a condition, a paper's convention) takes a
free color chosen for its figure or deck: `free_colors` gives readable ones away from the fixed hues, and
`confusable` says whether a color would read as one of them."""
import colorsys

import matplotlib.colors as mcolors
import numpy as np

BG = "#11100E"                    # slide and figure background: near-black, slightly warm
INK, INK2 = "#F2EDE4", "#D9D2C5"  # cream text; tick labels and panel titles
QUIET = "#9A938A"                 # text meant to recede (a reference's label), and uncolored lines
INK3 = "#4A4541"                  # reference and context lines, axes (too faint for text)

FAMILIES = {   # family: (hue, quantities that take it)
    "joint angle": ("#77AADD", ["joint angle", "joint position", "joint velocity"]),
    "force & torque": ("#EE8866", ["force", "torque", "joint torque", "leg load", "contact force"]),
    "muscle activation": ("#FFAAAA", ["muscle activation", "muscle force"]),
    "neural activity": ("#AAAA00", ["neural activity", "membrane voltage", "voltage", "firing rate", "spike rate"]),
    "body motion": ("#EEDD88", ["body motion", "forward speed", "speed", "body height", "heading", "turning rate"]),
}
_LOOKUP = {q: hue for fam, (hue, qs) in FAMILIES.items() for q in [fam, *qs]}
HUES = {hue for hue, _ in FAMILIES.values()}
INKS = {BG, INK, INK2, QUIET, INK3}


def color_for(quantity):
    """The fixed hue for a recurring quantity or its family."""
    try:
        return _LOOKUP[quantity.lower()]
    except KeyError:
        raise KeyError(f"{quantity!r} has no fixed hue (fixed families: {', '.join(FAMILIES)}). Give it a free "
                       "color (fs.free_colors) and keep that color for it throughout the figure or deck.") from None


def _hue(quantity_or_color):
    return _LOOKUP.get(str(quantity_or_color).lower()) or mcolors.to_hex(quantity_or_color)


def shade(quantity_or_color, f):
    """A tint (f > 0, toward cream) or shade (f < 0, toward the background) of a hue, |f| <= 1: sub-kinds of one
    quantity (e.g. three neuron types' voltages) in gradations of its hue."""
    h = np.array(mcolors.to_rgb(_hue(quantity_or_color)))
    to = np.array(mcolors.to_rgb(INK if f > 0 else BG))
    return mcolors.to_hex((1 - abs(f)) * h + abs(f) * to)


def seq_cmap(quantity_or_color):
    """Sequential colormap for a heatmap of one quantity: background at the low end, its hue at the high end."""
    return mcolors.LinearSegmentedColormap.from_list(str(quantity_or_color), [BG, _hue(quantity_or_color)])


def is_gray(color, tol=0.06):
    r, g, b = mcolors.to_rgb(color)
    return max(r, g, b) - min(r, g, b) <= tol


def contrast(a, b):
    """WCAG contrast ratio between two colors."""
    def lum(c):
        c = np.array(mcolors.to_rgb(c))
        c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# Machado et al. 2009, severity 1.0, in linear RGB (as swatch.py)
_CVD = [np.eye(3),
        np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
        np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
        np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])]


def _lab(rgb_lin):
    x = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ rgb_lin
    x = x / np.array([0.95047, 1.0, 1.08883])
    f = np.where(x > 0.008856, np.cbrt(x), 7.787 * x + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def distance(a, b):
    """Worst-case CIELAB distance between two colors under typical vision and the three deficiencies."""
    lin = lambda c: (lambda v: np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4))(np.array(mcolors.to_rgb(c)))
    la, lb = lin(a), lin(b)
    return min(np.linalg.norm(_lab(np.clip(M @ la, 0, 1)) - _lab(np.clip(M @ lb, 0, 1))) for M in _CVD)


def _is_gradation(color, hue, tol=0.012):
    """True if `color` is a tint or shade of `hue` (as `shade` makes them)."""
    c, h = np.array(mcolors.to_rgb(color)), np.array(mcolors.to_rgb(hue))
    for to in (np.array(mcolors.to_rgb(INK)), np.array(mcolors.to_rgb(BG))):
        d = to - h
        t = np.clip(np.dot(c - h, d) / max(np.dot(d, d), 1e-12), 0, 1)
        if np.linalg.norm(c - (h + t * d)) < tol:
            return True
    return False


def confusable(color, tol=15.0):
    """The fixed family `color` would be mistaken for (another color within `tol` of its hue, not a gradation of
    it), or None."""
    hx = mcolors.to_hex(color).upper()
    for fam, (hue, _) in FAMILIES.items():
        if hx == hue.upper() or _is_gradation(hx, hue):
            return None
    for fam, (hue, _) in FAMILIES.items():
        if distance(hx, hue) < tol:
            return fam
    return None


def free_colors(n, avoid=(), min_contrast=4.5):
    """`n` colors for things without a fixed hue: readable on the background, away from the fixed hues, the inks
    and `avoid`, and spread from each other. Deterministic."""
    fixed = [h for h, _ in FAMILIES.values()] + [INK, INK2, QUIET] + [mcolors.to_hex(a) for a in avoid]
    cands = []
    for h in np.arange(0, 360, 6) / 360:
        for light in (0.6, 0.68, 0.76):
            for sat in (0.55, 0.7, 0.85):
                c = mcolors.to_hex(colorsys.hls_to_rgb(h, light, sat))
                if contrast(c, BG) >= min_contrast:
                    cands.append(c)
    d_fixed = {c: min(distance(c, f) for f in fixed) for c in cands}
    out = []
    for _ in range(n):
        best = max(cands, key=lambda c: min([d_fixed[c]] + [distance(c, o) for o in out]))
        out.append(best)
    return out


def allowed(color):
    """True for a fixed hue, a gray, an ink, a gradation of a fixed hue, or a free color no fixed hue is confused
    with."""
    return is_gray(color) or mcolors.to_hex(color).upper() in {h.upper() for h in HUES | INKS} or confusable(color) is None
