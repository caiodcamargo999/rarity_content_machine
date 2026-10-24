#!/usr/bin/env python3
"""
lens_flare.py — procedural lens-flare transition track (brand-coloured).

Renders ONE full-length video (black everywhere except around each transition) that
build_voiceover_reel.py screen-blends over the cut. Each flare is a light source that sweeps
across the frame while the cut happens at its brightest moment, so the edit is hidden inside the
glow — the classic "lens flare transition".

Anatomy of one flare (all in Rarity's palette: warm white + magenta #D50057, so the video's
colour palette stays consistent and the flare never introduces off-brand hues):
  * core         small hot white-warm glow riding the light source
  * bloom        wide magenta glow around it
  * anamorphic   long thin horizontal streak through the source (pink-white)
  * ghosts       soft discs / rings mirrored through the frame centre (the lens internal reflections)
  * wash         full-frame warm-white lift at the peak that covers the cut itself
Intensity follows sin(pi*p)^1.6 over the flare's duration, so it ramps in, peaks mid-cut, and fades.

Run standalone for a quick preview strip:  python3 lens_flare.py preview.png
"""
import math
import subprocess
import sys

import numpy as np

W, H = 540, 960          # rendered at half-res (flares are soft); upscaled when blended
BRAND = np.array([0xD5, 0x00, 0x57], dtype=np.float32) / 255.0
HOT = np.array([0.98, 0.86, 0.80], dtype=np.float32)      # warm off-white (never pure white)
FLARE_STRENGTH = 0.62      # global light level (was 1.0 — Caio: "too lighty")
PINK_WHITE = np.array([0.95, 0.42, 0.66], dtype=np.float32)

_Y, _X = np.mgrid[0:H, 0:W].astype(np.float32)
_X /= H   # normalise both axes by HEIGHT so circles stay circles
_Y /= H
ASPECT = W / H


def _gauss(dx, dy, sx, sy=None):
    sy = sx if sy is None else sy
    return np.exp(-((dx / sx) ** 2 + (dy / sy) ** 2))


def _disc(dx, dy, r, soft=0.012, ring=False):
    d = np.sqrt(dx * dx + dy * dy)
    if ring:
        return np.clip(1 - np.abs(d - r) / soft, 0, 1) ** 1.5
    return np.clip((r - d) / soft + 0.5, 0, 1)


def flare_frame(p, direction=0):
    """p in [0,1] over the flare's life. direction picks the sweep path (0..3)."""
    I = math.sin(math.pi * p) ** 1.6
    if I < 1e-3:
        return None
    paths = [
        ((-0.10, 0.28), (ASPECT + 0.10, 0.62)),   # left-top  -> right-lower
        ((ASPECT + 0.10, 0.30), (-0.10, 0.66)),   # right-top -> left-lower
        ((-0.10, 0.70), (ASPECT + 0.10, 0.30)),   # left-low  -> right-top
        ((ASPECT + 0.10, 0.66), (-0.10, 0.34)),   # right-low -> left-top
    ]
    (x0, y0), (x1, y1) = paths[direction % len(paths)]
    ease = p * p * (3 - 2 * p)
    sx, sy = x0 + (x1 - x0) * ease, y0 + (y1 - y0) * ease
    dx, dy = _X - sx, _Y - sy

    out = np.zeros((H, W, 3), dtype=np.float32)
    core = _gauss(dx, dy, 0.09)[..., None] * HOT * 1.0
    core2 = _gauss(dx, dy, 0.03)[..., None] * HOT * 0.9
    bloom = _gauss(dx, dy, 0.42)[..., None] * (BRAND * 0.92 + HOT * 0.08) * 0.62
    streak = (_gauss(dx, dy, 0.85, 0.010)[..., None] * PINK_WHITE * 1.0
              + _gauss(dx, dy, 0.35, 0.028)[..., None] * HOT * 0.35)
    out += (core + core2 + bloom + streak) * I * FLARE_STRENGTH

    # ghosts: mirrored through the frame centre
    cx, cy = ASPECT / 2, 0.5
    for k, rad, a, tint, ring in ((-0.55, 0.050, 0.35, BRAND, False), (0.40, 0.085, 0.22, PINK_WHITE, True),
                                  (0.85, 0.035, 0.40, HOT, False), (1.35, 0.120, 0.18, BRAND, True),
                                  (1.80, 0.055, 0.25, PINK_WHITE, False)):
        gx, gy = cx + (cx - sx) * k, cy + (cy - sy) * k
        out += _disc(_X - gx, _Y - gy, rad, ring=ring)[..., None] * tint * a * I * FLARE_STRENGTH

    # wash: lift the whole frame near the peak so the cut itself is invisible
    wash = max(0.0, (I - 0.6) / 0.4) ** 1.6 * 0.20   # was 0.74: a tint, not a white-out
    out += wash * (BRAND * 0.75 + HOT * 0.25)
    return np.clip(out, 0.0, 1.0)


def build_flare_track(events, total_dur, out_path, fps=30):
    """events: [{'center': sec, 'dur': sec, 'dir': int}, ...] -> RGB .mov (qtrle) of length total_dur.
    Black outside the events. Blend later with `format=gbrp ... blend=all_mode=screen`."""
    n = int(round(total_dur * fps))
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-c:v", "qtrle", "-pix_fmt", "rgb24", str(out_path)]
    import shutil
    ff = shutil.which("ffmpeg")
    for cand in ("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", "/usr/local/opt/ffmpeg-full/bin/ffmpeg"):
        import os
        if os.path.exists(cand):
            ff = cand
            break
    cmd[0] = ff
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    black = np.zeros((H, W, 3), dtype=np.uint8).tobytes()
    for f in range(n):
        t = f / fps
        frame = None
        for ev in events:
            a = ev["center"] - ev["dur"] / 2
            if a <= t < a + ev["dur"]:
                frame = flare_frame((t - a) / ev["dur"], ev.get("dir", 0))
                break
        proc.stdin.write(black if frame is None else (frame * 255).astype(np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    from PIL import Image
    out = sys.argv[1] if len(sys.argv) > 1 else "flare_preview.png"
    ps = [0.1, 0.25, 0.4, 0.5, 0.6, 0.75, 0.9]
    tiles = []
    for p in ps:
        fr = flare_frame(p, 0)
        tiles.append(Image.fromarray(((fr if fr is not None else np.zeros((H, W, 3))) * 255).astype(np.uint8)).resize((W // 2, H // 2)))
    sheet = Image.new("RGB", (len(tiles) * (W // 2), H // 2))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * (W // 2), 0))
    sheet.save(out)
    print("preview ->", out)
