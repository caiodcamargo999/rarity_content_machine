# Rarity Content Machine — Guidelines

How to go from "nothing" to a finished, ready-to-post Instagram carousel/static for
**@rarity.agency**, in English, Spanish and Brazilian Portuguese, using the 4 skills installed in
this project (`.claude/skills/`).

```
 STEP 0            STEP 1                STEP 2              STEP 3
 trend-scout   →   idea-engine       →   designer        →   captions
 10 pitches        Content Idea Brief    rendered PNGs        final caption
 (menu, you pick)  (.docx, EN+ES+PT)     (EN / ES / PT)        (EN+ES+PT)
```

You can enter at any step — start at Step 0 for "what should I post," or jump straight to Step 1 if
you already know the subject ("decode Ayrton Senna for a post"), or even straight to Step 3 for a
standalone caption. Each step tells Claude to invoke the matching skill by name, or Claude will
pick it up automatically from what you ask for (see the trigger phrases in each section).

---

## Before you start (one-time per session)

The project has two MCP servers configured in `.mcp.json`:
- **`rss-reader`** — direct fetch of curated marketing/branding/social RSS feeds (no cost, no key).
- **`tavily-search`** — real-time news-mode web search (key in `.env`, free up to 1,000 credits/month).

Claude Code only picks up `.mcp.json` when the project loads. **If you just opened this folder for
the first time after setup, or added/changed `.mcp.json`, restart the Claude Code session** (reopen
the folder / restart the extension) so both servers connect before running Step 0.

---

## Step 0 — Trend Scout (optional, for "what should I post")

**Skill:** `rarity-ig-trend-scout`
**Say:** *"Give me 10 ideas for this week"* / *"o que tá em alta pra postar"* / *"10 ideias sobre IA em marketing"* (themed)

What happens:
1. Claude checks `public/Instagram Briefings/Trend Scouts <recent months>/` and `public/Instagram Briefings/Ideas <recent months>/` so it doesn't repitch a subject already covered.
2. It pulls fresh material from three angles: marketing/branding industry news (RSS + Tavily first, then general search), Instagram/Reels trends worldwide (RSS + search), and correlatable dates (on-this-day, anniversaries).
3. It filters down to **exactly 10** pitches, balanced across the 3 content pillars, anchor types, and subject domains.
4. It shows you the 10 as a scannable menu and **stops** — it never picks for you.
5. The full list of 10 (not just your pick) is saved to `public/Instagram Briefings/Trend Scouts <Month>/Trend Scout - <YYYY-MM-DD>.md`.

**Your action:** reply with the number (or subject) you want to run with. Say "run all the way through design and caption" if you want Steps 1→3 to chain automatically without you re-prompting.

---

## Step 1 — Idea Engine (the brief)

**Skill:** `rarity-ig-idea-engine`
**Say:** *"Decode Ayrton Senna for a post"* / *"3 Instagram ideas for this week"* (skips Step 0, researches directly) / or just continue after picking a Step 0 pitch.

What happens:
1. Claude establishes the **trigger** (your named subject, or its own live research if you didn't name one) and verifies it with real sources — never from memory.
2. It assigns one of the 3 pillars (Growth Marketing & Branding / Business & Strategy / Mindset & High Performance), rotating so a batch doesn't repeat one.
3. It **decodes** the real story into one sharp insight + one takeaway.
4. It picks **static vs. carousel** and writes the Hook (one of 5 named triggers), the headline (with the `*italic accent word*` marked), the open loop subhead, slide copy if carousel, and a draft caption — all in **English, then Spanish, then Portuguese**.
5. It sources and scores a **distinct real photo for every single slide** (never a flat/gradient card), each one passing the image QA gate (subject match, resolution, impact, currency).
6. Both the copy and the images run through their QA gates (`editorial-qa.md`, `image-qa.md`) before the brief is considered done.
7. It produces the **Content Idea Brief as a Word document (.docx)** — never markdown — via `scripts/build_brief_docx.js`.

**Output location:** `public/Instagram Briefings/Ideas <Month>/Idea N - <Short Name>.docx`
**Your action:** review the brief. Say "build this post" to move to Step 2, or ask for edits/alternate headlines first.

---

## Step 2 — Designer (the art)

**Skill:** `rarity-ig-designer`
**Say:** *"Build this post"* / *"cria a arte"* / *"design this"* (after a brief exists)

What happens:
1. Claude reads the brief and pulls the hook, headline (EN+ES+PT), subhead, slide copy, per-slide image URLs, and accent color.
2. It downloads every slide's distinct image into `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/` (`hero.jpg` + `bg2.jpg...bgN.jpg`).
3. It writes a JSON render spec and runs `scripts/render_post.py` — **100% rendered in Python/Pillow, never Canva or Figma** — producing `slide-1.png ... slide-N.png` per language.
4. It opens and critiques every PNG like a creative director (overflow, contrast, monotony between slides) before calling it done, then renders **English first, then Spanish, then Portuguese** as visual twins (same fonts/colors/layout, only the copy changes).

**Output location:** `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/EN/`, `/ES/`, `/PT/`
**Your action:** review the PNGs. Say "write the caption" to move to Step 3, or ask for design tweaks (re-renders are fast).

---

## Step 3 — Captions (ship it)

**Skill:** `rarity-ig-captions`
**Say:** *"Write the caption"* / *"escreve a legenda"* (after a brief and/or the art exists — also works standalone from just a topic)

What happens:
1. Claude pulls the real fact, insight, and takeaway from the brief (not the brief's own rough `## CAPTION` draft, which this skill overrides), plus whatever actually ended up on the rendered image.
2. It picks ONE opening technique (Thesis, Blunt Fact Drop, Confession, Direct Address, etc.) that survives Instagram's ~125-character truncation.
3. It writes three tight paragraphs + a save/share close — **zero hashtags, zero emoji, always** — then rebuilds the same technique fresh in Spanish, then in Brazilian Portuguese (true adaptation, not translation).
4. It runs the human-voice test on all three before shipping.

**Output location:** `Caption - <Short Name>.md` in `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/` (next to the art), or `public/Instagram Briefings/Ideas <Month>/` if no art yet.
**Your action:** copy the EN/ES/PT captions next to the matching PNG set and post. **This is the last step — the post is done.**

---

## Folder map (everything lives under `public/Instagram Briefings/`)

```
public/Instagram Briefings/
├── Trend Scouts <Month>/
│   └── Trend Scout - <YYYY-MM-DD>.md          ← Step 0 output (all 10 pitches)
├── Ideas <Month>/
│   └── Idea N - <Short Name>.docx             ← Step 1 output (the brief, EN+ES+PT)
└── Designs <Month>/
    └── <Idea N - Name>/
        ├── hero.jpg, bg2.jpg...               ← sourced slide images
        ├── EN/slide-1.png ... slide-N.png     ← Step 2 output
        ├── ES/slide-1.png ... slide-N.png
        ├── PT/slide-1.png ... slide-N.png
        └── Caption - <Short Name>.md          ← Step 3 output
```
`<Month>` = the calendar month the content is for (defaults to the current month). Numbering (`Idea N`) never restarts within a month — a batch continues from the highest existing number.

---

## House rules that apply across every step
- **No em dashes, en dashes, or hyphen-as-pause** in any posted headline or caption (any language).
- **Hashtags:** max 3 on the on-image copy; **zero** on the final caption (Step 3 overrides Step 1's draft).
- **No emoji** in headlines; none at all in captions.
- **No date ever rendered on the art** — month/year is only used for internal folder filing.
- **Never invent a fact, quote, or number.** If it can't be verified live, drop the anchor and pick another.
- **English → Spanish → Portuguese**, in that order, everywhere, every step. Spanish and Portuguese are always a true adaptation of the idea, never a literal translation.

## Quick reference — what to say at each stage
| You want... | Say this |
|---|---|
| A menu of ideas to choose from | "Give me 10 ideas for this week" |
| A specific subject, no menu | "Decode [person/brand/event] for a post" |
| Several ideas, no menu | "Give me 3 Instagram ideas for this week" |
| The art for an existing brief | "Build this post" |
| The caption for an existing brief/art | "Write the caption" |
| Everything in one go | "Scout 10 ideas, then take #4 all the way through design and caption" |
