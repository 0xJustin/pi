"""Slide geometry, in inches on a 16:9 slide. Figure frames match `fs.slide_figure(width, height)` exactly, so a
figure made for a frame lands on the slide uncropped and at the font sizes the figure check measured."""

W, H = 13.333, 7.5        # PowerPoint widescreen
M = 0.5                   # side margin for text
FIG_TOP = 1.65            # the figure band starts below a two-line claim

# layout name: {placeholder: (x, y, w, h)}. "figure" frames are picture placeholders.
LAYOUTS = {
    "Title": {"title": (M, 2.3, W - 2 * M, 1.7), "subtitle": (M, 4.15, W - 2 * M, 1.2)},
    "Claim + figure": {"title": (M, 0.35, W - 2 * M, 1.1), "figure": (0, FIG_TOP, W, H - FIG_TOP)},
    "Two figures": {"title": (M, 0.35, W - 2 * M, 1.1),
                    "left": (0, FIG_TOP, W / 2, H - FIG_TOP), "right": (W / 2, FIG_TOP, W / 2, H - FIG_TOP)},
    "Figure only": {"figure": (0, 0, W, H)},
    "Claim only": {"title": (M, 0.35, W - 2 * M, 1.1)},
    "Section": {"title": (M, 2.6, W - 2 * M, 1.9)},
    "Recap / asks": {"title": (M, 0.35, W - 2 * M, 1.1),
                     "recap": (M, FIG_TOP, 7.4, H - FIG_TOP - 0.6), "asks": (8.4, FIG_TOP, W - 8.4 - M, H - FIG_TOP - 0.6)},
}
SLIDE_NUMBER = (W - M - 1.0, H - 0.45, 1.0, 0.35)
NUMBERED = {"Claim + figure", "Two figures", "Claim only", "Recap / asks"}

TITLE_PT, SECTION_PT, BODY_PT, SUB_PT, NUMBER_PT = 28, 40, 20, 18, 12


def figure_size(layout, frame="figure"):
    """(width, height) as fractions of the slide, for fs.slide_figure(*figure_size(...))."""
    x, y, w, h = LAYOUTS[layout][frame]
    return round(w / W, 4), round(h / H, 4)
