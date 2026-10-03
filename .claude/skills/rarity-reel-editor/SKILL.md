---
name: rarity-reel-editor
description: "Step 3 of Caio's personal video pipeline — takes either (a) a raw recorded video or (b) a narration track + a list of B-roll clips/images per sentence, and produces a finished, cut, color-treated, captioned, branded vertical Reel (1080x1920). Animated word-highlight captions in Rarity's brand font + magenta accent, Rarity logo overlay, and (for the voiceover format) dynamic crossfade transitions between scenes. ALWAYS use when Caio wants raw footage turned into a finished Reel, or wants a voiceover-style video built from B-roll clips synced to narration — 'corta e edita esse vídeo', 'bota legenda nesse Reels', 'monta um vídeo com essas imagens/clipes e essa narração'. When in doubt, USE this skill."
---

# Rarity Reel Editor (Step 3 of the personal video pipeline)

Takes video that already has a voice track (Caio's own recording, or a narration track paired with
B-roll) and turns it into a finished, postable vertical Reel — cut, color-treated, captioned, and
branded. This is the step after `rarity-reel-scripts` (the words) and, for formats with a face on
camera, `rarity-reel-dubbing` (translating Caio's own recorded voice into other languages); it never
writes scripts or dubs voices itself.

Two formats, two scripts, same caption/branding engine underneath:

1. **`scripts/edit_reel.py`** — raw footage format. Input: one video file with Caio talking
   (direct-to-camera, podcast clip, street interview). Transcribes it, auto-cuts dead air, color
   grades, captions, brands.
2. **`scripts/build_voiceover_reel.py`** — voiceover + B-roll format. Input: a narration audio track
   (Caio's own voice, or a synthetic placeholder for a demo) plus an ordered list of
   `{video or image, text}` scenes. Each scene is shown for exactly as long as its sentence takes to
   say (aligned via real transcription, not a guessed split), with a slow push-in zoom, joined to the
   next scene with a dynamic crossfade. Prefer real video clips over static images — real motion
   reads as dramatically more realistic and "viral" than a Ken-Burns pan on a photo (confirmed with
   Caio, 2026-10: he explicitly called a photo-based version "not realistic" and asked for real clips).

Both scripts end by calling the same three shared functions in `edit_reel.py`:
`build_caption_frames` → `build_caption_track` → `final_pass`. Fix a caption/branding bug once, in
one place, and both formats inherit the fix.

## Non-negotiables (several of these are lessons from real failures — read before changing the code)

1. **Captions are ONE pre-baked video track, never a chain of per-word overlay filters.** The first
   version of `build_voiceover_reel.py` composited each word's caption PNG directly onto the main
   video with its own `overlay=...:enable='between(t,...)'` filter, chained one after another — for a
   ~20s script that's 50+ simultaneous `-i` inputs in one `filter_complex`. It silently stopped
   compositing partway through the video (captions just vanished for the second half, no ffmpeg
   error, no warning) — almost certainly a resource/stream-count ceiling in a single filtergraph with
   that many inputs. Confirmed and fixed 2026-10: `build_caption_track()` now bakes every caption PNG
   plus fully-transparent filler (for the natural pauses between words/sentences) into ONE
   alpha-channel `.mov` (via the concat demuxer's per-file `duration` directive, `qtrle` codec), so
   the final composite in `final_pass()` only ever has 3 inputs (video, caption track, logo)
   regardless of script length. **Never go back to per-word chained overlays** — if a caption bug
   shows up again, suspect `build_caption_track`/`final_pass` first, not the chaining approach.
2. **Scene transitions (voiceover format) use a rotating set of dynamic crossfades, not hard cuts.**
   Caio explicitly asked for this (2026-10): "eu gostaria que as transições fossem um pouco mais
   dinâmicas." `build_voiceover_reel.py` joins consecutive scene clips with ffmpeg's `xfade` filter,
   cycling through `TRANSITION_STYLES` (zoomin, slideleft, wiperight, slideup, smoothleft) so a
   multi-scene video doesn't repeat the same cut every time. To make room for the overlap without
   drifting the total video out of sync with the narration audio, each scene's visible slot is
   shrunk by a few hundred ms (split evenly across all scenes, see `plan_transitions()`) — this is
   invisible in practice, and caption timing is completely unaffected since captions key off the
   narration's own absolute word timestamps, never off scene boundaries.
3. **Narration for a synthetic/demo voice: use the ElevenLabs voice via Higgsfield's `generate_audio`
   (`model: text2speech_v2`, `variant: elevenlabs`), not macOS `say`.** Caio's exact words (2026-10):
   "can you turn the voice more human and not too robotic" — `say` was tried first and rejected as
   robotic. Use `list_voices` to pick a preset (`voice_type: "preset"`), pass the full script text in
   one `prompt`, download the result, use it as `--narration`. Cost is trivial (~1 credit for a
   20-30s script). **Check `balance` before generating** — if credits are insufficient (this has
   happened), say so plainly to Caio rather than silently downgrading; only fall back to `say` as a
   visibly-flagged, temporary stand-in, and tell him the pipeline supports swapping in a proper
   ElevenLabs track later with zero other changes (just re-run with a different `--narration` file).
   For Caio's own real content (not a demo), the actual narration is his own recorded voice — `say`
   and ElevenLabs are demo/placeholder tools only.
4. **B-roll clips must be thematically congruent with the sentence they're paired with, not just the
   closest keyword match.** Caio caught this directly (2026-10): a scene narrating "every number on
   this dashboard is a decision" was paired with a forex/crypto trading-screen stock video because
   that's what surfaced for "dashboard" — he called it out immediately ("eu tenho negócio de trade,
   nada a ver"). Watch the actual clip before using it, not just the search snippet/description.
   When no honestly-matching real clip exists for a line, it's better to rewrite the line to fit real
   available, congruent footage (e.g. "dashboard" → "checkout" when a real checkout/payment clip was
   available and a real dashboard clip wasn't) than to force a mismatched visual.
5. **B-roll sourcing discipline — same bar as the `rarity-ig-*` pipeline.** Real, specific,
   rights-traceable, free for commercial use. Pexels is the default source — its license is
   unambiguously free for commercial use (confirmed via
   `help.pexels.com/.../Can-I-use-the-photos-and-videos-for-a-commercial-project`), with no
   attribution required. To get a direct, no-API-key-needed mp4 URL for a given Pexels video page,
   use the download redirect: `https://www.pexels.com/download/video/<id>/` (redirects straight to
   the best-quality file — confirmed working via `curl -sIL`). **Avoid Mixkit items under the
   "Mixkit Restricted License"** (shown on the item's own page) — that license is personal-use-only
   and Rarity's work is commercial; only Mixkit's plain "Mixkit Stock Video Free License" items are
   safe to use commercially, and even then Pexels is preferred since every item there is unambiguously
   commercial-clear. Never use Shutterstock/Getty/Adobe Stock or other paid agencies.
6. **Captions must have zero errors — this is a hard gate, not a nice-to-have.** Caio's exact words
   (2026-10): "as legendas não pode ter nenhum erro." Before calling any render done:
   - Sample frames at regular intervals across the **entire** duration (not just the first few
     seconds — the caption-dropout bug in Non-negotiable 1 was invisible in early-frame spot checks
     and only showed up once frames late in the video were checked). A reasonable sampling cadence is
     one frame every 2-3 seconds of final output.
   - At every sampled timestamp that falls inside a spoken word's window, confirm a caption is
     actually on screen, legible (not cut off, not overlapping the logo), and shows the **correct**
     word highlighted in magenta for that exact instant — not a neighboring word, not stale text from
     the previous chunk.
   - If any sampled frame fails this, do not ship — find the cause (see Non-negotiable 1 for the known
     failure mode) and re-render before showing the result to Caio.
7. **B-roll must be very congruent with what's being said, not just thematically adjacent.** Caio's
   exact words (2026-10): "os takes de video devem ser muito congruentes com o que é falado." This
   means watching the actual candidate clip (not just reading its title/description) and asking "if
   Caio watched this exact clip while hearing this exact sentence, would it look intentional, or would
   it look like stock footage that happened to share a keyword?" A forex/crypto trading screen for a
   line about "numbers on a dashboard" fails this test even though "dashboard" and "financial chart"
   are keyword-adjacent — see Non-negotiable 4 for the real incident. When no clip clears this bar,
   either keep searching (try different phrasing, different source) or adjust the sentence to fit a
   clip that genuinely does — never ship the mismatch.

## Workflow A — raw footage (`edit_reel.py`)

```
python3 edit_reel.py <input_video> <output_video> [options]
```
Pipeline: transcribe (faster-whisper, local, word-level timestamps) → auto-cut dead air/long pauses
→ scale/crop to 1080x1920 + light color treatment → `build_caption_frames` → `build_caption_track` →
`final_pass` (composites caption track + Rarity symbol). See the script's own `--help` / docstring for
the full option list (`--language`, `--no-cut`, `--font`, `--accent`, `--model`, etc.).

## Workflow B — voiceover + B-roll (`build_voiceover_reel.py`)

```
python3 build_voiceover_reel.py --manifest scenes.json --narration narration.wav --output out.mp4
```
`scenes.json`:
```json
[
  {"video": "scene1.mp4", "offset": 2.0, "text": "The customer discovers your brand..."},
  {"image": "scene2.jpg", "text": "Days later a package arrives..."}
]
```
- `video` (preferred) or `image` (fallback, Ken Burns zoom) — paths relative to the manifest file or
  absolute.
- `offset` (video only, default 0) — seconds into the source clip to start reading from, to skip a
  boring intro second. The actual read offset shifts slightly earlier automatically to cover
  crossfade padding; you don't need to account for that yourself.
- `text` — the exact sentence spoken during this scene. Word count drives the forced-alignment (see
  Non-negotiable 1 in the module docstring) — the manifest's text must match what's actually said.

Pipeline: transcribe narration → align scene boundaries to real word timestamps
(`align_scenes_to_words`) → shrink each scene's slot slightly for transition padding
(`plan_transitions`) → render each scene clip (push-in zoom, real motion preserved for video scenes)
→ join with rotating crossfades (`xfade_concat`) → mux narration audio → `build_caption_frames` →
`build_caption_track` → `final_pass`.

Key options: `--font serif|sans`, `--accent <hex>`, `--model <whisper size>`, `--chunk-size <words>`,
`--zoom <amount>`, `--transition-duration <seconds>` (default 0.35), `--fps`, `--keep-temp`.

## Relationship to the other skills

Step 3 of Caio's personal video pipeline — downstream of `rarity-reel-scripts` (Step 1, the written
script) and, for the talking-head/podcast/street-interview formats only, `rarity-reel-dubbing`
(Step 2, translating a recorded take into other languages).

`rarity-reel-scripts` now writes directly for the "voiceover B-roll" format (its Non-negotiable 10):
it produces a scene-by-scene breakdown — a short visual description plus the exact sentence spoken
in that scene — already shaped to drop into a Workflow B `scenes.json` manifest almost unchanged
(find/confirm the actual B-roll clip per scene here, per Non-negotiable 7, before building). That
format routes **straight from Step 1 to Step 3** — there's no face to dub, so Step 2 is skipped
entirely for it.

Independent of the `rarity-ig-*` brand pipeline — this is Caio's own voice/content, not
@rarity.agency's.
