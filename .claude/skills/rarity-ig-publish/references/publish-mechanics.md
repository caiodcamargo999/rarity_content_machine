# Publish mechanics — Rarity IG

Everything here was learned by actually doing it once, end to end, for Idea 5 ("Eight Million
Same Tools") on 2026-09-06. Read this before improvising a fix.

## Why GitHub is the image host

The Instagram Graph API's Content Publishing endpoint (`POST /{ig-user-id}/media`) only takes
`image_url` — a publicly fetchable URL. It never accepts a direct binary upload for photos.

Two dead ends worth knowing about so they aren't retried:
- **Inlining image bytes as base64 into any tool call (Vercel's `deploy_to_vercel`, a Read-tool
  round-trip, anything text-based) does not scale.** A single ~150-330KB JPEG's base64 can
  balloon to an outsized share of a single turn's output budget — high-entropy base64 tokenizes
  far worse than prose. This isn't a "compress harder" problem; it's mechanically the wrong
  shape of solution. Anything that requires the agent to *generate or read* the full binary as
  text is out.
- **Anonymous third-party upload hosts (catbox.moe, similar) get blocked by the auto-mode
  safety classifier** as an unrecognized outbound destination, and rightly so — don't retry
  the same host expecting a different result.

What works: `git add` + `git commit` + `git push` move the file bytes straight from disk,
never through the model's token stream — only small JSON/text responses come back. The repo
(`caiodcamargo999/rarity_content_machine`, public) already hosts this whole project, so pushing
`ig-assets/<slug>/<lang>/*.jpg` there and reading it back via
`https://raw.githubusercontent.com/caiodcamargo999/rarity_content_machine/main/ig-assets/...`
is free, immediate, and permanent (unlike a Vercel deployment's alias, a raw GitHub file URL at
a specific commit never moves).

Because the repo is public, anything pushed to it is publicly visible immediately, not just
once the Instagram post goes live. Only push a post's assets when it's actually about to be
published — don't pre-stage a week's queue of unpublished ideas into `ig-assets/`.

## Auto-mode classifier notes (Bash)

A few things observed to trip the classifier, all avoidable:
- Piping `git commit` output through `| tail -N` got blocked repeatedly where the identical
  plain `git commit -m "..."` succeeded. Prefer plain commands over piped/suppressed output for
  git operations.
- `git add -A` / `git add .` gets blocked (and is against house style anyway — add paths
  explicitly).
- Occasionally a plain, previously-fine command (e.g. `git add public/`) gets a one-off block
  and then succeeds identically on retry. If a git/file command that has no reason to be
  risky gets denied, retrying once before treating it as a hard block is reasonable.
- Outbound `curl` to an established, already-in-use API host (api.github.com,
  graph.instagram.com) has never been blocked. The block is specifically about *new, unfamiliar*
  destinations (catbox.moe, `vercel whoami` as an auth check) — GitHub/Meta's own APIs, already
  in play for this project, are fine.

## Instagram Graph API flow (Instagram API with Instagram Login)

This app uses the newer Instagram-login-based API (no linked Facebook Page required), set up
2026-09-06 via a "Rarity Content Machine" app on developers.facebook.com:

1. **Item containers** (carousel only, skip for a single photo):
   `POST /{ig-user-id}/media` with `image_url` + `is_carousel_item=true` → returns an `id`.
2. **Parent container**:
   - Carousel: `POST /{ig-user-id}/media` with `media_type=CAROUSEL`,
     `children=<comma-separated item ids>`, `caption=<text>`.
   - Single photo: `POST /{ig-user-id}/media` with `image_url` + `caption` directly (no
     `is_carousel_item`, no `children`).
3. **Poll**: `GET /{container-id}?fields=status_code` until `FINISHED` (seen instantly in
   practice for this account, but poll a few times with a short sleep rather than assuming).
4. **Publish**: `POST /{ig-user-id}/media_publish` with `creation_id=<container-id>`. This is
   the live, irreversible step.
5. **Confirm**: `GET /{media-id}?fields=permalink,media_type,timestamp` for the permalink to
   report back.

Containers expire ~24h after creation if `media_publish` is never called on them. `prepare` is
safe to re-run if a container goes stale — it just creates a fresh one.

## Credentials and where they live

All in the project's `.env` (never committed — already in `.gitignore`):
- `IG_ACCESS_TOKEN` / `IG_USER_ID` — from the Meta app dashboard, Use cases → "Manage
  messaging & content on Instagram" → "API setup with Instagram login" → section 2, "Generate
  access tokens" → Add account → log in as @rarity.agency. The `id` this call returns is the
  canonical `IG_USER_ID` to use — it does NOT necessarily match the ID shown elsewhere in the
  dashboard UI; trust what `GET /{id}?fields=username` echoes back over what's displayed on
  screen.
  - Before this works, @rarity.agency must accept an **Instagram Tester** invite: Meta app →
    App roles → Roles → "Instagram Testers" tab → Add People → invite the handle. Accepting
    happens on the Instagram side at **instagram.com/accounts/manage_access/** (a
    desktop-browser-only settings page — it is not reachable from the mobile app's Accounts
    Center / "App connections" screen, which only lists already-active connections, not
    pending invites).
  - Also needs the `instagram_business_content_publish` permission added under "Permissions
    and features" (status "Ready for testing" is sufficient — no App Review needed as long as
    only admins/testers of the app are posting, which is the case here).
- `GITHUB_TOKEN` — a classic PAT with the `repo` scope, from
  github.com/settings/tokens → Tokens (classic). Used only as `https://TOKEN@github.com/...`
  in a one-off push URL, never written into `git remote` permanently (keeps it out of
  `.git/config`).
- `GITHUB_REPO` — `caiodcamargo999/rarity_content_machine`.

## Known limitations (as of 2026-09-06)

- No Reels/video support in this pipeline. Instagram's licensed music library is only
  selectable from inside the app; the Graph API can publish a video but never attach a
  catalog track to it. An API-published Reel would be silent unless a royalty-free track is
  mixed into the video file before upload — out of scope until that editing step exists.
- No native "schedule for later" — see the Scheduling note in SKILL.md.
