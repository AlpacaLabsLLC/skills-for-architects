#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

expected_skill_count=$(python3 -c 'import json; print(sum(c["category"] == "skills" for c in json.load(open("corpus/components.json"))["components"]))')
expected_agent_count=$(python3 -c 'import json; print(sum(k.startswith("agent:") for k in json.load(open("corpus/host-contracts.json"))["components"]))')

[ ! -e agents/README.md ]
[ -f docs/agents.md ]
[ "$(find agents -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')" = "$expected_agent_count" ]
[ "$(find skills -mindepth 2 -maxdepth 2 -type f -name SKILL.md | wc -l | tr -d ' ')" = "$expected_skill_count" ]
[ "$(find skills -mindepth 2 -type f -name SKILL.md | wc -l | tr -d ' ')" = "$expected_skill_count" ]

# Actual native installation is reserved for explicit final host acceptance.
# Ordinary engineering checks validate source inventory only.
if [ "${AS_FINAL_HOST_ACCEPTANCE:-0}" = 1 ] && command -v claude >/dev/null 2>&1; then
  test_root=$(mktemp -d)
  trap 'rm -rf "$test_root"' EXIT
  test_home="$test_root/home"
  test_config="$test_root/config"
  test_state="$test_root/state"
  mkdir -p "$test_home" "$test_config" "$test_state"

  env HOME="$test_home" \
    CLAUDE_CONFIG_DIR="$test_config" \
    ARCHITECTURE_STUDIO_STATE_DIR="$test_state" \
    claude plugin marketplace add "$PWD" >/dev/null
  env HOME="$test_home" \
    CLAUDE_CONFIG_DIR="$test_config" \
    ARCHITECTURE_STUDIO_STATE_DIR="$test_state" \
    claude plugin install as@skills-for-architects >/dev/null
  details=$(env HOME="$test_home" \
    CLAUDE_CONFIG_DIR="$test_config" \
    ARCHITECTURE_STUDIO_STATE_DIR="$test_state" \
    claude plugin details as@skills-for-architects)

  printf '%s\n' "$details" | grep -q "^  Skills ($expected_skill_count)  "
  printf '%s\n' "$details" | grep -q "^  Agents ($expected_agent_count)  "
  printf '%s\n' "$details" | grep -q '^  Hooks (3)  SessionStart, PostToolUse, PreToolUse'
  printf '%s\n' "$details" | grep -q '^  MCP servers (0)$'
  ! printf '%s\n' "$details" | grep -q 'Agents (.*README'
fi

echo "✓ source component inventory contains $expected_skill_count skills, $expected_agent_count agents, and 4 handlers across 3 hook events"
