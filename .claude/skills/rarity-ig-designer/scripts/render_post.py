#!/usr/bin/env python3
"""
render_post.py v7 — Rarity IG carousel, rendered 100% in Python/Pillow (no design connectors).

THE HOUSE STANDARD (matches the posts made in the Brands Decoded "Maquina" software, e.g.
"Idea 01 - Liquid Death"): a mixed-card carousel, 1080x1350, one distinct photo per slide.

  hook    full-bleed photo + bottom scrim, small handle top-left, profile chip (avatar +
          @rarity.agency + blue verified badge), white headline with ONE magenta italic accent
          word, light-blue subhead near the bottom.
  light   off-white card (#EFEEEA): navy headline top, black body text, framed photo at the bottom.
  photo   full-bleed photo + dark gradient: white arrow circle, SHORT white headline with magenta
          italic accent word mid-slide, white body text at the bottom.
  dark    near-black card (#0F0A1A): white headline, white body text, framed photo at the bottom.
  lesson  off-white card, short navy headline top, photo bleeding edge to edge across the bottom.
  action  off-white card, framed photo on top, MAGENTA headline below (the "try it this week" step).
  cta     off-white card, framed photo on top, NAVY headline with a magenta italic accent word
          ("Save this post. Share it with the people who *think* like you.").

The ONLY thing that varies between posts is the headline typeface (spec["headline_font"]):
  "sans"  -> Plus Jakarta Sans ExtraBold (the look of the reference posts)
  "serif" -> Playfair Display Bold
Body text, handle, colours and layout are identical in both.

Usage:  python3 render_post.py <spec.json>   ->  slide-01.png .. slide-NN.png in spec["out_dir"]

Spec:
{
 "out_dir": ".../Idea 12 - Title/EN",
 "handle": "@rarity.agency",
 "headline_font": "sans",              # or "serif" — alternate across posts
 "slides": [
   {"type":"hook","bg":"hero.jpg","headline":"Liquid Death made water look *dangerous*",
    "subhead":"Canned water. A $1.4B valuation. Same product as your tap.","focus_x":0.5,"focus_y":0.4},
   {"type":"light","bg":"bg2.jpg","headline":"The product was *never* the problem","body":"..."},
   {"type":"photo","bg":"bg3.jpg","headline":"He picked a *fight* with the category","body":"..."},
   {"type":"dark","bg":"bg4.jpg","headline":"The *hate* became the content","body":"..."},
   ... "lesson", "action", "cta"
 ]
}
"type" may be omitted: slide 1 = hook, last = cta, then action, lesson, and the middle cycles
light, photo, dark, photo, light, photo, photo (the 11 slide standard). *word* = magenta italic.
Per slide: focus_x / focus_y (0-1 crop focus), "verified": false to hide the blue badge.
"""
import sys, os, json, re
from PIL import Image, ImageDraw, ImageFont, ImageChops

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(SKILL, "assets")
W, H = 1080, 1350
MX = 51                         # left text margin
MAGENTA = (213, 0, 87)
NAVY = (0, 26, 112)
LIGHT_BG = (239, 238, 234)
DARK_BG = (15, 10, 26)
INK = (11, 11, 12)
SUB_BLUE = (173, 213, 240)
VERIFIED = (29, 155, 240)

MIDDLE_CYCLE = ["light", "photo", "dark", "photo", "light", "photo", "photo"]


# ---------------------------------------------------------------- fonts
def _path(name):
    p = os.path.join(A, name)
    return p if os.path.exists(p) else None

HEAD_FILES = {
    "sans": (_path("headline-sans.ttf"), _path("headline-sans-italic.ttf"), 1.0, -0.045),
    "serif": (_path("headline.ttf"), _path("headline-italic.ttf"), 1.0, -0.012),
}
BODY_FILE = _path("body-inter.ttf")


def body_font(size, weight=500):
    f = ImageFont.truetype(BODY_FILE, size)
    try:
        axes = f.get_variation_axes()
        vals = []
        for ax in axes:
            n = ax["name"] if isinstance(ax["name"], str) else ax["name"].decode()
            vals.append(weight if "eight" in n else min(max(size, ax["minimum"]), ax["maximum"]))
        f.set_variation_by_axes(vals)
    except Exception:
        pass
    return f


class Head:
    def __init__(self, choice):
        reg, ita, self.scale, self.track = HEAD_FILES[choice]
        self.reg, self.ita = reg, ita or reg

    def fonts(self, size):
        s = int(round(size * self.scale))
        return ImageFont.truetype(self.reg, s), ImageFont.truetype(self.ita, s), s


# ---------------------------------------------------------------- text helpers
def adv(font, text, track):
    """Width of text with kerning kept and tracking (px per glyph) applied."""
    if not text:
        return 0
    return font.getlength(text) + track * len(text)


def draw_run(d, x, y, text, font, fill, track):
    for i, ch in enumerate(text):
        d.text((x, y), ch, font=font, fill=fill)
        nxt = text[i:i + 2]
        step = font.getlength(nxt) - font.getlength(text[i + 1:i + 2]) if len(nxt) == 2 else font.getlength(ch)
        x += step + track
    return x


def tokens(text):
    """'a *b* c' -> [('a',False),('b',True),('c',False)] split per word."""
    out = []
    for i, part in enumerate(re.split(r"\*", text)):
        for w in part.split():
            out.append((w, i % 2 == 1))
    return out


def wrap(toks, fr, fi, track, space, max_w):
    lines, cur, cw = [], [], 0
    for w, it in toks:
        f = fi if it else fr
        ww = adv(f, w, track)
        add = ww if not cur else space + ww
        if cur and cw + add > max_w:
            lines.append(cur)
            cur, cw = [(w, it, ww)], ww
        else:
            cur.append((w, it, ww))
            cw += add
    if cur:
        lines.append(cur)
    return lines


def draw_headline(img, head, text, x, y, size, max_w, max_lines, color, accent=MAGENTA, pitch=1.03,
                  anchor="top", min_size=30):
    """Fits (shrinks) to max_lines, draws, returns (bottom_y, size_used, nlines)."""
    toks = tokens(text)
    d = ImageDraw.Draw(img)
    s = size
    while True:
        fr, fi, real = head.fonts(s)
        track = head.track * real
        space = 0.20 * real
        lines = wrap(toks, fr, fi, track, space, max_w)
        if (len(lines) <= max_lines and all(sum(w for *_, w in ln) <= max_w for ln in lines)) or s <= min_size:
            break
        s -= 2
    step = int(real * pitch)
    top = y - (len(lines) - 1) * step if anchor == "bottom" else y
    for li, ln in enumerate(lines):
        cx = x
        ly = top + li * step
        for w, it, ww in ln:
            f = fi if it else fr
            draw_run(d, cx, ly, w, f, accent if it else color, track)
            cx += ww + space
    return top + len(lines) * step, s, len(lines)


def draw_body(img, text, x, y, size, max_w, color, pitch, weight=500, max_lines=6):
    d = ImageDraw.Draw(img)
    s = size
    while True:
        f = body_font(s, weight)
        track = -0.012 * s
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if cur and adv(f, t, track) > max_w:
                lines.append(cur)
                cur = w
            else:
                cur = t
        lines.append(cur)
        if len(lines) <= max_lines or s <= 22:
            break
        s -= 2
    step = int(s * pitch)
    for i, ln in enumerate(lines):
        draw_run(d, x, y + i * step, ln, f, color, track)
    return y + len(lines) * step


def draw_handle(img, handle, color):
    f = body_font(15, 700)
    draw_run(ImageDraw.Draw(img), MX, 44, handle, f, color, -0.45)


# ---------------------------------------------------------------- image helpers
def cover(path, w, h, fx=0.5, fy=0.5):
    im = Image.open(path).convert("RGB")
    sc = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * sc)), max(h, round(im.height * sc))), Image.LANCZOS)
    x = round((im.width - w) * fx)
    y = round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def scrim(img, start=0.40, end_a=0.90, base=0.10, top_a=0.30):
    """Dark vertical gradient for legibility on full-bleed photos."""
    g = Image.new("L", (1, H))
    px = g.load()
    for y in range(H):
        t = y / H
        a = base
        if t > start:
            a += (end_a - base) * min(1, ((t - start) / (1 - start))) ** 1.25
        if t < 0.16:
            a = max(a, top_a * (1 - t / 0.16))
        px[0, y] = int(255 * min(a, 0.96))
    mask = g.resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, mask)


def ss_icon(size, painter, scale=4):
    big = Image.new("RGBA", (size * scale, size * scale), (0, 0, 0, 0))
    painter(ImageDraw.Draw(big), size * scale)
    return big.resize((size, size), Image.LANCZOS)


def arrow_circle(img, x, y, d=52):
    def paint(g, s):
        g.ellipse((0, 0, s - 1, s - 1), fill=(255, 255, 255, 255))
        c = s / 2
        lw = int(s * 0.055)
        g.line((c - s * .20, c, c + s * .20, c), fill=(10, 10, 10, 255), width=lw)
        g.line((c + s * .05, c - s * .15, c + s * .21, c, ), fill=(10, 10, 10, 255), width=lw)
        g.line((c + s * .05, c + s * .15, c + s * .21, c), fill=(10, 10, 10, 255), width=lw)
    img.paste(ss_icon(d, paint), (x, y), ss_icon(d, paint))


def verified_badge(img, x, y, d=27):
    def paint(g, s):
        g.ellipse((0, 0, s - 1, s - 1), fill=VERIFIED + (255,))
        lw = int(s * 0.1)
        g.line((s * .27, s * .52, s * .44, s * .68), fill=(255, 255, 255, 255), width=lw)
        g.line((s * .44, s * .68, s * .74, s * .34), fill=(255, 255, 255, 255), width=lw)
    ic = ss_icon(d, paint)
    img.paste(ic, (x, y), ic)


def avatar(img, x, y, d=38):
    def paint(g, s):
        g.ellipse((0, 0, s - 1, s - 1), fill=(255, 255, 255, 255))
    ic = ss_icon(d, paint)
    img.paste(ic, (x, y), ic)
    sym = _path("rarity-symbol-color.png")
    if sym:
        s = Image.open(sym).convert("RGBA")
        s.thumbnail((int(d * 0.66), int(d * 0.66)), Image.LANCZOS)
        img.paste(s, (x + (d - s.width) // 2, y + (d - s.height) // 2), s)


def luminance_ratio_white(img, box):
    reg = img.crop(box).convert("L")
    px = list(reg.get_flattened_data())
    lum = sum(px) / len(px) / 255.0
    lin = ((lum + 0.055) / 1.055) ** 2.4
    return 1.05 / (lin + 0.05)


# ---------------------------------------------------------------- slide builders
def build(slide, kind, head, handle, base_dir):
    bg = slide.get("bg")
    if bg and not os.path.isabs(bg):
        bg = os.path.join(base_dir, bg)
    if not bg or not os.path.exists(bg):
        sys.exit(f"ERROR: slide type '{kind}' needs its own photo ('bg'): {bg}")
    fx, fy = slide.get("focus_x", 0.5), slide.get("focus_y", 0.4)
    hl = slide.get("headline", "")
    body = slide.get("body", "")

    if kind == "hook":
        img = scrim(cover(bg, W, H, fx, fy), start=0.50, end_a=0.88, base=0.06)
        draw_handle(img, handle, (255, 255, 255))
        hy = slide.get("headline_bottom", 951)
        # measure first to anchor the block above the subhead, chip above the block
        probe = Image.new("RGB", (W, H))
        _, s_used, n = draw_headline(probe, head, hl, 48, 0, 72, 975, 3, (255, 255, 255), pitch=0.98, min_size=44)
        step = int(head.fonts(s_used)[2] * 0.98)
        top = hy - (n - 1) * step - step
        draw_headline(img, head, hl, 48, top, s_used, 975, 3, (255, 255, 255), pitch=0.98, min_size=44)
        cy = top - 88
        avatar(img, 47, cy)
        f = body_font(30, 600)
        draw_run(ImageDraw.Draw(img), 93, cy + 1, handle, f, (255, 255, 255), -0.6)
        if slide.get("verified", True):
            verified_badge(img, int(93 + adv(f, handle, -0.6)) + 5, cy + 5)
        if slide.get("subhead"):
            draw_body(img, slide["subhead"], 47, 1168, 34, 985, SUB_BLUE, 1.25, weight=500, max_lines=2)
        return img

    if kind == "photo":
        img = scrim(cover(bg, W, H, fx, fy), start=0.38, end_a=0.92, base=0.14)
        draw_handle(img, handle, (255, 255, 255))
        arrow_circle(img, 57, 543)
        draw_headline(img, head, hl, MX + 1, 660, 48, 975, 2, (255, 255, 255), pitch=1.05, min_size=34)
        if body:
            draw_body(img, body, MX, 1024, 46, 935, (255, 255, 255), 1.22, weight=500, max_lines=4)
        r = luminance_ratio_white(img, (MX, 1020, W - MX, 1180))
        if r < 4.5:
            print(f"  [contrast] body zone white-on-photo {r:.1f}:1 LOW — move focus or pick a darker photo")
        return img

    if kind in ("light", "dark"):
        dark = kind == "dark"
        img = Image.new("RGB", (W, H), DARK_BG if dark else LIGHT_BG)
        draw_handle(img, handle, (255, 255, 255) if dark else (10, 10, 10))
        draw_headline(img, head, hl, MX, 108, 76, 960, 3, (255, 255, 255) if dark else NAVY, pitch=1.03)
        if body:
            draw_body(img, body, MX, 478, 36, 990, (255, 255, 255) if dark else INK, 1.2 if dark else 1.4,
                      weight=500, max_lines=5)
        img.paste(cover(bg, 980, 520, fx, fy), (50, 790))
        return img

    if kind == "lesson":
        img = Image.new("RGB", (W, H), LIGHT_BG)
        draw_handle(img, handle, (10, 10, 10))
        draw_headline(img, head, hl, MX, 142, 54, 960, 2, NAVY, pitch=1.03)
        img.paste(cover(bg, W, 735, fx, fy), (0, H - 735))
        return img

    if kind in ("action", "cta"):
        img = Image.new("RGB", (W, H), LIGHT_BG)
        draw_handle(img, handle, (10, 10, 10))
        img.paste(cover(bg, 986, 612, fx, fy), (51, 128))
        col = MAGENTA if kind == "action" else NAVY
        draw_headline(img, head, hl, MX, 818, 70, 975, 4, col, pitch=1.04)
        return img

    sys.exit(f"ERROR: unknown slide type '{kind}'")


def assign_types(slides):
    n = len(slides)
    mid = [MIDDLE_CYCLE[i % len(MIDDLE_CYCLE)] for i in range(max(0, n - 4))]
    default = ["hook"] + mid + ["lesson", "action", "cta"][-min(3, n - 1):] if n > 1 else ["hook"]
    default = default[:n]
    return [s.get("type") or default[i] for i, s in enumerate(slides)]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    spec_path = os.path.abspath(sys.argv[1])
    spec = json.load(open(spec_path))
    base_dir = os.path.dirname(spec_path)
    choice = spec.get("headline_font", "sans")
    if choice not in HEAD_FILES or not HEAD_FILES[choice][0]:
        sys.exit(f"headline_font must be 'sans' or 'serif' with its font files in {A}")
    head = Head(choice)
    out = spec["out_dir"]
    os.makedirs(out, exist_ok=True)
    handle = spec.get("handle", "@rarity.agency")
    types = assign_types(spec["slides"])
    for i, (s, t) in enumerate(zip(spec["slides"], types), 1):
        img = build(s, t, head, handle, base_dir)
        fn = os.path.join(out, f"slide-{i:02d}.png")
        img.save(fn)
        print(f"slide {i:02d} [{t}] -> {fn}")


if __name__ == "__main__":
    main()
