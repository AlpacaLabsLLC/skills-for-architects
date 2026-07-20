#!/bin/bash
# pre-commit-spec-lint.sh
# PreToolUse hook (matcher: Bash). Fires before git commit — scans staged .md
# files for malformed CSI section references. On findings it exits 2, which
# blocks the commit and feeds the stderr message back to Claude to fix the
# staged files first.
#
# Command detection: matches `git … commit` as word-boundary tokens anywhere
# in the command, so compound forms fire too:
#   git commit -m …              git add -A && git commit -m …
#   git -C <dir> commit …        cd <dir> && git commit …
# Tokens between `git` and `commit` may not cross a command separator
# (; & |), so `git add … && ls` never matches. `git commitish` and
# `git commit-tree` are excluded by the trailing word boundary.
# Known, accepted false positive: quoted strings containing `git commit`
# (e.g. echo "git commit") — harmless, the lint just runs and passes.

INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')

GIT_COMMIT_RE='(^|[;&|[:space:]])git[[:space:]]+([^;&|]*[[:space:]])?commit([[:space:]]|$)'
if ! [[ "$COMMAND" =~ $GIT_COMMIT_RE ]]; then
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
  # NOTE: boundaries use (^|[^0-9]) … ([^0-9]|$) instead of \b — portable
  # across BSD (macOS) and GNU grep.

  # Find lines with 6-digit CSI-like numbers missing spaces
  BAD_COMPACT=$(grep -nE '(^|[^0-9])[0-9]{6}([^0-9]|$)' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_COMPACT" ]; then
    ERRORS="$ERRORS
$FILE: CSI section number missing spaces (use '09 29 00' not '092900'):
$BAD_COMPACT
"
  fi

  # Find lines with dashed CSI numbers
  BAD_DASHED=$(grep -nE '(^|[^0-9])[0-9]{2}-[0-9]{2}-[0-9]{2}([^0-9]|$)' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_DASHED" ]; then
    ERRORS="$ERRORS
$FILE: CSI section number uses dashes (use '09 29 00' not '09-29-00'):
$BAD_DASHED
"
  fi

  # Find lines with dotted CSI numbers
  BAD_DOTTED=$(grep -nE '(^|[^0-9])[0-9]{2}\.[0-9]{2}\.[0-9]{2}([^0-9]|$)' "$FILE" 2>/dev/null | grep -iE 'section|division|spec|CSI|MasterFormat')
  if [ -n "$BAD_DOTTED" ]; then
    ERRORS="$ERRORS
$FILE: CSI section number uses dots (use '09 29 00' not '09.29.00'):
$BAD_DOTTED
"
  fi

  # Check for section references missing a title after the number
  # Match lines that have a valid CSI number but no em dash or text after
  BAD_NOTITLE=$(grep -nE '(^|[^0-9])[0-9]{2} [0-9]{2} [0-9]{2}([^0-9]|$)' "$FILE" 2>/dev/null | grep -ivE '—|--' | grep -iE 'section|spec')
  if [ -n "$BAD_NOTITLE" ]; then
    ERRORS="$ERRORS
$FILE: CSI section reference missing title (use '09 29 00 — Gypsum Board'):
$BAD_NOTITLE
"
  fi

done <<< "$STAGED_FILES"

if [ -n "$ERRORS" ]; then
  {
    printf 'CSI formatting issues found in staged files:\n%s\n' "$ERRORS"
    printf 'Fix these before committing — see rules/csi-formatting.md for conventions.\n'
  } >&2
  # Exit 2 blocks the tool call; Claude Code feeds the stderr above back to
  # Claude so it can fix the staged files and retry the commit.
  exit 2
fi

exit 0
