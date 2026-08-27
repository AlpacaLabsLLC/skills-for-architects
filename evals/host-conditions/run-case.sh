#!/usr/bin/env bash
# Run one host-condition case against one plugin checkout.
#
# Usage: run-case.sh <plugin-root> <shell|noshell> <case-id> <trial> <prompt> <out-dir>
#
# The `noshell` condition withholds Bash, Write and Edit, which is how a host
# without shell execution or local file writing behaves. Use --disallowedTools
# for this: --allowedTools is an auto-approve list, not a restriction, and on
# its own leaves every tool reachable.
set -euo pipefail

plugin_root=${1:?usage: run-case.sh <plugin-root> <condition> <case-id> <trial> <prompt> <out-dir>}
condition=${2:?missing condition}
case_id=${3:?missing case id}
trial=${4:?missing trial}
prompt=${5:?missing prompt}
out_dir=${6:?missing out dir}

version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' \
  "$plugin_root/.claude-plugin/plugin.json")
stem="${version}__${condition}__${case_id}__${trial}"

mkdir -p "$out_dir/results" "$out_dir/runs"
work="$out_dir/runs/$stem"
"$(dirname "$0")/make-fixture.sh" "$work" "$plugin_root" >/dev/null

# Snapshot the fixture before the run so the grader can tell a modified file
# from an untouched one. Name-only comparison misses in-place writes.
snapshot() { find "$work" -type f -exec shasum -a 256 {} + | sed "s|$work/||" | sort; }
snapshot > "$out_dir/results/$stem.baseline"

if [ "$condition" = shell ]; then
  tool_flags=(--allowedTools Skill Read Glob Grep Write Edit Bash WebFetch WebSearch)
else
  tool_flags=(--allowedTools Skill Read Glob Grep WebFetch WebSearch
              --disallowedTools Bash Write Edit NotebookEdit)
fi

(
  cd "$work" || exit 1
  claude -p "$prompt" --plugin-dir "$plugin_root" "${tool_flags[@]}" \
    --output-format json > "$out_dir/results/$stem.json" 2> "$out_dir/results/$stem.err"
)

snapshot > "$out_dir/results/$stem.after"
echo "done: $stem"
