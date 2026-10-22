---
name: slides
description: Build every slide deck, weekly-meeting update or talk for the user on their dark PowerPoint template (Source Sans 3, one claim per slide, figures from the figures skill) and check the rendered slides before handing over. Use whenever you make or add to a .pptx, deck, slides or presentation for the user, in place of pptxgenjs or any generic theme.
---

# Slides

A deck should read as the user's own work: the argument and the figures carry it, and nothing in the styling
says an agent assembled it. Slides share the figures' visual language (the `figures` skill): same background,
inks, typeface and quantity colors, and figure frames sized so a figure drops in uncropped. The user fine-tunes
the result in PowerPoint, so build on the template's layouts and placeholders, never with free-floating boxes
where a layout exists.

## Code

```python
import sys, os; sys.path.insert(0, os.path.expanduser("~/.pi/agent/skills/slides"))
from slidestyle.deck import Deck
from slidestyle.render import render
d = Deck()                                  # Deck("weekly.pptx") adds to an existing deck on this template
d.title("Connectome-constrained walking", "Justin Ellis-Joyce · Turaga lab · 22 October 2026")
d.claim_figure("The connectome-constrained model falls 0.31 s into the clip", "falls.png", notes="…")
d.save("talk.pptx")                         # runs the slide checks and prints every issue
render("talk.pptx")                         # talk_render/slide-NN.png and sheet.png
```

Runs with the system `python3` (python-pptx, matplotlib). `render` uses LibreOffice from `~/apps/libreoffice-*`
(or `$SOFFICE`) and PyMuPDF through `uv`, with the bundled fonts.

## Layouts

| layout | method | figure made with |
|---|---|---|
| Title | `d.title(title, subtitle)` | |
| Section | `d.section(title)` | |
| Claim + figure | `d.claim_figure(claim, png_or_mp4)` | `fs.slide_figure(1.0, 0.78)` |
| Two figures | `d.two_figures(claim, left, right)` | `fs.slide_figure(0.5, 0.78)` each |
| Figure only | `d.figure(png_or_mp4)` | `fs.slide_figure(1.0, 1.0)` |
| Claim only | `d.claim(claim)` returns the slide, for content composed by hand | |
| Recap / asks | `d.recap_asks(claim, recap, asks)` (items are strings; a nested list holds sub-items) | |

Make each figure with the `figures` skill at exactly its frame's size; a figure made at another size gets
cropped. An MP4 goes in like a PNG (`poster=` sets its still; default the middle frame).

## Writing the slides

- **The title is the claim**: one full sentence, at most two lines, no period. "The connectome-constrained model
  falls 0.31 s into the clip", not "Fall analysis". Read the titles in order: they should be the talk's argument.
- **One claim per slide**, and the slide's figure is the evidence for exactly that claim. A number in a claim
  must be visible in that slide's figure. What the speaker says beyond the claim goes in `notes=`.
- **Mature talks** may drop titles (`d.figure`) and let the figure speak; the claim moves to the notes.
- **Name things as the project does**: models, conditions and quantities by their exact names, no internal ids.
- **Weekly running deck**: newest week first. Open the existing deck with `Deck(path)`, add the week's block
  (a section slide with the date, the strongest result first, then `recap_asks` with specific asks), and
  `d.move(new_slides, 1)` to put it right after the title slide.
- **Never add what makes a deck read as generated**: small all-caps labels above titles, lines or bars under
  titles or along edges, icons in circles, cards with colored borders, "Agenda", "Key takeaways" or "Thank you"
  slides, bullet lists standing in for a figure, emoji, centered body text, decorative color or gradients.
  Text is `INK` or the gray `INK2`; color only marks a physical quantity.

## The loop

1. **Save with `d.save`** and read every `SLIDE CHECK` line. Fix it, or say in your reply why it is right. The
   checks: text overflowing its box (measured with the real font), claims over two lines or ending in a period,
   text under 14 pt, fonts other than Source Sans 3, text colors off the palette, internal ids, empty placeholders
   and figure frames, figures cropped to fit (made at the wrong size), figures under 150 dpi on the slide,
   shapes off the slide, overlapping text boxes, slides over 40 words (Recap / asks excepted), layouts not from
   this template. `python -m slidestyle.check deck.pptx` runs them on a deck edited by hand.
2. **Render and look** (Read `sheet.png` for the whole deck, then each changed slide). Look for what the checks
   cannot see: does the eye land on the evidence for the claim; do titles sit at the same place on every slide of a
   layout; is the figure readable at this size; does the order of titles make the argument.
3. **Repeat until nothing fires.** LibreOffice draws text close to PowerPoint but not identically: a line that only
   just fits in the render may wrap in PowerPoint, so leave slack.

Do not hand over a deck the loop has not passed. If you hand one over with a known issue, name it.

## Handing over

Save under the home directory (not `/tmp`) and give a plain `~/sim_workspace/…` or `~/brain/…` path; the user
opens it in PowerPoint on the Mac. Give the render's `sheet.png` path too.

## Files

- `slidestyle/`: `deck.py` (`Deck`), `check.py` (`check`), `render.py` (`render`, `sheet`), `layouts.py` (frames
  in inches, `figure_size`), `build_template.py` (writes the template).
- `template/dark.pptx` (what `Deck` builds on) and `template/dark.potx` (for the user's PowerPoint). Both are
  generated: change colors in `../figures/figstyle/palette.py` or frames in `layouts.py`, then
  `python3 -m slidestyle.build_template` from this directory.
