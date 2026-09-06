---
name: rarity-ig-trend-scout
description: "Scouts 10 fresh Instagram content ideas for Rarity BEFORE the idea engine runs, sourced from live research across e-commerce and DTC industry news, worldwide Instagram and Reels trends (read for what a DTC brand can learn from them), and correlatable facts like on-this-day brand anniversaries. Rarity's content focus is the e-commerce DTC industry — every pitch has to be genuinely useful or resonant to a DTC founder or e-commerce operator, sourced broadly across DTC verticals (fashion, beauty, food and beverage, wellness, home, pets, fitness, electronics, subscription commerce, marketplace-native brands), and has to be CURRENT — real news from the last few days, not a stale story nobody's still talking about. STEP 0 of the Rarity IG pipeline: presents all 10 as a scannable menu with the real fact, why it is timely, a suggested pillar, and a source for each, then waits for Caio to pick ONE before handing that idea's research straight to rarity-ig-idea-engine for the full decode and brief. ALWAYS use when Caio asks for content ideas, trend scouting, what to post, ideias pra essa semana, o que ta em alta, ideas de contenido, 10 ideias, scan the news, or wants a batch of options to choose from rather than one finished idea. When in doubt, USE this skill before rarity-ig-idea-engine."
---

# Rarity IG — Trend Scout (Step 0, before the idea engine)

**Rarity's content is anchored in the e-commerce DTC industry** (direction from Caio, 2026-09-06). Every
pitch this skill surfaces has to be something a DTC founder or e-commerce operator would actually stop
and read — not general brand-marketing news about a legacy CPG or QSR chain doing an ad campaign, unless
the mechanic it teaches is genuinely useful to someone running a direct-to-consumer or e-commerce
business. "Broad" here means broad *across DTC*: fashion and apparel, beauty and personal care, food and
beverage, wellness and supplements, home and lifestyle, pets, fitness, electronics and gadgets,
subscription/box commerce, and marketplace-native brands (TikTok Shop, Amazon aggregators) are all fair
game — this is a wide industry, not a narrow one, and the batch of 10 should prove that by spanning
several of these verticals, not camping on one. See `references/sourcing-playbook.md` section 0 for the
full scoping test.

This skill finds **candidates**, not a finished idea. It casts a wide net across current e-commerce and
DTC industry news, worldwide Instagram and Reels trends (read through a DTC lens — what does this trend
reveal about attention, conversion, or retention, not just what the meme is), and correlatable facts
(on-this-day anniversaries, date puns, cultural moments), turns the strongest of what it finds into
**exactly 10 fast, scannable pitches**, and stops. Caio picks ONE. Only then does the real work start in
`rarity-ig-idea-engine` (Step 1), which takes that one pick and builds the full decode, hook, images, and
brief.

**Why this exists as its own step:** `rarity-ig-idea-engine` is built to go deep on one idea at a time.
Going deep is slow and worth doing properly (verification, hook engineering, image sourcing, the QA
gate). Spending that effort on an idea before Caio has seen the alternatives risks building the wrong
thing well. This skill's whole job is breadth, fast, so the depth that follows is spent on the idea
Caio actually wants.

---

## What "good" looks like (read this first)

1. **Every pitch is grounded in something real, found through live search just now, not memory.**
   Trends and news drift by the week; a scout skill working from training-data memory would suggest
   stale, dead, or made-up material. Run the searches in `references/sourcing-playbook.md` fresh, every
   time.
2. **Every pitch has to actually be about, or genuinely useful to, e-commerce and DTC.** That's Rarity's
   whole content focus now. A general brand-marketing story (a legacy CPG ad campaign, a QSR sponsorship)
   only earns a slot if the mechanic underneath it is something a DTC operator can use — otherwise it's
   the wrong feed. See `references/sourcing-playbook.md` section 0 for the scoping test.
3. **It has to be current, not old news or something nobody's still talking about.** A story that's
   technically true but already stale — the news cycle moved on, the trend peaked weeks ago — fails even
   if it's specific and DTC-relevant. See the freshness rule in `references/sourcing-playbook.md` section
   4.
4. **Exactly 10 pitches, and they're genuinely different from each other.** Different DTC vertical
   (fashion, beauty, food and beverage, wellness, home, pets, fitness, electronics, subscription,
   marketplace-native), different pillar, different anchor type (news story, live IG trend, correlatable
   date). Ten variations on the same AI story, or ten stories about the same vertical, is not ten ideas.
5. **Each pitch is fast to evaluate, not a mini-brief.** One glance should tell Caio what it is, why it's
   timely, and roughly where it would land (pillar, static or carousel). The deep decode, the hook
   trigger, the headline, the images: all of that is `rarity-ig-idea-engine`'s job once one is picked,
   not this skill's.
6. **Nothing repeats a subject already used in a recent Rarity brief.** Check what's already been posted
   before pitching it again (step 2 below).
7. **It stops and waits.** This skill's job ends at presenting the 10 and asking which one. It does not
   pick for Caio, and it does not start decoding before he answers.
8. **Once Caio picks, the handoff carries the research forward.** The chosen pitch's fact, source, and
   suggested pillar go straight into `rarity-ig-idea-engine` so Step 1 isn't re-researching from
   scratch, only deepening what Step 0 already found.

---

## Workflow

### 1. Read the references first
Skim `references/sourcing-playbook.md` for the three sourcing legs and their query patterns,
`references/rss-sources.md` for the curated, verified RSS feeds fetched via the `rss-reader` MCP server
(use these as the first pass for Legs 1 and 2, before general web search), and `references/pitch-template.md`
for the exact pitch-card format and a full worked example of 10 real pitches from a real day's research.

### 2. Check for recent repeats
Look for existing brief slugs in `public/Instagram Briefings/Ideas <recent months>/` (the last 1 to 2 months
is usually enough). Note any subjects already covered so step 4 doesn't re-pitch them. If the folder
doesn't exist yet or is empty, skip this step, nothing to dedupe against.

### 3. Run the three sourcing legs
Per `references/sourcing-playbook.md`:
- **E-commerce and DTC industry news** — funding and M&A, platform shifts (Shopify, TikTok Shop, Amazon),
  founder moves, retention and checkout tactics, category disruption, DTC brands going wholesale/retail
  or vice versa, AI-in-commerce developments, notable wins and failures. Prefer the last 3 to 7 days, hard
  cap 14 unless the story is still actively live.
- **Instagram and Reels trends worldwide** — current formats, audio, and the published insight about
  *why* something is working right now, read through what it means for a DTC brand's content or
  conversion strategy, not just what the meme is.
- **Correlatable facts** — on-this-day anniversaries, brand name and date puns (get today's actual date
  first), upcoming calendar moments a brand could piggyback in the next 1 to 2 weeks. Weight toward
  retail/commerce history (a DTC brand's founding, a platform's launch anniversary, a shopping holiday)
  over general history when both options exist.

Cast a wide net first. Aim for 15 to 20 raw candidates across all three legs before narrowing. If Caio
gave a theme or focus ("ideas about AI," "something for the Business pillar," "beauty DTC only"), weight
the search toward that theme but still pull from all three legs.

### 4. Filter down to the strongest, most different 10
Apply the quality bar from `references/sourcing-playbook.md`: real, specific (a number, a decision, a
named brand, not a vague trend label), current (not stale — see section 4's freshness rule), resonant for
a DTC founder or e-commerce operator specifically, and genuinely usable as a decode, not just a headline.
Reject anything that's really a generic listicle tip wearing a trend's clothes, and reject anything that
isn't about e-commerce/DTC or teachable to someone who is. While narrowing, actively balance pillar,
anchor type, and DTC vertical per the rotation logic in `references/sourcing-playbook.md` rather than
just taking the top 10 by search-result order.

### 5. Write the 10 pitch cards
One per idea, in the exact format in `references/pitch-template.md`: a short title, the pillar, the
anchor type, a format guess, the real fact with its source, and a one-line angle. Keep each pitch to
three or four lines. This is a pitch, not a brief.

### 6. Present and wait
Show all 10 in chat as a numbered, scannable list. Close by asking directly which one Caio wants to take
forward. Don't pre-select a favorite unless asked; if asked for a recommendation, name one and say why in
a line, but still wait for confirmation before treating anything as chosen.

### 7. Hand off the pick
Once Caio names a number or a subject, summarize that one pitch's full research (the real fact, the
source, the suggested pillar, the anchor type) and tell Caio the next step is `rarity-ig-idea-engine`
with that anchor. If continuing in the same conversation, proceed straight into `rarity-ig-idea-engine`'s
own workflow using this pitch as the named subject, so its own trigger-finding step is skipped and it
goes straight to verifying and deepening the fact already found here.

### 8. Save the full list
Save all 10 (not just the chosen one) to `public/Instagram Briefings/Trend Scouts <Month>/Trend Scout -
<YYYY-MM-DD>.md`, so ideas Caio didn't pick this time are still on record for a future batch instead of
lost. Create the month folder if it doesn't exist, using the same `<Month>` convention as the other
skills' folders (current month by default).

---

## Output discipline
- **Exactly 10 pitches**, not 8, not 15, unless Caio explicitly asks for a different count.
- **No invented facts, stats, or trends.** Every pitch traces to a real search result from this run. If
  a promising lead can't be pinned to a specific, checkable detail, drop it rather than soften it into
  something vague.
- **No repeats of a subject covered in a recent brief** (step 2).
- **Every pitch is e-commerce/DTC**, either directly (the story is about a DTC or e-commerce brand or
  platform) or by lesson (a bigger retailer's move that teaches a mechanic a DTC operator can use).
  General brand marketing with no commerce angle doesn't belong in the 10.
- **Current, not stale.** If the news cycle has visibly moved on from a story, or an IG trend already
  peaked weeks ago, it doesn't earn a slot even if it's otherwise a strong pitch.
- **Balance across the 10**: aim for real spread across the three pillars (Growth Marketing & Branding,
  Business & Strategy, Mindset & High Performance), a mix of anchor types (not 10 news stories, not 10
  IG trends), and a mix of DTC verticals (fashion, beauty, food and beverage, wellness, home, pets,
  fitness, electronics, subscription, marketplace-native). Real search results sometimes skew heavily
  toward one theme (AI is dominating e-commerce news right now); when that happens, search harder for the
  underrepresented pillars and verticals rather than forcing 10 near-identical AI pitches.
- **This is a fast pass, not the verification gate.** Cite the source found during scouting; the deeper
  primary-source verification that `rarity-ig-idea-engine`'s own process requires happens after Caio
  picks, on the one idea that matters, not on all 10 upfront.

## Relationship to the other skills
This is **Step 0**, upstream of everything else: `rarity-ig-idea-engine` (Step 1, the decode and the
brief), `rarity-ig-designer` (Step 2, the art), and `rarity-ig-captions` (Step 3, the caption). Those
three keep their existing step numbering; this skill sits before Step 1 rather than renumbering the
whole pipeline. It produces no brief, no art, and no caption itself, only the shortlist and the handoff.
