---
name: rarity-ig-idea-engine
description: "Generates non-generalist Instagram content IDEAS for Rarity Agency (@rarity.agency) in the editorial style of @vinci.society, @brandsdecoded__, @blankschoolbr and @matthgray. Every idea is anchored to a REAL trigger (current event, anniversary, news, or an iconic figure/brand like Ayrton Senna, Nike, Ferrari) found via live web research, then DECODED into ONE sharp lesson. Every slide ships its OWN distinct full-bleed photo that shows the actual named subject of that slide, scored through a mandatory image QA gate for subject match, impact, currency and resolution; the image is the focus, never a solid or gradient card, never generic stock. Rotates 3 pillars (Growth Marketing & Branding, Business & Strategy, Mindset & High Performance), decides static vs carousel, and outputs a Content Idea Brief in English + Spanish + Portuguese that rarity-ig-designer turns into art. ALWAYS use when Caio asks for Instagram ideas, posts, carousels, ideia de post, o que postar, ideas de contenido, decode a brand or person, or a content batch or calendar. When in doubt, USE this skill."
---

# Rarity IG — Idea Engine (Step 1 of 2)

This skill produces the **idea**, not the design. It finds a real-world anchor, decodes it into
one sharp insight for Rarity's audience, and writes a **Content Idea Brief** (EN + ES + PT). That brief
is the handoff to **`rarity-ig-designer`** (Step 2), which renders the art itself (Python/Pillow,
no design connectors).

The whole point: Rarity's feed should never look like recycled "5 marketing tips." It should look
like someone *decoded something real* — a person, a brand, a moment — and pulled a lesson out of it
that a founder or marketer can actually use. That is the @vinci.society / @brandsdecoded__ /
@blankschoolbr / @matthgray energy, in Rarity's voice: a big editorial serif line over a striking,
current, full-bleed photo.

---

## What "good" looks like (read this first)

Four non-negotiables separate a Rarity idea from generic content:

1. **It is anchored to something real and specific.** A named person, brand, product, event, or
   date — with a *verified fact* behind it (a number, a quote, a date, a documented decision).
   "Be consistent" is not an idea. "Ferrari deliberately makes fewer cars than the market wants —
   here's the demand lever most brands are too scared to pull" is an idea.
2. **It carries exactly one big idea.** One insight per post. If you can't say the takeaway in a
   single sentence, it's two posts.
3. **It earns the scroll-stop with a named trigger.** Every carousel's slide 1 is a HOOK built on one
   of five triggers: CONTRARIAN, AUTHORITY/ANTI-HERO, INNOVATIVE IDEA, APPARENT NONSENSE (a line that
   seems absurd and only makes sense as the post unfolds), or EXTREME CURIOSITY. The brief names the
   trigger, adds one open loop subhead (a question or subversion ending with an arrow), and marks the
   headline's *italic accent word*. See the Hook doctrine in `references/editorial-playbook.md`.
4. **The images are the focus, in REAL colour, and they shock.** Photos render in their real colours (no
   brand wash). EVERY slide gets its OWN distinct photo — subject-matched, current, high-resolution, and
   high-impact (emotional, dramatic, strange, or controversial). No solid or gradient cards, and never
   the same photo reused on every slide. Imagery is held to a scored gate exactly like the copy is: find
   it with `references/image-sourcing.md`, then score it with `references/image-qa.md`. **An image with
   no scorecard in the brief is not approved**, however good it looked in the search results.

If an idea fails any of these, fix it before writing the brief.

---

## Workflow

### 1. Read the references first
Before generating, skim these so the output matches the house style and format:
- `references/editorial-playbook.md` — the decode method, the 3 pillars, hook & headline patterns, Rarity voice, caption structure, do/don't.
- `references/headline-engine.md` — data-backed lift patterns, emotional triggers, the headline rejection checklist, and five extra rigid hook formats. Run headlines through this before they're final.
- `references/editorial-qa.md` — the full pre-ship quality gate: 7 scored parameters, banned constructions, jargon substitutions, the AI-tone test, and the review process. Run ALL copy through this before a brief is locked.
- `references/trigger-engine.md` — how to find and verify real anchors, the rotation logic, source quality.
- `references/brief-template.md` — the exact Content Idea Brief format you must output.
- `references/image-sourcing.md` — how to find, verify, and embed a distinct, subject-matched, high-impact image PER SLIDE: the order of operations, Rule #1, the source ladder, the banned-trope list, and the rights ladder.
- `references/image-qa.md` — the image quality gate: 6 binary checks plus 6 scored parameters per slide, and the rejection loop. Run EVERY image through it before a brief is locked, the same way all copy runs through `editorial-qa.md`.
- `references/docx-output.md` — how to render the finished brief as the Word (.docx) deliverable.

### 2. Establish the trigger (the anchor)
- **If Caio named a subject** (a person like Senna, a brand, an event, a news story) → use it. Still
  run web research to pull *specific, verifiable* facts (don't write from memory — details matter and
  memory drifts).
- **If Caio did NOT name a subject** (e.g. "give me 3 posts for this week", "what should we post") →
  use the trigger engine to find timely, high-signal anchors via **live web search**: on-this-day
  anniversaries, brand/marketing news, cultural or sports moments, business milestones, or an evergreen
  icon worth decoding. See `references/trigger-engine.md`.
- Always capture **at least one source URL** per idea. The fact must be real.
- **Anchors can be historical, not only current.** Legendary figures are encouraged: classic copywriters
  (Eugene Schwartz, David Ogilvy, Gary Halbert, Claude Hopkins), athletes (Muhammad Ali), thinkers and
  ancient stories (Aristotle, the Stoics, Sun Tzu), inventors, founders, brands. Any true story that maps
  to a marketing, branding, business, or mindset idea is fair game. The anchor can be from any era — but
  the IMAGES must always be current-feeling, high-resolution and high-impact (see step 6).

### 3. Pick the pillar (rotate — don't repeat)
Tag each idea with ONE pillar. When producing multiple ideas in a batch, rotate so the same pillar
never lands twice in a row:
- **Growth Marketing & Branding** — ads, positioning, demand creation, authority, offers, funnels.
- **Business & Strategy** — scaling, pricing, moats, decisions, bets, business models.
- **Mindset & High Performance** — discipline, standards, obsession, the cost of greatness (the
  Senna lane).

A single anchor can be decoded through any pillar — the pillar decides *which lesson* you pull out.

### 4. Decode (story → insight → takeaway)
Take the real story and run the decode:
- **The real thing they did / what happened** (concrete, sourced).
- **The non-obvious insight** — the mechanism most people miss.
- **The takeaway for Rarity's audience** — what a founder/brand/marketer does differently tomorrow.

Keep it sharp and a little contrarian. Rarity's voice is confident and systematic, never guru-fluffy.
"Growth is not luck. It is a system." Decode like that.

### 5. Decide the format (static vs carousel)
- **STATIC** — one punch: a bold claim, a flipped stat, a quote with a twist, a single decoded truth.
  Best when the idea lands in one beat.
- **CAROUSEL (6–10 slides)** — a breakdown or story arc that needs steps: a sequence, a framework,
  a before→after, a "here's how they actually did it." Slide 1 is the hook (same energy as a static).
Recommend one, and say why in a line.

### 6. Source, SCORE and attach a DISTINCT, subject-matched, high-impact image — one per slide
A brief is not finished until it carries the actual pictures it should use — sourced from the web,
viewed, scored, embedded, and ready for Step 2. **EVERY slide gets its OWN distinct background image**:
the hook, each body slide, and the CTA. Step 2 renders no flat or gradient cards, so a brief that only
ships a hero is incomplete, and reusing one photo across the set is not allowed.

Run `references/image-sourcing.md` to FIND the images and `references/image-qa.md` to APPROVE them.
Both are mandatory. The following is the short form, and none of it is optional:

**a. Work in this order — subject, then impact, then legibility, then rights.** Filtering by licence
before filtering by impact is the single biggest cause of generic imagery: a Creative-Commons-first
search returns the Commons/Unsplash pool, which is exactly where dated, posed, over-used photography
lives. Find the right image first; clear the rights afterwards.

**b. Match the SUBJECT. A metaphor is the exception, not the default.** If a slide's claim is about a
real, named thing (a company, product, tool, platform, person, event), the image must show THAT thing
or something literally from its world. Search the subject's own newsroom and Google News first — and
Pinterest to see how it is actually being shown — before touching a stock library. A wine-bottling line
standing in for "ads all look the same", or a robot arm standing in for "AI-generated content", is the
exact failure this rule exists to stop. The beat→query cheat sheet now lives in the Appendix of
`image-sourcing.md` and is only for claims that are genuinely abstract with no real subject to photograph.

**c. LOOK at every image before choosing it.** A URL that resolves is not a photo you have seen.
Choosing from filenames and alt text is how a pick ends up on-theme and visually dead. For each image
you intend to ship, view the frame and write one sentence describing what is literally in it. Note: the
sandbox shell cannot reach image hosts, so verify and view through the connected Chrome browser, never
via bash.

**d. Bring 3 to 5 candidates per slide, not one.** Score each against `references/image-qa.md` and
record in one line why the winner beat the runner-up. One search producing one pick is an accident, not
a choice.

**e. Clear the gate.** Every image passes 6 binaries (viewed · ≥1600px short side · URL verified in
Chrome · not on the banned-trope list · not reused beyond 2 slides · licence traced to the original
source) and scores 8+ on 6 parameters (subject match · the five-unrelated-posts test · charge ·
currency · legibility · set distinction). Below 8 anywhere, run the rejection loop: name the failure,
sharpen the search, re-gather, re-score — maximum three loops, after which sharpen the slide's CLAIM
instead of accepting a weak image.

**f. Never resolve a rights problem with a weak photo.** Work the rights ladder (official press kit →
Commons/CC with attribution → free stock for the metaphor case), and if the strongest image still can't
be cleared, flag it `INTERNAL MOCKUP ONLY` and name a cleared substitute. A free generic photo is a
worse outcome than a flagged strong one.

**g. Embed and record.** Inline `![desc — author, license](direct-url)` so the photo renders, plus the
IMAGES table with one row per slide (slide · description · direct URL · source page · author · licence)
and the QA scorecard beneath it. For Wikimedia Commons, build the direct URL with
`Special:FilePath/<File_Name>`.

### 7. Write the Content Idea Brief (EN + ES + PT)
Compose the brief content per `references/brief-template.md` (that file is the CONTENT spec; the final
deliverable is a Word .docx, see step 8). The brief MUST contain:
- The anchor + verified fact + source URL(s).
- The one-sentence big idea and the audience takeaway.
- The **Hook trigger** and the **headline** built on it — in **English, Spanish, and Portuguese**
  (3 to 9 words), with the *italic accent word(s)* marked by wrapping them in `*asterisks*` (Step 2
  renders those words in italic + magenta). Validate against `references/headline-engine.md`. If Caio
  wants options, draft 3 to 5 candidates and let him pick; otherwise ship the strongest one.
- The **Open loop subhead** (EN + ES + PT): one line under the headline that opens the loop and ends
  with an arrow. It promises the payoff; it never explains.
- If carousel: slide-by-slide copy (EN + ES + PT). Keep every internal line anchored (a name, a number,
  a specific mechanism).
- The caption (EN + ES + PT) in Rarity's voice, with a CTA.
- The **attached real images, one DISTINCT photo per slide** — embedded inline by direct URL, with
  source page, author, and license, so Step 2 knows exactly which photo backs which slide, **plus the
  `image-qa.md` scorecard for each** (binaries, the 6 scores, and the one-line reason it beat the
  runner-up). A slide image with no scorecard is a blocking gap, the same as a missing image.
- **Visual direction**: what the hero shows, the per-slide context logic (each different), and 2–4
  alternate image queries as backups.
- A rights/sensitivity note on the imagery.

Before locking any of the above, run **both** gates:
- all copy through the **Editorial QA gate** in `references/editorial-qa.md` — 7 scored parameters plus
  5 final tests. Rewrite anything below the bar.
- all imagery through the **Image QA gate** in `references/image-qa.md` — 6 binaries plus 6 scored
  parameters per slide, then the batch-level set-distinction check. Re-source anything below the bar.

### 8. Produce the Word document and hand off (follow exactly)
- **The output is a Word document (.docx), never a markdown file.** Compose the content (step 7), then
  build the .docx following `references/docx-output.md`: write the brief as JSON and run the bundled
  `scripts/build_brief_docx.js`. The document embeds the Rarity logo and lists each image as a
  clickable link with credit and license.
- Save under `public/Instagram Briefings/Ideas <Month>/`. `<Month>` is the month the content is for: default to
  the CURRENT month (from today's date); if Caio is planning a specific month, or an `Ideas <Month>`
  folder for that batch already exists, use that one. **Create the month folder if it does not exist.**
  (This month-based FILING is internal only — it never appears as a date on the card.)
- Name the file `Idea N - <Short Name>.docx`: N is the next number in that month folder, and <Short Name>
  is a few-word Title Case name. Keep the brief's internal `Slug` field too.
- For a batch, continue numbering from the highest existing Idea number in that month folder; never restart at 1.
- Show the brief in chat too.
- Close with the handoff line: *"Run **rarity-ig-designer** on this brief to build the art."*

---

## Language rule
Every idea ships **trilingual: English first, then a cloned Spanish version, then a cloned Portuguese
(Brazilian) version.** Both the Spanish and the Portuguese are a true adaptation, not a literal
translation — headlines must still hit in Spanish and in Brazilian Portuguese (rework wordplay so it
lands in each language, and re-mark the *italic accent word* in both). Keep all three versions to the
same one-big-idea and length. Portuguese here always means Brazilian Portuguese (Rarity's audience),
never European Portuguese.

## Output discipline
- **No hyphens or dashes in the posted copy.** Headlines and captions must contain no em dash, no en
  dash, and no hyphen used as a pause or connector. Rewrite with periods, commas, or colons. This rule
  applies to what gets posted: the headline and the caption.
- **Hashtags: 3 maximum, fewer is fine** (often 1 to 3, sometimes zero). One branded (#RarityAgency)
  plus one or two sharp, relevant tags. Localize per language.
- **The final slide and the caption close on SAVE + SHARE, never a follow pitch.** The carousel's last
  slide is one strong sentence ("Save this. Send it to a friend who runs ads." / "Guarda esto. Envialo a
  un amigo que hace anuncios." / "Salva isso. Manda pra um amigo que faz anúncios."), adapted to the
  post's audience. No button copy.
- **Headlines are a scroll-stopping HOOK built on a named trigger**, 3 to 9 words, plus an open loop
  subhead. The headline is a **white editorial serif with one or two *italic accent words*** (mark them
  with `*asterisks*`). The accent colour is **magenta `#D50057` by default; use shock yellow `#FFE400` or
  red `#FF3B3B` sometimes to spike attention** — set it per post/slide and vary it across a batch.
- **No date on the card.** Never put a month, year, or date label on the art. (Briefs are only FILED by
  month, internally.)
- One big idea per post. No listicles of everything.
- No emojis in headlines. Sparingly, if ever, in captions, matching Rarity's restrained tone.
- Never invent facts, quotes, or numbers. If you cannot verify it, do not claim it; pick another anchor.

## Batch requests
If Caio asks for N ideas (e.g. a week or a calendar), produce N briefs, rotate the pillars, vary the
anchor *type* (don't do three dead-icon posts in a row), and give each its own slug + file. Offer a
one-line index table at the top (pillar · format · headline) so he can scan the batch.

## Relationship to the other skill
This is **Step 1**. `rarity-ig-designer` is **Step 2** and consumes the brief this skill writes.
Keep the brief's *Visual direction*, *Headline* (with its `*italic*` accent word) and per-slide *Images*
fields clean and literal — they are read directly by the design step.
