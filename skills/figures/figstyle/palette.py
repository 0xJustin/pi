"""Colors. One hue per physical-quantity family, from Paul Tol's "light" scheme used as published; grays for
everything that is not a quantity. The five hues were picked from that scheme so every pair stays apart under
simulated deuteranopia, protanopia and tritanopia (worst-pair CIELAB distance >= 19), since any two quantities
may share a panel."""
import matplotlib.colors as mcolors

BG = "#111111"                                      # slide and figure background
INK, INK2, INK3 = "#E6E6E6", "#9A9A9A", "#4A4A4A"   # text; secondary text; reference and context lines (too faint for text)

FAMILIES = {   # family: (hue, quantities that take it)
    "joint angle": ("#77AADD", ["joint angle", "joint position", "joint velocity"]),
    "force & torque": ("#EE8866", ["force", "torque", "joint torque", "leg load", "contact force"]),
    "muscle activation": ("#FFAAAA", ["muscle activation", "muscle force"]),
    "neural activity": ("#AAAA00", ["neural activity", "membrane voltage", "voltage", "firing rate", "spike rate"]),
    "body motion": ("#EEDD88", ["body motion", "forward speed", "speed", "body height", "heading", "turning rate"]),
}
_LOOKUP = {q: hue for fam, (hue, qs) in FAMILIES.items() for q in [fam, *qs]}
HUES = {hue for hue, _ in FAMILIES.values()}


def color_for(quantity):
    """The hue for a physical quantity or its family. An unknown quantity is a design decision for the user."""
    try:
        return _LOOKUP[quantity.lower()]
    except KeyError:
        raise KeyError(f"{quantity!r} has no hue. Families: {', '.join(FAMILIES)}. "
                       "Ask the user which family it belongs to, or whether it needs a new one.") from None


def seq_cmap(quantity):
    """Sequential colormap for a heatmap of one quantity: background at the low end, the quantity's hue at the high end."""
    return mcolors.LinearSegmentedColormap.from_list(quantity, [BG, color_for(quantity)])


def is_gray(color, tol=0.06):
    r, g, b = mcolors.to_rgb(color)
    return max(r, g, b) - min(r, g, b) <= tol


def allowed(color):
    """True for a quantity hue or a gray (the background and inks included)."""
    return is_gray(color) or mcolors.to_hex(color).upper() in {h.upper() for h in HUES}
