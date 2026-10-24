---
name: rarity-reel-editor
description: "Step 3 of Caio's personal video pipeline — takes either (a) a raw recorded video or (b) a narration track + a list of B-roll clips/images per sentence, and produces a finished, cut, color-treated, captioned, branded vertical Reel (1080x1920). Minimal fixed-size captions in Rarity's brand typefaces (BentonSans + a magenta Playfair-italic key word), Rarity symbol overlay, and (for the voiceover format) dense brand-tinted lens-flare transitions by default (plus whip pan, zoom punch, flash, dip) with matching SFX, strong automatic colour matching so every clip shares one palette, a human-sounding local AI voice (Chatterbox), royalty-free music that ducks under the voice, and mastered loudness. Also edits ANY recorded talking-head clip — Reels AND ads, same house format (Workflow E, Limitless-style: tiny lowercase captions, word-synced glass-card graphics, floating callouts, white-flash transitions, deep-house bed, -14 LUFS) in Portuguese/English/Spanish; landscape VSLs use the sibling skill rarity-vsl-editor. ALWAYS use when Caio wants raw footage turned into a finished Reel, or wants a voiceover-style video built from B-roll clips synced to narration — 'corta e edita esse vídeo', 'bota legenda nesse Reels', 'monta um vídeo com essas imagens/clipes e essa narração', 'faz o voiceover', 'put music on it'. When in doubt, USE this skill."
---

# Rarity Reel Editor (Step 3 of the personal video pipeline)

Takes video that already has a voice track (Caio's own recording, or a narration track paired with
B-roll) and turns it into a finished, postable vertical Reel — cut, color-treated, captioned, scored
and branded. This is the step after `rarity-reel-scripts` (the words) and, for formats with a face on
camera, `rarity-reel-dubbing` (translating Caio's own recorded voice into other languages); it never
writes scripts or dubs voices itself.

Two formats, same caption/branding engine underneath:

1. **`scripts/edit_reel.py`** — raw footage format (Caio talking on camera). Transcribes, auto-cuts
   dead air, color grades, captions, brands.
2. **`scripts/build_voiceover_reel.py`** — voiceover + B-roll format. Narration + ordered
   `{video|image, text}` scenes → each scene shown exactly as long as its sentence is spoken, styled
   transitions + SFX, mastered voice, ducked music bed, captions, logo. **Prefer real video clips
   over photos** — Caio called a photo/Ken-Burns version "not realistic" (2026-10).

3. **Talking head (Reels + ads) → Workflow E below is the house format since 2026-10** (Caio: "the reels format and the ads in the same format when it's somebody talking to the camera"). `scripts/edit_talking_head.py` (Workflow C / C2, lower-third strips + Playfair key-word captions) is LEGACY — use it only if Caio asks for that older look or to re-render an old edit. Workflow C: a recorded talking-head clip (a team member such
   as Diego, or Caio) → CUTS + minimal captions + **speech-synced motion graphics** + music/SFX.
   Built for Rarity BR in Portuguese; language-agnostic. See "Workflow C" below.

All formats end with the same shared caption engine in `edit_reel.py`: `build_caption_frames` →
`build_caption_track`. Fix a caption/branding bug once, every format inherits it.

## Files in this skill

| Path | What it is |
|---|---|
| `scripts/build_voiceover_reel.py` | Workflow B builder (transitions, SFX, music ducking, voice mastering, captions) |
| `scripts/narrate_chatterbox.py` | Human-sounding local TTS (Chatterbox). Needs `~/.rarity-voice-venv` (setup in its docstring) |
| `scripts/align_words.py` | Forced alignment: whisper TIMES + the SCRIPT's own words → `words.json` (zero caption typos) |
| `scripts/edit_talking_head.py` | Workflow C: cut + grade + captions + motion graphics + music for a recorded talking head |
| `scripts/motion_graphics.py` | Speech-synced motion-graphic beats (strike, bars, bank, credits, sum, channels, lupa, cac, call, checklist) |
| `scripts/data_scenes.py` | Full-frame designed scenes for voiceover Reels (calendar, timeline, counter, bars, ladder, auction…) + plate overlays |
| `scripts/lens_flare.py` | Procedural brand-coloured lens-flare transition track (numpy → qtrle .mov) |
| `scripts/edit_reel.py` | Workflow A + the shared caption / branding engine |
| `music/` | Curated royalty-free tracks (Mixkit Stock Music Free License) + `README.md` with what to use when |
| `fonts/` | Brand fonts for captions: BentonSans Regular (body) + Playfair Display Bold Italic (accent word); fonts only — libass chokes on other files here |

## The voiceover recipe (Workflow B), end to end

```
# 0. script text, one file, exactly what will be spoken                       narration.txt
# 1. human voice (local, free)
~/.rarity-voice-venv/bin/python scripts/narrate_chatterbox.py narration.txt narration.wav
# 2. script-exact word timings
python3 scripts/align_words.py narration.wav narration.txt words.json
# 3. scenes.json = one entry per sentence-group with a REAL, watched B-roll clip (see rule 4/7)
# 4. build
python3 scripts/build_voiceover_reel.py --manifest scenes.json --narration narration.wav \
    --words words.json --music music/brainiac-167.mp3 --music-start 4 --transitions flare \
    --output reel.mp4 --language eng
# 5. QA gate (rule 6) before showing it to Caio
```
Always pass `--words` for AI-generated narration (captions then equal the script exactly). Without
`--words` the narration is transcribed by whisper — use that only for Caio's own recording, and
proof-read the captions because whisper writes "$96" for "ninety-six" and drops apostrophes.

`scenes.json`: `{"video": "x.mp4", "offset": 2.0, "text": "...", "transition": "whip"}` —
`offset` skips a dull intro; `transition` (optional) overrides the preset for the cut INTO that
scene: `flare`, `whip`, `whipr`, `punch`, `flash`, `dip`, `dissolve`, `cut`. Presets
(`--transitions`): `mix` (**default**: varied sequence, lens flare only at key turns), `flare` (lens flare on every cut — avoid unless asked), `dynamic` (whip → punch → flash → whip back…), `kinetic` (faster/more
whips), `clean` (dissolves + dips), `cinematic` (dips + punches). Every transition also gets a
matching whoosh / shimmer / thump / tick (synthesized with ffmpeg, no licensing issue) unless
`--no-sfx`. Colour handling: automatic per-clip colour matching + one shared look (`--no-grade`
disables it; see rule 10).

## Non-negotiables (most are lessons from real failures — read before changing the code)

1. **Captions are ONE pre-baked video track, never a chain of per-word overlay filters.** The first
   version chained one `overlay` per word (50+ inputs) and silently stopped compositing mid-video.
   `build_caption_track()` bakes every caption PNG + transparent filler into ONE alpha `.mov`
   (concat demuxer, `qtrle`), so `final_pass()` only ever has 3 inputs. If a caption bug appears,
   suspect `build_caption_track`/`final_pass` first. Inside it, windows are **frame-quantized**,
   tiny gaps are bridged, and short words get a minimum frame count — before that fix, words under
   ~0.12 s ("the", "are", "you're") vanished (found by the per-word QA gate, 2026-10).
2. **Transitions must look professional — never use ffmpeg's `zoomin` xfade.** It pixelates into
   visible blocks mid-transition (spotted on a render 2026-10, Caio: "very amateur"). The current
   set is: whip pan (slide + horizontal `gblur` motion blur on the overlap), punch (short dissolve
   while the INCOMING clip eases from 120% → 100% — implemented in the scene's zoom expression),
   flash (`fadewhite` 0.16 s), dip, dissolve. Rotate styles so no two neighbours repeat, keep them
   0.14–0.4 s, and always pair with SFX. Per-boundary durations differ, so `plan_transitions()`
   shrinks each scene by the average overlap to keep total length == narration length.
   **Lens flare is Caio's signature transition** (2026-10: "transição lens flare") but is NOT to be used on every cut — he later asked for variety (rule 21); default preset is now `mix`. It is rendered
   procedurally by `scripts/lens_flare.py` as ONE full-length RGB track (black except at the
   cuts) and screen-blended over the joined video in a single `blend=all_mode=screen` pass —
   convert both streams to `gbrp` first or the studio-range black of yuv420p lifts the whole
   frame. Each flare is a 0.66 s light source sweeping the frame (small hot core + magenta bloom
   + anamorphic streak + mirrored ghost discs + a faint magenta wash at the peak) with the actual
   cut (a 0.20 s dissolve) hidden under the brightest moment; the shimmer SFX leads the peak by
   ~0.34 s. **Keep the light DENSE and tinted, never a white-out** (Caio, 2026-10, on the first
   version: "make the light more opaque, it's too lighty"): the first version's wash was 0.74 of
   white and bloomed the whole frame pale; it is now `FLARE_STRENGTH = 0.62`, no pure white
   (`HOT` is warm off-white), wash 0.20 tinted brand magenta, and the screen blend runs at
   `--flare-opacity 0.85`. Tune lighter/darker with those two knobs, never by adding white.
   Flare colours are ONLY off-white + Rarity magenta so the palette stays consistent. Sweep
   direction rotates through 4 paths so consecutive flares don't repeat. Preview the flare alone
   with `python3 scripts/lens_flare.py out.png`.
3. **The voice must sound human. Hierarchy:** (a) Caio's own recording (best, always), (b) Chatterbox
   via `narrate_chatterbox.py` (open weights, preferred over ElevenLabs in Resemble's blind tests;
   optional `--voice-ref` to clone Caio's OWN voice from a 10 s clip he records), (c) ElevenLabs via
   Higgsfield `generate_audio` when that connector is available (check `balance` first), (d) Edge
   neural voices (`edge-tts`) only as a flagged stand-in. **Never `say`** — Caio rejected it as
   robotic; and Edge voices were still called "a little bit synthetic" (2026-10). Generate
   sentence-by-sentence (pacing resets naturally), never one giant paragraph. Chatterbox embeds an
   inaudible Perth AI watermark — fine to post, but don't pass it off as a human recording.
   Master the voice (`VOICE_CHAIN`: -4 dB headroom → high-pass → de-box → presence → air →
   compressor → -16 LUFS). The headroom matters: un-padded TTS peaks at 0 dBFS and clipped the EQs.
4. **B-roll must be very congruent with the sentence** ("os takes de video devem ser muito
   congruentes com o que é falado"). A "dashboard" line once got a forex-trading clip and Caio
   rejected it. Process: search Pexels via `tavily_search` (`include_domains: ["pexels.com"]`; phrase
   queries like video titles — "Free Stock Video Footage … <literal action>"), download with
   `https://www.pexels.com/download/video/<id>/` (302 → mp4, no key needed), then **look at a
   contact sheet** (`ffmpeg -vf fps=0.6,scale=-2:300,tile=6x1`) before accepting. Reject: foreign-
   language UI, brand/logos you don't want, blank phone screens when the line says "app", stock
   that merely shares a keyword. Prefer 9:16 sources; if none match, rewrite the line to fit real
   footage rather than ship a mismatch. Pexels licence = free commercial use, no attribution.
5. **Music: royalty-free only, picked by measurement, ducked under the voice.** Use the curated tracks
   in `music/` (Mixkit "Stock Music Free License": commercial + social OK, no attribution, not for
   re-sale as music). Selection rule for voiceover Reels: instrumental, 100–120 BPM, steady energy
   (low RMS variance), warm-mid spectrum (centroid ~1.4–2.3 kHz), no vocals, no big drops — it must
   *support* speech. The builder loudness-normalizes the bed to `--music-lufs` (-27), runs it through
   `sidechaincompress` keyed by the voice (it dips ~8–10 dB while words are spoken and breathes back
   up in pauses), fades in 0.8 s / out 1.8 s, then loudnorms the final mix to -14 LUFS / -1.2 dBTP
   (Instagram target). The Instagram Graph API cannot attach IG's licensed library, so the music is
   baked into the file; Caio can still layer an in-app trending sound at low volume if he wants.
6. **Captions: zero errors (hard gate) AND minimal.** ("as legendas não pode ter nenhum erro";
   "keep the subtitles the same size always"; and, on the bold word-by-word version: "the caption
   is too animated — make it a little bit with the font of Rarity, but more minimalist".)
   **Default style = `minimal`** (`--caption-style minimal`, in `edit_reel.build_caption_frames_minimal`):
   - whole PHRASE shown at once — no word-by-word flipping, no scaling, no pop, no stroke. Only a
     ~0.13 s opacity fade-in and a short fade-out; nothing moves.
   - Rarity's typefaces: **BentonSans Regular** (brand body font, `fonts/BentonSans-Regular.otf`) in
     brand off-white `#efeeea`, sentence case as written in the script, with ONE key word per
     phrase in **Playfair Display Bold Italic** + magenta (the same "italic accent word" device as
     the IG posts). The magenta is `legible_accent()` = `#D50057` lightened 30 % toward white,
     because pure brand magenta sinks into dark footage; same hue family so the palette holds.
   - ONE fixed size for the whole video (74 px) — never shrink-to-fit. Phrases end at sentence/clause
     punctuation; a clause too wide for one line (≤ 90 % of frame width) is split into BALANCED parts
     (`minimal_phrases`), never leaving an orphan last word ("…sixth and / seventh" was a bug).
   - key word = `pick_key_word`: digits/%/$ > number words > capitalised non-initial word (names,
     days, months) > longest content word; stop-words never win and a phrase of only filler gets no
     accent. An explicit `{"key": true}` on a word in `words.json` overrides it.
   - legibility without boxes: a very soft dark halo (blurred rounded rect, alpha ≈ 0.46) + a soft
     drop shadow behind the line. Without it bare type vanished on the white calendar and sofa shots.
   - position: baseline y = 1330 of 1920 (above IG's bottom UI, clear of the right rail and logo).
   The old bold/ALL-CAPS/word-highlight look is still available as `--caption-style bold` (112 px,
   max 3 words, stroke, active word recoloured) but is NOT the house style any more.
   **Before showing a render** run the per-word gate against a caption-less render: keep the temp
   dir (`--keep-temp`), and for every word grab a frame at its midpoint from BOTH `base_with_audio.mp4`
   and the final mp4, crop the caption band (y 1180–1480), and require > ~900 pixels that differ by
   more than 60 summed RGB. Then eyeball a contact sheet (every ~1.2 s) plus full-res crops of the
   caption zone on a bright, a dark and a busy background. Sample at word MIDPOINTS — near a word's
   end ffmpeg seek rounding gives false negatives.
7. **Alignment robustness.** `align_scenes_to_words` consumes `len(text.split())` words per scene, so
   the word list must have exactly the script's tokens. That is why `align_words.py` exists (it
   re-labels whisper's timings with the script tokens via difflib, interpolating mangled ones).
   Never hand whisper's raw transcript of AI narration to the builder.
8. **Clip rendering gotchas (each cost a broken render once).** `fps=` must come BEFORE `zoompan`
   (d=1 emits one frame per input frame; a 25 fps source ran ~17 % short and the xfade chain
   truncated → frozen picture). Use `-stream_loop -1` so a source shorter than its slot loops
   instead of ending early. Do not trust render success — check `concatenated.mp4` duration equals
   the sum of the plan.
9. **Hook scene gets the strongest B-roll and the first transition is a flare, flash or whip**, because
   the first 3 seconds decide retention. Don't open on a slow dissolve.
10. **One colour palette across the whole video** (Caio, 2026-10: "keep the consistency in the color
    palette" and then "I need even more congruence in the color palette"). Stock clips arrive with
    clashing grades (orange living room, teal studio, grey sofa, white desk; mean saturation
    ranged 0.09–0.64 in one video). `build_voiceover_reel.py` therefore, per clip:
    (a) measures mean RGB **and mean HSV saturation** over the segment actually used
    (`measure_clip_rgb`, 5 frames); (b) pulls it toward neutral white balance, a common luma
    (`TARGET_LUMA` 0.42) and a common saturation (`TARGET_SAT` 0.28) at **`MATCH_STRENGTH` 0.85**,
    clamped (channel gains 0.75–1.30, exposure 0.65–1.40, saturation ×0.55–1.15) —
    `color_match_filter`; then (c) applies the SAME `RARITY_LOOK` to every clip: saturation ×0.86,
    contrast 1.05, and a per-channel **split-tone curve** from the brand palette — shadows lifted to
    deep plum/navy (≈ `#0f0a1a`/`#1a0f2e`), highlights capped at warm off-white (≈ `#efeeea`) with a
    soft shoulder so sunlit clips don't blow out — plus a light vignette. Net effect: every shot
    shares the same black point, white point and muted tone, and the ONLY saturated colour on screen
    is the brand magenta (key word in captions, lens flare). `final_pass(grade=None)` so the look
    isn't applied twice; `--no-grade` turns the whole thing off. Still prefer B-roll whose native
    look is close (low saturation, neutral) — grading rescues, it can't fix a neon or monochrome
    clip. Brand palette reference: `rarity-ig-designer/assets/rarity-colors.json`.

## Workflow A — raw footage (`edit_reel.py`)

```
python3 scripts/edit_reel.py <input_video> <output_video> [options]
```
transcribe (faster-whisper) → auto-cut dead air → 1080x1920 crop + light grade →
`build_caption_frames` → `build_caption_track` → `final_pass`. Options: `--language`, `--no-cut`,
`--font`, `--accent`, `--model`, `--chunk-size` (default 3). Music/SFX mixing for Workflow A is not
wired yet — add a bed with `mix_audio()` from `build_voiceover_reel.py` if needed.

## Workflow B v2 — designed scenes, specific plates, varied transitions (rules 18-24)

Caio's feedback on the first stock-footage voiceover (2026-10): "you have to vary the transitions, not
only one"; "the clips are not very congruent and are very free stuff — I want something more
specific, more engaging"; "research the best video edits for voiceover and clips."

Research that shaped this (OpusClip, Captions, Zeely, Increditors, Async, Vidico; 2026): a visual
change every **1.5–3 s** (B-roll every 1–2 s for educational content), re-hook every 8–12 s; the
hook must land in **1.5 s and ALSO as on-screen text** (≈85 % watch muted); data should *move* —
bars growing, lines trending, percentages counting up; match cuts and beat-synced cuts only when they
clarify; keep transitions consistent *within a series* but purposeful *within a video*; end on a frame
that echoes the first (loop); captions ≤ 2 lines, high contrast, not at the very bottom.

18. **Specific beats generic.** If the sentence is about a number, a date or a comparison, draw THAT
    (`scripts/data_scenes.py`) instead of stock: a calendar with Oct 6 circled, a week schedule
    (Walmart Oct 5–11, Amazon/Target Oct 6–7) filling in, a count-up `$95.8B`, a `+8%` slam, Cyber
    Monday vs Black Friday bars with their YoY growth, a discount ladder (14 % → 21 % → 30 %), an ad-
    auction curve flooding with dots, a November calendar with a LATE stamp. Every figure on screen
    must come from a cited source (Adobe Analytics forecast 2026-09-28; retailer sale pages) and a small
    source chip is shown. Keep illustrations honest (relative bar heights real, nothing invented).
19. **Real clips only as *specific plates* under callouts**, never as wallpaper: an Amazon-branded
    courier under "AMAZON PRIME BIG DEAL DAYS · OCT 6–7"; a hand hanging a BLACK FRIDAY SALE placard
    under the discount ladder; a phone scrolling a short-video feed under "TESTING CREATIVE". Plates
    are push-in, colour-matched, dimmed/blurred as needed (`dim`, `blur` in the manifest).
20. **Scene types in `scenes.json`:** `{"graphic": "<kind>", "text": "...", "anchors": {name: wordIndex|seconds},
    "params": {...}, "video": "plate.mp4", "offset": 1.0, "dim": 0.3, "blur": 5, "transition": "whip"}`.
    Kinds: calendar_hook, calendar_late, timeline, counter, bigstat, bars2, ladder, feed, auction, chip
    (generic pills/lines over a plate). An int anchor is a WORD INDEX inside that scene's `text`
    (so animation lands exactly when the word is spoken); a float is seconds. Aim for 8–12 scenes in a
    28 s voiceover (one every 1.5–3.5 s) and alternate designed scene ↔ real plate.
21. **Vary transitions on purpose** — never one effect for the whole video, and don't force the
    signature lens flare on every cut. Palette: `cut` (hard, for fast beats or into a slam), `whip`/
    `whipr` (horizontal motion-blur whip), `whipup`/`whipdown` (vertical), `punch` (dissolve + incoming
    clip eases 120 → 100 %), `flash`, `iris` (circular reveal for a new data scene), `dip`, `dissolve`,
    and `flare` (lens flare, **reserve for section changes / the reveal of the big number / the
    closing**). Script 1 v2 uses: whip, iris, flare, cut, whipup, flash, whipr, punch, flare. Rule of
    thumb: hard cut or flash INTO a slam/number, whip between a plate and a graphic, flare at the 2–3
    emotional turns, never the same transition twice in a row.
22. **Dither all designed backgrounds.** A dark plum gradient quantised to 8-bit then x264-compressed
    shows concentric contour rings (seen on the first `+8%` frame). `designed_bg()` adds Gaussian
    noise σ≈2.2 per pixel before quantising; keep it when editing the backgrounds.
23. **Layout contract for designed scenes:** overlay band y 170–1300, captions below at y 1330 (halo top
    ≈ 1245) — never place a pill/line below y ≈ 1230. Headline text must be width-checked (a 150 px
    Playfair "BLACK FRIDAY" overflowed the frame; 112 px fits). Calendar `cell_h` 76 so a 6-row month
    leaves room for the line beneath it.
24. **Counters count from the start of the scene** (not from the word) over `params.dur` so the viewer
    never sees a stalled "$0.0B"; set `dur` so the final value lands as the number is spoken.

## Workflow C — talking head + motion graphics (`edit_talking_head.py`) — RETIRED for new work (use Workflow E)

First used on "Diego 01 Ecom DTC (rarity.br).mp4" (2026-10, Rarity BR, Portuguese). Recipe:

```
# 1. word timings from the real audio — large-v3 + a glossary prompt (medium mishears jargon)
#    (see the faster-whisper call in the session that built Diego 01: language='pt', beam_size=5,
#     initial_prompt="… ROAS, CAC, MER, DRE, Meta Ads, Klaviyo, Shopify, call de 45 minutos …")
# 2. READ the transcript critically, write the corrected text to script.txt, then
#    align_words.align(script_tokens, heard_words) -> words.json   (captions = script text exactly)
# 3. write beats.json (motion graphics, ORIGINAL-video times, anchored on word times)
# 4. python3 scripts/edit_talking_head.py video.mp4 words.json beats.json out.mp4 \
#        --music music/brainiac-167.mp3 --music-start 6
# 5. QA gate (below), then save to public/Creatives and Videos in General/Rarity BR Edits/ with an assets folder
```

Rules learned (2026-10):
11. **Transcripts: never trust raw whisper on Rarity jargon, and flag every correction.** Whisper heard
    "hoas" (ROAS), "clevel" (Klaviyo), "cá que máximo permitia" (CAC máximo permitido), "o Macau de 45
    minutos" (a call de 45 minutos), "numeral vivo" (número ao vivo). Run **large-v3** with a glossary
    `initial_prompt`, compare with a second model, correct by context, and write a
    `CORRECOES-TRANSCRICAO.md` (heard → used → confidence) next to the video so a human can confirm
    the doubtful ones against the audio. Captions must have zero errors, so a doubtful word is
    reported, never silently guessed.
12. **Cuts.** Keep `[word.start-0.06, word.end+0.10]` around every word; everything else goes
    (pauses collapse to ≈0.16 s, head/tail silence trimmed, 6 ms audio fades at joints). A clip that
    was already tightly edited loses little (Diego: 45.31 s → 44.10 s) — don't over-cut or the
    speech turns robotic. Never cut mid-word.
13. **Motion graphics = the speaker's words made visible, in lower-third strips only.** Zoomed-in shots
    of a talking head reach down to y≈1110 (chin) on a 1920 frame — a mid-frame card covers the
    mouth. So every beat is a ≈1000×270 strip at y 1120–1410 (`motion_graphics.ZONE_Y0/ZONE_H`) and
    captions sit below it at y 1480 (`--caption-y`); IG's own bottom UI starts ≈ y 1580. Beats appear
    when the idea is said (word-anchored: a platform chip pops on its own word, a bar chart rises
    on "escala o investimento", a checklist row ticks as each deliverable is spoken), pop in with an
    ease-out-back slide, fade out in 0.22 s, and use only brand colours (plum card, off-white text,
    lightened magenta). Show only what he actually says — diagrams are illustrative (relative bar
    heights, no invented numbers or claims). Build new beat types as `beat_<type>` functions.
    Keep a gap of plain face-time between beats (the hook and the "Sabe por quê?" beats are left clean
    on purpose); at most one beat on screen at a time.
18a. **Never let card text overflow** (Diego bug, 2026-10: "o Shopify mostra menos" ran past the card's right
    edge and was clipped). Any variable-length string in a beat must shrink-to-fit inside the card
    (`sum` beat does this; copy the pattern) and be checked at full-res at its fullest moment. Text in
    another language is longer — English labels need the same check. All card strings are `params`.
18c. **Dubbed versions:** `edit_talking_head.py --precut --voice dub.wav` takes a video/words/beats that are
    already on the final timeline (no cutting) and an external voice track — see `rarity-reel-dubbing`.
18b. **Never colour-grade recorded talking-head footage unless asked** (Diego feedback, 2026-10: "não
    precisava ter tratado cor, deixe como estava"). Rule 10 (colour matching + Rarity look) is for
    *assembled stock* in voiceover reels, where clips clash. A person's own recorded video keeps its
    original colours and skin tones: `edit_talking_head.py` is ungraded by default (`--grade` opts in);
    verify by comparing mean RGB of the same face region before/after (Diego: 107/75/62 → 107/75/62).
    Upscale, denoise, sharpen, grain and cuts are still fine.
14. **Low-resolution sources** (a 480×848 phone export was the input): denoise at native size
    (`hqdn3d`), lanczos upscale to 1080×1920, light `unsharp`, then film grain (`noise`) to hide the
    softness. Tell Caio the source is low-res and ask for the original export when quality matters.
15. **File size.** Grain makes x264 explode (382 MB for 44 s at crf 17). Final encode is
    `-preset slow -crf 21 -maxrate 14M -bufsize 28M -movflags +faststart` (≈59 MB / 44 s). Keep
    intermediates lossless-ish, the delivered file under ~100 MB.
16. **Caption fonts for numbers.** Playfair Display has old-style numerals ("90" looks like "9o"), so a
    numeric key word is drawn in BentonSans (still magenta). Portuguese/Spanish stop-words and
    all-caps acronyms (ROAS, CAC, DRE) are handled by `pick_key_word`.
17. **QA gate for talking heads** = the same per-word diff gate as rule 6, with the caption band at
    y 1390–1590 (`crop=1080:200:0:1390`) comparing the final render with `base.mp4` (use
    `--keep-temp`), plus full-res crops of the strip + caption zone at ≥5 beat moments.

## Workflow C2 — ad / content edit built from reference videos (`ad_graphics.py`) — RETIRED: creative ads now get the VSL edition (Workflow E)

First used on Caio's three English ads (`Rarity EN Edits/Caio Raw Videos (to edit)/caio-01..03.mp4`,
110 s / 81 s / 177 s, 2026-10) from two references in `Video Edition Ads and Content Refs/`.

**What the references do (analysed, not guessed):**
- *Ref 1* — direct-response ad, one continuous talking-head shot (6 scene changes in 81 s, -16.5 LUFS):
  name tag lower-third; bold caps captions with the key words in an accent colour; **single-colour line
  icons that pop beside the face exactly when the noun is said** (phone-with-X, pin, briefcase-check,
  calendar, bar chart…); thin progress bar.
- *Ref 2* — daily "Field Notes" series, vertical, essentially uncut (2 scene changes in 149 s, -15 LUFS):
  series title card + progress bar at the start; **dark translucent data panels** (stat rows, framework
  lists) and a small inset thumbnail; one-word captions.

**What we kept / translated (Rarity rules win over the refs' yellow/orange and heavy caps):**
| Reference device | Rarity version |
|---|---|
| Name tag | `nametag` beat, top-left: "Caio de Camargo / Founder, Rarity", plum card + magenta bar |
| Line icons | `icon` beat, 24 icons in `ad_graphics.ICONS`, off-white stroke + one magenta accent, at the OUTER top corners |
| Data panels | lower-strip beats: `stat` (1–4 big numbers), `level` (chapter chip), `vs` (struck % vs flat fee), `ceiling` (CAC ceiling demo), `cta`, `title` + the older `checklist`/`cac`/`channels`/`call`/`strike` |
| Progress bar | thin magenta fill on an off-white track at y 104 (`--no-progress` hides it) |
| Series title card | `title` beat (lower band) in the first 3 s: kicker + Playfair-italic topic line |
| Captions | unchanged house style (minimal Benton + Playfair-italic magenta key word) — NOT ref 1's caps |
| Colours / footage | brand palette only; footage ungraded (rule 18b); music bed + `pop` SFX |

Rules (2026-10):
25. **Top icons: outer corners only, ≤ 1.55× scale.** In Caio's close-ups the head spans x 200–900 down to
    y 1000; an icon at x≈880 sat on the glasses. Icons live at cx 936 (right) / 144 (left), y ≈ 288, and
    never more than one at a time. The Rarity symbol is at x 976–1040, y 40–104 — keep clear.
26. **Title / name cards never go in the top band over the face.** In wide shots the head starts at y≈130,
    so a top title cut across the eyes. Titles use the LOWER strip (`title` beat) in the first ~3 s; the
    name tag sits top-left (x 40–400) where there is only background.
27. **Phrase-anchored beats** (`scripts/beat_anchors.py`): `W.find("something called")` → seconds. Write the
    beat list as code, run it, and let it raise when a phrase isn't in the transcript. Keep lower beats
    sequential, ≤ 1 top icon at a time, one idea per card, a beat holds until the sentence it illustrates
    ends (+0.3–0.6 s). Aim for a new visual every ~3–6 s on a 80–180 s ad (the refs are slower than a 28 s
    voiceover reel because the speaker IS the visual).
28. **Never re-grade or re-sharpen a clean 1080×1920 source** (`edit_talking_head.py` skips `hqdn3d`/
    `unsharp`/grain when width ≥ 1080); those are for low-res phone exports only.
29. **Accented English transcripts need a second opinion.** Caio's English made large-v3 and medium.en
    disagree on proper nouns and jargon ("Herity" = Rarity, "17 Xbox" = 17x ROAS, "35 books/rooks" =
    35 hooks, "MR/MLR/NAR" = MER, "meta horror poster" = Meta roller coaster, "Maximal" = Maximum). Run
    BOTH models with a glossary prompt, compare line by line, correct by context and by the other
    videos in the same batch (a phrase clear in video 03 fixes video 01), and **list every doubtful
    correction for Caio** — captions must have zero errors.
30. **Output location:** edited ads go to `public/Creatives and Videos in General/Rarity EN Edits/` next to
    `Caio Raw Videos (to edit)/`, named `caio-0N - EDIT.mp4`, plus an `assets/` folder (words, beats,
    corrected script, `CORRECOES-TRANSCRICAO.md`).

### Dynamics pass for talking-head ads (Caio, 2026-10: "put a little deep house in the background, voice louder than the music… cut a little bit to make it dynamic")
31. **Music: deep house bed, voice clearly on top.** `music/deep-house-196.mp3` (Mixkit "Deep House",
    123 BPM, start ≈ 18 s) for ads ≤ 150 s; `deep-urban-623.mp3` for longer. Bed at `--music-lufs -21`
    (first try at -26 measured 19 LU under the voice — too faint; at -21 the ducked bed sits ≈ 14 LU under
    the voice: voice -17 LUFS vs bed -31 LUFS while speaking) and the sidechain compressor drops it ~8–10 dB
    while words are spoken, so the music is felt in the gaps and never competes with the voice. Measure
    voice and ducked-bed integrated loudness separately (see scripts/remix_music.py) instead of guessing.
32. **Cut tighter, then hide the jump cuts.** `--pre 0.035 --post 0.06` trims 2–3 s more than the default
    (0.06/0.10) without clipping consonants; `--punch 0.06 --punch-every 4.5` alternates a 6 % punch-in
    (anchored near the chin, so the face doesn't drop into the graphics strip) on every other shot and adds
    an extra punch-in at the next clause boundary every ~4.5 s. The extra cuts are VIDEO-only — the audio
    is continuous across them, so speech never gets chopped.
33. **Progress-bar bug (fixed):** `drawbox=w='…t…'` is not re-evaluated per frame, so only the grey track
    showed (looked like a stray line). The bar is now `ad_graphics.build_progress_track()` — a real RGBA
    track; verify by sampling the bar at 3 timestamps and checking the magenta fill grows.

## Relationship to the other skills

Step 3 of Caio's personal video pipeline — downstream of `rarity-reel-scripts` (Step 1) and, for
talking-head/podcast/street formats only, `rarity-reel-dubbing` (Step 2). The voiceover-B-roll format
goes **straight from Step 1 to Step 3** (no face to dub): `rarity-reel-scripts` writes the numbered
`visual note → sentence` scene list; here you source and *watch* the clip per scene (rule 4), record
or synthesize the narration (rule 3), then build. Independent of the `rarity-ig-*` brand pipeline.

Delivered reels live in `public/Creatives and Videos in General/Reel Scripts <Month>/` next to their script
(`Script N - <name>.mp4`) with a `Script N - assets/` folder (narration.wav, narration.txt,
words.json, scenes.json) so any reel can be re-rendered with a new voice/music/transition in one
command.

## Workflow D — LEGACY loud-caption VSL (superseded by Workflow E; only if Caio asks for "dynamic/loud" captions again)
Use when Caio asks for "dynamic / eye-catching subtitles" on a horizontal talking-head VSL. Command:
`python3 scripts/edit_vsl.py raw.mp4 words.json out.mp4` (captions from `scripts/dynamic_captions.py`).
34. Dynamic style = 1–3 UPPERCASE words, Plus Jakarta ExtraBold, thick outline + shadow, the spoken word turns magenta and pops (1.18 → 1.0 in 3 frames; power words — numbers, $, ROAS, CAC, profit… — pop 1.28 with glow). Keep layout gap ≥ 0.42·size or popped words collide.
35. Transcript: large-v3 AND medium.en, compare, then score doubtful phrasings with `prefix=` + avg_logprob on the clip. Retakes/stutters (heard twice) are simply omitted from the script text so the cut drops them. List every doubtful correction for Caio (VSL: "No ad account access…", "you can", "a 45-minute", "profit bottlenecks").
36. No colour grade, no music unless asked; alternating 1.00/1.09 punch-ins every ≥3.4 s at clause ends; thin magenta progress bar on the bottom edge; -14 LUFS.

### Workflow D, stage 2 — Limitless-style layer (Caio's reference VSL, 2026-10)
After `edit_vsl.py --keep-temp`, run `scripts/finish_vsl.py WORKDIR out.remapped.json out.mp4`. It replaces the loud
captions with MINIMAL ones (tiny lowercase white, word-by-word fade, no outline) and adds word-synced glass-card B-roll
(`vsl_graphics.py`: stat rows, chips, bar compare, checklists), floating stat/text callouts beside the speaker, and
white-flash transitions with whoosh SFX. Scene specs live in `build_scenes()` and are timed by phrase lookup, so retarget
them per script. Keep card text clear of the caption line (y > 900). Ref: public/Creatives and Videos in General/Rarity Dtc Ecom VSL/VSL Edition Ref.


## Workflow E — THE house format for anyone talking to the camera: Reels, ads AND VSLs (2026-10)
Caio: "I want the reels format and the ads in the same format when it's somebody talking to the camera." and, for the VSL,
"make the captions more minimalist… same edition as the Limitless Agency VSL". So **one engine, two sizes**:
`edit_vsl.py` (cut) → `finish_vsl.py` (captions + graphics + music). It replaces Workflow C/C2 for new work and
Workflow D's loud captions. The landscape VSL playbook (pipeline commands, scenes.json language, QA) is in the sibling skill
**`rarity-vsl-editor`** — read it; everything there applies to Reels/ads except the size and the positions below.

37. **Format = auto from the source.** Portrait source (or `--format vertical`) → 1080x1920; landscape → 1920x1080.
    `edit_vsl.py --cut-only --workdir W` fills the frame (cover+crop; low-res phone exports get `hqdn3d` + light `unsharp`),
    keeps `--pre 0.035 --post 0.06` tight cuts and `--punch 0.06 --punch-every 4.5` for ads/Reels (VSL defaults 0.05/0.13/0.09/3.4),
    never colour-grades. `finish_vsl.py` then renders cards on a design canvas of OUT/0.78 (1385x2461 for vertical) and
    scales down, so one `scenes.json` language serves both formats (`yv`/`xv` override positions for vertical).
38. **Vertical layout contract.** Captions: lowercase Benton 54 px, baseline y≈1510 (band y0 1300). Cards are full-screen
    (the speaker is hidden while a card is up — keep cards 2–9 s, speaker between them). Float callouts live in the lower
    strip at x≥500, y≈1130 (below the chin, right-aligned); Rarity symbol 64 px at x 976–1040, y 40–104. Keep card content
    above y≈0.72 of the height so captions never touch it.
39. **Creative ads = the VSL edition, no exceptions (Caio, 2026-10: "for the three ads I want the same style as the VSL, the same kind of edition… the same kind of edition for the VSL has to be for the creative ads as well").** The three Caio EN ads were re-edited this way (templates `ad_scenes_caio-01/02/03.json`); Workflow C/C2 looks (lower-third strips, Playfair key-word captions, name tag, line icons, progress bar) are retired. **Reels and ads are the same edit.** A 30 s Reel and a 180 s ad differ only in length: same captions, same card language
    (strike a wrong number, chips for lists, counting rows for numbers, compare bars for "$42 vs $62", checklist for what
    you get, big word for the offer, apply-below chip at the CTA), same flash+whoosh, same music. Aim for a graphic every
    ~4–8 s on ads; a 30 s Reel needs 2–4. No name tag / icon sets / progress bar from Workflow C2 unless asked.
40. **Music for talking heads = ELECTRONIC, excited and motivational, audible; ONE track family across every Caio video
    (Caio, 2026-10: deep house "not nice", then orchestral "bad music… keep the congruency, put electronic music a little more
    excited and motivational").** Default: `music/kraft-twerk-115.mp3` (Mixkit "Kraft Twerk", electronica, 117 BPM, major key,
    driving; only 9 % of its energy at 300-3400 Hz so it leaves the voice room). Alternatives to offer when Caio wants a
    different flavour: `motivating-mornings-033` (123 BPM, builds), `tech-house-vibes-130`. Orchestral (`epical-drums-*`) and
    deep house were REJECTED — don't use them for Caio. Same track on the VSL, the ads and the Reels so the channel sounds
    consistent. Build a bed to length with `scripts/music_bed.py <sec> bed.wav --track kraft-twerk-115.mp3`; level
    `--music-lufs -19 --duck-ratio 3` (≈ 7 dB under the voice while speaking, measured: -17 = 6.1 dB, -15 = 5.0; deep house at
    -26/ratio 9 was 14+ dB = "barely audible"). Measure (mix with/without music, music ≈ mix − voice, speech vs pause RMS),
    don't guess; the agent can't listen, so always say so and offer the next track.
41. **Transcript pipeline is shared** (`transcribe_two_models.py` → corrected `script.txt` → `align_to_script.py`); rules 11, 29
    apply unchanged (glossary prompt, two models, flag every doubtful correction, `CORRECOES-TRANSCRICAO.md` for PT/ES).
    Worked vertical example: `templates/ad_scenes_caio-02.json` (Caio EN ad, 6 cards over 79 s); worked landscape example:
    `templates/vsl_scenes_rarity-dtc-ecom.json`.
43. **Pacing knobs for short videos (`scenes.json` top level):** `"lead": 1.6` — a card pops in 1.6 s after its sentence starts, so the
    speaker is seen first; `"hold": 1.4` — a card hands the screen back 1.4 s after its last item. With these, a 100-170 s ad ends up
    ≈ 50 % cards + ≈ 12 % floating callouts (the ref VSL is ≈ 35-40 %; the landscape VSL was ≈ 59 %). Turn single-line ideas ("we call it the
    One Number Model", "one team, one number") into `float` text callouts instead of full cards; keep full cards for numbers, lists and
    comparisons. Items whose phrase precedes the (delayed) card start are clamped to appear right after it.
44. **Re-music / re-style without re-cutting:** the cut (`edit_vsl.py --cut-only --workdir W`) is reusable — keep `W` and re-run only
    `finish_vsl.py` (≈ 3-5 min) to change music, scenes or captions. Old versions are NOT kept (Caio: "just keep the most updated
    version on the project"): overwrite `<name> - EDIT.mp4` / `vsl-EDIT.mp4` and drop `assets/previous`.
45. **Portuguese / Spanish work the same.** `finish_vsl.py` strips accents when matching phrases ("máximo" = "maximo"), card text
    keeps its accents (Benton + Plus Jakarta both have them). Worked PT Reel: `templates/reel_scenes_diego-01-pt.json` (Diego, 45 s,
    cards ≈ 51 % + floats ≈ 27 %: strike ROAS, chips for Meta/Google/Klaviyo, CAC máximo permitido, 45 min, plano de 90 dias).
    Short Reels (< 60 s) want `lead` 0.3-1.4 per scene and `hold` 1.0 so the speaker stays visible; the PT edit still needs Diego's
    own corrections list (`CORRECOES-TRANSCRICAO.md`) confirmed against the audio.
42. **Output locations:** Reels `public/Creatives and Videos in General/Reel Scripts <Month>/`, BR edits `Rarity BR Edits/`, EN ads
    `Rarity EN Edits/` (`<name> - EDIT.mp4` + `assets/`), VSL `<VSL folder>/Edited-by-Claude/`. Never commit raw footage
    or renders (> 100 MB GitHub limit, public repo).
