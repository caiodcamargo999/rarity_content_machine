# Image QA — the quality gate for every picture in a brief

`editorial-qa.md` scores the copy. This file scores the pictures. Until this existed, every block of
text was audited against seven parameters while the imagery was chosen on feel — which is why briefs
kept coming back with photos that were technically on-theme and visually dead.

Run this on **every image, on every slide**, after `image-sourcing.md` has produced the candidates and
before the brief is locked. An image with no scorecard in the brief is not approved.

## The mentality

Pick like a photo editor at a serious magazine, not like someone filling a placeholder. The bar is not
"is this related to the topic." The bar is "would a picture desk have run this frame with this story."
That second bar rejects almost everything a stock search returns first.

---

## Gate 0 — the hard binaries (any FAIL kills the image immediately)

No scoring, no averaging, no "but the rest is strong." These are pass or fail.

| # | Binary check | FAIL means |
|---|---|---|
| B1 | **You have actually viewed the frame** and can describe what is literally in it in one sentence | Chosen from a filename, alt text, or a search caption |
| B2 | **Short side is at least 1600px** | A thumbnail, a preview, or a soft upscale |
| B3 | **The direct URL resolves to the file** (verified through Chrome, not bash) | A search page, a `pinimg.com` link, a cached thumbnail, a dead link |
| B4 | **Not on the banned-trope list** in `image-sourcing.md` | Handshake, laptop-on-desk, robot arm as "AI", chess pieces as "strategy", etc. |
| B5 | **Not reused on more than 2 slides**, and where reused, visibly different crops | The carousel reads as one photo re-tinted |
| B6 | **Licence and credit recorded from the traced original source page** | Rights taken from a search listing, or left blank |

If B1 fails, stop. Everything downstream of "I never actually looked at it" is guesswork.

---

## The 6 parameters (score every image 1 to 10; anything below 8 fails the image)

### 1. Subject match
Does the frame show the actual thing this slide is about — the named company, product, interface,
person, event — or something literally from its world?

- **10** — unmistakably this story; could illustrate no other post.
- **8** — clearly from the subject's own world, even if not the exact moment.
- **5** — same industry, generic instance.
- **2** — a cross-domain metaphor standing in for a real, photographable subject.

Score 5 or below is an automatic rewrite of the search, not a negotiation. The only exception is a
slide whose claim is genuinely abstract with no real subject to photograph — declare that explicitly
in the scorecard, and the parameter is then judged on metaphor precision instead.

### 2. The five-unrelated-posts test
Could this exact photo illustrate five other, completely unrelated posts without looking out of place?

**Write out the answer.** Name two of the five if the answer is yes. If you can name two, the image is
interchangeable stock and scores 4 or below.

- **10** — it would look absurd on any other post.
- **8** — it would only fit posts about this same subject.
- **4** — you can name two unrelated posts it would suit.
- **1** — you could drop it into anything.

### 3. Charge
Is there emotion, tension, or drama in the frame?

Look for: a face mid-emotion, direct eye contact, raking or violent light, an extreme close-up, an
absurd juxtaposition, a scale contrast, a provocative or polarising composition.

- **10** — stops a scroll before the headline is read.
- **8** — genuinely arresting; a real moment, not a performed one.
- **5** — competent, calm, unmemorable.
- **2** — posed, corporate, or a paid model performing an emotion.

The scream, not the headshot. The storm over the building, not the facade.

### 4. Currency
Does it feel contemporary and high-resolution?

- **10** — recent, sharp, current visual language.
- **8** — timeless and sharp; or, for a historical anchor, the best surviving frame in colour or
  high-resolution black and white.
- **5** — visibly dated in a way the post does not intend.
- **2** — low-resolution, grainy, or an over-used archive image everyone has seen.

A historical anchor lowers the "recent" requirement. It never lowers the resolution or striking-frame
requirement.

### 5. Legibility
Can it carry the type?

- Clear negative space where the bottom-anchored serif headline sits.
- **The eyebrow/kicker zone above the headline is also clear** — no face, logo, or busy detail landing
  exactly where the eyebrow goes.
- Enough tonal range to hold contrast under the navy scrim or duotone.
- Focal point survives a ~80px safe crop on 1080x1350.

- **10** — both zones clean, strong tonal range.
- **8** — usable with a standard scrim.
- **5** — one zone is compromised; the design step will have to fight it.
- **2** — no room for type anywhere.

Never trade parameter 1 away to raise this one. A generic-but-legible photo is still the wrong photo.

### 6. Set distinction
Judged across the whole carousel, not per image. Do the slides look like a curated set of different
photographs, or one look repeated?

- **10** — every slide visually distinct; the set has range.
- **8** — distinct subjects, coherent grade.
- **5** — two or three slides blur together.
- **2** — it reads as one photo re-tinted.

---

## The rejection loop

Below 8 on any parameter, or any Gate 0 fail:

1. **Name the failure** in one line — which parameter, and why.
2. **Change the search, not the standard.** Sharpen the subject term, add an emotion or an era, move up
   the source ladder (subject's own newsroom → Google News → Commons → Pinterest as a lead).
3. **Re-gather candidates** and score again.
4. **Maximum three loops per slide.** If three rounds cannot clear the bar, the slide's claim is
   probably too vague to photograph — go back and sharpen the claim so it has a real subject, rather
   than accepting a weak image for a weak line.

Never resolve a failure by lowering the bar, and never resolve a rights problem by substituting a
generic free photo. Flag the brief `INTERNAL MOCKUP ONLY` instead and say what a cleared substitute
would be.

---

## What goes in the brief

One scorecard row per slide, in the IMAGES table or immediately under it:

```
Slide 3 — Meta Ads Manager interface, Advantage+ panel open, screen glow on an empty room
Gate 0: B1 viewed · B2 2400x1600 · B3 verified · B4 clean · B5 unique · B6 Meta newsroom, press use
Scores: subject 9 · five-posts 9 ("would look absurd on anything else") · charge 8 · currency 10 ·
legibility 9 (clean lower third, eyebrow zone dark) · set distinction 9
Beat runner-up: the keynote stage wide shot — same subject, but the interface is the actual claim
```

Keep it this terse. The point is that the judgement is written down and checkable, not that it is long.

---

## Batch rule

When a brief ships several ideas at once, also check the imagery **across** ideas: three carousels that
all open on a stadium crowd, or all lean on the same colour grade, is a batch-level set-distinction
failure even when each idea passes on its own. Vary subject type, palette, and framing across the batch
the same way pillars are rotated.
