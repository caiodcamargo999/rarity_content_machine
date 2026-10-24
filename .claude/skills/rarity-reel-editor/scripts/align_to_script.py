#!/usr/bin/env python3
"""
align_to_script.py — step 2: relabel whisper TIMES with the CORRECTED script so captions have zero typos, and print
every place where script and audio disagree (that list is what Caio must confirm).

  python3 align_to_script.py script.txt words_L.json words.json [--drop 101.40-105.34 --drop ...]

--drop START-END   removes heard words in that window (a retake / stutter you left out of the script) so the cut drops it.
Words the script has but whisper did not hear are interpolated (check them: they are the "you"/"at" style doubts).
Also prints pauses > 0.45 s (cut points) and fixes overlaps between neighbouring words.
"""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location("align_words", Path(__file__).resolve().parent / "align_words.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("heard")
    ap.add_argument("out")
    ap.add_argument("--drop", action="append", default=[])
    args = ap.parse_args()
    heard = json.loads(Path(args.heard).read_text())
    for d in args.drop:
        a, b = (float(x) for x in d.split("-"))
        heard = [w for w in heard if not (a <= w["start"] < b)]
    tok = Path(args.script).read_text().split()
    words = A.align(tok, heard)
    for i in range(1, len(words)):
        if words[i]["start"] < words[i - 1]["end"]:
            m = (words[i]["start"] + words[i - 1]["end"]) / 2
            words[i - 1]["end"] = words[i]["start"] = round(m, 3)
    Path(args.out).write_text(json.dumps(words, indent=1))
    sm = difflib.SequenceMatcher(a=[A.norm(t) for t in tok], b=[A.norm(h["text"]) for h in heard], autojunk=False)
    print("script vs heard (confirm these with Caio):")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            print(f"  {tag:8s} SCRIPT: {' '.join(tok[i1:i2])!r:40s} HEARD: {' '.join(h['text'] for h in heard[j1:j2])!r} @ {heard[j1]['start']:.1f}s" if j1 < len(heard) else f"  {tag} {tok[i1:i2]}")
    gaps = [(round(words[i]["end"], 2), round(words[i + 1]["start"] - words[i]["end"], 2)) for i in range(len(words) - 1)
            if words[i + 1]["start"] - words[i]["end"] > 0.45]
    print(f"{len(tok)} script words -> {len(words)} timed; pauses > 0.45 s: {gaps}")


if __name__ == "__main__":
    main()
