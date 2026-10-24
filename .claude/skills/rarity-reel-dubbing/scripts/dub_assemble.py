#!/usr/bin/env python3
"""
dub_assemble.py — fit a dubbed voice (one wav per sentence) onto the original cut WITHOUT rushing it.

Translated speech is rarely the same length as the original (English from Portuguese ran 10-30 %
longer here, and a cloned voice speaks slower than the source speaker). Squeezing the audio to fit
the old timing sounds robotic, so — like a professional dub — we share the difference:

  per sentence i:  original window P_i (start_i -> start_{i+1}),  dubbed audio length L_i,  gap g
      video time-warp factor f_i = clamp((L_i + g)/P_i, 0.90, 1.15)      (slow-mo / speed-up of THAT sentence's
                                                                           video by at most 15 %, unnoticeable)
      audio speed          a_i = L_i / (f_i*P_i - g)   (kept <= 1.12; if more is needed, SHORTEN THE TEXT)
  video segments are re-timed (minterpolate for smooth motion), audio segments are placed back to back.

Inputs  (all in --dir):
  native_cut.mp4      the cut video at NATIVE resolution (run the lip-sync on native res, upscale later)
  pt_sents.json       [{start,end,...}] sentence windows on native_cut's timeline
  en_00.wav ...       dubbed audio per sentence (any sample rate)
Outputs:
  native_warped.mp4   time-warped video (silent)
  dub_voice.wav       the assembled dub track (44.1 kHz mono), same length as native_warped
  dub_timeline.json   [{i, start, end, audio_start, audio_end, speed, warp}] on the NEW timeline
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf


def run(cmd):
    subprocess.run([str(c) for c in cmd], check=True, stderr=subprocess.DEVNULL)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--gap", type=float, default=0.12)
    ap.add_argument("--max-audio-speed", type=float, default=1.12)
    ap.add_argument("--warp-min", type=float, default=0.90)
    ap.add_argument("--warp-max", type=float, default=1.15)
    ap.add_argument("--fps", type=int, default=30)
    args = ap.parse_args()
    d = Path(args.dir)
    sents = json.loads((d / "pt_sents.json").read_text())
    cut_info = json.loads((d / "cut.json").read_text())
    total_in = cut_info["total"]
    n = len(sents)
    SR = 44100

    plan, t_new = [], 0.0
    pieces = []
    for i, s in enumerate(sents):
        w_start = s["start"]
        w_end = sents[i + 1]["start"] if i + 1 < n else total_in
        P = w_end - w_start
        wav, sr = sf.read(d / f"en_{i:02d}.wav")
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        L = len(wav) / sr
        g = args.gap if i + 1 < n else 0.3
        f = min(args.warp_max, max(args.warp_min, (L + g) / P))
        N = P * f
        a = max(1.0, L / max(0.2, N - g))
        warn = ""
        if a > args.max_audio_speed:
            warn = f"  !! needs {a:.2f}x audio — shorten this sentence's text"
        plan.append(dict(i=i, src_start=w_start, src_end=w_end, P=P, L=L, f=f, N=N, a=a, start=t_new, end=t_new + N))
        print(f"[{i:2d}] window {P:5.2f}s  dub {L:5.2f}s  video x{f:4.2f}  audio x{a:4.2f}  -> {N:5.2f}s{warn}")
        t_new += N
        pieces.append((wav, sr, a, N))

    # --- video: per sentence trim + retime, concat
    parts = []
    for p in plan:
        i = p["i"]
        parts.append(f"[0:v]trim=start={p['src_start']:.3f}:end={p['src_end']:.3f},setpts=PTS-STARTPTS,"
                     f"setpts={p['f']:.4f}*PTS,minterpolate=fps={args.fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
                     f"trim=duration={p['N']:.3f},setpts=PTS-STARTPTS[v{i}]")
    cat = "".join(f"[v{p['i']}]" for p in plan)
    parts.append(f"{cat}concat=n={n}:v=1:a=0[out]")
    (d / "warp_filter.txt").write_text(";".join(parts))
    run(["ffmpeg", "-y", "-i", d / "native_cut.mp4", "-/filter_complex", d / "warp_filter.txt", "-map", "[out]",
         "-r", args.fps, "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", d / "native_warped.mp4"])

    # --- audio: speed-adjust (atempo via ffmpeg for pitch-preserving) and place back to back
    track = []
    for (wav, sr, a, N), p in zip(pieces, plan):
        tmp_in, tmp_out = d / "_a_in.wav", d / "_a_out.wav"
        sf.write(tmp_in, wav, sr)
        run(["ffmpeg", "-y", "-i", tmp_in, "-ar", SR, "-ac", 1, "-af", f"atempo={a:.4f}", tmp_out])
        seg, _ = sf.read(tmp_out)
        n_samp = int(round(p["N"] * SR))
        buf = np.zeros(n_samp, dtype=np.float32)
        buf[:min(len(seg), n_samp)] = seg[:n_samp]
        p["audio_len"] = len(seg) / SR
        track.append(buf)
    audio = np.concatenate(track)
    sf.write(d / "dub_voice.wav", audio, SR)
    for p in plan:
        p["audio_end"] = p["start"] + p["audio_len"]
    (d / "dub_timeline.json").write_text(json.dumps(plan, indent=1))
    print(f"[assemble] {total_in:.2f}s original -> {t_new:.2f}s dubbed timeline")


if __name__ == "__main__":
    main()
