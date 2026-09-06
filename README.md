# Rarity Instagram Content System

A four-skill pipeline that produces non-generalist Instagram content for **@rarity.agency** — in the
editorial spirit of **@brandsdecoded__**, **@vinci.society**, **@blankschoolbr** and **@matthgray**, but
anchored to real people, brands, and events and run through Rarity's own brand identity.

```
 Marketing/branding news · Instagram & Reels trends worldwide · correlatable dates
        │
        ▼
 ┌───────────────────────┐   10 pitches, a menu
 │ rarity-ig-trend-scout  │ ── Caio picks ONE ──┐
 │ STEP 0 — the SCOUT     │                     │
 └───────────────────────┘                      ▼
                              Real-life trigger / icon (the picked idea)
                                     │
                                     ▼
 ┌──────────────────────┐   Content Idea Brief    ┌──────────────────────┐   brief + finished art   ┌──────────────────────┐
 │ rarity-ig-idea-engine │ ───────────────────────▶│  rarity-ig-designer  │ ─────────────────────────▶│  rarity-ig-captions  │
 │ STEP 1 — the IDEA     │   (EN + ES)              │ STEP 2 — the ART     │                            │ STEP 3 — the CAPTION │
 └──────────────────────┘                          └──────────────────────┘                            └──────────────────────┘
   web-researches a real anchor,                     renders 100% in Claude                              writes the human, pattern-
   decodes it into ONE lesson,                        (Python/Pillow, no Canva/                          interrupt caption that pairs
   rotates 3 pillars, EN + ES                          Figma), full-bleed photo +                        with the art, EN + ES
                                                        editorial serif headline,
                                                        EN + ES
```

## The four skills

**0. `rarity-ig-trend-scout` (Step 0 — the scout)**
Runs BEFORE the idea engine. Live-researches current marketing/branding industry news, worldwide
Instagram and Reels trends, and correlatable facts (on-this-day anniversaries, date puns), and turns
the strongest findings into exactly **10 fast, sourced pitches** — different subjects, different
pillars, different anchor types. Presents them as a menu and waits for Caio to pick ONE. Also works
themed ("10 ideas about AI in marketing") and dedupes against subjects already covered in recent briefs.

**1. `rarity-ig-idea-engine` (Step 1 — the idea)**
Takes a trigger (from Step 0's pick, a subject Caio names directly, or its own research if asked for a
batch with no prior scouting) and decodes it into one sharp lesson, verified with live web search.
Rotates three pillars — Growth Marketing & Branding, Business & Strategy, Mindset & High Performance.
Outputs a structured **Content Idea Brief** (English + Spanish) as a Word doc, with the headline, a
draft caption, the **real image(s) embedded from the web** (one per slide), and a visual direction for
Step 2.

**2. `rarity-ig-designer` (Step 2 — the art)**
Takes the brief and renders the post **100% in Claude** — Python/Pillow, no design connector (never
Canva, never Figma). Every slide gets its own full-bleed, high-impact photo, a big editorial serif
headline with an italic accent word, and the Rarity symbol stamped transparent in the corner. Produces
an English version plus a true Spanish version.

**3. `rarity-ig-captions` (Step 3 — the caption)**
Takes the brief's decode and the finished art and writes the actual caption that ships with the post: a
human, pattern-interrupt caption that adds a beat the image didn't have room for, instead of restating
the headline. No hashtags, no emoji, ever. Reference energy: @brandsdecoded__ (grounded in real, current
captions from the account, not assumption). English + Spanish (true adaptation, not translation). Also
works standalone, without a brief.

## Install
Each skill is packaged as a `.skill` file in this folder:
- `rarity-ig-trend-scout.skill`
- `rarity-ig-idea-engine.skill`
- `rarity-ig-designer.skill`
- `rarity-ig-captions.skill`

Install via the **Save skill** button when they're presented in chat, or **Settings → Capabilities →
add skill**. (The unzipped source folders are here too, so you can read or tweak them.)

## How to use
- "Give me 10 ideas for this week" → Step 0 scouts and presents 10 pitches; say which one to run with.
- "Give me 3 Instagram ideas for this week for Rarity" (skipping the scout) → Step 1 produces 3 briefs
  (rotated pillars) directly from its own research.
- "Decode Ayrton Senna for a post" → Step 1 produces a Senna brief directly, no scouting needed.
- "Build this post" (after a brief) → Step 2 renders the EN + ES art.
- "Write the caption" (after a brief and/or the art) → Step 3 writes the EN + ES caption.
- You can also run them back-to-back: "scout 10 ideas, then take #4 all the way through design and
  caption."

## Brand assets used (Step 2)
Pulled from **Branding Rarity/** in this project:
- Headline / display: **Playfair Display** (editorial serif, the @vinci.society direction; bundled at
  `assets/headline.ttf` + italic — drop a licensed serif to override). Body / eyebrow / handle:
  **BentonSans** (Regular + Thin).
- Colors: navy `#001A70` (photo duotone tint), dark purple `#0f0a1a` / `#1a0f2e`, teal `#0fc1af` (eyebrow
  / stat label), accent rotates **magenta `#D50057` (default), shock yellow `#FFE400`, red `#FF3B3B`**,
  energy gradient `#0046FF → #9B00C8 → #D50057`, white headline text `#FFFFFF`.
- Logo: white wordmark (dark bg) + blue wordmark (light bg). Symbol: the transparent white "Y" mark,
  stamped small in the corner of every slide; the full white logo goes on the carousel's CTA slide.
- Photos render in their real colours (no brand-navy wash) — only a subtle vignette + bottom scrim.

## Folder contents
```
Instagram Content System/
├── README.md                              ← this file
├── EXAMPLE — Senna static (Step 1 output).md   ← sample brief from Step 1
├── rarity-ig-trend-scout.skill             ← installable
├── rarity-ig-idea-engine.skill             ← installable
├── rarity-ig-designer.skill                ← installable
├── rarity-ig-captions.skill                ← installable
├── rarity-ig-trend-scout/                  ← source (SKILL.md + references)
├── rarity-ig-idea-engine/                  ← source (SKILL.md + references)
├── rarity-ig-designer/                     ← source (SKILL.md + references + brand fonts/colors)
└── rarity-ig-captions/                     ← source (SKILL.md + references)
```
