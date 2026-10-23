---
name: figures
description: Make every figure, plot, chart, animation or video for the user in their visual language (dark background, color reserved for physical quantities, Figtree) and critique the rendered result before showing it — right chart for the question, no clipped or overlapping text, labeled axes with units, no internal ids as labels. Use every time you produce a figure or video for the user, including quick diagnostic plots, not only when asked to polish one.
---

# Figures

Figures and slides share one visual language, so a figure can go from an analysis session onto a slide
unchanged. A plotting call that runs is not a figure that communicates: overlap, clipping and the wrong chart
are visible only in the rendered image. So every figure goes through the loop below before the user sees it.

## Code

```python
import sys, os; sys.path.insert(0, os.path.expanduser("~/.pi/agent/skills/figures"))
import figstyle as fs
fs.apply()                                   # style for every figure after this
fig = fs.slide_figure()                      # made at its size on a 16:9 slide, so points are real points
ax.plot(t, angle, color=fs.color_for("joint angle"))
fs.save(fig, "name.png")                     # runs fs.check and prints every issue, then saves
```

Any venv with matplotlib and numpy works; videos also need `ffmpeg`. `fs.slide_figure(width, height)` takes
fractions of the slide; a figure made at another size passes `placed_width=` (inches on the slide) to `fs.save`
so font sizes are checked at the size they will be seen.

## The visual language

- **Dark background** (`fs.BG`, near-black and slightly warm). Slides are dark, and the user's PI reads them in
  dark mode.
- **Color means a physical quantity.** One hue per family, the same in every figure and talk:

  | family | quantities |
  |---|---|
  | joint angle | joint angle, joint position, joint velocity |
  | force & torque | joint torque, leg load, contact force |
  | muscle activation | muscle activation, muscle force |
  | neural activity | membrane voltage, firing rate |
  | body motion | forward speed, body height, heading, turning rate |

  `fs.color_for(quantity)` returns the hue; a heatmap of one quantity uses `fs.seq_cmap(quantity)` (background at
  zero, the hue at the top). A quantity not in the table raises: ask the user which family it joins. The hues
  stay apart under the common color-vision deficiencies (`python swatch.py out.png` shows them).
- **Everything else is warm gray.** Reference data (the fly) is a thick `fs.INK3` line behind the model. Text is
  cream `fs.INK`; tick labels and panel titles `fs.INK2`; only text meant to recede (the reference's label)
  `fs.QUIET`. An uncolored `plot` comes out `fs.QUIET`, so color is always a choice.
- **Models and conditions are told apart by position**: one row or panel each, the same reference in gray
  behind every one (small multiples), named by a direct label beside the row or at the line's end. No legends
  when a direct label fits. Color is never the only cue.
- **Categories that need color but are not quantities** (neuron superclasses, sensor classes, behaviors): ask
  the user before choosing colors. Paper figures on a light background are not defined yet: ask.
- **Figtree** for all text (bundled in `fonts/`; the user installs the same files for PowerPoint).
- **Soft shapes**: round line caps and joins (set by `fs.apply`); in diagrams, rounded boxes and open
  chevron arrowheads with round ends, never sharp filled triangles.
- **Panel titles name the quantity and its unit**, left-aligned: "body height (mm)". The y label lives in the
  title; small multiples sharing a y axis carry it once, on the top panel. The finding belongs in the slide or
  caption, never in the panel title; slide figures carry no figure title or subtitle.
- **No chart junk**: no top or right spines, no gridlines unless values are read off them, no legend frames, no
  decorative color, no internal ids.

## The loop

1. **Is this the right chart for the question?** Fix this before styling; no styling rescues the wrong family.
   - One bar, or a bar chart with one category, is almost never right: one number is text or an annotated
     point; one number with uncertainty is an error bar or a distribution.
   - Categories compared → bars or dots. Change over an ordered variable (time, epoch, dose) → line.
     Two continuous variables → scatter (a trend line only if you mean to claim one). One distribution →
     histogram, density or violin, only with enough data for a shape. Part of a whole → stacked bar or pie only
     when the parts sum to something meaningful and are few.
   - Position on a common axis and length are read far more accurately than angle, area or color; the number
     that matters most goes on position.
2. **Make it at its placed size and save with `fs.save`.** Read every printed issue. Fix it, or say in your
   reply why a flagged item is right (e.g. a dimensionless label). The checks: text off the figure edge, text on
   text, text running into another panel, axes with numbers but no label or unit, text under 12 pt on the
   slide, faint text, labels that look like internal ids, colors that are not a quantity hue or a gray, the
   wrong background.
3. **Look at the rendered PNG** (Read the file), not the code. Check what the code cannot:
   - data drawn so densely that elements merge (needs faceting, fewer series, or transparency, not cosmetics);
   - tick spacing that does not match the data's granularity;
   - categories in a meaningful order (by value or a natural sequence), not load order;
   - wasted space and panel spacing; labels that collide with data;
   - that the figure shows the one thing it is for, and the eye lands there first.
4. **Labels name what things are.** A hash, a run id, a `snake_case` name, a file path or a checkpoint label
   becomes the attribute it stands for (the architecture, the condition, the parameter value). If you cannot
   tell what an identifier means, ask or leave it out; never guess a label.
5. **Repeat until nothing fires.** A judgment call the checklist does not settle (is this chart type
   defensible, is this title too specific): say what you are unsure about and ask.

Do not show a figure the loop has not passed. If you hand one over with a known issue, name it.

## Videos

- `fs.Writer(path, fig, fps)` writes matplotlib frames to an H.264 MP4 that PowerPoint on a Mac plays, and
  runs the checks on frames as it goes (labels that move into clipping mid-video show up here).
- You cannot watch a video. Review `fs.contact_sheet(mp4)` (evenly spaced frames with their times) with the
  same loop: is what the video is for visible, does anything clip or collide at any time, does the motion read.
- Give a still for the slide and for previews: `fs.poster(mp4, t)` at the frame that shows the point.
- If playback is not real time, say the speed on the frame (e.g. "4× slower").

## Handing over

Save under the home directory (not `/tmp`) so the user's Mac can open it, and give plain `~/sim_workspace/…` or
`~/brain/…` paths; `showplot` opens them (the `show-plot` skill).

## Files

- `figstyle/`: `palette.py` (hues, grays, `color_for`, `seq_cmap`), `style.py` (`apply`, `slide_figure`, `save`),
  `check.py` (`check`), `video.py` (`Writer`, `poster`, `contact_sheet`).
- `swatch.py`: the hues under simulated color-vision deficiencies. `fonts/`: Figtree and its license (OFL).
