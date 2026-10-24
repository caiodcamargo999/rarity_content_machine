#!/usr/bin/env python3
"""
transcribe_two_models.py — step 1 of every talking-head edit (VSL, Reel, ad): word timings from TWO whisper models.

  python3 transcribe_two_models.py video.mp4 OUTDIR [--language en] [--prompt "extra glossary words"]

Writes OUTDIR/words_L.json + tr_L.txt (large-v3) and words_M.json + tr_M.txt (medium.en for English, medium otherwise).
Read both transcripts side by side, write the corrected script (script.txt), and run align_to_script.py.
Use the system python3 (it has faster-whisper); the voice venv does not.
"""
import argparse
import json
import subprocess
import wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
GLOSSARY = ("Rarity is a performance marketing agency for DTC ecommerce brands. Terms: ROAS, CAC, MER, LTV, P&L, Meta ads, "
            "Google ads, TikTok, Klaviyo, Shopify, creative testing, hooks, UGC, contribution margin, maximum allowable CAC, "
            "profit diagnostic, growth audit, one number, profit, scale, DTC, Caio.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--language", default="en")
    ap.add_argument("--prompt", default="")
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    wav = out / "v16.wav"
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", args.video, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)], check=True)
    with wave.open(str(wav), "rb") as wf:
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    second = "medium.en" if args.language == "en" else "medium"
    for name, tag in (("large-v3", "L"), (second, "M")):
        m = WhisperModel(name, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(audio, word_timestamps=True, language=args.language, beam_size=5,
                               initial_prompt=(GLOSSARY + " " + args.prompt).strip(), condition_on_previous_text=False)
        words, lines = [], []
        for s in segs:
            lines.append(f"{s.start:7.2f}-{s.end:7.2f}  {s.text.strip()}")
            words += [{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for w in (s.words or []) if w.word.strip()]
        (out / f"words_{tag}.json").write_text(json.dumps(words, indent=1))
        (out / f"tr_{tag}.txt").write_text("\n".join(lines))
        print(f"[{name}] {len(words)} words")


if __name__ == "__main__":
    main()
