#!/usr/bin/env python3
"""
localize_post.py: render the ES and PT versions of the October 2026 carousels in the house design.

Reads copy from "Ideas October 2026/Carousel Copy/localized_copy.py" and the per slide source photos from
"Ideas October 2026/Post Images/v2/<PNN_*>_sNN.jpg" (slide k uses sNN, slide 11 reuses s01). The crop of every
photo is auto matched against the already published EN slide so ES/PT keep the same framing.

  python3 localize_post.py            # all ideas, ES + PT
  python3 localize_post.py 2 5        # only ideas 2 and 5
Writes <Designs dir>/Idea NN - Title/{ES,PT}/slide-01..11.png and appends "## ES" / "## PT" to the caption md.
Headline font alternates per idea (odd = sans, even = serif); ES and PT of one idea share the font.
"""
import sys, os, re, json, glob, subprocess, importlib.util
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "../../../.."))
IDEAS_DIR = os.path.join(REPO, "public/Instagram Briefings/Ideas October 2026")
DESIGNS = os.path.join(REPO, "public/Instagram Briefings/Designs October 2026")
V2 = os.path.join(IDEAS_DIR, "Post Images/v2")
SCRATCH = os.environ.get("LOCALIZE_SCRATCH", os.path.join(REPO, ".publish_state/localize"))
PREFIX = {1: "P01_", 2: "P02_", 3: "P03_", 4: "P04_", 5: "P05_", 6: "P06_", 7: "P07_", 8: "P08_",
          9: "P09_", 10: "P10_", 11: "DTC_"}
TYPES = ["hook", "light", "photo", "dark", "photo", "light", "photo", "photo", "lesson", "action", "cta"]
REGION = {  # (x, y, w, h) of the photo area in the EN slide, matched for crop focus
    "hook": (0, 40, 1080, 480), "photo": (0, 40, 1080, 480), "light": (50, 790, 980, 520),
    "dark": (50, 790, 980, 520), "lesson": (0, 615, 1080, 735), "action": (51, 128, 986, 612),
    "cta": (51, 128, 986, 612)}
SIZE = {"light": (980, 520), "dark": (980, 520), "lesson": (1080, 735), "action": (986, 612), "cta": (986, 612)}


def load_copy():
    spec = importlib.util.spec_from_file_location("lc", os.path.join(IDEAS_DIR, "Carousel Copy/localized_copy.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cover(im, w, h, fx, fy):
    sc = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * sc)), max(h, round(im.height * sc))), Image.BILINEAR)
    x, y = round((im.width - w) * fx), round((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))


def gray(im):
    a = np.asarray(im.convert("L").resize((im.width // 4, im.height // 4)), dtype=np.float32)
    return (a - a.mean()) / (a.std() + 1e-6)


def best_focus(photo, en_slide, kind):
    rx, ry, rw, rh = REGION[kind]
    cw, ch = (1080, 1350) if kind in ("hook", "photo") else SIZE[kind]
    target = gray(en_slide.crop((rx, ry, rx + rw, ry + rh)))
    src = Image.open(photo).convert("RGB")
    best = (-9, 0.5, 0.5)
    for fx in (0, .25, .5, .75, 1):
        for fy in (0, .15, .3, .45, .6, .8, 1):
            c = cover(src, cw, ch, fx, fy)
            if kind in ("hook", "photo"):
                c = c.crop((0, 40, 1080, 520))
            s = float((gray(c) * target).mean())
            if s > best[0]:
                best = (s, fx, fy)
    return best


def bad_chars(text):
    return re.findall(r"[-–—#]|[\U0001F300-\U0001FAFF]", text.replace("1. ", "").replace("2. ", "")
                      .replace("3. ", "").replace("4. ", ""))


def main():
    only = {int(a) for a in sys.argv[1:]}
    lc = load_copy()
    os.makedirs(SCRATCH, exist_ok=True)
    for n, data in lc.IDEAS.items():
        if only and n not in only:
            continue
        idea_dir = glob.glob(os.path.join(DESIGNS, f"Idea {n:02d} - *"))[0]
        photos = {k: glob.glob(os.path.join(V2, f"{PREFIX[n]}*_s{k:02d}.jpg"))[0] for k in range(1, 11)}
        photos[11] = photos[1]
        en = {k: Image.open(os.path.join(idea_dir, "EN", f"slide-{k:02d}.png")).convert("RGB") for k in range(1, 12)}
        foc = {}
        for k in range(1, 12):
            sc, fx, fy = best_focus(photos[k], en[k], TYPES[k - 1])
            foc[k] = (fx, fy)
            print(f"  idea {n:02d} slide {k:02d} [{TYPES[k-1]}] match {sc:.2f} focus {fx},{fy}")
        font = "sans" if n % 2 else "serif"
        for lang, code in (("es", "ES"), ("pt", "PT")):
            d = data[lang]
            slides = []
            for k in range(1, 12):
                s = {"type": TYPES[k - 1], "bg": photos[k], "focus_x": foc[k][0], "focus_y": foc[k][1]}
                if k <= 9:
                    h, b = d["slides"][k - 1]
                    s["headline"] = h
                    if k == 1:
                        s["subhead"] = b
                    elif k <= 8:
                        s["body"] = b
                elif k == 10:
                    s["headline"] = d["slides"][8][1]
                else:
                    s["headline"] = lc.CTA[lang]
                slides.append(s)
            texts = [x for s in slides for x in (s.get("headline", ""), s.get("body", ""), s.get("subhead", ""))]
            texts.append(d["caption"])
            probs = [t for t in texts if bad_chars(t)]
            if probs:
                sys.exit(f"idea {n} {code}: forbidden characters in: {probs[:2]}")
            out = os.path.join(idea_dir, code)
            os.makedirs(out, exist_ok=True)
            spec = {"out_dir": out, "headline_font": font, "slides": slides}
            sp = os.path.join(SCRATCH, f"spec_{n:02d}_{code}.json")
            json.dump(spec, open(sp, "w"), ensure_ascii=False, indent=1)
            subprocess.run([sys.executable, os.path.join(HERE, "render_post.py"), sp], check=True,
                           stdout=subprocess.DEVNULL)
            # caption sections (appended once)
            cap = glob.glob(os.path.join(idea_dir, "Caption - *.md"))[0]
            txt = open(cap).read()
            if f"## {code}" not in txt:
                txt = txt.rstrip() + f"\n\n## {code}\n\n{d['caption']}\n\n{lc.SAVE[lang]}\n"
                open(cap, "w").write(txt)
        print(f"idea {n:02d} done ({font})")


if __name__ == "__main__":
    main()
