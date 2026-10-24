#!/usr/bin/env python3
"""
vsl_graphics.py — "Limitless-style" VSL layer: MINIMAL captions + glass-card B-roll + floating callouts.

Reference look (Limitless Agency VSL, 2026-10): tiny lowercase white captions under the speaker, full-screen
dark gradient cards with glass panels that pop in word-synced, floating stat / kinetic-text callouts beside the
speaker, white-flash transitions. Rarity palette (plum-black + magenta), Plus Jakarta ExtraBold + Benton.

  minimal_captions(words, out_dir) -> frames for dynamic_captions.build_track
  Scene.frame(t)                    -> PIL RGBA frame of one scene (card = opaque 1920x1080, float = FW x FH region)
"""
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30                    # DESIGN canvas (what the layouts are drawn on)
OUT_W, OUT_H, K = 1920, 1080, 1.0             # delivered size; the design canvas is scaled by K to reach it
FW, FH, FX, FY = 700, 470, 1210, 110          # float region: size on the design canvas, position in OUTPUT pixels
CAP = dict(size=46, band_h=330, band_y0=690, base=255)   # minimal-caption geometry, OUTPUT pixels
HERE = Path(__file__).resolve().parent
BOLD = str(HERE.parent / "fonts" / "headline-sans.ttf")
REG = str(HERE.parent / "fonts" / "BentonSans-Regular.otf")
MAG, MAG_D, GREEN, WHITE = (236, 64, 122), (213, 0, 87), (96, 224, 154), (255, 255, 255)

_fc = {}


def configure(fmt):
    """'landscape' (1920x1080 VSL/ad) or 'vertical' (1080x1920 Reel/ad). Layouts are drawn on a design canvas
    OUT/K and scaled down, so every font size / panel width in this file works unchanged in both formats."""
    global W, H, OUT_W, OUT_H, K, FX, FY, CAP, _bg
    _bg = None
    if fmt == "vertical":
        OUT_W, OUT_H, K = 1080, 1920, 0.78
        W, H = int(round(OUT_W / K)), int(round(OUT_H / K))
        FX, FY = 500, 1130
        CAP = dict(size=54, band_h=300, band_y0=1300, base=210)
    else:
        OUT_W, OUT_H, K = 1920, 1080, 1.0
        W, H = 1920, 1080
        FX, FY = 1210, 110
        CAP = dict(size=46, band_h=330, band_y0=690, base=255)
    return dict(W=OUT_W, H=OUT_H, K=K, FX=FX, FY=FY, CAP=CAP)


def font(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size))
    return _fc[k]


def ease(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def back(x):
    x = min(1.0, max(0.0, x))
    c1, c3 = 1.5, 2.5
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


# ----------------------------------------------------------------------------- minimal captions


def _cap_display(raw):
    return raw.strip().strip(".,;:—").lower()


def minimal_chunks(words, max_words=3, max_chars=26):
    if OUT_W < OUT_H:
        max_chars = 22
    out, cur = [], []
    for w in words:
        if cur and len(" ".join(_cap_display(x["text"]) for x in cur + [w])) > max_chars:
            out.append(cur)
            cur = []
        cur.append(w)
        t = w["text"].rstrip()
        if len(cur) >= max_words or (t and t[-1] in ".,;:?!—"):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def _cap_render(ch, shown, fade):
    """ch words, `shown` = how many are visible, the last visible one at alpha `fade`"""
    f = font(REG, CAP['size'])
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    texts = [_cap_display(w["text"]) for w in ch]
    space = probe.textlength(" ", font=f) * 1.15
    widths = [probe.textlength(t, font=f) for t in texts]
    total = sum(widths) + space * (len(texts) - 1)
    x = (OUT_W - total) / 2
    base_y = CAP['base']
    txt = Image.new("RGBA", (OUT_W, CAP['band_h']), (0, 0, 0, 0))
    sh = Image.new("RGBA", (OUT_W, CAP['band_h']), (0, 0, 0, 0))
    d, sd = ImageDraw.Draw(txt), ImageDraw.Draw(sh)
    for i, t in enumerate(texts):
        if i < shown:
            a = fade if i == shown - 1 else 1.0
            d.text((x, base_y), t, font=f, fill=(255, 255, 255, int(255 * a)), anchor="ls")
            sd.text((x, base_y + 3), t, font=f, fill=(0, 0, 0, int(210 * a)), anchor="ls", stroke_width=3, stroke_fill=(0, 0, 0, int(210 * a)))
        x += widths[i] + space
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    return Image.alpha_composite(sh, txt)


def minimal_captions(words, out_dir):
    """-> [(png, start, end, min_frames)]; words appear one by one (3-frame fade), chunk clears at the next chunk"""
    out_dir = Path(out_dir)
    frames = []
    chunks = minimal_chunks(words)
    for ci, ch in enumerate(chunks):
        for wi, w in enumerate(ch):
            start = w["start"]
            last = wi + 1 == len(ch)
            end = max(w["end"] + 0.12, start + 0.2) if last else ch[wi + 1]["start"]
            for k, a in enumerate((0.35, 0.7)):
                p = out_dir / f"m{ci:04d}_{wi}_{k}.png"
                _cap_render(ch, wi + 1, a).save(p)
                frames.append((p, start + k / 30.0, start + (k + 1) / 30.0, 1))
            p = out_dir / f"m{ci:04d}_{wi}_s.png"
            _cap_render(ch, wi + 1, 1.0).save(p)
            frames.append((p, start + 2 / 30.0, max(end, start + 3 / 30.0), 1))
    return frames


# ----------------------------------------------------------------------------- backgrounds / panels
_bg = None


def bg_crop(t):
    global _bg
    if _bg is None:
        bw, bh = W + 200, H + 120
        y, x = np.mgrid[0:bh, 0:bw].astype(np.float32)
        base = np.zeros((bh, bw, 3), np.float32) + np.array([11, 6, 21], np.float32)

        def blob(cx, cy, r, col, k):
            d = np.hypot(x - cx, y - cy) / r
            return np.exp(-d * d)[..., None] * np.array(col, np.float32) * k

        base += blob(bw * 0.10, bh * 1.00, 760, MAG_D, 0.62)
        base += blob(bw * 0.92, bh * 0.02, 700, (84, 30, 170), 0.62)
        base += blob(bw * 0.55, bh * 0.55, 1000, (62, 12, 64), 0.40)
        _bg = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    dx = int(100 + 90 * math.sin(t * 0.45))
    dy = int(60 + 50 * math.cos(t * 0.35))
    return _bg.crop((dx, dy, dx + W, dy + H))


def panel(w, h, radius=34, hl=False, tone=None):
    """glass panel RGBA with 40px margin for the glow -> (img, pad)"""
    pad = 44
    img = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    box = (pad, pad, pad + w, pad + h)
    col = tone or MAG_D
    if hl:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).rounded_rectangle(box, radius, fill=col + (190,))
        img = Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius, fill=(col + (84,)) if hl else (255, 255, 255, 26),
                        outline=(255, 255, 255, 235) if hl else (255, 255, 255, 120), width=2)
    # soft top highlight
    hi = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi).rounded_rectangle((pad + 3, pad + 3, pad + w - 3, pad + h * 0.45), radius, fill=(255, 255, 255, 12))
    return Image.alpha_composite(img, hi), pad


def check_icon(d, cx, cy, r, col=MAG_D):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col + (255,))
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.4), (cx + r * 0.5, cy - r * 0.35)], fill=WHITE + (255,),
           width=max(4, int(r * 0.22)), joint="curve")


def cross_icon(d, cx, cy, r, col=(255, 255, 255)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (200,), width=3)
    k = r * 0.42
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=col + (230,), width=4)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=col + (230,), width=4)


# ----------------------------------------------------------------------------- items
class Item:
    """layer (PIL RGBA, drawn once) or fn(tl)->RGBA (per frame); centred on (cx, cy); pops in at t0"""

    def __init__(self, t0, cx, cy, layer=None, fn=None, t1=None, anim="pop", dur=0.30):
        self.t0, self.cx, self.cy, self.layer, self.fn, self.t1, self.anim, self.dur = t0, cx, cy, layer, fn, t1, anim, dur

    def draw(self, canvas, t):
        if t < self.t0 or (self.t1 is not None and t > self.t1):
            return
        p = (t - self.t0) / self.dur
        e = ease(p)
        lay = self.fn(t - self.t0) if self.fn else self.layer
        if self.anim == "pop":
            s = 0.80 + 0.20 * back(p)
            dy = 0
        elif self.anim == "slide":
            s, dy = 1.0, 30 * (1 - e)
        else:
            s, dy = 1.0, 0
        if abs(s - 1.0) > 0.004:
            lay = lay.resize((max(2, int(lay.width * s)), max(2, int(lay.height * s))), Image.BICUBIC)
        if e < 0.999:
            lay = lay.copy()
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * e)))
        x = int(self.cx - lay.width / 2)
        y = int(self.cy - lay.height / 2 + dy)
        x, y = max(0, x), max(0, y)
        canvas.alpha_composite(lay, (x, y))


def text_img(txt, path, size, fill=WHITE, glow=None, pad=36, alpha=255):
    f = font(path, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = probe.textlength(txt, font=f)
    img = Image.new("RGBA", (int(tw) + 2 * pad, int(size * 1.5) + 2 * pad), (0, 0, 0, 0))
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).text((img.width / 2, img.height / 2), txt, font=f, fill=glow + (200,), anchor="mm", stroke_width=10, stroke_fill=glow + (160,))
        img = Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(20)))
    ImageDraw.Draw(img).text((img.width / 2, img.height / 2), txt, font=f, fill=fill + (alpha,), anchor="mm")
    return img


def chip(label, size=44, hl=False, icon=None, sub=None, min_w=0):
    f = font(BOLD, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = probe.textlength(label, font=f)
    ic = size * 1.1 if icon else 0
    w = int(max(min_w, tw + ic + size * 1.6 + (size * 0.5 if icon else 0)))
    h = int(size * 2.1 + (size * 0.55 if sub else 0))
    img, pad = panel(w, h, radius=int(h * 0.5), hl=hl)
    d = ImageDraw.Draw(img)
    x = pad + size * 0.8
    cy = pad + h / 2 - (size * 0.25 if sub else 0)
    if icon == "check":
        check_icon(d, x + ic / 2, cy, ic / 2)
    elif icon == "cross":
        cross_icon(d, x + ic / 2, cy, ic / 2)
    if icon:
        x += ic + size * 0.5
    d.text((x, cy), label, font=f, fill=WHITE + (255,), anchor="lm")
    if sub:
        d.text((x, pad + h - size * 0.72), sub, font=font(REG, int(size * 0.5)), fill=(255, 255, 255, 170), anchor="lm")
    return img


def label_item(t0, txt, cx, cy, size=30, col=MAG, anim="slide"):
    f = font(REG, size)
    spaced = " ".join(txt.upper())
    spaced = re.sub(r"  +", "   ", spaced)
    img = text_img(spaced, REG, size, fill=col, pad=14)
    return Item(t0, cx, cy, layer=img, anim=anim)


def big_item(t0, txt, cx, cy, size=150, glow=None, fill=WHITE, anim="pop", dur=0.34):
    return Item(t0, cx, cy, layer=text_img(txt, BOLD, size, fill=fill, glow=glow, pad=60), anim=anim, dur=dur)


def strike_item(t0, t_strike, txt, cx, cy, size=300):
    base = text_img(txt, BOLD, size, pad=70)
    f = font(BOLD, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = probe.textlength(txt, font=f)

    def fn(tl):
        lay = base.copy()
        p = ease((tl - (t_strike - t0)) / 0.30)
        if p > 0:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * (1 - 0.55 * p))))
            d = ImageDraw.Draw(lay)
            x0 = lay.width / 2 - tw / 2 - 40
            x1 = x0 + (tw + 80) * p
            d.line([(x0, lay.height / 2 + 4), (x1, lay.height / 2 + 4)], fill=MAG + (255,), width=int(size * 0.075))
        return lay
    return Item(t0, cx, cy, fn=fn, anim="pop", dur=0.34)


def row_item(t0, label, value, cx, cy, w=1180, hl=False, icon=None, count_to=None, prefix="$", dur=0.34):
    h = 118
    base, pad = panel(w, h, radius=40, hl=hl)
    fl, fv = font(BOLD, 40), font(BOLD, 66)

    def fn(tl):
        img = base.copy()
        d = ImageDraw.Draw(img)
        x = pad + 46
        if icon == "check":
            check_icon(d, x + 26, pad + h / 2, 26)
            x += 76
        d.text((x, pad + h / 2), label, font=fl, fill=WHITE + (255,), anchor="lm")
        if value is not None or count_to is not None:
            v = value
            if count_to is not None:
                p = ease(tl / 0.7)
                v = f"{prefix}{int(round(count_to * p)):,}"
            d.text((pad + w - 46, pad + h / 2), v, font=fv, fill=(MAG if not hl else WHITE) + (255,), anchor="rm")
        return img
    return Item(t0, cx, cy, fn=fn, dur=dur)


def chip_item(t0, label, cx, cy, size=44, hl=False, icon=None, sub=None, anim="pop"):
    return Item(t0, cx, cy, layer=chip(label, size, hl, icon, sub), anim=anim)


def flow_chips(entries, cy, size=46, gap=26, max_w=1500, row_gap=34, icon=None):
    """entries [(t0, label, hl)] -> centred rows of chips -> [Item]"""
    imgs = [(t0, chip(label, size, hl, icon)) for t0, label, hl in entries]
    rows, cur, cw = [], [], 0
    for t0, im in imgs:
        if cur and cw + im.width + gap > max_w:
            rows.append(cur)
            cur, cw = [], 0
        cur.append((t0, im))
        cw += im.width + gap
    if cur:
        rows.append(cur)
    rh = imgs[0][1].height
    top = cy - (len(rows) * rh + (len(rows) - 1) * row_gap) / 2 + rh / 2
    out = []
    for r, row in enumerate(rows):
        tw = sum(im.width for _, im in row) + gap * (len(row) - 1)
        x = W / 2 - tw / 2
        for t0, im in row:
            out.append(Item(t0, x + im.width / 2, top + r * (rh + row_gap), layer=im))
            x += im.width + gap
    return out


def stack_rows(rows, cy=500, gap=24, w=1180):
    """rows [(t0, label, value, kw)] -> Items vertically centred"""
    n = len(rows)
    rh = 118 + 88
    top = cy - ((n - 1) * (118 + gap)) / 2
    return [row_item(t0, label, val, W / 2, top + i * (118 + gap), w=w, **kw) for i, (t0, label, val, kw) in enumerate(rows)]


def compare_item(t0, t_good, t_bad, t_line, good, bad, line, cx=W / 2, cy=520):
    """two horizontal bars vs a dashed MAX CAC line"""
    BW, BH = 1100, 92
    x0 = cx - BW / 2
    scale = BW / (bad * 1.18)
    fl, fb = font(BOLD, 38), font(BOLD, 56)

    def fn(tl):
        t = t0 + tl
        img = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for (ts, val, col, lab, verdict, y) in ((t_good, good, GREEN, f"PAYING ${good}", "ROOM TO SCALE", 90),
                                                 (t_bad, bad, MAG_D, f"PAYING ${bad}", "BIGGER LOSSES", 330)):
            if t < ts:
                continue
            p = ease((t - ts) / 0.7)
            d.text((x0, y - 34), lab, font=fl, fill=(255, 255, 255, 200), anchor="ls")
            d.rounded_rectangle((x0, y, x0 + BW, y + BH), 46, fill=(255, 255, 255, 24), outline=(255, 255, 255, 90), width=2)
            wv = max(BH, val * scale * p)
            d.rounded_rectangle((x0, y, x0 + wv, y + BH), 46, fill=col + (255,))
            d.text((x0 + wv - 36 if wv > 300 else x0 + wv + 24, y + BH / 2), f"${int(val * p)}", font=fb,
                   fill=WHITE + (255,), anchor="rm" if wv > 300 else "lm")
            if p > 0.95:
                d.text((x0, y + BH + 52), verdict, font=fl, fill=col + (255,), anchor="ls")
        if t >= t_line:
            p = ease((t - t_line) / 0.4)
            lx = x0 + line * scale
            for yy in range(40, int(40 + 470 * p), 26):
                d.line([(lx, yy), (lx, yy + 14)], fill=WHITE + (235,), width=4)
            d.text((lx, 22), f"MAX CAC  ${line}", font=fl, fill=WHITE + (255,), anchor="mm")
        return img
    return Item(t0, cx, cy, fn=fn, anim="fade", dur=0.2)


# ----------------------------------------------------------------------------- floating callouts
def float_stat(t0, t1, value, label, count_from=0, prefix="$"):
    """ring + counting number + rising jagged line (Limitless-style), in the float region"""
    rng = np.random.RandomState(int(value) * 7 + 3)
    pts = []
    n = 26
    for i in range(n):
        pts.append((40 + i * (FW - 120) / (n - 1), 380 - i * 8.2 - rng.uniform(-24, 24) * (0.4 + i / n)))
    f = font(BOLD, 78)

    def fn(tl):
        img = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        p = ease(tl / 0.9)
        v = int(round(count_from + (value - count_from) * p))
        d.ellipse((40, 36, 96, 92), outline=MAG + (255,), width=8)
        d.text((126, 66), f"{prefix}{v:,}", font=f, fill=WHITE + (255,), anchor="lm")
        d.text((128, 128), label.upper(), font=font(REG, 27), fill=(255, 255, 255, 190), anchor="lm")
        k = max(2, int(len(pts) * ease(tl / 1.0)))
        glow = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        ImageDraw.Draw(glow).line(pts[:k], fill=MAG + (255,), width=16, joint="curve")
        img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(12)))
        ImageDraw.Draw(img).line(pts[:k], fill=MAG + (255,), width=7, joint="curve")
        return img
    return Item(0, FW / 2, FH / 2, fn=fn, anim="none")


def float_text(small, lines, strike_small=False):
    """small italic-ish line above, bold stacked lines below, right aligned (kinetic text callout)"""
    f1, f2 = font(REG, 32), font(BOLD, 84)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

    def fn(tl):
        img = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x = FW - 30
        y = 120
        if small:
            tw = probe.textlength(small, font=f1)
            d.text((x, y), small, font=f1, fill=(255, 255, 255, 200), anchor="rs")
            if strike_small:
                p = ease((tl - 0.35) / 0.25)
                d.line([(x - tw, y - 11), (x - tw + tw * p, y - 11)], fill=MAG + (255,), width=5)
        for i, ln in enumerate(lines):
            p = ease((tl - 0.08 * i) / 0.30)
            sh = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
            ImageDraw.Draw(sh).text((x, y + 82 + i * 92 + 5 + (1 - p) * 26), ln, font=f2, fill=(0, 0, 0, int(190 * p)), anchor="rs")
            img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(7)))
            ImageDraw.Draw(img).text((x, y + 82 + i * 92 + (1 - p) * 26), ln, font=f2, fill=(255, 255, 255, int(255 * p)), anchor="rs")
        return img
    return Item(0, FW / 2, FH / 2, fn=fn, anim="none")


# ----------------------------------------------------------------------------- scene
class Scene:
    def __init__(self, name, t0, t1, kind, items, intro=True, outro=True):
        self.name, self.t0, self.t1, self.kind, self.items, self.intro, self.outro = name, t0, t1, kind, items, intro, outro

    @property
    def dur(self):
        return self.t1 - self.t0

    def frame(self, tl):
        t = self.t0 + tl
        if self.kind == "card":
            cv = bg_crop(tl)
            for it in self.items:
                it.draw(cv, t)
            if self.intro and tl < 0.34:
                a = (1 - tl / 0.34) ** 2 * 0.92
                cv.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * a))))
            q = tl - (self.dur - 0.2)
            if self.outro and q > 0:
                cv.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * min(1, q / 0.2) ** 1.5))))
            return cv.convert("RGB")
        cv = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
        for it in self.items:
            cv.alpha_composite(it.fn(tl))
        fade = min(1.0, tl / 0.22, (self.dur - tl) / 0.22)
        if fade < 1.0:
            cv.putalpha(cv.getchannel("A").point(lambda v: int(v * max(0.0, fade))))
        return cv

    def out_size(self):
        return (OUT_W, OUT_H) if self.kind == "card" else (int(round(FW * K)), int(round(FH * K)))

    def frame_out(self, tl):
        """frame(tl) scaled from the design canvas to the delivered size"""
        im = self.frame(tl)
        size = self.out_size()
        return im if im.size == size else im.resize(size, Image.BICUBIC)
