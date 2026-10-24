#!/usr/bin/env python3
"""
ad_graphics.py — ad / content-edit overlay pack (Rarity branding x the two reference edits).

Derived from the two references Caio put in "Video Edition Ads and Content Refs":
  REF 1 (direct-response ad, landscape talking head): name tag lower-third, big bold captions with the
        key words in the accent colour, single-colour LINE ICONS that pop beside the face exactly when
        the matching noun is said (phone, calendar, pin, briefcase, bar chart...), thin progress bar.
  REF 2 (daily "Field Notes" series, vertical): series/title card at the very start with a progress
        bar, dark translucent DATA PANELS (stat rows, framework lists) over a mostly uncut single shot,
        small inset thumbnail, word-level captions.

Rarity translation (house rules win over the refs' colours/fonts): deep-plum glass cards (#1a0f2e),
off-white text (#efeeea), BentonSans + Playfair-Display-italic accent words, brand magenta (#D50057,
lightened for contrast) as the only accent — never the refs' yellow/orange. Captions stay the
minimal house style (edit_reel), not ref 1's heavy caps.

Two bands (both drawn with motion_graphics.Cv, 2x supersampled):
  TOP   band  y 150..470   -> line-icon stickers (right/left), name tag, title card
  LOWER band  y 1120..1410 -> stat rows, level chips, ceiling demo, CTA, + the motion_graphics beats
Both sit clear of the face in zoomed-in shots (chin ≈ y 1110) and of the captions (baseline 1480).
"""
import math

import motion_graphics as mg
from motion_graphics import (BENTON, MAGENTA, MAGENTA_L, MUTED, OFFWHITE, PLAYFAIR_I, PLUM, W, clamp01,
                             ease_in_out, ease_out_back, ease_out_cubic, font)

TOP_Y0, TOP_H = 150, 330
BLACK = (0, 0, 0)


# ------------------------------------------------------------------ line icons
class Ico:
    """draws in a ±50 unit box, scaled by s (px per unit) and rotated by rot (deg) about (cx, cy)"""

    def __init__(self, cv, cx, cy, s, rot=0.0, color=OFFWHITE, accent=MAGENTA_L, alpha=1.0, shadow=False):
        self.cv, self.cx, self.cy, self.s = cv, cx, cy, s
        self.c, self.r = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        self.color, self.accent, self.shadow = color, accent, shadow
        self.a = int(255 * alpha)
        self.w = max(3.0, 6.2 * s)

    def P(self, x, y):
        return (self.cx + (x * self.c - y * self.r) * self.s, self.cy + (x * self.r + y * self.c) * self.s)

    def line(self, pts, col=None, w=None):
        cv = self.cv
        pp = [self.P(x, y) for x, y in pts]
        col = col or self.color
        if self.shadow:
            cv.line([(x + 2, y + 5) for x, y in pp], BLACK, width=(w or self.w), a=int(110 * self.a / 255))
        cv.line(pp, col, width=(w or self.w), a=self.a)

    def circle(self, x, y, r, col=None, fill=False, w=None):
        cv = self.cv
        px, py = self.P(x, y)
        col = col or self.color
        if self.shadow:
            cv.ellipse(px + 2, py + 5, r * self.s, r * self.s, outline=BLACK, a=int(110 * self.a / 255), width=(w or self.w))
        if fill:
            cv.ellipse(px, py, r * self.s, r * self.s, fill=col, a=self.a)
        else:
            cv.ellipse(px, py, r * self.s, r * self.s, outline=col, a=self.a, width=(w or self.w))

    def poly(self, pts, col=None):
        self.cv.polygon([self.P(x, y) for x, y in pts], col or self.color, a=self.a)

    def rrect(self, x0, y0, x1, y1, r=8, col=None, w=None):
        pts, n = [], 6
        for (cx, cy, a0) in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
            for k in range(n + 1):
                ang = math.radians(a0 + 90 * k / n)
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        pts.append(pts[0])
        self.line(pts, col, w)

    def text(self, x, y, s, size, col=None):
        px, py = self.P(x, y)
        self.cv.text(px, py, s, font(BENTON, int(size * self.s)), col or self.color, a=self.a, anchor="mm")


def ic_phone(i):
    i.rrect(-22, -42, 22, 42, 9)
    i.line([(-6, 32), (6, 32)])
    i.circle(0, -30, 2.2, i.accent, fill=True)


def ic_calendar(i):
    i.rrect(-40, -32, 40, 40, 9)
    i.line([(-40, -10), (40, -10)])
    i.line([(-20, -42), (-20, -24)])
    i.line([(20, -42), (20, -24)])
    i.circle(-18, 10, 3.6, i.accent, fill=True)
    i.circle(0, 10, 3.6, fill=True)
    i.circle(18, 10, 3.6, fill=True)
    i.circle(-18, 26, 3.6, fill=True)


def ic_chart(i):
    i.line([(-40, 38), (40, 38)])
    for k, (x, h) in enumerate(((-28, 22), (-6, 40), (16, 62))):
        i.rrect(x - 8, 38 - h, x + 8, 38, 3, i.accent if k == 2 else None)
    i.line([(-40, -6), (-10, -22), (6, -10), (36, -40)], i.accent)
    i.line([(22, -40), (36, -40), (36, -26)], i.accent)


def ic_dollar(i):
    i.circle(0, 0, 40)
    i.text(0, 2, "$", 62, i.accent)


def ic_target(i):
    i.circle(0, 0, 40)
    i.circle(0, 0, 22)
    i.circle(0, 0, 6, i.accent, fill=True)
    i.line([(8, -8), (40, -40)], i.accent)
    i.line([(26, -40), (40, -40), (40, -26)], i.accent)


def ic_play(i):
    i.circle(0, 0, 40)
    i.poly([(-10, -18), (-10, 18), (22, 0)], i.accent)


def ic_megaphone(i):
    i.line([(-36, -12), (-12, -12), (30, -34), (30, 34), (-12, 12), (-36, 12), (-36, -12)])
    i.line([(-22, 12), (-14, 40), (-2, 40), (-4, 12)])
    i.line([(40, -14), (48, -20)], i.accent)
    i.line([(42, 0), (52, 0)], i.accent)
    i.line([(40, 14), (48, 20)], i.accent)


def ic_clock(i):
    i.circle(0, 0, 40)
    i.line([(0, -22), (0, 0), (16, 10)], i.accent)


def ic_pin(i):
    i.line([(0, 44), (-26, 6), (-30, -10), (-20, -32), (0, -42), (20, -32), (30, -10), (26, 6), (0, 44)])
    i.circle(0, -10, 10, i.accent)


def ic_mail(i):
    i.rrect(-42, -28, 42, 28, 7)
    i.line([(-42, -24), (0, 6), (42, -24)], i.accent)


def ic_cart(i):
    i.line([(-46, -34), (-30, -34), (-18, 14), (30, 14), (38, -18), (-24, -18)])
    i.circle(-12, 32, 6, i.accent, fill=True)
    i.circle(24, 32, 6, i.accent, fill=True)


def ic_search(i):
    i.circle(-8, -8, 28)
    i.line([(12, 12), (40, 40)], i.accent, w=i.w * 1.5)


def ic_bulb(i):
    i.circle(0, -12, 28)
    i.line([(-12, 22), (12, 22)])
    i.line([(-9, 34), (9, 34)])
    i.line([(0, -16), (0, 8)], i.accent)


def ic_arrow_up(i):
    i.line([(-36, 24), (-6, -6), (10, 10), (38, -22)], i.accent, w=i.w * 1.2)
    i.line([(20, -24), (38, -22), (36, -4)], i.accent, w=i.w * 1.2)
    i.line([(-40, 40), (40, 40)])


def ic_check(i):
    i.circle(0, 0, 40, i.accent, fill=True)
    i.line([(-18, 2), (-4, 16), (20, -14)], OFFWHITE, w=i.w * 1.3)


def ic_cross(i):
    i.circle(0, 0, 40, i.accent, fill=True)
    i.line([(-16, -16), (16, 16)], OFFWHITE, w=i.w * 1.3)
    i.line([(16, -16), (-16, 16)], OFFWHITE, w=i.w * 1.3)


def ic_users(i):
    i.circle(-14, -16, 13)
    i.line([(-40, 34), (-38, 14), (-26, 6), (-2, 6), (10, 14), (12, 34)])
    i.circle(22, -20, 11, i.accent)
    i.line([(26, 4), (38, 10), (42, 32)], i.accent)


def ic_camera(i):
    i.rrect(-42, -22, 18, 28, 8)
    i.line([(18, -6), (42, -20), (42, 26), (18, 12)], i.accent)


def ic_funnel(i):
    i.line([(-42, -34), (42, -34), (10, 4), (10, 38), (-10, 28), (-10, 4), (-42, -34)])
    i.circle(0, -34, 3, i.accent, fill=True)


def ic_gear(i):
    i.circle(0, 0, 18)
    for k in range(8):
        a = math.radians(k * 45)
        i.line([(26 * math.cos(a), 26 * math.sin(a)), (38 * math.cos(a), 38 * math.sin(a))], w=i.w * 1.5)
    i.circle(0, 0, 4, i.accent, fill=True)


def ic_shield(i):
    i.line([(0, -42), (36, -28), (34, 8), (0, 42), (-34, 8), (-36, -28), (0, -42)])
    i.line([(-14, 0), (-3, 12), (16, -12)], i.accent)


def ic_trophy(i):
    i.line([(-24, -36), (24, -36), (22, -4), (0, 12), (-22, -4), (-24, -36)])
    i.line([(0, 12), (0, 30)])
    i.line([(-16, 40), (16, 40)])
    i.line([(-24, -28), (-38, -28), (-34, -10), (-22, -8)], i.accent)
    i.line([(24, -28), (38, -28), (34, -10), (22, -8)], i.accent)


def ic_percent(i):
    i.circle(-20, -20, 11)
    i.circle(20, 20, 11)
    i.line([(30, -34), (-30, 34)], i.accent)


def ic_layers(i):
    i.line([(0, -38), (42, -16), (0, 6), (-42, -16), (0, -38)])
    i.line([(-42, 4), (0, 26), (42, 4)], i.accent)
    i.line([(-42, 20), (0, 42), (42, 20)])


ICONS = {"phone": ic_phone, "calendar": ic_calendar, "chart": ic_chart, "dollar": ic_dollar, "target": ic_target,
         "play": ic_play, "megaphone": ic_megaphone, "clock": ic_clock, "pin": ic_pin, "mail": ic_mail,
         "cart": ic_cart, "search": ic_search, "bulb": ic_bulb, "arrow_up": ic_arrow_up, "check": ic_check,
         "cross": ic_cross, "users": ic_users, "camera": ic_camera, "funnel": ic_funnel, "gear": ic_gear,
         "shield": ic_shield, "trophy": ic_trophy, "percent": ic_percent, "layers": ic_layers}


# ------------------------------------------------------------------ top-band beats
def beat_icon(cv, t, dur, a, p):
    """line-icon sticker beside the face, popping when the noun is spoken (ref 1)"""
    name = p.get("icon", "chart")
    side = p.get("side", "right")
    cx = 936 if side == "right" else 144   # outer corners: clear of hair/glasses in close-ups
    cy = 138
    k = ease_out_back(t / 0.40, 1.9)
    out = clamp01((dur - t) / 0.20)
    if k <= 0:
        return
    s = 1.55 * (0.35 + 0.65 * clamp01(k)) * (0.85 + 0.15 * out)
    rot = (1 - clamp01(k)) * (-14 if side == "right" else 14)
    fl = math.sin(t * 3.0) * 3.0                      # tiny idle float
    # soft plum disc behind for legibility on any background
    cv.ellipse(cx, cy + fl, 78 * s / 1.95, 78 * s / 1.95, fill=PLUM, a=int(150 * clamp01(k) * out))
    ic = Ico(cv, cx, cy + fl, s, rot, shadow=False, alpha=1.0)
    ICONS[name](ic)
    lab = p.get("label")
    if lab:
        cv.text(cx, cy + 104, lab, font(BENTON, 30), OFFWHITE, a=int(255 * clamp01((t - 0.2) / 0.3) * out), anchor="ms")


def beat_nametag(cv, t, dur, a, p):
    """name + role lower-third (ref 1), top-left, slides in with a magenta bar"""
    k = ease_out_cubic(t / 0.45)
    out = clamp01((dur - t) / 0.25)
    x0 = 40 - (1 - k) * 340
    name, role = p.get("name", "Caio de Camargo"), p.get("role", "Founder, Rarity")
    f1, f2 = font(BENTON, 44), font(BENTON, 28)
    w = max(cv.tw(name, f1), cv.tw(role, f2)) + 64
    cv.rect(x0, 40, x0 + w, 40 + 112, PLUM, a=int(225 * out), r=18)
    cv.rect(x0, 40, x0 + 9, 40 + 112, MAGENTA, a=int(255 * out), r=4)
    cv.text(x0 + 34, 92, name, f1, OFFWHITE, a=int(255 * out))
    cv.text(x0 + 34, 130, role, f2, MAGENTA_L, a=int(255 * out))


def beat_title(cv, t, dur, a, p):
    """series / topic title card at the very start (ref 2 'Day 21/365')"""
    k = ease_out_back(t / 0.45)
    out = clamp01((dur - t) / 0.25)
    al = int(255 * out * clamp01(k * 1.5))
    off = (1 - clamp01(k)) * -30
    cv.text(540, 70 + off, p.get("kicker", "RARITY"), font(BENTON, 34), MAGENTA_L, a=al, anchor="ms")
    cv.text(540, 170 + off, p.get("title", ""), font(PLAYFAIR_I, int(p.get("size", 104))), (255, 255, 255), a=al, anchor="ms")
    if p.get("sub"):
        cv.text(540, 232 + off, p["sub"], font(BENTON, 36), OFFWHITE, a=al, anchor="ms")
    g = ease_in_out((t - 0.3) / 0.7)
    cv.line([(340, 270), (340 + 400 * g, 270)], MAGENTA_L, width=6, a=int(255 * out))


TOP_BEATS = {"icon": beat_icon, "nametag": beat_nametag, "title": beat_title}


# ------------------------------------------------------------------ lower-strip beats
CARD = mg.CARD


def beat_stat(cv, t, dur, a, p):
    """1-4 big numbers with a label each (ref 2 stat panel)"""
    cv.card(*CARD)
    stats = p.get("stats", [])
    n = max(1, len(stats))
    cw = 920 / n
    for i, st in enumerate(stats):
        k = ease_out_back((t - at(a, f"s{i}", 0.2 + 0.35 * i)) / 0.4)
        if k <= 0:
            continue
        al = int(255 * clamp01(k))
        cx = 80 + cw * (i + 0.5)
        size = 108 if n <= 2 else (92 if n == 3 else 78)
        big, lab = st[0], st[1]
        hot = len(st) > 2 and st[2]
        cv.text(cx, 168 + (1 - clamp01(k)) * 20, big, font(BENTON, size), MAGENTA_L if hot else (255, 255, 255), a=al, anchor="ms")
        cv.text(cx, 222, lab, font(BENTON, 30 if n > 3 else 34), MUTED, a=al, anchor="ms")
        if i < n - 1:
            cv.line([(80 + cw * (i + 1), 80), (80 + cw * (i + 1), 240)], (80, 60, 120), width=3, a=int(200 * clamp01(k)))


def at(a, name, default=0.0):
    return a.get(name, default)


def beat_level(cv, t, dur, a, p):
    """'Level 1 — Performance media' chapter chip"""
    cv.card(*CARD)
    k = ease_out_back(t / 0.4)
    num = p.get("num", "1")
    cv.ellipse(150, 145, 78, 78, fill=MAGENTA, a=int(255 * clamp01(k)))
    cv.text(150, 135, "LEVEL", font(BENTON, 26), OFFWHITE, anchor="ms", a=int(255 * clamp01(k)))
    cv.text(150, 192, num, font(BENTON, 78), (255, 255, 255), anchor="ms", a=int(255 * clamp01(k)))
    f = font(PLAYFAIR_I, 76)
    cv.text(270, 142, p.get("title", ""), f, OFFWHITE, a=int(255 * ease_out_cubic((t - 0.1) / 0.4)))
    cv.text(270, 206, p.get("sub", ""), font(BENTON, 38), MUTED, a=int(255 * ease_out_cubic((t - 0.3) / 0.4)))


def beat_ceiling(cv, t, dur, a, p):
    """max allowable CAC demo: ceiling marker + 'you pay $X' dot that lands under/over it"""
    cv.card(*CARD)
    cv.text(90, 82, p.get("title", "Max allowable CAC"), font(PLAYFAIR_I, 56), OFFWHITE)
    x0, x1, y = 90, 990, 190
    lo, hi = p.get("lo", 0), p.get("hi", 80)
    def X(v):
        return x0 + (x1 - x0) * (v - lo) / (hi - lo)
    cv.rect(x0, y - 14, x1, y + 14, (60, 40, 92), r=14)
    ceil = p.get("ceiling", 55)
    kc = ease_out_cubic((t - 0.1) / 0.5)
    cv.rect(x0, y - 14, x0 + (X(ceil) - x0) * kc, y + 14, (110, 70, 170), r=14)
    cv.line([(X(ceil), y - 36), (X(ceil), y + 36)], OFFWHITE, width=6, a=int(255 * kc))
    cv.text(X(ceil), y - 46, f"${ceil} ceiling", font(BENTON, 30), OFFWHITE, a=int(255 * kc), anchor="ms")
    for j, (val, key, good) in enumerate(p.get("points", [])):
        k = ease_out_back((t - at(a, key, 1.0 + 1.5 * j)) / 0.4)
        if k <= 0:
            continue
        al = int(255 * clamp01(k))
        col = MAGENTA_L if not good else (255, 255, 255)
        cv.ellipse(X(val), y, 17 * clamp01(k), 17 * clamp01(k), fill=col, a=al)
        cv.text(X(val), y + 66, f"${val}", font(BENTON, 40), col, a=al, anchor="ms")
        cv.text(X(val), y + 98 if False else y + 100, p.get("labels", ["room to scale", "problem"])[0 if good else 1],
                font(PLAYFAIR_I, 32), col, a=al, anchor="ms")


def beat_cta(cv, t, dur, a, p):
    """closing call to action card with a pulsing arrow"""
    cv.card(*CARD)
    k = ease_out_back(t / 0.45)
    al = int(255 * clamp01(k))
    cv.text(90, 120, p.get("line1", "Free growth audit"), font(PLAYFAIR_I, 82), (255, 255, 255), a=al)
    cv.text(90, 186, p.get("line2", "Click the link"), font(BENTON, 46), MAGENTA_L, a=al)
    cv.text(90, 240, p.get("line3", ""), font(BENTON, 30), MUTED, a=al)
    pulse = 1 + 0.08 * math.sin(t * 7)
    cx, cy = 900, 150
    cv.ellipse(cx, cy, 70 * pulse, 70 * pulse, fill=MAGENTA, a=al)
    cv.polygon([(cx - 22, cy - 18), (cx + 6, cy - 18), (cx + 6, cy - 34), (cx + 34, cy), (cx + 6, cy + 34), (cx + 6, cy + 18), (cx - 22, cy + 18)], OFFWHITE, a=al)


def beat_vs(cv, t, dur, a, p):
    """'% of your spend' (struck) vs 'flat fee' — the pricing contrast"""
    cv.card(*CARD)
    l, r = p.get("left", "% of ad spend"), p.get("right", "flat fee")
    k1 = ease_out_cubic(t / 0.4)
    cv.text(300, 130, l, font(BENTON, 52), OFFWHITE, a=int(255 * k1), anchor="ms")
    g = ease_in_out((t - at(a, "strike", 0.9)) / 0.4)
    if g > 0:
        w = cv.tw(l, font(BENTON, 52))
        cv.line([(300 - w / 2 - 10, 112), (300 - w / 2 - 10 + (w + 20) * g, 112)], MAGENTA_L, width=8)
    cv.text(300, 190, p.get("lsub", "paid more when you spend more"), font(BENTON, 28), MUTED, a=int(255 * k1), anchor="ms")
    k2 = ease_out_back((t - at(a, "right", 1.3)) / 0.4)
    if k2 > 0:
        al = int(255 * clamp01(k2))
        cv.rect(560, 50, 1000, 240, MAGENTA, r=34, a=al)
        cv.text(780, 150, r, font(PLAYFAIR_I, 76), (255, 255, 255), a=al, anchor="ms")
        cv.text(780, 206, p.get("rsub", "never a % of your spend"), font(BENTON, 28), OFFWHITE, a=al, anchor="ms")


def beat_title_lower(cv, t, dur, a, p):
    """series / topic title card at the start — LOWER band (the top would sit on the face in wide shots)"""
    cv.card(*CARD)
    k = ease_out_cubic(t / 0.45)
    cv.text(90, 82, p.get("kicker", "RARITY"), font(BENTON, 32), MAGENTA_L, a=int(255 * k))
    cv.text(90, 176, p.get("title", ""), font(PLAYFAIR_I, int(p.get("size", 84))), (255, 255, 255), a=int(255 * k))
    if p.get("sub"):
        cv.text(90, 236, p["sub"], font(BENTON, 34), MUTED, a=int(255 * k))
    g = ease_in_out((t - 0.3) / 0.8)
    cv.line([(90, 204), (90 + 820 * g, 204)], MAGENTA_L, width=5)


LOWER_BEATS = {"title": beat_title_lower, "stat": beat_stat, "level": beat_level, "ceiling": beat_ceiling, "cta": beat_cta, "vs": beat_vs}


def register():
    """make the lower-band beats available to motion_graphics.render_frame"""
    mg.BEATS.update(LOWER_BEATS)


register()


# ------------------------------------------------------------------ progress bar track
def build_progress_track(total_dur, out_path, fps=30, ffmpeg="ffmpeg", x0=40, x1=1040, bar_h=6):
    """Thin brand progress bar as its own RGBA track (1080 x 12): off-white track + magenta fill that
    grows linearly over total_dur. (ffmpeg's drawbox does NOT re-evaluate `w=...t...` per frame — the
    fill silently stayed at 0 width, leaving only a stray grey line. Render it as frames instead.)"""
    import subprocess
    import numpy as np
    H = 12
    y0 = (H - bar_h) // 2
    n = int(round(total_dur * fps))
    proc = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
         "-c:v", "qtrle", "-pix_fmt", "argb", str(out_path)], stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    base = np.zeros((H, W, 4), dtype=np.uint8)
    base[y0:y0 + bar_h, x0:x1] = (239, 238, 234, 56)      # track: off-white @ 22 %
    for f in range(n):
        fr = base.copy()
        fx = x0 + int((x1 - x0) * min(1.0, f / max(1, n - 1)))
        if fx > x0:
            fr[y0:y0 + bar_h, x0:fx] = (213, 0, 87, 242)   # fill: brand magenta
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    proc.wait()
