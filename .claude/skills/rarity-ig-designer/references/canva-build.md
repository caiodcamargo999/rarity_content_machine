# Canva Build Recipe (default connector)

Build Rarity IG art in Canva by default. Combine with `rarity-brand-system.md` (colors, fonts, logo,
symbol) and `viral-layouts.md` (layout, safe zones). Pull the hero image FROM THE BRIEF.

## Tools
Load via ToolSearch: `generate-design`, `create-design-from-brand-template`, `autofill-design`,
`list-brand-kits`, `search-brand-templates`, `copy-design`, `start-editing-transaction`,
`perform-editing-operations`, `commit-editing-transaction`, `get-design-thumbnail`, `get-assets`.

## Step 1 — create the design
Pick the most controllable path available:
- **Rarity brand template (best):** if a Rarity Canva brand template exists, `search-brand-templates`
  then `create-design-from-brand-template` (Instagram post, 1080x1350). Fill fields with the brief copy
  via `autofill-design` if the template has fields.
- **Brand-kit generate (good):** `list-brand-kits` → pick Rarity's → `generate-design` with design_type
  `instagram_post` and a DETAILED query (the headline text, deep-navy or gradient background, yellow pop
  headline, teal accent, symbol top-right). It returns candidates; pick one and create the design from it.
- **Carousel** = multiple `instagram_post` pages: build the hook first, then body slides, then the CTA.
  `copy-design` a strong page and edit each to move fast.

## Step 2 — pull the hero image FROM THE BRIEF (required)
- Take the brief's IMAGES direct URL (e.g. the Wikimedia `Special:FilePath` link).
- Bring it into Canva and place it as the slide-1 background. Use the connector's asset import: if a Canva
  asset-upload tool accepts a URL, pass the brief's direct URL; otherwise upload the image file. Then
  either pass its `asset_id` to `generate-design` (`asset_ids`) or set it as the background by replacing
  media inside a `start-editing-transaction` → `perform-editing-operations` → `commit`.
- VERIFY at runtime which asset-import tool the Canva connector exposes and use it. The requirement is
  fixed (the brief's image must appear in the design); the exact tool may change.
- Last resort only: if import genuinely fails, use a brand-gradient background and tell Caio to drop the
  photo in with the direct URL. Do not make this the default.

## Step 3 — apply the brand + copy (editing transaction)
`start-editing-transaction` (design_id) → `perform-editing-operations`:
- Set the headline to the brief's EN headline, uppercase, in the pop color (off-brand allowed, e.g.
  `#FFE400`). Set the eyebrow, body lines, CTA, and `@rarity.agency` per the brief.
- Apply Rarity colors (navy background, teal accents). Place the **symbol** top-right (import
  `assets/rarity-symbol.png`); use the full white logo on the CTA slide.
- Keep ONLY the headline on the hero photo.
Then `commit-editing-transaction`. Preview with `get-design-thumbnail` and show it in chat.

## Step 4 — EN, then ES, then PT
Finish the English set, then `copy-design` and translate the copy to the brief's Spanish lines in another
editing transaction. Then `copy-design` again and translate the copy to the brief's Brazilian Portuguese
lines in a third editing transaction. Keep the layout identical across all three so the three language
sets are visual twins — same fonts, same brand colors, same layout, only the copy language changes.

## Fonts
Canva may not have TESLA/BentonSans. Use the brand kit's fonts, or Canva's closest heavy display + clean
grotesque, and flag that installing TESLA + BentonSans in Canva makes it brand-exact.

## Deliver
Give the Canva edit link plus a thumbnail of each page. Flag image rights and any font fallback.
