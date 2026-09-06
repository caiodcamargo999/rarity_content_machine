# Design Principles — hierarchy, rhythm, and the legibility bar

Ported and adapted from BrandsDecoded's own design-principles skill, translated to English and rebuilt
for Rarity's photo-only system (no dark/light card binary — every slide is a full-bleed contextual
photo; see `viral-layouts.md` and `rarity-brand-system.md`). Read this alongside those two files before
rendering; use it to judge a slide, not just to build one.

## 1. Three-level visual hierarchy
Every slide has exactly three tiers of visual weight. If two elements compete at the same weight, the
hierarchy is broken — fix it before moving on.

- **Anchor (the one thing the eye lands on first):** the headline on the hook, the big focal
  word/number on a body slide, the trigger line. Biggest, boldest, highest contrast. Exactly one per
  slide.
- **Context (supports the anchor):** the one short supporting body line that pays off the focal word,
  the open loop subhead under the hook headline. Smaller, quieter, never competing with the anchor.
- **Metadata (frames the slide but isn't the point):** eyebrow/kicker, slide-number counter, the
  `@rarity.agency` handle, the corner symbol. Smallest, most muted. It should recede.

**The test:** cover the slide and ask what the eye sees first. If the answer is ambiguous, or if you'd
answer "the headline AND the supporting line" in the same breath, the two are fighting — resize one.

## 2. Rhythm across the set
Rarity has no dark/light binary to alternate (BrandsDecoded's own system leans on that), so rhythm has
to come from three other levers instead:

- **Vary photo mood and crop.** Don't let every body slide use the same framing (e.g. all
  medium-shot, all centered). Alternate wide environmental shots with tighter detail crops so the
  carousel has visual movement when swiped quickly.
- **Text density breathes with the photo.** A busy, detailed photo can hold less text before it turns
  illegible — drop to just the focal word/number and cut the supporting line. A calmer, simpler photo
  (open sky, plain wall, negative space) can hold a full two-line supporting sentence.
  **Rule of thumb: busier photo → fewer words.**
  - Simple/plain image → focal element + full supporting line (both context and anchor active).
  - Busy/detailed image → focal element alone, supporting line cut or shortened to a fragment.
- **Gradient-drama as a deliberate rhythm break.** For the Mindset & High Performance pillar, the
  blue→purple→magenta gradient (see `rarity-brand-system.md`) is allowed to replace the photo
  background on ONE slide (typically the takeaway, right before the CTA) to mark an emotional turn. Use
  it as punctuation, not wallpaper — if every slide uses it, it stops reading as a break.

## 3. Content anchoring + the empty-slide escalation ladder
Every slide must contain something concrete to anchor to — a real number, a named fact, a specific
image, not a vague motivational statement floating in space. If a slide idea comes out feeling empty
("Show up before everyone else." with nothing under it), don't ship it thin. Escalate in this order:

1. **Size up the headline/stat.** Sometimes the content is fine but under-presented — make the focal
   number or word bigger and let it fully own the slide.
2. **Add one supporting line, if there's a genuine one to add.** Not filler — an actual fact, consequence,
   or specific example that earns its place. If you can't write one that passes `editorial-qa.md`'s
   density test, don't force it.
3. **Pick a busier or tighter photo crop** so the image itself carries more of the slide's weight and the
   text can stay minimal without feeling empty.
4. **Last resort: flag it back to the brief.** If a slide still feels empty after 1–3, it probably
   doesn't have enough material to be its own slide — tell Caio to merge it with the neighboring slide
   rather than shipping a thin one. Anchored beats padded, always.

Compare: *"Show up before everyone else."* (generic, floats free of any fact) versus *"127 people on a
waitlist. Zero ad spend."* (anchored — a real number, a real absence, an implicit mechanism). The second
version needs no extra line; the number does the work.

## 4. Typography discipline
- **Never give two elements the same font, weight, AND size.** If the anchor and context line share all
  three, they're visually the same tier and the hierarchy collapses (see section 1).
  Following `rarity-brand-system.md`'s type scale keeps this automatic — the condensed headline font
  and BentonSans are never interchangeable, and the scale spaces sizes far enough apart that no two
  tiers are visually adjacent.
- **The accent color is a scalpel, not a highlighter.** Cap any teal or pop-color emphasis to 2–3 words
  per slide — accenting a whole line or sentence defeats the point of an accent.
- **Body copy is never uppercase.** Uppercase is reserved for the condensed headline font display type
  (headlines, focal words/numbers). Sentence-case or lowercase body copy is what signals "this is the
  explanation," not "this is the shout."

## 5. Quantified legibility bar
These are hard numbers, not vibes — check them on every slide before calling it done:

- **Contrast: minimum 4.5:1** between text and its background (photo + scrim combined).
  - **This is now measured, not eyeballed.** `render_post.py` (v6+) prints a `[contrast]` line for every
    text zone on every slide — which letter colour it picked (light or dark) and the resulting ratio
    against the 4.5:1 bar, sampled from the actual rendered pixels. Read the printed lines after every
    render; don't just look at the PNG.
  - **The fix mechanism is ADAPTIVE LETTER COLOUR, not a patch on the photo (2026-07-11, hard rule from
    Caio).** Every text element — headline, subhead, eyebrow, kicker, handle, page counter, even the CTA
    logo asset — samples its own local background luminance and switches between a light colour (dark
    bg) and navy (light bg); see `rarity-brand-system.md`'s Text table for the exact pairs. This replaced
    v5's approach of keeping text fixed white and hiding a blurred dark patch behind small text: that
    either read as a hard-edged sticker (tight blur) or still missed 4.5:1 (loose blur), and either way
    put a graphic element on top of the photo that broke "real photo colours, no wash." There is no patch
    anymore — the photo shows through completely clean, the letter colour does the work.
  - **If a zone is STILL flagged `LOW CONTRAST` after adapting, that means the zone is genuinely mid-gray**
    — neither white nor navy wins clearly against it (this happens on backgrounds sitting right around
    18-30% luminance, common on a photo with only a light `dark=` overlay). Fix it the same way as
    before: change `focus_x`/`focus_y` onto cleaner negative space, or raise that slide's `dark=` a bit
    so the zone lands clearly on one side (dark) rather than in the middle — `dark=` is now a mood/mode
    knob that decides which pole a zone sits on, not the primary contrast mechanism itself.
- **Headline length: 4 lines maximum.** Past that, either the headline is doing too much (split the
  idea across two slides) or the type size needs to come down — but never below the type scale's floor
  in `rarity-brand-system.md`.
- **Margins: 56px inner text margin, 80px outer canvas margin** on the 1080-wide canvas (matches
  `viral-layouts.md`'s safe-zone spec — this is the same rule stated in pixel terms for the render step).
- **No headline, eyebrow, or kicker may sit on top of the photo's busy subject** — a face, a logo, a
  cluttered detail. These read as visually "dirty" even when contrast is technically fine (a patch behind
  the text can save the ratio but not the collision). Choose `focus_x`/`focus_y` so that zone lands on
  genuine negative space — sky, out-of-focus background, a plain wall — the same way `image-sourcing.md`
  already asks you to pick images with a clean zone for the headline; the eyebrow/kicker needs that same
  clean treatment, not just the headline.
- **The symbol and handle must never share a color with their background.** If a slide's corner happens
  to be a light sky or white shirt, the white-bodied symbol disappears — switch to a navy-tinted symbol
  variant or nudge its position to a darker part of the frame rather than letting it vanish.

## 6. CTA bridge check
The CTA slide's line must connect back to the specific theme of THIS carousel, not read as a generic
sign-off that could close any post ever made. This is fundamentally a copy problem, not a rendering
one: if the CTA line feels generic when you reach this step, that's a signal to flag it back to the
brief (`rarity-ig-idea-engine`) for a rewrite rather than trying to fix it by changing fonts or colors at
render time. A render can't fix a copy problem.

## 7. Visual anti-patterns (Rarity's photo-only system)
Reject any of these on sight:
- Centered text anywhere except the CTA slide — body/hook text is left-aligned per `viral-layouts.md`.
- Two paragraphs of equal visual weight on one slide (violates section 1's hierarchy rule).
- A zone where contrast drops under 4.5:1 even after adaptive letter colour picked its best option
  (check the render's printed `[contrast]` lines, don't eyeball it) — means the crop needs to change.
- Eyebrow, kicker, or headline text sitting on top of a face, logo, or other busy photo detail — even if
  adaptive colour keeps it technically legible, it still reads as a collision. Re-pick `focus_x`/`focus_y`.
- A headline block sitting closer than ~56-60px above the subhead/handle below it — descenders on a
  110px+ serif need that clearance (see `rarity-brand-system.md`'s spacing section).
- An accent color applied to more than 2–3 words.
- A sentence-case or lowercase headline (headlines are always UPPER per the type scale).
- Uppercase body copy.
- More than ~25–30 words of body copy on a single body/stat slide — that's a paragraph, not a slide.
- An orphan fragment slide that doesn't anchor to any concrete fact (see section 3's ladder).
- Three or more consecutive slides that are visually interchangeable (same crop style, same layout,
  same text length) — breaks the rhythm described in section 2.

## 8. Contact-sheet check (final step, every time)
Before calling a set done, view all slides together as a strip or grid — not one at a time. This is the
only way to catch: repeated crops back-to-back, an accent color used inconsistently, a hierarchy break
that only shows up in comparison, or a rhythm that's flat across the whole carousel. If a full-set
export/contact-sheet tool isn't available, lay screenshots of each slide side by side before delivering.

## Where this fits
This file governs how a slide should look once built; `viral-layouts.md` governs what goes on which
slide type (hook/body/stat/CTA structure); `rarity-brand-system.md` governs the exact colors, fonts, and
asset files to use. Check a rendered set against all three before delivering — this file is the one to
reach for when something looks "off" but you can't immediately say why.
