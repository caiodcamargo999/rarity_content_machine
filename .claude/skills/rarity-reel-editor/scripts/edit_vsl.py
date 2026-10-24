#!/usr/bin/env python3
"""
edit_vsl.py — Workflow D: a LANDSCAPE (1920x1080) talking-head VSL / ad -> tight cuts, punch-ins and
DYNAMIC word-by-word captions (dynamic_captions.py), mastered voice, thin brand progress bar.

  python3 edit_vsl.py raw.mp4 words.json out.mp4 [--keep-temp]

words.json  [{text,start,end}] in the ORIGINAL clock; text = the CORRECTED script (align_words.align).
            Words that were stuttered / retaken are simply NOT in the list, so the cut drops them.
Look        no colour treatment (house rule for recorded footage); alternating 1.00 / 1.09 punch-ins on
            clause boundaries (>= --punch-every s apart) so the frame changes every few seconds.
Cuts        keeps [start-pre, end+post] around each word; pauses collapse to ~0.2 s, sentence ends keep 0.30 s.
Audio       afftdn + voice chain (bvr.mix_audio, no music unless --music) -> -14 LUFS.
"""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPT_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


edit_reel = _load("edit_reel")
bvr = _load("build_voiceover_reel")
dyn = _load("dynamic_captions")
W, H = dyn.W, dyn.H


def keep_segments(words, duration, pre, post, post_sentence):
    segs = []
    for w in words:
        end_sentence = w["text"].rstrip()[-1:] in ".?!"
        s = max(0.0, w["start"] - pre)
        e = min(duration, w["end"] + (post_sentence if end_sentence else post))
        if segs and s <= segs[-1][1] + 1e-3:
            segs[-1][1] = max(segs[-1][1], e)
        else:
            segs.append([s, e])
    return [tuple(s) for s in segs]


def make_remap(segs):
    table, out = [], 0.0
    for s, e in segs:
        table.append((s, e, out))
        out += e - s

    def remap(t):
        for s, e, o in table:
            if t < s:
                return o
            if t <= e:
                return o + (t - s)
        return out
    return remap, out


def build_bar(total, path, fps, ffmpeg):
    import numpy as np
    bar_h, n = 8, int(round(total * fps))
    proc = subprocess.Popen([ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{bar_h}", "-r", str(fps),
                             "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", str(path)],
                            stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    base = np.zeros((bar_h, W, 4), dtype=np.uint8)
    base[:, :] = (239, 238, 234, 50)
    for f in range(n):
        fr = base.copy()
        fx = int(W * min(1.0, f / max(1, n - 1)))
        fr[:, :fx] = (213, 0, 87, 245)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    proc.wait()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("words")
    ap.add_argument("output")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--pre", type=float, default=0.05)
    ap.add_argument("--post", type=float, default=0.13)
    ap.add_argument("--post-sentence", type=float, default=0.30)
    ap.add_argument("--punch", type=float, default=0.09)
    ap.add_argument("--punch-every", type=float, default=3.4)
    ap.add_argument("--music", default=None)
    ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--music-lufs", type=float, default=-21.0)
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--keep-temp", action="store_true")
    ap.add_argument("--cut-only", action="store_true",
                    help="stop after the cut: writes WORKDIR/base.mp4 + voice.wav and <out>.remapped.json for finish_vsl.py")
    ap.add_argument("--workdir", default=None, help="keep the work files here (required with --cut-only)")
    ap.add_argument("--format", default="auto", choices=["auto", "landscape", "vertical"],
                    help="output size: landscape 1920x1080 (VSL) / vertical 1080x1920 (Reel, ad); auto = from the source")
    args = ap.parse_args()

    video = str(Path(args.video).resolve())
    words = json.loads(Path(args.words).read_text())
    info = edit_reel.ffprobe_json(video)
    duration = float(info["format"]["duration"])
    vs = next(x for x in info["streams"] if x["codec_type"] == "video")
    sw, sh = int(vs["width"]), int(vs["height"])
    fmt = args.format if args.format != "auto" else ("vertical" if sh > sw else "landscape")
    global W, H
    W, H = (1080, 1920) if fmt == "vertical" else (1920, 1080)
    fit = ""
    if (sw, sh) != (W, H):       # fill the frame (cover + centre crop); low-res phone exports get denoise + light sharpen
        fit = (("hqdn3d=3:2:4:3," if sw < W else "") +
               f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}" +
               (",unsharp=5:5:0.5" if sw < W else "") + ",")
    segs = keep_segments(words, duration, args.pre, args.post, args.post_sentence)
    remap, total = make_remap(segs)
    print(f"[cut] {len(segs)} segments, {duration:.2f}s -> {total:.2f}s")

    if args.workdir:
        tmp = Path(args.workdir).resolve()
        tmp.mkdir(parents=True, exist_ok=True)
    else:
        tmp = Path(tempfile.mkdtemp(prefix="rarity_vsl_"))
    print(f"[workdir] {tmp}")
    try:
        # punch-in shots: split kept segments at clause ends
        vsegs, zi = [], 0
        for (s, e) in segs:
            cuts, last = [s], s
            for w in words:
                if w["end"] <= s + 0.5 or w["end"] >= e - 0.5:
                    continue
                if w["text"].rstrip()[-1:] in ".,;:?!" and w["end"] - last >= args.punch_every:
                    cuts.append(w["end"] + args.post * 0.5)
                    last = cuts[-1]
            cuts.append(e)
            for a_, b_ in zip(cuts, cuts[1:]):
                vsegs.append((a_, b_, 1.0 + (args.punch if zi % 2 else 0.0)))
                zi += 1
        parts = []
        for i, (s, e, z) in enumerate(vsegs):
            zf = ""
            if z > 1.0:
                zw, zh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
                zf = f",scale={zw}:{zh}:flags=lanczos,crop={W}:{H}:{int(W * 0.5 * (z - 1))}:{int(H * 0.40 * (z - 1))}"
            parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS,{fit}null{zf},setsar=1[v{i}]")
        for i, (s, e) in enumerate(segs):
            fd = 0.006
            parts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                         f"afade=t=in:d={fd},afade=t=out:st={max(0.0, e - s - fd):.3f}:d={fd}[a{i}]")
        parts.append("".join(f"[v{i}]" for i in range(len(vsegs))) + f"concat=n={len(vsegs)}:v=1:a=0[cv]")
        parts.append("".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[ca]")
        parts.append(f"[cv]fps={args.fps}[vout]")
        parts.append("[ca]afftdn=nr=10:nf=-38[aout]")
        print(f"[cut] {len(vsegs)} shots ({len(vsegs) - len(segs)} punch-in cuts)")
        base, voice = tmp / "base.mp4", tmp / "voice.wav"
        fc = tmp / "fc.txt"
        fc.write_text(";\n".join(parts))
        edit_reel.run(["ffmpeg", "-y", "-i", video, "-/filter_complex", str(fc),
                       "-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p",
                       "-r", str(args.fps), str(base), "-map", "[aout]", "-ar", "44100", "-ac", "1", str(voice)])

        w2 = [{**w, "start": remap(w["start"]), "end": max(remap(w["end"]), remap(w["start"]) + 0.05)} for w in words]
        if args.cut_only:
            json.dump({"words": w2, "total": total}, open(Path(args.output).resolve().with_suffix(".remapped.json"), "w"), indent=1)
            print(f"[cut-only] {fmt} {W}x{H} {total:.2f}s -> {tmp} (base.mp4, voice.wav) + remapped.json")
            args.keep_temp = True
            return
        mixed = tmp / "mix.wav"
        bvr.mix_audio(voice, mixed, total, tmp, music=args.music, music_start=args.music_start,
                      music_lufs=args.music_lufs, sfx_events=[], voice_fx=True)

        caps = tmp / "caps"
        caps.mkdir()
        frames = dyn.build_frames(w2, caps)
        print(f"[captions] {len(frames)} images")
        cap_track = dyn.build_track(frames, total, caps, args.fps, ffmpeg=edit_reel.FFMPEG)
        bar = tmp / "bar.mov"
        build_bar(total, bar, args.fps, edit_reel.FFMPEG)

        out = Path(args.output).resolve()
        chain = (f"[0:v][2:v]overlay=0:{dyn.BAND_Y0}[a];[4:v]scale=72:-1[sym];[a][sym]overlay=W-w-44:34[b];"
                 f"[b][3:v]overlay=0:H-h[outv]")
        edit_reel.run(["ffmpeg", "-y", "-i", base, "-i", mixed, "-i", cap_track, "-i", bar, "-i", edit_reel.SYMBOL,
                       "-filter_complex", chain, "-map", "[outv]", "-map", "1:a",
                       "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-maxrate", "16M", "-bufsize", "32M",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
                       "-shortest", str(out)])
        json.dump({"words": w2, "total": total}, open(out.with_suffix(".remapped.json"), "w"), indent=1)
        print(f"[done] -> {out} ({total:.2f}s)")
    finally:
        if args.keep_temp:
            print(f"[keep-temp] {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
