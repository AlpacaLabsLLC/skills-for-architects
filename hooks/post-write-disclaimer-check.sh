#!/bin/bash
# post-write-disclaimer-check.sh
# Fires after Write tool — checks that regulatory outputs include the professional disclaimer.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only check markdown reports (skip HTML, CSV, JSON, images)
if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

# Check if the file came from a regulatory skill by scanning for keywords
# that indicate zoning, occupancy, code analysis, or environmental risk content
CONTENT=$(cat "$FILE_PATH" 2>/dev/null)
if [ -z "$CONTENT" ]; then
  exit 0
fi

# Look for regulatory indicators
REGULATORY=false
if echo "$CONTENT" | grep -qiE 'zoning|setback|FAR |floor area ratio|height limit|use group'; then
  REGULATORY=true
elif echo "$CONTENT" | grep -qiE 'occupan(cy|t) load|egress|IBC|IRC|NFPA|fire rating'; then
  REGULATORY=true
elif echo "$CONTENT" | grep -qiE 'flood zone|seismic|FEMA|environmental risk'; then
  REGULATORY=true
elif echo "$CONTENT" | grep -qiE 'BSA|variance|special permit|DOB|violation'; then
  REGULATORY=true
fi

if [ "$REGULATORY" = false ]; then
  exit 0
fi

# Check for disclaimer
if echo "$CONTENT" | grep -qiE 'disclaimer|verified by a licensed professional|preliminary planning purposes'; then
  exit 0
fi

# Missing disclaimer on regulatory output — warn (don't block)
echo "WARNING: $FILE_PATH contains regulatory content but no professional disclaimer. Add the standard disclaimer from rules/professional-disclaimer.md." >&2
exit 0
