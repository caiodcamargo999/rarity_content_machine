# Rarity Brand System — IG design spec

The canonical visual identity for Rarity Agency Instagram art. Source: Rarity rebrand palette +
brand fonts (in the project's "Branding Rarity" folder). Values are exact — use them, don't approximate.
The house look follows the reference feeds (@vinci.society, @brandsdecoded__, @blankschoolbr,
@matthgray): a big **editorial serif** headline over a **full-bleed, high-impact photo**, on every slide.

## Color palette

### Backgrounds
| Role | Hex | Notes |
|---|---|---|
| Primary tint | `#001A70` | Deep navy. The cohesive duotone tint laid lightly over every photo. |
| Alt background (deep) | `#0f0a1a` | Very dark purple (Rarity BR LP). For the darkest scrims. |
| Alt background (mid) | `#1a0f2e` | Dark purple. Gradient partner to `#0f0a1a`. |

Note: the brand navy is NOT laid over photos. Photos render in their REAL colours. There are still no solid or gradient-only slides.

### Accent — ONE per slide; colours the italic word + stat number + kicker dash
| Role | Hex | Notes |
|---|---|---|
| Magenta (default) | `#D50057` | The everyday accent. |
| Shock yellow | `#FFE400` | High-vis. Use SOMETIMES to spike attention. |
| Shock red | `#FF3B3B` | Urgency / alarm. Use SOMETIMES. |
| Teal (secondary) | `#0fc1af` | Eyebrow / stat label only. |
Vary the accent across a post or batch — magenta by default, **yellow or red to grab attention**. Set it
per post (`"accent"`) or per slide (slide-level `"accent"`).

### Energy gradient (drama on scrims / stat slides)
Blue → purple → magenta. Stops:
`#0046FF` (pure blue) → `#9B00C8` (intense purple) → `#D50057` (vibrant magenta).

### Text — ADAPTIVE, not fixed (2026-07-11, hard rule from Caio)
Every text element's colour is chosen at render time by sampling the actual photo underneath it:
**dark background → light letter, light background → dark (navy) letter.** There is no single
"the headline is always white" rule anymore — white is the letter colour on a dark zone, navy
`#001A70` is the letter colour on a light zone, and the engine (`render_post.py` v6, `adapt()`)
picks per text block automatically. This replaced an earlier approach (v5) that kept text fixed
white and tried to darken the photo behind it with a blurred patch — that either looked like a
hard-edged sticker or still didn't hit 4.5:1 on light photos. Letter colour doing the adapting,
not a patch sitting on the photo, is what keeps the set feeling like real photography rather than
photos with graphic chips stuck on top ("harmony," per Caio's direction).

| Role | Dark-bg colour | Light-bg colour | Notes |
|---|---|---|---|
| Headline (hook/body/CTA) | `#FFFFFF` white | `#001A70` navy | Whole headline is ONE colour (sampled once over its zone), never mixed mid-block. |
| Subhead / stat sub | `#c6cee4` muted light | `#2E364E` muted dark | Same adaptive logic, softer pair. |
| Eyebrow / kicker / stat label | `#0fc1af` teal | `#001A70` navy | Teal is the dark-bg version; on a light zone it drops straight to navy (a "darker teal" doesn't read as branded or legible enough). |
| Handle / page counter | `#ececec` off-white | `#34394A` dark grey-navy | |
| CTA logo image | `rarity-logo-white.png` | `rarity-logo-blue.png` | Same adapt logic, applied to which logo ASSET gets pasted, not just text. |

The italic accent word stays **magenta `#D50057` always**, regardless of background — it's the
brand signature, small enough (1-2 words) that it doesn't carry the block's main legibility job;
the surrounding adaptive white/navy text does that.

(Machine-readable copy of the old fixed values still ships as `assets/rarity-colors.json` for
reference; the live source of truth for the adaptive pairs is `render_post.py`'s own colour
constants — `WHITE`/`NAVY`, `MUT`/`MUT_DARK`, `TEAL`/`TEAL_DARK`, `HANDLE_LIGHT`/`HANDLE_DARK`.)

## Typography — editorial serif (the @vinci.society direction)
The headline voice is a **high-contrast editorial SERIF**, not a condensed sans. This is the single
biggest identity cue of the reference feeds.

- **Headline / display: Playfair Display** (bundled at `assets/headline.ttf`, with the italic at
  `assets/headline-italic.ttf`). High-contrast Didone serif. Set headlines in **sentence case**
  (not all-caps). Big, bottom-anchored over the photo, colour ADAPTIVE — white on a dark zone,
  navy on a light zone (see the Text table above), never fixed white.
- **The italic is the accent.** One or two emphasis words per headline are set in **Playfair Italic +
  the magenta accent** — the vinci.society signature. In the brief / spec, wrap those words in
  `*asterisks*` and the engine renders them italic + accent automatically.
- **Body / eyebrow / kicker / handle: BentonSans** — `assets/BentonSans-Regular.otf` and
  `assets/BentonSans-Thin.otf`. Clean grotesque for the small supporting text (eyebrow, subhead,
  stat sub, handle, page counter).
- Pairing rule: the serif carries the idea, BentonSans handles the labels. Never set the headline in
  BentonSans; never set body labels in the serif.
- **Swap in a licensed serif** by dropping it at `assets/headline.ttf` (+ `assets/headline-italic.ttf`)
  — e.g. the exact font a reference brand uses. The engine picks it up automatically. Playfair is the
  free, embeddable default.

### Type scale (1080x1350 canvas)
| Element | Font | Size (px) | Case | Color |
|---|---|---|---|---|
| Hook headline | Playfair (serif) | 108–132 | Sentence | adaptive white/navy, italic accent word always magenta |
| Body headline | Playfair (serif) | 84–104 | Sentence | adaptive white/navy, italic accent word always magenta |
| Stat number | Playfair (serif) | 180–236 | — | magenta `#D50057` always (not adaptive — it's the accent) |
| Eyebrow / kicker | BentonSans | 24–28 | UPPER, tracked | adaptive teal `#0fc1af` / navy |
| Subhead / stat sub | BentonSans | 30–34 | sentence | adaptive muted-light `#c6cee4` / muted-dark |
| Handle / page no. | BentonSans | 23–27 | lower | adaptive off-white / dark grey-navy |

## Headline accent — italic, in the accent color
The emphasis in a Rarity headline is carried by **an italic word in magenta**, not by an off-brand
poster color. Pick one (occasionally two) words that turn the line and wrap them in `*asterisks*`.
Everything else in the headline is white. Keep it to one accent idea per slide.

## Logo & symbol (real assets ship in this skill's `assets/`)
- **`rarity-symbol-white.png`** — the "Y" diamond mark as a clean **transparent white** silhouette
  (no white box). This is the corner stamp for dark photos.
- **`rarity-symbol-color.png`** — the same mark keyed transparent but keeping its magenta / light tone
  (optional, for special light layouts).
- **`rarity-logo-white.png`** — full "RARITY / AGENCY" wordmark in WHITE (transparent). CTA slide.
- **`rarity-logo-blue.png`** — full wordmark in navy. Only on light backgrounds.
- `rarity-symbol.png` — the legacy raster with a baked white background. **Do not place this one on
  slides** (it drops a white box); use `rarity-symbol-white.png`.

**Symbol-in-corner rule — on EVERY slide.** Place `rarity-symbol-white.png`, small (~54–60px on 1080),
in a consistent corner — **default top-right**, ~80px margin, transparent (no box, no chip). Same size
and position across the set so the grid reads as one system. It is a stamp, never a focal element.

**Full logo** appears on the **CTA / closing slide**, colour ADAPTIVE like the text: `rarity-logo-white`
on a dark zone, `rarity-logo-blue` on a light zone (the engine samples the logo's own patch and picks).
The corner symbol still sits top-right for consistency (white only — no navy symbol asset exists yet;
low-stakes since it's a small recede-tier mark, not primary reading text).

## NO date on the card
Never render a month, year, or any date label on a slide (no "JULY 2026", no "2026"). Briefs are still
FILED by month in `public/Instagram Briefings/`, but nothing dated appears on the art itself.

## Photo treatment — REAL COLOUR (no brand wash)
The photo shows in its **real colours** — do NOT wash the image with brand navy. The engine only adds a
soft neutral vignette + a bottom scrim (so the bottom-anchored headline stays legible) + faint film
grain. The image is the hero of the slide; keep it vivid. Only the CTA slide gets a light NEUTRAL darken
so the centred logo + line read — still not a colour wash. Push the bottom scrim a touch on a busy photo
rather than tinting the whole frame.

## Spacing & composition
- Outer margin: ~80px on a 1080-wide canvas.
- One focal idea per slide. Text bottom-anchored, left-aligned (hook / body / stat); centered on the CTA.
- Generous negative space in the upper frame where the photo breathes — premium brands don't crowd.
- Keep key text out of IG safe zones (see viral-layouts.md).
- **Headline-to-subhead gap (hook slide): minimum 56-60px** between the headline block's bottom
  anchor and the subhead's top. A serif at 110-130px has real descenders (g, y, periods) that extend
  visibly below the nominal line box — a tight ~24px gap (v5's old default) let the last headline
  line's descenders collide with the subhead text below it. Found + fixed 2026-07-11; don't tighten
  this back down even if a spec looks like it has "extra" white space, that space is descender
  clearance, not slack. Headline internal line-height (`lead`) is 1.12, also loosened from v5's
  tighter 1.05-1.06 for the same breathing-room reason.

## Don't
- No condensed-sans / all-caps poster headlines (that's the OLD look — the identity is serif now).
- No flat, solid, or gradient-only slides. No slide without its own photo.
- No white box behind the symbol; no month / year on the card.
- No drop-shadow soup, no stroked text, no more than two type sizes per slide.
