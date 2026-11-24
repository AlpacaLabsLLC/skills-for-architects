#!/bin/sh
# Rhino pointer (Arch Studio): SessionStart hook.
#
# The Rhino AI panel cannot load plugin skills, so this adds one short line naming the skill
# index in this installed plugin version and the folder the as-rhino skills keep their lessons
# in. That folder is Claude Code's plugin data folder (CLAUDE_PLUGIN_DATA), which survives
# plugin updates; the panel has no plugin variables, so the line is how a skill finds it.
#
# Plain POSIX sh with tr and sed only: no Python, node or jq, so it runs in macOS's sh and in
# Git Bash, the shell Claude Code uses for hooks on Windows. Paths are printed with forward
# slashes, which Rhino's Python reads on Windows too. No input, no network, no writes.
# Any problem means no output and exit 0, so it can never block a session.

root=${CLAUDE_PLUGIN_ROOT:-}
if [ -z "$root" ]; then
  case $0 in
    */*) root=$(cd "$(dirname "$0")/.." 2>/dev/null && pwd) || exit 0 ;;
    *) exit 0 ;;
  esac
fi
root=$(printf '%s' "$root" | tr '\\' '/') || exit 0
root=${root%/}
index="$root/skills/as-rhino-index.md"
[ -f "$index" ] || exit 0

data=${CLAUDE_PLUGIN_DATA:-}
if [ -n "$data" ]; then
  data=$(printf '%s' "$data" | tr '\\' '/') || exit 0
  data=${data%/}
else
  # The same folder Claude Code uses: .../plugins/cache/<marketplace>/<plugin>/<version>
  # -> .../plugins/data/<plugin>@<marketplace>, with every character other than a letter,
  # digit, _ or - replaced by -.
  plugin_dir=${root%/*}
  market_dir=${plugin_dir%/*}
  cache_dir=${market_dir%/*}
  plugins_dir=${cache_dir%/*}
  if [ "${cache_dir##*/}" = cache ] && [ "${plugins_dir##*/}" = plugins ]; then
    id=$(printf '%s@%s' "${plugin_dir##*/}" "${market_dir##*/}" | sed 's/[^A-Za-z0-9_-]/-/g') || exit 0
    data="$plugins_dir/data/$id"
  fi
fi

line="Arch Studio: if the user names an as-rhino skill or Arch Studio in Rhino, read $index with run_python; with a Skill tool, use it instead. Read again after compaction."
if [ -n "$data" ] && [ -f "$root/skills/as-rhino-lessons.py" ]; then
  line="$line Their lessons folder: $data/rhino-lessons."
fi
# A path with a control character (tab, newline, ...) would not be valid JSON: stay silent rather than print it.
case $line in *[[:cntrl:]]*) exit 0 ;; esac
line=$(printf '%s' "$line" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g') || exit 0
printf '{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "%s"}}\n' "$line" || true
exit 0
