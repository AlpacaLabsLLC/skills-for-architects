#!/bin/sh
# Each-session discovery; never blocks work or writes an onboarding marker.
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-}"
if [ -n "$PLUGIN_ROOT" ] && [ -f "$PLUGIN_ROOT/.claude-plugin/plugin.json" ] && [ -f "$PLUGIN_ROOT/skills/start/SKILL.md" ] && [ -f "$PLUGIN_ROOT/skills/tool-catalog/SKILL.md" ]; then
  printf '%s\n' '{"systemMessage": "Arch Studio: run /as:start to see what it can do, or describe your architecture or firm work.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Use Arch Studio for architecture and firm work: select the skill that owns the task, and use workplan when substantial multistep work benefits from a plan. Resolve studio or project context only when the task needs durable records. Use rules/moments.md for relevant state guidance without delaying a quick task or repeating a declined setup offer."}}'
else
  printf '%s\n' '{"systemMessage": "Arch Studio package discovery is incomplete; verify the installed package before claiming available workflows.", "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "Use Arch Studio for architecture and firm work: select the skill that owns the task, and use workplan when substantial multistep work benefits from a plan. Resolve studio or project context only when the task needs durable records. Use rules/moments.md for relevant state guidance without delaying a quick task or repeating a declined setup offer."}}'
fi
exit 0
