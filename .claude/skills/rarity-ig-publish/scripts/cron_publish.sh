#!/bin/bash
# cron_publish.sh — wrapper for scheduled (cron) prepare+publish runs.
# Usage: cron_publish.sh "<idea-dir>" "<caption-md>" "<lang>" ["<account>"]
#   account defaults to "default" (@rarity.agency). Pass "ES" for @rarity.es.
# Logs everything to logs/<slug>-<lang>-<account>-<timestamp>.log inside .publish_state/.
set -u

REPO_ROOT="/Users/lenovo/Desktop/DIGITAL MARKETING/02_RARITY GROUP/RARITY AGENCY/RARITY AI/rarity_content_machine"
PYTHON="$REPO_ROOT/.venv/bin/python3"
SCRIPT="$REPO_ROOT/.claude/skills/rarity-ig-publish/scripts/publish_post.py"

IDEA_DIR="$1"
CAPTION_MD="$2"
POST_LANG="${3:-EN}"
POST_ACCOUNT="${4:-default}"
POST_LANG_LOWER=$(echo "$POST_LANG" | tr '[:upper:]' '[:lower:]')
POST_ACCOUNT_LOWER=$(echo "$POST_ACCOUNT" | tr '[:upper:]' '[:lower:]')

LOG_DIR="$REPO_ROOT/.publish_state/logs"
mkdir -p "$LOG_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
SLUG_GUESS=$(basename "$IDEA_DIR" | sed -E 's/^Idea [0-9]+ - //' | tr '[:upper:] ' '[:lower:]-')
LOG_FILE="$LOG_DIR/${SLUG_GUESS}-${POST_LANG_LOWER}-${POST_ACCOUNT_LOWER}-${STAMP}.log"

{
  echo "=== cron_publish.sh started at $(date) ==="
  echo "idea-dir: $IDEA_DIR"
  echo "caption-md: $CAPTION_MD"
  echo "lang: $POST_LANG"
  echo "account: $POST_ACCOUNT"
  echo

  echo "--- prepare ---"
  PREPARE_OUT=$("$PYTHON" "$SCRIPT" prepare --idea-dir "$IDEA_DIR" --lang "$POST_LANG" --caption-md "$CAPTION_MD" --account "$POST_ACCOUNT" 2>&1)
  echo "$PREPARE_OUT"

  STATE_PATH=$(echo "$PREPARE_OUT" | grep -oE '\.publish_state/[^"[:space:]]+\.json' | tail -1)
  if [ -z "$STATE_PATH" ]; then
    echo "ERROR: could not find state file path in prepare output. Aborting, NOT publishing."
    exit 1
  fi
  FULL_STATE_PATH="$REPO_ROOT/$STATE_PATH"
  echo "Resolved state file: $FULL_STATE_PATH"

  if ! echo "$PREPARE_OUT" | grep -q "Ready to publish"; then
    echo "ERROR: prepare did not report 'Ready to publish'. Aborting, NOT publishing."
    exit 1
  fi

  echo
  echo "--- publish (going live) ---"
  "$PYTHON" "$SCRIPT" publish --state "$FULL_STATE_PATH" 2>&1

  echo
  echo "=== cron_publish.sh finished at $(date) ==="
} >> "$LOG_FILE" 2>&1

exit $?
