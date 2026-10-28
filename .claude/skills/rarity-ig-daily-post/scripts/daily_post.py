#!/usr/bin/env python3
"""Rarity daily Instagram post: publish the NEXT ready carousel on each account, at most one per account per day.

Runs on the Mac (launchd), never in the cloud sandbox: the Graph API and the .env credentials only
exist there. Reuses the rarity-ig-publish script (prepare, then publish).

Three lanes, each with its own Instagram account, language folder and queue marker:
  EN  @rarity.agency  EN/  READY_TO_POST      (credentials IG_ACCESS_TOKEN / IG_USER_ID)
  ES  @rarity.es      ES/  READY_TO_POST_ES   (IG_ACCESS_TOKEN_ES / IG_USER_ID_ES)
  PT  @rarity.br      PT/  READY_TO_POST_PT   (IG_ACCESS_TOKEN_BR / IG_USER_ID_BR)

A post is eligible in a lane only if its idea folder contains the lane's (empty) marker file, plus
<LANG>/slide-*.png|jpg and a "Caption - *.md" with a "## <LANG>" section. Delete the marker to hold a post
back. After a successful publish the marker is renamed to POSTED.txt (EN) / POSTED_ES.txt / POSTED_PT.txt
(permalink inside) and the day is recorded in .publish_state/daily_post_log.json, so a second run the same
day does nothing for that lane. A lane can have a "start" date; it stays idle until then.

Usage:
  daily_post.py                   # publish the next ready post of every lane (normal scheduled run)
  daily_post.py --dry-run         # show what would be posted, touch nothing, no network
  daily_post.py --lane ES         # only one lane
  daily_post.py --as-of 2026-10-29 --dry-run   # preview what a future day would post
  daily_post.py --force           # ignore the one per day guard (manual catch up only)
  daily_post.py --not-before HH:MM  # do nothing earlier than this local time (RunAtLoad catch up)
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
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm"}

# lane name, language folder, publish account (None = default), queue marker, posted marker, first day, label
LANES = [
    dict(name="EN", lang="EN", account=None, marker="READY_TO_POST", posted="POSTED.txt", start=None, label="@rarity.agency"),
    dict(name="ES", lang="ES", account="ES", marker="READY_TO_POST_ES", posted="POSTED_ES.txt", start="2026-10-29", label="@rarity.es"),
    dict(name="PT", lang="PT", account="BR", marker="READY_TO_POST_PT", posted="POSTED_PT.txt", start="2026-10-29", label="@rarity.br"),
]


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


def candidates(marker_name):
    found = []
    for marker in BRIEFS.glob(f"Designs */Idea * - */{marker_name}"):
        d = marker.parent
        m = re.match(r"Idea\s*(\d+)\s*-", d.name)
        found.append((month_key(d), int(m.group(1)) if m else 9999, d))
    return [d for _, _, d in sorted(found)]


def caption_for(d: Path, lang):
    for p in sorted(d.glob("Caption - *.md")):
        if any(l.strip().upper().startswith(f"## {lang}") for l in p.read_text().splitlines()):
            return p
    return None


def load_ledger():
    try:
        return json.loads(LEDGER.read_text())
    except Exception:
        return []


def posted_today(ledger, lane, today):
    # entries written before lanes existed have no "lane" and belong to EN
    return any(e.get("date") == today and e.get("lane", "EN") == lane["name"] for e in ledger)


def run(cmd, fh):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    out = (p.stdout or "") + (p.stderr or "")
    # never echo credentials, even if a library prints them
    out = re.sub(r"(access_token=|IG_ACCESS_TOKEN\w*=|GITHUB_TOKEN=|ghp_)[^\s&\"']+", r"\1<redacted>", out)
    fh.write(out + "\n")
    fh.flush()
    return p.returncode, out


def mark_posted(d: Path, lane, permalink: str):
    marker = d / lane["marker"]
    (d / lane["posted"]).write_text(f"{permalink}\n{now().isoformat()}\n")
    if marker.exists():
        marker.unlink()


def state_path_for(slug, lane):
    suffix = f"-{lane['account'].lower()}" if lane["account"] else ""
    return STATE / f"{slug}-{lane['lang'].lower()}{suffix}.json"


def run_lane(lane, a, today, ledger, fh):
    """Returns (status, empty): status 0 ok / 1 problem, empty True when the queue had nothing."""
    tag = f"[{lane['name']} {lane['label']}]"
    if lane["start"] and today < lane["start"] and not a.ignore_start:
        log(f"{tag} starts on {lane['start']}. Nothing to do yet.", fh)
        return 0, False
    if not a.force and posted_today(ledger, lane, today):
        log(f"{tag} already posted today. Nothing to do.", fh)
        return 0, False

    for d in candidates(lane["marker"]):
        slug = slugify(d.name)
        state_file = state_path_for(slug, lane)
        # Safety: never post the same carousel twice on the same account.
        if state_file.exists():
            try:
                pub = json.loads(state_file.read_text()).get("published")
            except Exception:
                pub = None
            if pub:
                log(f"{tag} {d.name} was already published ({pub.get('permalink')}). Marking and moving on.", fh)
                if not a.dry_run:
                    mark_posted(d, lane, pub.get("permalink", "unknown"))
                continue

        lang_dir = d / lane["lang"]
        slides = sorted(p for p in lang_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS) if lang_dir.is_dir() else []
        videos = [p for p in lang_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS] if lang_dir.is_dir() else []
        cap = caption_for(d, lane["lang"])
        problems = []
        if len(slides) < 2:
            problems.append(f"fewer than 2 slides in {lane['lang']}/")
        if videos:
            problems.append("video file found (photo/carousel only)")
        if not cap:
            problems.append(f"no Caption - *.md with a '## {lane['lang']}' section")
        if problems:
            msg = f"{tag} {d.name} is not postable: " + "; ".join(problems)
            log(msg, fh)
            notify("Rarity daily post blocked", msg[:180])
            return 1, False

        log(f"{tag} Next post: {d.name} ({len(slides)} slides, caption {cap.name})", fh)
        if a.dry_run:
            log(f"{tag} DRY RUN: stopping before prepare/publish.", fh)
            return 0, False

        cmd = [PYTHON, str(PUBLISH), "prepare", "--idea-dir", str(d), "--lang", lane["lang"], "--caption-md", str(cap)]
        if lane["account"]:
            cmd += ["--account", lane["account"]]
        code, out = run(cmd, fh)
        m = re.search(r"State saved to:\s*(\S.*\.json)", out)
        if code != 0 or "Ready to publish" not in out or not m:
            msg = f"{tag} prepare failed for {d.name}. NOT publishing. See {fh.name}"
            log(msg, fh)
            notify("Rarity daily post FAILED", f"{lane['label']}: prepare failed for {d.name}")
            return 1, False
        state_path = m.group(1).strip()

        code, out = run([PYTHON, str(PUBLISH), "publish", "--state", state_path], fh)
        pm = re.search(r"PUBLISHED:\s*(https?://\S+)", out)
        if code != 0 or not pm:
            msg = f"{tag} publish failed for {d.name}. Check Instagram before retrying. See {fh.name}"
            log(msg, fh)
            notify("Rarity daily post FAILED", f"{lane['label']}: publish failed for {d.name}")
            return 1, False

        permalink = pm.group(1)
        ledger.append({"date": today, "lane": lane["name"], "idea": d.name, "permalink": permalink})
        LEDGER.write_text(json.dumps(ledger, indent=2))
        mark_posted(d, lane, permalink)
        log(f"{tag} PUBLISHED {d.name}: {permalink}", fh)
        notify("Rarity posted", f"{lane['label']}: {d.name}")
        return 0, False

    log(f"{tag} Queue empty: no idea folder has {lane['marker']}.", fh)
    return 0, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--ignore-start", action="store_true", help="post even before the lane start date (manual early start)")
    ap.add_argument("--lane", choices=[l["name"] for l in LANES])
    ap.add_argument("--as-of", help="YYYY-MM-DD, pretend it is this day (use with --dry-run)")
    ap.add_argument("--not-before", help="HH:MM local time; do nothing earlier than this (used with RunAtLoad catch up)")
    a = ap.parse_args()
    if a.as_of and not a.dry_run:
        ap.error("--as-of is only allowed with --dry-run")

    LOGS.mkdir(parents=True, exist_ok=True)
    fh = open(LOGS / f"daily-{now().strftime('%Y%m%d-%H%M%S')}.log", "a")

    if a.not_before and not a.force:
        h, m = map(int, a.not_before.split(":"))
        if (now().hour, now().minute) < (h, m):
            log(f"Before {a.not_before}. Nothing to do yet.", fh)
            return 0

    today = a.as_of or now().date().isoformat()
    ledger = load_ledger()
    rc, empties, lanes = 0, 0, [l for l in LANES if not a.lane or l["name"] == a.lane]
    for lane in lanes:
        try:
            status, empty = run_lane(lane, a, today, ledger, fh)
        except Exception as e:  # one lane failing must not stop the others
            log(f"[{lane['name']}] unexpected error: {e!r}", fh)
            notify("Rarity daily post FAILED", f"{lane['label']}: {e!r}"[:180])
            status, empty = 1, False
        rc = rc or status
        empties += empty
    if empties == len(lanes):
        notify("Rarity daily post", "All queues are empty. Export and mark more posts.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
