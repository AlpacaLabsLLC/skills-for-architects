#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import importlib.util, tempfile, pathlib, copy, json, hashlib
spec=importlib.util.spec_from_file_location('records','tools/workspace/ffe_records.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
def tree(root): return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
def refuses(root, fn):
    before=tree(root)
    try: fn()
    except (ValueError,FileExistsError): pass
    else: raise AssertionError('operation should refuse')
    assert tree(root)==before, 'failed operation changed files'
with tempfile.TemporaryDirectory() as td:
    p=pathlib.Path(td); (p/'PROJECT.md').write_text('# Synthetic project\n')
    a=r.write_revision(p,dict(name='Appliances',actor='Synthetic tester',reason='Explicit adoption',items=[dict(tag='AP-01',fields={'model':'A','finish':'white','hyperlink':{'label':'Source','url':'https://example.invalid/a'}},provenance={'model':{'source':'source.pdf','status':'supplied'}}),dict(tag='AP-02',fields={'price':None})]))
    sid=a['schedule_id']; assert a['revision']==1
    assert list(p.rglob('schedule.md')) and not list((p/'ffe'/'schedules').rglob('*.json'))
    change=dict(name='Appliances',actor='Tester',reason='Selected finish',items=copy.deepcopy(a['items']))
    change['items'][0]['fields']['finish']='black'
    b=r.write_revision(p,change,sid,1)
    assert b['items'][0]['revision']==2 and b['items'][1]['revision']==1
    assert b['item_refs'][1]==a['item_refs'][1]
    refuses(p,lambda:r.write_revision(p,change,sid,1))
    incoming=copy.deepcopy(change); incoming['items']=copy.deepcopy(a['items']); incoming['items'][0]['fields']['model']='B'
    merge=r.reconcile(p,sid,1,incoming)
    assert not merge['conflicts'] and merge['proposal']['items'][0]['fields']==dict(a['items'][0]['fields'],finish='black',model='B')
    incoming['items'][0]['fields']['finish']='red'
    assert r.reconcile(p,sid,1,incoming)['conflicts']
    change['items']=copy.deepcopy(b['items'])
    removed=copy.deepcopy(change); removed['items']=removed['items'][:1]
    refuses(p,lambda:r.write_revision(p,removed,sid,2))
    duplicate=copy.deepcopy(change); duplicate['items'][1]['tag']='AP-01'
    refuses(p,lambda:r.write_revision(p,duplicate,sid,2))
    approved=copy.deepcopy(change); approved['lifecycle']='approved'
    refuses(p,lambda:r.write_revision(p,approved,sid,2))
    retag=copy.deepcopy(change); retag['items'][0]['tag']='AP-10'
    c=r.write_revision(p,retag,sid,2); assert c['items'][0]['item_id']==a['items'][0]['item_id']
    (p/'source.xlsx').write_bytes(b'Synthetic native workbook bytes')
    before=tree(p)
    snap=r.snapshot(p,sid,'source.xlsx',phase='pre-edit',mapping={'Model':'model'},gaps=['formula extraction requires host'])
    r.recover(p,sid,snap['snapshot_id'],'restored.xlsx','native')
    assert (p/'restored.xlsx').read_bytes()==(p/'source.xlsx').read_bytes()
    refuses(p,lambda:r.recover(p,sid,snap['snapshot_id'],'restored.xlsx','native'))
    refuses(p,lambda:r.recover(p,sid,snap['snapshot_id'],'PROJECT.md','csv'))
    refuses(p,lambda:r.recover(p,sid,snap['snapshot_id'],'../escape.csv','csv'))
    outside=p/'outside'; outside.symlink_to('/tmp',target_is_directory=True)
    refuses(p,lambda:r.recover(p,sid,snap['snapshot_id'],'outside/escape.csv','csv'))
    latest=r.read_schedule(p,sid); assert latest==c
    itemfile=p/c['item_refs'][0]['path']; itemfile.write_text(itemfile.read_text().replace('black','rogue'))
    refuses(p,lambda:r.write_revision(p,change,sid,3))
print('PASS: adoption, Markdown authority, pinned items, revision integrity, three-way merge, conflicts, retag, approval, recovery, path safety')
PY
