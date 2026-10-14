#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

TEST_ROOT=$(mktemp -d)
trap 'rm -rf "$TEST_ROOT"' EXIT

PLUGIN_ROOT="$TEST_ROOT/plugin"
FAKE_BIN="$TEST_ROOT/bin"
mkdir -p "$PLUGIN_ROOT/.claude-plugin" "$FAKE_BIN"
printf '{"version":"1.4.0"}\n' > "$PLUGIN_ROOT/.claude-plugin/plugin.json"

cat > "$FAKE_BIN/curl" <<'SH'
#!/usr/bin/env bash
printf 'called %s\n' "$*" >> "$CURL_MARKER"
if [ "${CURL_FAIL:-0}" = 1 ]; then exit 7; fi
if [ -n "${CURL_RESPONSE:-}" ]; then
  printf '%s\n' "$CURL_RESPONSE"
else
  printf '%s\n' '{"version":"v9.9.9"}'
fi
SH
chmod +x "$FAKE_BIN/curl"

run_hook() {
  response=${2:-'{"version":"v9.9.9"}'}
  PATH="$FAKE_BIN:$PATH" \
  CLAUDE_PLUGIN_ROOT="$PLUGIN_ROOT" \
  CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA_FIXTURE:-$TEST_ROOT/plugin-data-new}" \
  ARCHITECTURE_STUDIO_STATE_DIR="$1" \
  CURL_MARKER="$1/curl-called" \
  CURL_RESPONSE="$response" \
  CURL_FAIL="${3:-0}" \
  ./hooks/version-check.sh
}

preference() {
  python3 - "$ARCHITECTURE_STUDIO_STATE_DIR" "$1" <<'PREFPY'
import importlib.util,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location('preference',Path('skills/studio/scripts/update_preference.py'))
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
result=module.dispatch('update_preference.'+sys.argv[2],{'state_directory':sys.argv[1]})
print('enabled' if result['enabled'] else 'disabled')
PREFPY
}

# Preference changes are deterministic and status is read-only. On is the default.
PREF="$TEST_ROOT/preference"
[ "$(CLAUDE_PLUGIN_DATA="$TEST_ROOT/plugin-data-old" ARCHITECTURE_STUDIO_STATE_DIR="$PREF" preference status)" = enabled ]
[ ! -e "$PREF" ]
[ "$(CLAUDE_PLUGIN_DATA="$TEST_ROOT/plugin-data-old" ARCHITECTURE_STUDIO_STATE_DIR="$PREF" preference disable)" = disabled ]
[ -f "$PREF/.architecture-studio-update-check-disabled" ]
[ ! -e "$TEST_ROOT/plugin-data-old/.architecture-studio-update-check-disabled" ]
mode=$(python3 -c 'import os,sys; print(oct(os.stat(sys.argv[1]).st_mode & 0o777)[2:])' "$PREF/.architecture-studio-update-check-disabled")
[ "$mode" = 600 ]
printf 'checked_at=0\nremote=9.9.9\nnudged_for=\n' > "$PREF/.architecture-studio-version-check"
[ "$(CLAUDE_PLUGIN_DATA="$TEST_ROOT/plugin-data-new" ARCHITECTURE_STUDIO_STATE_DIR="$PREF" preference enable)" = enabled ]
[ ! -e "$PREF/.architecture-studio-version-check" ]
[ ! -e "$PREF/.architecture-studio-update-check-disabled" ]

# Opt out under the retired identifier's plugin-data root, then run the hook
# under the new identifier's distinct root. Both must use the stable state root;
# with both switches off the hook does no I/O.
CONTINUITY="$TEST_ROOT/continuity"
CLAUDE_PLUGIN_DATA_FIXTURE="$TEST_ROOT/plugin-data-new"
[ "$(CLAUDE_PLUGIN_DATA="$TEST_ROOT/plugin-data-old" ARCHITECTURE_STUDIO_STATE_DIR="$CONTINUITY" preference disable)" = disabled ]
[ -z "$(AS_TELEMETRY_DISABLED=1 run_hook "$CONTINUITY")" ]
[ ! -e "$CONTINUITY/.architecture-studio-version-check" ]
[ ! -e "$CONTINUITY/curl-called" ]
[ ! -e "$TEST_ROOT/plugin-data-old/.architecture-studio-update-check-disabled" ]

# Both environment opt-outs: no directory, cache, or request.
OFF="$TEST_ROOT/off"
[ -z "$(AS_UPDATE_CHECK_DISABLED=1 AS_TELEMETRY_DISABLED=1 run_hook "$OFF")" ]
[ ! -e "$OFF" ]

# Usage ping: a random install ID is created once, reused, and dropped by the opt-out.
PING="$TEST_ROOT/ping"
mkdir -p "$PING"
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$PING/.architecture-studio-version-check"
run_hook "$PING" >/dev/null
id=$(cat "$PING/.architecture-studio-install-id")
[[ $id =~ ^[0-9a-f]{32}$ ]]
grep -qxF "called -fsS --max-time 2 https://version.alpa.llc/?id=$id&v=1.4.0" "$PING/curl-called"
mode=$(python3 -c 'import os,sys; print(oct(os.stat(sys.argv[1]).st_mode & 0o777)[2:])' "$PING/.architecture-studio-install-id")
[ "$mode" = 600 ]
rm -f "$PING/curl-called"
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$PING/.architecture-studio-version-check"
[ -z "$(AS_UPDATE_CHECK_DISABLED=1 run_hook "$PING")" ]
grep -qxF "called -fsS --max-time 2 https://version.alpa.llc/?id=$id&v=1.4.0" "$PING/curl-called"
rm -f "$PING/curl-called"
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$PING/.architecture-studio-version-check"
AS_TELEMETRY_DISABLED=1 run_hook "$PING" >/dev/null
grep -qxF "called -fsS --max-time 2 https://version.alpa.llc/" "$PING/curl-called"

# First session seeds silently without curl, independent of welcome state.
FIRST="$TEST_ROOT/first"
mkdir -p "$FIRST"
touch "$FIRST/.architecture-studio-welcomed"
[ -z "$(run_hook "$FIRST")" ]
[ -f "$FIRST/.architecture-studio-version-check" ]
[ ! -e "$FIRST/curl-called" ]

# Stale cache and newer remote nudges once.
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$FIRST/.architecture-studio-version-check"
NEW=$(run_hook "$FIRST")
printf '%s' "$NEW" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "9.9.9" in d["systemMessage"]; assert "1.4.0" in d["systemMessage"]; assert "do not bring this up unprompted" in d["hookSpecificOutput"]["additionalContext"]'
grep -q '^nudged_for=9.9.9$' "$FIRST/.architecture-studio-version-check"
[ -f "$FIRST/curl-called" ]

rm -f "$FIRST/curl-called"
[ -z "$(run_hook "$FIRST")" ]
[ ! -e "$FIRST/curl-called" ]

# Equal and older remote versions stay silent.
for remote in v1.4.0 v1.3.9; do
  CASE_DIR="$TEST_ROOT/${remote#v}"
  mkdir -p "$CASE_DIR"
  printf 'checked_at=0\nremote=\nnudged_for=\n' > "$CASE_DIR/.architecture-studio-version-check"
  [ -z "$(run_hook "$CASE_DIR" "{\"version\":\"$remote\"}")" ]
done

# Four-segment content patches: a missing fourth segment compares as zero.
for spec in 1.5.0:v1.5.0.1:nudge 1.5.0.1:v1.5.0:silent 1.5.0.1:v1.5.1:nudge 1.5.0.1:v1.5.0.1:silent; do
  IFS=: read -r local_v remote expect <<< "$spec"
  CASE_DIR="$TEST_ROOT/patch-$local_v-${remote#v}"
  mkdir -p "$CASE_DIR"
  printf 'checked_at=0\nremote=\nnudged_for=\n' > "$CASE_DIR/.architecture-studio-version-check"
  printf '{"version":"%s"}\n' "$local_v" > "$PLUGIN_ROOT/.claude-plugin/plugin.json"
  OUT=$(run_hook "$CASE_DIR" "{\"version\":\"$remote\"}")
  if [ "$expect" = nudge ]; then
    printf '%s' "$OUT" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert sys.argv[1] in d["systemMessage"]; assert sys.argv[2] in d["systemMessage"]' "${remote#v}" "$local_v"
    grep -q "^nudged_for=${remote#v}\$" "$CASE_DIR/.architecture-studio-version-check"
  else
    [ -z "$OUT" ]
  fi
done
printf '{"version":"1.4.0"}\n' > "$PLUGIN_ROOT/.claude-plugin/plugin.json"

# Failure and malformed state are silent and always exit zero.
FAIL_DIR="$TEST_ROOT/fail"
mkdir -p "$FAIL_DIR"
printf 'checked_at=banana\nremote=bad\nnudged_for=bad\n' > "$FAIL_DIR/.architecture-studio-version-check"
[ -z "$(run_hook "$FAIL_DIR" '{}' 1)" ]
grep -Eq '^checked_at=[0-9]+$' "$FAIL_DIR/.architecture-studio-version-check"

MALFORMED="$TEST_ROOT/malformed"
mkdir -p "$MALFORMED"
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$MALFORMED/.architecture-studio-version-check"
[ -z "$(run_hook "$MALFORMED" 'not-json')" ]

# Concurrent stale checks may duplicate a bounded request, but atomic cache
# replacement must always leave one complete, parseable three-line record.
CONCURRENT="$TEST_ROOT/concurrent"
mkdir -p "$CONCURRENT"
printf 'checked_at=0\nremote=\nnudged_for=\n' > "$CONCURRENT/.architecture-studio-version-check"
run_hook "$CONCURRENT" >/dev/null & first_pid=$!
run_hook "$CONCURRENT" >/dev/null & second_pid=$!
wait "$first_pid" "$second_pid"
python3 - "$CONCURRENT/.architecture-studio-version-check" <<'PY'
from pathlib import Path
import re, sys
text = Path(sys.argv[1]).read_text()
assert re.fullmatch(r'checked_at=\d+\nremote=\d+\.\d+\.\d+\nnudged_for=(?:\d+\.\d+\.\d+)?\n', text), text
PY

# Native MCP does not install lifecycle hooks; the installed-package helper contract remains tested above.
python3 - <<'PYTEST'
from pathlib import Path
import json
studio=Path('skills/studio/SKILL.md').read_text()
assert 'MCP instruction delivery does not install lifecycle hooks' in studio
assert 'report it unavailable here without inspecting or creating package state' in studio
assert 'do not invoke installed-package update operations through this workflow' in studio
declaration=json.loads(Path('skills/studio/host-contract.json').read_text())
assert declaration['execution']['model']=='harness-native'
assert not any(operation.startswith('update_preference.') for operation in declaration['execution']['operations'])
registry=json.loads(Path('tools/runner/operations.json').read_text())
for command in ('status','enable','disable'):
    assert any(row['id']=='update_preference.'+command for row in registry['operations'])
governance=Path('docs/data-governance.md').read_text()
assert 'update checking is on by default' in governance
assert 'anonymous usage ping, on by default' in governance
assert 'AS_UPDATE_CHECK_DISABLED=1' in governance
assert 'AS_TELEMETRY_DISABLED=1' in governance
assert 'available only on Claude Code' in governance
assert 'The Codex package does not install that lifecycle hook' in governance
assert 'do not write an enablement marker or cache' in governance
PYTEST
printf '%s\n' '✓ update check and usage ping are on by default, throttled, fail-silent, and honor their opt-outs; install ID persists'
