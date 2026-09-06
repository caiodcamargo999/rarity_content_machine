# Figma Build Recipe (environment-correct)

How to actually construct the post in Figma with the connector. **Load the `figma-use` skill first** —
it owns the API rules; this file is the Rarity-specific recipe on top of it. Work incrementally
(≤10 ops per `use_figma` call), `return` node IDs every call, and screenshot to verify.

> Colors are 0–1 in the API. Quick conversions used below:
> navy `#001A70` → `{r:0, g:0.102, b:0.439}` · teal `#0fc1af` → `{r:0.059, g:0.757, b:0.686}` ·
> off-white `#efeeea` → `{r:0.937, g:0.933, b:0.917}` · white `{r:1,g:1,b:1}` ·
> blue `#0046FF` → `{r:0, g:0.275, b:1}` · purple `#9B00C8` → `{r:0.608, g:0, b:0.784}` ·
> magenta `#D50057` → `{r:0.835, g:0, b:0.341}` · dark-purple `#0f0a1a` → `{r:0.059, g:0.039, b:0.102}`.

## Step 0 — create the file
Load `figma-create-new-file`, then `create_new_file` (editorType `figma`/design) named
`Rarity IG — <slug> — <YYYY-MM-DD>`. Confirm it's a design file (`figma.com/design/...`). Or build in a
file Caio links.

## Step 1 — fonts (load once, with fallback)
Brand fonts: **TESLA** (headlines), **BentonSans** (body). They ship in this skill's `assets/`. Figma
only sees fonts installed on the machine / in the org, so check availability and fall back gracefully.

```js
// read-only check
const fonts = await figma.listAvailableFontsAsync();
const fams = new Set(fonts.map(f => f.fontName.family));
return {
  hasTesla: fams.has('TESLA'),
  hasBenton: [...fams].filter(f => f.toLowerCase().includes('benton')),
};
```
- If **TESLA** present → headline font `{family:'TESLA', style:'Regular'}`.
  Else fallback (first available): `Anton`, `Archivo Black`, `Oswald`, `Bebas Neue` (all bold display).
- If **BentonSans** present → body `{family:'BentonSans', style:'Regular'}` / eyebrow `'Thin'`.
  Else fallback: `Inter` (`Regular`/`Light`), then `Helvetica Neue`, `Arial`.
- **Always `await figma.loadFontAsync(<fontName>)` before setting `characters` or `fontName`.** If you
  fell back, add a flag to the final summary telling Caio to install TESLA + BentonSans in Figma (the
  `.ttf`/`.otf` are in `assets/` and in his "Branding Rarity" folder) for brand-accurate output.

## Step 2 — the hook frame (image + scrim + headline)
Create the 1080×1350 frame, fill with the photo, add the gradient scrim, then the headline.

```js
// 2a. frame + hero image by URL
const f = figma.createFrame();
f.name = 'EN / 1 Hook';
f.resize(1080, 1350);
f.x = 200; f.y = 200;                 // keep off (0,0)
const img = await figma.createImageAsync('<HERO_IMAGE_URL>');   // loads inside Figma
f.fills = [{ type:'IMAGE', imageHash: img.hash, scaleMode:'FILL' }];
return { frameId: f.id };
```
```js
// 2b. gradient scrim (navy transparent at top → opaque at bottom) for legibility
const f = await figma.getNodeByIdAsync('<frameId>');
const scrim = figma.createRectangle();
scrim.resize(1080, 1350);
scrim.x = f.x; scrim.y = f.y;
scrim.fills = [{
  type:'GRADIENT_LINEAR',
  gradientTransform: [[0, 1, 0], [-1, 0, 1]],     // vertical; flip stops if the opaque end is wrong
  gradientStops: [
    { position:0.0, color:{ r:0, g:0.102, b:0.439, a:0 } },     // top: clear navy
    { position:0.55, color:{ r:0, g:0.102, b:0.439, a:0.35 } },
    { position:1.0, color:{ r:0, g:0.102, b:0.439, a:0.95 } },  // bottom: solid navy
  ],
}];
f.appendChild(scrim);
return { scrimId: scrim.id };
```
```js
// 2c. headline (TESLA, uppercase) + teal accent bar + handle
const f = await figma.getNodeByIdAsync('<frameId>');
const HEAD = { family:'TESLA', style:'Regular' };      // or your fallback
const BODY = { family:'BentonSans', style:'Regular' };  // or 'Inter'
await figma.loadFontAsync(HEAD); await figma.loadFontAsync(BODY);

const bar = figma.createRectangle();          // teal accent bar
bar.resize(12, 150); bar.x = f.x + 80; bar.y = f.y + 1010;
bar.fills = [{ type:'SOLID', color:{ r:0.059, g:0.757, b:0.686 } }];
f.appendChild(bar);

const h = figma.createText();
h.fontName = HEAD; h.characters = 'STANDARDS BEAT TALENT';
h.fontSize = 120; h.lineHeight = { unit:'PERCENT', value:96 };
h.textCase = 'UPPER';
// Headline color = the brief's POP color, chosen to stop the scroll (may be OFF-brand, e.g.
// yellow {r:1,g:0.894,b:0} or red {r:1,g:0.231,b:0.231}). Default off-white #efeeea shown:
h.fills = [{ type:'SOLID', color:{ r:0.937, g:0.933, b:0.917 } }];
h.resize(880, h.height); h.x = f.x + 110; h.y = f.y + 1000;
f.appendChild(h);

const handle = figma.createText();
handle.fontName = BODY; handle.characters = '@rarity.agency';
handle.fontSize = 32; handle.fills = [{ type:'SOLID', color:{ r:0.655, g:0.675, b:0.796 } }];
handle.x = f.x + 80; handle.y = f.y + 1180;       // above bottom safe zone
f.appendChild(handle);
return { createdNodeIds:[bar.id, h.id, handle.id] };
```
Then `await f.screenshot()` (or `get_screenshot`) and check legibility; strengthen the scrim or resize
the headline if needed. Then stamp the corner symbol (Step 2.5).

## Step 2.5 — Rarity symbol in the corner (every image)
The brand marks are LOCAL PNGs in this skill's `assets/`: `rarity-symbol.png` (the corner stamp),
`rarity-logo-white.png` (full logo for dark bg), `rarity-logo-blue.png` (light bg). `createImageAsync`
needs a URL, so for these local files use the **`upload_assets` Figma MCP tool** to upload the file once
and get an `imageHash`. Upload the symbol ONCE and reuse that hash on every slide — don't re-upload.

```js
// after upload_assets returns the symbol's imageHash, stamp it top-right:
const f = await figma.getNodeByIdAsync('<frameId>');
const sym = figma.createRectangle();
sym.resize(96, 96);                       // square box; the art keeps its aspect via FIT
sym.x = f.x + 1080 - 96 - 70;             // top-right, ~70px margin
sym.y = f.y + 70;
sym.name = 'Rarity symbol';
sym.fills = [{ type:'IMAGE', imageHash:'<SYMBOL_HASH>', scaleMode:'FIT' }];
f.appendChild(sym);
return { symbolId: sym.id };
```
Use the SAME size and position on every hook + body slide so the set reads as one system — just the
symbol, nothing else. Skip it on the CTA slide (the full logo is there instead). The symbol has a white
body, so it reads on navy/dark; on a rare light background, skip it or use a tinted version. If
`upload_assets` is unavailable, fall back to a small TESLA `RARITY` wordmark and flag it.

## Step 3 — carousel body & CTA slides
For each body slide: a 1080×1350 frame with a solid navy fill (or a gradient for the Mindset pillar),
one big TESLA focal word/number (accent the key word teal), and one short BentonSans line. Use
`figma.createAutoLayout('VERTICAL', {...})` for the text stack so spacing stays clean (see figma-use
Rule 12). Stamp the corner symbol on each body slide (Step 2.5). CTA slide: the full white logo
(`rarity-logo-white.png` via `upload_assets`), the CTA line (accent last word), a teal CTA element,
`@rarity.agency` — no corner symbol here.

Gradient background (Mindset pillar) example fill:
```js
fills = [{ type:'GRADIENT_LINEAR', gradientTransform:[[1,0,0],[0,1,0]], gradientStops:[
  { position:0, color:{ r:0, g:0.275, b:1, a:1 } },      // #0046FF
  { position:0.5, color:{ r:0.608, g:0, b:0.784, a:1 } },// #9B00C8
  { position:1, color:{ r:0.835, g:0, b:0.341, a:1 } },  // #D50057
]}];
```
Lay slides left→right with ~120px gaps so the carousel reads as a strip. Keep ≤10 ops/call; build a few
slides, screenshot, continue.

## Step 4 — clone EN → ES → PT
1. Create/switch to an `ES` page (`await figma.setCurrentPageAsync(...)`; one switch per call).
2. Clone each EN frame (`const es = enFrame.clone()`), move to the ES page/positions.
3. **Before editing any text**, load that node's current fonts
   (`getStyledTextSegments(['fontName'])`) then set `.characters` to the Spanish line. Keep identical
   sizes/positions; if Spanish runs long, drop one size step or rebalance the line break — don't overflow.
4. Screenshot the ES set to confirm it's a visual twin of EN.
5. Repeat the same three steps for a `PT` page: clone each EN frame, load fonts before editing text, set
   `.characters` to the brief's Brazilian Portuguese line (PT, like ES, often runs long — drop a size
   step or rebalance rather than overflow), then screenshot the PT set to confirm it's a visual twin of
   EN and ES too.

## Step 5 — verify & deliver
- `get_screenshot` (or inline `node.screenshot()`) every frame, EN + ES + PT. Look for clipped text,
  overlap, weak contrast. Fix before declaring done.
- Give Caio the **Figma file URL**.
- Present preview images of the frames in chat so he can review without opening Figma. (Use the
  screenshots you captured; if an export-to-file tool is available, also drop PNGs into
  `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/`.)
- Summary + flags: image-rights reminder; font-fallback note if TESLA/BentonSans weren't installed.

## Gotchas (Rarity-specific)
- Load fonts before text — every time. Brand fonts aren't preloaded.
- Reassign fills as new arrays; don't mutate in place. Colors 0–1. Paint color has no `a` for SOLID
  (put opacity at paint level); gradient *stops* do take `a`.
- Position top-level frames away from (0,0). Return node IDs from every call.
- If `createImageAsync(url)` fails (hotlink blocked), download the image to the working folder and use
  the `upload_assets` Figma tool, then fill with the returned hash.
