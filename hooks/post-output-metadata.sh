#!/bin/bash
# post-output-metadata.sh
# Fires after Write tool — stamps markdown reports with YAML front matter if missing.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only process markdown files
if [[ "$FILE_PATH" != *.md ]]; then
  exit 0
fi

# Skip files that already have YAML front matter
if head -1 "$FILE_PATH" 2>/dev/null | grep -q '^---$'; then
  exit 0
fi

# Skip README files and rule files
BASENAME=$(basename "$FILE_PATH")
if [[ "$BASENAME" == "README.md" || "$BASENAME" == "SKILL.md" || "$BASENAME" == "CLAUDE.md" ]]; then
  exit 0
fi

# Skip files inside rules/, hooks/, .claude-plugin/ directories
if echo "$FILE_PATH" | grep -qE '/(rules|hooks|\.claude-plugin)/'; then
  exit 0
fi

# Extract a title from the first heading
TITLE=$(grep -m1 '^#\s' "$FILE_PATH" 2>/dev/null | sed 's/^#\s*//')
if [ -z "$TITLE" ]; then
  TITLE="$BASENAME"
fi

# Build front matter
DATE=$(date '+%Y-%m-%d')
FRONTMATTER="---
title: \"$TITLE\"
date: $DATE
generated_by: skills-for-architects
---
"

# Prepend front matter to file
TMPFILE=$(mktemp)
echo "$FRONTMATTER" > "$TMPFILE"
cat "$FILE_PATH" >> "$TMPFILE"
mv "$TMPFILE" "$FILE_PATH"

exit 0
