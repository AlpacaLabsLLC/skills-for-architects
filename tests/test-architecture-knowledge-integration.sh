#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json,re
from pathlib import Path
root=Path.cwd()
paths=['skills/architecture-knowledge/SKILL.md','skills/spec-writer/SKILL.md','skills/epd-to-spec/SKILL.md','rules/csi-formatting.md','rules/terminology.md','docs/source-integration-contracts.md']
for rel in paths:
    p=root/rel
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('https:', '#')): continue
        path=target.split('#')[0]
        assert (p.parent/path).exists(), (rel,target)
declaration=json.loads((root/'skills/architecture-knowledge/host-contract.json').read_text())
assert not declaration['owned_records'],'Terminology must not own project writes'
assert 'research' in {m['mode'] for m in declaration['modes']},'Original-source interpretation needs retrieval mode'
assert 'record-write' not in {m['mode'] for m in declaration['modes']}
print('PASS: source consumers resolve current owners and terminology declares retrieval without record ownership')
PY
