#!/usr/bin/env python3
"""
edit_reel.py — Rarity Reel Editor (Step 3 of the personal video pipeline).

Takes one raw recorded video and produces a cut, treated, captioned, branded vertical Reel:
  1. Transcribes the audio locally (faster-whisper, word-level timestamps).
  2. Auto-cuts dead air / long pauses (jump-cut style) based on word gaps.
  3. Applies a light brand colour treatment and crops/scales to 1080x1920 (9:16).
  4. Burns in animated word-highlight captions in Rarity's brand font + magenta accent,
     reusing the exact font assets and accent colour from the rarity-ig-designer skill.
  5. Overlays the transparent Rarity symbol, top-right, for the whole clip.

Usage:
  python3 edit_reel.py <input_video> <output_video> [options]

Options:
  --language eng|por|spa      Force transcription language (default: auto-detect)
  --no-cut                    Skip dead-air removal, keep original timing
  --cut-threshold 0.6         Minimum silence gap (seconds) to cut (default 0.6)
  --chunk-size 4              Words per caption chunk (default 4)
  --font serif|sans           Caption font: Playfair Display or Plus Jakarta Sans (default sans)
  --accent D50057             Accent hex colour for the highlighted word (default Rarity magenta)
  --model tiny|base|small|medium   Whisper model size (default small; tiny/base are faster, less accurate)
  --keep-temp                 Don't delete intermediate files (for debugging)

Requires: ffmpeg + ffprobe on PATH, faster-whisper installed in this project's .venv.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent  # .claude/skills/rarity-reel-editor
SKILLS_ROOT = SKILL_DIR.parent  # .claude/skills
DESIGNER_ASSETS = SKILLS_ROOT / "rarity-ig-designer" / "assets"
FONTS_DIR = SKILL_DIR / "fonts"  # clean, fonts-ONLY copy — libass's fontsdir scan gets
                                  # confused (and silently falls back to a system font)
                                  # if the directory also has .png/.json/.txt files in it.

FONT_SANS = FONTS_DIR / "headline-sans.ttf"
FONT_SERIF = FONTS_DIR / "headline.ttf"
SYMBOL = DESIGNER_ASSETS / "rarity-symbol-white.png"

DEFAULT_ACCENT = "D50057"  # Rarity magenta, RGB hex
WHITE_RGB = "FFFFFF"

OUT_W, OUT_H = 1080, 1920


def find_binary(name, candidates):
    """ass/subtitles burn-in needs libass — the plain Homebrew `ffmpeg` formula does NOT
    bundle it (only `ffmpeg-full` does, as of 2026-10). Prefer ffmpeg-full's binaries over
    whatever's on PATH so this skill doesn't silently fall back to a build with no libass."""
    for c in candidates:
        if Path(c).exists():
            return c
    found = shutil.which(name)
    if found:
        return found
    sys.exit(f"[error] '{name}' not found. Install it: brew install ffmpeg-full")


FFMPEG = find_binary("ffmpeg", ["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", "/usr/local/opt/ffmpeg-full/bin/ffmpeg"])
FFPROBE = find_binary("ffprobe", ["/opt/homebrew/opt/ffmpeg-full/bin/ffprobe", "/usr/local/opt/ffmpeg-full/bin/ffprobe"])


def run(cmd, quiet=False):
    cmd = [str(c) for c in cmd]
    if cmd and cmd[0] == "ffmpeg":
        cmd[0] = FFMPEG
    if not quiet:
        print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, capture_output=quiet)


def ffprobe_json(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration:stream=width,height,codec_type",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def has_audio_stream(probe):
    return any(s.get("codec_type") == "audio" for s in probe.get("streams", []))


def extract_audio(video, wav_path):
    run(["ffmpeg", "-y", "-i", video, "-ac", "1", "-ar", "16000", "-vn", wav_path])


def load_wav_as_float_array(wav_path):
    """Read a 16kHz mono 16-bit PCM wav directly (stdlib only) — avoids a broken
    faster-whisper -> PyAV version pairing where model.transcribe(path) fails on
    av.open(metadata_errors=...). We already produce exactly this format via ffmpeg."""
    import wave
    import numpy as np
    with wave.open(str(wav_path), "rb") as wf:
        assert wf.getframerate() == 16000, f"expected 16kHz wav, got {wf.getframerate()}"
        assert wf.getnchannels() == 1, "expected mono wav"
        raw = wf.readframes(wf.getnframes())
    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return audio


def transcribe(wav_path, language, model_size):
    from faster_whisper import WhisperModel
    print(f"[transcribe] loading faster-whisper model '{model_size}' (first run downloads it)...")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    audio_array = load_wav_as_float_array(wav_path)
    segments, info = model.transcribe(audio_array, word_timestamps=True, language=language)
    words = []
    for seg in segments:
        if not seg.words:
            continue
        for w in seg.words:
            text = w.word.strip()
            if text:
                words.append({"start": w.start, "end": w.end, "text": text})
    print(f"[transcribe] detected language: {info.language} (p={info.language_probability:.2f}), {len(words)} words")
    return words, info.language


def compute_cuts(words, duration, min_gap, pad=0.08):
    """Return list of (start,end) regions to REMOVE — gaps between words longer than min_gap."""
    cuts = []
    prev_end = 0.0
    for w in words:
        gap = w["start"] - prev_end
        if gap > min_gap:
            cuts.append((prev_end + pad, w["start"] - pad))
        prev_end = max(prev_end, w["end"])
    if duration - prev_end > min_gap:
        cuts.append((prev_end + pad, duration - pad))
    return [(max(0.0, s), min(duration, e)) for s, e in cuts if e - s > 0.05]


def keep_segments_from_cuts(cuts, duration):
    keeps = []
    cur = 0.0
    for s, e in sorted(cuts):
        if s > cur:
            keeps.append((cur, s))
        cur = max(cur, e)
    if cur < duration:
        keeps.append((cur, duration))
    return [k for k in keeps if k[1] - k[0] > 0.05]


def remap_time(t, cuts):
    """Map an original timestamp to its position on the post-cut timeline."""
    offset = 0.0
    for s, e in cuts:
        if e <= t:
            offset += (e - s)
        elif s < t:
            offset += (t - s)
    return max(0.0, t - offset)


def cut_video(input_video, output_video, keeps, has_audio):
    if len(keeps) == 1 and keeps[0][0] == 0.0:
        shutil.copy(input_video, output_video)
        return
    vparts, aparts = [], []
    for i, (s, e) in enumerate(keeps):
        vparts.append(f"[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]")
        if has_audio:
            aparts.append(f"[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]")
    n = len(keeps)
    if has_audio:
        concat_inputs = "".join(f"[v{i}][a{i}]" for i in range(n))
        concat = f"{concat_inputs}concat=n={n}:v=1:a=1[vcat][acat]"
        maps = ["-map", "[vcat]", "-map", "[acat]"]
    else:
        concat_inputs = "".join(f"[v{i}]" for i in range(n))
        concat = f"{concat_inputs}concat=n={n}:v=1:a=0[vcat]"
        maps = ["-map", "[vcat]"]
    filt = ";".join(vparts + aparts + [concat])
    run(["ffmpeg", "-y", "-i", input_video, "-filter_complex", filt, *maps,
         "-c:v", "libx264", "-preset", "fast", "-crf", "18",
         *(["-c:a", "aac", "-b:a", "192k"] if has_audio else []),
         output_video])


CAPTION_MAX_W = int(OUT_W * 0.86)
CAPTION_BASE_SIZE = 86
CAPTION_MIN_SIZE = 46
CAPTION_BOTTOM_MARGIN = 420  # px from bottom — clears IG's own UI buttons/caption area


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def fit_caption_font(draw, texts, font_path, max_width):
    """Pick the largest size in range that fits all words of this chunk on one line —
    rendered directly from our own bundled TTF via Pillow, same engine as render_post.py.
    Zero dependency on the OS's font database (unlike ASS/libass's fontsdir, which proved
    unreliable on macOS's CoreText backend — see README note below)."""
    full_text = " ".join(texts)
    size = CAPTION_BASE_SIZE
    while size > CAPTION_MIN_SIZE:
        font = ImageFont.truetype(str(font_path), size)
        if draw.textlength(full_text, font=font) <= max_width:
            return size, font
        size -= 4
    return CAPTION_MIN_SIZE, ImageFont.truetype(str(font_path), CAPTION_MIN_SIZE)


def render_caption_frame(chunk_words, highlight_idx, font, accent_rgb, out_path):
    """One transparent 1080x1920 PNG: the whole chunk in white, the currently-spoken
    word in the brand accent colour — same visual language as the carousel's italic
    accent word, just without the italic (captions stay upright for legibility at
    speed)."""
    img = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    texts = [w["text"].upper() for w in chunk_words]
    space_w = d.textlength(" ", font=font)
    widths = [d.textlength(t, font=font) for t in texts]
    total_w = sum(widths) + space_w * max(0, len(texts) - 1)
    x = (OUT_W - total_w) / 2
    baseline_y = OUT_H - CAPTION_BOTTOM_MARGIN

    for i, (t, w) in enumerate(zip(texts, widths)):
        color = accent_rgb if i == highlight_idx else (255, 255, 255)
        for dx, dy in ((-3, -3), (-3, 0), (-3, 3), (0, -3), (0, 3), (3, -3), (3, 0), (3, 3)):
            d.text((x + dx, baseline_y + dy), t, font=font, fill=(0, 0, 0, 235))
        d.text((x, baseline_y), t, font=font, fill=color + (255,))
        x += w + space_w
    img.save(out_path)


def build_caption_frames(words_remapped, font_path, accent_hex, chunk_size, out_dir):
    """Builds one PNG per word (the chunk it belongs to, with that word highlighted) and
    returns [(png_path, start, end), ...] in the same post-cut timeline as the video."""
    accent_rgb = hx(accent_hex)
    probe_img = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    probe_draw = ImageDraw.Draw(probe_img)
    chunks = [words_remapped[i:i + chunk_size] for i in range(0, len(words_remapped), chunk_size)]
    frames = []
    for ci, chunk in enumerate(chunks):
        if not chunk:
            continue
        texts = [w["text"].upper() for w in chunk]
        _, font = fit_caption_font(probe_draw, texts, font_path, CAPTION_MAX_W)
        for wi, w in enumerate(chunk):
            if w["end"] <= w["start"]:
                continue
            png_path = out_dir / f"cap_{ci:04d}_{wi:02d}.png"
            render_caption_frame(chunk, wi, font, accent_rgb, png_path)
            frames.append((png_path, w["start"], w["end"]))
    return frames


BLANK_CAPTION_NAME = "cap_blank.png"


def build_caption_track(caption_frames, total_duration, out_dir, fps=30):
    """Bakes every caption PNG (plus a fully-transparent filler for the gaps between words/
    sentences) into ONE alpha-channel video spanning [0, total_duration], via the concat
    demuxer's per-file `duration` directive.

    This replaces the old approach of chaining one `overlay` filter per word directly onto
    the main video (50+ simultaneous `-i` inputs for a full sentence-length script). That
    chain silently stopped compositing partway through on longer renders — the captions
    would just vanish for the second half of the video with no ffmpeg error — almost
    certainly a resource/stream-count ceiling in a single filtergraph with that many inputs.
    Baking to one pre-rendered track first means the final composite only ever adds ONE extra
    input (this track) regardless of how many words are in the script, which is both the fix
    and a faster render."""
    out_dir = Path(out_dir)
    blank_path = out_dir / BLANK_CAPTION_NAME
    Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0)).save(blank_path)

    entries = []  # (png_path, duration)
    cursor = 0.0
    for png_path, start, end in caption_frames:
        if start > cursor + 0.001:
            entries.append((blank_path, start - cursor))
        entries.append((png_path, max(0.01, end - start)))
        cursor = max(cursor, end)
    if total_duration > cursor + 0.001:
        entries.append((blank_path, total_duration - cursor))
    if not entries:
        entries.append((blank_path, total_duration))

    concat_list = out_dir / "caption_concat.txt"
    lines = []
    for png_path, dur in entries:
        lines.append(f"file '{png_path}'\nduration {dur:.3f}\n")
    lines.append(f"file '{entries[-1][0]}'\n")  # concat demuxer quirk: repeat last file, no duration
    concat_list.write_text("".join(lines))

    track_path = out_dir / "caption_track.mov"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-r", str(fps), "-fps_mode", "cfr", "-c:v", "qtrle", str(track_path)])
    return track_path


def final_pass(cut_video_path, caption_track_path, output_path):
    """Scale/crop to 9:16, apply a light brand colour treatment, overlay the single
    pre-rendered caption track, then stamp the transparent Rarity symbol top-right —
    always exactly 3 inputs, regardless of script length (see build_caption_track)."""
    filt = (
        f"[0:v]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H},eq=contrast=1.06:saturation=1.08:brightness=0.01[v0];"
        f"[v0][1:v]overlay=0:0[v1];"
        f"[2:v]scale=64:-1[sym];"
        f"[v1][sym]overlay=W-w-40:40[outv]"
    )
    run(["ffmpeg", "-y", "-i", cut_video_path, "-i", str(caption_track_path), "-i", str(SYMBOL),
         "-filter_complex", filt,
         "-map", "[outv]", "-map", "0:a?",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k",
         output_path])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input_video")
    ap.add_argument("output_video")
    ap.add_argument("--language", default=None, choices=["eng", "por", "spa", None],
                     help="ISO-ish hint; mapped to whisper 2-letter codes internally")
    ap.add_argument("--no-cut", action="store_true")
    ap.add_argument("--cut-threshold", type=float, default=0.6)
    ap.add_argument("--chunk-size", type=int, default=4)
    ap.add_argument("--font", choices=["serif", "sans"], default="sans")
    ap.add_argument("--accent", default=DEFAULT_ACCENT)
    ap.add_argument("--model", default="small")
    ap.add_argument("--keep-temp", action="store_true")
    args = ap.parse_args()

    lang_map = {"eng": "en", "por": "pt", "spa": "es", None: None}
    whisper_lang = lang_map[args.language]

    input_video = str(Path(args.input_video).resolve())
    output_video = str(Path(args.output_video).resolve())
    font_path = FONT_SANS if args.font == "sans" else FONT_SERIF
    font_family = {"sans": "Plus Jakarta Sans", "serif": "Playfair Display"}[args.font]

    tmp = Path(tempfile.mkdtemp(prefix="rarity_reel_"))
    print(f"[workdir] {tmp}")
    try:
        probe = ffprobe_json(input_video)
        duration = float(probe["format"]["duration"])
        audio_present = has_audio_stream(probe)
        if not audio_present:
            sys.exit("[error] input video has no audio track — nothing to transcribe/caption.")

        wav_path = tmp / "audio.wav"
        extract_audio(input_video, wav_path)

        words, detected_lang = transcribe(wav_path, whisper_lang, args.model)
        if not words:
            sys.exit("[error] transcription returned no words — check the audio track.")

        if args.no_cut:
            cuts = []
        else:
            cuts = compute_cuts(words, duration, args.cut_threshold)
        keeps = keep_segments_from_cuts(cuts, duration) if cuts else [(0.0, duration)]
        removed = sum(e - s for s, e in cuts)
        print(f"[cuts] {len(cuts)} gap(s) removed, {removed:.2f}s cut from {duration:.2f}s original")

        cut_path = tmp / "cut.mp4"
        cut_video(input_video, cut_path, keeps, audio_present)

        words_remapped = [
            {"start": remap_time(w["start"], cuts), "end": remap_time(w["end"], cuts), "text": w["text"]}
            for w in words
        ]

        cut_duration = sum(e - s for s, e in keeps)

        caps_dir = tmp / "caps"
        caps_dir.mkdir(exist_ok=True)
        caption_frames = build_caption_frames(words_remapped, font_path, args.accent, args.chunk_size, caps_dir)
        print(f"[captions] {len(caption_frames)} word-highlight frames rendered (font: {font_family})")
        caption_track = build_caption_track(caption_frames, cut_duration, caps_dir)

        final_pass(cut_path, caption_track, output_video)
        print(f"[done] -> {output_video}")
    finally:
        if args.keep_temp:
            print(f"[keep-temp] intermediates left at {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
