#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json
from pathlib import Path
load=lambda p:json.loads(Path(p).read_text())
components={c['id']:c for c in load('corpus/components.json')['components']}
clusters={p.stem:load(p) for p in Path('clusters').glob('*.json')}
for source in load('corpus/sources/catalog.json')['sources']:
    for skill in source['existing_skills']:
        assert 'knowledge:nyc-sources' in components['skill:'+skill]['dependencies'],skill
assert components['knowledge:nyc-sources']['path']=='corpus/sources/catalog.json'
assert components['tool:source-health']['path']=='tools/integrations/source-health.mjs'
health=next(i for i in load('tools/integrations/catalog.json')['integrations'] if i['id']=='integration:public-source-health')
assert health['runtime']=='node>=18' and health['hosted_binding']=='not-implemented'
assert components['tool:source-health']['execution']=='local-node'
for key in ['site-zoning','programming']:
    c=clusters[key]
    assert 'knowledge:nyc-sources' in c['members']
    assert c['coverage']['sources_indexed'] and c['coverage']['jurisdictions']==['jurisdiction:us-ny-nyc']
assert not clusters['due-diligence']['coverage']['sources_indexed']
assert 'tool:source-health' in clusters['site-zoning']['members']
assert 'knowledge:astm-e84-reference' in clusters['specifications']['members']
assert len({c['coverage']['limitations'] for c in clusters.values()})==len(clusters)
assert all(not c['coverage']['workflow_validated'] for c in clusters.values())
print('source component dependencies, limited coverage and execution distinctions verified')
PY
