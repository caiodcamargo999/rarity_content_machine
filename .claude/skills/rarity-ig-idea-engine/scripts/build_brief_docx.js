/*
 * build_brief_docx.js — turns a Content Idea Brief JSON into a branded Word (.docx).
 * Usage:  NODE_PATH=$(npm root -g) node build_brief_docx.js <brief.json> <out.docx>
 * Requires: npm install -g docx
 *
 * JSON shape (all fields optional except headline/title):
 * {
 *   "title","date","pillar","format","recommended",
 *   "logoPath": "abs path to rarity-logo-blue.png (navy logo for white page)",
 *   "anchor": { "subject","fact","timePeg","sources":["url", ...] },
 *   "bigIdea","takeaway",
 *   "headline": { "en","es","pt","eyebrow_en","eyebrow_es","eyebrow_pt","color" },
 *   "slides": [ { "n":1,"en":"","es":"","pt":"","bigWord":"" }, ... ],   // omit/empty for static
 *   "captionEN": ["para", ...], "captionES": ["para", ...], "captionPT": ["para", ...],
 *   "images": [ { "desc","url","source","author","license","localPath","type":"jpg|png","height":240 } ],
 *   "visual": { "hero","altQueries":[],"colorMood","symbolCorner","logo" },
 *   "rights"
 * }
 */
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, HeadingLevel, BorderStyle, WidthType, ShadingType, ExternalHyperlink
} = require('docx');

const [, , jsonPath, outPath] = process.argv;
if (!jsonPath || !outPath) { console.error('Usage: node build_brief_docx.js <brief.json> <out.docx>'); process.exit(1); }
const b = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));

const NAVY = '001A70', TEAL = '0FC1AF', INK = '1A1A1A', MUT = '6B7280';

const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const P  = (t, o = {}) => new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: t || '', ...o })] });
const label = (l, v) => new Paragraph({ spacing: { after: 60 }, children: [
  new TextRun({ text: l + '  ', bold: true, color: NAVY }), new TextRun({ text: v || '' })] });

function cell(text, w, header = false) {
  const lines = Array.isArray(text) ? text : String(text).split('\n');
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    shading: header ? { fill: 'E6E9F5', type: ShadingType.CLEAR } : undefined,
    children: lines.map((l) => new Paragraph({ children: [new TextRun({ text: l, bold: header, color: header ? NAVY : INK })] })),
  });
}

const children = [];

// Brand logo (navy logo on white page)
if (b.logoPath && fs.existsSync(b.logoPath)) {
  children.push(new Paragraph({ spacing: { after: 80 }, children: [new ImageRun({
    type: 'png', data: fs.readFileSync(b.logoPath), transformation: { width: 150, height: 62 },
    altText: { title: 'Rarity', description: 'Rarity Agency logo', name: 'logo' } })] }));
}

// Title + teal rule
children.push(new Paragraph({
  spacing: { after: 40 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: TEAL, space: 6 } },
  children: [new TextRun({ text: b.title || 'Rarity IG Content Idea Brief', bold: true, size: 36, color: NAVY })] }));
children.push(new Paragraph({ spacing: { after: 160 },
  children: [new TextRun({ text: [b.date, b.pillar, b.format].filter(Boolean).join('   ·   '), color: MUT })] }));
if (b.recommended) children.push(P('Recommended: ' + b.recommended, { italics: true, color: MUT }));

// Anchor
children.push(H2('The Anchor'));
if (b.anchor) {
  if (b.anchor.subject) children.push(label('Subject:', b.anchor.subject));
  if (b.anchor.fact) children.push(label('Real fact:', b.anchor.fact));
  if (b.anchor.timePeg) children.push(label('Time peg:', b.anchor.timePeg));
  (b.anchor.sources || []).forEach((u, i) => children.push(new Paragraph({ spacing: { after: 40 }, children: [
    new TextRun({ text: `Source ${i + 1}: `, bold: true, color: NAVY }),
    new ExternalHyperlink({ link: u, children: [new TextRun({ text: u, style: 'Hyperlink' })] })] })));
}

// Big idea + takeaway
children.push(H2('The Big Idea')); children.push(P(b.bigIdea));
children.push(H2('Audience Takeaway')); children.push(P(b.takeaway));

// Headline
children.push(H2('Headline (the only text on the hero image)'));
if (b.headline) {
  if (b.headline.en) children.push(label('EN:', b.headline.en));
  if (b.headline.es) children.push(label('ES:', b.headline.es));
  if (b.headline.pt) children.push(label('PT:', b.headline.pt));
  if (b.headline.eyebrow_en) children.push(label('Eyebrow:', [b.headline.eyebrow_en, b.headline.eyebrow_es, b.headline.eyebrow_pt].filter(Boolean).join('  |  ')));
  if (b.headline.color) children.push(label('Headline color:', b.headline.color + '  (off-brand allowed; chosen to stop the scroll)'));
}

// Carousel slides
if (b.slides && b.slides.length) {
  children.push(H2('Carousel Slides'));
  const rows = [new TableRow({ tableHeader: true, children: [cell('Slide', 900, true), cell('EN', 2820, true), cell('ES', 2820, true), cell('PT', 2820, true)] })];
  b.slides.forEach((s) => {
    const left = s.bigWord ? [String(s.n), '[' + s.bigWord + ']'] : [String(s.n)];
    rows.push(new TableRow({ children: [cell(left, 900), cell(s.en || '', 2820), cell(s.es || '', 2820), cell(s.pt || '', 2820)] }));
  });
  children.push(new Table({ width: { size: 9360, type: WidthType.DXA }, columnWidths: [900, 2820, 2820, 2820], rows }));
}

// Captions
children.push(H2('Caption (EN)')); (b.captionEN || []).forEach((p) => children.push(P(p)));
children.push(H2('Caption (ES)')); (b.captionES || []).forEach((p) => children.push(P(p)));
children.push(H2('Caption (PT)')); (b.captionPT || []).forEach((p) => children.push(P(p)));

// Images
children.push(H2('Images (sourced from the web)'));
(b.images || []).forEach((img) => {
  if (img.localPath && fs.existsSync(img.localPath)) {
    children.push(new Paragraph({ spacing: { after: 60 }, children: [new ImageRun({
      type: img.type || 'jpg', data: fs.readFileSync(img.localPath),
      transformation: { width: 360, height: img.height || 240 },
      altText: { title: img.desc || 'image', description: img.desc || 'image', name: 'img' } })] }));
  }
  if (img.url) children.push(new Paragraph({ spacing: { after: 20 }, children: [
    new TextRun({ text: (img.desc || 'Hero') + ': ', bold: true, color: NAVY }),
    new ExternalHyperlink({ link: img.url, children: [new TextRun({ text: img.url, style: 'Hyperlink' })] })] }));
  const meta = [img.source && ('Source: ' + img.source), img.author && ('Author: ' + img.author), img.license && ('License: ' + img.license)].filter(Boolean).join('    ');
  if (meta) children.push(P(meta, { color: MUT, size: 18 }));
});

// Visual direction
children.push(H2('Visual Direction (for the design step)'));
if (b.visual) {
  if (b.visual.hero) children.push(label('Hero image:', b.visual.hero));
  if (b.visual.altQueries) children.push(label('Alt image queries:', b.visual.altQueries.join('   |   ')));
  if (b.visual.colorMood) children.push(label('Color mood:', b.visual.colorMood));
  if (b.visual.symbolCorner) children.push(label('Symbol corner:', b.visual.symbolCorner));
  if (b.visual.logo) children.push(label('Logo (CTA slide):', b.visual.logo));
}

// Rights
children.push(H2('Rights / Sensitivity')); children.push(P(b.rights));
children.push(new Paragraph({ spacing: { before: 200 }, children: [new TextRun({
  text: 'Next step: run rarity-ig-designer on this brief to build the EN, ES, and PT art with rarity-ig-designer.',
  italics: true, color: MUT })] }));

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 26, bold: true, font: 'Arial', color: NAVY }, paragraph: { spacing: { before: 220, after: 80 }, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(outPath, buf); console.log('Wrote ' + outPath); });
