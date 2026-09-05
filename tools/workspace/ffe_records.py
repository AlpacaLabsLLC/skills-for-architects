#!/usr/bin/env python3
"""Project-owned FF&E schedule revisions. Standard-library only; no workbook engine."""
import argparse
import copy
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def safe_path(root, *parts):
    root = Path(root).resolve()
    if any('..' in Path(part).parts for part in parts):
        raise ValueError('Parent traversal is not supported')
    path = root.joinpath(*parts)
    if not path.is_relative_to(root):
        raise ValueError('Path escapes project')
    for p in [path, *path.parents]:
        if p.is_symlink():
            raise ValueError('Symlink paths are not supported')
    return path


def project_root(project):
    if Path(project).is_symlink():
        raise ValueError('Project root must not be a symlink')
    root = safe_path(project)
    if not (root / 'PROJECT.md').is_file():
        raise ValueError('Explicit project root must contain PROJECT.md')
    return root


def identity(value):
    if str(uuid.UUID(value)) != value:
        raise ValueError('Identity must be a canonical UUID')
    return value


def schedule_path(project, schedule_id):
    return safe_path(project_root(project), 'ffe', 'schedules', identity(schedule_id))


def signed(record):
    record = copy.deepcopy(record)
    record.pop('hash', None)
    record['hash'] = digest(encode(record))
    return record


def validate_items(items, previous=None):
    if not isinstance(items, list) or not items:
        raise ValueError('A schedule requires at least one item')
    old = {i['item_id']: i for i in (previous or [])}
    result, ids, tags = [], set(), set()
    for raw in items:
        if not isinstance(raw, dict) or set(raw) - {'item_id','revision','tag','fields','provenance','decision_refs'}:
            raise ValueError('Unknown item property')
        item = copy.deepcopy(raw)
        iid = identity(item.get('item_id', str(uuid.uuid4())))
        tag = item.get('tag')
        if not isinstance(tag, str) or not tag.strip() or tag in tags or iid in ids:
            raise ValueError('Missing or duplicate item identity/tag')
        for key in ('fields','provenance'):
            if not isinstance(item.get(key, {}), dict):
                raise ValueError(key + ' must be an object')
        refs = item.get('decision_refs', [])
        if not isinstance(refs, list) or any(not isinstance(r, str) or r.startswith('/') or '..' in Path(r).parts for r in refs):
            raise ValueError('Decision references must be project-relative links')
        provenance = item.get('provenance', {})
        if any(not isinstance(e, dict) or e.get('status') not in ('supplied','verified','unknown','inferred') or set(e) - {'status','source','retrieved_at','note'} or any(not isinstance(v,str) for v in e.values()) for e in provenance.values()):
            raise ValueError('Provenance requires status and bounded source/retrieval/note evidence')
        provenance = {k: provenance.get(k, {'status':'unknown'}) for k in item.get('fields', {})}
        item.update(item_id=iid, fields=item.get('fields', {}), provenance=provenance, decision_refs=refs)
        item.pop('revision', None)
        before = copy.deepcopy(old.get(iid, {}))
        rev = before.pop('revision', 0)
        item['revision'] = rev if before == item else rev + 1
        ids.add(iid); tags.add(tag); result.append(item)
    encode(result)
    return result


def markdown(record, title):
    return (f"# {title}\n\nRevision: {record['revision']} · Actor: {record['actor']}\n\nReason: {record['reason']}\n\nImmutable revision; edit by creating a new revision.\n\n```json\n" + encode(record).decode() + "```\n").encode()


def parse_record(path):
    text = path.read_text()
    if text.count('```json\n') != 1 or not text.endswith('```\n'):
        raise ValueError('Malformed typed Markdown record')
    return json.loads(text.split('```json\n')[1][:-4])


def read_schedule(project, schedule_id, revision=None):
    root = project_root(project)
    directory = schedule_path(root, schedule_id) / 'revisions'
    paths = sorted(p for p in directory.glob('*') if not p.name.startswith('.'))
    if not paths:
        raise ValueError('Schedule does not exist')
    previous = None
    for n, path in enumerate(paths, 1):
        safe_path(root, *path.relative_to(root).parts)
        if path.name != f'{n:06d}' or not path.is_dir():
            raise ValueError('Missing or unexpected revision directory')
        safe_path(root, * (path / 'schedule.md').relative_to(root).parts)
        stored = parse_record(path / 'schedule.md')
        if set(stored) != {'schema_version','schedule_id','name','revision','created_at','actor','reason','lifecycle','approval_refs','previous_hash','source','item_refs','hash'} or stored['schema_version'] != 1:
            raise ValueError('Invalid schedule envelope')
        if stored != signed(stored) or stored.get('revision') != n or stored.get('schedule_id') != schedule_id or stored.get('previous_hash') != (previous['hash'] if previous else None):
            raise ValueError('Corrupt schedule revision/hash chain')
        record = copy.deepcopy(stored)
        record['items'] = []
        for ref in stored['item_refs']:
            itempath = safe_path(root, ref['path'])
            expected_path = safe_path(root,'ffe','items',identity(ref['item_id']),'revisions',f"{ref['revision']:06d}.md")
            if itempath != expected_path:
                raise ValueError('Invalid item reference boundary')
            item = parse_record(itempath)
            if set(item) != {'schema_version','item_id','revision','tag','fields','provenance','decision_refs','actor','reason','created_at','previous_hash','hash'} or item['schema_version'] != 1:
                raise ValueError('Invalid item envelope')
            if item != signed(item) or item['hash'] != ref['hash'] or item['item_id'] != ref['item_id'] or item['revision'] != ref['revision']:
                raise ValueError('Corrupt item reference/hash')
            record['items'].append({k:v for k,v in item.items() if k in ('item_id','revision','tag','fields','provenance','decision_refs')})
        validate_items(record['items'])
        previous = record
        if revision == n:
            return record
    if revision is not None:
        raise ValueError('Requested revision is absent')
    return previous


@contextmanager
def locked(root):
    base = safe_path(root, 'ffe')
    base.mkdir(exist_ok=True)
    lock = base / '.write-lock'
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError('Another writer or interrupted operation holds the FF&E lock')
    os.close(fd)
    try:
        yield
    finally:
        lock.unlink()


def write_revision(project, payload, schedule_id=None, expected=None, allow_remove=False):
    root = project_root(project)
    if not isinstance(payload.get('source', {}), dict):
        raise ValueError('Source must be an evidence object')
    with locked(root):
        previous = read_schedule(root, schedule_id) if schedule_id else None
        if previous and expected != previous['revision']:
            raise ValueError('Stale revision: reread and reconcile before writing')
        global_items = []
        global_refs = {}
        for raw in payload['items']:
            if raw.get('item_id'):
                iid = identity(raw['item_id'])
                itemdir = safe_path(root,'ffe','items',iid,'revisions')
                files = sorted(itemdir.glob('*.md'))
                if not files:
                    raise ValueError('Unknown or foreign item identity; new items must omit item_id')
                if files:
                    latest = None
                    for number, file in enumerate(files,1):
                        safe_path(root, *file.relative_to(root).parts)
                        item = parse_record(file)
                        if file.name != f'{number:06d}.md' or item != signed(item) or item['previous_hash'] != (latest['hash'] if latest else None):
                            raise ValueError('Corrupt global item revision chain')
                        latest = item
                    committed_paths = set()
                    for schedulefile in safe_path(root,'ffe','schedules').glob('*/revisions/*/schedule.md'):
                        if not schedulefile.parent.name.isdigit(): continue
                        owner = parse_record(schedulefile)
                        if owner != signed(owner): raise ValueError('Corrupt schedule while resolving item ownership')
                        committed_paths.update(ref['path'] for ref in owner['item_refs'])
                    if str(files[-1].relative_to(root)) not in committed_paths:
                        raise ValueError('Uncommitted item revision requires interrupted-operation review')
                    if raw.get('revision') != latest['revision']:
                        raise ValueError('Stale item revision: reconcile all affected schedules')
                    global_items.append({k:v for k,v in latest.items() if k in ('item_id','revision','tag','fields','provenance','decision_refs')})
                    global_refs[iid] = dict(item_id=iid,revision=latest['revision'],hash=latest['hash'],path=str(files[-1].relative_to(root)))
        items = validate_items(payload['items'], global_items)
        if previous:
            historical_ids = {ref['item_id'] for n in range(1, previous['revision'] + 1) for ref in read_schedule(root,schedule_id,n)['item_refs']}
            if ({i['item_id'] for i in items} - {i['item_id'] for i in previous['items']}) & historical_ids:
                raise ValueError('Removed identity cannot be silently reintroduced; review its retained history')
            removed = {i['item_id'] for i in previous['items']} - {i['item_id'] for i in items}
            if removed and not allow_remove:
                raise ValueError('Removal requires explicit --allow-remove')
        sid = schedule_id or str(uuid.uuid4())
        name = payload.get('name', previous['name'] if previous else None)
        if not isinstance(name, str) or not name.strip():
            raise ValueError('Schedule name is required')
        actor, reason = payload.get('actor'), payload.get('reason')
        if not all(isinstance(v,str) and v.strip() for v in (actor,reason)):
            raise ValueError('Actor and change reason are required')
        lifecycle = payload.get('lifecycle', 'proposed')
        if lifecycle not in ('proposed','selected','approved','superseded'):
            raise ValueError('Invalid lifecycle')
        approval_refs = payload.get('approval_refs', [])
        if not isinstance(approval_refs,list) or any(not isinstance(r,str) or r.startswith('/') or '..' in Path(r).parts for r in approval_refs):
            raise ValueError('Approval evidence must be project-relative')
        if lifecycle == 'approved' and not approval_refs:
            raise ValueError('Approved lifecycle requires explicit approval evidence')
        rev = previous['revision'] + 1 if previous else 1
        directory = schedule_path(root, sid) / 'revisions'
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f'{rev:06d}'
        temp = Path(tempfile.mkdtemp(prefix='.revision-', dir=directory))
        oldrefs = global_refs
        olditems = {i['item_id']:i for i in global_items}
        published_items = []
        committed = False
        refs=[]
        created = datetime.now(timezone.utc).isoformat()
        try:
            for item in items:
                if item == olditems.get(item['item_id']):
                    refs.append(oldrefs[item['item_id']]); continue
                itemrecord = signed(dict(item, schema_version=1, actor=actor, reason=reason, created_at=created,
                    previous_hash=oldrefs.get(item['item_id'],{}).get('hash')))
                filename = item['item_id'] + f"-r{item['revision']:06d}.md"
                (temp/filename).write_bytes(markdown(itemrecord, 'FF&E item ' + item['tag']))
                itemtarget = safe_path(root,'ffe','items',item['item_id'],'revisions',f"{item['revision']:06d}.md")
                itemtarget.parent.mkdir(parents=True,exist_ok=True)
                os.link(temp/filename,itemtarget)
                published_items.append(itemtarget)
                (temp/filename).unlink()
                refs.append(dict(item_id=item['item_id'],revision=item['revision'],hash=itemrecord['hash'],path=str(itemtarget.relative_to(root))))
            record = signed(dict(schema_version=1, schedule_id=sid, name=name, revision=rev,
                created_at=created, actor=actor, reason=reason, lifecycle=lifecycle, approval_refs=approval_refs,
                previous_hash=previous['hash'] if previous else None,
                source=payload.get('source', previous['source'] if previous else {}), item_refs=refs))
            (temp/'schedule.md').write_bytes(markdown(record,'FF&E schedule ' + name))
            for file in temp.iterdir():
                with file.open('rb') as handle: os.fsync(handle.fileno())
            os.rename(temp,target)
            committed = True
        finally:
            if not committed:
                for file in published_items: file.unlink()
            if temp.exists(): shutil.rmtree(temp)
        return read_schedule(root,sid)



MISSING = object()
def merge_value(base, current, incoming, path, conflicts):
    if incoming == base or incoming == current:
        return copy.deepcopy(current) if current is not MISSING else MISSING
    if current == base:
        return copy.deepcopy(incoming) if incoming is not MISSING else MISSING
    if all(isinstance(v, dict) for v in (base, current, incoming)):
        out = {}
        for key in sorted(set(base) | set(current) | set(incoming)):
            value = merge_value(base.get(key,MISSING), current.get(key,MISSING), incoming.get(key,MISSING), path + '/' + key, conflicts)
            if value is not MISSING:
                out[key] = value
        return out
    def display(v):
        return {'absent': True} if v is MISSING else v
    conflicts.append(dict(path=path, base=display(base), current=display(current), incoming=display(incoming)))
    return copy.deepcopy(current) if current is not MISSING else MISSING


def reconcile(project, schedule_id, base_revision, payload):
    base = read_schedule(project, schedule_id, base_revision)
    current = read_schedule(project, schedule_id)
    incoming = validate_items(payload['items'], base['items'])
    def mapping(items):
        return {i['item_id']: {k:v for k,v in i.items() if k != 'revision'} for i in items}
    conflicts = []
    merged = merge_value(mapping(base['items']), mapping(current['items']), mapping(incoming), '/items', conflicts)
    order = merge_value([i['item_id'] for i in base['items']], [i['item_id'] for i in current['items']], [i['item_id'] for i in incoming], '/item_order', conflicts)
    order += [iid for iid in merged if iid not in order]
    current_revs = {i['item_id']:i['revision'] for i in current['items']}
    for iid,item in merged.items():
        if iid in current_revs: item['revision'] = current_revs[iid]
    proposal = dict(name=current['name'], actor=payload.get('actor'), reason=payload.get('reason'), source=payload.get('source',current['source']), items=[merged[k] for k in order if k in merged])
    try:
        validate_items(proposal['items'], current['items'])
    except ValueError as error:
        conflicts.append({'path':'/items','error':str(error)})
    return dict(schedule_id=schedule_id, base_revision=base_revision, expected_revision=current['revision'], conflicts=conflicts,
        requires_review=True, removal_ids=sorted(set(mapping(current['items'])) - set(merged)), proposal=proposal)


def csv_bytes(record):
    fields = sorted({k for i in record['items'] for k in i['fields']})
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\r\n')
    writer.writerow(['item_id','item_revision','tag'] + ['field:' + k for k in fields])
    for i in record['items']:
        # JSON cells preserve null, numbers, strings, nested values and hyperlink objects losslessly.
        writer.writerow([i['item_id'], i['revision'], i['tag']] + [json.dumps(i['fields'][k], ensure_ascii=False, allow_nan=False) if k in i['fields'] else '' for k in fields])
    data = stream.getvalue().encode()
    if len(list(csv.reader(io.StringIO(data.decode())))) != len(record['items']) + 1:
        raise ValueError('CSV validation failed')
    return data


def snapshot(project, schedule_id, native=None, revision=None, phase='manual', mapping=None, gaps=None):
    root = project_root(project)
    record = read_schedule(root, schedule_id, revision)
    native_data = None
    if native:
        native_path = safe_path(root, native)
        if not native_path.is_file():
            raise ValueError('Native backup source must be a project-local file')
        native_data = native_path.read_bytes()
    if phase not in ('pre-edit','post-edit','manual'):
        raise ValueError('Invalid snapshot phase')
    with locked(root):
        directory = safe_path(root,'ffe','recovery',schedule_id)
        directory.mkdir(parents=True,exist_ok=True)
        temp = Path(tempfile.mkdtemp(prefix='.snapshot-',dir=directory))
        sid = str(uuid.uuid4())
        try:
            (temp/'schedule.json').write_bytes(encode(record))
            (temp/'schedule.csv').write_bytes(csv_bytes(record))
            if native_data is not None:
                (temp/'native-backup').write_bytes(native_data)
            receipt = dict(schema_version=1,snapshot_id=sid,schedule_id=schedule_id,revision=record['revision'],record_hash=record['hash'],
                created_at=datetime.now(timezone.utc).isoformat(),phase=phase,source_path=native,field_mapping=mapping or {},extraction_gaps=gaps or [],
                limitations=['CSV stores evaluated/structured fields; formulas, styles, images and workbook structure require the native backup or host reconstruction.'],
                files={p.name:digest(p.read_bytes()) for p in temp.iterdir()})
            (temp/'receipt.json').write_bytes(encode(receipt))
            os.rename(temp,directory/sid)
        finally:
            if temp.exists(): shutil.rmtree(temp)
    return receipt


def recover(project, schedule_id, snapshot_id, destination, kind='csv'):
    root = project_root(project)
    directory = safe_path(root,'ffe','recovery',identity(schedule_id),identity(snapshot_id))
    receipt = json.loads(safe_path(directory,'receipt.json').read_bytes())
    if receipt.get('schedule_id') != schedule_id or receipt.get('snapshot_id') != snapshot_id:
        raise ValueError('Snapshot identity mismatch')
    for name, checksum in receipt['files'].items():
        if name not in ('schedule.csv','schedule.json','native-backup') or digest(safe_path(directory,name).read_bytes()) != checksum:
            raise ValueError('Corrupt snapshot')
    source = {'csv':'schedule.csv','native':'native-backup','json':'schedule.json'}[kind]
    if source not in receipt['files']:
        raise ValueError('Requested recovery format is absent')
    target = safe_path(root,destination)
    if target == root or target.is_relative_to(root/'ffe') or target.name in ('PROJECT.md','STUDIO.md','AGENTS.md','CLAUDE.md'):
        raise ValueError('Recovery destination must be a new artifact outside canonical records')
    # Never replace a workbook, record, or previous recovery, including empty files.
    with target.open('xb') as out:
        out.write((directory/source).read_bytes())
    return dict(destination=str(target.relative_to(root)),snapshot_id=snapshot_id,revision=receipt['revision'],canonical_records_changed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['adopt','read','revise','reconcile','snapshot','recover','export'])
    parser.add_argument('--project',required=True)
    parser.add_argument('--schedule'); parser.add_argument('--input'); parser.add_argument('--revision',type=int)
    parser.add_argument('--expected-revision',type=int); parser.add_argument('--base-revision',type=int)
    parser.add_argument('--allow-remove',action='store_true'); parser.add_argument('--native'); parser.add_argument('--phase',default='manual')
    parser.add_argument('--snapshot'); parser.add_argument('--destination'); parser.add_argument('--kind',choices=['csv','native','json'],default='csv')
    args=parser.parse_args()
    try:
        payload=json.loads(Path(args.input).read_bytes()) if args.input else None
        if args.command=='adopt': result=write_revision(args.project,payload)
        elif args.command=='read': result=read_schedule(args.project,args.schedule,args.revision)
        elif args.command=='revise': result=write_revision(args.project,payload,args.schedule,args.expected_revision,args.allow_remove)
        elif args.command=='reconcile': result=reconcile(args.project,args.schedule,args.base_revision,payload)
        elif args.command=='snapshot': result=snapshot(args.project,args.schedule,args.native,args.revision,args.phase,(payload or {}).get('field_mapping'),(payload or {}).get('extraction_gaps'))
        elif args.command=='recover': result=recover(args.project,args.schedule,args.snapshot,args.destination,args.kind)
        else:
            root=project_root(args.project); target=safe_path(root,args.destination)
            if target.is_relative_to(root/'ffe') or target.name in ('PROJECT.md','STUDIO.md','AGENTS.md','CLAUDE.md'): raise ValueError('Export requires a new artifact path outside records')
            data = csv_bytes(read_schedule(root,args.schedule,args.revision))
            with target.open('xb') as out: out.write(data)
            result={'destination':str(target.relative_to(root))}
        print(encode(result).decode(),end='')
    except (ValueError,TypeError,KeyError,OSError,AttributeError) as error:
        parser.exit(1,f'FF&E operation refused: {error}\n')

if __name__=='__main__': main()
