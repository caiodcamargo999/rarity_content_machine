# Curated RSS Sources (MCP)

These feeds are fetched directly via the `rss-reader` MCP server (tools: `fetch_feed_entries`,
`fetch_article_content`), instead of relying only on general web search. Direct RSS is faster, avoids
bot-blocked search results, and guarantees the source is a real, dated, traceable publication — every
URL below was verified live (returns a valid RSS/Atom document, checked 2026-09-06, the day Rarity's
content focus narrowed to e-commerce/DTC).

Use this as the FIRST pass for Leg 1 (e-commerce/DTC industry news) and Leg 2 (Instagram/Reels trends) in
`sourcing-playbook.md`, then fall back to general web search (query patterns in that file) for anything
these feeds don't cover, or for a named subject not covered by any of them.

## E-commerce & DTC industry news (primary, since 2026-09-06)
| Source | Feed URL | Notes |
|---|---|---|
| Modern Retail | https://www.modernretail.co/feed/ | Best direct fit — covers DTC-native brands, not just legacy retail. |
| Retail Dive | https://www.retaildive.com/feeds/news/ | Broad retail, strong on public-company earnings/strategy detail. |
| Glossy | https://www.glossy.co/feed/ | Fashion and beauty DTC specifically. |
| Practical Ecommerce | https://www.practicalecommerce.com/feed | Operator-level tactics (checkout, TikTok Shop, tools) — small/mid DTC merchant angle. |
| Digital Commerce 360 | https://www.digitalcommerce360.com/feed/ | Broad e-commerce, good AI-in-commerce and platform-feature coverage. |
| Chain Store Age | https://chainstoreage.com/rss.xml | Skews legacy chain retail — use for the "by lesson" scoping path (section 0), not pure DTC. |

## Social media / Instagram & Reels trends worldwide
| Source | Feed URL |
|---|---|
| Social Media Today | https://www.socialmediatoday.com/feeds/news |
| Hootsuite Blog | https://blog.hootsuite.com/feed/ |
| Sprout Social Insights | https://sproutsocial.com/insights/feed/ |

## Branding (secondary — only for the "by lesson" scoping path)
| Source | Feed URL |
|---|---|
| Branding Strategy Insider | https://brandingstrategyinsider.com/feed/ |

## SEO / content marketing (secondary)
| Source | Feed URL |
|---|---|
| Search Engine Journal | https://www.searchenginejournal.com/feed/ |
| HubSpot Marketing Blog | https://blog.hubspot.com/marketing/rss.xml |

## How to use in a scouting pass
1. Call `fetch_feed_entries` on each feed relevant to the leg you're running (e-commerce/DTC news → the
   first table; IG/Reels trends → the second table), with a reasonable `limit` (15–25 is enough to spot
   what's fresh without drowning in back-catalog).
2. Skim titles/summaries for candidates that clear the quality bar in `sourcing-playbook.md` (specific,
   decodable, resonant, DTC-scoped, current).
3. For a promising hit, call `fetch_article_content` on its URL to pull the full piece and extract the
   real mechanism, number, or quote — a title alone is never enough to pitch from.
4. Still run general web search (query patterns in `sourcing-playbook.md`) alongside this: these feeds
   are a strong baseline, not exhaustive, and Leg 3 (correlatable dates) has no feed equivalent at all.

## Known gaps (do not rely on these — blocked, defunct, or checked and failed as of 2026-09-06)
Ad Age, The Drum, Campaign (US/UK/Asia), Marketing Week, PR Week, and Search Engine Land all block
automated feed fetches (Cloudflare bot checks) or no longer publish at the expected RSS path. AdExchanger
and Digiday (general marketing/ad-tech, not DTC-specific) are no longer the primary Leg 1 sources now
that the focus is e-commerce/DTC, but their coverage is still fine through general web search when a
story crosses into commerce. DTC Newsletter (dtcnewsletter.com/feed), Retail Brew
(retailbrew.com/feed and /rss/latest), eMarketer (emarketer.com/rss), and Common Thread Collective's blog
were all tried and returned 403/404 — their coverage still surfaces through general web search, just not
via direct feed fetch. Re-check periodically — outlets change their bot-protection and feed setup without
notice.
