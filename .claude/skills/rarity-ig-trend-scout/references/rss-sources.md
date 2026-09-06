# Curated RSS Sources (MCP)

These feeds are fetched directly via the `rss-reader` MCP server (tools: `fetch_feed_entries`,
`fetch_article_content`), instead of relying only on general web search. Direct RSS is faster, avoids
bot-blocked search results, and guarantees the source is a real, dated, traceable publication — every
URL below was verified live (returns a valid RSS/Atom document, checked 2026-08-25).

Use this as the FIRST pass for Leg 1 (industry news) and Leg 2 (Instagram/Reels trends) in
`sourcing-playbook.md`, then fall back to general web search (query patterns in that file) for anything
these feeds don't cover, or for a named subject not covered by any of them.

## Marketing & advertising industry news
| Source | Feed URL |
|---|---|
| Adweek | https://www.adweek.com/feed/ |
| Marketing Dive | https://www.marketingdive.com/feeds/news/ |
| Digiday | https://digiday.com/feed/ |
| AdExchanger | https://www.adexchanger.com/feed/ |
| PR Daily | https://www.prdaily.com/feed/ |

## Branding
| Source | Feed URL |
|---|---|
| Branding in Asia | https://www.brandinginasia.com/feed/ |
| Branding Strategy Insider | https://brandingstrategyinsider.com/feed/ |

## Social media / Instagram & Reels trends worldwide
| Source | Feed URL |
|---|---|
| Social Media Today | https://www.socialmediatoday.com/feeds/news |
| Hootsuite Blog | https://blog.hootsuite.com/feed/ |
| Sprout Social Insights | https://sproutsocial.com/insights/feed/ |

## SEO / content marketing
| Source | Feed URL |
|---|---|
| Search Engine Journal | https://www.searchenginejournal.com/feed/ |
| HubSpot Marketing Blog | https://blog.hubspot.com/marketing/rss.xml |

## How to use in a scouting pass
1. Call `fetch_feed_entries` on each feed relevant to the leg you're running (industry news → the first
   two tables; IG/Reels trends → the third table), with a reasonable `limit` (15–25 is enough to spot
   what's fresh without drowning in back-catalog).
2. Skim titles/summaries for candidates that clear the quality bar in `sourcing-playbook.md` (specific,
   decodable, resonant).
3. For a promising hit, call `fetch_article_content` on its URL to pull the full piece and extract the
   real mechanism, number, or quote — a title alone is never enough to pitch from.
4. Still run general web search (query patterns in `sourcing-playbook.md`) alongside this: these feeds
   are a strong baseline, not exhaustive, and Leg 3 (correlatable dates) has no feed equivalent at all.

## Known gaps (do not rely on these — blocked or defunct as of 2026-08-25)
Ad Age, The Drum, Campaign (US/UK/Asia), Marketing Week, PR Week, and Search Engine Land all block
automated feed fetches (Cloudflare bot checks) or no longer publish at the expected RSS path. Their
coverage still surfaces fine through general web search (they're well-indexed), just not via direct
feed fetch. Re-check periodically — outlets change their bot-protection and feed setup without notice.
