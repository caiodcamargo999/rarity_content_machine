#!/usr/bin/env python3
"""
align_words.py — word-level timings for a narration, expressed in the SCRIPT's own words.

Why: captions must have zero errors. Whisper's transcript drifts from the script ("$96" for
"ninety-six billion", "Amazon sale" for "Amazon's sale", "8%" for "eight percent"), so for any
narration we generated from a known script we transcribe only to get TIMES, then re-label every
timing with the script's exact token. Tokens whisper merged/split/mangled are interpolated
between their matched neighbours (proportional to character length).

Usage:
  python3 align_words.py narration.wav narration.txt words.json [--language en] [--model small]

narration.txt  the exact script text that was spoken (newlines = whitespace).
words.json     output: [{"text": "Black", "start": 0.11, "end": 0.29}, ...]  (one per script token)
"""
import argparse
import difflib
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

NUM_WORDS = {  # tiny normaliser so "96" ~ "ninety-six" and "8%" ~ "eight percent" still anchor
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six",
    "7": "seven", "8": "eight", "9": "nine", "10": "ten",
}


def norm(tok):
    t = tok.lower().replace("’", "'")
    t = re.sub(r"[^a-z0-9']+", "", t)
    return NUM_WORDS.get(t, t)


def whisper_words(wav_path, language, model, prompt):
    import importlib.util
    spec = importlib.util.spec_from_file_location("edit_reel", SCRIPT_DIR / "edit_reel.py")
    er = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(er)
    import numpy as np
    from faster_whisper import WhisperModel
    m = WhisperModel(model, device="cpu", compute_type="int8")
    # edit_reel.load_wav_as_float_array needs 16 kHz mono
    tmp = Path(wav_path).with_suffix(".16k.wav")
    er.run(["ffmpeg", "-y", "-i", str(wav_path), "-ac", "1", "-ar", "16000", str(tmp)], quiet=True)
    audio = er.load_wav_as_float_array(tmp)
    segs, _ = m.transcribe(audio, word_timestamps=True, language=language, initial_prompt=prompt)
    out = []
    for s in segs:
        for w in (s.words or []):
            if w.word.strip():
                out.append({"text": w.word.strip(), "start": float(w.start), "end": float(w.end)})
    tmp.unlink(missing_ok=True)
    return out


def align(script_tokens, heard):
    a = [norm(t) for t in script_tokens]
    b = [norm(h["text"]) for h in heard]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    timing = [None] * len(a)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            h = heard[blk.b + k]
            timing[blk.a + k] = (h["start"], h["end"])
    # replace-blocks of equal length: pair them positionally (e.g. "96" vs "ninety-six" is 1:1)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            n_i, n_j = i2 - i1, j2 - j1
            if n_i == n_j:
                for k in range(n_i):
                    h = heard[j1 + k]
                    timing[i1 + k] = (h["start"], h["end"])
            elif n_j > 0:  # spread the heard span proportionally over the script tokens
                t0, t1 = heard[j1]["start"], heard[j2 - 1]["end"]
                lens = [max(1, len(script_tokens[i1 + k])) for k in range(n_i)]
                tot, acc = sum(lens), 0
                for k in range(n_i):
                    timing[i1 + k] = (t0 + (t1 - t0) * acc / tot, t0 + (t1 - t0) * (acc + lens[k]) / tot)
                    acc += lens[k]
    # interpolate any remaining gaps between known neighbours
    known = [i for i, t in enumerate(timing) if t]
    if not known:
        sys.exit("[error] nothing aligned — wrong narration/script pairing?")
    for i in range(len(timing)):
        if timing[i]:
            continue
        lo = max([k for k in known if k < i], default=None)
        hi = min([k for k in known if k > i], default=None)
        t0 = timing[lo][1] if lo is not None else 0.0
        t1 = timing[hi][0] if hi is not None else t0 + 0.3 * (i - (lo or 0))
        run = [k for k in range(len(timing)) if (lo is None or k > lo) and (hi is None or k < hi) and not timing[k]]
        lens = [max(1, len(script_tokens[k])) for k in run]
        tot, acc = sum(lens), 0
        for k, ln in zip(run, lens):
            timing[k] = (t0 + (t1 - t0) * acc / tot, t0 + (t1 - t0) * (acc + ln) / tot)
            acc += ln
    return [{"text": tok, "start": round(s, 3), "end": round(e, 3)} for tok, (s, e) in zip(script_tokens, timing)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("narration")
    ap.add_argument("script_txt")
    ap.add_argument("out_json")
    ap.add_argument("--language", default="en")
    ap.add_argument("--model", default="small")
    args = ap.parse_args()
    text = Path(args.script_txt).read_text()
    tokens = text.split()
    heard = whisper_words(args.narration, args.language, args.model, text.replace("\n", " "))
    words = align(tokens, heard)
    # enforce monotonic, non-overlapping times
    for i in range(1, len(words)):
        if words[i]["start"] < words[i - 1]["end"]:
            mid = (words[i]["start"] + words[i - 1]["end"]) / 2
            words[i - 1]["end"] = words[i]["start"] = round(mid, 3)
    Path(args.out_json).write_text(json.dumps(words, indent=1))
    miss = sum(1 for t in tokens if t)  # informational
    print(f"[align_words] {len(tokens)} script tokens, {len(heard)} heard -> {args.out_json}")


if __name__ == "__main__":
    main()
