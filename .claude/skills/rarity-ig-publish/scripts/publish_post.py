#!/usr/bin/env python3
"""
publish_post.py — Rarity IG publishing (Step 4 of the pipeline).

Takes the finished art (Step 2, rarity-ig-designer) and the finished caption (Step 3,
rarity-ig-captions) and puts the post live on Instagram, via the Instagram Graph API
(Instagram API with Instagram Login — no linked Facebook Page required).

Why GitHub is in the loop: the Graph API's Content Publishing endpoint only accepts an
"image_url" — it cannot take a direct file upload. Local PNGs are compressed to JPEG,
committed to this project's own GitHub repo under ig-assets/<slug>/<lang>/, and pushed.
raw.githubusercontent.com then serves as the public URL Meta's crawler fetches from.

Split into two explicit steps on purpose — "prepare" and "publish" — because going live
is irreversible and public. "prepare" does everything up to and including Meta finishing
its processing, then stops and prints a creation_id. Nothing goes live until "publish" is
run separately, deliberately, against that creation_id.

Usage:
  python3 publish_post.py prepare --idea-dir "<path to .../Idea N - Name>" --lang EN \
      [--caption-md "<path to Caption - Name.md>" | --caption-file <plain text file>] \
      [--slug custom-slug]
    -> prints a creation_id, saves state to <repo_root>/.publish_state/<slug>-<lang>.json

  python3 publish_post.py publish --state <path to that .json>
    -> calls media_publish. THIS IS THE STEP THAT GOES LIVE. Prints the permalink.

  python3 publish_post.py status --state <path to that .json>
    -> re-checks container status_code without publishing anything.

Credentials come from <repo_root>/.env: IG_ACCESS_TOKEN, IG_USER_ID, GITHUB_TOKEN, GITHUB_REPO.
Instagram media containers expire ~24h after creation if unpublished — don't run "prepare"
more than a few hours before you intend to "publish".

Only feed photo / carousel posts are supported. Reels/video are NOT — the Graph API cannot
attach Instagram's licensed music library to a Reel (that only works from inside the app),
so a "silent" API-published Reel would be a worse result than a carousel; this script raises
a clear error instead of publishing something you didn't ask for.
"""
import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

GRAPH_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.instagram.com/{GRAPH_VERSION}"
REPO_ROOT = Path(__file__).resolve().parents[4]
STATE_DIR = REPO_ROOT / ".publish_state"
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".mov"}


def load_env():
    env_path = REPO_ROOT / ".env"
    env = {}
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    required = ["IG_ACCESS_TOKEN", "IG_USER_ID", "GITHUB_TOKEN", "GITHUB_REPO"]
    missing = [k for k in required if not env.get(k)]
    if missing:
        sys.exit(f"Missing in .env: {', '.join(missing)}")
    return env


def slugify(name):
    s = re.sub(r"^Idea\s*\d+\s*-\s*", "", name, flags=re.IGNORECASE)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s or "post"


def natural_key(p: Path):
    m = re.search(r"(\d+)", p.stem)
    return (int(m.group(1)) if m else 0, p.name)


def find_slides(idea_dir: Path, lang: str):
    lang_dir = idea_dir / lang
    if not lang_dir.is_dir():
        sys.exit(f"No {lang}/ folder inside {idea_dir}")
    videos = sorted(p for p in lang_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS)
    if videos:
        sys.exit(
            "Found a video file in this folder. This script only publishes photo/carousel "
            "posts — Reels/video publishing isn't supported here (see the skill's README "
            "for why: the Graph API can't attach Instagram's music library to a Reel)."
        )
    images = sorted(
        (p for p in lang_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS),
        key=natural_key,
    )
    if not images:
        sys.exit(f"No slide images found in {lang_dir}")
    return images


def extract_caption_from_md(md_path: Path, lang: str) -> str:
    text = md_path.read_text()
    lang_headers = {"EN": "## EN", "ES": "## ES", "PT": "## PT"}
    header = lang_headers.get(lang.upper())
    if not header:
        sys.exit(f"Unknown lang '{lang}' for caption extraction (expected EN, ES, or PT)")
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().upper().startswith(header):
            start = i + 1
            break
    if start is None:
        sys.exit(f"No '{header}' section found in {md_path}")
    out = []
    for line in lines[start:]:
        if line.strip().startswith("## ") or line.strip() == "---":
            break
        out.append(line)
    caption = "\n".join(out).strip()
    if not caption:
        sys.exit(f"Empty caption extracted for {lang} from {md_path}")
    return caption


def convert_to_jpeg(src: Path, dst: Path, quality=85):
    from PIL import Image

    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.save(dst, "JPEG", quality=quality, optimize=True)


def run(cmd, **kwargs):
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def git_publish_assets(paths, slug, lang, env):
    rel_paths = [str(p.relative_to(REPO_ROOT)) for p in paths]
    run(["git", "add", *rel_paths])
    status = run(["git", "status", "--short", *rel_paths])
    if status:
        run(["git", "commit", "-m", f"Publish assets: {slug} ({lang})"])
    push_url = f"https://{env['GITHUB_TOKEN']}@github.com/{env['GITHUB_REPO']}.git"
    run(["git", "push", push_url, "HEAD:main"])


def raw_url(slug, lang, filename, env):
    return (
        f"https://raw.githubusercontent.com/{env['GITHUB_REPO']}/main/"
        f"ig-assets/{slug}/{lang.lower()}/{filename}"
    )


def verify_public(url, tries=6, delay=2):
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                if resp.status == 200:
                    return True
        except urllib.error.HTTPError as e:
            if attempt == tries - 1:
                sys.exit(f"Image URL not reachable ({e.code}): {url}")
        except urllib.error.URLError:
            pass
        time.sleep(delay)
    sys.exit(f"Image URL never became reachable: {url}")


def graph_post(path, data, env):
    url = f"{GRAPH_BASE}/{path}"
    body = urllib.parse.urlencode({**data, "access_token": env["IG_ACCESS_TOKEN"]}).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Graph API error on POST {path}: {e.read().decode()}")


def graph_get(path, params, env):
    query = urllib.parse.urlencode({**params, "access_token": env["IG_ACCESS_TOKEN"]})
    url = f"{GRAPH_BASE}/{path}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"Graph API error on GET {path}: {e.read().decode()}")


def cmd_prepare(args):
    env = load_env()
    idea_dir = Path(args.idea_dir).resolve()
    lang = args.lang.upper()
    slug = args.slug or slugify(idea_dir.name)

    slides = find_slides(idea_dir, lang)
    print(f"Found {len(slides)} slide(s) in {idea_dir.name}/{lang}")

    if args.caption_md:
        caption = extract_caption_from_md(Path(args.caption_md).resolve(), lang)
    elif args.caption_file:
        caption = Path(args.caption_file).read_text().strip()
    else:
        sys.exit("Provide --caption-md or --caption-file")
    print(f"Caption loaded ({len(caption)} chars)")

    jpeg_paths = []
    for i, src in enumerate(slides, start=1):
        dst = REPO_ROOT / "ig-assets" / slug / lang.lower() / f"slide-{i}.jpg"
        convert_to_jpeg(src, dst)
        jpeg_paths.append(dst)
    print(f"Compressed {len(jpeg_paths)} slide(s) to JPEG")

    git_publish_assets(jpeg_paths, slug, lang, env)
    print("Pushed to GitHub")

    urls = [raw_url(slug, lang, p.name, env) for p in jpeg_paths]
    for u in urls:
        verify_public(u)
    print("All image URLs are publicly reachable")

    if len(urls) == 1:
        resp = graph_post(
            f"{env['IG_USER_ID']}/media",
            {"image_url": urls[0], "caption": caption},
            env,
        )
        container_id = resp["id"]
    else:
        item_ids = []
        for u in urls:
            resp = graph_post(
                f"{env['IG_USER_ID']}/media",
                {"image_url": u, "is_carousel_item": "true"},
                env,
            )
            item_ids.append(resp["id"])
        resp = graph_post(
            f"{env['IG_USER_ID']}/media",
            {
                "media_type": "CAROUSEL",
                "children": ",".join(item_ids),
                "caption": caption,
            },
            env,
        )
        container_id = resp["id"]
    print(f"Container created: {container_id}")

    status = None
    for _ in range(10):
        resp = graph_get(str(container_id), {"fields": "status_code"}, env)
        status = resp.get("status_code")
        print(f"  status: {status}")
        if status == "FINISHED":
            break
        if status == "ERROR":
            sys.exit(f"Container processing failed: {resp}")
        time.sleep(3)
    if status != "FINISHED":
        sys.exit(f"Container never reached FINISHED (last status: {status})")

    STATE_DIR.mkdir(exist_ok=True)
    state_path = STATE_DIR / f"{slug}-{lang.lower()}.json"
    state_path.write_text(
        json.dumps(
            {
                "slug": slug,
                "lang": lang,
                "idea_dir": str(idea_dir),
                "ig_user_id": env["IG_USER_ID"],
                "creation_id": container_id,
                "image_urls": urls,
                "prepared_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        )
    )
    print(f"\nReady to publish. State saved to: {state_path}")
    print(f"Run: python3 {Path(__file__).name} publish --state \"{state_path}\"")


def cmd_status(args):
    env = load_env()
    state = json.loads(Path(args.state).read_text())
    resp = graph_get(state["creation_id"], {"fields": "status_code"}, env)
    print(resp)


def cmd_publish(args):
    env = load_env()
    state_path = Path(args.state)
    state = json.loads(state_path.read_text())
    resp = graph_post(
        f"{state['ig_user_id']}/media_publish",
        {"creation_id": state["creation_id"]},
        env,
    )
    media_id = resp["id"]
    info = graph_get(media_id, {"fields": "permalink,media_type,timestamp"}, env)
    print(f"PUBLISHED: {info.get('permalink')}")
    print(json.dumps(info, indent=2))
    state["published"] = info
    state_path.write_text(json.dumps(state, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prepare = sub.add_parser("prepare")
    p_prepare.add_argument("--idea-dir", required=True)
    p_prepare.add_argument("--lang", required=True)
    p_prepare.add_argument("--caption-md")
    p_prepare.add_argument("--caption-file")
    p_prepare.add_argument("--slug")
    p_prepare.set_defaults(func=cmd_prepare)

    p_status = sub.add_parser("status")
    p_status.add_argument("--state", required=True)
    p_status.set_defaults(func=cmd_status)

    p_publish = sub.add_parser("publish")
    p_publish.add_argument("--state", required=True)
    p_publish.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
