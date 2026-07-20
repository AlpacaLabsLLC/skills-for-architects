#!/usr/bin/env bash
# First-session welcome: confirm the install and offer /learn.
# Fires on SessionStart (matcher: startup); a marker file limits it to the
# first session after install. Exit 0 always — a broken welcome must never
# block a session.

set -u

DATA_DIR="${CLAUDE_PLUGIN_DATA:-$HOME/.claude}"
MARKER="$DATA_DIR/.architecture-studio-welcomed"

[ -f "$MARKER" ] && exit 0
mkdir -p "$DATA_DIR" 2>/dev/null || exit 0
touch "$MARKER" 2>/dev/null || exit 0

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
SKILL_COUNT=0
if [ -n "$PLUGIN_ROOT" ] && [ -d "$PLUGIN_ROOT/skills" ]; then
  SKILL_COUNT=$(find "$PLUGIN_ROOT/skills" -mindepth 2 -maxdepth 2 -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
fi

if [ "$SKILL_COUNT" -ge 40 ]; then
  STATUS="Architecture Studio installed successfully: $SKILL_COUNT skills, 7 agents, and its hooks are loaded."
elif [ "$SKILL_COUNT" -gt 0 ]; then
  STATUS="Architecture Studio loaded partially: only $SKILL_COUNT of 40 skills were found. Suggest the user run: claude plugin marketplace update skills-for-architects, then reinstall architecture-studio."
else
  STATUS="Architecture Studio's hooks are running but its skills directory was not found. Suggest the user reinstall: claude plugin install architecture-studio@skills-for-architects."
fi

CONTEXT="[architecture-studio first run] $STATUS
This is the user's first session since installing Architecture Studio. At the start of your reply — before addressing anything else, unless the user's message is already /learn or /studio — do two things in a short paragraph, then continue normally:
1. Report the install status above in one plain sentence.
2. Offer the guided course: type /learn for a ~15-minute jump start. Mention what it covers in one sentence: how this works locally (your files stay in your folders on your machine — no ALPA servers, no accounts; only what you ask about goes to Claude, like any conversation), what Architecture Studio is (a pre-configured, open-source harness on Claude Code so a firm doesn't start from zero — fork it and make it your own), and how memory works here (plain markdown files you can open and read — everything the tools know is on your disk, in the open).
Do not repeat this welcome in later sessions."

if command -v jq >/dev/null 2>&1; then
  jq -n --arg ctx "$CONTEXT" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$ctx}}'
else
  ESCAPED=$(printf '%s' "$CONTEXT" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed -e 's/\\n$//')
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ESCAPED"
fi
exit 0
