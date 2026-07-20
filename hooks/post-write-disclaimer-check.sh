#!/bin/bash
# post-write-disclaimer-check.sh
# PostToolUse hook (matcher: Write|Edit). Verifies that markdown outputs
# claiming to be regulatory (via the architecture-studio:requires-disclaimer
# marker) also carry the canonical disclaimer block.
#
# Contract:
#   - A regulatory output ends with the canonical disclaimer block followed
#     by the HTML-comment marker `<!-- architecture-studio:requires-disclaimer -->`.
#   - This hook is marker-driven: if the marker is present, the canonical
#     disclaimer text must also be present. If the marker is absent, the
#     hook stays silent — the skill considered the output non-regulatory.
#   - Both Write and Edit provide `tool_input.file_path`; Edit carries no
#     full content, so the hook always reads the file from disk.
#   - On findings it emits PostToolUse JSON `{"decision": "block", ...}` on
#     stdout, which surfaces the reason to Claude (stderr + exit 0 is shown
#     to no one).
#   - See rules/professional-disclaimer.md for the canonical block.

INPUT=$(cat)
FILE_PATH=$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check writes/edits with a known markdown path.
[ -z "$FILE_PATH" ] && exit 0
[[ "$FILE_PATH" != *.md ]] && exit 0
[ -f "$FILE_PATH" ] || exit 0
[ -s "$FILE_PATH" ] || exit 0

MARKER='<!-- architecture-studio:requires-disclaimer -->'
DISCLAIMER_PHRASE='AI-generated analysis for preliminary planning purposes'

# If no marker, this isn't a regulatory output; nothing to check.
if ! grep -qF "$MARKER" "$FILE_PATH"; then
  exit 0
fi

PROBLEMS=""

# Marker present → canonical disclaimer text must also be present.
if ! grep -qF "$DISCLAIMER_PHRASE" "$FILE_PATH"; then
  PROBLEMS="$FILE_PATH carries the architecture-studio:requires-disclaimer marker but is missing the canonical disclaimer block. Restore the block from rules/professional-disclaimer.md."
fi

# Marker should be a single end-of-file sentinel; flag duplicates.
MARKER_COUNT=$(grep -cF "$MARKER" "$FILE_PATH")
if [ "$MARKER_COUNT" -gt 1 ]; then
  [ -n "$PROBLEMS" ] && PROBLEMS="$PROBLEMS
"
  PROBLEMS="${PROBLEMS}$FILE_PATH contains the architecture-studio:requires-disclaimer marker $MARKER_COUNT times. It must appear exactly once, at end of file."
fi

if [ -n "$PROBLEMS" ]; then
  jq -n --arg reason "$PROBLEMS" '{decision: "block", reason: $reason}'
fi

exit 0
