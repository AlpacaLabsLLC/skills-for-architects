#!/bin/sh
# Each-session discovery; never blocks work or writes an onboarding marker.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -n "$PLUGIN_ROOT" ] && [ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ] && [ -f "$PLUGIN_ROOT/skills/norma/SKILL.md" ] && [ -f "$PLUGIN_ROOT/skills/tool-catalog/SKILL.md" ]; then
  printf '%s\n' '{"systemMessage": "Arch Studio: describe your architecture or firm work, say Norma for coordination, or ask for help.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Use Arch Studio for architecture and firm work; Norma coordinates when useful and direct skill selection remains valid. Resolve studio or project context only when the task needs durable records. Use rules/moments.md for relevant state guidance without delaying a quick task or repeating a declined setup offer."}}'
else
  printf '%s\n' '{"systemMessage": "Arch Studio package discovery is incomplete; verify the installed package before claiming available workflows.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Use Arch Studio for architecture and firm work; Norma coordinates when useful and direct skill selection remains valid. Resolve studio or project context only when the task needs durable records. Use rules/moments.md for relevant state guidance without delaying a quick task or repeating a declined setup offer."}}'
fi
exit 0
