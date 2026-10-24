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
  --chunk-size 3              Max words per caption chunk (default 3; also breaks at punctuation)
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


CAPTION_MAX_W = int(OUT_W * 0.88)
CAPTION_BASE_SIZE = 112          # ONE fixed size for the whole video (never shrinks/grows)
CAPTION_MIN_SIZE = 60
CAPTION_BASELINE_Y = 1290        # px from TOP of the 1920 frame: lower-middle, above IG's
                                 # bottom UI (~y>1560) and clear of the right-hand button rail
CAPTION_MAX_WORDS = 3            # chunk size; also breaks at punctuation (see chunk_words)
CAPTION_STROKE = 9               # dark outline px
CAPTION_ACTIVE_SCALE = 1.0       # active word is NOT resized — only recoloured
CAPTION_POP_SCALES = (1.26, 1.16)  # 2-frame "pop" overshoot when a word lands


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


_PUNCT_BREAK = (".", ",", "!", "?", ";", ":", "\u2014", "-")


def chunk_words(words, max_words=CAPTION_MAX_WORDS, font=None, max_width=None):
    """Group words into caption chunks of up to `max_words`. A chunk ALWAYS ends at
    sentence/clause punctuation (a phrase never straddles two captions) and, when `font` and
    `max_width` are given, never gets wider than the safe width at the FIXED caption size —
    which is what lets every caption in the video share one font size."""
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8))) if font else None

    def width(ws):
        txt = " ".join(caption_text(w["text"]) for w in ws)
        return probe.textlength(txt, font=font) + CAPTION_STROKE * 2 * len(ws)

    chunks, cur = [], []
    for w in words:
        if cur and font and width(cur + [w]) > max_width:
            chunks.append(cur)
            cur = []
        cur.append(w)
        t = w["text"].rstrip()
        if len(cur) >= max_words or (t and t[-1] in _PUNCT_BREAK and t[-1] != "-"):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def caption_text(raw):
    """Display form: UPPERCASE with sentence punctuation stripped (viral-caption look).
    Keeps ? and ! and apostrophes/hyphens inside words."""
    return raw.strip().strip(".,;:\u2014").upper()


def render_caption_frame(chunk_words_, highlight_idx, font, accent_rgb, out_path, active_scale=CAPTION_ACTIVE_SCALE):
    """One transparent 1080x1920 PNG: the chunk in white with a heavy dark outline + soft
    drop shadow, the word being spoken in the brand accent colour and scaled up so it visibly
    'pops'. The layout is computed ONCE with the active word at its settled size, so the words
    never collide and nothing jitters sideways between frames; pop frames just draw the active
    word bigger around its own centre."""
    from PIL import ImageFilter
    texts = [caption_text(w["text"]) for w in chunk_words_]
    settled = ImageFont.truetype(font.path, int(round(font.size * CAPTION_ACTIVE_SCALE)))
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    gap = font.size * 0.30 + CAPTION_STROKE
    # slot width per word = width at its largest drawn state (settled size if active)
    widths = [probe.textlength(t, font=font) for t in texts]
    slot = [probe.textlength(t, font=settled) if i == highlight_idx else widths[i] for i, t in enumerate(texts)]
    total_w = sum(slot) + gap * max(0, len(texts) - 1)
    x = (OUT_W - total_w) / 2

    shadow = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    img = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    sd, d = ImageDraw.Draw(shadow), ImageDraw.Draw(img)
    for i, t in enumerate(texts):
        active = i == highlight_idx
        if active:
            f = ImageFont.truetype(font.path, int(round(font.size * active_scale)))
            fw = d.textlength(t, font=f)
            fx = x + (slot[i] - fw) / 2
            y = CAPTION_BASELINE_Y - int((f.size - font.size) * 0.5)
            color = accent_rgb
        else:
            f, fw = font, widths[i]
            fx = x + (slot[i] - fw) / 2
            y, color = CAPTION_BASELINE_Y, (255, 255, 255)
        sd.text((fx, y + 10), t, font=f, fill=(0, 0, 0, 200), stroke_width=CAPTION_STROKE + 2, stroke_fill=(0, 0, 0, 200))
        d.text((fx, y), t, font=f, fill=color + (255,), stroke_width=CAPTION_STROKE, stroke_fill=(8, 8, 8, 255))
        x += slot[i] + gap
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    Image.alpha_composite(shadow, img).save(out_path)


def build_caption_frames(words_remapped, font_path, accent_hex, chunk_size, out_dir, pop=False, style="minimal"):
    """Builds the caption PNGs and returns [(png_path, start, end, min_frames), ...].

    ONE font size (CAPTION_BASE_SIZE) for the entire video — chunks are re-split by width so
    they always fit at that size instead of shrinking the font (Caio, 2026-10: "keep the
    subtitles the same size always"). The active word only changes COLOUR (magenta); it is not
    scaled, and by default there is no pop animation (pop=True re-enables a size overshoot)."""
    if style == "minimal":
        return build_caption_frames_minimal(words_remapped, accent_hex, out_dir)
    accent_rgb = hx(accent_hex)
    font = ImageFont.truetype(str(font_path), CAPTION_BASE_SIZE)
    chunks = chunk_words(words_remapped, min(chunk_size, CAPTION_MAX_WORDS) if chunk_size else CAPTION_MAX_WORDS,
                         font=font, max_width=CAPTION_MAX_W)
    frames = []
    for ci, chunk in enumerate(chunks):
        for wi, w in enumerate(chunk):
            if w["end"] <= w["start"]:
                continue
            steady = out_dir / f"cap_{ci:04d}_{wi:02d}.png"
            render_caption_frame(chunk, wi, font, accent_rgb, steady)
            if pop:
                two_f = 2 / 30.0
                p1 = out_dir / f"cap_{ci:04d}_{wi:02d}_p1.png"
                p2 = out_dir / f"cap_{ci:04d}_{wi:02d}_p2.png"
                render_caption_frame(chunk, wi, font, accent_rgb, p1, CAPTION_POP_SCALES[0])
                render_caption_frame(chunk, wi, font, accent_rgb, p2, CAPTION_POP_SCALES[1])
                frames.append((p1, w["start"], w["start"] + two_f, 2))
                frames.append((p2, w["start"] + two_f, w["start"] + 2 * two_f, 2))
                frames.append((steady, w["start"] + 2 * two_f, max(w["end"], w["start"] + 2 * two_f + 1 / 30.0), 3))
            else:
                frames.append((steady, w["start"], w["end"], 4))
    return frames


# ----------------------------------------------------------------------------------------------
# MINIMAL caption style (default since 2026-10; Caio: captions were "too animated", wanted
# "a little bit the font of Rarity, but more minimalist"):
#   * whole PHRASE shown at once (no word-by-word flipping, no size changes, no pop, no stroke)
#   * BentonSans Regular — Rarity's body typeface — off-white (#efeeea), sentence case, soft shadow
#   * ONE key word per phrase in Playfair Display Bold Italic + Rarity magenta (the same
#     "italic accent word" device as the IG posts); static for the whole phrase
#   * phrases appear/disappear with a ~0.1 s opacity fade, nothing else moves
#   * fixed size for the whole video
# ----------------------------------------------------------------------------------------------
FONT_BENTON = FONTS_DIR / "BentonSans-Regular.otf"
FONT_ACCENT = FONTS_DIR / "headline-italic.ttf"      # Playfair Display Bold Italic
MIN_SIZE = 74                  # px, fixed for the entire video
MIN_ACCENT_SCALE = 1.10        # Playfair's x-height is smaller; optically match Benton
MIN_MAX_W = int(OUT_W * 0.90)  # single line, generous side margins
MIN_BASELINE_Y = 1330
MIN_MAX_WORDS = 7
MIN_TEXT_RGB = (239, 238, 234)   # brand "primary_offwhite" #efeeea
_NUM_WORDS = {"um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "vinte", "trinta",
              "quarenta", "cinquenta", "noventa", "cem", "mil", "milhão", "milhões", "bilhão", "bilhões",
              "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
              "twelve", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety",
              "hundred", "thousand", "million", "billion", "trillion", "percent", "first", "second",
              "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"}


_STOP = {"the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "for", "with", "from", "by",
         "as", "is", "are", "was", "were", "be", "will", "that", "this", "these", "those", "their", "theirs",
         "they", "it", "its", "your", "you", "you're", "we", "our", "if", "so", "up", "not", "because", "than",
         "then", "same", "now", "right", "run", "runs", "says", "itself", "just", "very", "all", "any",
         "that's", "it's", "doesn't", "isn't", "you're", "here's", "what", "why", "how", "but", "so", "well", "we'll", "we're",
         "your", "our", "us", "me", "my", "have", "has", "had", "do", "does", "did", "can", "could", "would", "should",
         "about", "into", "than", "when", "while", "who", "which", "there", "their", "them", "these", "those",
         # Portuguese / Spanish filler
         "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
         "por", "pra", "pro", "para", "com", "que", "e", "é", "ou", "se", "seu", "sua", "seus", "suas", "te",
         "tua", "teu", "mais", "mesma", "mesmo", "esse", "essa", "isso", "aí", "sabe", "quando", "como",
         "já", "não", "ao", "à", "pelo", "pela", "você", "vocês", "eles", "elas", "gente", "tá", "está",
         "são", "ser", "ter", "vai", "foi", "tem", "ele", "ela", "nós", "eu", "me", "lhe", "isto", "aquilo",
         "toda", "todo", "todos", "todas", "muito", "pouco", "só", "também", "então", "porque", "porém",
         "el", "la", "los", "las", "un", "una", "del", "al", "con", "por", "para", "su", "sus", "es", "y"}


def _clean(raw):
    """Display text of a token: drop trailing . , ; : (keep ? ! and inner punctuation)."""
    return raw.strip().rstrip(".,;:\u2014")


def pick_key_word(tokens):
    """Index of the word to accent. Explicit {'key': True} on a word wins; otherwise score:
    digits/%/$ > number words > capitalised non-initial word (names, days, months) > longest."""
    for i, t in enumerate(tokens):
        if isinstance(t, dict) and t.get("key"):
            return i
    best, best_s = 0, -1.0
    for i, t in enumerate(tokens):
        w = _clean(t["text"] if isinstance(t, dict) else t)
        core = "".join(ch for ch in w.lower() if ch.isalnum() or ch == "-")
        score = len(core) / 40.0 - (5 if core in _STOP else 0)
        if any(ch.isdigit() for ch in w) or "%" in w or "$" in w:
            score += 6
        elif any(part in _NUM_WORDS for part in core.split("-")):
            score += 4
        elif len(w) >= 2 and w.isalpha() and w.isupper():
            score += 4            # acronyms: ROAS, CAC, DRE, LTV...
        elif i > 0 and w[:1].isupper():
            score += 3
        if score > best_s:
            best, best_s = i, score
    return best if best_s >= 0 else -1      # a phrase made only of filler words gets no accent


def minimal_phrases(words):
    """Group words into single-line phrases: break at sentence/clause punctuation, at
    MIN_MAX_WORDS, or when the line would exceed MIN_MAX_W at the fixed size."""
    body = ImageFont.truetype(str(FONT_BENTON), MIN_SIZE)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

    def line_w(ws):
        return sum(probe.textlength(_clean(w["text"]), font=body) for w in ws) + \
            probe.textlength(" ", font=body) * (len(ws) - 1)

    # 1) clauses: always end at sentence / clause punctuation
    clauses, cur = [], []
    for w in words:
        cur.append(w)
        t = w["text"].rstrip()
        if t and t[-1] in ".,;:!?\u2014":
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)

    # 2) a clause that is too wide (or too long) is split into BALANCED parts \u2014 never an orphan
    #    last word ("...sixth and / seventh") \u2014 by cutting at the word boundary nearest the middle
    def fits(ws):
        return len(ws) <= MIN_MAX_WORDS and line_w(ws) * 1.04 <= MIN_MAX_W

    def split(ws):
        if fits(ws) or len(ws) < 2:
            return [ws]
        total = line_w(ws)
        best_i, best_gap = 1, 1e9
        for i in range(1, len(ws)):
            gap = abs(line_w(ws[:i]) - total / 2)
            if gap < best_gap:
                best_i, best_gap = i, gap
        return split(ws[:best_i]) + split(ws[best_i:])

    phrases = []
    for c in clauses:
        phrases.extend(split(c))
    return phrases


def legible_accent(rgb, mix=0.30):
    """Brand magenta lightened toward white so the italic key word keeps contrast on dark footage
    (pure #D50057 sinks into navy/black scenes). Same hue family, so the palette stays on-brand."""
    return tuple(int(round(c + (255 - c) * mix)) for c in rgb)


def render_minimal_phrase(phrase, key_idx, accent_rgb, out_path, alpha=1.0):
    from PIL import ImageFilter
    body = ImageFont.truetype(str(FONT_BENTON), MIN_SIZE)
    acc = ImageFont.truetype(str(FONT_ACCENT), int(round(MIN_SIZE * MIN_ACCENT_SCALE)))
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    texts = [_clean(w["text"]) for w in phrase]
    # Playfair's old-style numerals read as "9o" — numeric key words keep Benton (still magenta)
    fonts = [(body if any(ch.isdigit() for ch in texts[i]) else acc) if i == key_idx else body
             for i in range(len(texts))]
    space = probe.textlength(" ", font=body)
    widths = [probe.textlength(t, font=f) for t, f in zip(texts, fonts)]
    total = sum(widths) + space * (len(texts) - 1)
    x = (OUT_W - total) / 2
    layer = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    d, sd = ImageDraw.Draw(layer), ImageDraw.Draw(shadow)
    # very soft dark halo behind the line (no hard edge, no box): keeps the text readable on white
    # tables / calendars / sunlit shots while the caption still looks like bare type
    halo = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    ImageDraw.Draw(halo).rounded_rectangle(
        (x - 70, MIN_BASELINE_Y - MIN_SIZE * 1.15, x + total + 70, MIN_BASELINE_Y + MIN_SIZE * 0.55),
        radius=60, fill=(10, 6, 20, 150))
    halo = halo.filter(ImageFilter.GaussianBlur(44))
    accent_rgb = legible_accent(accent_rgb)
    for i, (t, f, w) in enumerate(zip(texts, fonts, widths)):
        col = accent_rgb if i == key_idx else MIN_TEXT_RGB
        sd.text((x, MIN_BASELINE_Y + 4), t, font=f, fill=(0, 0, 0, 215), anchor="ls")
        d.text((x, MIN_BASELINE_Y), t, font=f, fill=col + (255,), anchor="ls")
        x += w + space
    shadow = shadow.filter(ImageFilter.GaussianBlur(7))
    img = Image.alpha_composite(Image.alpha_composite(halo, shadow), layer)
    if alpha < 1.0:
        a = img.getchannel("A").point(lambda v: int(v * alpha))
        img.putalpha(a)
    img.save(out_path)


def build_caption_frames_minimal(words, accent_hex, out_dir):
    accent_rgb = hx(accent_hex)
    phrases = minimal_phrases(words)
    FADE_IN = (0.35, 0.7)        # two 2-frame steps (~0.13 s total) before full opacity
    frames = []
    for pi, ph in enumerate(phrases):
        key = pick_key_word(ph)
        start, end = ph[0]["start"], ph[-1]["end"]
        nxt_start = phrases[pi + 1][0]["start"] if pi + 1 < len(phrases) else None
        full = out_dir / f"ph_{pi:03d}_full.png"
        render_minimal_phrase(ph, key, accent_rgb, full)
        t = start
        for k, a in enumerate(FADE_IN):
            f = out_dir / f"ph_{pi:03d}_in{k}.png"
            render_minimal_phrase(ph, key, accent_rgb, f, alpha=a)
            frames.append((f, t, t + 2 / 30.0, 2))
            t += 2 / 30.0
        hold_end = max(end, t + 0.2)
        frames.append((full, t, hold_end, 4))
        if nxt_start is None or nxt_start - hold_end > 0.25:
            f = out_dir / f"ph_{pi:03d}_out.png"
            render_minimal_phrase(ph, key, accent_rgb, f, alpha=0.4)
            frames.append((f, hold_end, hold_end + 2 / 30.0, 2))
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

    # Frame-quantize every caption window. With raw float durations, very short words ("the",
    # "are", "you're", ~0.07-0.12s) came out at 0-2 frames and vanished from the track (found by
    # the every-word QA gate, 2026-10). So: (1) snap to integer frames, (2) bridge tiny gaps
    # between neighbouring words so the chunk doesn't flicker off, (3) give every word at least
    # MIN_FRAMES by pushing the next word's start later (total timeline length is unchanged).
    BRIDGE_FRAMES = 6  # gaps up to 0.2s between words are bridged (keeps the phrase on screen)
    total_frames = int(round(total_duration * fps))
    wins = []
    for item in caption_frames:
        png_path, start, end = item[0], item[1], item[2]
        min_f = item[3] if len(item) > 3 else 4
        sf = int(round(start * fps))
        ef = max(int(round(end * fps)), sf + 1)
        wins.append([png_path, sf, ef, min_f])
    prev_end = 0
    for i, w in enumerate(wins):
        if w[1] < prev_end:
            w[1] = prev_end
        if i + 1 < len(wins):
            gap = wins[i + 1][1] - w[2]
            if 0 < gap <= BRIDGE_FRAMES:
                w[2] = wins[i + 1][1]
        w[2] = max(w[2], w[1] + w[3])
        prev_end = w[2]
    entries = []  # (png_path, duration)
    cursor = 0
    for png_path, sf, ef, _mf in wins:
        if sf > cursor:
            entries.append((blank_path, (sf - cursor) / fps))
        entries.append((png_path, (ef - sf) / fps))
        cursor = ef
    if total_frames > cursor:
        entries.append((blank_path, (total_frames - cursor) / fps))
    if not entries:
        entries.append((blank_path, total_duration))

    concat_list = out_dir / "caption_concat.txt"
    lines = []
    for png_path, dur in entries:
        lines.append(f"file '{png_path}'\nduration {dur:.5f}\n")
    lines.append(f"file '{entries[-1][0]}'\n")  # concat demuxer quirk: repeat last file, no duration
    concat_list.write_text("".join(lines))

    track_path = out_dir / "caption_track.mov"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
         "-r", str(fps), "-fps_mode", "cfr", "-c:v", "qtrle", str(track_path)])
    return track_path


def final_pass(cut_video_path, caption_track_path, output_path, grade="eq=contrast=1.06:saturation=1.08:brightness=0.01"):
    """Scale/crop to 9:16, apply a light brand colour treatment, overlay the single
    pre-rendered caption track, then stamp the transparent Rarity symbol top-right —
    always exactly 3 inputs, regardless of script length (see build_caption_track)."""
    filt = (
        f"[0:v]scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase,"
        f"crop={OUT_W}:{OUT_H}{',' + grade if grade else ''}[v0];"
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
    ap.add_argument("--chunk-size", type=int, default=3)
    ap.add_argument("--caption-style", choices=["minimal", "bold"], default="minimal")
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
        caption_frames = build_caption_frames(words_remapped, font_path, args.accent, args.chunk_size, caps_dir, style=args.caption_style)
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
