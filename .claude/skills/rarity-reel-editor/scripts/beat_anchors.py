#!/usr/bin/env python3
"""
beat_anchors.py — place motion-graphic beats by PHRASE instead of by hand-typed seconds.

    from beat_anchors import Words
    W = Words("words_fix02.json")            # [{text,start,end}] from align_words.py (script-exact text)
    t0 = W.find("something called")          # start of the first word of that phrase
    t1 = W.find("still make money", end=True)  # end of its last word
    t2 = W.find("growth audit", nth=2, end=True)

Matching ignores case and punctuation ("$55," == "55", "P&L" == "pl", "45-minute" == "45minute"), and
the phrase must appear as consecutive words. It raises if a phrase is missing, so a typo in the
transcript or the beat list fails loudly instead of putting a card at the wrong moment.

Pattern used for Caio's three ads (see rarity-reel-editor SKILL.md, Workflow C2):
    low("stat", W.find("5 million")-0.4, W.find("on Google", end=True)+0.5, {"s0": W.find("5 million"), ...}, stats=[...])
    top("icon", W.find("platform ROAS")-0.05, 2.2, icon="chart")
Beats: zone "top" = icon / nametag / title (ad_graphics.TOP_BEATS); default zone = lower strip.
Keep lower beats sequential (the helper trims overlaps) and at most one top icon at a time.
"""
import json
import re


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


class Words:
    def __init__(self, path):
        self.w = json.load(open(path))
        self.n = [norm(x["text"]) for x in self.w]

    def find(self, phrase, nth=1, end=False):
        toks = [norm(t) for t in phrase.split()]
        c = 0
        for i in range(len(self.n) - len(toks) + 1):
            if self.n[i:i + len(toks)] == toks:
                c += 1
                if c == nth:
                    j = i + len(toks) - 1
                    return round(self.w[j]["end"] if end else self.w[i]["start"], 2)
        raise KeyError(f"phrase not found: {phrase!r} (nth={nth})")


def trim_overlaps(beats):
    """lower beats and top beats are each kept sequential: a beat ends 0.05 s before the next starts"""
    for zone_top in (False, True):
        seq = sorted([b for b in beats if (b.get("zone") == "top") == zone_top], key=lambda b: b["start"])
        for a, b in zip(seq, seq[1:]):
            if b["start"] < a["end"]:
                a["end"] = b["start"] - 0.05
    return beats
