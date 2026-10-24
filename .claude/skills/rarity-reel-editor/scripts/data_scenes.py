#!/usr/bin/env python3
"""
data_scenes.py — full-frame DESIGNED scenes for voiceover Reels (replaces generic stock where a
number, a date or a comparison is what the sentence is actually about).

Why: generic stock B-roll ("a man typing", "a hand on a phone") was called out as "free stuff, not
specific, not engaging". A viewer scrolling at 1.5-3 s per beat is held by *information that moves*
— a date being circled, a number counting up, bars growing, a schedule filling in — plus a few
hand-picked, genuinely specific real clips (an Amazon courier, a hand hanging a BLACK FRIDAY SALE
placard) used as plates under callouts.

A scene = optional background plate (real clip: push-in, colour-matched, dimmed/blurred) + an
animated overlay drawn per frame (motion_graphics.Cv, 2x supersampled) + a designed background when
there is no plate. Everything uses the Rarity palette: deep plum, off-white, ONE magenta accent.

Kinds (see sc_* functions):
  calendar_hook, calendar_late, timeline, counter, bigstat, bars2, ladder, feed, auction, chip
Add a kind by writing sc_<kind>(cv, t, dur, a, p) and registering it in KINDS.
  t = seconds into the scene clip, a = {anchor: seconds}, p = params dict.
"""
import calendar as pycal
import math
import random
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import motion_graphics as mg
from motion_graphics import (BENTON, MAGENTA, MAGENTA_L, MUTED, OFFWHITE, PLAYFAIR_I, PLUM, W, Cv, clamp01,
                             ease_in_out, ease_out_back, ease_out_cubic, font)

OUT_H = 1920
BAND_Y0, BAND_H = 170, 1130          # overlay band: y 170..1300 (captions sit below at ~1330)
FPS = 30


def at(a, k, d=0.0):
    return a.get(k, d)


# ------------------------------------------------------------------ background
_RNG = np.random.default_rng(11)
_YY, _XX = np.mgrid[0:OUT_H // 4, 0:W // 4].astype(np.float32)


def designed_bg(t):
    """plum gradient + two slowly drifting glows (magenta top-right, violet bottom-left)"""
    top = np.array([24, 14, 40], dtype=np.float32)
    bot = np.array([13, 8, 22], dtype=np.float32)
    g = np.linspace(0, 1, OUT_H // 4, dtype=np.float32)[:, None, None]
    small = top * (1 - g) + bot * g
    small = np.broadcast_to(small, (OUT_H // 4, W // 4, 3)).copy()
    for (cx, cy, sig, col, amp) in (
        (0.80 + 0.04 * math.sin(t * 0.6), 0.26 + 0.02 * math.cos(t * 0.5), 0.36, np.array([213, 0, 87], np.float32), 0.34),
        (0.18 + 0.03 * math.cos(t * 0.5), 0.80 + 0.02 * math.sin(t * 0.4), 0.46, np.array([74, 40, 150], np.float32), 0.30),
    ):
        d2 = ((_XX / (W / 4) - cx) ** 2) * (W / OUT_H) ** 2 * (OUT_H / W) ** 2 + ((_YY / (OUT_H / 4) - cy) ** 2)
        gl = np.exp(-d2 / (sig ** 2 * 0.5))[..., None] * amp
        small = small * (1 - gl) + col * gl
    img = Image.fromarray(np.clip(small, 0, 255).astype(np.uint8)).resize((W, OUT_H), Image.BICUBIC)
    # dark gradients band badly in 8-bit + x264 (visible contour rings) -> dither with fine noise
    arr = np.asarray(img, dtype=np.float32) + _RNG.normal(0.0, 2.2, (OUT_H, W, 1)).astype(np.float32)
    return np.clip(arr, 0, 255).astype(np.uint8)


# ------------------------------------------------------------------ small drawing helpers
def tw_center(cv, x, y, s, f, fill=OFFWHITE, a=255):
    cv.text(x, y, s, f, fill, a=a, anchor="ms")


def pop(t, t0, tin=0.4):
    return ease_out_back((t - t0) / tin)


def pill(cv, cx, cy, label, f_size=40, fill=PLUM, text=OFFWHITE, outline=OFFWHITE, k=1.0, pad=36, h=76):
    if k <= 0:
        return
    f = font(BENTON, f_size)
    w = cv.tw(label, f) + pad * 2
    s_ = 0.8 + 0.2 * clamp01(k)
    al = int(255 * clamp01(k))
    cv.rect(cx - w * s_ / 2, cy - h * s_ / 2, cx + w * s_ / 2, cy + h * s_ / 2, fill, r=h * s_ / 2, a=al, outline=outline)
    cv.text(cx, cy + f_size * 0.34 * s_, label, font(BENTON, int(f_size * s_)), text, a=al, anchor="ms")


def source_chip(cv, y, label, k):
    pill(cv, 540, y, label, f_size=28, fill=(30, 18, 52), text=MUTED, outline=MUTED, k=k, pad=26, h=54)


# ------------------------------------------------------------------ calendar
def draw_calendar(cv, year, month, x0, y0, w, t, a, hi=None, hi_t=None, mark=None, k_card=1.0, cell_h=86):
    """month grid. hi=(day) circled with a draw-on ring starting at hi_t; mark={day: label}."""
    if k_card <= 0:
        return
    al = clamp01(k_card)
    weeks = pycal.Calendar(firstweekday=6).monthdayscalendar(year, month)   # Sunday first
    h = 150 + cell_h * len(weeks)
    off = (1 - al) * 40
    cv.card(x0, y0 + off, x0 + w, y0 + off + h, r=34)
    cv.text(x0 + 44, y0 + off + 78, pycal.month_name[month].upper() + f" {year}", font(BENTON, 40), MUTED, a=int(255 * al))
    cw = (w - 60) / 7
    for i, d in enumerate("SMTWTFS"):
        cv.text(x0 + 30 + cw * (i + 0.5), y0 + off + 134, d, font(BENTON, 28), MUTED, a=int(200 * al), anchor="ms")
    for r, wk in enumerate(weeks):
        for c, day in enumerate(wk):
            if not day:
                continue
            cx, cy = x0 + 30 + cw * (c + 0.5), y0 + off + 150 + cell_h * (r + 0.5)
            is_hi = hi == day
            col = OFFWHITE if not is_hi else (255, 255, 255)
            cv.text(cx, cy + 14, str(day), font(BENTON, 38), col, a=int((255 if is_hi else 190) * al), anchor="ms")
            if mark and day in mark:
                cv.text(cx, cy + 40, mark[day], font(BENTON, 20), MAGENTA_L, a=int(255 * al), anchor="ms")
    if hi and hi_t is not None:
        for r, wk in enumerate(weeks):
            if hi in wk:
                c = wk.index(hi)
                cx, cy = x0 + 30 + cw * (c + 0.5), y0 + off + 150 + cell_h * (r + 0.5)
                g = ease_in_out((t - hi_t) / 0.5)
                if g > 0:
                    cv.arc(cx, cy, 40, -90, -90 + 360 * g, MAGENTA_L, width=7)
                    pulse = 1 + 0.06 * math.sin((t - hi_t) * 7)
                    cv.ellipse(cx, cy, 36 * pulse, 36 * pulse, fill=MAGENTA, a=int(110 * clamp01(g)))
                    cv.text(cx, cy + 14, str(hi), font(BENTON, 40), (255, 255, 255), anchor="ms")
    return y0 + off + h


def sc_calendar_hook(cv, t, dur, a, p):
    """hook: BLACK FRIDAY slams in, October calendar, Tuesday 6 circled, NOVEMBER struck"""
    k1 = ease_out_back((t - at(a, "h1", 0.0)) / 0.38, 1.9)
    if k1 > 0:
        s_ = 1.35 - 0.35 * clamp01(k1)
        f = font(PLAYFAIR_I, int(112 * s_))
        cv.text(540, 150 + (1 - clamp01(k1)) * -10, "BLACK FRIDAY", f, MAGENTA_L, a=int(255 * clamp01(k1 * 1.4)), anchor="ms")
    k2 = ease_out_cubic((t - at(a, "h2", 0.45)) / 0.4)
    if k2 > 0:
        cv.text(540, 236, "starts this", font(BENTON, 66), OFFWHITE, a=int(255 * k2), anchor="ms")
    kt = pop(t, at(a, "tue", 1.05), 0.34)
    if kt > 0:
        s_ = 0.8 + 0.2 * clamp01(kt)
        cv.text(540, 236 + 96 * s_, "TUESDAY", font(PLAYFAIR_I, int(88 * s_)), (255, 255, 255), a=int(255 * clamp01(kt)), anchor="ms")
    kc = pop(t, at(a, "cal", 0.8), 0.45)
    draw_calendar(cv, 2026, 10, 90, 360, 900, t, a, hi=6, hi_t=at(a, "circle", 1.25), k_card=kc, cell_h=76)
    # NOT NOVEMBER (struck)
    kn = ease_out_cubic((t - at(a, "nov", 2.2)) / 0.35)
    if kn > 0:
        f = font(BENTON, 78)
        cv.text(540, 962, "NOT NOVEMBER", f, OFFWHITE, a=int(255 * kn), anchor="ms")
        g = ease_in_out((t - at(a, "strike", 2.5)) / 0.35)
        if g > 0:
            w = cv.tw("NOT NOVEMBER", f)
            cv.line([(540 - w / 2 - 14, 937), (540 - w / 2 - 14 + (w + 28) * g, 937)], MAGENTA_L, width=9)


def sc_calendar_late(cv, t, dur, a, p):
    """closing: November calendar, Black Friday Nov 27 marked, plan starts Nov 1 -> LATE stamp"""
    cv.text(540, 130, "your plan starts", font(BENTON, 60), OFFWHITE, a=int(255 * ease_out_cubic((t - at(a, "h", 0.0)) / 0.4)), anchor="ms")
    k = pop(t, at(a, "cal", 0.25), 0.45)
    draw_calendar(cv, 2026, 11, 90, 200, 900, t, a, hi=1, hi_t=at(a, "nov1", 0.9), mark={27: "BF"}, k_card=k)
    # stamp
    ks = ease_out_back((t - at(a, "late", 1.7)) / 0.3, 1.6)
    if ks > 0:
        layer = Image.new("RGBA", (W * mg.S, 520 * mg.S), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        f = font(PLAYFAIR_I, 230)
        txt = "LATE"
        tw = d.textlength(txt, font=f)
        cx, cy = layer.width / 2, layer.height / 2
        col = (*MAGENTA_L, int(255 * clamp01(ks * 1.3) * cv.alpha))
        d.rounded_rectangle((cx - tw / 2 - 70, cy - 190, cx + tw / 2 + 70, cy + 120), radius=34, outline=col, width=14)
        d.text((cx, cy + 70), txt, font=f, fill=col, anchor="ms")
        s_ = 1.5 - 0.5 * clamp01(ks)
        layer = layer.rotate(8, resample=Image.BICUBIC, expand=False)
        nw, nh = int(layer.width * s_), int(layer.height * s_)
        layer = layer.resize((nw, nh), Image.LANCZOS)
        cv.img.alpha_composite(layer, (int((W * mg.S - nw) / 2), int(930 * mg.S - nh / 2)))


# ------------------------------------------------------------------ timeline (schedule)
def sc_timeline(cv, t, dur, a, p):
    cv.text(540, 90, "WEEK OF OCT 5", font(BENTON, 46), MUTED, a=int(255 * ease_out_cubic(t / 0.4)), anchor="ms")
    x0, cw = 250, 110
    days = [("M", 5), ("T", 6), ("W", 7), ("T", 8), ("F", 9), ("S", 10), ("S", 11)]
    # overlap column highlight (Oct 6-7)
    ko = ease_in_out((t - at(a, "same", 2.3)) / 0.5)
    if ko > 0:
        cv.rect(x0 + cw * 1 - 6, 150, x0 + cw * 3 + 6, 800, MAGENTA, a=int(60 * ko), r=26, outline=MAGENTA_L)
    for i, (d, n) in enumerate(days):
        cx = x0 + cw * (i + 0.5)
        cv.text(cx, 190, d, font(BENTON, 30), MUTED, anchor="ms")
        cv.text(cx, 244, str(n), font(BENTON, 46), OFFWHITE, anchor="ms")
    rows = [("Walmart", 0, 6, (92, 52, 120), "walmart"), ("Amazon", 1, 2, MAGENTA_L, "amazon"), ("Target", 1, 2, (168, 60, 130), "target")]
    for r, (name, c0, c1, col, key) in enumerate(rows):
        y = 380 + r * 150
        t0 = at(a, key, 0.2 + r * 0.3)
        k = ease_out_cubic((t - t0) / 0.5)
        if k <= 0:
            continue
        cv.text(x0 - 26, y + 16, name, font(BENTON, 44), OFFWHITE, a=int(255 * clamp01(k * 1.5)), anchor="rs")
        bx0, bx1 = x0 + cw * c0 + 8, x0 + cw * (c1 + 1) - 8
        cv.rect(bx0, y - 34, bx0 + (bx1 - bx0) * k, y + 34, col, r=34)
    kk = pop(t, at(a, "same", 2.3), 0.4)
    if kk > 0:
        cv.text(540, 960, "same week", font(PLAYFAIR_I, 96), MAGENTA_L, a=int(255 * clamp01(kk)), anchor="ms")
    source_chip(cv, 1060, "retailer sale calendars · Oct 2026", ease_out_cubic((t - 1.0) / 0.5))


# ------------------------------------------------------------------ counter / bigstat
def sc_counter(cv, t, dur, a, p):
    val = p.get("value", 95.8)
    tc = at(a, "count", 0.4)
    cd = p.get("dur", 1.5)
    k = ease_out_cubic((t - tc) / cd)
    al = ease_out_cubic((t - 0.1) / 0.4)
    cv.text(540, 250, p.get("eyebrow", "ADOBE ANALYTICS · OCT 2026 FORECAST"), font(BENTON, 32), MUTED, a=int(255 * al), anchor="ms")
    s_ = 0.92 + 0.08 * clamp01(k)
    txt = f"${val * k:.1f}B"
    cv.text(540, 560, txt, font(BENTON, int(250 * s_)), (255, 255, 255), a=int(255 * clamp01(al * 2)), anchor="ms")
    kl = ease_out_cubic((t - tc - cd * 0.75) / 0.5)
    if kl > 0:
        cv.text(540, 690, p.get("label", "spent online in October"), font(PLAYFAIR_I, 76), MAGENTA_L, a=int(255 * kl), anchor="ms")
    # bar fill underline
    cv.rect(190, 740, 890, 756, (60, 40, 92), r=8)
    cv.rect(190, 740, 190 + 700 * k, 756, MAGENTA_L, r=8)


def sc_bigstat(cv, t, dur, a, p):
    big = p.get("big", "+8%")
    k = ease_out_back((t - at(a, "slam", 0.0)) / 0.4, 1.9)
    s_ = 1.45 - 0.45 * clamp01(k)
    cv.text(540, 560, big, font(PLAYFAIR_I, int(330 * s_)), MAGENTA_L, a=int(255 * clamp01(k * 1.6)), anchor="ms")
    # up arrow
    ka = ease_out_cubic((t - 0.25) / 0.4)
    if ka > 0:
        cv.polygon([(540, 150 - 20 * (1 - ka)), (610, 250), (470, 250)], OFFWHITE, a=int(255 * ka))
    kl = ease_out_cubic((t - 0.5) / 0.4)
    if kl > 0:
        cv.text(540, 700, p.get("sub", "vs. last October"), font(BENTON, 56), OFFWHITE, a=int(255 * kl), anchor="ms")
        cv.text(540, 770, p.get("src", "Adobe Analytics"), font(BENTON, 34), MUTED, a=int(255 * kl), anchor="ms")


# ------------------------------------------------------------------ two bars
def sc_bars2(cv, t, dur, a, p):
    cv.text(540, 100, "2026 US online sales · forecast", font(BENTON, 40), MUTED, a=int(255 * ease_out_cubic(t / 0.4)), anchor="ms")
    base, maxh = 860, 560
    data = [("Cyber Monday", 15.1, "+6.2%", 300, (92, 52, 120)), ("Black Friday", 12.9, "+9.2%", 780, MAGENTA_L)]
    for i, (name, v, g, cx, col) in enumerate(data):
        k = ease_out_cubic((t - 0.25 - i * 0.35) / 0.8)
        h = maxh * (v / 15.1) * k
        cv.rect(cx - 120, base - h, cx + 120, base, col, r=18)
        cv.text(cx, base + 62, name, font(BENTON, 44), OFFWHITE, anchor="ms")
        if k > 0.15:
            cv.text(cx, base - h - 26, f"${v * k:.1f}B", font(BENTON, 56), OFFWHITE, a=int(255 * clamp01(k * 2)), anchor="ms")
        kb = pop(t, at(a, "bf" if i else "cm", 1.2 + i * 0.9), 0.4)
        if kb > 0:
            pill(cv, cx, base - h - 110, g + " YoY", f_size=40, fill=MAGENTA if i else PLUM, outline=MAGENTA_L if i else MUTED,
                 k=kb, pad=30, h=70)
    kf = ease_out_cubic((t - at(a, "faster", 2.0)) / 0.5)
    if kf > 0:
        cv.text(540, 1040, "growing faster", font(PLAYFAIR_I, 84), MAGENTA_L, a=int(255 * kf), anchor="ms")
        cv.text(540, 1096, "source: Adobe Analytics", font(BENTON, 30), MUTED, a=int(255 * kf), anchor="ms")


# ------------------------------------------------------------------ ladder (overlay on a plate)
def sc_ladder(cv, t, dur, a, p):
    cv.text(540, 520, "Discounts build through the season", font(BENTON, 38), OFFWHITE, a=int(255 * ease_out_cubic(t / 0.4)), anchor="ms")
    rows = [("early Nov", "up to 14% off", 14, "r0"), ("pre-Thanksgiving", "up to 21%", 21, "r1"), ("Cyber Week", "up to 30%", 30, "r2")]
    for i, (lab, val, pct, key) in enumerate(rows):
        t0 = at(a, key, 0.3 + i * 0.5)
        k = ease_out_cubic((t - t0) / 0.5)
        if k <= 0:
            continue
        y = 580 + i * 128
        cv.card(80, y, 1000, y + 108, r=28)
        cv.rect(100, y + 74, 100 + 860 * (pct / 30) * k, y + 90, MAGENTA_L, r=8)
        cv.text(112, y + 54, lab, font(BENTON, 40), OFFWHITE, a=int(255 * clamp01(k * 2)))
        cv.text(968, y + 54, val, font(PLAYFAIR_I, 46), MAGENTA_L, a=int(255 * clamp01(k * 2)), anchor="rs")
    source_chip(cv, 988, "Adobe Analytics forecast", ease_out_cubic((t - 1.3) / 0.4))


def sc_feed(cv, t, dur, a, p):
    k = pop(t, at(a, "pill", 0.2), 0.45)
    pill(cv, 540, 170, "TESTING CREATIVE", f_size=50, fill=MAGENTA, outline=MAGENTA, k=k, pad=48, h=100)
    kr = ease_out_cubic((t - at(a, "now", 1.6)) / 0.4)
    if kr > 0:
        cv.text(540, 300, "right now", font(PLAYFAIR_I, 92), (255, 255, 255), a=int(255 * kr), anchor="ms")
    # A / B / C variant tiles at the bottom of the band
    for i, lab in enumerate("ABC"):
        kk = pop(t, 0.9 + i * 0.25, 0.4)
        if kk <= 0:
            continue
        cx = 340 + i * 200
        win = (t > at(a, "win", 2.8)) and i == 1
        s_ = 0.8 + 0.2 * clamp01(kk)
        cv.rect(cx - 70 * s_, 960 - 70 * s_, cx + 70 * s_, 960 + 70 * s_, MAGENTA if win else PLUM, r=24, a=int(255 * clamp01(kk)), outline=MAGENTA_L if win else OFFWHITE)
        cv.text(cx, 960 + 20 * s_, lab, font(PLAYFAIR_I, int(80 * s_)), OFFWHITE, a=int(255 * clamp01(kk)), anchor="ms")


# ------------------------------------------------------------------ auction curve
def sc_auction(cv, t, dur, a, p):
    cv.text(540, 100, "the ad auction", font(PLAYFAIR_I, 84), OFFWHITE, a=int(255 * ease_out_cubic(t / 0.4)), anchor="ms")
    x0, x1, yb, yt = 130, 950, 900, 260
    cv.line([(x0, yb), (x1, yb)], (110, 90, 150), width=4)
    cv.line([(x0, yb), (x0, yt)], (110, 90, 150), width=4)
    cv.text(x0, yb + 56, "OCT", font(BENTON, 36), MUTED)
    cv.text(x1, yb + 56, "NOV", font(BENTON, 36), MUTED, anchor="rs")
    cv.text(x0 + 16, yt + 6, "cost", font(BENTON, 30), MUTED)
    g = ease_in_out((t - 0.3) / 1.6)
    pts = []
    n = 48
    for i in range(int(n * g) + 1):
        u = i / n
        pts.append((x0 + (x1 - x0) * u, yb - (yb - yt - 40) * (0.04 + 0.96 * u ** 2.6)))
    if len(pts) > 1:
        cv.line(pts, MAGENTA_L, width=9)
    # flood of advertisers (dots) as he says "floods"
    tf = at(a, "flood", 1.6)
    rnd = random.Random(7)
    for i in range(46):
        ti = tf + i * 0.035
        k = ease_out_back((t - ti) / 0.3)
        if k <= 0:
            continue
        u = 0.45 + 0.55 * rnd.random()
        px = x0 + (x1 - x0) * u + rnd.uniform(-22, 22)
        py = yb - (yb - yt - 40) * (0.04 + 0.96 * u ** 2.6) + rnd.uniform(30, 150)
        r = 10 + 8 * rnd.random()
        cv.ellipse(px, min(py, yb - 14), r * clamp01(k), r * clamp01(k), fill=(232, 120, 180), a=int(200 * clamp01(k)))
    kn = pop(t, at(a, "nov", 2.4), 0.4)
    if kn > 0:
        pill(cv, 790, 200, "NOVEMBER", f_size=44, fill=MAGENTA, outline=MAGENTA, k=kn, pad=40, h=84)


def sc_chip(cv, t, dur, a, p):
    """callout pill(s) over a plate: params {pills:[{text, at, y, size, fill}]}"""
    for pl in p.get("pills", []):
        k = pop(t, at(a, pl.get("at", "p0"), pl.get("t", 0.3)), 0.45)
        fill = MAGENTA if pl.get("hot") else PLUM
        pill(cv, 540, pl.get("y", 200), pl["text"], f_size=pl.get("size", 48), fill=fill,
             outline=MAGENTA if pl.get("hot") else OFFWHITE, k=k, pad=44, h=pl.get("h", 96))
    for ln in p.get("lines", []):
        k = ease_out_cubic((t - at(a, ln.get("at", "l0"), ln.get("t", 0.8))) / 0.4)
        if k > 0:
            f = font(PLAYFAIR_I if ln.get("italic") else BENTON, ln.get("size", 70))
            cv.text(540, ln.get("y", 330), ln["text"], f, MAGENTA_L if ln.get("hot") else OFFWHITE, a=int(255 * k), anchor="ms")


KINDS = {"calendar_hook": sc_calendar_hook, "calendar_late": sc_calendar_late, "timeline": sc_timeline,
         "counter": sc_counter, "bigstat": sc_bigstat, "bars2": sc_bars2, "ladder": sc_ladder, "feed": sc_feed,
         "auction": sc_auction, "chip": sc_chip}


# ------------------------------------------------------------------ renderer
def render_scene(out_path, kind, params, anchors, dur, fps, ffmpeg, bg_cmd=None, band_y=None):
    """Render one scene to an mp4.

    bg_cmd: optional ffmpeg argv that writes the background PLATE as raw rgb24 1080x1920 frames to
            stdout (the caller builds it: seek, loop, push-in, colour-match, dim/blur). When None a
            designed animated background is used.
    """
    n = max(1, int(round(dur * fps)))
    enc = subprocess.Popen(
        [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{OUT_H}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(out_path)],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    dec = None
    if bg_cmd:
        dec = subprocess.Popen(bg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fsz = W * OUT_H * 3
    fn = KINDS[kind]
    last = None
    for f in range(n):
        t = f / fps
        if dec:
            raw = dec.stdout.read(fsz)
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(OUT_H, W, 3).copy() if len(raw) == fsz else last
        else:
            frame = designed_bg(t).copy()
        last = frame
        cv = Cv(BAND_H)
        # global enter/exit fade for overlay-only scenes is handled per element; keep alpha = 1
        cv.alpha, cv.dy = 1.0, 0.0
        fn(cv, t, dur, anchors, params)
        ov = np.asarray(cv.done(), dtype=np.float32)
        y0 = BAND_Y0 if band_y is None else band_y
        band = frame[y0:y0 + BAND_H].astype(np.float32)
        a_ = ov[..., 3:4] / 255.0
        frame[y0:y0 + BAND_H] = np.clip(band * (1 - a_) + ov[..., :3] * a_, 0, 255).astype(np.uint8)
        enc.stdin.write(frame.tobytes())
    enc.stdin.close()
    enc.wait()
    if dec:
        dec.stdout.close()
        dec.terminate()


if __name__ == "__main__":
    import sys
    from PIL import Image as _I
    kind = sys.argv[1]
    out = sys.argv[2]
    t = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    cv = Cv(BAND_H)
    KINDS[kind](cv, t, 4.0, {}, {})
    bg = Image.fromarray(designed_bg(t))
    bg.alpha_composite if False else None
    ov = cv.done()
    base = bg.convert("RGBA")
    base.alpha_composite(ov, (0, BAND_Y0))
    base.convert("RGB").resize((540, 960)).save(out)
