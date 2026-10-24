#!/usr/bin/env python3
"""
music_bed.py — a long, steady, voice-friendly music bed from deep-house-196.mp3 (157 s) by crossfading its two
steadiest stretches (18-50 s, 80-140 s) until `duration` is covered, with a -4/-3 dB dip at 1 kHz / 2.5 kHz so the
bed leaves the voice's band free (deep house has only ~9 % of its energy at 300-3400 Hz — the lowest of the library).

  python3 music_bed.py 215 bed.wav                       # deep house (legacy default)
  python3 music_bed.py 215 bed.wav --track epical-drums-03-678.mp3   # orchestral/epic (Caio 2026-10: "more orchestral")
  -> then  finish_vsl.py ... --music bed.wav --music-lufs -21 --duck-ratio 3

Any other track: plays once from 0 (so its intro/build lands at the start), then loops its body (12 s .. end-4 s)
with 2 s crossfades until `duration` is covered.
"""
import subprocess
import sys
from pathlib import Path

TRACK = Path(__file__).resolve().parent.parent / "music" / "deep-house-196.mp3"
A, B, XF = (18, 50), (80, 140), 2.0
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"


def main():
    need, out = float(sys.argv[1]), sys.argv[2]
    track = TRACK
    if "--track" in sys.argv:
        track = TRACK.parent / sys.argv[sys.argv.index("--track") + 1]
    segs, total, i = [], 0.0, 0
    if track == TRACK:
        while total < need + 1:
            a, b = (A, B)[i % 2]
            segs.append((a, b))
            total += (b - a) - (XF if i else 0)
            i += 1
    else:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(track)],
                                   capture_output=True, text=True).stdout)
        while total < need + 1:
            a, b = (0, dur - 4) if i == 0 else (12, dur - 4)
            segs.append((a, b))
            total += (b - a) - (XF if i else 0)
            i += 1
    parts = [f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS[s{k}]" for k, (a, b) in enumerate(segs)]
    cur = "s0"
    for k in range(1, len(segs)):
        parts.append(f"[{cur}][s{k}]acrossfade=d={XF}[x{k}]")
        cur = f"x{k}"
    parts.append(f"[{cur}]equalizer=f=1000:t=q:w=0.6:g=-4,equalizer=f=2500:t=q:w=0.8:g=-3[o]")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(track), "-filter_complex", ";".join(parts), "-map", "[o]",
                    "-ar", "44100", out], check=True)
    print(f"[bed] {out} ({total:.0f} s)")


if __name__ == "__main__":
    main()
