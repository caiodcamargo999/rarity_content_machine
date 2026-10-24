#!/usr/bin/env python3
"""
finish_vsl.py — stage 2 of the Rarity talking-head house format (VSL 1920x1080, Reels/ads 1080x1920).

Takes the CUT (edit_vsl.py --cut-only --workdir DIR -> DIR/base.mp4 + DIR/voice.wav + <out>.remapped.json) and adds
MINIMAL lowercase captions, word-synced glass-card B-roll, floating stat/text callouts, white-flash transitions
with whoosh SFX, optional ducked music bed, -14 LUFS.

  python3 finish_vsl.py WORKDIR out.remapped.json out.mp4 --scenes scenes.json [--format auto|landscape|vertical]
         [--music bed.wav --music-lufs -26] [--workers 8] [--only 0,3] [--keep-temp]

scenes.json  {"lead": 1.4 (optional: cards pop in this many s after their sentence starts), "hold": 2.2 (optional: a card ends this many s after its last item, so the speaker comes back), "scenes": [ {name, kind: card|float, start, end, [start_dt,end_dt], [title], items: [...]} ]}
  time spec   a phrase from the corrected transcript ("maximum allowable"), or seconds (number), or "total".
              Scene start phrases are searched after the previous scene's start; item phrases after their scene's start.
              Item "dt" shifts an item's time; items take "y"/"x" as FRACTIONS of the design canvas (+ "yv"/"xv"
              overrides for vertical).
  item types  card:  strike{text,at,strike,size}  big{text,at,size,glow,color}  label{text,at,size,color}
                     chip{text,at,size,hl,icon,sub}  chips{entries:[{at,text,hl}],size,icon}
                     rows{rows:[{at,label,value|count_to,prefix,icon,hl}],w,gap}
                     compare{good,bad,line,at_good,at_bad,at_line}
              float: stat{value,label,at,prefix}  text{small,lines,strike_small}
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from concurrent.futures import ProcessPoolExecutor
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
g = _load("vsl_graphics")
FPS = g.FPS


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()   # PT/ES accents: "máximo" == "maximo"
    return re.sub(r"[^a-z0-9]", "", t)


def make_T(words):
    toks = [norm(w["text"]) for w in words]

    def T(phrase, after=0.0):
        want = [norm(p) for p in phrase.split()]
        for i in range(len(toks) - len(want) + 1):
            if words[i]["start"] >= after - 1e-6 and toks[i:i + len(want)] == want:
                return words[i]["start"]
        raise KeyError(f"phrase not found after {after:.1f}s: {phrase!r}")
    return T


COL = {"white": g.WHITE, "mag": g.MAG, "magenta": g.MAG}


def build_scenes(spec, words, total):
    """scenes.json (+ corrected words) -> [vsl_graphics.Scene]; raises if a phrase is missing from the transcript"""
    T = make_T(words)
    out, cursor = [], 0.0

    def when(v, after, dt=0.0):
        if v == "total":
            return total
        return (v if isinstance(v, (int, float)) else T(v, after)) + dt

    for sd in spec["scenes"]:
        t0p = when(sd["start"], cursor, sd.get("start_dt", 0.0))
        t1 = when(sd["end"], t0p + 0.2, sd.get("end_dt", 0.0))
        cursor = t0p
        lead = sd.get("lead", spec.get("lead", 0.0)) if sd["kind"] == "card" else 0.0
        t0 = t0p + lead            # the speaker stays on screen for `lead` s of the sentence, then the card pops in

        def iw(v, dt=0.0):          # item time: phrase searched from the ORIGINAL start, never before the card exists
            return max(when(v, t0p, dt), t0 + 0.2)
        items = []
        if sd.get("title"):
            items.append(g.label_item(t0 + 0.25, sd["title"], g.W / 2, g.H * sd.get("title_y", 0.14)))
        for it in sd.get("items", []):
            ty = it["type"]
            vert = g.OUT_W < g.OUT_H
            x = g.W * (it.get("xv", it.get("x", 0.5)) if vert else it.get("x", 0.5))
            y = g.H * (it.get("yv", it.get("y", 0.5)) if vert else it.get("y", 0.5))
            at = iw(it["at"], it.get("dt", 0.0)) if "at" in it else t0 + 0.2 + it.get("dt", 0.0)
            if ty == "strike":
                items.append(g.strike_item(at, max(when(it["strike"], t0p), at + 0.35), it["text"], x, y, it.get("size", 330)))
            elif ty == "big":
                glow = g.MAG if it.get("glow") else None
                items.append(g.big_item(at, it["text"], x, y, it.get("size", 150), glow=glow, fill=COL[it.get("color", "white")]))
            elif ty == "label":
                items.append(g.label_item(at, it["text"], x, y, it.get("size", 30), col=COL[it.get("color", "mag")]))
            elif ty == "chip":
                items.append(g.chip_item(at, it["text"], x, y, it.get("size", 46), it.get("hl", False), it.get("icon"), it.get("sub")))
            elif ty == "chips":
                ents = [(iw(e["at"], e.get("dt", 0.0)), e["text"], e.get("hl", False)) for e in it["entries"]]
                items += g.flow_chips(ents, y, it.get("size", 50), max_w=min(1500, g.W - 160), icon=it.get("icon"))
            elif ty == "rows":
                rows = []
                for r in it["rows"]:
                    kw = {k: r[k] for k in ("icon", "count_to", "prefix", "hl") if k in r}
                    rows.append((iw(r["at"], r.get("dt", 0.0)), r["label"], r.get("value"), kw))
                items += g.stack_rows(rows, cy=y, gap=it.get("gap", 24), w=min(it.get("w", 1180), g.W - 120))
            elif ty == "compare":
                tg, tb = when(it["at_good"], t0p), when(it["at_bad"], t0p)
                ci = g.compare_item(at, max(tg, at), max(tb, at), at + 0.15, it["good"], it["bad"], it["line"], cx=x, cy=y)
                ci.t_last = max(tb, at)
                items.append(ci)
            elif ty == "stat":
                items.append(g.float_stat(at, 0, it["value"], it["label"], prefix=it.get("prefix", "$")))
            elif ty == "text":
                items.append(g.float_text(it.get("small"), it["lines"], it.get("strike_small", False)))
            else:
                raise ValueError(f"unknown item type {ty}")
        hold = sd.get("hold", spec.get("hold"))
        if hold and sd["kind"] == "card" and sd["end"] != "total" and items:
            t1 = min(t1, max(getattr(i, 't_last', i.t0) for i in items) + hold)       # hand the screen back to the speaker soon after the last item pops
        out.append(g.Scene(sd["name"], t0, t1, sd["kind"], items, outro=sd.get("outro", True)))
    return out


def render_scene(a):
    idx, scenes_path, words_path, fmt, tmp = a
    g.configure(fmt)
    meta = json.loads(Path(words_path).read_text())
    sc = build_scenes(json.loads(Path(scenes_path).read_text()), meta["words"], meta["total"])[idx]
    n = int(round(sc.dur * FPS))
    out = Path(tmp) / f"scene_{idx:02d}_{sc.name}.{'mp4' if sc.kind == 'card' else 'mov'}"
    w, h = sc.out_size()
    if sc.kind == "card":
        enc, pix = ["-c:v", "libx264", "-preset", "fast", "-crf", "14", "-pix_fmt", "yuv420p"], "rgb24"
    else:
        enc, pix = ["-c:v", "qtrle", "-pix_fmt", "argb"], "rgba"
    proc = subprocess.Popen([edit_reel.FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", pix, "-s", f"{w}x{h}", "-r", str(FPS),
                             "-i", "-", *enc, str(out)], stdin=subprocess.PIPE)
    for f in range(n):
        proc.stdin.write(sc.frame_out(f / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    return idx, sc.name, sc.kind, sc.t0, sc.t1, str(out)


def probe_dims(path):
    j = edit_reel.ffprobe_json(str(path))
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return int(v["width"]), int(v["height"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("workdir")
    ap.add_argument("remapped")
    ap.add_argument("output")
    ap.add_argument("--scenes", required=True)
    ap.add_argument("--format", default="auto", choices=["auto", "landscape", "vertical"])
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--only", default=None, help="render only these scene indexes (comma list) — preview")
    ap.add_argument("--music", default=None)
    ap.add_argument("--music-lufs", type=float, default=-26.0)
    ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--duck-ratio", type=float, default=3.0, help="how hard the voice ducks the music (9 = old deep-house bed, 3 = audible orchestral bed)")
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    work = Path(args.workdir)
    bw, bh = probe_dims(work / "base.mp4")
    fmt = args.format if args.format != "auto" else ("vertical" if bh > bw else "landscape")
    geo = g.configure(fmt)
    OW, OH = geo["W"], geo["H"]
    meta = json.loads(Path(args.remapped).read_text())
    words, total = meta["words"], meta["total"]
    spec = json.loads(Path(args.scenes).read_text())
    scenes = build_scenes(spec, words, total)
    print(f"[{fmt}] {len(scenes)} scenes ({sum(s.dur for s in scenes if s.kind == 'card'):.1f}s cards, "
          f"{sum(s.dur for s in scenes if s.kind == 'float'):.1f}s floats) of {total:.1f}s")
    tmp = Path(args.output).resolve().parent / ".finish_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir()
    idxs = [int(i) for i in args.only.split(",")] if args.only else list(range(len(scenes)))
    with ProcessPoolExecutor(args.workers) as ex:
        res = sorted(ex.map(render_scene, [(i, str(Path(args.scenes).resolve()), str(Path(args.remapped).resolve()), fmt, str(tmp)) for i in idxs]))
    for r in res:
        print("[scene]", r[:5])

    caps = tmp / "caps"
    caps.mkdir()
    frames = g.minimal_captions(words, caps)
    dyn.W, dyn.BAND_H, dyn.BAND_Y0 = OW, g.CAP["band_h"], g.CAP["band_y0"]
    cap_track = dyn.build_track(frames, total, caps, FPS, ffmpeg=edit_reel.FFMPEG)
    print(f"[captions] {len(frames)} images")

    sfx = [(max(0.0, t0 - 0.12), "whoosh" if kind == "card" else "soft", -19 if kind == "card" else -26) for _, _, kind, t0, t1, _ in res]
    mixed = tmp / "mix.wav"
    bvr.mix_audio(work / "voice.wav", mixed, total, tmp, music=args.music, music_start=args.music_start,
                  music_lufs=args.music_lufs, sfx_events=sfx, voice_fx=True, duck_ratio=args.duck_ratio)

    inputs = ["-i", str(work / "base.mp4"), "-i", str(mixed), "-i", str(cap_track), "-i", edit_reel.SYMBOL]
    parts, cur, k = [], "0:v", 4
    for _, name, kind, t0, t1, path in res:
        inputs += ["-i", path]
        x, y = (0, 0) if kind == "card" else (g.FX, g.FY)
        parts.append(f"[{k}:v]setpts=PTS+{t0:.3f}/TB[s{k}]")
        parts.append(f"[{cur}][s{k}]overlay={x}:{y}:eof_action=pass:enable='between(t,{t0:.3f},{t1:.3f})'[o{k}]")
        cur = f"o{k}"
        if kind == "card":
            if t0 > 0.2:
                parts.append(f"color=c=white:s={OW}x{OH}:r={FPS}:d=0.12,format=rgba,fade=t=in:st=0:d=0.12:alpha=1,setpts=PTS+{t0 - 0.12:.3f}/TB[pf{k}]")
                parts.append(f"[{cur}][pf{k}]overlay=0:0:eof_action=pass[p{k}]")
                cur = f"p{k}"
            if t1 < total - 0.2:
                parts.append(f"color=c=white:s={OW}x{OH}:r={FPS}:d=0.18,format=rgba,fade=t=out:st=0:d=0.18:alpha=1,setpts=PTS+{t1:.3f}/TB[xf{k}]")
                parts.append(f"[{cur}][xf{k}]overlay=0:0:eof_action=pass[x{k}]")
                cur = f"x{k}"
        k += 1
    sym = 72 if fmt == "landscape" else 64
    parts.append(f"[{cur}][2:v]overlay=0:{g.CAP['band_y0']}[c1]")
    parts.append(f"[3:v]scale={sym}:-1[sym]")
    parts.append("[c1][sym]overlay=W-w-44:40[outv]")
    fc = tmp / "fc.txt"
    fc.write_text(";\n".join(parts))
    edit_reel.run(["ffmpeg", "-y", *inputs, "-/filter_complex", str(fc), "-map", "[outv]", "-map", "1:a",
                   "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-maxrate", "16M", "-bufsize", "32M",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest",
                   str(Path(args.output).resolve())])
    print("[done]", args.output)
    if not args.keep_temp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
