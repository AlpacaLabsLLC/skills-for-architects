#!/bin/bash
# post-write-disclaimer-check.sh
# Fires after Write tool. Verifies that markdown outputs claiming to be
# regulatory (via the architecture-studio:requires-disclaimer marker) also
# carry the canonical disclaimer block.
#
# Contract:
#   - A regulatory output ends with the canonical disclaimer block followed
#     by the HTML-comment marker `<!-- architecture-studio:requires-disclaimer -->`.
#   - This hook is marker-driven: if the marker is present, the canonical
#     disclaimer text must also be present. If the marker is absent, the
#     hook stays silent — the skill considered the output non-regulatory.
#   - See rules/professional-disclaimer.md for the canonical block.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check writes with a known markdown path.
[ -z "$FILE_PATH" ] && exit 0
[[ "$FILE_PATH" != *.md ]] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

CONTENT=$(cat "$FILE_PATH")
[ -z "$CONTENT" ] && exit 0

MARKER='<!-- architecture-studio:requires-disclaimer -->'
DISCLAIMER_PHRASE='AI-generated analysis for preliminary planning purposes'

# If no marker, this isn't a regulatory output; nothing to check.
if ! grep -qF "$MARKER" <<< "$CONTENT"; then
  exit 0
fi

# Marker present → canonical disclaimer text must also be present.
if ! grep -qF "$DISCLAIMER_PHRASE" <<< "$CONTENT"; then
  echo "WARNING: $FILE_PATH carries the architecture-studio:requires-disclaimer marker but is missing the canonical disclaimer block. Restore the block from rules/professional-disclaimer.md." >&2
  exit 0
fi

# Marker should be a single end-of-file sentinel; flag duplicates.
MARKER_COUNT=$(grep -cF "$MARKER" <<< "$CONTENT")
if [ "$MARKER_COUNT" -gt 1 ]; then
  echo "WARNING: $FILE_PATH contains the architecture-studio:requires-disclaimer marker $MARKER_COUNT times. It must appear exactly once, at end of file." >&2
fi

exit 0
