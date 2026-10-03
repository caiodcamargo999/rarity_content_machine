#!/usr/bin/env python3
"""
build_voiceover_reel.py — voiceover + correlated-images format (extension of the Reel Editor).

Takes a narration audio track plus an ordered list of (clip, sentence) scenes, and produces a
branded vertical video where each clip is shown — with a slow push-in zoom layered on top — for
exactly as long as its matching sentence is being spoken, synced via real word-level transcription
of the narration (not a guessed even split). Finishes with the same animated word-highlight
captions and Rarity logo overlay as edit_reel.py, by reusing its caption/branding pipeline directly.

Each scene can be either a real VIDEO clip (preferred — real motion reads as far more realistic and
"viral" than a photo with a zoom effect bolted on) or a static image (falls back to the old Ken
Burns-on-a-photo treatment). Mixing both in one manifest is fine.

Alignment method: the manifest gives us the exact script text per scene, so after transcribing the
narration we walk the transcribed word list and consume `len(scene_text.split())` words per scene
in order. This is reliable because the words are known in advance — it is NOT a general "match any
audio to any text" aligner.

Usage:
  python3 build_voiceover_reel.py --manifest scenes.json --narration narration.wav --output out.mp4

manifest.json: [
  {"video": "scene1.mp4", "offset": 2.0, "text": "The customer discovers your brand..."},
  {"image": "scene2.jpg", "text": "Days later a package arrives..."}
]
"offset" (video scenes only, default 0) is where to start reading the source clip from, so you can
skip a boring intro second instead of always starting at frame 0.

Transitions: consecutive scenes are joined with a short xfade (not a hard cut) — the style
rotates through a curated list (zoom/slide/wipe) so a multi-scene video doesn't repeat the same
cut every time. Each scene's slot is shrunk very slightly (a few hundred ms, split evenly across
all scenes) to make room for the overlaps, so the total video length still matches the narration
exactly — only the scene-to-scene boundary shifts a touch, never the caption timing, since captions
are keyed to the narration's own absolute word timestamps regardless of where scene cuts land.

Options:
  --font serif|sans      Caption font (default sans)
  --accent D50057        Accent hex for the highlighted word (default Rarity magenta)
  --model small          Whisper model size
  --chunk-size 4         Words per caption chunk
  --zoom 0.15            Total Ken Burns zoom amount per scene (0.15 = zooms in to 115%)
  --transition-duration 0.35   Crossfade length between scenes, in seconds
  --fps 30
  --keep-temp

Requires: ffmpeg-full (libass not actually needed here, but find_binary in edit_reel.py pins the
same ffmpeg-full binaries used elsewhere in this project) + faster-whisper, both already set up by
edit_reel.py / rarity-reel-editor.
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

OUT_W, OUT_H = edit_reel.OUT_W, edit_reel.OUT_H


def tokenize(text):
    return [t for t in re.split(r"\s+", text.strip()) if t]


def generate_narration_wavs(narration_path, tmp):
    """Returns (wav_16k_for_transcription, duration_seconds). The original narration file is
    used as-is for the final mux (better quality than the 16kHz mono copy whisper needs)."""
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
                      f"Transcription may have dropped/merged words — check narration audio.")
        scene_words.append(chunk)
        cursor += n
    if cursor < len(words):
        print(f"[align] note: {len(words) - cursor} trailing transcribed word(s) unused "
              f"(fine if narration has a trailing beat with no matching scene).")

    for i, sc in enumerate(scenes):
        sc["start"] = 0.0 if i == 0 else None
        sc["end"] = None
    for i in range(len(scenes) - 1):
        boundary = (scene_words[i][-1]["end"] + scene_words[i + 1][0]["start"]) / 2
        scenes[i]["end"] = boundary
        scenes[i + 1]["start"] = boundary
    return scenes


def build_scene_clip_image(image_path, render_dur, out_path, zoom_amount, fps):
    """Static photo -> Ken Burns zoom clip (fallback path when a scene has no real video).
    render_dur already includes any xfade padding added on top of the scene's visible slot."""
    total_frames = max(1, round(render_dur * fps))
    zoom_rate = zoom_amount / total_frames
    vf = (
        f"scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,"
        f"zoompan=z='min(zoom+{zoom_rate:.8f},{1 + zoom_amount})':d={total_frames}:"
        f"s={OUT_W}x{OUT_H}:fps={fps}"
    )
    edit_reel.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf", vf, "-frames:v", str(total_frames), "-r", str(fps),
        "-pix_fmt", "yuv420p", str(out_path),
    ])


def build_scene_clip_video(video_path, offset, render_dur, out_path, zoom_amount, fps):
    """Real video clip, trimmed to render_dur (the visible slot plus any xfade padding on either
    side), with a slow push-in zoom layered on top of its own real motion (zoompan with d=1
    advances the zoom one step per actual video frame, instead of replicating a single still frame
    like the image path does)."""
    total_frames = max(1, round(render_dur * fps))
    zoom_rate = zoom_amount / total_frames
    vf = (
        f"scale=3240:5760:force_original_aspect_ratio=increase,crop=3240:5760,"
        f"zoompan=z='min(zoom+{zoom_rate:.8f},{1 + zoom_amount})':d=1:"
        f"s={OUT_W}x{OUT_H}:fps={fps}"
    )
    edit_reel.run([
        "ffmpeg", "-y", "-ss", f"{offset:.3f}", "-t", f"{render_dur + 1.0:.3f}", "-i", str(video_path),
        "-vf", vf, "-frames:v", str(total_frames), "-r", str(fps),
        "-an", "-pix_fmt", "yuv420p", str(out_path),
    ])


TRANSITION_STYLES = ["zoomin", "slideleft", "wiperight", "slideup", "smoothleft"]


def plan_transitions(scenes, xfade_dur):
    """Shrinks each scene's visible slot a touch (split evenly) to make room for xfade overlaps,
    so sum(rendered) - overlaps == the original total (narration) duration. Sets 'render_dur' and
    'offset_shift' (video scenes: how much earlier to start reading the source clip) on each
    scene dict in place."""
    n = len(scenes)
    if n < 2 or xfade_dur <= 0:
        for sc in scenes:
            sc["render_dur"] = sc["end"] - sc["start"]
            sc["offset_shift"] = 0.0
        return scenes
    shrink_each = (xfade_dur * (n - 1)) / n
    for i, sc in enumerate(scenes):
        target = max(0.3, (sc["end"] - sc["start"]) - shrink_each)
        pre = xfade_dur if i > 0 else 0.0
        post = xfade_dur if i < n - 1 else 0.0
        sc["render_dur"] = target + pre + post
        sc["offset_shift"] = pre
    return scenes


def xfade_concat(clip_paths, render_durs, xfade_dur, out_path):
    """Joins scene clips with a rotating set of dynamic transitions (zoom/slide/wipe) instead of
    a hard cut, via ffmpeg's xfade filter. Needs clip_paths[i] to already be render_durs[i] long,
    padded per plan_transitions() so the overlaps don't eat into the visible content."""
    inputs = []
    for p in clip_paths:
        inputs += ["-i", str(p)]
    filt_parts = []
    prev_label = "0:v"
    cumulative = render_durs[0]
    for i in range(1, len(clip_paths)):
        style = TRANSITION_STYLES[(i - 1) % len(TRANSITION_STYLES)]
        offset = max(0.0, cumulative - xfade_dur)
        nxt = f"x{i}"
        filt_parts.append(
            f"[{prev_label}][{i}:v]xfade=transition={style}:duration={xfade_dur:.3f}:offset={offset:.3f}[{nxt}]"
        )
        prev_label = nxt
        cumulative = cumulative + render_durs[i] - xfade_dur
    filt = ";".join(filt_parts)
    edit_reel.run([
        "ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", f"[{prev_label}]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(out_path),
    ])


def mux_audio(video_path, narration_path, out_path):
    edit_reel.run([
        "ffmpeg", "-y", "-i", str(video_path), "-i", str(narration_path),
        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(out_path),
    ])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--font", choices=["serif", "sans"], default="sans")
    ap.add_argument("--accent", default=edit_reel.DEFAULT_ACCENT)
    ap.add_argument("--model", default="small")
    ap.add_argument("--chunk-size", type=int, default=4)
    ap.add_argument("--zoom", type=float, default=0.15)
    ap.add_argument("--transition-duration", type=float, default=0.35)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--language", default=None, choices=["eng", "por", "spa", None])
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    lang_map = {"eng": "en", "por": "pt", "spa": "es", None: None}
    whisper_lang = lang_map[args.language]

    manifest_path = Path(args.manifest).resolve()
    scenes = json.loads(manifest_path.read_text())
    manifest_dir = manifest_path.parent
    for sc in scenes:
        key = "video" if "video" in sc else "image"
        sc["_kind"] = key
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
        words, detected_lang = edit_reel.transcribe(wav16, whisper_lang, args.model)
        if not words:
            sys.exit("[error] transcription returned no words — check narration audio.")

        scenes = align_scenes_to_words(scenes, words)
        scenes[-1]["end"] = duration
        scenes = plan_transitions(scenes, args.transition_duration)

        clips_dir = tmp / "clips"
        clips_dir.mkdir()
        clip_paths = []
        render_durs = []
        for i, sc in enumerate(scenes):
            clip_path = clips_dir / f"scene_{i:02d}.mp4"
            print(f"[scene {i}] {sc['start']:.2f}s -> {sc['end']:.2f}s "
                  f"(render {sc['render_dur']:.2f}s incl. transition padding): {sc['text']!r}")
            if sc["_kind"] == "video":
                src_offset = max(0.0, sc["offset"] - sc["offset_shift"])
                build_scene_clip_video(sc["video"], src_offset, sc["render_dur"], clip_path, args.zoom, args.fps)
            else:
                build_scene_clip_image(sc["image"], sc["render_dur"], clip_path, args.zoom, args.fps)
            clip_paths.append(clip_path)
            render_durs.append(sc["render_dur"])

        concatenated = tmp / "concatenated.mp4"
        if len(clip_paths) > 1:
            xfade_concat(clip_paths, render_durs, args.transition_duration, concatenated)
        else:
            shutil.copy(clip_paths[0], concatenated)

        base_with_audio = tmp / "base_with_audio.mp4"
        mux_audio(concatenated, narration_path, base_with_audio)

        caps_dir = tmp / "caps"
        caps_dir.mkdir()
        caption_frames = edit_reel.build_caption_frames(words, font_path, args.accent, args.chunk_size, caps_dir)
        print(f"[captions] {len(caption_frames)} word-highlight frames rendered")
        caption_track = edit_reel.build_caption_track(caption_frames, duration, caps_dir, args.fps)

        edit_reel.final_pass(base_with_audio, caption_track, output_path)
        print(f"[done] -> {output_path}")
    finally:
        if args.keep_temp:
            print(f"[keep-temp] intermediates left at {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
