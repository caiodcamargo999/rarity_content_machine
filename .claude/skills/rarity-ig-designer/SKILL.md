---
name: rarity-ig-designer
description: "Turns a Rarity IG Content Idea Brief into the actual Instagram ART, rendered 100% by Claude in Python/Pillow with NO design connectors (never Canva, never Figma). Every slide is its OWN distinct, current, high-res, high-impact photo full-bleed (no flat, solid, or gradient cards), with a high-contrast editorial SERIF headline (Playfair Display) and italic accent words in magenta, the Rarity symbol transparent in the corner (no white box), NO date, a trigger HOOK with an open loop subhead, and a SAVE + SHARE close (no button). English + Spanish + Portuguese. STEP 2, consuming the brief from rarity-ig-idea-engine. ALWAYS use when Caio wants to design or create the post art: make the design, build the carousel, turn this idea into a post, cria a arte, monta o post, design this, haz el diseno. When in doubt, USE this skill."
---

# Rarity IG — Designer (Step 2 of 2) · Claude-rendered, no connectors

Claude builds the art **itself** by rendering 1080x1350 PNGs with the bundled Python/Pillow engine
(`scripts/render_post.py`). The output IS the deliverable — real image files, in Rarity's identity, in
the editorial style of the reference feeds (@vinci.society, @brandsdecoded__, @blankschoolbr,
@matthgray): every slide a full-bleed, high-impact photo + a big editorial serif headline. EN + ES + PT.

## Non-negotiables (hard rules from Caio — do not break)
1. **Render it 100% in Claude. NEVER use a design connector — not Canva, not Figma, not any other.**
   Everything is done with `scripts/render_post.py`.
2. **The headline font is a high-contrast editorial SERIF (the @vinci.society look), not a condensed
   sans.** The engine uses `assets/headline.ttf` (bundled Playfair Display) with the italic at
   `assets/headline-italic.ttf`. Headlines are sentence case, white, with **one or two emphasis words in
   *italic* + magenta** — wrap them in `*asterisks*` in the spec and the engine renders them. To match a
   brand/paid serif exactly, drop it at `assets/headline.ttf` (+ `-italic`). Small labels stay BentonSans.
3. **EVERY slide carries its OWN distinct, current, high-resolution, high-impact photo — hook, every
   body slide, the CTA. No flat, solid, or gradient cards. Ever.** Each photo creates CONTEXT for that
   slide's line and is different from the others (never the same hero re-tinted on every slide). Every
   photo must pass the SHOCK BAR: current where possible, high-res, emotional / dramatic / strange /
   controversial — a face mid-emotion, charged action, a cinematic or provocative frame. If it would sit
   in a corporate deck or a generic stock search, find the charged version. The engine ERRORS on any
   slide with no photo — that is intentional.
4. **The Rarity symbol sits transparent in the corner of EVERY slide (default top-right), no white
   box.** Use `assets/rarity-symbol-white.png` (clean transparent mark). Never the legacy
   `rarity-symbol.png` (it carries a white background box). Keep the same size/position across the set.
5. **No date on the card.** Never render a month, year, or date label on a slide.
6. **The hook follows the HOOK DOCTRINE.** Slide 1's headline carries exactly ONE named trigger from the
   brief (CONTRARIAN, AUTHORITY/ANTI-HERO, INNOVATIVE IDEA, APPARENT NONSENSE, EXTREME CURIOSITY) with
   ONE open loop subhead under it (a short question / subversion ending with an arrow). If the brief
   lacks the trigger or subhead, derive them before rendering; never ship a merely descriptive hook.
7. **The final slide is a SAVE + SHARE close, not a follow pitch. NO button.** One strong sentence in the
   serif (italic accent on the turn), the white logo above, small handle under. Adapt the "who" to the
   audience. ES and PT both mirror it.
8. **Top-tier design bar.** Render → open every PNG → critique like a creative director → fix →
   re-render. Judge the set against `references/design-principles.md` and `references/viral-layouts.md`.
   "It rendered without errors" is not the bar.
9. **Always produce EN, ES, and PT.**

## Step 1 — intake the brief
Read the brief (`public/Instagram Briefings/Ideas <Month>/Idea N - Name.docx`, or pasted). Pull: the Hook
trigger, the headline (EN+ES+PT) with its *italic* accent word(s), the open loop subhead (EN+ES+PT),
format + slide copy, the per-slide image URLs (one DISTINCT background per slide), the accent color, and
the slug. See `references/claude-render.md` for the slide spec.

## Step 2 — get a distinct photo for EVERY slide (automatic, do it yourself)
- Target folder: `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/` — `hero.jpg` for slide 1 and
  `bg/bg2.jpg ... bgN.jpg` for the rest. Create folders if missing.
- **If images are already in the folder, use them.** Otherwise AUTOMATICALLY download each DISTINCT
  direct image URL from the brief's IMAGES table (Wikimedia direct file:
  `https://commons.wikimedia.org/wiki/Special:FilePath/<File_Name>`).
- Prefer **current, high-resolution, high-impact** imagery. A background may serve at most 2 slides, and
  only as visibly different crops — otherwise every slide is its own picture.
- If a slide's image is missing, source one yourself (web search → direct URL → download) that creates
  context for that line and clears the shock bar.
- Rights: for real people, prefer a licensed image; carry the brief's credit/license into the summary.

## Step 3 — build the spec + render
- Write a JSON spec per `references/claude-render.md` (out_dir, handle, accent, and the `slides` array —
  every slide with its OWN `bg` path). Hook carries `eyebrow`, the trigger `headline` (with `*italic*`
  accent word) and the open loop `subhead` (ending with an arrow).
- Run: `python3 <skill>/scripts/render_post.py <spec_en.json>` → writes `slide-1.png ... slide-N.png`.
  The engine applies the house treatment (navy duotone tint, vignette, bottom scrim, grain), the serif
  headline with italic/magenta accents, and the transparent symbol top-right.
- **Verify like a creative director**: open each PNG. Check overflow/clipping, weak contrast, the photo
  reading through (it should — it is the focus), awkward crops, monotony between consecutive slides
  (each photo must be visibly different). Tune sizes, focus_x/focus_y, and re-render.

## Step 4 — EN, then ES, then PT
Render EN first and get it right. Copy the spec, swap to the brief's Spanish lines (keep the `*italic*`
accent words; ES runs longer so drop sizes a step where needed), same backgrounds, `out_dir` → `ES/`,
render. Then copy the spec again, swap to the brief's Brazilian Portuguese lines (same `*italic*` accent
word rule; PT, like ES, often runs longer than EN so drop sizes a step where needed), same backgrounds,
`out_dir` → `PT/`, render. EN, ES, and PT must all be visual twins — same fonts, same brand colors, same
layout, only the copy language changes.

## Step 5 — deliver
Present the PNGs in chat (`.../EN`, `/ES`, and `/PT`). Close with a short summary + the image
credit/license note, and flag if the headline used the bundled Playfair fallback (drop a licensed serif
into `assets/headline.ttf` + `assets/headline-italic.ttf` for an exact brand match).

## References
- `references/claude-render.md` — the render engine: spec schema, how to run, how to tune, the layout.
- `references/rarity-brand-system.md` — exact colors, the serif type system, the symbol/logo, accent rules.
- `references/viral-layouts.md` — editorial layout patterns and IG safe zones.
- `references/design-principles.md` — hierarchy, rhythm across the set, the legibility bar.

## Relationship to the other skill
This is **Step 2**, consuming the brief from **`rarity-ig-idea-engine`** (Step 1). That brief maps one
DISTINCT contextual photo per slide and marks the headline's italic accent word(s); hold it to that.
