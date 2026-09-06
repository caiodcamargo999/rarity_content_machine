# Sourcing Playbook — Trend Scout

How to actually run the three legs, what makes a candidate strong enough to survive the cut to 10, and
how to keep the final 10 genuinely diverse instead of ten versions of the same headline.

**Search tooling available in this project:** the `tavily-search` MCP server (news-optimized web search,
use `topic: "news"` for time-sensitive queries) and the `rss-reader` MCP server (direct feed fetch, see
`references/rss-sources.md`). Prefer Tavily's news mode over generic web search for the query patterns
below when it's connected — it's tuned for exactly this "what happened recently" retrieval.

## Contents
1. Leg one: marketing and branding industry news
2. Leg two: Instagram and Reels trends worldwide
3. Leg three: correlatable facts (dates, anniversaries, calendar moments)
4. The quality bar (what survives the cut to 10)
5. Diversity and rotation logic

---

## 1. Leg one: marketing and branding industry news

**Start with direct RSS.** Call `fetch_feed_entries` (via the `rss-reader` MCP server) on the industry-news
feeds in `references/rss-sources.md` — Adweek, Marketing Dive, Digiday, AdExchanger, PR Daily. This is
faster and more reliable than search for "what's fresh right now," and sidesteps outlets whose search
results are often bot-blocked. Use `fetch_article_content` on any promising hit to pull the real mechanism
or number before pitching it.

Then get the real current month and year (don't assume from memory), and search broadly before
narrowing to fill in what the feeds didn't cover. Query patterns that work:
- `"marketing branding industry news [current month] [year]"`
- `"brand marketing campaign this week [year]"`
- `"[industry] marketing news this week"` (advertising, martech, retail, fintech, whatever's relevant)
- `"best marketing campaigns [month] [year]"`
- `"AI marketing news [current month] [year]"` (AI is currently reshaping ad platforms, measurement,
  and content production fast enough that it resurfaces in almost every search window)

Outlets whose roundups tend to surface well in search and are reliably current: Marketing Dive, Adweek,
The Drum, Digiday, Ad Age, Marketing Brew, Famous Campaigns, Social Media Today, and general
martech/AI-news aggregators. You don't need to search these by name specifically; searching the query
patterns above naturally surfaces their coverage. (Ad Age and The Drum block direct feed fetches — see
`references/rss-sources.md`'s Known Gaps — so they only come in through search, not the RSS pass.)

**What to pull out of a news hit:** not just "brand X did a campaign," but the specific mechanism: what
they actually did, the number behind it (spend, reach, a stat, a timeline), and why it's a genuine
departure from what everyone else in that category does. A campaign write-up with no real specific in
it is not a usable pitch yet, keep searching.

**Time window:** prefer the last 7 to 14 days for "this is happening right now" pitches. A month-old
story can still work if it's still actively being discussed or if it ties cleanly to a correlatable date
(leg three), but don't reach past about 30 days unless it's functioning as an evergreen anchor rather
than a "current news" one.

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
NapoleonCat, Lightreel, and similar social-media-marketing publications that specifically track format
and audio trends weekly.

**Optional live spot-check:** if Claude in Chrome is connected, browsing Instagram's own Explore or
Reels tab can sanity-check or freshen the picture. Treat it as a supplement, not the primary source,
since what it shows is personalized to whatever account is logged in.

**What actually makes a good pitch out of a trend (this is the part that's easy to get wrong):** Rarity's
feed is editorial, not meme-format content, so the pitch is almost never "do the exact trend." It's
either (a) the trend ITSELF as the anchor, decoded for what it reveals about attention, psychology, or
marketing mechanics ("why is the trend built on borrowing someone else's music taste actually working,
and what does that teach about earned attention versus paid attention"), or (b) a stat or insight
published alongside the trend roundup (share rates, engagement shifts, "aesthetic content is losing to
timely discourse") that itself is the real, citable fact worth decoding. Pull the INSIGHT, not the
instructions for how to film the trend.

---

## 3. Leg three: correlatable facts (dates, anniversaries, calendar moments)

This extends the same anchor logic `rarity-ig-idea-engine`'s own trigger step already uses, applied
here to generate menu candidates rather than a single chosen anchor.

Query patterns that work:
- `"on this day [Month Day] marketing OR advertising OR brand history"`
- `"[Month Day] anniversary brand campaign"`
- `"[Month Day] brand history"` (some brands, like 7-Eleven's July 11 "Free Slurpee Day," have a
  built-in date pun baked into the calendar itself, which is an unusually strong, evergreen-but-timely
  correlatable fact)
- A look at what's on the calendar in the next 1 to 2 weeks (a major sporting event, a well-known
  product launch anniversary, a widely observed cultural date) that a brand could plausibly piggyback

**Verify the specific detail**, not just the general topic, same discipline as `rarity-ig-idea-engine`'s
own trigger engine: the exact date, the exact figure, the exact quote. Many "on this day" business
anecdotes online are exaggerated or wrong; if a date-based claim can't be pinned down cleanly, either
soften it or drop it for a cleaner one.

---

## 4. The quality bar (what survives the cut to 10)

A raw candidate earns a spot in the final 10 only if it clears all of these:
- **Specific, not vague.** A real number, a named brand, a documented decision, an actual quote. "Brands
  are using AI more" is not a pitch. "2,000+ brands are already running ads inside ChatGPT" is.
- **Resonant for Rarity's audience.** Founders, marketers, and brand builders should recognize the
  stakes immediately, even if they didn't know the specific story yet.
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

Reject on sight: generic "X launches new campaign" write-ups with no real mechanism, anything that reads
like a listicle tip in a trend's clothing, anything you can't trace to an actual source from this search
session, and any angle that only works if the reader already has specialist knowledge.

---

## 5. Diversity and rotation logic

Applied while narrowing raw candidates down to the final 10, not as an afterthought:
- **Pillar spread** — actively look for Growth Marketing & Branding, Business & Strategy, and Mindset &
  High Performance angles, not just whichever pillar the raw material happens to skew toward. If the
  news cycle is dominated by one theme (often AI right now), search specifically for a Business &
  Strategy or Mindset angle rather than filling all 10 slots with the same lens.
- **Anchor-type spread** — mix news, IG trend, and correlatable-date pitches. Ten news stories with no
  trend or date-based pitch mixed in defeats the point of running all three legs.
- **Subject-domain spread** — tech, fashion, food and beverage, sport, finance, luxury, and so on. Don't
  let all 10 come from the same industry just because that's where the news happened to be dense this
  week.
- **Format spread** — note a rough static-versus-carousel guess per pitch so the final batch, once
  built out, won't turn into ten carousels in a row.

This mirrors `rarity-ig-idea-engine`'s own batch rotation discipline (pillar, anchor type, format,
subject domain), applied one step earlier, to a wider set of options.
