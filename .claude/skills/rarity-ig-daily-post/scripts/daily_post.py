#!/usr/bin/env python3
"""Rarity daily Instagram post: publish the NEXT ready carousel to @rarity.agency, at most one per day.

Runs on the Mac (launchd), never in the cloud sandbox: the Graph API and the .env credentials only
exist there. Reuses the rarity-ig-publish script (prepare, then publish).

A post is eligible only if its idea folder contains an (empty) file named READY_TO_POST, plus
EN/slide-*.png|jpg and a "Caption - *.md" with a "## EN" section. Delete READY_TO_POST to hold a post back.
After a successful publish READY_TO_POST is renamed to POSTED.txt (permalink inside) and the day is
recorded in .publish_state/daily_post_log.json, so a second run the same day does nothing.

Usage:
  daily_post.py            # publish the next ready post (normal scheduled run)
  daily_post.py --dry-run  # show what would be posted, touch nothing, no network
  daily_post.py --force    # ignore the one per day guard (manual catch up only)
"""
import argparse, json, re, subprocess, sys
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Sao_Paulo")
except Exception:  # pragma: no cover
    TZ = None

REPO = Path(__file__).resolve().parents[4]
PUBLISH = REPO / ".claude/skills/rarity-ig-publish/scripts/publish_post.py"
STATE = REPO / ".publish_state"
LOGS = STATE / "logs"
LEDGER = STATE / "daily_post_log.json"
BRIEFS = REPO / "public" / "Instagram Briefings"
PY = REPO / ".venv/bin/python3"
PYTHON = str(PY) if PY.exists() else sys.executable
LANG = "EN"
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}


def now():
    return datetime.now(TZ) if TZ else datetime.now()


def log(msg, fh=None):
    line = f"[{now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    if fh:
        fh.write(line + "\n")
        fh.flush()


def notify(title, text):
    try:
        subprocess.run(["osascript", "-e", f'display notification "{text}" with title "{title}"'],
                       timeout=10, check=False, capture_output=True)
    except Exception:
        pass


def slugify(name):
    s = re.sub(r"^Idea\s*\d+\s*-\s*", "", name, flags=re.IGNORECASE)
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower() or "post"


def month_key(d: Path):
    try:
        return datetime.strptime(d.parent.name.replace("Designs ", ""), "%B %Y")
    except ValueError:
        return datetime.min


def candidates():
    found = []
    for marker in BRIEFS.glob("Designs */Idea * - */READY_TO_POST"):
        d = marker.parent
        m = re.match(r"Idea\s*(\d+)\s*-", d.name)
        found.append((month_key(d), int(m.group(1)) if m else 9999, d))
    return [d for _, _, d in sorted(found)]


def caption_for(d: Path):
    for p in sorted(d.glob("Caption - *.md")):
        if any(l.strip().upper().startswith("## EN") for l in p.read_text().splitlines()):
            return p
    return None


def load_ledger():
    try:
        return json.loads(LEDGER.read_text())
    except Exception:
        return []


def run(cmd, fh):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    out = (p.stdout or "") + (p.stderr or "")
    # never echo credentials, even if a library prints them
    out = re.sub(r"(access_token=|IG_ACCESS_TOKEN=|GITHUB_TOKEN=|ghp_)[^\s&\"']+", r"\1<redacted>", out)
    fh.write(out + "\n")
    fh.flush()
    return p.returncode, out


def mark_posted(d: Path, permalink: str):
    marker = d / "READY_TO_POST"
    (d / "POSTED.txt").write_text(f"{permalink}\n{now().isoformat()}\n")
    if marker.exists():
        marker.unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--not-before", help="HH:MM local time; do nothing earlier than this (used with RunAtLoad catch up)")
    a = ap.parse_args()

    LOGS.mkdir(parents=True, exist_ok=True)
    fh = open(LOGS / f"daily-{now().strftime('%Y%m%d-%H%M%S')}.log", "a")
    today = now().date().isoformat()
    ledger = load_ledger()

    if a.not_before and not a.force:
        h, m = map(int, a.not_before.split(":"))
        if (now().hour, now().minute) < (h, m):
            log(f"Before {a.not_before}. Nothing to do yet.", fh)
            return 0

    if not a.force and any(e.get("date") == today for e in ledger):
        log("Already posted today. Nothing to do.", fh)
        return 0

    for d in candidates():
        slug = slugify(d.name)
        state_file = STATE / f"{slug}-{LANG.lower()}.json"
        # Safety: never post the same carousel twice.
        if state_file.exists():
            try:
                pub = json.loads(state_file.read_text()).get("published")
            except Exception:
                pub = None
            if pub:
                log(f"{d.name} was already published ({pub.get('permalink')}). Marking and moving on.", fh)
                if not a.dry_run:
                    mark_posted(d, pub.get("permalink", "unknown"))
                continue

        lang_dir = d / LANG
        slides = sorted(p for p in lang_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS) if lang_dir.is_dir() else []
        videos = [p for p in lang_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS] if lang_dir.is_dir() else []
        cap = caption_for(d)
        problems = []
        if len(slides) < 2:
            problems.append("fewer than 2 slides in EN/")
        if videos:
            problems.append("video file found (photo/carousel only)")
        if not cap:
            problems.append("no Caption - *.md with a '## EN' section")
        if problems:
            msg = f"{d.name} is not postable: " + "; ".join(problems)
            log(msg, fh)
            notify("Rarity daily post blocked", msg[:180])
            return 1

        log(f"Next post: {d.name} ({len(slides)} slides, caption {cap.name})", fh)
        if a.dry_run:
            log("DRY RUN: stopping before prepare/publish.", fh)
            return 0

        code, out = run([PYTHON, str(PUBLISH), "prepare", "--idea-dir", str(d), "--lang", LANG, "--caption-md", str(cap)], fh)
        m = re.search(r"State saved to:\s*(\S.*\.json)", out)
        if code != 0 or "Ready to publish" not in out or not m:
            msg = f"prepare failed for {d.name}. NOT publishing. See {fh.name}"
            log(msg, fh)
            notify("Rarity daily post FAILED", f"prepare failed for {d.name}")
            return 1
        state_path = m.group(1).strip()

        code, out = run([PYTHON, str(PUBLISH), "publish", "--state", state_path], fh)
        pm = re.search(r"PUBLISHED:\s*(https?://\S+)", out)
        if code != 0 or not pm:
            msg = f"publish failed for {d.name}. Check Instagram before retrying. See {fh.name}"
            log(msg, fh)
            notify("Rarity daily post FAILED", f"publish failed for {d.name}")
            return 1

        permalink = pm.group(1)
        ledger.append({"date": today, "idea": d.name, "permalink": permalink})
        LEDGER.write_text(json.dumps(ledger, indent=2))
        mark_posted(d, permalink)
        log(f"PUBLISHED {d.name}: {permalink}", fh)
        notify("Rarity posted", f"{d.name}")
        return 0

    log("Queue empty: no idea folder has READY_TO_POST.", fh)
    notify("Rarity daily post", "Queue is empty. Export and mark more posts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
