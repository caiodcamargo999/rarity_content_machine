#!/usr/bin/env python3
"""Organize a Brands Decoded Maquina carousel export (.zip) into the Rarity Content Machine layout.

Usage:
  organize_export.py --zip <export.zip> --num 1 --title "Liquid Death Made Water Look Dangerous" \
      [--month "October 2026"] [--repo <repo root>] [--lang EN] [--force]

Result:
  <repo>/public/Instagram Briefings/Designs <Month Year>/Idea NN - <Title>/<LANG>/slide-01.png ... slide-NN.png

Rules:
  * Every image in the zip must be a PNG/JPEG of 1080x1350 (4:5). Anything else aborts: the Graph API
    crops later slides to the first slide's ratio, so a wrong size ruins the carousel.
  * Between 2 and 20 slides (Instagram carousel limit via the API is 20).
  * Idempotent: if the target folder already holds slides it aborts unless --force is given.
  * Never writes a caption and never marks the post ready: that is the caller's decision.
"""
import argparse, re, struct, sys, zipfile
from datetime import datetime
from pathlib import Path


def dims(data: bytes):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
    return None


def slide_no(name: str) -> int:
    m = re.search(r"slide-(\d+)", name, re.I) or re.search(r"(\d+)(?=\.\w+$)", name)
    return int(m.group(1)) if m else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--num", type=int, required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--month", default=datetime.now().strftime("%B %Y"))
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[4]))
    ap.add_argument("--lang", default="EN")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    title = re.sub(r"[\\/:*?\"<>|]+", "", a.title).strip()
    idea_dir = Path(a.repo) / "public" / "Instagram Briefings" / f"Designs {a.month}" / f"Idea {a.num:02d} - {title}"
    out = idea_dir / a.lang.upper()
    if out.is_dir() and any(out.glob("slide-*")) and not a.force:
        sys.exit(f"Already organized: {out} (use --force to overwrite)")

    z = zipfile.ZipFile(a.zip)
    members = [i for i in z.infolist() if i.filename.lower().endswith((".png", ".jpg", ".jpeg")) and not i.filename.startswith("__MACOSX")]
    members.sort(key=lambda i: slide_no(i.filename))
    if not 2 <= len(members) <= 20:
        sys.exit(f"Expected 2 to 20 slides, found {len(members)}")
    nos = [slide_no(i.filename) for i in members]
    if nos != list(range(1, len(members) + 1)):
        sys.exit(f"Slide numbers are not 1..N in order: {nos}")

    out.mkdir(parents=True, exist_ok=True)
    for i, m in enumerate(members, start=1):
        data = z.read(m)
        d = dims(data)
        if d != (1080, 1350):
            sys.exit(f"Slide {i} is {d}, expected 1080x1350")
        ext = Path(m.filename).suffix.lower().replace(".jpeg", ".jpg")
        (out / f"slide-{i:02d}{ext}").write_bytes(data)
    print(f"OK {len(members)} slides -> {out}")


if __name__ == "__main__":
    main()
