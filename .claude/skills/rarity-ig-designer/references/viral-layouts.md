# Viral Layouts — static & carousel patterns

How to lay out Rarity posts so they stop the scroll and get saved. Grounded in what actually performs
on Instagram feed today. Combine with `rarity-brand-system.md` for colors/fonts and
`design-principles.md` for hierarchy, rhythm, and the legibility bar.

## Canvas & safe zones
- **Default canvas: 1080 × 1350 px (4:5 portrait).** Takes the most vertical feed space → more attention.
- Square 1080 × 1080 is allowed if Caio asks.
- **Safe zones (keep key text/logo clear):**
  - Bottom ~250px: caption preview, like/comment/share UI, carousel dots.
  - Top-right ~140px: nothing critical (profile/menu overlay zone in some views).
  - Keep a ≥80px outer margin everywhere.

## What makes feed content go viral (apply all)
1. **One idea, one focal point.** The eye should land in <0.5s. Kill competing elements.
2. **Big, bold headline.** Display type at 96–140px. Small text loses on mobile.
3. **High contrast.** Dark scrim under light the condensed headline font text. If you squint and can't read it, fix it.
4. **A face / eye-contact** in the hero photo when possible — faces out-perform objects for stopping
   power. Every image passes the SHOCK BAR: emotion, drama, strangeness or scale; never a posed,
   stock or common shot. The charged version of the subject, always (the scream, not the headshot).
5. **Tension in the words.** A flip, a cost, a number-shock (the headline patterns from Step 1).
6. **Brand consistency.** Same fonts, same navy/teal, same logo placement every time → a recognizable grid.
7. **Save-worthiness (carousels).** A clear payoff/framework people want to keep → saves drive reach.
8. **Consistent corner symbol.** The Rarity symbol sits small in the same corner on every slide →
   instant brand recognition across the grid (brand system: top-right, ~90px). Just the symbol.

---

## STATIC post (and carousel slide 1 = the hook)

```
┌───────────────────────────────┐  1080 × 1350
│                       ◆ symbol │  ← Rarity SYMBOL, small, top-right corner (on every image)
│                               │
│         HERO PHOTO            │  full-bleed, scaleMode FILL, face/eye-contact, B&W or high-contrast
│        (full-bleed)           │
│                               │
│░░ gradient scrim navy→clear ░░│  ← bottom-up gradient for legibility (rarity-brand-system.md)
│ ▌ THE HEADLINE                │  ← the condensed headline font, 96–140px, UPPER, off-white; teal accent bar ▌ at left
│   GOES HERE                   │
│ @rarity.agency                │  ← small handle (BentonSans), above the bottom safe zone
└───────────────────────────────┘
```
- The headline is a HOOK on one of five named triggers (contrarian · authority/anti-hero · innovative
  idea · apparent nonsense · extreme curiosity), bottom-left, 1–3 lines, generous leading. Under it, ONE
  open loop subhead that promises the payoff and ends with an arrow (→), never an explanation — the
  reference is @vinci.society / @brandsdecoded__ hooks. The ONLY text on the photo is eyebrow +
  trigger headline + open loop subhead + handle/logo.
- If the photo has no dark area for text, strengthen the scrim or add a navy lower-third block.
- **Headline color stops the scroll.** Choose it for maximum contrast on THIS photo; it MAY go off-brand
  (high-vis yellow, red, white). Use the brief's Headline color. Everything else stays on-brand.

---

## CAROUSEL (6–10 slides)

**Slide 1 — Hook:** identical pattern to the static above. Job: stop the scroll + promise a payoff.

**Slides 2 … N-1 — Body (one idea each):**
```
┌───────────────────────────────┐  FULL-BLEED CONTEXTUAL PHOTO (darkened duotone; NEVER flat navy or gradient)
│  02                   ◆ symbol │  ← slide number top-left (optional) · SYMBOL top-right (every slide)
│                               │
│  BIG FOCAL                    │  ← the condensed headline font 120–200px; accent the key word in teal
│  WORD / 1.4s                  │
│                               │
│  one short supporting line    │  ← BentonSans Regular 40–56px, off-white
│  that pays off the focal word │
│                          ▌    │  ← small teal mark for rhythm
└───────────────────────────────┘
```
- One idea per slide. If a slide has two thoughts, split it. Big focal word/number is the anchor.
- EVERY body slide sits on a real photo that creates context for its line (typewriter for the writing
  beat, newspaper for the mass-desire beat, the desk for the spend beat). The engine darkens it to
  texture level so type always wins. A photo may serve 2 slides max, as visibly different crops.
- Carry the hero subject onto the CTA slide to bookend the story.
- Vary photo mood and crop between consecutive slides so the set has rhythm, and match text density to
  how busy each photo is — see `design-principles.md` section 2. If a slide idea feels thin, work the
  escalation ladder in that file's section 3 before shipping it empty.

**Final slide — CTA (save + share; NO button):**
```
┌───────────────────────────────┐  FULL-BLEED PHOTO, darkest treatment (often the hero subject again)
│        [ RARITY logo ]        │  ← small, top-center
│                               │
│      SAVE THIS.               │  ← the condensed HEADLINE font (brandsdecoded voice), centered
│      SEND IT TO A FRIEND      │
│      WHO RUNS ADS.            │  ← last line in the accent color
│        @rarity.agency         │  ← small handle. NO button, NO follow pitch.
└───────────────────────────────┘
```
The close is always a SAVE + SHARE action (saves and sends drive reach), phrased for the post's
audience ("who runs ads", "who builds brands", "que hace anuncios", "que faz anúncios"…). EN, ES, and PT
mirror each other. The line must bridge back to this carousel's specific theme, not read as a generic
sign-off — if it feels generic, that's a copy fix for the brief, not something to patch at render time
(`design-principles.md` section 6).

## Slide flow (maps to the brief's slide copy)
1 Hook → 2 Tension/setup → 3–7 Decode (real thing → insight → why it matters) → 8 Takeaway →
9 CTA. Use as many body slides as the brief specifies (6–10 total).

## EN / ES / PT
Build the English set first and lock the layout. Clone it to an "ES" page and swap only the copy to the
brief's Spanish lines — keep identical composition, sizes, and positions so the language sets are
visually twins. Then clone it again to a "PT" page and swap only the copy to the brief's Brazilian
Portuguese lines, same identical composition, sizes, and positions. Re-check line breaks: Spanish and
Portuguese often run longer than English; reduce size a step or rebalance line breaks rather than
letting text overflow or hit the safe zone.

## Quality checklist (before delivering)
- [ ] Hook headline carries a named trigger and an open loop subhead ending with →.
- [ ] Headline legible at a glance (strong contrast/scrim).
- [ ] Only eyebrow + trigger headline + open loop subhead + handle/logo on the hero photo.
- [ ] Every background passes the shock bar (no stock-looking, posed or common imagery).
- [ ] One idea per slide; big focal element.
- [ ] Brand-exact colors and fonts (or flagged fallback).
- [ ] A real contextual photo behind EVERY slide (no flat navy, no gradient cards).
- [ ] Rarity symbol stamped in the corner of every slide (same size/position); logo on the CTA slide.
- [ ] Final slide is a save + share sentence in the condensed headline font, no button.
- [ ] Key text/logo outside IG safe zones.
- [ ] EN, ES, and PT are visual twins; no clipped or overflowing text.
- [ ] Every PNG opened and reviewed like a creative director; at least one polish pass done.
- [ ] Contrast measured at 4.5:1 minimum between text and background on every slide (`design-principles.md` section 5).
- [ ] Full set viewed together as a contact sheet, not slide by slide, to catch repeated crops and flat rhythm (`design-principles.md` section 8).
