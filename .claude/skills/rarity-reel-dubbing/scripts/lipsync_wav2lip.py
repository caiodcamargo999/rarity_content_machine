#!/usr/bin/env python3
"""
lipsync_wav2lip.py — LOCAL lip-sync (fallback when Higgsfield's `dubbing` connector is not available).

Re-animates the mouth of a talking-head video so it matches a NEW audio track (e.g. the English dub
in the speaker's cloned voice). Uses Wav2Lip-GAN (Rudrabha/Wav2Lip, research licence — fine for
internal/company content, check the licence before commercial redistribution of the model itself).

Run with the dedicated venv (never the voice venv — numpy/protobuf pins clash):
  ~/.rarity-lipsync/venv/bin/python lipsync_wav2lip.py video.mp4 new_audio.wav out_silent.mp4
then mux the audio yourself (build_voiceover / edit_talking_head do this).

Setup (once):
  mkdir -p ~/.rarity-lipsync && cd ~/.rarity-lipsync
  git clone https://github.com/Rudrabha/Wav2Lip.git
  mkdir -p ckpt && curl -L -o ckpt/wav2lip_gan.pth \
      https://huggingface.co/numz/wav2lip_studio/resolve/main/Wav2lip/wav2lip_gan.pth
  /opt/homebrew/bin/python3.12 -m venv venv
  ./venv/bin/pip install "numpy<2" torch torchvision "opencv-python-headless<4.11" \
      "mediapipe==0.10.14" librosa==0.10.2.post1 numba tqdm scipy soundfile

Quality notes (be honest with Caio):
  * Wav2Lip predicts a 96x96 mouth/face patch. Run it on the NATIVE-resolution video (before any
    upscale) so the patch is as sharp as the surrounding frame, then upscale the whole frame.
  * It is a research model: expect a slightly soft mouth and occasional teeth/lip flicker on fast
    speech, big head turns or hands crossing the face. Higgsfield `dubbing` (or LatentSync/MuseTalk on
    a CUDA box) is visibly better; use it whenever the connector is reachable.
  * Mouth region is blended with a feathered mask + colour match so there is no visible box.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(os.environ.get("WAV2LIP_DIR", Path.home() / ".rarity-lipsync" / "Wav2Lip"))
CKPT = Path(os.environ.get("WAV2LIP_CKPT", Path.home() / ".rarity-lipsync" / "ckpt" / "wav2lip_gan.pth"))
sys.path.insert(0, str(REPO))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402

import audio  # noqa: E402  (Wav2Lip's)
from models import Wav2Lip  # noqa: E402


def load_model(device):
    m = Wav2Lip()
    ck = torch.load(str(CKPT), map_location="cpu")
    sd = {k.replace("module.", ""): v for k, v in ck["state_dict"].items()}
    m.load_state_dict(sd)
    return m.to(device).eval()


def detect_boxes(frames):
    """Per-frame face box (x1,y1,x2,y2) via MediaPipe, expanded to include chin, temporally smoothed."""
    import mediapipe as mp
    fd = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    boxes, last = [], None
    for fr in frames:
        h, w = fr.shape[:2]
        res = fd.process(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
        if res.detections:
            bb = max(res.detections, key=lambda d: d.score[0]).location_data.relative_bounding_box
            x1, y1 = bb.xmin * w, bb.ymin * h
            x2, y2 = x1 + bb.width * w, y1 + bb.height * h
            bw, bh = x2 - x1, y2 - y1
            last = [x1 - 0.06 * bw, y1 - 0.02 * bh, x2 + 0.06 * bw, y2 + 0.16 * bh]
        boxes.append(list(last) if last else None)
    # fill leading gaps, then smooth (moving average, 7 frames)
    first = next((b for b in boxes if b), None)
    if first is None:
        sys.exit("[lipsync] no face found in the video")
    boxes = [b or first for b in boxes]
    arr = np.array(boxes, dtype=np.float32)
    k = 7
    pad = np.pad(arr, ((k // 2, k // 2), (0, 0)), mode="edge")
    sm = np.stack([pad[i:i + len(arr)] for i in range(k)]).mean(axis=0)
    out = []
    for b, (h, w) in zip(sm, [f.shape[:2] for f in frames]):
        x1, y1, x2, y2 = int(max(0, b[0])), int(max(0, b[1])), int(min(w, b[2])), int(min(h, b[3]))
        out.append((x1, y1, x2, y2))
    return out


def feather_mask(h, w, top=0.56, bottom=0.86, left=0.22, right=0.78):
    """soft mask over the MOUTH only (lips + a little chin), not the whole lower face: blending the
    full lower half warped the moustache/goatee in testing. Defaults are fractions of the face box."""
    m = np.zeros((h, w), np.float32)
    m[int(h * top):int(h * bottom), int(w * left):int(w * right)] = 1.0
    k = max(3, int(min(h, w) * 0.10) | 1)
    return cv2.GaussianBlur(m, (k, k), 0)[..., None]


def color_match(pred, ref, mask, chroma=0.65):
    """Match the generated mouth patch to the surrounding frame in LAB space: full-strength on the
    chroma channels' MEAN (kills the purple/magenta cast the GAN gives an open mouth), partial on
    lightness, std-ratio clamped so contrast is never amplified."""
    p8 = np.clip(pred, 0, 255).astype(np.uint8)
    r8 = np.clip(ref, 0, 255).astype(np.uint8)
    pl = cv2.cvtColor(p8, cv2.COLOR_BGR2LAB).astype(np.float32)
    rl = cv2.cvtColor(r8, cv2.COLOR_BGR2LAB).astype(np.float32)
    wsum = mask.sum() + 1e-6
    out = pl.copy()
    for c, strength in ((0, 0.35), (1, chroma), (2, chroma)):
        mp_ = (pl[..., c] * mask[..., 0]).sum() / wsum
        mr_ = (rl[..., c] * mask[..., 0]).sum() / wsum
        out[..., c] = pl[..., c] + (mr_ - mp_) * strength
        if c > 0:   # keep chroma spread no wider than the real face's
            sp = np.sqrt(((pl[..., c] - mp_) ** 2 * mask[..., 0]).sum() / wsum) + 1e-6
            sr = np.sqrt(((rl[..., c] - mr_) ** 2 * mask[..., 0]).sum() / wsum) + 1e-6
            k = min(1.0, max(0.55, sr / sp * 1.6))
            out[..., c] = (out[..., c] - out[..., c].mean()) * k + out[..., c].mean()
    return cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("audio_wav")
    ap.add_argument("out_video")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--sharpen", type=float, default=0.9, help="unsharp amount on the generated mouth patch")
    args = ap.parse_args()

    device = "mps" if torch.backends.mps.is_available() else "cpu"
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        frames.append(fr)
    cap.release()
    H, W = frames[0].shape[:2]
    print(f"[lipsync] {len(frames)} frames {W}x{H} @ {fps:.2f}fps, device={device}")

    wav = audio.load_wav(args.audio_wav, 16000)
    mel = audio.melspectrogram(wav)
    step, idx, mels = 80.0 / fps, 0, []
    while True:
        s = int(idx * step)
        if s + 16 > mel.shape[1]:
            mels.append(mel[:, mel.shape[1] - 16:])
            break
        mels.append(mel[:, s:s + 16])
        idx += 1
    n = min(len(frames), len(mels))
    frames, mels = frames[:n], mels[:n]
    print(f"[lipsync] audio -> {len(mels)} mel chunks; using {n} frames")

    boxes = detect_boxes(frames)
    model = load_model(device)

    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps:.4f}", "-i", "-",
         "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", args.out_video],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    for b0 in range(0, n, args.batch):
        idxs = list(range(b0, min(n, b0 + args.batch)))
        imgs, ms = [], []
        for i in idxs:
            x1, y1, x2, y2 = boxes[i]
            face = cv2.resize(frames[i][y1:y2, x1:x2], (96, 96))
            imgs.append(face)
            ms.append(mels[i])
        img_np = np.asarray(imgs, dtype=np.float32)
        masked = img_np.copy()
        masked[:, 48:] = 0
        inp = np.concatenate((masked, img_np), axis=3) / 255.0
        inp = torch.from_numpy(inp.transpose(0, 3, 1, 2)).float().to(device)
        mel_t = torch.from_numpy(np.asarray(ms, dtype=np.float32)[:, None]).float().to(device)
        with torch.no_grad():
            pred = model(mel_t, inp).cpu().numpy().transpose(0, 2, 3, 1) * 255.0
        for j, i in enumerate(idxs):
            x1, y1, x2, y2 = boxes[i]
            bw, bh = x2 - x1, y2 - y1
            patch = cv2.resize(pred[j], (bw, bh), interpolation=cv2.INTER_CUBIC)
            if args.sharpen > 0:
                blur = cv2.GaussianBlur(patch, (0, 0), 1.2)
                patch = np.clip(patch + args.sharpen * (patch - blur), 0, 255)
            ref = frames[i][y1:y2, x1:x2].astype(np.float32)
            mask = feather_mask(bh, bw)
            patch = color_match(patch, ref, mask)
            blended = ref * (1 - mask) + patch * mask
            out = frames[i].copy()
            out[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
            enc.stdin.write(out.tobytes())
        print(f"[lipsync] {idxs[-1] + 1}/{n}", flush=True)
    enc.stdin.close()
    enc.wait()
    print(f"[lipsync] done -> {args.out_video}")


if __name__ == "__main__":
    main()
