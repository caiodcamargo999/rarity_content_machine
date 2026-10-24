#!/usr/bin/env python3
"""
motion_graphics.py — speech-synced motion graphics for talking-head Reels (Rarity house style).

A "beat" is a small animated card that explains WHAT THE SPEAKER IS SAYING at the exact moment he
says it (bars rising when he says "escala o investimento", three platform chips when he lists
"Meta, Google, Klaviyo", a checklist ticking as he lists what the call delivers...). Beats are
declared in a JSON spec with times in the ORIGINAL video's clock plus word anchors; the caller
remaps them through the edit's cut map before rendering.

Rendering: every frame is drawn at 2x and downsampled (smooth edges), into a 1080x{ZONE_H}
strip that is overlaid at y = ZONE_Y0 (so the overlay track stays small and fast). The strip sits
BELOW the speaker's face and ABOVE the captions (face ≈ y 130-660, captions baseline y 1330).

House style: translucent deep-plum cards (#1a0f2e), brand off-white text (#efeeea), BentonSans for
labels, Playfair Display Bold Italic for emphasised words, brand magenta (#D50057, lightened for
contrast) as the ONLY saturated colour. Motion: ease-out-back pop-in (slide 34 px + fade), 0.2 s fade
out, draw-on lines, rising bars, counters — nothing loops, nothing flashes.

Spec (list of beats):
  {"type": "strike", "start": 4.2, "end": 6.4, "anchors": {"strike": 5.6}, "text": {...}}
Types: strike, bars, bank, credits, sum, channels, lupa, cac, call, checklist.
Add a new type by writing a `beat_<type>(cv, t, dur, a, p)` function and registering it in BEATS.
"""
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = 1080
ZONE_Y0, ZONE_H = 1120, 290
S = 2  # supersample

FONTS = Path(__file__).resolve().parent.parent / "fonts"
BENTON = str(FONTS / "BentonSans-Regular.otf")
PLAYFAIR_I = str(FONTS / "headline-italic.ttf")

OFFWHITE = (239, 238, 234)
PLUM = (26, 15, 46)
MAGENTA = (213, 0, 87)
MAGENTA_L = (232, 77, 128)       # legible magenta (brand magenta lightened ~30 %)
MUTED = (167, 172, 203)          # brand "muted" #a7accb

_font_cache = {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, int(size * S))
    return _font_cache[k]


def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out_cubic(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def ease_out_back(x, k=1.45):
    x = clamp01(x)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


class Cv:
    """1x-coordinate drawing API over a 2x RGBA canvas, with a global alpha/offset for the beat."""

    def __init__(self, h=None):
        self.h = h or ZONE_H
        self.img = Image.new("RGBA", (W * S, self.h * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.alpha = 1.0
        self.dy = 0.0

    # --- helpers
    def _c(self, rgb, a=255):
        return (*rgb, int(a * self.alpha))

    def _p(self, x, y):
        return (x * S, (y + self.dy) * S)

    def rect(self, x0, y0, x1, y1, fill, a=255, r=0, outline=None, width=1):
        x0, y0 = self._p(x0, y0)
        x1, y1 = self._p(x1, y1)
        self.d.rounded_rectangle((x0, y0, x1, y1), radius=r * S, fill=self._c(fill, a),
                                 outline=self._c(outline, 90) if outline else None, width=int(width * S))

    def ellipse(self, cx, cy, rx, ry, fill=None, a=255, outline=None, width=2):
        x, y = self._p(cx, cy)
        self.d.ellipse((x - rx * S, y - ry * S, x + rx * S, y + ry * S),
                       fill=self._c(fill, a) if fill else None,
                       outline=self._c(outline, a) if outline else None, width=int(width * S))

    def line(self, pts, fill, width=4, a=255):
        pp = [self._p(x, y) for x, y in pts]
        self.d.line(pp, fill=self._c(fill, a), width=int(width * S), joint="curve")
        for (x, y) in (pp[0], pp[-1]):
            r = width * S / 2
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=self._c(fill, a))

    def polygon(self, pts, fill, a=255):
        self.d.polygon([self._p(x, y) for x, y in pts], fill=self._c(fill, a))

    def arc(self, cx, cy, r, start, end, fill, width=10, a=255):
        x, y = self._p(cx, cy)
        self.d.arc((x - r * S, y - r * S, x + r * S, y + r * S), start, end, fill=self._c(fill, a), width=int(width * S))

    def text(self, x, y, s, f, fill=OFFWHITE, a=255, anchor="ls"):
        px, py = self._p(x, y)
        self.d.text((px, py), s, font=f, fill=self._c(fill, a), anchor=anchor)

    def tw(self, s, f):
        return self.d.textlength(s, font=f) / S

    def card(self, x0, y0, x1, y1, r=34):
        """translucent plum glass card with soft shadow + hairline"""
        sh = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        a0, b0 = self._p(x0, y0 + 10)
        a1, b1 = self._p(x1, y1 + 10)
        ImageDraw.Draw(sh).rounded_rectangle((a0, b0, a1, b1), radius=r * S, fill=(0, 0, 0, int(120 * self.alpha)))
        sh = sh.filter(ImageFilter.GaussianBlur(22))
        self.img = Image.alpha_composite(self.img, sh)
        self.d = ImageDraw.Draw(self.img)
        self.rect(x0, y0, x1, y1, PLUM, a=222, r=r, outline=OFFWHITE, width=1.4)

    def done(self):
        return self.img.resize((W, self.h), Image.LANCZOS)


# ------------------------------------------------------------------------------------------
# beats. t = seconds since the beat started (output clock), dur = beat length, a = anchors
# (seconds since beat start), p = free-form params from the spec.  All beats are LOWER-THIRD
# strips (card ≈ 1000 x 270 px) because in the speaker's zoomed-in shots his chin reaches
# y ≈ 1110 of 1920 — anything taller would cover his mouth.
# ------------------------------------------------------------------------------------------
def fade_state(t, dur, tin=0.34, tout=0.22):
    inn = ease_out_back(t / tin)
    alpha = clamp01(t / (tin * 0.6)) * clamp01((dur - t) / tout)
    return alpha, (1 - inn) * 34


def at(a, name, default=0.0):
    return a.get(name, default)


CARD = (40, 8, 1040, 282)


def beat_strike(cv, t, dur, a, p):
    """BIG word + a label that gets struck through (the 'error')."""
    cv.card(*CARD)
    big, label = p.get("big", "ROAS"), p.get("label", "métrica principal")
    fb = font(PLAYFAIR_I, 138)
    cv.text(90, 190, big, fb, MAGENTA_L)
    lx = 90 + cv.tw(big, fb) + 50
    f = font(BENTON, 52)
    cv.text(lx, 150, label, f, OFFWHITE)
    cv.text(lx, 208, p.get("sub", "o erro da loja virtual"), font(BENTON, 34), MUTED)
    k = ease_in_out((t - at(a, "strike", 1.0)) / 0.45)
    if k > 0:
        w = cv.tw(label, f)
        cv.line([(lx - 6, 133), (lx - 6 + (w + 12) * k, 133)], MAGENTA_L, width=7)


def beat_bars(cv, t, dur, a, p):
    """investment bars rise; ROAS up-pill pops when he says 'bate o ROAS'"""
    cv.card(*CARD)
    cv.text(90, 62, p.get("title", "investimento"), font(BENTON, 32), MUTED)
    n, base = 8, 246
    for i in range(n):
        k = ease_out_cubic((t - 0.25 - i * 0.14) / 0.5)
        h = (34 + i * 17) * k
        x = 90 + i * 52
        cv.rect(x, base - h, x + 34, base, MAGENTA_L if i == n - 1 else (92, 52, 120), r=8)
    k = ease_out_back((t - at(a, "pill", 2.0)) / 0.4)
    if k > 0:
        s_ = 0.6 + 0.4 * clamp01(k)
        cx, cy = 770, 145
        cv.rect(cx - 190 * s_, cy - 62 * s_, cx + 190 * s_, cy + 62 * s_, MAGENTA, r=62, a=int(255 * clamp01(k)))
        cv.text(cx - 96 * s_, cy + 20 * s_, "ROAS", font(BENTON, int(60 * s_)), OFFWHITE)
        ax = cx + 100 * s_
        cv.polygon([(ax, cy + 22 * s_), (ax + 34 * s_, cy - 26 * s_), (ax + 68 * s_, cy + 22 * s_)], OFFWHITE)


def beat_bank(cv, t, dur, a, p):
    """conta bancária: R$ 0 and a flat line"""
    cv.card(*CARD)
    cv.text(90, 72, p.get("title", "conta bancária"), font(BENTON, 36), MUTED)
    k = ease_out_cubic(t / 0.5)
    cv.text(90, 224, "R$ 0", font(BENTON, 124), OFFWHITE, a=int(255 * k))
    g = ease_in_out((t - 0.3) / 0.8)
    cv.line([(560, 190), (560 + 420 * g, 190)], MAGENTA_L, width=6)
    n0 = at(a, "nada", 1.0)
    if t > n0:
        cv.text(560, 150, p.get("nada_text", "nada."), font(PLAYFAIR_I, 70), MAGENTA_L, a=int(255 * clamp01((t - n0) / 0.25)))


def _chip(cv, cx, cy, label, sub, k, w0=290, h0=104):
    if k <= 0:
        return
    s_ = 0.7 + 0.3 * clamp01(k)
    w, h = w0 * s_, h0 * s_
    al = int(255 * clamp01(k))
    cv.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, (46, 28, 78), r=28 * s_, a=al, outline=OFFWHITE)
    cv.text(cx, cy + (2 if sub else 14) * s_, label, font(BENTON, int(46 * s_)), OFFWHITE, a=al, anchor="ms")
    if sub:
        cv.text(cx, cy + 36 * s_, sub, font(BENTON, int(26 * s_)), MAGENTA_L, a=al, anchor="ms")


def beat_credits(cv, t, dur, a, p):
    """Meta / Google / Klaviyo all take credit for the same sale"""
    cv.card(*CARD)
    names = p.get("names", ["Meta", "Google", "Klaviyo"])
    xs = [200, 540, 880]
    for i, (nm, x) in enumerate(zip(names, xs)):
        t0 = at(a, f"c{i}", 0.3 + i * 0.5)
        _chip(cv, x, 90, nm, p.get("credit", "crédito"), ease_out_back((t - t0) / 0.4))
        g = ease_in_out((t - t0 - 0.25) / 0.45)
        if g > 0:
            x1, y1, x2, y2 = x, 146, 540 + (x - 540) * 0.30, 206
            cv.line([(x1, y1), (x1 + (x2 - x1) * g, y1 + (y2 - y1) * g)], MAGENTA_L, width=5)
    k = ease_out_back((t - at(a, "sale", 0.9)) / 0.4)
    if k > 0:
        al = int(255 * clamp01(k))
        cv.rect(400, 206, 680, 266, (60, 36, 100), r=30, a=al, outline=OFFWHITE)
        cv.text(540, 248, p.get("sale", "1 venda"), font(BENTON, 40), OFFWHITE, a=al, anchor="ms")


def beat_sum(cv, t, dur, a, p):
    """sum of platform credits is longer than what Shopify shows"""
    cv.card(*CARD)
    parts = p.get("parts", ["Meta", "Google", "Klaviyo"])
    x = 90
    for i, nm in enumerate(parts):
        k = ease_out_cubic((t - 0.2 - i * 0.25) / 0.45)
        w = 250 * k
        cv.rect(x, 52, x + w, 112, [(120, 66, 150), (168, 60, 130), MAGENTA_L][i % 3], r=10)
        if k > 0.7:
            cv.text(x + w / 2, 93, nm, font(BENTON, 32), OFFWHITE, anchor="ms")
        x += w + 6
    cv.text(90, 150, p.get("left", "soma das plataformas"), font(BENTON, 28), MUTED)
    k2 = ease_out_cubic((t - at(a, "shopify", 1.4)) / 0.6)
    cv.rect(90, 180, 90 + 520 * k2, 238, (96, 96, 124), r=10)
    cv.text(90, 268, "Shopify", font(BENTON, 28), MUTED)
    if k2 > 0.6:
        al = int(255 * clamp01((t - at(a, 'shopify', 1.4) - 0.3) / 0.35))
        note = p.get("note", "mostra menos")
        size, x_note = 52, 650
        while size > 28 and cv.tw(note, font(PLAYFAIR_I, size)) > (CARD[2] - 30) - x_note:   # never overflow the card
            size -= 2
        cv.text(x_note, 224, note, font(PLAYFAIR_I, size), MAGENTA_L, a=al)


def beat_channels(cv, t, dur, a, p):
    """every channel looks like a winner while the DRE line stays flat"""
    cv.card(*CARD)
    names = p.get("names", ["Meta", "Google", "Klaviyo"])
    for i, nm in enumerate(names):
        k = ease_out_back((t - 0.2 - i * 0.18) / 0.4)
        cx = 200 + i * 340
        _chip(cv, cx, 82, nm, "", k, w0=290, h0=80)
        if k > 0.5:  # little up-triangle badge
            al = int(255 * clamp01(k))
            cv.polygon([(cx + 92, 92), (cx + 108, 62), (cx + 124, 92)], MAGENTA_L, a=al)
    cv.text(90, 232, p.get("metric", "DRE"), font(BENTON, 36), MUTED)
    g = ease_in_out((t - at(a, "flat", 1.3)) / 0.9)
    cv.line([(210 if len(p.get("metric", "DRE")) <= 4 else 250, 222), ((210 if len(p.get("metric", "DRE")) <= 4 else 250) + 600 * g, 222)], MAGENTA_L, width=6)
    if g > 0.9:
        cv.text(960, 238, p.get("flat_label", "parado"), font(PLAYFAIR_I, 56), MAGENTA_L, anchor="rs")


def beat_lupa(cv, t, dur, a, p):
    """'olhando somente pro ROAS' -> ROAS under a magnifier, then dimmed"""
    cv.card(*CARD)
    word = p.get("word", "ROAS")
    dim = ease_in_out((t - at(a, "dim", 2.2)) / 0.5)
    col = tuple(int(c * (1 - 0.55 * dim) + 60 * 0.55 * dim) for c in MAGENTA_L)
    cv.text(540, 205, word, font(PLAYFAIR_I, 150), col, anchor="ms")
    pulse = 1 + 0.04 * math.sin(t * 6)
    cv.ellipse(790, 110, 46 * pulse, 46 * pulse, outline=OFFWHITE, width=7)
    cv.line([(823, 143), (856, 176)], OFFWHITE, width=9)
    cv.text(90, 80, p.get("sub", "somente"), font(BENTON, 38), MUTED)


def beat_cac(cv, t, dur, a, p):
    """CAC máximo permitido: a ceiling marker on a cost-per-sale bar"""
    cv.card(*CARD)
    cv.text(90, 92, p.get("title", "CAC máximo permitido"), font(PLAYFAIR_I, 76), OFFWHITE)
    cv.text(90, 130, p.get("sub", "o teto que você pode pagar por uma venda"), font(BENTON, 30), MUTED)
    x0, x1, y = 90, 990, 218
    cv.rect(x0, y - 18, x1, y + 18, (60, 40, 92), r=18)
    fill = ease_out_cubic((t - 0.3) / 1.0) * 0.64
    cv.rect(x0, y - 18, x0 + (x1 - x0) * fill, y + 18, MAGENTA_L, r=18)
    mk = ease_out_back((t - at(a, "marker", 1.4)) / 0.45)
    if mk > 0:
        mx = x0 + (x1 - x0) * 0.64
        al = int(255 * clamp01(mk))
        cv.line([(mx, y - 30), (mx, y + 30)], OFFWHITE, width=7, a=al)
        cv.text(mx, y - 40, p.get("ceiling", "teto"), font(BENTON, 34), OFFWHITE, a=al, anchor="ms")
    n0 = at(a, "profit", 3.2)
    if t > n0:
        cv.text(x0, 268, p.get("profit_text", "ainda ganha dinheiro"), font(BENTON, 32), MAGENTA_L, a=int(255 * clamp01((t - n0) / 0.3)))


def beat_call(cv, t, dur, a, p):
    """45-minute call: timer ring fills"""
    cv.card(*CARD)
    cx, cy, r = 190, 145, 82
    cv.ellipse(cx, cy, r, r, outline=(70, 46, 104), width=14)
    prog = ease_in_out(t / max(0.5, dur - 0.5))
    cv.arc(cx, cy, r, -90, -90 + 360 * prog, MAGENTA_L, width=14)
    cv.text(cx, cy + 22, p.get("big", "45"), font(BENTON, 80), OFFWHITE, anchor="ms")
    cv.text(cx, cy + 56, p.get("unit", "min"), font(BENTON, 28), MUTED, anchor="ms")
    cv.text(340, 128, p.get("kicker", "call de 45 minutos"), font(PLAYFAIR_I, 70), OFFWHITE)
    cv.text(340, 186, p.get("foot", "traga seus números"), font(BENTON, 40), MUTED)


def beat_checklist(cv, t, dur, a, p):
    """what the call delivers, ticked as he says it"""
    rows = p.get("rows", [])
    cv.card(*CARD)
    for i, row in enumerate(rows):
        t0 = at(a, f"r{i}", 0.2 + i * 1.2)
        k = ease_out_back((t - t0) / 0.38)
        if k <= 0:
            continue
        y = 22 + 82 * i
        off = (1 - clamp01(k)) * 40
        al = int(255 * clamp01(k))
        cv.ellipse(100, y + 44, 26, 26, fill=MAGENTA, a=al)
        g = ease_in_out((t - t0 - 0.2) / 0.3)
        if g > 0 and p.get("mark") == "x":          # "doesn't know ..." style lists
            cv.line([(89, y + 33), (111, y + 55)], OFFWHITE, width=6)
            cv.line([(111, y + 33), (89, y + 55)], OFFWHITE, width=6)
        elif g > 0:
            pts = [(88, y + 44), (97, y + 54), (114, y + 32)]
            if g < 0.5:
                q = g / 0.5
                pts = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q)]
            else:
                q = (g - 0.5) / 0.5
                pts = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)]
            cv.line(pts, OFFWHITE, width=6)
        cv.text(152 + off, y + 58, row[0], font(BENTON, 44), OFFWHITE, a=al)
        if len(row) > 1:
            w = cv.tw(row[0], font(BENTON, 44))
            cv.text(152 + off + w + 18, y + 58, row[1], font(PLAYFAIR_I, 40), MAGENTA_L, a=al)


BEATS = {"strike": beat_strike, "bars": beat_bars, "bank": beat_bank, "credits": beat_credits,
         "sum": beat_sum, "channels": beat_channels, "lupa": beat_lupa, "cac": beat_cac,
         "call": beat_call, "checklist": beat_checklist}


def render_frame(beats, T, h=None, registry=None):
    """beats: [{type,start,end,anchors,params}] already in OUTPUT time. Returns RGBA strip or None."""
    active = [b for b in beats if b["start"] <= T < b["end"]]
    if not active:
        return None
    cv = Cv(h)
    reg = registry if registry is not None else BEATS
    for b in active:
        t, dur = T - b["start"], b["end"] - b["start"]
        # registry beats that draw their own entrance (top band) get alpha 1 / dy 0
        if registry is not None:
            cv.alpha, cv.dy = 1.0, 0.0
        else:
            cv.alpha, cv.dy = fade_state(t, dur)
        a = {k: v - b["start"] for k, v in b.get("anchors", {}).items()}
        reg[b["type"]](cv, t, dur, a, b.get("params", {}))
    return cv.done()


def build_track(beats, total_dur, out_path, fps=30, ffmpeg="ffmpeg", h=None, registry=None):
    """Render all beats into ONE rgba qtrle .mov of size 1080 x ZONE_H (overlay at y=ZONE_Y0)."""
    n = int(round(total_dur * fps))
    proc = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{h or ZONE_H}", "-r", str(fps), "-i", "-",
         "-c:v", "qtrle", "-pix_fmt", "argb", str(out_path)],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    blank = bytes(W * (h or ZONE_H) * 4)
    for f in range(n):
        fr = render_frame(beats, f / fps, h, registry)
        proc.stdin.write(blank if fr is None else np.asarray(fr, dtype=np.uint8).tobytes())
    proc.stdin.close()
    proc.wait()
