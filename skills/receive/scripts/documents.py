#!/usr/bin/env python3
"""Receive-owned document operations. Python stdlib; no host or network access."""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
import threading
import uuid

SCHEMA_VERSION = 1
FIELDS = ['id','sha256','filename','path','type','kind','phase','stage','scope','originator','date','received_at','title','sheet','package','status','supersedes','source','change_id','notes','history']
COORDS = ('phase','stage','scope','originator','date')
DEFAULT_TEMPLATE = '{phase}/{stage}/{scope}/{originator}/{date}'
TASK_FIELDS = ['id','project_id','description','owner','due','status','created','updated','completed','cancelled','source','related','history']
TIME_FIELDS = ['id','date','hours','description','sources','correction']
INVOICE_FIELDS = ['id','invoice_number','period_start','period_end','currency','base','expenses','total','sent','paid','status','correction','document_id','history']
CHANGE_FIELDS = ['id','description','status','source','document_ids','date','notes']
REGISTERS = {'DOCUMENTS.csv':FIELDS,'TASKS.csv':TASK_FIELDS,'TIME.csv':TIME_FIELDS,'INVOICES.csv':INVOICE_FIELDS,'CHANGES.csv':CHANGE_FIELDS}
_LOCAL=threading.local()

def versions():
    if not hasattr(_LOCAL,'reads'): _LOCAL.reads={}
    return _LOCAL.reads

def read_text(path):
    content=path.read_bytes(); versions()[str(path.absolute())]=hashlib.sha256(content).hexdigest()
    return content.decode('utf-8')

def expect_absent(path):
    versions()[str(path.absolute())]=None

class DomainError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def fail(code, message):
    raise DomainError(code, message)

def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def today():
    return dt.date.today().isoformat()

def date_value(value):
    if not isinstance(value, str): fail('invalid_date', 'date must be text')
    if not re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?',value): fail('invalid_date','use YYYY-MM-DD or known YYYY-MM precision')
    try:
        if re.fullmatch(r'\d{4}-\d{2}', value): dt.date.fromisoformat(value + '-01')
        else: dt.date.fromisoformat(value)
    except ValueError: fail('invalid_date', 'use YYYY-MM-DD or known YYYY-MM precision')
    return value

def safe_text(value):
    if not isinstance(value, str) or not value.strip() or '|' in value or any(ord(c)<32 for c in value):
        fail('invalid_input', 'nonempty single-line text required')
    return value

def relative(value):
    if not isinstance(value, str) or not value or any(c in value for c in '\\:<>"|?*'):
        fail('unsafe_path', 'expected a portable project-relative path')
    p = Path(value)
    if p.is_absolute() or any(part in ('..','.','') for part in value.split('/')) or any(ord(c)<32 for c in value):
        fail('unsafe_path', 'path escapes the project or contains unsafe segments')
    if any(part.rstrip(' .') != part or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(\..*)?', part) for part in p.parts):
        fail('unsafe_path', 'path contains a reserved portable filename')
    return p

def inside(root, value):
    p = root / relative(str(value))
    try: p.resolve().relative_to(root.resolve())
    except ValueError: fail('unsafe_path', 'path resolves outside project')
    for part in [p, *p.parents]:
        if part == root.parent: break
        if part.is_symlink(): fail('unsafe_path', 'symlinks are not document targets')
    return p

def fields(text):
    out = {}
    for line in text.splitlines():
        if line.startswith('|'):
            row = [v.strip() for v in line.strip('|').split('|')]
            if len(row)>1 and row[0] not in out: out[row[0]] = row[1]
    return out

def table(text, name):
    match = re.search(r'<!-- '+re.escape(name)+r':start -->\s*(.*?)\s*<!-- '+re.escape(name)+r':end -->', text, re.S)
    if not match: fail('invalid_manifest', 'missing bounded table: ' + name)
    lines = [line for line in match[1].splitlines() if line.startswith('|')]
    if len(lines)<2: fail('invalid_manifest','table header absent: '+name)
    header = [v.strip() for v in lines[0].strip('|').split('|')]
    result=[]
    for line in lines[2:]:
        vals=[v.strip() for v in line.strip('|').split('|')]
        if len(vals)!=len(header): fail('invalid_manifest','malformed table: '+name)
        result.append(dict(zip(header, vals)))
    return result

def context(data):
    root = Path(data['project_root']).absolute()
    if root.is_symlink() or not root.is_dir(): fail('invalid_project','project root is unavailable or symlinked')
    manifest = inside(root, 'PROJECT.md')
    info = fields(read_text(manifest))
    if info.get('Format version') != '3' or info.get('Document model') != '1':
        fail('invalid_project','new document model 1 is required; no conversion is performed')
    if not info.get('Project ID') or not info.get('Kind'): fail('invalid_project','project identity is incomplete')
    config=json.loads(read_text(inside(root,'.as-folder.json')))
    try: valid_id='asf_'+str(uuid.UUID(config.get('folder_id','').removeprefix('asf_')))
    except ValueError: fail('invalid_identity','invalid project Folder ID')
    if set(config)!={'format','folder_id','kind'} or config.get('format')!=1 or config.get('kind')!='project' or config['folder_id']!=valid_id: fail('invalid_identity','invalid project folder identity')
    studio = None
    if data.get('studio_root'):
        studio=Path(data['studio_root']).absolute()
        if studio.is_symlink(): fail('invalid_studio','symlinked studio root')
        try: root.resolve().relative_to(studio.resolve())
        except ValueError: fail('invalid_studio','project is not a descendant of studio')
        studio_text=read_text(inside(studio, 'STUDIO.md'))
        entries=table(studio_text,'projects')
        matches=[r for r in entries if r.get('Project ID')==info['Project ID'] and registered_folder(studio,r).resolve()==root.resolve()]
        if len(matches)!=1: fail('invalid_studio','project is not uniquely registered in supplied studio')
    return root,info,studio

def registered_folder(studio,row):
    """Folder ID is durable; cached readable paths can drift without losing identity."""
    identity=row.get('Folder ID')
    if not identity: fail('invalid_identity','registered Folder ID required')
    matches=[]
    for directory,dirs,files in os.walk(studio,followlinks=False):
        dirs[:]=[name for name in dirs if not name.startswith('.') and not (Path(directory)/name).is_symlink()]
        if '.as-folder.json' not in files: continue
        p=Path(directory)/'.as-folder.json'
        if p.is_symlink(): fail('unsafe_path','folder identity is symlinked')
        try: config=json.loads(p.read_text())
        except (ValueError,OSError): continue
        if config.get('folder_id')==identity and config.get('kind')=='project': matches.append(Path(directory))
    if len(matches)!=1: fail('invalid_identity','Folder ID missing or duplicated')
    return matches[0]

def read_csv(path, header):
    if path.is_symlink(): fail('unsafe_path','register is symlinked')
    if not path.exists(): fail('invalid_register','missing '+path.name)
    try:
        reader=csv.DictReader(io.StringIO(read_text(path)))
        if reader.fieldnames!=header: fail('invalid_register','unexpected '+path.name+' columns')
        rows=list(reader)
        if any(None in r or any(v is None for v in r.values()) for r in rows): fail('invalid_register','malformed '+path.name)
        return rows
    except (UnicodeError,csv.Error) as e: fail('invalid_register',str(e))

def csv_bytes(rows, header):
    stream=io.StringIO(newline='')
    w=csv.DictWriter(stream,fieldnames=header,lineterminator='\n')
    w.writeheader(); w.writerows(rows)
    return stream.getvalue().encode()

def digest(path):
    if path.is_symlink(): fail('unsafe_path','cannot hash symlink')
    h=hashlib.sha256()
    if path.is_dir():
        h.update(b'package\0')
        for f in sorted(path.rglob('*')):
            if f.is_symlink(): fail('unsafe_path','package contains symlink')
            if f.is_dir(): h.update(b'directory\0'+f.relative_to(path).as_posix().encode()+b'\0')
            elif f.is_file():
                h.update(b'file\0'+f.relative_to(path).as_posix().encode()+b'\0')
                h.update(bytes.fromhex(digest(f)))
    elif path.is_file():
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    else: fail('missing_file','file or package is unavailable')
    value=h.hexdigest()
    if path.is_file(): versions()[str(path.absolute())]=value
    return value

def rows_for(root):
    rows=read_csv(inside(root,'DOCUMENTS.csv'),FIELDS)
    ids=set(); paths=set()
    for row in rows:
        if not re.fullmatch('D[0-9]{6,}',row['id']) or row['id'] in ids or row['path'] in paths:
            fail('invalid_register','duplicate/invalid document identity or path')
        ids.add(row['id']); paths.add(row['path']); inside(root,row['path'])
        if Path(row['path']).name!=row['filename']: fail('invalid_register','registered filename differs from path')
        safe_text(row['kind'])
        for coordinate in ('phase','stage','scope','originator'): safe_text(row[coordinate])
        if not re.fullmatch('[a-f0-9]{64}',row['sha256']): fail('invalid_register','invalid document hash')
        date_value(row['date'])
        try:
            history=json.loads(row['history']); provenance=json.loads(row['source'])
            if not isinstance(history,list) or any(not isinstance(e,dict) or not e.get('event') for e in history) or not isinstance(provenance,dict): raise ValueError()
            dt.datetime.fromisoformat(row['received_at'])
            if provenance.get('expires'): date_value(provenance['expires'])
        except (ValueError,TypeError): fail('invalid_register','source/history JSON is invalid')
    if any(r['supersedes'] and r['supersedes'] not in ids for r in rows): fail('invalid_register','unknown superseded document')
    links={r['id']:r['supersedes'] for r in rows}
    for identifier in links:
        visited=set(); current=identifier
        while current:
            if current in visited: fail('invalid_register','cyclic revision lineage')
            visited.add(current); current=links[current]
    return rows

def configuration(root, studio):
    text=(root/'PROJECT.md').read_text()
    settings=fields(text)
    vocab={name:{r['Value'] for r in table(text,name+'s')} for name in ('phase','scope','originator')}
    if studio: text=(studio/'STUDIO.md').read_text(); settings=fields(text)
    stages=table(text,'stages')
    kind=fields((root/'PROJECT.md').read_text())['Kind']
    vocab['stage']={r['Value'] for r in stages if r['Kind'] in (kind,'*')}
    if not vocab['stage']: fail('unknown_vocabulary','no firm stage vocabulary for project Kind')
    template=settings.get('Document path template')
    if template is None: fail('invalid_manifest','Document path template is required (empty is allowed)')
    return template,vocab

def resolved(data, config=None):
    root,info,studio=context(data)
    template,vocab=config if config is not None else configuration(root,studio)
    values=dict(data.get('coordinates',{}))
    record=data.get('record')
    if record not in (None,'SCHEDULE.csv'): fail('invalid_record','unsupported scoped register')
    needed=('phase','stage','scope') if record else COORDS
    for key in needed:
        if key not in values: fail('invalid_coordinates','missing '+key)
        if key=='date': date_value(values[key])
        elif values[key] not in vocab[key]: fail('unknown_vocabulary','unknown '+key+': '+str(values[key]))
    if not record: safe_text(data.get('kind'))
    if not template:
        p=inside(root,data.get('path',''))
        return {'folder':p.relative_to(root).as_posix(),'path':(p/record).relative_to(root).as_posix() if record else None,'coordinates':values}
    fields_used=re.findall(r'{([^{}]+)}',template)
    if any(key not in FIELDS for key in fields_used): fail('invalid_template','template uses unknown register column')
    segments=template.strip('/').split('/')
    if template.startswith('/') or template.endswith('/'): fail('invalid_template','template must be relative without trailing slash')
    if record: segments=[s for s in segments if any('{'+c+'}' in s for c in needed)]
    mapping={**data.get('metadata',{}),**values,'kind':data.get('kind','')}
    try: folder='/'.join(segments).format_map(mapping)
    except (KeyError,ValueError) as e: fail('invalid_coordinates','template value missing/invalid: '+str(e))
    p=inside(root,folder)
    # Each coordinate is a folder component; custom confirmed spelling is preserved.
    for key in fields_used:
        value=mapping.get(key)
        if isinstance(value,str) and ('/' in value or '\\' in value): fail('invalid_coordinates','coordinate cannot contain a path separator')
    return {'folder':p.relative_to(root).as_posix(),'path':(p/record).relative_to(root).as_posix() if record else None,'coordinates':values}

def recover(root):
    transaction=root/'.as-document-transaction'
    if not transaction.exists(): return {'recovered':False}
    if transaction.is_symlink(): fail('unsafe_path','symlinked transaction')
    journal=json.loads((transaction/'journal.json').read_text())
    if journal['state']=='committed': shutil.rmtree(transaction); return {'recovered':False,'committed':True}
    for item in reversed(journal['files']):
        dest=inside(root,item['path']); backup=transaction/item['backup']
        if item['existed']:
            dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(backup,dest)
        elif dest.exists(): dest.unlink()
    for item in journal.get('directories',[]):
        if item['existed']:
            dest=inside(root,item['path']); dest.mkdir(parents=True,exist_ok=True); os.chmod(dest,item['mode'])
    for item in sorted(journal.get('directories',[]),key=lambda item:len(Path(item['path']).parts),reverse=True):
        dest=inside(root,item['path'])
        if not item['existed'] and dest.exists(): dest.rmdir()
    shutil.rmtree(transaction)
    return {'recovered':True}

def commit(root, changes, directories=None, read_guards=None):
    """Journal all targets before publication. Hard interruptions require explicit recover."""
    transaction=root/'.as-document-transaction'
    if transaction.exists(): fail('recovery_required','run documents.recover before another mutation')
    directories=directories or {}
    for name in set(changes)|set(directories): inside(root,name)
    transaction.mkdir(mode=0o700)
    journal={'state':'prepared','files':[],'directories':[]}
    try:
        checked={str(inside(root,name).absolute()) for name in directories if directories[name]=='create'}
        for name,value in changes.items():
            checked.add(str(inside(root,name).absolute()))
            if isinstance(value,Path): checked.add(str(value.absolute()))
        for name in checked:
            if name not in versions(): continue
            expected=versions()[name]; path=Path(name)
            if expected is None:
                if path.exists(): fail('conflict','target appeared since preview: '+name)
            elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
                fail('conflict','file changed since read: '+name)
        for number,(name,value) in enumerate(changes.items()):
            dest=inside(root,name); backup=str(number)+'.backup'; staged=str(number)+'.new'
            if dest.exists() and not dest.is_file(): fail('collision','target is not a file: '+name)
            if dest.exists(): shutil.copy2(dest,transaction/backup)
            if isinstance(value,Path): shutil.copy2(value,transaction/staged)
            elif value is not None: (transaction/staged).write_bytes(value)
            if value is not None and dest.exists(): os.chmod(transaction/staged,stat.S_IMODE(dest.stat().st_mode))
            journal['files'].append({'path':name,'backup':backup,'staged':staged,'existed':dest.exists(),'delete':value is None,'sha256':digest(transaction/staged) if value is not None else None})
        for name,action in directories.items():
            dest=inside(root,name)
            if action not in ('create','remove') or dest.exists() and not dest.is_dir(): fail('collision','invalid directory target: '+name)
            journal['directories'].append({'path':name,'existed':dest.exists(),'delete':action=='remove','mode':stat.S_IMODE(dest.stat().st_mode) if dest.exists() else 0o755})
        for path,expected in (read_guards or {}).items():
            if digest(path)!=expected: fail('conflict','affected document changed before publication: '+str(path))
        (transaction/'journal.json').write_text(json_text(journal))
        for item in sorted(journal['directories'],key=lambda item:len(Path(item['path']).parts)):
            if not item['delete']: inside(root,item['path']).mkdir(parents=True,exist_ok=True)
        for index,item in enumerate(journal['files']):
            dest=inside(root,item['path']); dest.parent.mkdir(parents=True,exist_ok=True)
            if item['delete']:
                if dest.exists(): dest.unlink()
            else: os.replace(transaction/item['staged'],dest)
            if os.environ.get('AS_DOCUMENT_TEST_FAIL_AFTER')==str(index+1): raise OSError('injected document publication failure')
        for item in sorted(journal['directories'],key=lambda item:len(Path(item['path']).parts),reverse=True):
            if item['delete']: inside(root,item['path']).rmdir()
        for item in journal['files']:
            dest=inside(root,item['path'])
            if item['delete']:
                if dest.exists(): fail('verification_failed','deleted source unexpectedly remains')
            elif digest(dest)!=item['sha256']: fail('verification_failed','published bytes differ from staged bytes')
        for item in journal['directories']:
            dest=inside(root,item['path'])
            if dest.exists()==item['delete']: fail('verification_failed','package directory publication differs from plan')
        journal['state']='committed'; (transaction/'journal.json').write_text(json_text(journal))
    except BaseException:
        if (transaction/'journal.json').exists(): recover(root)
        else: shutil.rmtree(transaction)
        raise
    shutil.rmtree(transaction)
    for name in changes:
        path=inside(root,name)
        versions()[str(path.absolute())]=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def dry_run(data):
    value=data.get('dry_run',True)
    if not isinstance(value,bool): fail('invalid_input','dry_run must be boolean')
    return value

def file_changes(source, target):
    if source.is_dir():
        out={}
        for f in source.rglob('*'):
            if f.is_symlink(): fail('unsafe_path','source package contains symlink')
            if f.is_file(): out[(Path(target)/f.relative_to(source)).as_posix()]=f
        return out
    return {target:source}

def directory_changes(source,target,remove_source=False,root=None):
    if not source.is_dir(): return {}
    result={target:'create'}
    for directory in source.rglob('*'):
        if directory.is_symlink(): fail('unsafe_path','source package contains symlink')
        if directory.is_dir(): result[(Path(target)/directory.relative_to(source)).as_posix()]='create'
    if remove_source:
        for directory in [source,*[p for p in source.rglob('*') if p.is_dir()]]: result[directory.relative_to(root).as_posix()]='remove'
    return result

def register(data):
    root,_,_=context(data); rows=rows_for(root); location=resolved(data)
    source=Path(data['source_path']).absolute()
    if source.is_symlink(): fail('unsafe_path','source is symlinked')
    sha=digest(source)
    target=(Path(location['folder'])/source.name).as_posix(); dest=inside(root,target)
    for row in rows:
        if row['path']==target:
            if row['sha256']==sha and (not dest.exists() or digest(dest)==sha):
                if not dest.exists(): fail('missing_file','registered destination is missing')
                return {'document':row,'changed':False,'dry_run':dry_run(data)}
            fail('collision','existing document differs; create an explicit new revision')
    if dest.exists() and (source.resolve()!=dest.resolve() or digest(dest)!=sha): fail('collision','unregistered target already exists')
    if not dest.exists():
        for name in file_changes(source,target): expect_absent(inside(root,name))
        for name in directory_changes(source,target): expect_absent(inside(root,name))
    meta=data.get('metadata',{})
    allowed={'title','sheet','package','status','supersedes','source','change_id','notes'}
    if set(meta)-allowed: fail('invalid_input','unknown document metadata')
    if meta.get('supersedes') and meta['supersedes'] not in {r['id'] for r in rows}: fail('invalid_revision','supersedes must identify existing document')
    provenance=meta.get('source',{})
    if not isinstance(provenance,dict): fail('invalid_input','source must be a provenance object')
    if provenance.get('expires'): date_value(provenance['expires'])
    row={key:'' for key in FIELDS}
    row.update({**meta,**location['coordinates'],'id':'D'+str(max([int(r['id'][1:]) for r in rows],default=0)+1).zfill(6),'sha256':sha,'filename':source.name,'path':target,'type':'package' if source.is_dir() else source.suffix.lstrip('.').lower(),'kind':data['kind'],'received_at':dt.datetime.now(dt.timezone.utc).isoformat(),'status':meta.get('status','received'),'source':json_text(provenance),'history':json_text([{'event':'registered','date':today(),'sha256':sha,'path':target}])})
    result={'document':row,'changed':not dry_run(data),'dry_run':dry_run(data),'duplicate_hash_ids':[r['id'] for r in rows if r['sha256']==sha]}
    if not dry_run(data):
        changes={} if source.resolve()==dest.resolve() else file_changes(source,target)
        directories={} if source.resolve()==dest.resolve() else directory_changes(source,target)
        changes['DOCUMENTS.csv']=csv_bytes(rows+[row],FIELDS); commit(root,changes,directories,{source:sha})
        if digest(dest)!=sha: fail('verification_failed','registered destination hash mismatch')
    return result

def query(data):
    root,_,_=context(data); rows=rows_for(root); filters=data.get('filters',{})
    superseded={r['supersedes'] for r in rows if r['supersedes']}
    allowed={'id','kind','phase','stage','scope','originator','since','latest','change_id','source_type','expires_before'}
    if set(filters)-allowed: fail('invalid_input','unknown query filter')
    for name in ('id','kind','phase','stage','scope','originator','change_id'):
        if name in filters: rows=[r for r in rows if r[name]==filters[name]]
    if filters.get('since'): date_value(filters['since']); rows=[r for r in rows if r['received_at'][:10]>=filters['since']]
    if filters.get('source_type'): rows=[r for r in rows if json.loads(r['source']).get('type')==filters['source_type']]
    if filters.get('expires_before'):
        date_value(filters['expires_before']); rows=[r for r in rows if json.loads(r['source']).get('expires','9999')<=filters['expires_before']]
    rows.sort(key=lambda r:(r['date'],r['received_at'],r['id']),reverse=True)
    if filters.get('latest'):
        rows=[r for r in rows if r['id'] not in superseded][:1]
    return {'documents':rows,'count':len(rows),'changed':False}

def update(data):
    root,_,_=context(data); rows=rows_for(root)
    matches=[r for r in rows if r['id']==data['id']]
    if len(matches)!=1: fail('unknown_document','document ID is not registered')
    row=matches[0]
    if data.get('expected_sha256')!=row['sha256'] or digest(inside(root,row['path']))!=row['sha256']: fail('conflict','document bytes changed')
    changes=data.get('changes',{})
    if set(changes)-{'status','title','notes','source','change_id'}: fail('invalid_input','identity, bytes and revision links are immutable; receive a new revision')
    if 'source' in changes:
        if not isinstance(changes['source'],dict): fail('invalid_input','source must be object')
        if changes['source'].get('expires'): date_value(changes['source']['expires'])
        changes={**changes,'source':json_text(changes['source'])}
    event=data.get('event',{'event':'metadata-updated','date':today()})
    if not isinstance(event,dict) or not event.get('event'): fail('invalid_input','history event required')
    if all(row[k]==v for k,v in changes.items()) and event in json.loads(row['history']): return {'document':row,'changed':False}
    before={k:row[k] for k in changes}; row.update(changes)
    history=json.loads(row['history']); history.append({**event,'before':before,'after':changes}); row['history']=json_text(history)
    if not dry_run(data): commit(root,{'DOCUMENTS.csv':csv_bytes(rows,FIELDS)})
    return {'document':row,'changed':not dry_run(data),'dry_run':dry_run(data)}

def rewrite_links(text, old_file, new_file, moves):
    def replace(match):
        url=match.group(2)
        if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:',url) or url.startswith(('#','/')): return match.group(0)
        raw,sep,anchor=url.partition('#')
        target=os.path.normpath(str(Path(old_file).parent/raw))
        changed=moves.get(target,target)
        if old_file==new_file and changed==target: return match.group(0)
        path=os.path.relpath(changed,Path(new_file).parent).replace(os.sep,'/')
        return match.group(1)+path+(sep+anchor if sep else '')+match.group(3)
    return re.sub(r'(\]\()([^\s)]+)(\))',replace,text)

def relocate(data, targets, config=None, project_text=None):
    """Plan all moves and link updates together; one transaction for a vocabulary rename."""
    root,_,_=context(data); rows=rows_for(root); changes={}; directories={}; moves={}; old_paths={}; row_targets={}; rewritten=set()
    by_id={r['id']:r for r in rows}; registered_hashes={r['id']:r['sha256'] for r in rows}
    for identifier,coordinates in targets.items():
        if identifier not in by_id: fail('unknown_document','document ID is not registered')
        row=by_id[identifier]; source=inside(root,row['path'])
        if digest(source)!=row['sha256']: fail('conflict','registered bytes changed')
        location_data={**data,'coordinates':coordinates,'kind':row['kind'],'metadata':{k:row[k] for k in FIELDS if k not in COORDS}}
        if config is not None and config[0]=='': location_data['path']=str(Path(row['path']).parent)
        location=resolved(location_data,config=config)
        target=(Path(location['folder'])/row['filename']).as_posix()
        if target==row['path']:
            if any(row[k]!=v for k,v in coordinates.items()):
                row.update(coordinates); history=json.loads(row['history']); history.append({'event':'coordinates-updated','date':today(),'coordinates':coordinates}); row['history']=json_text(history)
                changes['DOCUMENTS.csv']=b''
            continue
        if inside(root,target).exists() or any(r['path']==target for r in rows) or target in row_targets.values(): fail('collision','move target exists')
        old_paths[identifier]=row['path']; row_targets[identifier]=target
        package_dirs=directory_changes(source,target,remove_source=True,root=root)
        for name,action in package_dirs.items():
            if action=='create': expect_absent(inside(root,name))
        directories.update(package_dirs)
        for new,old_source in file_changes(source,target).items():
            expect_absent(inside(root,new)); old_relative=old_source.relative_to(root).as_posix()
            moves[old_relative]=new; changes[new]=old_source; changes[old_relative]=None
        row.update({**coordinates,'path':target})
    for row in rows:
        original=old_paths.get(row['id'],row['path']); path=inside(root,original)
        files=sorted(path.rglob('*')) if path.is_dir() else [path]
        for file in files:
            if file.is_file() and file.suffix=='.md':
                old=file.relative_to(root).as_posix(); new=moves.get(old,old)
                content=read_text(file); updated=rewrite_links(content,old,new,moves)
                if content!=updated:
                    # A path correction cannot authorize new accepted/issued bytes.
                    if row['status'] in ('accepted','issued','sent','signed') or any(event.get('terms_sha256') for event in json.loads(row['history'])):
                        fail('sealed_reference_conflict','move would rewrite immutable issued/accepted document '+row['id']+'; an explicitly authorized new revision is required')
                    if row['id'] not in rewritten and digest(path)!=row['sha256']: fail('conflict','linked document '+row['id']+' differs from its registered hash')
                    rewritten.add(row['id']); changes[new]=updated.encode()
    existing=read_text(root/'PROJECT.md'); new_project=rewrite_links(existing if project_text is None else project_text,'PROJECT.md','PROJECT.md',moves)
    if new_project!=existing: changes['PROJECT.md']=new_project.encode()
    for row in rows:
        original=old_paths.get(row['id'],row['path']); path=inside(root,original); old_hash=row['sha256']
        if row['id'] not in rewritten: pass
        elif path.is_dir():
            tree=hashlib.sha256(); tree.update(b'package\0')
            for file in sorted(path.rglob('*')):
                if file.is_dir(): tree.update(b'directory\0'+file.relative_to(path).as_posix().encode()+b'\0'); continue
                if not file.is_file(): continue
                old=file.relative_to(root).as_posix(); new=moves.get(old,old); value=changes.get(new,file)
                content_hash=hashlib.sha256(value).hexdigest() if isinstance(value,bytes) else digest(file)
                tree.update(b'file\0'+file.relative_to(path).as_posix().encode()+b'\0'); tree.update(bytes.fromhex(content_hash))
            row['sha256']=tree.hexdigest()
        elif isinstance(changes.get(row['path']),bytes): row['sha256']=hashlib.sha256(changes[row['path']]).hexdigest()
        if row['id'] in old_paths or row['sha256']!=old_hash:
            history=json.loads(row['history']); history.append({'event':'moved' if row['id'] in old_paths else 'links-updated','date':today(),'from':original,'path':row['path'],'sha256':row['sha256']}); row['history']=json_text(history)
    if changes or directories:
        changes['DOCUMENTS.csv']=csv_bytes(rows,FIELDS)
        guards={inside(root,old_paths.get(identifier,by_id[identifier]['path'])):registered_hashes[identifier] for identifier in set(targets)|rewritten}
        if not dry_run(data): commit(root,changes,directories,guards)
    return {'documents':[by_id[i] for i in targets],'changed':bool(changes) and not dry_run(data),'dry_run':dry_run(data),'rewritten_files':[p for p,v in changes.items() if isinstance(v,bytes)]}


def move(data):
    root,_,_=context(data); rows=rows_for(root); matches=[r for r in rows if r['id']==data['id']]
    if len(matches)!=1: fail('unknown_document','document ID is not registered')
    if data.get('expected_sha256')!=matches[0]['sha256']: fail('conflict','expected document hash differs')
    result=relocate(data,{data['id']:data['coordinates']})
    return {**result,'document':result['documents'][0]}


def verify(data):
    root,_,_=context(data); rows=rows_for(root); findings=[]; seen={}; covered=set()
    as_of=date_value(data.get('as_of',today()))
    for row in rows:
        p=inside(root,row['path']); covered.add(row['path'])
        if not p.exists(): findings.append({'code':'missing_file','id':row['id']}); continue
        if p.is_dir(): covered.update(f.relative_to(root).as_posix() for f in p.rglob('*') if f.is_file())
        if digest(p)!=row['sha256']: findings.append({'code':'hash_mismatch','id':row['id']})
        if row['sha256'] in seen: findings.append({'code':'duplicate_hash','ids':[seen[row['sha256']],row['id']]})
        seen[row['sha256']]=row['id']
        try:
            expected=resolved({**data,'coordinates':{c:row[c] for c in COORDS},'kind':row['kind'],'path':str(Path(row['path']).parent),'metadata':{k:row[k] for k in FIELDS if k not in COORDS}})
            if str(Path(row['path']).parent)!=expected['folder']: findings.append({'code':'template_violation','id':row['id']})
        except DomainError as e: findings.append({'code':e.code,'id':row['id'],'message':str(e)})
        expires=json.loads(row['source']).get('expires')
        if expires and expires<as_of: findings.append({'code':'expired_source','id':row['id'],'expires':expires})
    reserved=set(REGISTERS)|{'PROJECT.md','AGENTS.md','CLAUDE.md','.as-folder.json','.gitignore','product-library.csv','epd-library.csv'}
    for p in root.rglob('*'):
        rel=p.relative_to(root)
        if any(part.startswith('.') for part in rel.parts): continue
        if p.is_file() and rel.as_posix() not in covered and not (len(rel.parts)==1 and p.name in reserved) and p.name!='SCHEDULE.csv': findings.append({'code':'unreceived_file','path':rel.as_posix()})
    if (root/'.as-document-transaction').exists(): findings.append({'code':'recovery_required'})
    return {'findings':findings,'valid':not findings,'count':len(rows),'changed':False}

def dispatch(operation,data):
    if not isinstance(data,dict): fail('invalid_input','input must be an object')
    verb=operation.removeprefix('documents.')
    if verb=='resolve': return resolved(data)
    if verb=='hash':
        root,_,_=context(data); p=inside(root,data['path']); return {'sha256':digest(p),'path':data['path'],'changed':False}
    if verb=='register': return register(data)
    if verb=='move': return move(data)
    if verb=='verify': return verify(data)
    if verb=='query': return query(data)
    if verb=='update': return update(data)
    if verb=='recover':
        root,_,_=context(data)
        if dry_run(data): return {'pending':(root/'.as-document-transaction').exists(),'changed':False,'dry_run':True}
        return recover(root)
    fail('unknown_operation','unknown document operation')

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('operation'); args=parser.parse_args()
    try:
        result=dispatch(args.operation,json.load(sys.stdin)); print(json_text(result))
    except (ValueError,KeyError,OSError) as e:
        print(json_text({'error':{'code':getattr(e,'code','io_error' if isinstance(e,OSError) else 'invalid_input'),'message':str(e)}})); return 2
    return 0

if __name__=='__main__': sys.exit(main())
