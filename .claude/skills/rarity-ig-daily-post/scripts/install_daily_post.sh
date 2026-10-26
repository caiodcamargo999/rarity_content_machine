#!/bin/bash
# Installs (or replaces) the macOS LaunchAgent that publishes one Rarity post per day.
# Run ONCE in Terminal on the Mac:   bash ".../install_daily_post.sh" [HH] [MM]
# Default time: 10:30 local time (America/Sao_Paulo). Uninstall: bash install_daily_post.sh --uninstall
set -e
LABEL="com.rarity.instagram.daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
PY="$REPO/.venv/bin/python3"; [ -x "$PY" ] || PY="$(command -v python3)"

if [ "${1:-}" = "--uninstall" ]; then
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  rm -f "$PLIST"; echo "Removed $LABEL"; exit 0
fi

HOUR="${1:-10}"; MIN="${2:-30}"
mkdir -p "$HOME/Library/LaunchAgents" "$REPO/.publish_state/logs"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array>
    <string>$PY</string>
    <string>$HERE/daily_post.py</string>
    <string>--not-before</string>
    <string>$(printf '%02d:%02d' "$HOUR" "$MIN")</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>StartCalendarInterval</key><dict>
    <key>Hour</key><integer>$HOUR</integer><key>Minute</key><integer>$MIN</integer>
  </dict>
  <key>StandardOutPath</key><string>$REPO/.publish_state/logs/launchd_daily_stdout.log</string>
  <key>StandardErrorPath</key><string>$REPO/.publish_state/logs/launchd_daily_stderr.log</string>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed $LABEL: one post per day at $(printf '%02d:%02d' "$HOUR" "$MIN") local time."
echo "Test without posting:  \"$PY\" \"$HERE/daily_post.py\" --dry-run"
