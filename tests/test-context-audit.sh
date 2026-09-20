#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
first="$(mktemp)"
second="$(mktemp)"
trap 'rm -f "${first}" "${second}"' EXIT

"${repo_root}/scripts/audit-skill-context.sh" > "${first}"
LC_ALL=POSIX LANG=POSIX "${repo_root}/scripts/audit-skill-context.sh" > "${second}"
cmp "${first}" "${second}"

expected="$(( $(find "${repo_root}/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ') + 1 ))"
actual="$(wc -l < "${first}" | tr -d ' ')"
test "${actual}" = "${expected}"

head -1 "${first}" | grep -q $'^skill\tdescription_chars\tdescription_words\tdescription_lines\tdescription_est_tokens\tbody_chars\tbody_words\tbody_lines$'
grep -q '^occupancy-calculator[[:space:]]' "${first}"
awk -F '\t' 'NR > 1 { if ($2 < 1 || $5 < 1 || $6 < 1 || $8 < 1) exit 1 }' "${first}"

# Historical optimization reports are dated evidence, not a live size quota.
# Quoted/folded description parsing has separate fixture coverage.
echo "context audit contract: ok"
