# Claude Render Engine — how the design gets made (NO connectors)

The whole design is produced by `scripts/render_post.py` (Python/Pillow). No Canva, no Figma — ever.
It outputs 1080x1350 PNGs in the reference editorial style (@vinci.society): **every slide is its own
full-bleed photo** run through the house treatment (a light navy duotone so the photo stays the focus,
vignette, bottom scrim, film grain), with a big **editorial serif** headline.

## Fonts (editorial serif, NOT condensed sans)
- Headline: **Playfair Display**, a high-contrast Didone serif — `assets/headline.ttf` (roman) and
  `assets/headline-italic.ttf` (italic). Sentence case, white.
- **Italic accent:** wrap emphasis word(s) in `*asterisks*` in any headline / cta line → the engine sets
  them in Playfair Italic + the accent color (magenta). This is the vinci.society signature.
- Body / eyebrow / kicker / subhead / handle: **BentonSans** (bundled).
- Swap in a licensed serif by replacing `assets/headline.ttf` (+ `-italic`); the engine auto-detects it.

## Step A — a DISTINCT photo for EVERY slide (automatic)
Every slide REQUIRES its own `"bg"` (a real image path). Save to
`public/Instagram Briefings/Designs <Month>/<Idea N - Name>/`: `hero.jpg` (slide 1) and `bg/bg2.jpg ... bgN.jpg`.
Download each DISTINCT direct URL from the brief's IMAGES table yourself. The engine ERRORS on any slide
without a photo — that is intentional (no flat / solid / gradient cards, and no reusing one image for the
whole set).

## Step B — write the spec JSON
```json
{
  "out_dir": "<.../Idea N - Name/EN>",
  "handle": "@rarity.agency",
  "accent": "#D50057",
  "slides": [
    {"type":"hook","bg":"<.../hero.jpg>","focus_x":0.5,"focus_y":0.42,
     "eyebrow":"Eugene Schwartz, 1966",
     "headline":"You can't *create* desire.","size":126,
     "subhead":"What the most stolen book in advertising knew about your ads ->"},
    {"type":"body","bg":"<.../bg/bg2.jpg>","kicker":"The mistake",
     "headline":"Most brands burn millions *shouting* at people who will never buy.","size":94},
    {"type":"stat","bg":"<.../bg/bg3.jpg>","stat":"85%","label":"of ads are ignored",
     "sub":"Because they sell the product, not the desire already in the room."},
    {"type":"cta","bg":"<.../bg/bg4.jpg>",
     "headline":"Save this. *Send it* to someone who runs ads.","size":98}
  ]
}
```
Notes:
- Photos render in their REAL colours (no brand-navy wash) — only a bottom scrim + vignette for legibility.
- `accent` may be set per post OR per slide: magenta `#D50057` (default), shock yellow `#FFE400`, or red
  `#FF3B3B`. It colours the italic word, the stat number, and the kicker dash. Optional `head_color` sets
  the whole headline in a shock colour.
- No `date_label` — there is no date anywhere on the card.
- Each slide has its OWN `bg`. An image may serve 2 slides max, as different crops.
- `*asterisks*` = italic + accent word(s). With no asterisks, the last wrapped line auto-accents in
  magenta (set `"accent_last": false` to keep it white). Use the arrow character in the subhead.
- `focus_x` / `focus_y` (0–1) choose the cover-crop focal point.

Slide types (all photo-backed):
- `hook` — brightest photo, bottom scrim, top strip (RARITY AGENCY left, symbol top-right), teal
  eyebrow, big serif headline bottom-left (italic accent word in magenta), open loop `subhead` under it.
- `body` — photo at context level, page counter bottom-right, symbol top-right, optional teal `kicker`
  (dash + word), serif headline bottom-left, handle bottom-left.
- `stat` — like body with a giant magenta serif number + teal `label` + `sub`.
- `cta` — darker photo, white logo centered, the SAVE + SHARE sentence in the serif (italic accent),
  centered, small handle under. **NO button.**

## Step C — render + verify like a creative director
```
python3 <skill>/scripts/render_post.py <spec_en.json>
```
The script prints a `[contrast]` line per text zone per slide — which letter colour it picked (light or
navy-dark, adaptive per `rarity-brand-system.md`'s Text table) and the resulting ratio against the 4.5:1
bar from `design-principles.md`, measured off the actual rendered pixels. **Read this output before
opening a single PNG.** Anything still flagged `LOW CONTRAST` after adapting means the zone is genuinely
mid-gray (neither light nor navy wins) — move `focus_x`/`focus_y` onto cleaner negative space, or raise
that slide's `dark=` a bit so the zone commits to one pole — not a re-run of the same spec hoping it
reads differently the second time.

Then open each `slide-N.png`. Fix overflow (lower `size`), bad crops (move `focus_x` / `focus_y`), a
photo buried too dark or washed too bright, monotony (each slide's photo must look different), any
headline/eyebrow/kicker sitting on top of a face or busy detail (adaptive colour keeps it readable but
it should still not be there — recrop), and any text block sitting closer than ~56-60px above the line
below it (serif descenders need that clearance — see `rarity-brand-system.md`). Expect at least one
polish pass.

## Step D — Spanish
Copy the spec, swap each line to the ES copy (keep the `*italic*` accent words; ES runs longer — drop
`size` a step where needed), same `bg`s, `out_dir` → `ES/`. EN and ES must look identical except language.

## Step E — Portuguese
Copy the spec again, swap each line to the brief's Brazilian Portuguese copy (keep the `*italic*` accent
words; PT, like ES, often runs longer than EN — drop `size` a step where needed), same `bg`s, `out_dir`
→ `PT/`. EN, ES, and PT must all look identical except language — same fonts, same brand colors, same
layout, only the copy changes.

## Layout (reference standard)
Every slide: full-bleed photo → light navy duotone + vignette + bottom scrim → top strip (RARITY AGENCY
left, transparent symbol top-right) → bottom-anchored serif headline (adaptive white/navy, italic accent
word always magenta). Hook adds an adaptive teal/navy eyebrow + open loop subhead + handle. Body / stat
add an adaptive kicker / label + page counter + handle. CTA centers the adaptive-colour logo asset +
save/share sentence + handle. No date, ever. Keep key text out of the bottom ~210px (IG UI). High
contrast always — measured by the render's own `[contrast]` output, not just eyeballed (see
`design-principles.md` section 5), and never sitting on top of a face or busy detail even when adaptive
colour keeps it technically legible.
