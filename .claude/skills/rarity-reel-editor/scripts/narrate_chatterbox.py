#!/usr/bin/env python3
"""
narrate_chatterbox.py — human-sounding narration from a script, fully local and free.

Uses Resemble AI's Chatterbox (MIT licence, open weights) — in Resemble's own blind listening
tests it was preferred over ElevenLabs, and it is far more natural than Edge/macOS `say` voices.
Runs on Apple Silicon via MPS. Each sentence is generated separately (so pacing, breath and
emphasis restart naturally at every sentence), silence-trimmed, and joined with human-length gaps.

Setup (once; ~3 GB of model weights are cached in ~/.cache/huggingface after the first run):
  /opt/homebrew/bin/python3.12 -m venv ~/.rarity-voice-venv
  ~/.rarity-voice-venv/bin/pip install chatterbox-tts soundfile librosa "setuptools<81"
  # (setuptools<81 is required: newer versions drop pkg_resources and the watermarker import dies
  #  with "TypeError: 'NoneType' object is not callable")

Usage (run with the venv's python, NOT the system python):
  ~/.rarity-voice-venv/bin/python narrate_chatterbox.py narration.txt narration.wav \
      [--exaggeration 0.55] [--cfg 0.45] [--temperature 0.75] [--voice-ref my_voice_10s.wav]

  --voice-ref   a clean 8-15 s recording of the voice to clone (use Caio's OWN voice, recorded by
                him — never someone else's). Without it Chatterbox uses its built-in male voice.
  --exaggeration  0.3 calm/neutral ... 0.7 animated. 0.5-0.6 is the sweet spot for punchy reels.
  --cfg          lower = faster/looser pacing, higher = more deliberate. 0.4-0.5 for reels.

Notes
  * Chatterbox embeds an inaudible Perth watermark in its output (AI-audio provenance). Fine for
    posting; just don't claim the voice is a human recording.
  * Output is mono 24 kHz float WAV. build_voiceover_reel.py masters it (EQ, compression, -16 LUFS).
  * After this, get script-exact word timings with align_words.py.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text_file")
    ap.add_argument("out_wav")
    ap.add_argument("--exaggeration", type=float, default=0.55)
    ap.add_argument("--cfg", type=float, default=0.45)
    ap.add_argument("--temperature", type=float, default=0.75)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--voice-ref", default=None)
    ap.add_argument("--gap-sentence", type=float, default=0.34, help="seconds of silence after a sentence")
    ap.add_argument("--gap-clause", type=float, default=0.20, help="after ?/! style short beats")
    args = ap.parse_args()

    import numpy as np
    import soundfile as sf
    import torch
    from chatterbox.tts import ChatterboxTTS

    text = Path(args.text_file).read_text().replace("\n", " ").strip()
    sentences = [s.strip() for s in re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", text) if s.strip()]
    dev = "mps" if torch.backends.mps.is_available() else "cpu"

    # Chatterbox checkpoints were saved on CUDA; load them to CPU first, then move to the device.
    _orig = torch.load
    torch.load = lambda *a, **k: _orig(*a, **{**k, "map_location": torch.device("cpu")})
    model = ChatterboxTTS.from_pretrained(device=dev)
    sr = model.sr

    pieces = []
    for i, s in enumerate(sentences):
        torch.manual_seed(args.seed + i)
        kw = dict(exaggeration=args.exaggeration, cfg_weight=args.cfg, temperature=args.temperature)
        if args.voice_ref:
            kw["audio_prompt_path"] = args.voice_ref
        wav = model.generate(s, **kw).squeeze().cpu().numpy()
        loud = np.where(np.abs(wav) > 0.01)[0]
        if len(loud):  # trim leading/trailing silence, keep a natural breath of room
            wav = wav[max(0, loud[0] - int(0.03 * sr)): loud[-1] + int(0.06 * sr)]
        pieces.append(wav)
        gap = args.gap_sentence if s.endswith(".") else args.gap_clause
        pieces.append(np.zeros(int(gap * sr), dtype=np.float32))
        print(f"[{i + 1}/{len(sentences)}] {len(wav) / sr:.2f}s  {s}", flush=True)

    audio = np.concatenate(pieces)
    sf.write(args.out_wav, audio, sr)
    print(f"[done] {len(audio) / sr:.2f}s -> {args.out_wav}")


if __name__ == "__main__":
    main()
