# Claude Render Engine v7: the house standard (NO connectors)

`scripts/render_post.py` (Python/Pillow) reproduces the carousel design of the posts made in the Brands
Decoded "Maquina" software (reference: `Designs October 2026/Idea 01 - Liquid Death`). 1080x1350 PNGs,
`slide-01.png ... slide-NN.png`. Same look, same layout, same colours every time. The ONLY thing that
varies between posts is the headline typeface.

## Headline font: alternate between the two, nothing else changes
`spec["headline_font"]`:
- `"sans"`: Plus Jakarta Sans ExtraBold (`assets/headline-sans.ttf` + `-italic`). The look of the reference posts.
- `"serif"`: Playfair Display Bold (`assets/headline.ttf` + `-italic`).
Body text (Inter 500, `assets/body-inter.ttf`), handle, colours, spacing and card layout are identical in both.
Alternate across the content calendar: if the last post used sans, this one uses serif.

## Palette (exact)
| Token | Hex |
|---|---|
| Light card | `#EFEEEA` |
| Dark card | `#0F0A1A` |
| Navy headline | `#001A70` |
| Magenta accent / action headline | `#D50057` |
| Body ink on light | `#0B0B0C` |
| Hook subhead blue | `#ADD5F0` |
| Verified badge | `#1D9BF0` |

## Slide types (the 11 slide standard)
Omit `type` and the engine assigns it: 1 hook, 2 light, 3 photo, 4 dark, 5 photo, 6 light, 7 photo,
8 photo, 9 lesson, 10 action, 11 cta. For other lengths: hook first, then the middle cycle
(light, photo, dark, photo, light, photo, photo), then lesson, action, cta.

| type | Look | Fields |
|---|---|---|
| `hook` | Full-bleed photo, bottom scrim, handle top-left, profile chip (avatar + @rarity.agency + blue verified), big white headline with ONE magenta italic word, light-blue subhead near the bottom | `bg`, `headline`, `subhead` |
| `light` | Off-white card, navy headline top, black body, framed photo bottom | `bg`, `headline`, `body` |
| `photo` | Full-bleed photo + dark gradient, white arrow circle, SHORT white headline (magenta italic word) mid-slide, white body at the bottom | `bg`, `headline`, `body` |
| `dark` | Near-black card, white headline, white body, framed photo bottom | `bg`, `headline`, `body` |
| `lesson` | Off-white card, short navy headline ("The *lesson* for your brand"), photo bleeding edge to edge across the bottom | `bg`, `headline` |
| `action` | Off-white card, framed photo on top, MAGENTA headline (the "do this week" step) | `bg`, `headline` |
| `cta` | Off-white card, framed photo on top, NAVY headline, magenta italic word. Always "Save this post. Share it with the people who *think* like you." | `bg`, `headline` |

`*word*` = magenta italic (one word per headline; action headline is fully magenta). Optional per slide:
`focus_x`/`focus_y` (0 to 1 crop focus), `"verified": false`.

## Copy rules baked into the standard
- Headlines short, sentence case. Hook headline names the brand and the twist; `photo` headlines are even
  shorter (about 6 words).
- Body: one or two plain sentences with a real fact (year, number, name). No hyphens or dashes, no emoji.
- Handle is always `@rarity.agency` (small, top-left). No symbol in the corner, no date, no page counter, no button.
- Final slide is the fixed Save + Share line; the caption carries the rest.

## Spec
```json
{
  "out_dir": ".../Idea 12 - Title/EN",
  "handle": "@rarity.agency",
  "headline_font": "serif",
  "slides": [
    {"type":"hook","bg":"hero.jpg","headline":"Brand made X look *dangerous*","subhead":"Hook fact. Second fact.","focus_x":0.5,"focus_y":0.4},
    {"type":"light","bg":"bg/bg2.jpg","headline":"The product was *never* the problem","body":"One or two sentences."}
  ]
}
```
`bg` paths are relative to the spec file (or absolute). Every slide needs its own distinct photo; the
engine errors if one is missing. Run: `python3 <skill>/scripts/render_post.py spec_en.json`.

## Verify like a creative director (mandatory)
Open every PNG next to the reference (Idea 01). Check: headline fits in the line limit, accent word is
readable, framed photos are distinct and sharp, white text on `photo` slides clears the `[contrast]` line the
engine prints (4.5:1), hook subhead not cut off, nothing in the bottom ~120px. Magenta on a busy dark photo
can be weak: pick a photo whose headline zone is calm or move `focus_y`.

## Languages
EN first. For ES and PT copy the spec, swap the text (keep the `*accent*` word, drop nothing else), point
`out_dir` to `ES/` or `PT/`, same photos, same `headline_font`. The three sets are visual twins.

`scripts/render_post_legacy.py` is the retired full-bleed photo engine (v6). Do not use it for new posts.
