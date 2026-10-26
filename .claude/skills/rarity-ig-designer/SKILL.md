---
name: rarity-ig-designer
description: "Turns a Rarity IG Content Idea Brief into the actual Instagram carousel ART, rendered 100% by Claude in Python/Pillow with NO design connectors (never Canva, never Figma), in the EXACT house design of the Brands Decoded Maquina posts (e.g. Idea 01 Liquid Death): full-bleed photo hook with profile chip and magenta italic accent word, then alternating off-white cards (navy headline, body text, framed photo), full-bleed photo slides with arrow circle, a near-black card, a lesson slide, a magenta action slide and a Save + Share close. The only thing that varies between posts is the headline font: Plus Jakarta Sans ExtraBold or Playfair Display. 1080x1350, English plus Spanish plus Portuguese. STEP 2, consuming the brief from rarity-ig-idea-engine. ALWAYS use when Caio wants to design or create the post art: make the design, build the carousel, turn this idea into a post, cria a arte, monta o post, design this, haz el diseno. When in doubt, USE this skill."
---

# Rarity IG Designer (Step 2) · Claude-rendered, house standard

Claude builds the art itself with `scripts/render_post.py`. The output must be indistinguishable in layout,
colours and spacing from the posts Caio makes in the Brands Decoded Maquina software. Reference to compare
against every time: `public/Instagram Briefings/Designs October 2026/Idea 01 - Liquid Death Made Water Look Dangerous/EN/`.

## Non-negotiables
1. **Render it 100% in Claude. Never a design connector** (no Canva, no Figma).
2. **The design is the house standard, not a free interpretation.** Use the 11 slide template and slide types in
   `references/claude-render.md` (hook, light, photo, dark, lesson, action, cta) and the exact palette
   (`#EFEEEA` light, `#0F0A1A` dark, `#001A70` navy, `#D50057` magenta). Do not invent new layouts, colours,
   gradients, symbols in the corner, page counters, dates or buttons.
3. **The only variable is the headline font.** `headline_font` is `"sans"` (Plus Jakarta Sans ExtraBold) or
   `"serif"` (Playfair Display Bold). Alternate it across posts: check the last post's font in the calendar and
   use the other one. Body text (Inter), handle, colours and layout never change.
4. **Every slide has its own distinct photo** (framed or full-bleed, per type). Current, high resolution, emotional or
   strange, showing the actual subject of that slide's line. The engine errors on a missing photo.
5. **One magenta italic accent word per headline** (`*word*`). The `action` headline is entirely magenta.
6. **Hook** carries the brief's trigger in the headline plus a short factual subhead. **Final slide** is always
   "Save this post. Share it with the people who *think* like you." on the `cta` card.
7. **Copy style:** short sentence case headlines, one or two plain factual sentences of body (year, number, name),
   no hyphens or dashes, no emoji. Handle `@rarity.agency` only.
8. **Verify like a creative director.** Render, open every PNG next to the Idea 01 reference, fix, re-render.
   "It rendered" is not the bar. Read the engine's `[contrast]` lines for `photo` slides.
9. **Always produce EN, ES and PT** as visual twins (same photos, same font, same layout).

## Step 1. Intake the brief
Read the brief (`public/Instagram Briefings/Ideas <Month>/Idea N - Name.docx`, or pasted). Map it onto the 11
slides: hook (headline + subhead), slides 2 to 8 (headline + one or two sentence body each), lesson ("The
*lesson* for your brand"), action (the one thing to try this week), cta (fixed). Trim to the short house headline
lengths. If the brief has fewer slides, the engine drops from the middle cycle.

## Step 2. Photos
Folder: `public/Instagram Briefings/Designs <Month>/Idea NN - <Title>/` with `hero.jpg` and `bg/bg2.jpg ... bgN.jpg`.
Use images already there; otherwise download each distinct direct URL from the brief (Wikimedia
`Special:FilePath/<File_Name>`) or source one yourself. A photo serves at most 2 slides, as different crops.
Carry the credit/license into the summary. Do NOT commit these folders (public repo; only rarity-ig-publish pushes).

## Step 3. Spec and render
Write the JSON spec per `references/claude-render.md` (`out_dir`, `headline_font`, slides). Run
`python3 <skill>/scripts/render_post.py spec_en.json`. Output: `EN/slide-01.png ... slide-11.png`, the exact
naming rarity-ig-daily-post and rarity-ig-publish expect.

## Step 4. ES then PT
Copy the spec, swap the copy (keep the accent word, ES and PT run longer: the engine auto-shrinks to the line
limits), `out_dir` to `ES/` then `PT/`. Same photos, same `headline_font`.

## Step 5. Deliver
Show the PNGs, state which `headline_font` was used (so the next post uses the other), and note photo credits.
To queue it for the daily publisher, follow rarity-ig-captions then `touch READY_TO_POST` (see rarity-ig-daily-post).

## References
- `references/claude-render.md`: slide types, palette, spec schema, verification checklist (the source of truth).
- `references/design-principles.md`, `references/viral-layouts.md`, `references/rarity-brand-system.md`: older
  background reading. Where they conflict with `claude-render.md` (full-bleed only, symbol corner, serif only,
  no flat cards), `claude-render.md` wins.

## Relationship to the other skills
Step 2, consuming the brief from `rarity-ig-idea-engine` (Step 1); feeds `rarity-ig-captions` and then
`rarity-ig-daily-post` / `rarity-ig-publish`. Posts built inside the Maquina software via
brand-decoded-saas-carousel-maker already follow this same design.
