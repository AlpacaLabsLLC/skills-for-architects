#!/usr/bin/env bash
# Windows CI: run every Claude Code hook the way hooks.json registers it, under Git Bash, with no
# Python, jq or node on PATH, and Windows-style paths in CLAUDE_PLUGIN_ROOT and in hook input.
# Writes each hook's stdout and exit code to the folder given as $1; tests/windows/check-hooks.py
# validates them afterwards (with Python, which this step must not have).
set -u
out=${1:?usage: run-hooks-no-python.sh <output dir>}
mkdir -p "$out"
repo=$(cd "$(dirname "$0")/../.." && pwd)
win() { cygpath -w "$1"; }

# Only Git for Windows' own tools: sh, bash, tr, sed, grep, ... and none of python, jq or node.
export PATH=/usr/bin:/bin
for tool in python python3 py jq node; do
  if command -v "$tool" >/dev/null 2>&1; then echo "FAIL: $tool is on PATH: $(command -v "$tool")"; exit 1; fi
done

# An installed layout, as Claude Code lays out a plugin cache: .../plugins/cache/<marketplace>/<plugin>/<version>
tmp=$(mktemp -d)
plugin="$tmp/home/.claude/plugins/cache/skills-for-architects/as/1.5.4"
mkdir -p "$plugin"
cp -R "$repo/hooks" "$repo/skills" "$repo/rules" "$repo/.claude-plugin" "$plugin/"
root_win=$(win "$plugin")
data_win=$(win "$tmp/home/.claude/plugins/data/as-skills-for-architects")
printf '%s\n' "$root_win" > "$out/plugin-root.txt"
printf '%s\n' "$(win "$tmp")" > "$out/tmp-root.txt"

# The commands exactly as registered (the check step compares them with hooks.json).
CMD_WELCOME='/bin/sh "${CLAUDE_PLUGIN_ROOT}/hooks/session-start-welcome.sh"'
CMD_VERSION='bash "${CLAUDE_PLUGIN_ROOT}/hooks/version-check.sh"'
CMD_POINTER='/bin/sh "${CLAUDE_PLUGIN_ROOT}/hooks/as-rhino-context.sh"'
CMD_DISCLAIMER='bash "${CLAUDE_PLUGIN_ROOT}/hooks/post-write-disclaimer-check.sh"'
printf '%s\n' "$CMD_WELCOME" "$CMD_VERSION" "$CMD_POINTER" "$CMD_DISCLAIMER" > "$out/commands.txt"

run() {  # name, stdin, command, extra env...
  name=$1; input=$2; cmd=$3; shift 3
  printf '%s' "$input" | env CLAUDE_PLUGIN_ROOT="$root_win" "$@" bash -c "$cmd" > "$out/$name.out" 2> "$out/$name.err"
  echo $? > "$out/$name.rc"
}
start='{"hook_event_name":"SessionStart","source":"startup"}'

run pointer "$start" "$CMD_POINTER" CLAUDE_PLUGIN_DATA="$data_win"
run pointer-derived "$start" "$CMD_POINTER"
run welcome "$start" "$CMD_WELCOME"
state="$tmp/state"   # a real install uses $HOME/.claude, a POSIX path under Git Bash
run version-off "$start" "$CMD_VERSION" ARCHITECTURE_STUDIO_STATE_DIR="$state" AS_UPDATE_CHECK_DISABLED=1 AS_TELEMETRY_DISABLED=1
run version-seed "$start" "$CMD_VERSION" ARCHITECTURE_STUDIO_STATE_DIR="$state" AS_TELEMETRY_DISABLED=1
[ -f "$tmp/state/.architecture-studio-version-check" ] && echo seeded > "$out/version-seed.cache" || echo missing > "$out/version-seed.cache"

# Disclaimer check: Windows paths with backslashes and a space, as Claude Code sends them.
mkdir -p "$tmp/docs dir"
printf 'Zoning summary\n\n<!-- architecture-studio:requires-disclaimer -->\n' > "$tmp/docs dir/marked.md"
printf 'Plain notes\n' > "$tmp/docs dir/plain.md"
json_path() { win "$1" | sed -e 's/\\/\\\\/g'; }
run disclaimer-marked "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$(json_path "$tmp/docs dir/marked.md")\",\"content\":\"x\"}}" "$CMD_DISCLAIMER"
run disclaimer-plain "{\"tool_name\":\"Edit\",\"tool_input\":{\"file_path\":\"$(json_path "$tmp/docs dir/plain.md")\",\"old_string\":\"a\",\"new_string\":\"b\"}}" "$CMD_DISCLAIMER"

# A broken package (a separate copy): the pointer stays silent and exits 0.
broken="$tmp/broken/plugins/cache/skills-for-architects/as/1.5.4"
mkdir -p "$broken" && cp -R "$plugin/hooks" "$plugin/skills" "$broken/" && rm "$broken/skills/as-rhino-index.md"
printf '%s' "$start" | env CLAUDE_PLUGIN_ROOT="$(win "$broken")" bash -c "$CMD_POINTER" > "$out/pointer-broken.out" 2> "$out/pointer-broken.err"
echo $? > "$out/pointer-broken.rc"
ls "$out"
