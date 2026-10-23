"""Render a deck to PNGs (one per slide) and a contact sheet, with the same fonts PowerPoint will use, so the
rendered slide can be looked at. LibreOffice draws text close to PowerPoint, not identically: leave slack."""
import glob, os, shutil, subprocess, tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTS = SKILL.parent / "figures" / "fonts"
CACHE = Path.home() / ".cache" / "slidestyle"


def soffice():
    found = os.environ.get("SOFFICE") or shutil.which("soffice") or \
        next(iter(sorted(glob.glob(str(Path.home() / "apps/libreoffice-*/opt/libreoffice*/program/soffice")))), None)
    if not found:
        raise FileNotFoundError("LibreOffice not found: set SOFFICE to its soffice binary")
    return found


def _env():
    """LibreOffice finds fonts through fontconfig: add the bundled Figtree to the system configuration."""
    CACHE.mkdir(parents=True, exist_ok=True)
    conf = CACHE / "fonts.conf"
    conf.write_text(f"""<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig><include ignore_missing="yes">/etc/fonts/fonts.conf</include><dir>{FONTS}</dir>
<cachedir>{CACHE / "fc"}</cachedir></fontconfig>""")
    return {**os.environ, "FONTCONFIG_FILE": str(conf), "SAL_USE_VCLPLUGIN": "svp"}


def to_pdf(pptx, out_dir):
    with tempfile.TemporaryDirectory(dir=CACHE.parent) as profile:   # private profile: runs never collide
        subprocess.run([soffice(), f"-env:UserInstallation=file://{profile}", "--headless", "--norestore",
                        "--convert-to", "pdf", "--outdir", str(out_dir), str(pptx)],
                       env=_env(), check=True, capture_output=True, timeout=300)
    return Path(out_dir) / (Path(pptx).stem + ".pdf")


def render(pptx, out_dir=None, dpi=110):
    """Slide PNGs in out_dir (default: <deck>_render/ beside the deck), plus sheet.png with every slide."""
    pptx = Path(pptx).resolve()
    out = Path(out_dir) if out_dir else pptx.with_name(pptx.stem + "_render")
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    pdf = to_pdf(pptx, out)
    # PDF -> PNG through PyMuPDF in a throwaway uv environment (nothing installed into the user's Pythons)
    script = ("import sys, pymupdf\n"
              "d = pymupdf.open(sys.argv[1])\n"
              "for k, p in enumerate(d):\n"
              "    p.get_pixmap(dpi=int(sys.argv[3])).save(f'{sys.argv[2]}/slide-{k + 1:02d}.png')\n")
    subprocess.run(["uv", "run", "--quiet", "--no-project", "--with", "pymupdf", "python", "-c", script,
                    str(pdf), str(out), str(dpi)], check=True, timeout=300)
    pdf.unlink()
    pngs = sorted(out.glob("slide-*.png"))
    sheet(pngs, out / "sheet.png")
    return pngs


def sheet(pngs, path, cols=3):
    """Every slide in one image, numbered, to compare titles and layouts across the deck."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = -(-len(pngs) // cols)
    fig, axs = plt.subplots(rows, cols, figsize=(cols * 4.4, rows * 2.75), facecolor="#000000", squeeze=False)
    for ax in axs.ravel():
        ax.axis("off")
    for k, (ax, p) in enumerate(zip(axs.ravel(), pngs)):
        ax.imshow(plt.imread(p))
        ax.set_title(str(k + 1), color="#9A9A9A", fontsize=11, loc="left")
    fig.subplots_adjust(0.01, 0.01, 0.99, 0.97, 0.04, 0.12)
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path
