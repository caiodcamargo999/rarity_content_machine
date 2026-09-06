# Headline Engine — data-backed patterns behind the hook

Ported and translated from BrandsDecoded's own "Content Machine" methodology (their internal system,
built on an analysis of 1,168 posts and a bank of 56 outlier hooks with 10k+ likes) — the same account
Rarity's hook doctrine already models itself on (see `editorial-playbook.md` section 1). This file is
a validation layer: it does not replace the five hook triggers (CONTRARIAN, AUTHORITY/ANTI-HERO,
INNOVATIVE IDEA, APPARENT NONSENSE, EXTREME CURIOSITY) or the six headline patterns already in the
playbook — it makes any of them sharper, and gives two extra rigid formats for when a straight flip or
number-shock isn't landing.

## 1. Lift-validated patterns (every headline needs at least one)
Real, measured performance deltas vs. baseline. Zero of these present = weak headline, rework it.

| Pattern | Lift | When it applies |
|---|---|---|
| Named place / cultural identity | +155% | Connects to a specific culture, country, or "local" identity the audience recognizes. Adapt to the post's market — Brazil, LatAm, Spain, the US, whichever the EN, ES, or PT version is speaking to. |
| End / Death / Crisis | +119% | Something is changing, ending, or at risk. |
| Generational | +119% | Names a generation or age-cohort behavior (Gen Z, Millennials, Boomers). |
| Novelty | +99% | Signals a new mechanism, an emerging shift, a recent turn. |

**Avoid — negative lift:**

| Pattern | Lift | Why it fails |
|---|---|---|
| Direct statement | -29% | Asserts without provoking curiosity or tension. |
| Generic "reveal" ("discover…", "find out…", "learn…") | -42% | Saturated format, reads as clickbait. |
| Listicle / numbered tips | flat | Dead format, no tension. |
| Empty motivational copy | flat | No data, no conflict, no point of view. |

## 2. Emotional triggers (need at least 2 active simultaneously)

| Trigger | What it activates |
|---|---|
| Nostalgia | Affective memory, "how it used to be." |
| Fear / alert | Urgency, something at risk. |
| Indignation | "This is wrong" — outrage. |
| Identity | "This is about me / my generation." |
| Curiosity | An information gap that has to be closed. |
| Aspiration | The desire to be, have, or reach something. |

One active trigger is emotionally weak. Zero triggers fails outright.

**Proven high-performing combos:** Nostalgia + Identity · Fear + Generational · Named place + Identity
· Curiosity + Nostalgia.

## 3. Rejection checklist (run on every headline before it ships)
Reject and **rewrite** (never just delete) any headline that:
- Is a **direct statement** with no provocation.
- Opens with a **generic reveal** — "Discover…", "Find out…", "Learn…".
- Is a **listicle** — "5 ways to…", "3 tips for…".
- Is **empty motivational** copy: no data, no conflict, no point of view.
- **Reads like generic AI copy** — say it out loud; if any account could have posted it, redo it.
- Leans on a banned construction: *"it's not X, it's Y"*, *"the rise of…"*, *"the impact of…"*,
  *"why X is changing everything"*, *"when X becomes Y"*, or uses "turned into" as its main verb.

## 4. Five extra rigid hook formats
Use alongside the six headline patterns in the playbook and the five hook triggers — stricter molds
for when a plain flip or number-shock doesn't land.

**Cultural Investigation** — `[Provocative reframe]: [curiosity hook]`, split by a colon. Clause 1
reframes the phenomenon; clause 2 opens a gap.
- Right: *"The death of taste: how the algorithm made everyone like the same five brands."*
- Right: *"Investigating the founders who fire their best salespeople: the retention math nobody
  runs."*
- Wrong — no colon, no reframe: *"Gyms reopened. Nobody stopped running."*
- Wrong — flat claim: *"Running is the new status symbol."*

**Magnetic Narrative** — three short sentences, no colon: `[Concrete scene]. [Mechanism]. [Open
tension]`. Sentence 1 shows what happened; sentence 2 explains the mechanism; sentence 3 opens the
loop.
- Right: *"Ferrari sells fewer cars every year on purpose. The waitlist is the marketing budget.
  Nobody at the company calls it scarcity."*
- Right: *"A copywriter died broke in 1963. His sales letters are still used, word for word, by
  agencies that have never heard his name."*
- Wrong — one sentence, no arc: *"Ferrari's scarcity strategy is changing luxury marketing."*

**Pop Reference Twist** — `How [a universally recognized reference] [does something unexpected]`.
Takes something everyone already knows and shows it acting against what people assume about it. The
twist has to be real and verifiable, not a rhetorical flourish.
- Right: *"How Ferrari's logo survived a company that almost never wins."*
- Right: *"How a jingle written in 1971 still outsells every ad made this year."*
- Wrong — states a fact with no unexpected action: *"Ferrari's logo has a long history."*

**Why X Is Becoming a Surprising Trend** — `Why [a named group or behavior] is [a trend that
contradicts expectation]`. Names a specific, real, checkable shift already underway — not a
hypothetical or a prediction.
- Right: *"Why senior marketers are quitting agencies to sell one single course."*
- Right: *"Why the best copywriters are refusing to write headlines anymore."*
- Wrong — vague, no named group: *"Why more people are changing how they work."*

**Existential Provocation** — a blunt, uncomfortable question about identity, mortality, or worth.
The post must genuinely answer it — this is not a rhetorical opener to be left hanging.
- Right: *"What happens to a brand after the founder everyone followed leaves?"*
- Right: *"Does anyone remember who came in second, in any industry?"*
- Wrong — never answered by the deck: *"What does it all mean?"*

All five formats work as the hook headline itself, or as the caption's opening line when the
headline on the image is a shorter flip.

## 5. Editorial QA
The full 7-parameter quality gate, the complete banned-construction lists, the jargon substitution
table, the AI-tone test, and the pre-ship review process now live in **`references/editorial-qa.md`**
— run every block of copy (headline, slide lines, caption, both languages) through that file before a
brief is locked. This file's section 3 rejection checklist above is headline-specific and
complementary to it; run both.

## 6. Anchored vs. generic internal slide lines
The short line under each slide's big number/word is a concrete claim, not a motivational slogan.

**Reject — generic, would fit almost any topic:**
- "Show up before everyone else."
- "The shift nobody saw coming."
- "Those who understand, win."

**Keep — anchored, only true of this specific idea:**
- "127 people on a waitlist. Zero ad spend."
- "What Ferrari understood before the rest of the industry."
- "One sales letter, sixty years, still unchanged."

Test: swap in a different brand or person. If the line still makes perfect sense, it's too generic —
rewrite it anchored to this idea specifically.

## Where this plugs into the workflow
Apply sections 1 to 4 while drafting the Headline and the carousel slide lines (main workflow step 7).
Run `references/editorial-qa.md`'s full gate right before the brief is locked and handed to
`docx-output.md` (step 8). Anything that fails gets rewritten — never shipped with a known weak spot.
