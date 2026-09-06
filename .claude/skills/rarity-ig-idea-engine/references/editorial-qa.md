# Editorial QA — the full quality gate for all copy

Ported and translated from BrandsDecoded's own editorial training manual and anti-slop filter (the
account Rarity's voice already models itself on — see `editorial-playbook.md` section 1). This is the
complete quality bar for every block of copy in a brief — headline, slide lines, and caption, in all
three languages — before it ships. Run this on the whole deck, after `headline-engine.md`'s headline-specific
checks.

## The mentality
Write like a sharp reporter for a serious business or culture publication, not like an AI translating a
template. The bar is not "is this grammatically correct" — it's "would a real journalist have written
this sentence." That second bar rejects almost everything that sounds robotic, corporate, or translated.

## The clarity gate — can a first-time reader get it? (hard rule, 2026-07-11 from Caio)
A carousel can pass every parameter below — clean grammar, real facts, editorial tone — and still fail if
the core idea itself never registers on a fast scroll. This happened on a real, shipped brief (Idea 11,
"The Ad That Explains"): the copy was well-written by every parameter, but the central contrast leaned on
chemistry jargon ("glycinate vs oxide") the audience doesn't reliably know, and two body slides had
kickers that didn't visually parallel each other ("The claim" next to "The other ad"), so the pattern the
whole idea depends on never clicked. Caio's own words after seeing it: "I didn't understand well what it
means... is not simple to understand."

**The test:** imagine handing the deck to someone who has never thought about this niche for five seconds
and asking them to say the core idea back in one plain sentence, using only slides 1 through 3. If they'd
need to infer an unstated pattern, or the sentence requires a technical term the brief never explains,
the deck fails the gate — even if every individual line is well-written. Run this mentally on every brief
before it ships, the same way you'd run the promise test or the binary test below.

**Two specific failure modes to actively hunt for:**
- **Unexplained jargon carrying the whole payoff.** If a slide's entire point depends on the reader
  already knowing a specific technical term (a chemical name, an acronym, an industry metric), either
  translate it into a plain-language consequence in the same breath, or drop the jargon and state the
  underlying mechanism directly instead. Specificity is good; specificity that requires prior expertise
  to parse is a comprehension tax, not a strength. ("Explains what's actually in the bottle, and why" beats
  "explains the difference between glycinate and oxide" — same underlying fact, no chemistry degree needed.)
- **Parallel structures that aren't actually parallel.** When a carousel sets up a contrast (claim vs.
  explanation, before vs. after, the mistake vs. the fix), every kicker/label naming each side of that
  contrast must visually and verbally mirror the other. "The claim" next to "The explanation" reads as one
  system instantly; "The claim" next to "The other ad" makes the reader do the matching work themselves.
  If one side of a batch's contrast has a sharper label than the other, rename the weaker one before
  shipping.

Run this gate after the 7 parameters below, not instead of them — clean, jargon-free prose that still
fails the 7 parameters needs the editorial pass too, and copy that aces the 7 parameters but fails this
gate still isn't ready. Both bars have to clear.

## Structural rules
- **Max 2 text blocks per slide, never 3.** Block 1 sets context; block 2 deepens or contradicts it.
- **Never end a slide on a fully closed statement.** Always leave something open that pulls the reader
  into the next slide — the next slide should feel inevitable, not announced.
- **The last body slide before the CTA (the "takeaway") must pivot, not summarize.** If it just recaps
  what came before, rewrite it as a genuine final turn on the idea. A summary reads like a lecture
  ending; a pivot reads like an idea landing.
- **The CTA is directive, not grateful.** "Save this. Send it to..." Never "hope you enjoyed this" /
  "thanks for reading" / "don't forget to follow."
- Every slide from 2 onward opens directly on the fact, tension, or number — never on throat-clearing
  ("today we're going to talk about...", "here's something you probably already know...").

## The 7 parameters (score every block 1 to 10; anything below 8 fails the whole block)

1. **Grammar** — clean, no fragments, correct agreement, every noun keeps its article.
   Penalty: a dropped article caps the score at 7/10 even if everything else is perfect.
2. **Flow** — reads like a reported paragraph aloud, not a truncated list.
   ❌ Choppy: *"Sales is execution. Performance matters. Results define careers. Best rep wins."*
   ✅ Flowing: *"Sales is individual execution, because performance face to face is what counts when the
   result has to show up, and the best rep wins on raw talent applied with consistency."*
   Penalty: a choppy block with no connectives caps the score at 5/10.
3. **Zero AI slop** — no banned binary constructions, no AI clichés, no corporate jargon (see the lists
   below).
   ❌ *"Engagement comes from emotional identification, not expertise."*
   ✅ *"Engagement happens when the reader sees themselves in the subject, and that recognition lands
   long before any expertise enters the picture."*
   Penalty: one binary structure caps the score at 6/10; one banned cliché caps it at 5/10.
4. **Verified facts** — every number, stat, date, or quote is confirmed via web search before it ships.
   Always verify: follower/user counts, survey percentages (and where that percentage actually comes
   from), revenue or valuation figures, attributed quotes. Penalty: an unverified material claim caps
   the score at 6/10.
5. **Structure** — the hook's promise gets paid off before the CTA; the anatomy holds (hook → mechanism
   → proof → expansion → application → direction). The most common failure is a broken promise: if the
   hook says "three decisions," the deck needs three decisions. Fix it by either expanding the deck to
   deliver what was promised, or loosening the hook's specific language to match what the deck actually
   delivers.
6. **Density** — strip the articles, connectives, and adjectives; what's left should still be substance.
   ❌ Generic: *"Companies are adopting new approaches to improve results."*
   ✅ Dense: *"Strava has 120 million users and 40 million activities a week because leaderboard
   gamification cuts churn by half."*
   Any block that would work unchanged with a different subject swapped in fails this parameter.
7. **Editorial tone** — prefer two short sentences over one long comma-joined one; no meta-language
   ("this carousel shows..."), no second-person advice-voice in the decode. *Exception: the closing
   save + share line is deliberately a direct imperative and stays that way.*
   ❌ *"Neymar launches a brand while sidelined, and the brand is born as a category built from the
   accessory the public already recognizes."*
   ✅ *"Neymar launches the brand while he's sidelined. It's born as a clear extension of the
   personality the public already recognizes."*

## Banned constructions (reject on sight, rewrite — never just delete)

| Banned | Why | Do instead |
|---|---|---|
| "It's not X, it's Y" | Worn-out binary, reads as formulaic | Show the difference without naming the formula |
| "And that changes everything" | Empty hyperbole, proves nothing | State specifically what changes and how |
| "At the end of the day" | Generic close, adds nothing | Cut it, or rewrite the idea without a closing tag |
| "Here's the thing:" / "The question is:" / "The point is:" | Weak announcement instead of just making the point | Make the point; cut the announcement |
| "In a world where..." / "We live in an era of..." | Essay-opening cliché | Start on the fact |
| "You need to..." / "You should..." | Second-person advice voice in the decode | Rewrite as reportage, describing rather than prescribing |
| "Simply" / "Basically" / "Just" | Hedges that add nothing | Cut |
| Forced parallelism: "X shrinks while Y grows", "Less X, more Y", "Before: X. Now: Y." | Formulaic contrast dressed as insight | Write the real contrast in prose with a natural connector |

**Banned headline/hook constructions** (in addition to the rejection checklist in `headline-engine.md`):
"the rise of X", "the impact of X", "why X is changing everything", "X: what you need to know",
"everything you need to know about X", "the ultimate guide to X", "X changed forever", "turned into" as
the main verb, and "discover / find out / learn" as an opening move.

**Banned slide openings:** "Today we'll cover...", "In this carousel you'll learn...", "Before we
start...", "As you probably know...", "Everyone's heard of..."

**Banned slide and CTA closings:** "Swipe to see more →", "But there's more...", "Hope you enjoyed
this!", "If you have questions, DM me", "Thanks for following along", "Don't forget to follow."

**Banned vague-data phrases — always replace with number + source + year:** "Studies show...",
"Experts say...", "Many companies...", "Most people...", "Recently...". If you can't attach a real
number, a named source, and a year, it isn't a fact yet — it's an opinion, so don't state it as one.

## Jargon substitution
Use the plain word unless the jargon IS the niche's real, expected vocabulary.

| Jargon | Use instead |
|---|---|
| Ecosystem | system, market, landscape |
| Synergy | integration, working together |
| Disruptive | breaks the pattern, changes the game |
| Stakeholders | the people involved |
| Mindset | mentality, way of thinking |
| Engagement (as a vague good-outcome word) | result, reach, performance |
| Curation (generic) | selection, deliberate choice |
| Storytelling | narrative, story |
| Overview | picture, summary |
| Benchmark (as a verb) | compare against, measure against |

Exception: if the jargon is genuinely how the niche talks (e.g. "CAC" in performance marketing), keep
it and gloss it on first use.

## Grammar and flow, quick version
- Every noun keeps its article ("a system," not "system") — dropped articles are the single most common
  AI tell in this style of copy.
- Every block needs at least one natural connective (because, but, so, while, even though, still) — a
  string of short flat declaratives back to back reads as a disguised list, not a paragraph.
- Read every block aloud. If it sounds truncated, translated, or like a bullet list wearing a sentence's
  clothes, rewrite it as a real paragraph.

## The AI-tone test (5 questions — any "yes" means rewrite)
1. Could any account with 10k+ followers have posted this exact line?
2. Would it still work if you swapped the subject for something unrelated?
3. Does any phrase sound like a generic essay conclusion?
4. Is there a word a sharp business journalist would never actually use?
5. Does the block motivate without stating anything concrete?

## The 6 final tests before shipping any brief
1. **Native-voice test** — does the EN read like it was written in English, the ES like it was
   written in Spanish, and the PT like it was written in Brazilian Portuguese (none of the three a
   mirror translation of the others)?
2. **Substitution test** — swap in an unrelated subject; if the line still works, it's generic.
3. **Promise test** — is every claim the hook makes paid off somewhere in the deck?
4. **Article test** — does every noun have its article?
5. **Binary test** — did you actively hunt for "it's not X, it's Y" and its relatives?
6. **Clarity test** — could a first-time reader restate the core idea in one plain sentence using only
   slides 1 to 3, with no unexplained jargon and no unstated pattern left to infer? (see the clarity gate
   above for the two specific failure modes to check)

## Review process (run in order)
1. Read the whole deck aloud. Mark anywhere it snags, sounds robotic, or reads like a translation.
2. Fact-check every number, date, and quote before touching anything else.
3. Scan actively for the banned constructions above.
4. Score the copy against the 7 parameters.
5. Run the clarity gate: state the core idea in one plain sentence using only slides 1 to 3. If you can't
   do it without inferring or already knowing a technical term, fix the jargon or the kicker parallelism
   before moving on.
6. Decide: fix or rewrite? If stripping filler still leaves real substance, edit it. If stripping filler
   leaves nothing, start that block over from scratch.
7. Rewrite anything that failed, then re-run this whole checklist on the rewritten blocks.
8. Only then hand off to `docx-output.md`.

## One-line summary
Write like a journalist. Think like an editor. Verify like a fact-checker.
