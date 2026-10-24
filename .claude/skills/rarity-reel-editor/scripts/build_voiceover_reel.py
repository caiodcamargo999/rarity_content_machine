#!/usr/bin/env python3
"""
build_voiceover_reel.py — voiceover + B-roll format (Workflow B of the Reel Editor).

Takes a narration audio track plus an ordered list of (clip, sentence) scenes and produces a
finished, branded vertical Reel: each clip is shown (slow push-in layered on its own real motion)
for exactly as long as its sentence is spoken; scenes are joined with styled transitions (whip
pan with motion blur, zoom punch, flash, dip...) with matching whoosh/thump SFX; the voice is
mastered, royalty-free music sits underneath and DUCKS whenever the voice speaks; and the
animated word-pop captions + Rarity symbol are burned on by reusing edit_reel.py's pipeline.

Usage:
  python3 build_voiceover_reel.py --manifest scenes.json --narration narration.wav \
      --words words.json --music ../music/brainiac.mp3 --output out.mp4

manifest.json: [
  {"video": "scene1.mp4", "offset": 2.0, "text": "The customer discovers your brand..."},
  {"video": "scene2.mp4", "text": "...", "transition": "punch"},   # optional: transition INTO this scene
  {"image": "scene3.jpg", "text": "..."}
]
  "offset"      video only, seconds into the source clip to start from (skip a boring intro).
  "transition"  one of flare, whip, whipr, punch, flash, dip, dissolve, cut. Overrides the preset for the
                boundary leading INTO this scene. (Ignored on the first scene.)

Word timings (--words): JSON [{text,start,end}] aligned to the script's own words — produced by
align_words.py (forced alignment of the narration against the script, so captions are exactly
the script's text). Without --words the narration is transcribed with whisper (needed for a
recording of Caio's real voice whose words may deviate from the script; captions then show what
whisper heard, so proof-read them).

Options:
  --transitions mix|flare|dynamic|kinetic|clean|cinematic   preset (default mix = varied, flare only at key turns)
  --music FILE            royalty-free background track (looped/trimmed to the video length)
  --music-start SEC       where in the track to start (skip a quiet intro)
  --music-lufs -27        loudness of the music bed BEFORE ducking (voice is mastered to -16)
  --no-sfx                no transition whooshes
  --no-voice-fx           don't master the voice (use when the file is already processed)
  --caption-style minimal|bold   (default minimal: Benton phrase + Playfair-italic magenta key word)
  --flare-opacity 0.85   lens-flare strength 0-1        --no-grade   skip colour matching
  --font serif|sans  --accent D50057  --chunk-size 3  --zoom 0.15  --fps 30  --keep-temp
  --model small --language eng|por|spa   (whisper; only when --words is not given)
"""
import argparse
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("edit_reel", SCRIPT_DIR / "edit_reel.py")
edit_reel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(edit_reel)

_fspec = importlib.util.spec_from_file_location("lens_flare", SCRIPT_DIR / "lens_flare.py")
lens_flare = importlib.util.module_from_spec(_fspec)
_fspec.loader.exec_module(lens_flare)

_dspec = importlib.util.spec_from_file_location("data_scenes", SCRIPT_DIR / "data_scenes.py")
sys.path.insert(0, str(SCRIPT_DIR))
data_scenes = importlib.util.module_from_spec(_dspec)
_dspec.loader.exec_module(data_scenes)

OUT_W, OUT_H = edit_reel.OUT_W, edit_reel.OUT_H

# ----------------------------------------------------------------------------------------------
# Transitions. Each is an ffmpeg `xfade` transition plus optional horizontal motion blur across
# the overlap window and a matching SFX recipe (see SFX_RECIPES).
# ----------------------------------------------------------------------------------------------
TRANSITIONS = {
    "whip":     dict(xfade="slideleft",  dur=0.28, blur=70, sfx="whoosh"),   # whip pan -> left
    "whipr":    dict(xfade="slideright", dur=0.28, blur=70, sfx="whoosh"),   # whip pan -> right
    # zoom punch: quick dissolve while the INCOMING clip snaps in from 120% -> 100% (ease-out).
    # (ffmpeg's own xfade "zoomin" pixelates badly — never use it.)
    "punch":    dict(xfade="fade",       dur=0.14, blur=0,  sfx="thump", punch=0.20),
    "whipup":   dict(xfade="slideup",    dur=0.28, blur=70, sfx="whoosh", blurdir="v"),   # vertical whip
    "whipdown": dict(xfade="slidedown",  dur=0.28, blur=70, sfx="whoosh", blurdir="v"),
    "iris":     dict(xfade="circleopen", dur=0.36, blur=0,  sfx="soft"),                  # circular reveal
    "flash":    dict(xfade="fadewhite",  dur=0.16, blur=0,  sfx="tick"),     # quick white flash cut
    "dip":      dict(xfade="fadeblack",  dur=0.42, blur=0,  sfx="soft"),     # dip to black
    # lens flare: a brand-coloured light source sweeps the frame; the cut happens at its peak.
    # (flare=True -> lens_flare.py track is screen-blended over the join; flare_dur = glow length)
    "flare":    dict(xfade="fade",       dur=0.20, blur=0,  sfx="shine", flare=True, flare_dur=0.66),
    "dissolve": dict(xfade="fade",       dur=0.40, blur=0,  sfx=None),       # clean cross-dissolve
    "cut":      dict(xfade="fade",       dur=0.04, blur=0,  sfx=None),       # effectively a hard cut
}

PRESETS = {
    # DEFAULT: varied on purpose; lens flare only at the 2 emotional turns (see SKILL.md rule 21)
    "mix":       ["whip", "iris", "flare", "cut", "whipup", "flash", "whipr", "punch", "flare", "whip"],
    # lens flare on every boundary (use sparingly — Caio asked for variety, not only flare)
    "flare":     ["flare"] * 6,
    # punchy social-native rotation: whip, punch, flash, whip back, punch...
    "dynamic":   ["whip", "punch", "flash", "whipr", "punch", "flash"],
    # fast + kinetic: lots of whips and punches, a flash for the hook
    "kinetic":   ["flash", "whip", "punch", "whipr", "whip", "punch"],
    # calm, premium: dissolves with the odd dip
    "clean":     ["dissolve", "dissolve", "dip", "dissolve", "dissolve", "dip"],
    # film-style: dips and soft punches
    "cinematic": ["dip", "punch", "dip", "dissolve", "dip", "punch"],
}


def tokenize(text):
    return [t for t in re.split(r"\s+", text.strip()) if t]


def generate_narration_wavs(narration_path, tmp):
    """Returns (wav_16k_for_transcription, duration_seconds). The original narration file is
    used as-is for the final mix (better quality than the 16kHz mono copy whisper needs)."""
    wav16 = tmp / "narration_16k.wav"
    edit_reel.run(["ffmpeg", "-y", "-i", str(narration_path), "-ac", "1", "-ar", "16000", str(wav16)])
    probe = edit_reel.ffprobe_json(str(narration_path))
    duration = float(probe["format"]["duration"])
    return wav16, duration


def align_scenes_to_words(scenes, words):
    """Consume words in order, `len(tokenize(scene text))` at a time. Returns scenes with
    start/end set to contiguous, speech-synced boundaries (midpoint between sentences)."""
    cursor = 0
    scene_words = []
    for sc in scenes:
        n = len(tokenize(sc["text"]))
        chunk = words[cursor:cursor + n]
        if not chunk:
            sys.exit(f"[error] ran out of transcribed words aligning scene: {sc['text']!r}. "
                      f"Transcription may have dropped/merged words — check narration audio "
                      f"or pass --words from align_words.py.")
        scene_words.append(chunk)
        sc["words"] = chunk
        cursor += n
    if cursor < len(words):
        print(f"[align] note: {len(words) - cursor} trailing word(s) unused "
              f"(fine if narration has a trailing beat with no matching scene).")

    for i, sc in enumerate(scenes):
        sc["start"] = 0.0 if i == 0 else None
        sc["end"] = None
    for i in range(len(scenes) - 1):
        boundary = (scene_words[i][-1]["end"] + scene_words[i + 1][0]["start"]) / 2
        scenes[i]["end"] = boundary
        scenes[i + 1]["start"] = boundary
    return scenes


def build_scene_clip_image(image_path, render_dur, out_path, zoom_amount, fps, punch=0.0, grade=""):
    """Static photo -> Ken Burns zoom clip (fallback path when a scene has no real video)."""
    total_frames = max(1, round(render_dur * fps))
    # d=total_frames replicates ONE still: `in` is constant there, so use `on` (output frame no.)
    expr = zoom_expr(zoom_amount, total_frames, punch, fps).replace("in/", "on/")
    vf = (
        f"scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,"
        f"zoompan=z={expr}:d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={OUT_W}x{OUT_H}:fps={fps}"
        f"{',' + grade if grade else ''}"
    )
    edit_reel.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf", vf, "-frames:v", str(total_frames), "-r", str(fps),
        "-pix_fmt", "yuv420p", str(out_path),
    ])


# ----------------------------------------------------------------------------------------------
# Colour consistency. Stock clips arrive with wildly different white balance / exposure (orange
# living room, teal studio, grey sofa, white desk). Each clip is measured, nudged toward a common
# neutral + exposure (partial strength, clamped), then ALL clips get the same "Rarity look"
# (slightly desaturated, cool-magenta shadows, warm highlights, soft S-curve, light vignette).
# ----------------------------------------------------------------------------------------------
TARGET_LUMA = 0.42
TARGET_SAT = 0.28          # mean HSV saturation every clip is pulled toward (stock ranges 0.1-0.6)
MATCH_STRENGTH = 0.85      # was 0.6 — Caio asked for "even more congruence" in the palette


def measure_clip_rgb(path, kind, start, dur):
    """Mean RGB (0..1) and mean HSV saturation of a few frames from the part of the clip we use."""
    import colorsys
    import numpy as np
    from PIL import Image
    samples = []
    if kind == "image":
        samples.append(np.asarray(Image.open(path).convert("RGB").resize((160, 160)), dtype=np.float32) / 255.0)
    else:
        for k in range(5):
            t = max(0.0, start + dur * (k + 0.5) / 5)
            tmp = Path(tempfile.gettempdir()) / f"_cm_{abs(hash((path, k)))}.png"
            edit_reel.run(["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1",
                           "-vf", "scale=160:-2", str(tmp)], quiet=True)
            samples.append(np.asarray(Image.open(tmp).convert("RGB"), dtype=np.float32) / 255.0)
            tmp.unlink(missing_ok=True)
    px = np.concatenate([s.reshape(-1, 3) for s in samples])
    m = px.mean(axis=0)
    mx, mn = px.max(axis=1), px.min(axis=1)
    sat = float(np.mean((mx - mn) / np.maximum(mx, 1e-3)))
    return [float(v) for v in m] + [sat]


# Shared "Rarity look": brand palette split-tone. Shadows -> deep plum/navy (#0f0a1a family),
# highlights -> warm off-white (#efeeea), mids neutral; saturation held low so the ONLY strong
# colour on screen is the brand magenta (#D50057) in captions and the flare.
RARITY_LOOK = (
    "eq=contrast=1.05:saturation=0.86,"
    "curves=r='0/0.06 0.25/0.24 0.5/0.50 0.8/0.80 0.93/0.89 1/0.94':"
    "g='0/0.04 0.25/0.22 0.5/0.48 0.8/0.78 0.93/0.88 1/0.93':"
    "b='0/0.11 0.25/0.27 0.5/0.52 0.8/0.79 0.93/0.88 1/0.91',"
    "vignette=angle=PI/6:mode=backward"
)


def color_match_filter(meas):
    """ffmpeg filter chain: per-clip white-balance + exposure + saturation match toward common
    targets (strong, clamped), then the one shared Rarity look."""
    r, g, b, sat = [max(0.02, v) for v in meas]
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    gains = [min(1.30, max(0.75, 1 + MATCH_STRENGTH * (y / c - 1))) for c in (r, g, b)]
    exp = min(1.40, max(0.65, 1 + MATCH_STRENGTH * (TARGET_LUMA / y - 1)))
    rr, gg, bb = (exp * k for k in gains)
    sat_adj = min(1.15, max(0.55, 1 + MATCH_STRENGTH * (TARGET_SAT / sat - 1)))
    return (f"colorchannelmixer=rr={rr:.4f}:gg={gg:.4f}:bb={bb:.4f},"
            f"eq=saturation={sat_adj:.3f},{RARITY_LOOK}")


def zoom_expr(zoom_amount, total_frames, punch, fps):
    """zoompan z-expression: slow push-in (1 -> 1+zoom_amount) plus, if punch>0, a fast ease-out
    from 1+punch down to 1 over the first ~0.32s (the 'zoom punch' transition)."""
    expr = f"1+{zoom_amount}*in/{max(1, total_frames)}"
    if punch:
        pf = max(2, int(0.32 * fps))
        expr += f"+{punch}*pow(max(0,1-in/{pf}),2.2)"
    return f"'{expr}'"


def build_scene_clip_video(video_path, offset, render_dur, out_path, zoom_amount, fps, punch=0.0, grade=""):
    """Real video clip trimmed to render_dur with a slow push-in on top of its own motion.

    fps= comes BEFORE zoompan: zoompan(d=1) emits one frame per input frame, so a 25fps source
    would otherwise come out ~17% too short and the xfade chain would run out of video.
    -stream_loop covers sources shorter than the slot; -frames:v trims to the exact slot."""
    total_frames = max(1, round(render_dur * fps))
    vf = (
        f"fps={fps},scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,"
        f"zoompan=z={zoom_expr(zoom_amount, total_frames, punch, fps)}:d=1:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={OUT_W}x{OUT_H}:fps={fps}"
        f"{',' + grade if grade else ''}"
    )
    edit_reel.run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-ss", f"{offset:.3f}", "-i", str(video_path),
        "-vf", vf, "-frames:v", str(total_frames), "-r", str(fps),
        "-an", "-pix_fmt", "yuv420p", str(out_path),
    ])


def plate_cmd(video, offset, render_dur, zoom_amount, fps, punch, grade, dim=0.0, blur=0.0):
    """ffmpeg argv that streams a push-in, colour-matched, optionally dimmed/blurred PLATE as raw rgb24
    1080x1920 frames — used as the background of a data scene (clip + animated callouts)."""
    total_frames = max(1, round(render_dur * fps))
    extra = ""
    if dim:
        extra += f",eq=brightness={-dim:.3f}:contrast={1 - dim * 0.5:.3f}"
    if blur:
        extra += f",gblur=sigma={blur}"
    vf = (f"fps={fps},scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,"
          f"zoompan=z={zoom_expr(zoom_amount, total_frames, punch, fps)}:d=1:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={OUT_W}x{OUT_H}:fps={fps}"
          f"{',' + grade if grade else ''}{extra}")
    return [edit_reel.FFMPEG, "-v", "error", "-stream_loop", "-1", "-ss", f"{offset:.3f}", "-i", str(video),
            "-vf", vf, "-frames:v", str(total_frames), "-r", str(fps), "-an", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]


def scene_anchors(sc):
    """manifest anchors: int = WORD INDEX within the scene's text, float = seconds after the scene's
    text starts. Returned in seconds from the START OF THE RENDERED CLIP (which begins
    offset_shift earlier than the text because of transition padding)."""
    out = {}
    for k, v in sc.get("anchors", {}).items():
        if isinstance(v, int) and not isinstance(v, bool):
            v = max(0, min(v, len(sc["words"]) - 1))
            sec = sc["words"][v]["start"] - sc["start"]
        else:
            sec = float(v)
        out[k] = sec + sc["offset_shift"]
    return out


def pick_transitions(scenes, preset):
    """Transition spec for each boundary i (scene i-1 -> scene i), i = 1..n-1."""
    seq = PRESETS[preset]
    specs = []
    for i in range(1, len(scenes)):
        name = scenes[i].get("transition") or seq[(i - 1) % len(seq)]
        if name not in TRANSITIONS:
            sys.exit(f"[error] unknown transition {name!r}; use one of {sorted(TRANSITIONS)}")
        specs.append({"name": name, **TRANSITIONS[name]})
    return specs


def plan_transitions(scenes, specs):
    """Shrink each scene's visible slot a touch (split evenly) to make room for the xfade
    overlaps, so sum(rendered) - overlaps == the narration duration. Boundary durations may
    differ per transition. Sets 'render_dur' and 'offset_shift' on each scene dict."""
    n = len(scenes)
    if n < 2:
        for sc in scenes:
            sc["render_dur"] = sc["end"] - sc["start"]
            sc["offset_shift"] = 0.0
        return scenes
    durs = [s["dur"] for s in specs]  # durs[i-1] = overlap between scene i-1 and i
    shrink_each = sum(durs) / n
    for i, sc in enumerate(scenes):
        target = max(0.3, (sc["end"] - sc["start"]) - shrink_each)
        pre = durs[i - 1] if i > 0 else 0.0
        post = durs[i] if i < n - 1 else 0.0
        sc["render_dur"] = target + pre + post
        sc["offset_shift"] = pre
    return scenes


def xfade_concat(clip_paths, render_durs, specs, out_path, fps, flare_path=None, flare_opacity=0.85):
    """Join scene clips with the planned transitions. Returns the list of
    (window_start, window_end, spec) in output time, used for blur + SFX placement."""
    inputs = []
    for p in clip_paths:
        inputs += ["-i", str(p)]
    parts, windows = [], []
    prev = "0:v"
    cumulative = render_durs[0]
    for i in range(1, len(clip_paths)):
        sp = specs[i - 1]
        offset = max(0.0, cumulative - sp["dur"])
        nxt = f"x{i}"
        parts.append(f"[{prev}][{i}:v]xfade=transition={sp['xfade']}:duration={sp['dur']:.3f}:offset={offset:.3f}[{nxt}]")
        windows.append((offset, offset + sp["dur"], sp))
        prev = nxt
        cumulative = cumulative + render_durs[i] - sp["dur"]
    # horizontal motion blur across the (inner part of the) whip windows
    for k, (a, b, sp) in enumerate(windows):
        if sp["blur"]:
            pad = (b - a) * 0.12
            nxt = f"b{k}"
            sh, sv = (0.01, sp["blur"]) if sp.get("blurdir") == "v" else (sp["blur"], 0)
            parts.append(f"[{prev}]gblur=sigma={sh}:sigmaV={sv}:steps=2:enable='between(t,{a + pad:.3f},{b - pad:.3f})'[{nxt}]")
            prev = nxt
    if flare_path:
        # screen-blend the flare track in RGB (gbrp) so its black adds exactly nothing
        inputs += ["-i", str(flare_path)]
        parts.append(f"[{prev}]format=gbrp[mainrgb]")
        parts.append(f"[{len(clip_paths)}:v]scale={OUT_W}:{OUT_H}:flags=bicubic,format=gbrp[flr]")
        parts.append(f"[mainrgb][flr]blend=all_mode=screen:all_opacity={flare_opacity}:shortest=1,format=yuv420p[flared]")
        prev = "flared"
    edit_reel.run([
        "ffmpeg", "-y", *inputs, "-filter_complex", ";".join(parts), "-map", f"[{prev}]",
        "-r", str(fps), "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", str(out_path),
    ])
    return windows


def plan_windows(render_durs, specs):
    """Output-time (start, end, spec) of every transition, computed without rendering."""
    wins, cumulative = [], render_durs[0]
    for i in range(1, len(render_durs)):
        sp = specs[i - 1]
        off = max(0.0, cumulative - sp["dur"])
        wins.append((off, off + sp["dur"], sp))
        cumulative = cumulative + render_durs[i] - sp["dur"]
    return wins


# ----------------------------------------------------------------------------------------------
# Audio: synthesized SFX, voice mastering, music bed with ducking, final loudness.
# ----------------------------------------------------------------------------------------------
SFX_RECIPES = {
    # pink-noise swell, band-limited, fast attack -> soft tail
    "whoosh": "anoisesrc=d=0.55:c=pink:r=44100:a=0.8,highpass=f=350,lowpass=f=7000,"
              "afade=t=in:d=0.18:curve=qsin,afade=t=out:st=0.2:d=0.35:curve=exp,volume=1.0",
    # sub thump
    "thump":  "sine=f=62:d=0.32:r=44100,afade=t=out:d=0.3:curve=exp,volume=2.4",
    # soft UI "pop" for motion-graphic cards
    "pop":    "sine=f=640:d=0.10:r=44100,afade=t=out:d=0.10:curve=exp,volume=0.7",
    # tiny high tick
    "tick":   "anoisesrc=d=0.09:c=white:r=44100:a=0.6,highpass=f=2500,afade=t=out:d=0.08,volume=0.9",
    # airy rising shimmer + soft whoosh for lens-flare cuts
    "shine":  "anoisesrc=d=0.8:c=pink:r=44100:a=0.7,highpass=f=1400,lowpass=f=11000,"
              "afade=t=in:d=0.42:curve=qsin,afade=t=out:st=0.4:d=0.4:curve=exp,volume=0.9",
    # low airy exhale for dips
    "soft":   "anoisesrc=d=0.7:c=brown:r=44100:a=0.7,lowpass=f=2200,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.4,volume=1.2",
}


def make_sfx(kind, out_path):
    edit_reel.run(["ffmpeg", "-y", "-f", "lavfi", "-i", SFX_RECIPES[kind], "-ac", "2", str(out_path)], quiet=True)


VOICE_CHAIN = (
    "volume=-4dB,"                                # headroom: raw TTS peaks near 0 dBFS
    "highpass=f=75,"
    "equalizer=f=220:t=q:w=1.0:g=-1.5,"          # tame boxiness
    "equalizer=f=3200:t=q:w=1.2:g=2.5,"          # presence
    "equalizer=f=9000:t=h:w=0.7:g=1.2,"          # air
    "acompressor=threshold=-20dB:ratio=3:attack=8:release=140:makeup=3,"
    "loudnorm=I=-16:TP=-1.5:LRA=7"
)


def mix_audio(narration, out_wav, total_dur, tmp, music=None, music_start=0.0, music_lufs=-27.0,
              sfx_events=(), voice_fx=True):
    """Mix voice + music (ducked) + SFX into one stereo wav of exactly total_dur seconds."""
    cmd = ["ffmpeg", "-y", "-i", str(narration)]
    fc = []
    idx = 1
    chain = VOICE_CHAIN if voice_fx else "anull"
    fc.append(f"[0:a]{chain},apad=whole_dur={total_dur:.3f},atrim=0:{total_dur:.3f},aformat=channel_layouts=stereo[voice]")
    mix_inputs = ["[voice]"]
    if music:
        cmd += ["-stream_loop", "-1", "-ss", f"{music_start:.2f}", "-i", str(music)]
        fade_out_st = max(0.0, total_dur - 1.8)
        fc.append(
            f"[{idx}:a]aformat=channel_layouts=stereo,atrim=0:{total_dur:.3f},asetpts=PTS-STARTPTS,"
            f"loudnorm=I={music_lufs}:TP=-3:LRA=9,"
            f"afade=t=in:st=0:d=0.8,afade=t=out:st={fade_out_st:.3f}:d=1.8[mus]"
        )
        # duck the music whenever the voice is present (a copy of the voice drives the compressor)
        fc.append("[voice]asplit=2[voice][vsc]")
        fc.append("[mus][vsc]sidechaincompress=threshold=0.025:ratio=9:attack=12:release=420:makeup=1[musd]")
        mix_inputs.append("[musd]")
        idx += 1
    for k, (t, kind, db) in enumerate(sfx_events):
        wav = tmp / f"sfx_{k}_{kind}.wav"
        make_sfx(kind, wav)
        cmd += ["-i", str(wav)]
        ms = max(0, int(t * 1000))
        fc.append(f"[{idx}:a]aformat=channel_layouts=stereo,adelay={ms}|{ms},volume={db}dB[s{k}]")
        mix_inputs.append(f"[s{k}]")
        idx += 1
    fc.append(f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:normalize=0:duration=first,"
              f"atrim=0:{total_dur:.3f},loudnorm=I=-14:TP=-1.2:LRA=9[out]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "44100", "-ac", "2", str(out_wav)]
    edit_reel.run(cmd)


def mux_audio(video_path, audio_path, out_path):
    edit_reel.run([
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(audio_path),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-shortest", str(out_path),
    ])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--words", default=None, help="JSON [{text,start,end}] (from align_words.py); skips whisper")
    ap.add_argument("--transitions", default="mix", choices=sorted(PRESETS))
    ap.add_argument("--music", default=None)
    ap.add_argument("--music-start", type=float, default=0.0)
    ap.add_argument("--music-lufs", type=float, default=-27.0)
    ap.add_argument("--no-sfx", action="store_true")
    ap.add_argument("--no-voice-fx", action="store_true")
    ap.add_argument("--flare-opacity", type=float, default=0.85, help="0-1 strength of the lens-flare blend (default 0.85)")
    ap.add_argument("--caption-style", choices=["minimal", "bold"], default="minimal")
    ap.add_argument("--no-grade", action="store_true", help="skip per-clip colour matching + shared look")
    ap.add_argument("--font", choices=["serif", "sans"], default="sans")
    ap.add_argument("--accent", default=edit_reel.DEFAULT_ACCENT)
    ap.add_argument("--model", default="small")
    ap.add_argument("--chunk-size", type=int, default=3)
    ap.add_argument("--zoom", type=float, default=0.15)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--language", default=None, choices=["eng", "por", "spa", None])
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    whisper_lang = {"eng": "en", "por": "pt", "spa": "es", None: None}[args.language]

    manifest_path = Path(args.manifest).resolve()
    scenes = json.loads(manifest_path.read_text())
    manifest_dir = manifest_path.parent
    for sc in scenes:
        key = "video" if "video" in sc else ("image" if "image" in sc else None)
        sc["_kind"] = "graphic" if "graphic" in sc else key
        if key:
            p = Path(sc[key])
            sc[key] = str(p if p.is_absolute() else (manifest_dir / p).resolve())
        sc.setdefault("offset", 0.0)

    narration_path = Path(args.narration).resolve()
    output_path = Path(args.output).resolve()
    font_path = edit_reel.FONT_SANS if args.font == "sans" else edit_reel.FONT_SERIF

    tmp = Path(tempfile.mkdtemp(prefix="rarity_voiceover_"))
    print(f"[workdir] {tmp}")
    try:
        wav16, duration = generate_narration_wavs(narration_path, tmp)
        if args.words:
            words = json.loads(Path(args.words).read_text())
        else:
            words, _ = edit_reel.transcribe(wav16, whisper_lang, args.model)
        if not words:
            sys.exit("[error] no word timings — check narration audio.")

        scenes = align_scenes_to_words(scenes, words)
        scenes[-1]["end"] = duration
        specs = pick_transitions(scenes, args.transitions)
        scenes = plan_transitions(scenes, specs)

        clips_dir = tmp / "clips"
        clips_dir.mkdir()
        clip_paths, render_durs = [], []
        for i, sc in enumerate(scenes):
            clip_path = clips_dir / f"scene_{i:02d}.mp4"
            tname = "" if i == 0 else f" [{specs[i - 1]['name']}]"
            punch = 0.0 if i == 0 else specs[i - 1].get("punch", 0.0)
            print(f"[scene {i}]{tname} {sc['start']:.2f}s -> {sc['end']:.2f}s (render {sc['render_dur']:.2f}s): {sc['text']!r}")
            has_plate = sc["_kind"] in ("video", "image") or (sc["_kind"] == "graphic" and "video" in sc)
            src = sc.get("video") or sc.get("image")
            src_offset = max(0.0, sc["offset"] - sc["offset_shift"]) if sc.get("video") else 0.0
            grade = ""
            if has_plate and not args.no_grade:
                rgb = measure_clip_rgb(src, "video" if sc.get("video") else "image", src_offset, sc["render_dur"])
                grade = color_match_filter(rgb)
                print(f"           colour-match: mean RGB {[round(v, 2) for v in rgb[:3]]}, sat {rgb[3]:.2f}")
            if sc["_kind"] == "graphic":
                bg = None
                if sc.get("video"):
                    bg = plate_cmd(sc["video"], src_offset, sc["render_dur"], args.zoom, args.fps, punch, grade,
                                   dim=sc.get("dim", 0.0), blur=sc.get("blur", 0.0))
                data_scenes.render_scene(clip_path, sc["graphic"], sc.get("params", {}), scene_anchors(sc),
                                         sc["render_dur"], args.fps, edit_reel.FFMPEG, bg_cmd=bg)
            elif sc["_kind"] == "video":
                build_scene_clip_video(sc["video"], src_offset, sc["render_dur"], clip_path, args.zoom, args.fps, punch, grade)
            else:
                build_scene_clip_image(sc["image"], sc["render_dur"], clip_path, args.zoom, args.fps, punch, grade)
            clip_paths.append(clip_path)
            render_durs.append(sc["render_dur"])

        concatenated = tmp / "concatenated.mp4"
        if len(clip_paths) > 1:
            windows = plan_windows(render_durs, specs)
            flare_events = [{"center": (a + b) / 2, "dur": sp["flare_dur"], "dir": k}
                            for k, (a, b, sp) in enumerate(windows) if sp.get("flare")]
            flare_path = None
            if flare_events:
                flare_path = tmp / "flares.mov"
                lens_flare.build_flare_track(flare_events, sum(render_durs) - sum(s["dur"] for s in specs), flare_path, args.fps)
            windows = xfade_concat(clip_paths, render_durs, specs, concatenated, args.fps, flare_path, args.flare_opacity)
        else:
            shutil.copy(clip_paths[0], concatenated)
            windows = []

        # SFX land on the middle of each transition window, slightly early so the swell leads in
        sfx_events = []
        if not args.no_sfx:
            for a, b, sp in windows:
                if sp["sfx"]:
                    lead = 0.34 if sp["sfx"] == "shine" else 0.16
                    sfx_events.append((max(0.0, (a + b) / 2 - lead), sp["sfx"], -17 if sp["sfx"] != "tick" else -22))

        mixed = tmp / "mix.wav"
        mix_audio(narration_path, mixed, duration, tmp, music=args.music, music_start=args.music_start,
                  music_lufs=args.music_lufs, sfx_events=sfx_events, voice_fx=not args.no_voice_fx)

        base_with_audio = tmp / "base_with_audio.mp4"
        mux_audio(concatenated, mixed, base_with_audio)

        caps_dir = tmp / "caps"
        caps_dir.mkdir()
        caption_frames = edit_reel.build_caption_frames(words, font_path, args.accent, args.chunk_size, caps_dir, style=args.caption_style)
        print(f"[captions] {len(caption_frames)} caption images rendered")
        caption_track = edit_reel.build_caption_track(caption_frames, duration, caps_dir, args.fps)

        edit_reel.final_pass(base_with_audio, caption_track, output_path, grade=None if not args.no_grade else "eq=contrast=1.06:saturation=1.08:brightness=0.01")
        print(f"[done] -> {output_path}")
    finally:
        if args.keep_temp:
            print(f"[keep-temp] intermediates left at {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
