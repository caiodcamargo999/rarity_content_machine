#!/usr/bin/env python3
"""
edit_talking_head.py — Workflow C: a recorded talking-head clip -> finished Reel with CUTS,
minimal captions, SPEECH-SYNCED MOTION GRAPHICS, music bed and SFX. Language-agnostic
(built for Rarity BR in Portuguese; also works for EN/ES).

  python3 edit_talking_head.py video.mp4 words.json beats.json out.mp4 \
        [--music ../music/brainiac-167.mp3 --music-start 6] [--keep-temp]

Inputs
  words.json   [{text,start,end}] in the ORIGINAL video's clock, text = the CORRECTED transcript
               (see "Transcript rule" below). Produce with whisper large-v3 + align_words.py.
  beats.json   motion-graphic beats (see motion_graphics.py): [{type,start,end,anchors,params}],
               also in ORIGINAL time; they are remapped through the cuts automatically.

What it does
  1. CUT: keeps [word.start-0.06, word.end+0.10] around every word and drops the rest, so any
     pause longer than ~0.16 s collapses to 0.16 s (breaths and "ums" between sentences go);
     joints get 6 ms audio fades. Head/tail silence is trimmed.
  2. LOOK: denoise at native res -> lanczos upscale to 1080x1920 -> light sharpen -> fine grain (hides
     the softness of low-res sources such as a 480x848 phone export). NO colour treatment by default —
     the footage keeps its original colours; pass --grade only if asked.
  3. AUDIO: gentle denoise, voice mastering chain, optional music bed ducked by the voice, soft
     "pop" SFX on every motion card and ticks on checklist rows, final -14 LUFS.
  4. CAPTIONS: minimal house style (BentonSans phrase + Playfair-italic magenta key word) at
     y = --caption-y (default 1480, BELOW the motion-graphics strip so they never collide).
  5. MOTION GRAPHICS: compact lower-third strips at y = 1120..1410 (below the speaker's chin even
     in his zoomed-in shots), timed to the words they illustrate.

Transcript rule (captions must have ZERO errors)
  Whisper mishears jargon (ROAS -> "hoas", CAC -> "cá que", call -> "Macau", Klaviyo -> "clevel").
  Always: transcribe with large-v3 + a glossary --initial_prompt, read the result critically,
  rewrite wrong terms, and align the corrected text with align_words.align(). Tell Caio which
  words were corrected from what, so he can confirm against the audio.
"""
import argparse
import importlib.util
import json
import shutil
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
mg = _load("motion_graphics")
ag = _load("ad_graphics")
bvr = _load("build_voiceover_reel")

OUT_W, OUT_H = edit_reel.OUT_W, edit_reel.OUT_H


def keep_segments(words, duration, pre=0.06, post=0.10):
    """[(src_start, src_end)] merged windows around the words."""
    segs = []
    for w in words:
        s, e = max(0.0, w["start"] - pre), min(duration, w["end"] + post)
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
                return o            # inside a removed gap -> snap to the next kept moment
            if t <= e:
                return o + (t - s)
        return out
    return remap, out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("words")
    ap.add_argument("beats")
    ap.add_argument("output")
    ap.add_argument("--music", default=None)
    ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--music-lufs", type=float, default=-29.0)
    ap.add_argument("--caption-y", type=int, default=1480)
    ap.add_argument("--accent", default=edit_reel.DEFAULT_ACCENT)
    ap.add_argument("--no-sfx", action="store_true")
    ap.add_argument("--grade", action="store_true",
                    help="apply colour matching + the Rarity look. OFF by default: talking-head footage keeps its\n                    original colours (Caio, 2026-10: \"não precisava ter tratado cor\")")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--pre", type=float, default=0.06, help="seconds kept before each word (tighter = punchier)")
    ap.add_argument("--post", type=float, default=0.10, help="seconds kept after each word")
    ap.add_argument("--punch", type=float, default=0.0,
                    help="alternate punch-in zoom (e.g. 0.06 = 6 %%) applied to every other shot so jump cuts feel intentional")
    ap.add_argument("--punch-every", type=float, default=4.5,
                    help="with --punch: also add a punch-in cut at the next clause boundary after this many seconds")
    ap.add_argument("--no-progress", action="store_true", help="hide the thin brand progress bar (default: shown, ref 1/2)")
    ap.add_argument("--precut", action="store_true",
                    help="input video/words/beats are ALREADY on the final timeline (no cutting/remapping) — used for dubs")
    ap.add_argument("--voice", default=None,
                    help="external voice track (wav) to use instead of the video's own audio (dubs: the video is silent)")
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    edit_reel.MIN_BASELINE_Y = args.caption_y
    video = str(Path(args.video).resolve())
    words = json.loads(Path(args.words).read_text())
    beats = json.loads(Path(args.beats).read_text())
    probe = edit_reel.ffprobe_json(video)
    duration = float(probe["format"]["duration"])

    if args.precut:
        segs = [(0.0, duration)]
        remap, total = (lambda t: t), duration
    else:
        segs = keep_segments(words, duration, args.pre, args.post)
        remap, total = make_remap(segs)
    print(f"[cut] {len(segs)} kept segments, {duration:.2f}s -> {total:.2f}s (removed {duration - total:.2f}s)")

    tmp = Path(tempfile.mkdtemp(prefix="rarity_th_"))
    print(f"[workdir] {tmp}")
    try:
        # ---- 1+2+3a: cut, look, voice -------------------------------------------------------
        grade = ""
        if args.grade:
            meas = bvr.measure_clip_rgb(video, "video", 0.0, duration)
            grade = "," + bvr.color_match_filter(meas)
            print(f"[look] mean RGB {[round(v, 2) for v in meas[:3]]}, sat {meas[3]:.2f}")
        parts, vl, al = [], [], []
        # video parts = kept segments, optionally subdivided at clause boundaries (extra punch-in cuts)
        vsegs = []   # (src_start, src_end, zoom)
        zi = 0
        for (s, e) in segs:
            cuts = [s]
            if args.punch > 0:
                last = s
                for w in words:
                    if w["end"] <= s + 0.3 or w["end"] >= e - 0.3:
                        continue
                    if w["text"].rstrip()[-1:] in ".,;:?!" and w["end"] - last >= args.punch_every:
                        cuts.append(w["end"] + args.post * 0.5)
                        last = w["end"]
            cuts.append(e)
            for a_, b_ in zip(cuts, cuts[1:]):
                vsegs.append((a_, b_, 1.0 + (args.punch if zi % 2 else 0.0)))
                zi += 1
        src_w = next((st.get("width") for st in probe.get("streams", []) if st.get("width")), OUT_W)
        src_h = next((st.get("height") for st in probe.get("streams", []) if st.get("height")), OUT_H)
        for i, (s, e, z) in enumerate(vsegs):
            zf = ""
            if z > 1.0:
                zw, zh = int(src_w * z) // 2 * 2, int(src_h * z) // 2 * 2
                zf = (f",scale={zw}:{zh}:flags=lanczos,"
                      f"crop={src_w}:{src_h}:{int(src_w * 0.5 * (z - 1))}:{int(src_h * 0.42 * (z - 1))}")
            parts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS{zf}[v{i}]")
        for i, (s, e) in enumerate(segs):
            fd = 0.006
            asrc = "[1:a]" if args.voice else "[0:a]"
            parts.append(f"{asrc}atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                         f"afade=t=in:d={fd},afade=t=out:st={max(0.0, e - s - fd):.3f}:d={fd}[a{i}]")
        parts.append("".join(f"[v{i}]" for i in range(len(vsegs))) + f"concat=n={len(vsegs)}:v=1:a=0[cv]")
        parts.append("".join(f"[a{i}]" for i in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1[ca]")
        print(f"[cut] {len(vsegs)} video shots ({len(vsegs) - len(segs)} extra punch-in cuts)")
        hi_res = any((st.get("width") or 0) >= OUT_W for st in probe.get("streams", []))
        if hi_res:   # already 1080 wide: don't denoise/sharpen/grain a clean source
            parts.append(f"[cv]fps={args.fps},scale={OUT_W}:{OUT_H}:flags=lanczos{grade}[vout]")
        else:
            parts.append(
                f"[cv]fps={args.fps},hqdn3d=1.6:1.6:4:4,scale={OUT_W}:{OUT_H}:flags=lanczos,unsharp=5:5:0.9:5:5:0.0"
                f"{grade},noise=alls=5:allf=t[vout]")
        parts.append("[ca]afftdn=nr=10:nf=-38[aout]")
        base = tmp / "base.mp4"
        voice = tmp / "voice.wav"
        in_args = ["-i", video] + (["-i", str(Path(args.voice).resolve())] if args.voice else [])
        edit_reel.run(["ffmpeg", "-y", *in_args, "-filter_complex", ";".join(parts),
                       "-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                       "-r", str(args.fps), str(base),
                       "-map", "[aout]", "-ar", "44100", "-ac", "1", str(voice)])

        # ---- remap words + beats ---------------------------------------------------------
        w2 = [{**w, "start": remap(w["start"]), "end": max(remap(w["end"]), remap(w["start"]) + 0.05)} for w in words]
        b2, sfx = [], []
        for b in beats:
            nb = dict(b)
            nb["start"], nb["end"] = remap(b["start"]), remap(b["end"])
            nb["anchors"] = {k: remap(v) for k, v in b.get("anchors", {}).items()}
            b2.append(nb)
            sfx.append((nb["start"] + 0.02, "pop", -23))
            if b["type"] == "checklist":
                for k, v in nb["anchors"].items():
                    if k.startswith("r") and v > nb["start"] + 0.1:
                        sfx.append((v + 0.02, "pop", -25))
        # ---- 3b: mix --------------------------------------------------------------------
        mixed = tmp / "mix.wav"
        bvr.mix_audio(voice, mixed, total, tmp, music=args.music, music_start=args.music_start,
                      music_lufs=args.music_lufs, sfx_events=[] if args.no_sfx else sfx, voice_fx=True)

        # ---- 4: captions ---------------------------------------------------------------
        caps_dir = tmp / "caps"
        caps_dir.mkdir()
        frames = edit_reel.build_caption_frames(w2, edit_reel.FONT_SANS, args.accent, 3, caps_dir, style="minimal")
        print(f"[captions] {len(frames)} images")
        cap_track = edit_reel.build_caption_track(frames, total, caps_dir, args.fps)

        # ---- 5: motion graphics --------------------------------------------------------
        mg_track = tmp / "mg.mov"
        lower = [b for b in b2 if b.get("zone", "lower") != "top"]
        top = [b for b in b2 if b.get("zone") == "top"]
        mg.build_track(lower, total, mg_track, args.fps, ffmpeg=edit_reel.FFMPEG)
        top_track = None
        if top:
            top_track = tmp / "mg_top.mov"
            mg.build_track(top, total, top_track, args.fps, ffmpeg=edit_reel.FFMPEG, h=ag.TOP_H, registry=ag.TOP_BEATS)

        # ---- final composite -------------------------------------------------------------
        out = Path(args.output).resolve()
        inputs = ["-i", base, "-i", mixed, "-i", cap_track, "-i", mg_track]
        chain = f"[0:v][2:v]overlay=0:0[a];[a][3:v]overlay=0:{mg.ZONE_Y0}[b]"
        last, nxt = "b", 5
        if top_track:
            inputs += ["-i", top_track]
            chain += f";[{last}][{nxt - 1}:v]overlay=0:{ag.TOP_Y0}[t]"
            last, nxt = "t", nxt + 1
        inputs += ["-i", edit_reel.SYMBOL]
        sym = nxt - 1
        chain += f";[{sym}:v]scale=64:-1[sym];[{last}][sym]overlay=W-w-40:40[c]"
        last = "c"
        if not args.no_progress:
            # thin brand progress bar (refs 1+2) as its own track: dim track + growing magenta fill
            prog = tmp / "progress.mov"
            ag.build_progress_track(total, prog, args.fps, ffmpeg=edit_reel.FFMPEG)
            inputs += ["-i", prog]
            chain += f";[{last}][{nxt}:v]overlay=0:101[outv]"
        else:
            chain += f";[{last}]null[outv]"
        edit_reel.run(["ffmpeg", "-y", *inputs, "-filter_complex", chain, "-map", "[outv]", "-map", "1:a",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "14M", "-bufsize", "28M",
                       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart",
                       "-shortest", str(out)])
        json.dump({"words": w2, "beats": b2, "total": total}, open(tmp / "remapped.json", "w"), indent=1)
        shutil.copy(tmp / "remapped.json", out.with_suffix(".remapped.json"))
        print(f"[done] -> {out} ({total:.2f}s)")
    finally:
        if args.keep_temp:
            print(f"[keep-temp] {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
