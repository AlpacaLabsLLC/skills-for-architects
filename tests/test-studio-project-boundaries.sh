#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import json,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path('skills/receive/scripts').resolve()))
import workspaces as w
d=w.d
studio=json.loads(Path('skills/studio/host-contract.json').read_text())
project=json.loads(Path('skills/project/host-contract.json').read_text())
assert 'STUDIO.md' in studio['owned_records']
assert 'STUDIO.md' in project['non_owned_records']
assert 'PROJECT.md' in project['owned_records']
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp).resolve()
    before=list(root.iterdir())
    assert w.resolve_context({'path':str(root)})['type']=='no-context'
    assert list(root.iterdir())==before
    target=root/'Standalone'
    args={'target':str(target),'name':'Standalone','project_id':'S1','kind':'software','type':'internal','status':'archived','client_code':'INT','client':'Internal','vocabularies':{'phases':['main'],'scopes':['engineering'],'originators':['firm']},'dry_run':False}
    w.project_init(args)
    result=w.resolve_context({'path':str(target)})
    assert result['type']=='project' and result['studio_root'] is None and result['status']=='archived'
    assert not (target/'.mcp.json').exists()
    try: w.studio_init({'target':str(target/'Nested'),'name':'Invalid','dry_run':False})
    except d.DomainError as e: assert e.code=='nested_project'
    else: raise AssertionError('nested studio accepted')
# The host-specific conversation itself is verified in final host acceptance.
assert '../../rules/moments.md' in Path('skills/studio/SKILL.md').read_text()
assert '████' not in Path('skills/studio/SKILL.md').read_text()
PY
printf '%s\n' '✓ studio/project owners, standalone context and no implicit setup'
