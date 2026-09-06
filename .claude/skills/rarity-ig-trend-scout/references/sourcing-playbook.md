# Sourcing Playbook — Trend Scout

How to actually run the three legs, what makes a candidate strong enough to survive the cut to 10, and
how to keep the final 10 genuinely diverse instead of ten versions of the same headline.

**Search tooling available in this project:** the `tavily-search` MCP server (news-optimized web search,
use `topic: "news"` for time-sensitive queries) and the `rss-reader` MCP server (direct feed fetch, see
`references/rss-sources.md`). Prefer Tavily's news mode over generic web search for the query patterns
below when it's connected — it's tuned for exactly this "what happened recently" retrieval.

## Contents
0. The DTC scoping test (direction from Caio, 2026-09-06)
1. Leg one: e-commerce and DTC industry news
2. Leg two: Instagram and Reels trends worldwide
3. Leg three: correlatable facts (dates, anniversaries, calendar moments)
4. The quality bar (what survives the cut to 10)
5. Diversity and rotation logic

---

## 0. The DTC scoping test (direction from Caio, 2026-09-06)

Rarity's content is anchored in the **e-commerce DTC industry**. Before a candidate goes any further,
ask: would a DTC founder or e-commerce operator actually stop scrolling for this? Two ways a candidate
passes:

- **Direct** — the story's subject IS a DTC or e-commerce brand, platform, or mechanic: a DTC brand's
  funding round, a Shopify or TikTok Shop feature, a subscription-commerce tactic, a checkout/retention
  number, a founder's decision, a DTC brand's move into wholesale or physical retail (or the reverse).
- **By lesson** — the subject is a bigger, non-DTC retailer or platform, but the specific mechanic is one
  a DTC operator can actually steal: a big retailer's loyalty-program math, a legacy brand's TikTok Shop
  pilot, a platform algorithm change that affects anyone selling through it. The Amazon ad-auction
  lawsuit or a Sephora TikTok Shop pilot both pass this way even though neither is a "DTC startup" story.

What does NOT pass: general brand-marketing or ad-agency news with no commerce mechanic underneath it — a
QSR chain's new ad campaign, an agency account switching hands, a CMO hire at a legacy brand with no
digital/DTC angle. That's the wrong feed now, even if it was fair game before this direction.

**"Broad" means broad across DTC, not narrow.** E-commerce/DTC spans a lot of ground — fashion and
apparel, beauty and personal care, food and beverage, wellness and supplements, home and lifestyle, pets,
fitness, electronics and gadgets, subscription/box commerce, and marketplace-native brands (TikTok Shop
sellers, Amazon aggregators). A batch of 10 should prove that breadth (see section 5), not read like it
only knows one vertical exists.

---

## 1. Leg one: e-commerce and DTC industry news

**Start with direct RSS.** Call `fetch_feed_entries` (via the `rss-reader` MCP server) on the e-commerce/
DTC feeds in `references/rss-sources.md` — Retail Dive, Modern Retail, Glossy, Practical Ecommerce, Chain
Store Age, Digital Commerce 360. This is faster and more reliable than search for "what's fresh right
now," and Modern Retail and Glossy in particular cover DTC-native brands directly rather than only big
legacy retail. Use `fetch_article_content` on any promising hit to pull the real mechanism or number
before pitching it.

Then get the real current month and year (don't assume from memory), and search broadly before narrowing
to fill in what the feeds didn't cover. Query patterns that work:
- `"DTC brand news this week [month] [year]"`
- `"ecommerce industry news [current month] [year]"`
- `"direct to consumer brand funding OR acquisition [month] [year]"`
- `"Shopify OR TikTok Shop news this week"`
- `"[vertical] DTC brand launch OR funding"` (beauty, wellness, food and beverage, pet, home — rotate
  through verticals deliberately, don't just take whatever the first search returns)
- `"retail media news this week"` / `"checkout OR retention ecommerce news [month] [year]"`

Outlets whose roundups tend to surface well in search and are reliably current, beyond the RSS list:
Retail Brew, eMarketer/Insider Intelligence commerce coverage, Digiday's commerce/retail vertical, and
general martech/AI-in-commerce aggregators. You don't need to search these by name specifically;
searching the query patterns above naturally surfaces their coverage.

**What to pull out of a news hit:** not just "brand X did a thing," but the specific mechanism: what they
actually did, the number behind it (funding amount, conversion lift, revenue figure, timeline), and why
it's a genuine departure from what everyone else selling direct-to-consumer does. A write-up with no real
specific in it is not a usable pitch yet, keep searching.

**Time window — tighter than a general marketing beat.** Prefer the last 3 to 7 days for "this is
happening right now" pitches; 14 days is the hard ceiling, and only when the story is still visibly being
discussed (follow-on coverage, an ongoing lawsuit, a still-unfolding earnings reaction), not just
technically within range. A number or decision that was news two weeks ago and has already been absorbed
by the industry is stale — see section 4's freshness rule before pitching anything past a few days old.

---

## 2. Leg two: Instagram and Reels trends worldwide

**Reality check first:** there is no public "worldwide trending topics" board for Instagram the way
some platforms expose one, and Explore/Reels feeds are personalized per account, not global. The
reliable signal is published trend tracking: social media marketing sites run weekly or monthly
"what's trending on Instagram / Reels right now" roundups that aggregate what's actually spreading
across regions and niches. Treat those as the primary source.

**Start with direct RSS.** Call `fetch_feed_entries` on the social-media feeds in
`references/rss-sources.md` — Social Media Today, Hootsuite Blog, Sprout Social Insights — before
searching. These three specifically track format and audio trends on a weekly cadence.

Query patterns that work:
- `"Instagram trends [current month] [year]"`
- `"what's trending on Instagram right now [month] [year]"`
- `"Instagram Reels trending audio this week"`
- `"top Instagram Reels trends [month] [year]"`

Sources whose roundups tend to surface: Later, Hootsuite, Sprout Social, SocialBee, SocialPilot,
NapoleonCat, Lightreel, Newengen, and similar social-media-marketing publications that specifically track
format and audio trends weekly.

**Optional live spot-check:** if Claude in Chrome is connected, browsing Instagram's own Explore or
Reels tab can sanity-check or freshen the picture. Treat it as a supplement, not the primary source,
since what it shows is personalized to whatever account is logged in.

**Read every trend through the DTC lens.** Rarity's feed is editorial, not meme-format content, and now
specifically speaks to DTC operators, so the pitch is almost never "do the exact trend." It's either
(a) the trend ITSELF as the anchor, decoded for what it reveals about attention, conversion, or retention
("DM shares now count 3-5x more than likes for reach — what does that mean for a DTC brand still
optimizing content for likes"), or (b) a stat or insight published alongside the trend roundup (share
rates, engagement shifts, format performance data) that itself is the real, citable fact worth decoding.
Pull the INSIGHT and its commerce implication, not the instructions for how to film the trend.

---

## 3. Leg three: correlatable facts (dates, anniversaries, calendar moments)

This extends the same anchor logic `rarity-ig-idea-engine`'s own trigger step already uses, applied
here to generate menu candidates rather than a single chosen anchor.

**Weight toward retail/commerce history first**, general history second, when both are available for a
given date: a DTC brand's founding or funding anniversary, a marketplace or platform's launch date
(Amazon, Shopify, Instagram Shopping), a shopping holiday, a retail-format milestone (the kind of thing
Piggly Wiggly's 1916 self-service opening represents). General history and pop-culture anniversaries
still work as a Date anchor, but only when the angle clearly ties back to a commerce mechanic — see
section 0's scoping test.

Query patterns that work:
- `"on this day [Month Day] retail OR ecommerce OR DTC history"`
- `"[Month Day] anniversary brand OR retailer launch"`
- `"[Month Day] shopping holiday OR retail history"`
- A look at what's on the retail/shopping calendar in the next 1 to 2 weeks (Prime Day, BFCM lead-up,
  a major shopping holiday, a platform's anniversary) that a DTC brand could plausibly piggyback

**Verify the specific detail**, not just the general topic, same discipline as `rarity-ig-idea-engine`'s
own trigger engine: the exact date, the exact figure, the exact quote. Many "on this day" business
anecdotes online are exaggerated or wrong; if a date-based claim can't be pinned down cleanly, either
soften it or drop it for a cleaner one.

---

## 4. The quality bar (what survives the cut to 10)

A raw candidate earns a spot in the final 10 only if it clears all of these:
- **Passes the DTC scoping test** (section 0) — directly about e-commerce/DTC, or teaches a mechanic a
  DTC operator can use.
- **Specific, not vague.** A real number, a named brand, a documented decision, an actual quote. "DTC
  brands are struggling with retention" is not a pitch. "A DTC brand lost millions in a single quarter
  because its own loyalty program was too generous" is.
- **Current, not stale (hard rule).** Ask directly: would this still stop someone scrolling today, or has
  the news cycle already moved past it? A story that's three weeks old and nobody's still discussing,
  or an IG trend that already peaked, fails this test even if everything else about it is strong.
  Freshness beats importance — a smaller story from this week usually beats a bigger story from three
  weeks ago that's already been fully digested by the industry.
- **Resonant for a DTC founder or e-commerce operator.** They should recognize the stakes immediately,
  even if they didn't know the specific story yet.
- **Decodable, not just newsworthy.** There has to be a plausible lesson or mechanism underneath it, not
  just "this happened." If you can't sketch even a rough one-line angle, it's not ready to pitch yet.
- **Sourced.** Keep the URL you found it through. Full primary-source verification happens after Caio
  picks (see SKILL.md's Output discipline), but the scouting source itself has to be real and specific
  enough to hand to `rarity-ig-idea-engine` as a starting point.
- **Graspable without jargon or inference (hard rule, 2026-07-11 from Caio).** The Angle line has to land
  in one read. If it only makes sense to someone who already knows a technical term (a chemical name, an
  acronym, a niche metric) or requires inferring an unstated pattern from two juxtaposed facts, rewrite
  the angle in plain language before it goes in the 10 — a pitch that only becomes clear after
  `rarity-ig-idea-engine` does the deep decode isn't ready to pitch yet. This surfaced from a real brief
  (Idea 11) where a jargon-heavy contrast ("glycinate vs oxide") made the finished carousel hard to
  understand even after it was fully built; catching an ungraspable angle here, before a full brief gets
  built on top of it, is cheaper than fixing it after. See `rarity-ig-idea-engine`'s `editorial-qa.md`
  clarity gate for the fuller version of this test — same bar, one step earlier in the pipeline.

Reject on sight: anything that fails the DTC scoping test, generic "X launches new campaign" write-ups
with no real mechanism, anything that reads like a listicle tip in a trend's clothing, anything you can't
trace to an actual source from this search session, anything visibly stale, and any angle that only works
if the reader already has specialist knowledge.

---

## 5. Diversity and rotation logic

Applied while narrowing raw candidates down to the final 10, not as an afterthought:
- **Pillar spread** — actively look for Growth Marketing & Branding, Business & Strategy, and Mindset &
  High Performance angles, not just whichever pillar the raw material happens to skew toward. If the
  news cycle is dominated by one theme (often AI right now), search specifically for a Business &
  Strategy or Mindset angle rather than filling all 10 slots with the same lens.
- **Anchor-type spread** — mix news, IG trend, and correlatable-date pitches. Ten news stories with no
  trend or date-based pitch mixed in defeats the point of running all three legs.
- **DTC vertical spread** — fashion and apparel, beauty and personal care, food and beverage, wellness
  and supplements, home and lifestyle, pets, fitness, electronics and gadgets, subscription/box commerce,
  and marketplace-native brands (TikTok Shop, Amazon aggregators). Don't let all 10 come from the same
  vertical just because that's where the news happened to be dense this week — if beauty DTC dominated
  this run's search results, deliberately search another vertical (pets, home, food and beverage) before
  finalizing the 10.
- **Format spread** — note a rough static-versus-carousel guess per pitch so the final batch, once
  built out, won't turn into ten carousels in a row.

This mirrors `rarity-ig-idea-engine`'s own batch rotation discipline (pillar, anchor type, format,
subject domain), applied one step earlier, to a wider set of options, now scoped to e-commerce/DTC.
