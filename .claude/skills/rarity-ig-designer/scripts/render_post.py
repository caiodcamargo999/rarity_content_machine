#!/usr/bin/env python3
"""
render_post.py — Rarity IG art, rendered 100% by Claude (NO design connectors).
v6 — replaces v5's dark-patch-behind-text approach with ADAPTIVE LETTER COLOR: every text
element (headline, subhead, eyebrow, kicker, handle, page counter, CTA logo) samples its own
local background luminance and switches between white/teal (on a dark zone) and navy (on a
light zone) — whichever actually contrasts. No patches, no chips: the photo shows through
clean everywhere and the letter color does the legibility work, per Caio's 2026-07-11 direction
("if background is darker, letter lighter" — and the converse: light background, dark letter).
The old fixed-white + blurred-dark-patch approach either read as a hard-edged sticker (tight
blur) or still under-shot 4.5:1 (loose blur) — this replaces both call sites entirely.

Look: every slide is its OWN full-bleed photo in REAL colors (no brand-navy wash). A bottom
scrim + subtle vignette + grain still apply for mood, but at a much lighter touch than v5,
since letter-color adaptation now carries contrast instead of image-darkening.
Headline = editorial SERIF (Playfair Display, assets/headline.ttf), with *italic* accent words
in the accent colour. Rarity symbol sits transparent top-right on EVERY slide. No date anywhere.

Usage:  python3 render_post.py <spec.json>   ->  slide-1.png .. slide-N.png in spec["out_dir"]
Every render prints a "[contrast]" line per text zone: which colour was picked (light/dark) and
the resulting ratio against the 4.5:1 bar. Anything still flagged LOW CONTRAST after adaptive
colour needs a focus_x/focus_y change or a different photo — the letter color can't rescue a
zone that's exactly mid-gray (contrast ~1:1 against both white AND navy).

Spec:
{
 "out_dir": "<.../EN>", "handle": "@rarity.agency",
 "accent": "#D50057",                      # default accent; magenta | #FFE400 yellow | #FF3B3B red
 "slides": [
   {"type":"hook","bg":"<.../hero.jpg>","focus_x":0.5,"focus_y":0.4,
    "eyebrow":"Eugene Schwartz, 1966","headline":"You can't *create* desire.","size":126,
    "subhead":"What the most stolen book in advertising knew about your ads ->"},
   {"type":"body","bg":"<.../bg2.jpg>","kicker":"The mistake",
    "headline":"Most brands burn millions *shouting* at people who never buy.","size":94},
   {"type":"stat","bg":"<.../bg3.jpg>","stat":"85%","label":"of ads are ignored",
    "sub":"They sell the product, not the desire already in the room."},
   {"type":"cta","bg":"<.../bg4.jpg>","headline":"Save this. *Send it* to someone who runs ads.","size":98}
 ]
}

Per-slide options: "accent" (override colour, always used as-is for italic words + stat number —
NOT adapted, it's the deliberate brand accent), "head_color" (force the whole headline to one
colour, skips adaptation), "accent_last", "focus_x"/"focus_y", "dark" (0-1 extra full-frame
darken — now a MOOD knob, not the primary contrast mechanism), "bot_a"/"bot_start" (scrim).
Wrap emphasis word(s) in *asterisks* -> italic + accent colour.
"""
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(SKILL, "assets")
W, H = 1080, 1350
M = 80
TXW = int((W - 2*M) * 0.78)   # approx text-width for zone sampling (avoid far-right photo edge)

def first(paths):
    for p in paths:
        if p and os.path.exists(p): return p
    return None

HEAD   = first([os.path.join(A, "headline.ttf"), "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"])
HEADIT = first([os.path.join(A, "headline-italic.ttf"), os.path.join(A, "headline.ttf"),
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"])
BEN_R  = first([os.path.join(A, "BentonSans-Regular.otf"), "/usr/share/fonts/truetype/lato/Lato-Regular.ttf"])
BEN_T  = first([os.path.join(A, "BentonSans-Thin.otf"),    "/usr/share/fonts/truetype/lato/Lato-Light.ttf"])
ARROW  = first(["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
                 "/System/Library/Fonts/Supplemental/Arial.ttf",
                 "/System/Library/Fonts/Helvetica.ttc", BEN_R])
SYMW   = first([os.path.join(A, "rarity-symbol-white.png"), os.path.join(A, "rarity-symbol.png")])
LOGO_W = first([os.path.join(A, "rarity-logo-white.png")])
LOGO_D = first([os.path.join(A, "rarity-logo-blue.png"), LOGO_W])

def hx(c): return tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
WHITE=(255,255,255); TEAL=hx('#0fc1af'); NAVY=hx('#001A70'); MUT=(210,216,230); OFF=(240,240,236)
MUT_DARK=(46,54,78); TEAL_DARK=NAVY; HANDLE_LIGHT=(238,238,238); HANDLE_DARK=(52,58,74)

def Fh(s): return ImageFont.truetype(HEAD, s)
def Fi(s): return ImageFont.truetype(HEADIT, s)
def Fb(s): return ImageFont.truetype(BEN_R, s)
def Ft(s): return ImageFont.truetype(BEN_T, s)
def Fa(s): return ImageFont.truetype(ARROW, s)
_md = ImageDraw.Draw(Image.new("RGB", (8, 8)))

# ---------------------------------------------------------------- image treatment (REAL COLOR)
def cover(img, fx=0.5, fy=0.5):
    scl = max(W/img.width, H/img.height)
    im = img.resize((max(W, int(img.width*scl)), max(H, int(img.height*scl))), Image.LANCZOS)
    left = int((im.width-W)*fx); top = int((im.height-H)*fy)
    left = max(0, min(im.width-W, left)); top = max(0, min(im.height-H, top))
    return im.crop((left, top, left+W, top+H)).convert("RGB")

def vignette(im):
    mask = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mask)
    d.ellipse([-int(W*0.32), -int(H*0.18), int(W*1.32), int(H*1.18)], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(230))
    return Image.composite(im, Image.new("RGB", (W, H), (10, 11, 16)), mask)

def scrim(bot_a=252, bot_start=0.34, top_a=150, top_h=230, col=(5, 6, 12)):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    s = int(H*bot_start)
    for y in range(s, H):
        a = int(bot_a*((y-s)/(H-s))**1.12); d.line([(0, y), (W, y)], fill=col+(a,))
    for y in range(top_h):
        a = int(top_a*(1-y/top_h)); d.line([(0, y), (W, y)], fill=col+(a,))
    return g

def grain(im, a=0.03):
    n = Image.effect_noise((W, H), 24).convert("L")
    return Image.blend(im, Image.merge("RGB", (n, n, n)), a)

def treat(img, fx=0.5, fy=0.5, bot_a=252, bot_start=0.34, dark=0.0, blur_zone=None, blur_r=25):
    base = cover(img, fx, fy)
    if blur_zone:
        blurred = base.filter(ImageFilter.GaussianBlur(blur_r))
        mask = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(mask)
        if len(blur_zone) == 4:
            d.rectangle(blur_zone, fill=255)
        elif len(blur_zone) == 2:
            d.rectangle([0, blur_zone[0], W, blur_zone[1]], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(70))
        base = Image.composite(blurred, base, mask)
    if dark: base = Image.blend(base, Image.new("RGB", (W, H), (6, 8, 14)), dark)
    base = vignette(base)
    base = Image.alpha_composite(base.convert("RGBA"), scrim(bot_a, bot_start)).convert("RGB")
    return grain(base)

# ---------------------------------------------------------------- contrast: measure AND adapt the LETTER
def zone_luminance(im, box):
    x0, y0, x1, y1 = box
    x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(W, int(x1)), min(H, int(y1))
    if x1 <= x0 or y1 <= y0: return 0.3, (90, 90, 90)
    px = im.convert("RGB").resize((1, 1), Image.LANCZOS, box=(x0, y0, x1, y1)).getpixel((0, 0))
    return (0.2126*px[0] + 0.7152*px[1] + 0.0722*px[2]) / 255, px

def ratio_for(Lbg, color):
    Lc = (0.2126*color[0] + 0.7152*color[1] + 0.0722*color[2]) / 255
    lighter, darker = max(Lbg, Lc), min(Lbg, Lc)
    return (lighter + 0.05) / (darker + 0.05)

def adapt(im, box, light, dark, label=""):
    """THE core v6 mechanism. Samples the background under `box` and returns whichever of
    light/dark contrasts better against it — dark background -> light letter, light
    background -> dark (navy) letter. Always prints the decision so the render log shows
    exactly why a colour was picked, and still flags anything that can't clear 4.5:1 either
    way (a genuinely mid-gray zone needs a crop change, not a colour trick)."""
    Lbg, px = zone_luminance(im, box)
    r_light, r_dark = ratio_for(Lbg, light), ratio_for(Lbg, dark)
    choice, ratio = (light, r_light) if r_light >= r_dark else (dark, r_dark)
    tag = "light" if choice is light else "dark"
    flag = "ok" if ratio >= 4.5 else "*** LOW CONTRAST even after adapting, fix the crop/photo ***"
    print(f"  [contrast] {label}: bg~rgb{px} -> {tag} letter, {ratio:.1f}:1  {flag}")
    return choice

# ---------------------------------------------------------------- marks / chrome
def sym(h):
    s = Image.open(SYMW).convert("RGBA"); r = h/s.height
    return s.resize((max(1, int(s.width*r)), h), Image.LANCZOS)

def tracked(d, xy, s, font, fill, tr=3):
    x, y = xy
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font)+tr
    return x

def text_w(s, font, tr=3):
    return sum(_md.textlength(ch, font=font) for ch in s) + tr*len(s)

def topbar(im, page=None):
    d = ImageDraw.Draw(im, "RGBA")
    lab_col = adapt(im, (M, 40, M+230, 74), HANDLE_LIGHT, HANDLE_DARK, "top label zone")
    tracked(d, (M, 52), "RARITY AGENCY", Ft(23), lab_col+(235,), 4)
    s = sym(54); im.paste(s, (W-M-s.width, 42), s)
    if page:
        pf = Ft(23)
        pg_col = adapt(im, (W-M-140, 1200, W-M, 1230), (226,230,240), HANDLE_DARK, "page counter zone")
        d.text((W-M-d.textlength(page, font=pf), 1214), page, font=pf, fill=pg_col+(230,))

# ---------------------------------------------------------------- headline (serif + italic accents)
def toks(text):
    raw = []
    for i, seg in enumerate(text.split("*")):
        it = (i % 2 == 1)
        for w in seg.split(): raw.append([w, it])
    out = []
    for w, it in raw:
        if out and all(c in ".,!?:;…" for c in w): out[-1][0] += w
        else: out.append([w, it])
    return [(w, it) for w, it in out]

def wrap_tok(tokens, size, maxw):
    F = Fh(size); I = Fi(size); sp = _md.textlength(" ", font=F)
    lines = []; cur = []; cw = 0
    for w, it in tokens:
        f = I if it else F; ww = _md.textlength(w, font=f)
        add = ww if not cur else sp+ww
        if cur and cw+add > maxw:
            lines.append(cur); cur = [(w, it, ww)]; cw = ww
        else:
            cur.append((w, it, ww)); cw += add
    if cur: lines.append(cur)
    return lines, sp

def line_w(line, sp): return sum(w for _, _, w in line) + sp*(len(line)-1)

def fit_size(text, size, maxw, max_h, lead):
    while size > 54:
        lines, sp = wrap_tok(toks(text), size, maxw)
        if int(size*lead)*len(lines) <= max_h and all(line_w(l, sp) <= maxw for l in lines):
            return size
        size -= 3
    return size

def draw_head(im, text, size, accent, bottom_y, align="left", lead=1.12,
              accent_last=True, max_h=680, roman=WHITE):
    size = fit_size(text, size, W-2*M, max_h, lead)
    d = ImageDraw.Draw(im, "RGBA")
    lines, sp = wrap_tok(toks(text), size, W-2*M)
    F = Fh(size); I = Fi(size); lh = int(size*lead)
    has_it = any(it for _, it in toks(text))
    y = bottom_y - lh*len(lines); top = y
    for li, ln in enumerate(lines):
        x = (W-line_w(ln, sp))//2 if align == "center" else M
        last = (li == len(lines)-1)
        for w, it, ww in ln:
            if it: fill = accent
            elif (not has_it and accent_last and last): fill = accent
            else: fill = roman
            d.text((x, y), w, font=(I if it else F), fill=fill); x += ww+sp
        y += lh
    return top

def draw_sub(im, text, bottom_y, size=30, fill=MUT, maxw=None):
    maxw = maxw or (W-2*M); F = Fb(size); d = ImageDraw.Draw(im, "RGBA")
    text = text.replace("*", "").replace("->", "→")
    words = text.split(); lines = []; cur = ""
    for wd in words:
        t = (cur+" "+wd).strip()
        if _md.textlength(t.replace("→", ""), font=F) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    lh = int(size*1.3); y = bottom_y - lh*len(lines); top = y
    for ln in lines:
        if "→" in ln:
            pre = ln.split("→")[0]
            d.text((M, y), pre, font=F, fill=fill)
            d.text((M+d.textlength(pre, font=F)+4, y-1), "→", font=Fa(size), fill=fill)
        else:
            d.text((M, y), ln, font=F, fill=fill)
        y += lh
    return top

def kicker(im, text, y, accent, col):
    """Body/stat kicker: small accent dash + label. v6: no backing patch, colour adapts instead."""
    txt = text.upper()
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle([M, y+7, M+52, y+18], 5, fill=accent)
    tracked(d, (M+70, y), txt, Fb(26), col+(255,), 3)

# ---------------------------------------------------------------- slides
def render(spec):
    out = spec["out_dir"]; os.makedirs(out, exist_ok=True)
    dflt = hx(spec.get("accent", "#D50057"))
    handle = spec.get("handle", "@rarity.agency")
    total = len(spec["slides"]); n = 0
    for sl in spec["slides"]:
        n += 1; t = sl.get("type", "body"); fn = os.path.join(out, f"slide-{n}.png")
        p = sl.get("bg") or spec.get("hero_image")
        if not p or not os.path.exists(p):
            raise SystemExit(f"[render] slide {n} ({t}) has no real photo in 'bg'. Every slide needs its "
                             f"own image; flat / solid / gradient cards are not allowed.")
        img = Image.open(p).convert("RGB")
        fx = sl.get("focus_x", 0.5); fy = sl.get("focus_y", 0.42)
        accent = hx(sl["accent"]) if sl.get("accent") else dflt
        forced_roman = hx(sl["head_color"]) if sl.get("head_color") else None
        page = f"{n:02d} / {total:02d}"
        print(f"slide {n} ({t}):")

        if t == "hook":
            im = treat(img, fx, fy, bot_a=sl.get("bot_a",236), bot_start=sl.get("bot_start",0.32),
                       dark=sl.get("dark",0.0), blur_zone=sl.get("blur_zone"), blur_r=sl.get("blur_r", 25))
            topbar(im)
            d = ImageDraw.Draw(im, "RGBA")
            handle_col = adapt(im, (M,1195,M+260,1228), HANDLE_LIGHT, HANDLE_DARK, "handle zone")
            tracked(d, (M, 1206), handle, Fb(27), handle_col+(238,), 1)
            sub_top = 1188
            if sl.get("subhead"):
                sub_col = adapt(im, (M,1140,M+TXW,1225), MUT, MUT_DARK, "subhead zone")
                sub_top = draw_sub(im, sl["subhead"], 1176, 31, sub_col)
            head_zone = (M, sub_top-220, M+TXW, sub_top-60)
            roman = forced_roman or adapt(im, head_zone, WHITE, NAVY, "headline/subhead zone (general)")
            head_top = draw_head(im, sl["headline"], sl.get("size", 124), accent, sub_top-60,
                                 "left", 1.12, sl.get("accent_last", True), 560, roman)
            if sl.get("eyebrow"):
                etxt = sl["eyebrow"].upper(); ew = text_w(etxt, Fb(25)); ey = head_top-60
                eye_col = TEAL if (roman == WHITE or forced_roman == WHITE) else adapt(im, (M, ey-4, M+ew+10, ey+30), TEAL, TEAL_DARK, "eyebrow zone")
                d = ImageDraw.Draw(im, "RGBA")
                tracked(d, (M, ey), etxt, Fb(25), eye_col+(255,), 3)
            im.convert("RGB").save(fn); continue

        if t == "cta":
            im = treat(img, fx, fy, bot_a=sl.get("bot_a",250), bot_start=sl.get("bot_start",0.16),
                       dark=sl.get("dark",0.42), blur_zone=sl.get("blur_zone"), blur_r=sl.get("blur_r", 25))
            topbar(im)
            Llogo, _ = zone_luminance(im, (W*0.5-140, 470, W*0.5+140, 610))
            use_dark_logo = ratio_for(Llogo, NAVY) > ratio_for(Llogo, WHITE)
            lg = Image.open(LOGO_D if use_dark_logo else LOGO_W).convert("RGBA")
            r = 250/lg.width; lg = lg.resize((250, int(lg.height*r)), Image.LANCZOS)
            im.paste(lg, ((W-250)//2, 470), lg)
            d = ImageDraw.Draw(im, "RGBA")
            head_zone = (W*0.5-TXW/2, 780, W*0.5+TXW/2, 950)
            roman = forced_roman or adapt(im, head_zone, WHITE, NAVY, "CTA headline zone")
            draw_head(im, sl["headline"], sl.get("size", 104), accent, 900, "center", 1.12,
                      sl.get("accent_last", True), 430, roman)
            handle_col = adapt(im, (W*0.5-140,1195,W*0.5+140,1228), (234,234,234), HANDLE_DARK, "CTA handle zone")
            d.text(((W-d.textlength(handle, font=Fb(28)))//2, 1206), handle, font=Fb(28), fill=handle_col+(236,))
            im.convert("RGB").save(fn); continue

        if t == "stat":
            im = treat(img, fx, fy, bot_a=sl.get("bot_a",250), bot_start=sl.get("bot_start",0.30),
                       dark=sl.get("dark",0.0), blur_zone=sl.get("blur_zone"), blur_r=sl.get("blur_r", 25))
            topbar(im, page)
            d = ImageDraw.Draw(im, "RGBA")
            handle_col = adapt(im, (M,1195,M+260,1228), HANDLE_LIGHT, HANDLE_DARK, "handle zone")
            tracked(d, (M, 1206), handle, Fb(27), handle_col+(238,), 1)
            sub_top = 1150
            if sl.get("sub"):
                sub_col = adapt(im, (M,1095,M+TXW,1168), OFF, MUT_DARK, "sub zone")
                sub_top = draw_sub(im, sl["sub"], 1150, 33, sub_col)
            S = 236
            while S > 120 and _md.textlength(sl["stat"], font=Fh(S)) > W-2*M-8: S -= 6
            bb = Fh(S).getbbox(sl["stat"]); nh = bb[3]-bb[1]; num_top = sub_top-30-nh
            d.text((M-6, num_top-bb[1]), sl["stat"], font=Fh(S), fill=accent)
            if sl.get("label"):
                ltxt = sl["label"].upper(); lw = text_w(ltxt, Fb(28)); ly = num_top-60
                lab_col = adapt(im, (M, ly-4, M+lw+10, ly+30), TEAL, TEAL_DARK, "label zone")
                d = ImageDraw.Draw(im, "RGBA")
                tracked(d, (M, ly), ltxt, Fb(28), lab_col+(255,), 3)
            im.convert("RGB").save(fn); continue

        # body
        im = treat(img, fx, fy, bot_a=sl.get("bot_a",248), bot_start=sl.get("bot_start",0.34),
                   dark=sl.get("dark",0.0), blur_zone=sl.get("blur_zone"), blur_r=sl.get("blur_r", 25))
        topbar(im, page)
        d = ImageDraw.Draw(im, "RGBA")
        handle_col = adapt(im, (M,1195,M+260,1228), HANDLE_LIGHT, HANDLE_DARK, "handle zone")
        tracked(d, (M, 1206), handle, Fb(27), handle_col+(238,), 1)
        head_zone = (M, 1150-190, M+TXW, 1150)
        roman = forced_roman or adapt(im, head_zone, WHITE, NAVY, "headline zone (general)")
        head_top = draw_head(im, sl["headline"], sl.get("size", 96), accent, 1150,
                             "left", 1.12, sl.get("accent_last", True), 720, roman)
        if sl.get("kicker"):
            kt = sl["kicker"]; ky = head_top-62
            kw = text_w(kt.upper(), Fb(26))
            k_col = TEAL if (roman == WHITE or forced_roman == WHITE) else adapt(im, (M+70, ky-4, M+70+kw+10, ky+30), TEAL, TEAL_DARK, "kicker zone")
            kicker(im, kt, ky, accent, k_col)
        im.convert("RGB").save(fn)
    print("done", total, "slides ->", out)
    print("Adaptive letter colour handled contrast above. Anything still flagged LOW CONTRAST")
    print("needs a focus_x/focus_y change or a different photo (a truly mid-gray zone can't be")
    print("rescued by switching letter colour) — not a re-run of the same spec.")

if __name__ == "__main__":
    render(json.load(open(sys.argv[1])))
    print("HEAD:", os.path.basename(HEAD), "| SYMBOL:", os.path.basename(SYMW), "| adaptive-color v6")
