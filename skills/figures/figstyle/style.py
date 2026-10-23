"""The dark slide style: Figtree, sizes in real points at slide scale, no chart junk."""
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
from cycler import cycler
from matplotlib import font_manager
from .palette import BG, INK, INK2, INK3, QUIET

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"
SLIDE_W, SLIDE_H = 13.333, 7.5   # 16:9 PowerPoint slide, inches


def apply(size=16):
    """Set the style for every figure made after this call. `size` is body text in points on the slide."""
    for f in FONT_DIR.glob("*.ttf"):
        font_manager.fontManager.addfont(str(f))
    plt.rcParams.update({
        "font.family": "Figtree", "font.size": size,
        "axes.titlesize": size, "axes.labelsize": size, "xtick.labelsize": size - 2, "ytick.labelsize": size - 2,
        "legend.fontsize": size - 2, "legend.frameon": False,
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG, "savefig.dpi": 200,
        "text.color": INK, "axes.labelcolor": INK2, "axes.titlecolor": INK2, "axes.titlelocation": "left",
        "axes.edgecolor": INK3, "xtick.color": INK2, "ytick.color": INK2,
        "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
        "axes.prop_cycle": cycler(color=[QUIET]),   # an uncolored line is gray: color is always a choice
        "image.cmap": "gray", "lines.linewidth": 2.2, "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round", "lines.dash_capstyle": "round",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",   # editable text in Illustrator
    })


def slide_figure(width=1.0, height=0.78, **kw):
    """A figure at the size it will have on a 16:9 slide (fractions of the slide), so points are real points.
    The default height leaves room for a slide title."""
    return plt.figure(figsize=(SLIDE_W * width, SLIDE_H * height), **kw)


def save(fig, path, placed_width=None, **kw):
    """Check the figure, print every issue, then save it. Returns the issues."""
    from .check import check
    issues = check(fig, placed_width=placed_width, edges=kw.get("bbox_inches") != "tight")
    for i in issues:
        print(f"FIGURE CHECK {Path(path).name}: {i}")
    fig.savefig(path, **kw)
    return issues
