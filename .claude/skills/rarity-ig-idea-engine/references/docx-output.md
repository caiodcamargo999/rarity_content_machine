# DOCX Output — render the brief as a Word document

The brief is delivered as a Word (.docx) file, not markdown. Use the `docx` skill (docx-js) through the
bundled builder so every run is consistent.

## Steps
1. Compose the full brief content (every section from `brief-template.md`), EN + ES + PT, following all
   copy rules: no hyphens or dashes, max 3 hashtags, headline is a hook with a pop color.
2. Write the content as a JSON file matching the schema documented at the top of
   `scripts/build_brief_docx.js`.
3. Ensure docx-js is available once per environment: `npm install -g docx`.
4. Build:
   `NODE_PATH=$(npm root -g) node <skill>/scripts/build_brief_docx.js <brief.json> "<out>/Idea N - Name.docx"`
5. Validate: `python3 <docx-skill>/scripts/office/validate.py "<out>/Idea N - Name.docx"`. If it fails,
   unpack, fix the XML, repack (see the docx skill).
6. Save to `public/Instagram Briefings/Ideas <Month>/Idea N - <Name>.docx`, delete the temp JSON, and present
   the .docx in chat.

## What the document contains
- Rarity logo at the top (use the navy logo on the white page:
  `Branding Rarity/logo_rarity_azul_sem_fundo_zoom_in.png`).
- Title with a teal rule, and a meta line (date · pillar · format).
- The Anchor (with clickable source links), the Big Idea, the Audience Takeaway.
- The Headline EN/ES/PT, eyebrow, and the pop color (off-brand allowed).
- A Carousel Slides table (when it is a carousel), then Caption (EN), Caption (ES), and Caption (PT).
- Images: the hero photo as a clickable link with source, author, and license. If a LOCAL image file is
  available (Caio provided one, or already downloaded into the design folder by Step 2), pass its path
  as `localPath` in the JSON and it is embedded inline.
- Visual Direction and a Rights / Sensitivity note.

## Image note (important)
The brief itself does not embed a binary copy of the hero photo, so it goes in the document as its
verified direct URL (clickable) plus full credit. Step 2 (`rarity-ig-designer`) downloads the real file
itself, automatically, straight from that URL — no design connector, no manual step. Embed an actual
picture in the .docx only when a real local file already exists on disk (via `localPath`).

## Keep it clean
A professional working document: Arial, navy headings, US Letter. No dashes anywhere (periods, commas,
colons), matching the copy rules.
