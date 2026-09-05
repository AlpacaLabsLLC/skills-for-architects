#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import copy, importlib.util, json, tempfile
from pathlib import Path

def module(path):
    spec=importlib.util.spec_from_file_location(Path(path).stem,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

audit=module('tools/validators/ffe_audit.py').audit
sample={'schema_version':1,'mode':'snapshot','started_at':'2026-09-05T10:00:00Z','items':[{'item_id':'item-1','revision':1,'tag':'AP-01','fields':{'manufacturer':'Maker','model':'M1'}}],'observations':[{'item_id':'item-1','field':field,'value':value,'status':'observed','source':{'reference':'sources/product.pdf','locator':'page 1'},'observed_at':'2026-09-04T10:00:00Z'} for field,value in [('manufacturer','Maker'),('model','M1')]]}
assert audit(sample)['status']=='matches-supplied-observations'
assert not audit(sample)['retrieval_performed']
x=copy.deepcopy(sample);x['mode']='live';assert 'stale-observation' in {f['code'] for f in audit(x)['findings']}
x=copy.deepcopy(sample);x['observations'][0]['value']='Reseller';assert audit(x)['findings'][0]['code']=='discrepancy';assert x['items'][0]['fields']['manufacturer']=='Maker'
x=copy.deepcopy(sample);x['observations'][0]['status']='unavailable';assert 'source-unavailable' in {f['code'] for f in audit(x)['findings']}
x=copy.deepcopy(sample);x['observations'].append(dict(x['observations'][0],value='Other'));assert 'conflicting-sources' in {f['code'] for f in audit(x)['findings']}
x=copy.deepcopy(sample);x['items'].append(x['items'][0])
try:audit(x)
except ValueError:pass
else:raise AssertionError('duplicate accepted')
for patch in ({'schema_version':True}, {'started_at':'2099-01-01T00:00:00Z'}, {'started_at':'2026-09-05T10:00:00'}):
    bad=copy.deepcopy(sample);bad.update(patch)
    try:audit(bad)
    except ValueError:pass
    else:raise AssertionError('invalid audit version/time accepted')
bad=copy.deepcopy(sample);bad['observations']=[]
assert audit(bad)['status']=='findings' and audit(bad)['compared_fields']==0
intake=module('tools/transformers/ffe_intake.py').manifest
with tempfile.TemporaryDirectory() as folder:
    root=Path(folder);(root/'PROJECT.md').write_text('# Synthetic project\n');(root/'source.csv').write_text('Tag,Model\nAP-01,M1\n')
    request={'schema_version':1,'mode':'one-off','job_id':'synthetic-1','sources':[{'id':'source-1','kind':'file','reference':'source.csv','sha256':None,'status':'available'}],'selected_tags':['AP-01'],'template':None,'record_basis':None,'supersedes':None,'actor':'test','reason':'explicit synthetic input'}
    out=intake(root,request);target=root/out['path'];before=target.read_bytes();assert not out['adoption_performed'];assert len(json.loads(before)['sources'][0]['sha256'])==64
    try:intake(root,request)
    except ValueError:pass
    else:raise AssertionError('overwrite accepted')
    assert target.read_bytes()==before
    changed=copy.deepcopy(request);changed['job_id']='synthetic-2';changed['supersedes']='synthetic-1';assert intake(root,changed)['path'].endswith('synthetic-2/input-manifest.json')
    bad=copy.deepcopy(request);bad['job_id']='bad';bad['sources'][0]['reference']='../outside.csv'
    try:intake(root,bad)
    except ValueError:pass
    else:raise AssertionError('traversal accepted')
    assert not (root/'ffe/jobs/bad').exists()
print('FF&E audit and intake negative contracts passed')
PY
