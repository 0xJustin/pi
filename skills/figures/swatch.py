"""Render the quantity hues on the slide background under typical vision and simulated color-vision deficiencies.
usage: python swatch.py OUT.png"""
import sys
from pathlib import Path
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, str(Path(__file__).resolve().parent))
import figstyle as fs
from figstyle.check import _contrast

CVD = {"typical": np.eye(3),   # Machado et al. 2009, severity 1.0, in linear RGB
       "deuteranopia": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
       "protanopia": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
       "tritanopia": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]])}
lin = lambda c: np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
gam = lambda c: np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.clip(c, 0, 1) ** (1 / 2.4) - 0.055)
sim = lambda h, M: tuple(np.clip(gam(M @ lin(np.array(matplotlib.colors.to_rgb(h)))), 0, 1))

fs.apply(14)
fig = plt.figure(figsize=(14, 1.2 + 0.9 * len(fs.FAMILIES)))
n = len(fs.FAMILIES); tt = np.linspace(0, 1, 200); row = lambda i: 1 - (i + 1.5) / (n + 1.5)
for j, v in enumerate(CVD):
    fig.text(0.42 + 0.145 * j, row(-0.6), v, color=fs.INK2)
for i, (fam, (hue, qs)) in enumerate(fs.FAMILIES.items()):
    y = row(i)
    fig.text(0.02, y, fam, color=hue, va="bottom", fontsize=16)
    fig.text(0.02, y, ", ".join(q for q in qs if q != fam), color=fs.INK2, va="top", fontsize=13)
    fig.text(0.375, y, f"{_contrast(hue, fs.BG):.1f}:1", color=fs.INK2, va="center")
    for j, M in enumerate(CVD.values()):
        ax = fig.add_axes([0.42 + 0.145 * j, y - 0.2 / (n + 1.5), 0.12, 0.4 / (n + 1.5)]); ax.axis("off")
        ax.plot(tt, np.sin(2 * np.pi * (2 * tt + 0.3 * i)), color=sim(hue, M), lw=3)
for i in fs.check(fig):
    if not i.startswith("color "):   # the simulated colors are off-palette by design
        print("FIGURE CHECK:", i)
fig.savefig(sys.argv[1]); print(sys.argv[1])
