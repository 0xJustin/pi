"""Videos from matplotlib frames, and stills for reviewing them (an agent cannot watch a video)."""
import io, json, subprocess
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from .palette import BG, INK2


class Writer:
    """Write matplotlib frames to an H.264 MP4 that PowerPoint on a Mac plays (yuv420p, even size, faststart).

        with Writer("out.mp4", fig, fps=30) as w:
            for k in range(n):
                update(k); w.frame()

    Runs check() on the first frame and every `check_every` frames after it, and prints each distinct issue."""

    def __init__(self, path, fig, fps=30, crf=18, check_every=100):
        self.path, self.fig, self.fps, self.crf, self.check_every = Path(path), fig, fps, crf, check_every
        self.n, self.issues = 0, {}

    def __enter__(self):
        self.fig.canvas.draw()
        w, h = self.fig.canvas.get_width_height(physical=True)
        self.proc = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", str(self.fps),
             "-i", "-", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", str(self.crf), "-movflags", "+faststart", str(self.path)], stdin=subprocess.PIPE)
        return self

    def frame(self):
        if self.check_every and self.n % self.check_every == 0:
            from .check import check
            for i in check(self.fig):
                self.issues.setdefault(i, self.n)
        else:
            self.fig.canvas.draw()
        self.proc.stdin.write(np.asarray(self.fig.canvas.buffer_rgba()).tobytes())
        self.n += 1

    def __exit__(self, *exc):
        self.proc.stdin.close()
        self.proc.wait()
        for i, k in self.issues.items():
            print(f"FIGURE CHECK {self.path.name} (first at frame {k}): {i}")
        print(f"wrote {self.path} ({self.n} frames, {self.n / self.fps:.1f} s at {self.fps} fps)")


def _duration(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(mp4)],
                         capture_output=True, check=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])


def _grab(mp4, t, width):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1",
                          "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    return plt.imread(io.BytesIO(raw), format="png")


def poster(mp4, t=None, out=None):
    """One frame as a PNG, for the slide's still and for previews. Default: the middle of the video; t="last" is
    the final frame (the finished figure)."""
    out = Path(out) if out else Path(mp4).with_name(Path(mp4).stem + "_poster.png")
    out.unlink(missing_ok=True)
    if t == "last":   # seek near the end and keep overwriting: -ss at the exact duration yields no frame
        cmd = ["-sseof", "-1", "-i", str(mp4), "-update", "1"]
    else:
        cmd = ["-ss", f"{_duration(mp4) / 2 if t is None else t:.3f}", "-i", str(mp4), "-frames:v", "1"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", *cmd, str(out)], check=True)
    if not out.exists():
        raise ValueError(f"no frame at t={t} in {mp4} (duration {_duration(mp4):.2f} s)")
    return out


def contact_sheet(mp4, n=12, cols=4, width=640, out=None):
    """n evenly spaced frames in a grid, each with its time, so the whole video can be reviewed as one image."""
    d = _duration(mp4)
    ts = [d * (k + 0.5) / n for k in range(n)]
    frames = [_grab(mp4, t, width) for t in ts]
    rows = -(-n // cols)
    h, w = frames[0].shape[:2]
    fig, axs = plt.subplots(rows, cols, figsize=(cols * w / 100, rows * (h + 30) / 100), dpi=100, facecolor=BG)
    for ax in np.ravel(axs):
        ax.axis("off")
    for ax, fr, t in zip(np.ravel(axs), frames, ts):
        ax.imshow(fr)
        ax.set_title(f"{t:.2f} s", color=INK2, fontsize=11, loc="left")
    fig.subplots_adjust(0.005, 0.005, 0.995, 0.97, 0.03, 0.12)
    out = Path(out) if out else Path(mp4).with_name(Path(mp4).stem + "_sheet.png")
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    return out
