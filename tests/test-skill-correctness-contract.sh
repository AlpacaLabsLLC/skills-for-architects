#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"

if rg -n 'FLOAT' \
  "${repo_root}/skills/occupancy-calculator/SKILL.md" \
  "${repo_root}/skills/workplace-programmer/SKILL.md"; then
  echo "legacy FLOAT branding remains" >&2
  exit 1
fi

for skill in environmental-analysis spec-writer occupancy-calculator; do
  file="${repo_root}/skills/${skill}/SKILL.md"
  grep -q 'architecture-studio:requires-disclaimer' "${file}"
done

product="${repo_root}/skills/product-research/SKILL.md"
grep -q 'Never fill price, availability, lead time, dimensions, finishes, certifications, or other purchasing facts from model memory' "${product}"
grep -q 'Not verified' "${product}"

occupancy="${repo_root}/skills/occupancy-calculator/SKILL.md"
grep -A8 '^allowed-tools:' "${occupancy}" | grep -q 'WebSearch'
grep -A8 '^allowed-tools:' "${occupancy}" | grep -q 'WebFetch'
# Current source interpretation has no bundled regulatory table or numeric fallback.
[ ! -e "${repo_root}/skills/occupancy-calculator/data/occupancy-load-factors.json" ]
[ ! -e "${repo_root}/skills/occupancy-calculator/data/use-groups.json" ]
grep -q 'source catalog' "${occupancy}"
grep -q 'dependent conclusions unresolved' "${occupancy}"
if rg -n '≤49|50-500|501-1000|1001\+|0\.2"/occupant|0\.15"/occupant' "${occupancy}"; then
  echo "occupancy skill contains uncited jurisdiction-sensitive egress constants" >&2
  exit 1
fi

resize="${repo_root}/skills/resize-images/SKILL.md"
grep -q 'resize_images.resize' "${resize}"
if grep -q '^```python$' "${resize}"; then
  echo "resize-images still embeds Python" >&2
  exit 1
fi
grep -q 'Do not dump the layout/background table' "${repo_root}/skills/slide-deck-generator/SKILL.md"

# These assertions protect host instructions, not model routing or actual network execution.
adapter="${repo_root}/docs/host-adapters.md"
grep -q "try the host's page-fetch/retrieval capability first" "${adapter}"
grep -q 'Use search' "${adapter}"
grep -q 'interactive browsing when the task needs interaction' "${adapter}"
grep -q 'A failed shell request is not proof that host fetching failed' "${adapter}"
grep -q 'not-attempted, proxy/policy rejection, robots/anti-bot blocking' "${adapter}"
grep -q 'observed origin HTTP 404' "${adapter}"
grep -q 'supplied-link denominator separate from replacement search' "${adapter}"

echo "skill correctness contract: ok"
