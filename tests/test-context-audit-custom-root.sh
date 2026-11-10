#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
tmp="$(mktemp -d)"
trap 'rm -rf "${tmp}"' EXIT

mkdir -p "${tmp}/fixture-root/example-skill"
cat > "${tmp}/fixture-root/example-skill/SKILL.md" <<'EOF'
---
name: example-skill
description: A synthetic fixture.
---
Synthetic body.
EOF

output="$(cd "${tmp}" && "${repo_root}/scripts/audit-skill-context.sh" fixture-root)"
printf '%s\n' "${output}" | awk -F '\t' '$1 == "example-skill" { found = 1 } END { exit !found }'
if printf '%s\n' "${output}" | awk -F '\t' '$1 == "fixture-root/example-skill" { found = 1 } END { exit !found }'; then
  echo 'audit output includes the custom root path instead of the skill name' >&2
  exit 1
fi

echo 'context audit custom-root contract: ok'
