#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json,re
from pathlib import Path
skill=Path('skills/studio/SKILL.md').read_text()
setup=skill[skill.index('## Setup'):skill.index('## Projects and settings')]
# The four decisions appear in order, after location and name.
steps=['**Location and name.**','**Governance:','**Practice areas:','**Memory:','**Tooling:']
positions=[setup.index(s) for s in steps]
assert positions==sorted(positions), positions
# Existing guarantees: tools-only path, policy question, single approval gate, Codex parity.
for phrase in ('tools only','Tools only writes nothing','ask once whether the user has an AI-use policy',
               'One concrete setup gate covers all of it; nothing is written before it',
               'Codex asks the same questions','never walked through again or migrated automatically'):
    assert phrase.lower() in setup.lower(), phrase
# The template carries one practice-areas marker pair with the documented columns.
template=Path('studio/templates/studio/STUDIO.md').read_text()
assert template.count('<!-- practice-areas:start -->')==1 and template.count('<!-- practice-areas:end -->')==1
block=template.split('<!-- practice-areas:start -->')[1].split('<!-- practice-areas:end -->')[0]
assert '| Cluster | Practice area |' in block and '{{PRACTICE_AREA_ROWS}}' in block
# Every shipped cluster linked from the practice-areas guide exists.
clusters={json.loads(p.read_text())['id'] for p in Path('clusters').glob('*.json')}
linked={'cluster:'+m for m in re.findall(r'\(\.\./clusters/([a-z-]+)\.json\)',Path('docs/practice-clusters.md').read_text())}
assert linked and linked<=clusters, linked-clusters
assert 'practice-areas table' in Path('docs/workspace-model.md').read_text()
PY
printf '%s\n' '✓ studio setup walks governance, practice areas, memory and tooling with one approval gate'
