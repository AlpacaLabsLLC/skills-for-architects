#!/bin/bash
# pre-commit-spec-lint.sh
# Fires before git commit — scans staged .md files for malformed CSI section references.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only run on git commit commands
if [[ "$COMMAND" != git\ commit* ]]; then
  exit 0
fi

# Get list of staged markdown files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep '\.md$')

if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

ERRORS=""

while IFS= read -r FILE; do
  [ -f "$FILE" ] || continue

  # Check for CSI section references that look malformed
  # Valid: 09 29 00, 07 21 13
  # Invalid: 092900, 09-29-00, 09.29.00

  # Find lines with 6-digit CSI-like numbers missing spaces
  BAD_COMPACT=$(grep -nE '\b[0-9]{6}\b' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_COMPACT" ]; then
    ERRORS="$ERRORS\n$FILE: CSI section number missing spaces (use '09 29 00' not '092900'):\n$BAD_COMPACT\n"
  fi

  # Find lines with dashed CSI numbers
  BAD_DASHED=$(grep -nE '\b[0-9]{2}-[0-9]{2}-[0-9]{2}\b' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_DASHED" ]; then
    ERRORS="$ERRORS\n$FILE: CSI section number uses dashes (use '09 29 00' not '09-29-00'):\n$BAD_DASHED\n"
  fi

  # Find lines with dotted CSI numbers
  BAD_DOTTED=$(grep -nE '\b[0-9]{2}\.[0-9]{2}\.[0-9]{2}\b' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_DOTTED" ]; then
    ERRORS="$ERRORS\n$FILE: CSI section number uses dots (use '09 29 00' not '09.29.00'):\n$BAD_DOTTED\n"
  fi

  # Check for section references missing a title after the number
  # Match lines that have a valid CSI number but no em dash or text after
  BAD_NOTITLE=$(grep -nE '\b[0-9]{2} [0-9]{2} [0-9]{2}\b' "$FILE" 2>/dev/null | grep -ivE '—|--' | grep -iE 'section|spec')
  if [ -n "$BAD_NOTITLE" ]; then
    ERRORS="$ERRORS\n$FILE: CSI section reference missing title (use '09 29 00 — Gypsum Board'):\n$BAD_NOTITLE\n"
  fi

done <<< "$STAGED_FILES"

if [ -n "$ERRORS" ]; then
  echo -e "CSI formatting issues found in staged files:\n$ERRORS" >&2
  echo "Fix these before committing, or see rules/csi-formatting.md for conventions." >&2
  # Warn but don't block — exit 0 to allow commit, change to exit 2 to enforce
  exit 0
fi

exit 0
