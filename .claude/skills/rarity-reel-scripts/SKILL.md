---
name: rarity-reel-scripts
description: "Writes spoken-word video scripts for Caio, the founder of Rarity, to record himself as Reels / Shorts / podcast clips — talking head, street interview, podcast, or voiceover-over-B-roll, format varies per script. Grounded in Rarity's real day-to-day DTC/ecommerce operation and the agency's business as a whole, not generic marketing-guru content. Output is the spoken lines ONLY for on-camera formats, or a scene-by-scene breakdown (visual + sentence) for the voiceover B-roll format feeding rarity-reel-editor. One language per script: English primary, Portuguese (Brazilian) secondary, Spanish tertiary — a frequency mix across a batch, not simultaneous trilingual output (that's rarity-reel-dubbing, Step 2). ALWAYS use when Caio asks for a Reel script, video script, talking points, a voiceover/B-roll-style video idea, 'roteiro pro reels', 'script pra gravar', 'o que eu falo nesse vídeo', 'ideia pra um vídeo de voiceover', or wants a founder-voice video written. When in doubt, USE this skill."
---

# Rarity Reel Scripts (Step 1 — personal video pipeline)

This writes the **script**, not the video. For on-camera formats it produces what Caio says, start to
finish, so he can read or memorize it and record — Step 2 (`rarity-reel-dubbing`) then takes the
recorded take and produces AI-dubbed, lip-synced versions in the other two languages. For the
voiceover B-roll format it produces a scene-by-scene breakdown instead, which skips straight to Step 3
(`rarity-reel-editor`). This skill never touches audio or video itself either way.

**This is Caio's own voice, not Rarity's brand voice.** The IG pipeline (`rarity-ig-*`) writes for
@rarity.agency / @rarity.es / @rarity.br as an editorial brand account. This skill writes for Caio
the person — founder of a DTC/ecommerce performance agency, talking in first person about what he
actually sees running it. Never slip into the brand's third-person "decode" register here.

## Non-negotiables
1. **Real anchor required, same discipline as the IG pipeline.** Every script is built on something
   real: either (a) a real thing Caio tells you directly — a client situation, a number from an
   account he runs, a decision, a mistake, an internal debate — trust what he says as the anchor, or
   (b) a real, current, verified DTC/ecommerce industry trigger he's reacting to in first person
   (sourced via live search, same standard as `rarity-ig-trend-scout`). Never invent a stat, a client
   result, or a "this happened to me" story.
2. **One idea per script.** Same rule as the IG posts. If it takes two breaths to explain, it's two
   scripts, not one with a detour.
3. **First-person founder voice.** "I" and "we" statements. Direct, a little blunt, opinionated,
   operator-credible — someone who actually runs ad accounts and manages a DTC agency, not a
   generic LinkedIn-guru voice. See `references/caio-voice.md`.
4. **The hook doctrine, adapted for speech.** The first ~3 seconds (roughly 6-12 spoken words) must
   do real scroll-stopping work, built on ONE named trigger: CONTRARIAN, AUTHORITY/ANTI-HERO,
   INNOVATIVE IDEA, APPARENT NONSENSE, or EXTREME CURIOSITY (same five as the IG pipeline — see
   `references/spoken-hook-doctrine.md` for how each one sounds said out loud vs. written as a
   headline). Name which trigger you used.
5. **Written to be SAID, not read.** Short sentences. Contractions always. The way someone actually
   talks when they're fired up about something, never the more composed editorial register the IG
   captions use. Read every draft out loud (mentally) before shipping — if it sounds like it's being
   read aloud rather than genuinely said, rewrite it.
6. **Length matches the format**, calibrated at natural speaking pace (~150 words/minute):
   - Talking-head / direct-to-camera Reel: 30-75 seconds → roughly 75-190 words.
   - Podcast-clip style take: can run longer, 60-120 seconds → roughly 150-300 words.
   - Street-interview format: mostly reactive, so the "script" is a short list of planned beats or
     answers Caio can riff from in his own words, not a verbatim read — say so explicitly when you
     produce this format.
   - Voiceover B-roll format: 15-30 seconds total, broken into 4-7 scenes of roughly one sentence
     each (~10-20 words/scene at speaking pace) — matches `rarity-reel-editor`'s Workflow B, where
     each scene is shown for exactly as long as its sentence takes to say.
7. **No forced CTA.** The close is one direct, natural final line that lands the point — a challenge
   to the viewer, a blunt conclusion, sometimes just the punchline landing with nothing after it.
   Never a "like and subscribe" / follow-pitch close, and never the IG pipeline's "save and share"
   line — that's brand-account language, not how a founder ends a take.
8. **Output is the spoken lines ONLY for on-camera formats** (talking head, podcast clip, street
   interview — confirmed directly by Caio, 2026-10). No shot list, no b-roll notes, no on-screen text
   cues, no camera direction. Just what he says. The voiceover B-roll format (Non-negotiable 10) is the
   deliberate, explicit exception — there, a visual note per scene is the whole point.
9. **One language per script.** Default English unless Caio names Portuguese or Spanish for that
   specific script. Mark the language at the top. When producing a batch without per-script language
   direction, mix roughly: majority English, some Portuguese (Brazilian), fewest Spanish — don't force
   every batch into an even split, and don't default to English out of habit when Caio asked for a mix.
10. **Voiceover B-roll format: write scene-by-scene, and only to real, sourceable, congruent visuals.**
    This format (consumed by `rarity-reel-editor`'s Workflow B) has no face on camera — narration plays
    over a sequence of B-roll clips, one per sentence. When writing for it:
    - Break the script into 4-7 short scenes, each one sentence (see Non-negotiable 6 for length).
    - For every scene, write a one-line **visual note** naming the concrete, literal thing the B-roll
      should show (e.g. "a hand scrolling TikTok on a phone," "someone entering a card number at
      checkout") — not a mood or metaphor ("the feeling of urgency"). The sentence must describe
      something a real, ordinary stock-footage clip could literally show.
    - Before finalizing, sanity-check each scene against `rarity-reel-editor`'s own congruence bar
      (its Non-negotiable 7, "muito congruente com o que é falado," added after a real incident where
      a "dashboard" line got paired with an unrelated forex-trading clip): would the obvious, literal
      B-roll search for this visual note actually surface something that matches the sentence, or is
      the wording abstract enough that it's likely to pull a mismatched clip? If a line reads as
      abstract/metaphorical, rewrite it concrete before handing it off — don't leave that problem for
      the editing step to discover.
    - Deliver the script as a numbered scene list: `visual note → sentence`, one block per scene, so it
      can be turned almost directly into a `rarity-reel-editor` Workflow B manifest (one JSON object per
      scene once real clips are sourced).

## Workflow

### 1. Intake
- **Caio named a topic/story** → use it directly. Only ask a clarifying question if a specific
  external number or claim inside it needs pinning down (same verification bar as the IG pipeline —
  never invent a figure). A personal anecdote or operational detail he states is trusted as-is; it's
  his own business.
- **Caio wants ideas / didn't name a topic** → do both of the following and present options together:
  (a) ask if there's a specific Rarity/operational angle on his mind right now (a client win, a
  platform change affecting accounts he runs, a mistake worth sharing), and (b) run a live search for
  current DTC/ecommerce news or trend triggers (same method as `rarity-ig-trend-scout`:
  `tavily-search`/`rss-reader`, real and sourced, last few days). Present 3-5 short pitches (one line
  each: the real anchor + the angle), and wait for Caio to pick before writing the full script.
- **Format** (talking head / street interview / podcast clip / voiceover B-roll) — use what Caio
  specifies; if unstated and it would change how you write the script (verbatim vs. talking-point
  beats vs. scene-by-scene), ask once. Voiceover B-roll is the right call when Caio describes a video
  with no face on camera — "um vídeo de voiceover," "monta um vídeo com imagens/clipes passando,"
  an explainer/listicle-style idea — or when he asks for an idea for that format directly.

### 2. Hook
Pick the sharpest of the five triggers for this specific anchor (see
`references/spoken-hook-doctrine.md`). Draft 2-3 opening-line candidates before settling — the first
line is the highest-leverage line in the whole script, same as the IG headline.

### 3. Write the script
Hook → the real story/insight in Caio's own voice → the takeaway/payoff → a natural spoken close.
Keep it to the one idea from Non-negotiable 2. Write it as continuous spoken lines (not bullet
fragments) unless the format is street-interview (short list of beats) or voiceover B-roll (numbered
scene list of visual note + sentence, per Non-negotiable 10).

### 4. Voice-check before shipping
Read it out loud (mentally). Cut anything that reads like copy rather than talk: no "leverage,"
"unlock," "game-changer," or other written-marketing filler; keep sentences short; keep contractions;
vary sentence length the way real speech does. See `references/caio-voice.md` for the specific
banned-phrase list and worked before/after example.

### 5. Save and deliver
- Save as `public/Instagram Briefings/Reel Scripts <Month>/Script N - <Short Name>.md`. `<Month>` is
  the current month by default (match the existing `Ideas <Month>` / `Designs <Month>` convention
  already used in this project); create the folder if it doesn't exist. Continue numbering from the
  highest existing `Script N` in that folder; never restart at 1.
- The file content is just: a one-line header (language, format, hook trigger used, rough word
  count/duration), then the script itself (scene list, for voiceover B-roll). No other metadata.
- Show the script in chat too.
- If a dubbed multi-language version is wanted once Caio records this, point him to
  `rarity-reel-dubbing` (Step 2) — don't attempt dubbing or translation yourself here. This only
  applies to on-camera formats; voiceover B-roll scripts go straight to `rarity-reel-editor` instead
  (no face to dub — see that skill's Workflow B).

## Batch requests
If Caio asks for several scripts at once (a week's worth, a content sprint), rotate: the anchor type
(his own story vs. an industry trigger), the hook trigger (don't reuse the same one twice in a row),
and the language mix per Non-negotiable 9. Give a one-line index (language · format · hook trigger ·
one-line topic) at the top so he can scan the batch before reading each script in full.

## Relationship to the other skills
This is Step 1 of Caio's personal video pipeline, and it branches by format:
- **Talking head / podcast clip / street interview** → Caio films it → `rarity-reel-dubbing` (Step 2)
  consumes the *recorded video* to produce the other two language versions → `rarity-reel-editor`
  (Step 3) cuts, captions, and brands it.
- **Voiceover B-roll** → no face to dub, so Step 2 is skipped entirely. This skill's scene list goes
  straight to `rarity-reel-editor`'s Workflow B: source/confirm a real, congruent clip per scene
  (`rarity-reel-editor` Non-negotiable 7), record or generate the narration, then build.

This skill is independent of the `rarity-ig-*` brand pipeline (idea-engine / designer / captions /
publish) — different voice, different account (Caio personally, not @rarity.agency), do not mix the
two.
