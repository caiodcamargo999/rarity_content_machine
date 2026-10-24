#!/usr/bin/env python3
"""
dynamic_captions.py — attention-grabbing word-by-word captions for LANDSCAPE VSL / ad edits (1920x1080).

When Caio asks for "dynamic, eye-catching subtitles that grab attention every second" (VSL, 2026-10) the
house MINIMAL caption style (edit_reel) is the wrong tool — that one was chosen for calm Reels. This is
the high-energy house variant, still 100 % Rarity palette:
  * 1-3 UPPERCASE words per caption in Plus Jakarta Sans ExtraBold, white, thick dark outline + soft shadow
  * the word being SPOKEN turns brand magenta and "pops" (overshoot 1.18 -> 1.0 in 3 frames)
  * each new caption slides up 22 px and fades in over 3 frames
  * POWER words (numbers, $, %, ROAS, CAC, MER, P&L, profit, free ...) pop harder (1.28) and get a magenta glow
  * layout is computed once at the settled sizes, so words never jitter or collide; font size is constant
Output: a single RGBA .mov track of the caption BAND only (1920 x BAND_H) to overlay at y = BAND_Y0.
"""
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
BAND_Y0, BAND_H = 690, 330
FONT = str(Path(__file__).resolve().parent.parent / "fonts" / "headline-sans.ttf")   # Plus Jakarta Sans ExtraBold
SIZE = 104
STROKE = 11
MAX_W = int(W * 0.78)
MAX_WORDS = 3
WHITE, MAG = (255, 255, 255), (236, 64, 122)          # magenta lightened ~25 % for contrast on dark footage
POP = (1.18, 1.09, 1.03)
POP_POWER = (1.28, 1.13, 1.04)
POWER = {"roas", "cac", "mer", "ltv", "pl", "profit", "free", "revenue", "million", "billion", "percent", "audit",
         "profitable", "real", "number", "never", "flat", "fee", "hooks", "winners"}

_cache = {}


def font(size):
    k = int(size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONT, k)
    return _cache[k]


def display(raw):
    return raw.strip().strip(".,;:—").upper()


def is_power(raw):
    core = re.sub(r"[^a-z0-9]", "", raw.lower())
    return bool(re.search(r"\d", raw)) or "$" in raw or "%" in raw or core in POWER


def chunk(words):
    """<= MAX_WORDS words, break at sentence/clause punctuation and when too wide at SIZE"""
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    f = font(SIZE)

    def width(ws):
        return probe.textlength(" ".join(display(w["text"]) for w in ws), font=f) + STROKE * 2 * len(ws)

    out, cur = [], []
    for w in words:
        if cur and width(cur + [w]) > MAX_W:
            out.append(cur)
            cur = []
        cur.append(w)
        t = w["text"].rstrip()
        if len(cur) >= MAX_WORDS or (t and t[-1] in ".,;:?!—"):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def render(chunk_words, active, pop=1.0, slide=0.0, alpha=1.0):
    """one RGBA band image (W x BAND_H) for `chunk_words` with word `active` highlighted"""
    texts = [display(w["text"]) for w in chunk_words]
    power = [is_power(w["text"]) for w in chunk_words]
    f = font(SIZE)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    gap = SIZE * 0.42 + STROKE
    widths = [probe.textlength(t, font=f) for t in texts]
    total = sum(widths) + gap * (len(texts) - 1)
    x = (W - total) / 2
    base_y = BAND_H * 0.62 + slide
    layer = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
    d, sd, gd = ImageDraw.Draw(layer), ImageDraw.Draw(shadow), ImageDraw.Draw(glow)
    for i, t in enumerate(texts):
        act = i == active
        sz = SIZE * (pop if act else 1.0)
        ft = font(sz)
        wt = probe.textlength(t, font=ft)
        fx = x + (widths[i] - wt) / 2
        fy = base_y - (sz - SIZE) * 0.45
        col = MAG if act else WHITE
        sd.text((fx, fy + 9), t, font=ft, fill=(0, 0, 0, 215), anchor="ls", stroke_width=STROKE + 3, stroke_fill=(0, 0, 0, 215))
        if act and power[i]:
            gd.text((fx, fy), t, font=ft, fill=(236, 64, 122, 200), anchor="ls", stroke_width=STROKE + 16, stroke_fill=(236, 64, 122, 150))
        d.text((fx, fy), t, font=ft, fill=col + (255,), anchor="ls", stroke_width=STROKE, stroke_fill=(10, 8, 14, 255))
        x += widths[i] + gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(Image.alpha_composite(glow, shadow), layer)
    if alpha < 1.0:
        img.putalpha(img.getchannel("A").point(lambda v: int(v * alpha)))
    return img


def build_frames(words, out_dir):
    """-> [(png, start, end, min_frames)] — per word: 3 pop frames then the settled frame"""
    out_dir = Path(out_dir)
    frames = []
    chunks = chunk(words)
    for ci, ch in enumerate(chunks):
        for wi, w in enumerate(ch):
            start = w["start"]
            nxt = ch[wi + 1]["start"] if wi + 1 < len(ch) else max(w["end"], start + 0.2) + 0.10
            end = max(nxt, start + 0.12)
            pw = is_power(w["text"])
            seq = POP_POWER if pw else POP
            f3 = 1 / 30.0
            for k, sc in enumerate(seq):
                slide = (22 * (1 - (k + 1) / 3)) if wi == 0 else 0.0
                alpha = min(1.0, 0.45 + 0.28 * k) if wi == 0 else 1.0
                p = out_dir / f"c{ci:04d}_{wi}_{k}.png"
                render(ch, wi, sc, slide, alpha).save(p)
                frames.append((p, start + k * f3, start + (k + 1) * f3, 1))
            p = out_dir / f"c{ci:04d}_{wi}_s.png"
            render(ch, wi, 1.0).save(p)
            frames.append((p, start + 3 * f3, max(end, start + 4 * f3), 1))
    return frames


def build_track(frames, total_dur, out_dir, fps=30, ffmpeg="ffmpeg"):
    """concat the PNGs (+ transparent filler) into ONE RGBA qtrle .mov, frame-quantized"""
    out_dir = Path(out_dir)
    blank = out_dir / "blank.png"
    Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0)).save(blank)
    total = int(round(total_dur * fps))
    wins = []
    for png, s, e, mn in frames:
        sf = int(round(s * fps))
        ef = max(int(round(e * fps)), sf + mn)
        wins.append([png, sf, ef])
    prev = 0
    for i, w in enumerate(wins):
        if w[1] < prev:
            w[1] = prev
        if w[2] <= w[1]:
            w[2] = w[1] + 1
        if i + 1 < len(wins):
            gap = wins[i + 1][1] - w[2]
            if 0 < gap <= 9:          # bridge short gaps so the caption doesn't flicker off between words
                w[2] = wins[i + 1][1]
        prev = w[2]
    entries, cur = [], 0
    for png, sf, ef in wins:
        if sf > cur:
            entries.append((blank, (sf - cur) / fps))
        entries.append((png, (ef - sf) / fps))
        cur = ef
    if total > cur:
        entries.append((blank, (total - cur) / fps))
    lst = out_dir / "concat.txt"
    lst.write_text("".join(f"file '{p}'\nduration {d:.5f}\n" for p, d in entries) + f"file '{entries[-1][0]}'\n")
    track = out_dir / "caption_track.mov"
    subprocess.run([ffmpeg, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-r", str(fps),
                    "-fps_mode", "cfr", "-c:v", "qtrle", str(track)], check=True)
    return track


if __name__ == "__main__":
    import sys
    demo = [{"text": t, "start": i * 0.3, "end": i * 0.3 + 0.25} for i, t in enumerate(["We", "help", "brands", "generate", "$5", "million", "in", "verified", "revenue."])]
    ch = chunk(demo)[1]
    bg = Image.new("RGBA", (W, H), (22, 20, 26, 255))
    bg.alpha_composite(render(ch, 1, 1.0), (0, BAND_Y0))
    bg.alpha_composite(render(chunk(demo)[1], 1, 1.3), (0, BAND_Y0 - 330))
    bg.convert("RGB").resize((960, 540)).save(sys.argv[1] if len(sys.argv) > 1 else "dyn_preview.png")
