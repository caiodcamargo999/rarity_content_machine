---
name: rarity-reel-dubbing
description: "Takes ONE video Caio recorded (in English, Portuguese, or Spanish) and produces AI-dubbed, lip-synced versions in the other two languages, using the connected Higgsfield dubbing model (translates the speech, synthesizes it in the target language, and lip-syncs the result back onto the original footage). STEP 2 of Caio's personal video pipeline, after rarity-reel-scripts. Does NOT write scripts, edit video, add captions, or add motion graphics — language localization only. ALWAYS use when Caio wants a recorded video dubbed or translated into other languages, 'dubla esse vídeo', 'traduz esse Reels pros outros idiomas', 'bota lip sync nos outros idiomas', 'dub this into Portuguese and Spanish'. When in doubt, USE this skill."
---

# Rarity Reel Dubbing (Step 2 of 2 — personal video pipeline)

Caio records a script (from `rarity-reel-scripts`, or any video he already has) ONCE, in whichever
language he's comfortable filming in. This skill produces the other two language versions
automatically — translated speech, re-synthesized, lip-synced onto his own face and footage — so he
never has to re-record the same take three times.

**This wraps an existing tool, it doesn't build one.** The actual translate+synthesize+lip-sync work
is done by Higgsfield's `dubbing` model (already connected in this project). This skill's job is
getting the video in and out cleanly, running both target languages, and saving the results in a
consistent place — not reimplementing dubbing logic.

## What this does NOT do (hard boundary, say so if asked)
- **Does not write the script.** That's `rarity-reel-scripts`, Step 1 — run that first if there's no
  recorded video yet.
- **Does not edit the video, add captions, add motion graphics, or add music.** This is a known,
  larger, separate build (no existing connector does this as of 2026-10) — tell Caio plainly it isn't
  built yet rather than attempting a partial version here.
- **Does not post anything.** Hand the finished dubs to Caio to review and post himself (or to the
  `rarity-ig-publish` pipeline only if Caio explicitly wants one on a brand account — unusual for his
  personal founder content, confirm before treating it that way).

## Supported languages
The Higgsfield `dubbing` tool uses three-letter codes. The three Caio actually needs:
`eng` = English, `por` = Portuguese, `spa` = Spanish. (It also supports several others — cmn, fra,
hin, ita, jpn, kor, rus, tur, deu, ara, pol, ind, fil, swe, fin — out of scope for Rarity's use case
unless Caio asks for one specifically.)

## Workflow

### 1. Get the source video in, and confirm its source language
Ask Caio which language the recording is already in if it isn't obvious from context (he'll usually
say, e.g. "I just recorded this in English, dub it to Portuguese and Spanish").
- **If Caio is attaching/uploading the video live in this session**: call `media_upload_widget` with
  `type: "video"` as the ONLY tool call that turn — do not inspect local file paths or chat
  attachments yourself, the widget is the real upload surface and hands back a confirmed `media_id`.
- **If the video is already a file this environment can read from disk** (e.g. already saved in the
  project): use `media_upload` (get a presigned `upload_url`), PUT the file's bytes to it, then
  `media_confirm` with `type: "video"` to get the confirmed `media_id`.
- Either path ends with one confirmed video `media_id`. That's `video_id` for the next step.

### 2. Run dubbing for the other two languages
For each of the two languages that are NOT the source language, call:
```
mcp__claude_ai_Higgsfield__dubbing({
  params: { video_id: "<confirmed media_id>", target_language: "<eng|por|spa>" }
})
```
Run both calls (the two target languages) rather than one at a time where possible. If the tool
returns a job that isn't immediately finished, poll it with `job_display` (pass the returned job id)
until it reaches a terminal state, the same way other Higgsfield generation jobs are checked in this
project. There is no `get_cost` preflight on this tool — it isn't supported, don't claim otherwise.

### 3. Save the results
Figure out which script/folder this video belongs to:
- **If it's the recording of a script from `rarity-reel-scripts`**: save alongside that script, e.g.
  `public/Instagram Briefings/Reel Scripts <Month>/Script N - <Short Name>/original-<lang>.mp4` and
  `dubbed-<lang>.mp4` for each of the two generated versions (download each result video and write it
  to disk at that path — don't leave the only copy sitting in Higgsfield's hosted history).
- **If it's a standalone video with no associated script file**: save to
  `public/Instagram Briefings/Reel Dubs <Month>/<short name>/` with the same `original-<lang>.mp4` /
  `dubbed-<lang>.mp4` naming. Create the month folder if it doesn't exist, following the same
  `<Month>` convention as the rest of this project (current month by default).

### 4. Hand off with an honest caveat
Always tell Caio to actually watch each dubbed version before posting it, specifically listening for:
- **Mispronounced names or jargon** — brand names, platform names ("TikTok Shop," "Meta," client
  names), and DTC-specific terms are the most common place an AI dub gets the pronunciation wrong.
- **Lip-sync drift** on fast speech or if the original has a lot of hand gestures/camera movement —
  flag this as a known limitation of the model, not something this skill can fix after the fact.
- If either dub looks genuinely wrong (garbled audio, broken sync, clearly mistranslated meaning), say
  so plainly and offer to re-run that one language rather than shipping it anyway.

## HARD RULE: never deliver Wav2Lip (or any local patch-based) lip-sync output

Caio, 2026-10, on the Wav2Lip result for Diego: "a boca está completamente deformada, se for assim nem
faz". Frame-by-frame comparison confirmed it: the untouched video was clean; Wav2Lip itself produced the
purple/smeared lips and a reshaped chin/goatee (it regenerates a 96×96 mouth patch). Tuning the mask and
colour only reduced it, never fixed it. So:
- If the Higgsfield `dubbing` tool (or another proper video-to-video lip-sync such as LatentSync/MuseTalk on
  a GPU) is not available, **do NOT ship a lip-synced file**. Stop after the voice step, deliver the dub
  with the original mouth ("sem lip-sync") clearly labelled as such, and ask Caio to authorize Higgsfield
  or an external service. Sending someone's face/voice to a third-party service needs Caio's OK first.
- Any lip-sync result must be inspected at full-res on open vowels and "m/b/p" closures BEFORE showing it,
  and must not change the chin, moustache, teeth or lip colour. If it does, discard it.

## Local pieces that are still good (voice + timing) — use them with Higgsfield or on their own

(The section below documents the local pipeline; **skip its Wav2Lip step 5 for deliverables**.)

## Fallback — LOCAL dub when the Higgsfield `dubbing` connector is NOT reachable

First used on "Diego 01 Ecom DTC (rarity.br)" (PT → EN, 2026-10). Check first: `ToolSearch` for
`Higgsfield dubbing`; if it returns nothing the connector is not loaded in this session (non-interactive
sessions can't authorize it) — say so plainly, then run this local pipeline, and **always tell Caio the
lip-sync is a draft and that the Higgsfield tool gives the real quality**. Never present Wav2Lip output
as "optimal".

Pipeline (scripts in this skill's `scripts/` + `rarity-reel-editor/scripts/`):
1. **Cut at native resolution first** (`native_cut.mp4`, from the same keep-segments as the PT edit) and
   get sentence windows (`pt_sents.json`). Lip-sync must run on NATIVE pixels, before any upscale.
2. **Translate by hand, sentence by sentence** (keep jargon: ROAS, CAC, Meta, Shopify; DRE → P&L;
   "CAC máximo permitido" → "max allowable CAC"). Keep each EN sentence ≈ the PT sentence's length.
3. **Clone the speaker's own voice** with Chatterbox: `rarity-reel-editor/scripts/narrate_chatterbox.py`-style
   call with `audio_prompt_path` = ~12 s of the speaker's clean audio (denoised, `loudnorm`). One wav per
   sentence (`cb_dub.py` pattern: exaggeration 0.5, cfg 0.35, temperature 0.7, seeded). Check the clone:
   median f0 should match the original (Diego: 158 Hz vs 160 Hz). **Only clone a voice with the owner's
   consent** (company video, speaker is a Rarity team member — still confirm with them) and mention the
   Perth watermark.
4. **Fit time without rushing: `scripts/dub_assemble.py`.** A cloned voice speaks ≈3 words/s (slower than
   a fast native speaker), so English ran 10–30 % long. Squeezing audio to the old timing sounds robotic.
   Instead per sentence: video time-warp ≤ ±15 % (`minterpolate`) + audio speed ≤ 1.12× (pitch-preserving
   `atempo`); if a sentence needs more, SHORTEN ITS TEXT (the script prints "!! needs …x audio"). Pad the
   video to the audio length afterwards (`tpad`), minterpolate returns slightly short.
5. **Lip-sync: `scripts/lipsync_wav2lip.py`** (Wav2Lip-GAN, MPS, ≈3 min / 45 s). Needs its OWN venv
   (`~/.rarity-lipsync/venv`; setup in the script docstring) — installing mediapipe into the Chatterbox
   venv broke numpy/protobuf once. Patch `Wav2Lip/audio.py` `librosa.filters.mel(sr=…, n_fft=…, …)` keyword
   form for new librosa. Blend ONLY the mouth region (feathered mask rows 0.56–0.86, cols 0.22–0.78 of the
   face box); blending the whole lower face warped the moustache/goatee. Colour-match the patch in LAB
   (chroma mean 65 %, lightness 35 %) — the raw GAN patch is purple/magenta when the mouth is open.
6. **Word timings for captions:** `rarity-reel-editor/scripts/align_words.py dub_voice.wav en_script.txt`.
7. **Finish with `edit_talking_head.py … --precut --voice dub_voice.wav`** (English captions, English
   motion-graphic cards via `params` strings, music). Card text must be translatable: all labels live in
   `params` (`title`, `nada_text`, `credit`, `metric`, `flat_label`, `ceiling`, `profit_text`, `unit`…).
8. **QA before handing over:** per-word caption gate, loudness (-14 LUFS), and crops of the mouth at several
   moments (open vowels, "m/b/p" closures). Report the honest limits: slightly soft/blurry mouth, occasional
   purple tint inside an open mouth, flicker on very fast speech or hand-over-face moments.
7. **Outputs:** `public/Instagram Briefings/Reel Dubs <Month>/<name>/dubbed-eng.mp4`, `original-por.mp4`,
   and `assets/` (en_sents, words_en, beats_en, dub_timeline, NOTAS.md with the translation choices).

## Relationship to the other skills
Step 2 of Caio's personal video pipeline, downstream of `rarity-reel-scripts` (Step 1, the written
script) and the actual recording Caio does himself (outside this project). A planned but NOT YET
BUILT Step 3 would add captions and motion editing — if Caio asks for that, tell him plainly it's a
separate, larger build that hasn't been started yet (confirmed with Caio, 2026-10), don't attempt a
partial version with whatever tools happen to be connected. This is independent of the `rarity-ig-*`
brand pipeline — different voice, different accounts (Caio personally, not the brand), don't mix them.
