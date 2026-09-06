---
name: rarity-ig-publish
description: "Publishes a finished Rarity Instagram post (photo or carousel) LIVE to @rarity.agency via the Instagram Graph API. STEP 4 of the Rarity IG pipeline, consuming the rendered art from rarity-ig-designer and the caption from rarity-ig-captions. Hosts the compressed slides on the project's own GitHub repo (raw.githubusercontent.com) since the Graph API only accepts a public image_url, never a direct upload. Runs in two explicit stages, prepare then publish, so nothing goes live by accident. Does NOT support Reels/video — the Graph API can't attach Instagram's licensed music library to a Reel, only the app can. ALWAYS use when Caio asks to publish a post, post isso no Instagram, sobe esse post, agenda esse post, publica agora, or go live with a finished carousel/caption. When in doubt, USE this skill rather than improvising curl/Graph API calls from scratch."
---

# Rarity IG — Publish (Step 4 of 4)

This skill takes what Step 2 (`rarity-ig-designer`) rendered and what Step 3
(`rarity-ig-captions`) wrote, and puts the finished post live on Instagram. It does not
generate ideas, art, or copy — by the time this skill runs, all of that already exists on
disk under `public/Instagram Briefings/Designs <Month>/<Idea N - Name>/`.

**This is the one step in the pipeline with a real-world, irreversible, public side effect.**
Every other skill only writes files. This one posts to the actual @rarity.agency account.
Treat the final `publish` call with the same care as a `git push --force` — confirm with Caio
before running it, every time, even if `prepare` already ran cleanly.

## How it works

The script is `scripts/publish_post.py`, split into three subcommands:

1. **`prepare`** — does everything except go live:
   - Finds the slide images in `<idea-dir>/<LANG>/`, compresses them to JPEG.
   - Commits them into this project's own GitHub repo under `ig-assets/<slug>/<lang>/` and
     pushes. This is the image-hosting workaround: the Instagram Graph API's Content
     Publishing endpoint only accepts a public `image_url`, never a direct file upload, so
     `raw.githubusercontent.com` is the public URL Meta's crawler fetches from.
   - Creates the Instagram media container (a single photo container if there's one slide,
     or item containers + a parent carousel container if there are several) and attaches the
     caption.
   - Polls until Meta reports `status_code: FINISHED`.
   - Saves a small state file to `.publish_state/<slug>-<lang>.json` holding the
     `creation_id`, and prints the exact `publish` command to run next. **Stops here.**
2. **`publish`** — the only command that goes live. Takes the state file, calls
   `media_publish`, and prints the resulting permalink. Confirm with Caio before running this.
3. **`status`** — re-checks the container's `status_code` without publishing anything. Useful
   if `prepare` was run a while ago and you want to confirm the container hasn't expired
   (Instagram containers expire ~24h after creation if never published).

## Workflow

1. Confirm the art and caption both exist and are final — `<idea-dir>/<LANG>/slide-*.png` and
   the `Caption - <Name>.md` from `rarity-ig-captions` (or a plain-text caption file).
2. Ask Caio which language(s) to publish and confirm the exact intent (post now vs. a
   specific future date/time — see "Scheduling" below, this skill only handles "now").
3. Run `prepare`:
   ```
   python3 .claude/skills/rarity-ig-publish/scripts/publish_post.py prepare \
     --idea-dir "public/Instagram Briefings/Designs August 2026/Idea N - Name" \
     --lang EN \
     --caption-md "public/Instagram Briefings/Designs August 2026/Idea N - Name/Caption - Name.md"
   ```
   (Use `--caption-file <path>` instead of `--caption-md` if the caption is plain text, not
   the three-language markdown file.)
4. Read the printed status. If it stops with an error (missing `.env` key, unreachable image
   URL, Graph API error), fix the underlying issue — see `references/publish-mechanics.md` —
   and re-run `prepare` (it's safe to re-run; it just re-pushes and re-creates a container).
5. **Before running `publish`, show Caio the permalink-to-be context (which post, which
   language, which account) and get an explicit go-ahead.** This is a hard rule, not a
   suggestion — see the "irreversible" note above.
6. Run `publish` with the state file path `prepare` printed. Report the returned permalink
   back to Caio.

## Credentials

Read from `<repo root>/.env`, already set up for @rarity.agency:
- `IG_ACCESS_TOKEN`, `IG_USER_ID` — Instagram Graph API (Instagram API with Instagram Login,
  from the "Rarity Content Machine" app on developers.facebook.com). This token expires
  periodically; if the script errors with an auth failure, the fix is generating a fresh one
  from the app dashboard's "API setup with Instagram login" screen and updating `.env` — see
  `references/publish-mechanics.md` for the exact path.
- `GITHUB_TOKEN`, `GITHUB_REPO` — for pushing assets to `caiodcamargo999/rarity_content_machine`
  (the same repo this project lives in).

Never print these values in chat. If Caio pastes a token directly into the conversation,
save it to `.env` and don't echo it back.

## What this skill does NOT do

- **Scheduling for a future date/time.** This skill only publishes immediately (`prepare`
  gets everything ready, `publish` goes live right then). A container created by `prepare`
  expires after ~24h unpublished, so it cannot sit ready for a post next week. Real
  scheduling needs a cloud-side trigger (a scheduled agent) to run `prepare` + `publish` at
  the target time — that's a separate piece of infrastructure this skill doesn't set up on
  its own; flag this to Caio if he asks for a future-dated post.
- **Reels or any video post.** The Graph API can publish a video, but it cannot attach a
  track from Instagram's licensed music library to it — that's app-only. An API-published
  Reel would either be silent or need audio baked into the video file beforehand. This skill
  refuses video input outright rather than silently publishing something worse than what
  Caio actually wants. If he wants a music-backed Reel, that needs a different, video-editing
  step upstream (mixing a royalty-free track into the file) before this skill would apply.
- **Stories.** Not implemented — the pipeline as built targets feed photo/carousel posts.
- **Editing or deleting a published post.** Once `publish` runs, further changes happen
  manually in the Instagram app, or via a new Graph API call this skill doesn't wrap yet.

## Relationship to the other skills

Step 4, downstream of `rarity-ig-designer` (Step 2, the art) and `rarity-ig-captions` (Step 3,
the caption). It reads their output from disk; it doesn't regenerate either. If the art or
caption isn't final yet, send Caio back to those skills first rather than publishing a draft.
