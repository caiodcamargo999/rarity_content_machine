---
name: rarity-vsl-editor
description: "Edits a recorded VSL (video sales letter) or any landscape 1920x1080 talking-head video of Caio / the Rarity team into the finished Rarity house format: transcribes with two whisper models and a corrected script (zero caption errors, doubtful corrections flagged), cuts pauses and retakes, punch-ins, tiny minimal lowercase captions, word-synced glass-card B-roll (stat rows, chips, bar compare, checklists, big numbers), floating stat/text callouts, white-flash transitions with whoosh SFX, an electronic, motivational music bed ducked under the voice, mastered to -14 LUFS. Style reference: the Limitless Agency VSL in 'VSL Edition Ref'. ALWAYS use when Caio drops a VSL / long talking-head video in a raw-video folder and asks to edit it, add subtitles/legendas, add B-roll or transitions, 'edita esse VSL', 'put subtitles on the VSL', 'choose music for the VSL'. Creative ads and Reels (1080x1920) get the SAME edition — rarity-reel-editor Workflow E, same engine. When in doubt, USE this skill."
---

# Rarity VSL Editor

One house format for every talking-head video — a VSL (1920x1080) and a Reel/ad (1080x1920) are the same edit at
different sizes (`rarity-reel-editor` → "Workflow E"). Everything lives in `../rarity-reel-editor/scripts/`.
Reference look: `public/Creatives and Videos in General/Rarity Dtc Ecom VSL/VSL Edition Ref/Limitless Agency (1).mp4`
(tiny lowercase captions, glass cards on a dark gradient, stat callouts beside the speaker, white-flash cuts).

## The format (what Caio asked for, 2026-10 — do not drift from it; creative ads and Reels use it too, see `rarity-reel-editor` Workflow E, rules 37-44)
- **Captions: minimal.** 1–3 words, lowercase, white, Benton, no outline, soft shadow, each word fades in as it is spoken,
  just under the speaker (landscape baseline y≈945; vertical y≈1510, above IG's bottom UI). NOT the loud uppercase
  magenta word-pop style (`dynamic_captions.py` is legacy — only if Caio asks for "dynamic/loud" captions again).
- **B-roll = word-synced graphics, many of them.** About a third to a half of the runtime is a full-screen glass card or a
  floating callout; the speaker returns between them. Show only what is said (numbers, lists, comparisons) — never invent
  figures. Real footage clips are an option only if Caio supplies them or approves Higgsfield credits.
- **Transitions:** white flash in/out of every card (+ whoosh SFX), punch-in cuts on the speaker every ~3.4 s at clause ends.
- **No colour grade** on recorded footage. Rarity palette only (plum-black gradient, magenta 213,0,87 / 236,64,122, white;
  green only for "good/room to scale" bars).
- **Music: electronic, excited, motivational, audible** (Caio, 2026-10: deep house "not nice", orchestral "bad"). `kraft-twerk-115.mp3` via
  `music_bed.py <sec> bed.wav --track kraft-twerk-115.mp3`, render with `--music-lufs -19 --duck-ratio 3` (≈ 7 dB under the voice). Same
  track as the Reels/ads for consistency. Alternatives: `motivating-mornings-033`, `tech-house-vibes-130` (`music/README.md`).
- Rarity symbol top-right (72 px landscape). No progress bar in this format.

## Pipeline (all commands from `.claude/skills/rarity-reel-editor/scripts/`, system `python3`)
```
V="public/Creatives and Videos in General/<VSL folder>"          # Raw-video/<file>.mp4 in, Edited-by-Claude/ out
W=/path/to/scratch/work                              # work dir (kept)

# 1. two transcripts (large-v3 + medium.en, glossary prompt)           -> words_L/M.json, tr_L/M.txt
python3 transcribe_two_models.py "$V/Raw-video/x.mp4" $W/tr
# 2. READ both, write the corrected script.txt (see "Transcript rules"), then relabel the timings with it
python3 align_to_script.py $W/script.txt $W/tr/words_L.json $W/words.json [--drop 101.4-105.3]
# 3. cut (tightens pauses, removes retakes, punch-ins, noise reduction) -> WORKDIR/base.mp4 + voice.wav + .remapped.json
python3 edit_vsl.py "$V/Raw-video/x.mp4" $W/words.json "$V/Edited-by-Claude/out.mp4" --cut-only --workdir $W/cut
# 4. music bed for that length
python3 music_bed.py <ceil(duration)+5> $W/bed.wav --track kraft-twerk-115.mp3
# 5. scenes.json — copy ../templates/vsl_scenes_rarity-dtc-ecom.json and retarget the phrases to THIS script
python3 finish_vsl.py $W/cut "$V/Edited-by-Claude/out.remapped.json" "$V/Edited-by-Claude/out.mp4" \
       --scenes $W/scenes.json --music $W/bed.wav --music-lufs -19 --duck-ratio 3 --workers 8
```
Raw video is huge (500 MB) and the render >100 MB limit applies to git: **never commit the VSL folder**; the repo is public.
`finish_vsl.py` prints every scene's window; a phrase missing from the transcript raises — fix the JSON, don't guess.
`--only 3,7` renders just those scenes for a quick look. Render time ≈ 5 min for 210 s.

## scenes.json (the B-roll language)
Card (full screen, opaque) or float (right of the speaker). Times are PHRASES from the corrected transcript (first match after
the scene start) or seconds; `dt` shifts. Positions are fractions of the canvas (`y`, `x`; `yv`/`xv` for vertical).
Item types: `strike` (word struck through, e.g. ROAS), `big`, `label`, `chip` (icon check/cross, `hl`), `chips` (flow row),
`rows` (glass rows with counting numbers `count_to`, `prefix`, check icons), `compare` (bars vs a MAX CAC line), float
`stat` (ring + counting number + rising line) and float `text` (small line + 2 bold lines, optional struck small line).
Docstring of `finish_vsl.py` has the exact keys; `templates/vsl_scenes_rarity-dtc-ecom.json` is the worked 20-scene example
(it maps one idea per sentence: wrong number → max CAC → unit economics → $42 vs $62 vs $55 → what ROAS can't see → real
numbers → bottlenecks → solutions → who it's for → 45-min diagnostic → free → apply). Design rules that cost a re-render:
- keep card content above y≈0.74 of the canvas — captions live below; chips at y 0.88 collided with them;
- big text must fit: 150 px for 2-word lines, ≤ 250 px for 3 letters; vertical canvas is 1385 wide in design space;
- one idea per card, items pop on the word that names them, 4–6 items max; a card holds until its sentence ends;
- leave plain speaker time between cards (hook and CTA sentences are strong on camera).

## Transcript rules (captions must have ZERO errors)
- Run BOTH models; Caio's accent makes them disagree on jargon. Known misses: Kyle→Caio, Herity/Heritage→Rarity,
  Ross/"leading Ross"→ROAS, math→Meta, foxwood→conversion-focused, agent→agency, "45 minutes"→"a 45-minute".
- Resolve doubtful phrasings by scoring alternatives with `prefix=` + avg_logprob on the clip (see the VSL session),
  correct by context, **and tell Caio every doubtful correction** (heard → used → where) so he can confirm against the audio.
  Last VSL: "No ad account access is required upfront" (heard "No other contact"), "how much you can", "you're either scared",
  "looking at the wrong number", "getting you higher ROAS", "a 45-minute profit diagnostic", "core profit bottlenecks",
  "conversion-focused UGC", "site conversions", "performance media on Meta and Google".
- Retakes / stutters (said twice, "site site", "is isn't") are left OUT of script.txt; `--drop` removes heard words of a
  discarded take, and the cut drops the audio.

## QA gate before showing Caio
1. Contact sheet (ffmpeg `tile`) of ≥ 16 frames incl. every scene type; check overlaps, clipped text, caption collisions.
2. Every word has a caption at its time: compare the caption band of the final vs `base.mp4` per word (diff > 1.0), and no run
   of > 3 speech frames without a caption.
3. `ffmpeg -af ebur128` → -14.0 LUFS, true peak ≤ -1 dBFS; speech-segment mean volume should not drop vs the no-music render.
4. You cannot hear it — say so and ask Caio to listen once.

## Output + reporting
Save as `Edited-by-Claude/<name>-EDIT.mp4` (+ `.remapped.json`); older versions stay beside it. Reply in Caio's language with
the file path, what was done, the doubtful corrections list, and what is a graphic vs real footage. Do not commit or push unless asked.
