#!/usr/bin/env python3
"""fetch_music.py — download the curated royalty-free tracks (Mixkit Stock Music Free License) into ../music/.

The mp3 files are NOT committed (the repo is public and the licence forbids redistributing raw tracks);
run this once on a new machine:  python3 fetch_music.py
Ids/names are the ones documented in ../music/README.md.
"""
import urllib.request
from pathlib import Path

TRACKS = {  # id -> local filename
    167: "brainiac-167.mp3",
    440: "infinity-440.mp3",
    34: "raising-me-higher-034.mp3",
    623: "deep-urban-623.mp3",
    196: "deep-house-196.mp3",
}
out = Path(__file__).resolve().parent.parent / "music"
out.mkdir(exist_ok=True)
for i, name in TRACKS.items():
    dst = out / name
    if dst.exists():
        print("have", name)
        continue
    req = urllib.request.Request(f"https://assets.mixkit.co/music/{i}/{i}.mp3", headers={"User-Agent": "Mozilla/5.0"})
    dst.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    print("downloaded", name)
