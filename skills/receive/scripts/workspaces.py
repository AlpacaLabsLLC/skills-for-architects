#!/usr/bin/env python3
"""Fresh document-model workspace operations; no legacy conversion."""
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

# Import shared code by exact packaged path AND bytes; persistent hosts must not
# reuse a sibling from another installed release through sys.modules['documents'].
import importlib.util
import hashlib
_module_path=Path(__file__).with_name('documents.py')
_module_key='_as_documents_'+hashlib.sha256(str(_module_path.resolve()).encode()+_module_path.read_bytes()).hexdigest()
if _module_key not in sys.modules:
    _spec=importlib.util.spec_from_file_location(_module_key,_module_path)
    _module=importlib.util.module_from_spec(_spec); sys.modules[_module_key]=_module; _spec.loader.exec_module(_module)
d=sys.modules[_module_key]

STAGES={'building':['0-predesign','1-sd','2-dd','3-cd','4-procurement','5-construction','6-closeout'],'software':['0-discovery','1-design','2-build','3-release','4-operate'],'initiative':['0-plan','1-deliver','2-review']}
DEFAULT_SCOPES={'building':['architecture','interiors'],'software':['product','engineering'],'initiative':['operations']}
REGISTRY=['Project ID','Project','Client','Code','Type','Kind','Status','Folder','Opened','Folder ID']

def bounded(name,header,rows):
    return '<!-- '+name+':start -->\n'+'\n'.join(['| '+' | '.join(header)+' |','|'+'|'.join('---' for _ in header)+'|']+['| '+' | '.join(str(r.get(h,'')) for h in header)+' |' for r in rows])+'\n<!-- '+name+':end -->'

def replace_table(text,name,header,rows):
    pattern=r'<!-- '+re.escape(name)+r':start -->.*?<!-- '+re.escape(name)+r':end -->'
    if len(re.findall(pattern,text,re.S))!=1: d.fail('invalid_manifest','table missing or repeated: '+name)
    return re.sub(pattern,lambda _:bounded(name,header,rows),text,flags=re.S)

def identity(kind):
    return {'format':1,'folder_id':'asf_'+str(uuid.uuid4()),'kind':kind}

def folder_id(root):
    p=d.inside(root,'.as-folder.json'); value=json.loads(p.read_text())
    try: valid_id='asf_'+str(uuid.UUID(value.get('folder_id','').removeprefix('asf_')))
    except ValueError: d.fail('invalid_identity','invalid Folder ID UUID')
    if set(value)!={'format','folder_id','kind'} or value['format']!=1 or value['folder_id']!=valid_id: d.fail('invalid_identity','invalid folder identity')
    return value

def table_values(values):
    if not isinstance(values,list) or not values: d.fail('invalid_vocabulary','nonempty vocabulary required')
    if len(values)!=len(set(values)): d.fail('invalid_vocabulary','duplicate vocabulary value')
    for value in values:
        d.safe_text(value); d.relative(value)
        if '/' in value: d.fail('invalid_vocabulary','vocabulary value must be one folder component')
    return [{'Value':v} for v in values]

def stage_rows(stages):
    rows=[]
    for kind,values in stages.items():
        d.safe_text(kind)
        for row in table_values(values): rows.append({'Kind':kind,**row})
    return rows

def setting(text,key,value):
    d.safe_text(str(value))
    pattern=r'(?m)^\| '+re.escape(key)+r' \|[^\n]*$'
    if len(re.findall(pattern,text))!=1: d.fail('invalid_manifest','setting missing or repeated: '+key)
    old=re.search(pattern,text).group(0).split('|'); old[2]=' '+str(value)+' '
    return re.sub(pattern,lambda _:'|'.join(old),text)

def new_target(data,kind):
    target=Path(data['target']).absolute()
    if target.is_symlink() or (target.exists() and (not target.is_dir() or any(target.iterdir()))): d.fail('collision','fresh setup needs an absent or empty exact target')
    for parent in target.parents:
        if parent.is_symlink(): d.fail('unsafe_path','setup ancestor is symlinked')
        if (parent/'PROJECT.md').exists(): d.fail('nested_project','cannot initialize inside an existing project')
        if kind=='studio' and (parent/'STUDIO.md').exists(): d.fail('nested_studio','cannot initialize inside an existing studio')
    return target

def publish_setup(target,files,dirs):
    target.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.as-setup-',dir=target.parent))
    try:
        for name,content in files.items():
            p=d.inside(staging,name); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(content if isinstance(content,bytes) else content.encode())
        for name in dirs: d.inside(staging,name).mkdir(parents=True,exist_ok=True)
        if target.exists():
            if any(target.iterdir()): d.fail('conflict','target changed during setup')
            target.rmdir()
        os.rename(staging,target)
    finally:
        if staging.exists(): shutil.rmtree(staging)

def project_init(data):
    target=new_target(data,'project')
    required=['name','project_id','kind','type','status','client_code','client']
    for field in required: d.safe_text(data[field])
    if data['type'] not in ('internal','client'): d.fail('invalid_identity','Type must be internal or client')
    created=d.date_value(data.get('created',d.today()))
    if len(created)!=10: d.fail('invalid_date','Created needs day precision')
    values=data.get('vocabularies',{})
    for field in ('phases','scopes','originators'):
        if field not in values: d.fail('missing_vocabulary','confirm '+field+' for fresh project')
        table_values(values[field])
    stages=data.get('stages',STAGES)
    if data['kind'] not in stages and '*' not in stages: d.fail('missing_vocabulary','confirm stages for this project Kind')
    template=data.get('path_template',d.DEFAULT_TEMPLATE)
    if not isinstance(template,str): d.fail('invalid_template','path_template must be text')
    if any(f not in d.FIELDS for f in re.findall(r'{([^{}]+)}',template)): d.fail('invalid_template','unknown template field')
    config=identity('project')
    info={'Format version':'3','Document model':'1','Project ID':data['project_id'],'Project':data['name'],'Type':data['type'],'Kind':data['kind'],'Status':data['status'],'Created':created,'Client code':data['client_code'],'Client':data['client'],'Document path template':template}
    text='# Project — '+data['name']+'\n\n## Identity\n\n| Field | Value | Source | Date |\n|---|---|---|---|\n'+''.join('| '+k+' | '+v+' | project setup | '+created+' |\n' for k,v in info.items())
    text+='\n## Project records\n\nDocuments and authored decisions, events, plans and commercial records are indexed by ID/kind in [DOCUMENTS.csv](DOCUMENTS.csv).\n\nTasks: [TASKS.csv](TASKS.csv). Time: [TIME.csv](TIME.csv). Invoice history: [INVOICES.csv](INVOICES.csv).\n'
    for key in ('phases','scopes','originators'): text+='\n## '+key.title()+'\n\n'+bounded(key,['Value'],table_values(values[key]))+'\n'
    text+='\n## Stages (standalone defaults)\n\n'+bounded('stages',['Kind','Value'],stage_rows(stages))+'\n'
    instructions='# Project instructions\n\nRead PROJECT.md before durable work. Preserve immutable Project ID and Folder ID. Facts belong in PROJECT.md; authored decisions/events/plans/commercial records are documents indexed by DOCUMENTS.csv. Use the installed receive-owned document operations to resolve and register files; never compose document folders. TASKS.csv, TIME.csv and INVOICES.csv have separate skill owners. Existing exact authorization persists. Do not infer acceptance, billability, payment or completion.\n'
    files={'PROJECT.md':text,'.as-folder.json':d.json_text(config)+'\n','AGENTS.md':instructions,'CLAUDE.md':'@AGENTS.md\n','.gitignore':'# User artifacts remain private unless explicitly selected for version control.\n*.pdf\n*.zip\n*.ifc\n*.rvt\n.as-document-transaction/\n'}
    for name,header in d.REGISTERS.items(): files[name]=d.csv_bytes([],header)
    if data.get('task_mode','project')=='portfolio':
        if not data.get('studio_root'): d.fail('invalid_task_mode','portfolio setup requires explicit owning studio')
        studio=Path(data['studio_root']).absolute(); st=d.fields((studio/'STUDIO.md').read_text())
        if st.get('Task register')!='portfolio': d.fail('invalid_task_mode','studio does not own portfolio tasks')
        target.resolve().relative_to(studio.resolve()); del files['TASKS.csv']
        files['PROJECT.md']=text.replace('Tasks: [TASKS.csv](TASKS.csv).','Tasks: the owning studio portfolio TASKS.csv filtered by Project ID.')
    elif data.get('task_mode','project')!='project': d.fail('invalid_task_mode','unknown task mode')
    result={'target':str(target),'files':sorted(files),'identity':config,'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}
    if not d.dry_run(data): publish_setup(target,files,['.agents/skills','.claude/skills'])
    return result

def studio_init(data):
    target=new_target(data,'studio'); name=d.safe_text(data['name']); config=identity('studio')
    roots=data.get('roots',{'projects':'Projects','operations':'Operations','standards':'Standards','references':'References'})
    if set(roots)!={'projects','operations','standards','references'}: d.fail('invalid_taxonomy','four managed roots required')
    for value in roots.values(): d.relative(value)
    if len(set(roots.values()))!=4: d.fail('invalid_taxonomy','managed roots must be distinct')
    for a in roots.values():
        if any(a!=b and a.startswith(b+'/') for b in roots.values()): d.fail('invalid_taxonomy','managed roots cannot overlap')
    policy=data.get('naming_policy','as')
    if policy not in ('as','firm','none'): d.fail('invalid_policy','unknown naming policy')
    settings={'Format version':'3','Document model':'1','Studio':name,'Folder ID':config['folder_id'],'Working units':data.get('units','project-specific / mixed'),'Country':data.get('country','No default'),'State/region':data.get('region','No default'),'City':data.get('city','No default'),'Project naming':policy,'Project ID convention':data.get('id_convention','YYMMDD-CCC-PROJECT-NAME'),'Folder taxonomy':data.get('folder_taxonomy','as'),'Project folder convention':data.get('folder_convention','Projects/{Client Account or Internal}/{YYYYMM} {Project Name}'),'Task register':data.get('task_mode','project'),'Document path template':data.get('path_template',d.DEFAULT_TEMPLATE)}
    for key,value in settings.items():
        if value!='': d.safe_text(value)
    if settings['Task register'] not in ('project','portfolio'): d.fail('invalid_task_mode','unknown task mode')
    settings.update({k.title()+' root':v for k,v in roots.items()})
    text='# Studio — '+name+'\n\n## Settings\n\n| Setting | Value |\n|---|---|\n'+''.join('| '+k+' | '+v+' |\n' for k,v in settings.items())
    text+='\n## Projects\n\n'+bounded('projects',REGISTRY,[])+'\n\n## Firm stage vocabulary\n\nThe shipped names are Arch Studio-owned defaults; they do not reproduce or certify an external professional standard. Confirm firm changes at setup.\n\n'+bounded('stages',['Kind','Value'],stage_rows(data.get('stages',STAGES)))+'\n'
    text+='\n## Proposed scopes by Kind\n\n'+bounded('default-scopes',['Kind','Value'],stage_rows(data.get('default_scopes',DEFAULT_SCOPES)))+'\n'
    text+='\n## Storage\n\nRecords remain in this user-owned workspace. Setup creates no ALPA account or cloud storage. Content supplied to a configured model follows that provider account and terms.\n'
    instructions='# Studio instructions\n\nRead STUDIO.md and resolve one registered project before durable project work. Only studio writes STUDIO.md. Project Type/Kind/Status are advisory. Use current document/register owners; preserve user authorization and source provenance. Do not create projects implicitly. Firm skills belong in the active host skill root.\n'
    files={'STUDIO.md':text,'.as-folder.json':d.json_text(config)+'\n','AGENTS.md':instructions,'CLAUDE.md':'@AGENTS.md\n','.mcp.json':'{"mcpServers":{}}\n'}
    for key,value in roots.items():
        root_identity=identity(key); files[value+'/.as-folder.json']=d.json_text(root_identity)+'\n'
        files['STUDIO.md']=files['STUDIO.md'].replace('| '+key.title()+' root | '+value+' |','| '+key.title()+' root | '+value+' |\n| '+key.title()+' folder ID | '+root_identity['folder_id']+' |')
    if settings['Task register']=='portfolio': files['TASKS.csv']=d.csv_bytes([],d.TASK_FIELDS)
    result={'target':str(target),'files':sorted(files),'identity':config,'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}
    if not d.dry_run(data): publish_setup(target,files,['.agents/skills','.claude/skills',*roots.values()])
    return result

def studio_context(data):
    root=Path(data['studio_root']).absolute()
    if root.is_symlink(): d.fail('invalid_studio','symlinked studio root')
    text=d.read_text(d.inside(root,'STUDIO.md')); info=d.fields(text)
    if info.get('Format version')!='3' or info.get('Document model')!='1': d.fail('invalid_studio','fresh document model 1 required')
    return root,text,info,d.table(text,'projects')

def valid_projects(root,rows):
    results=[]; ids=set(); folder_ids=set()
    for row in rows:
        item=dict(row)
        try:
            project=d.registered_folder(root,row); info=d.fields((project/'PROJECT.md').read_text()); fid=folder_id(project)
            if info.get('Project ID')!=row['Project ID'] or fid['folder_id']!=row['Folder ID'] or row['Project ID'] in ids or fid['folder_id'] in folder_ids: d.fail('invalid_identity','registry identity mismatch or duplicate')
            if info.get('Document model')!='1': d.fail('invalid_project','project lacks document model 1')
            if any(info.get(key)!=row[key] for key in ('Project','Client','Type','Kind','Status')): d.fail('invalid_identity','registry metadata drift')
            ids.add(row['Project ID']); folder_ids.add(fid['folder_id']); item['valid']=True; item['resolved_folder']=project.relative_to(root).as_posix()
            if item['resolved_folder']!=row['Folder']: item['path_drift']=True
        except (ValueError,OSError,KeyError) as e: item.update(valid=False,error=str(e))
        results.append(item)
    return results

def studio_operation(verb,data):
    if verb=='init': return studio_init(data)
    root,text,info,rows=studio_context(data)
    if verb=='status': return {'studio_root':str(root),'settings':info,'projects':valid_projects(root,rows),'changed':False}
    changes={}; result={}
    if verb=='register':
        project=Path(data['project_root']).absolute()
        try: rel=project.relative_to(root).as_posix()
        except ValueError: d.fail('unsafe_path','project is outside studio')
        d.inside(root,rel); pi=d.fields((project/'PROJECT.md').read_text()); fid=folder_id(project)
        if pi.get('Document model')!='1': d.fail('invalid_project','fresh model 1 project required')
        if any(r['Project ID']==pi['Project ID'] or r['Folder ID']==fid['folder_id'] or r['Folder']==rel for r in rows): d.fail('duplicate_identity','project already registered or identity conflict')
        row={'Project ID':pi['Project ID'],'Project':pi['Project'],'Client':pi['Client'],'Code':pi['Client code'],'Type':pi['Type'],'Kind':pi['Kind'],'Status':pi['Status'],'Folder':rel,'Opened':pi['Created'],'Folder ID':fid['folder_id']}
        if info['Task register']=='portfolio' and (project/'TASKS.csv').exists():
            if d.read_csv(project/'TASKS.csv',d.TASK_FIELDS): d.fail('task_conflict','populated project tasks cannot be registered into portfolio mode')
            changes[rel+'/TASKS.csv']=None
        rows.append(row); text=replace_table(text,'projects',REGISTRY,rows); result['project']=row
    elif verb in ('set-status','archive'):
        matching=[r for r in rows if r['Project ID']==data['project_id']]
        if len(matching)!=1: d.fail('unknown_project','project is not uniquely registered')
        row=matching[0]; status='archived' if verb=='archive' else d.safe_text(data['status'])
        if not all(r['valid'] for r in valid_projects(root,rows)): d.fail('invalid_registry','registry needs review before mutation')
        actual=d.registered_folder(root,row); p=actual/'PROJECT.md'; changes[actual.relative_to(root).as_posix()+'/PROJECT.md']=setting(p.read_text(),'Status',status).encode()
        row['Status']=status; text=replace_table(text,'projects',REGISTRY,rows); result['project']=row
    elif verb=='set-naming':
        if data['policy'] not in ('as','firm','none'): d.fail('invalid_policy','unknown naming policy')
        text=setting(setting(text,'Project naming',data['policy']),'Project ID convention',data['convention'])
    elif verb=='task-mode':
        mode=data['mode']
        if mode not in ('project','portfolio'): d.fail('invalid_task_mode','unknown mode')
        if mode==info['Task register']: return {'changed':False,'mode':mode}
        paths=['TASKS.csv'] if info['Task register']=='portfolio' else [d.registered_folder(root,r).relative_to(root).as_posix()+'/TASKS.csv' for r in rows]
        for name in paths:
            if d.read_csv(d.inside(root,name),d.TASK_FIELDS): d.fail('populated_register','task mode change is limited to empty current-model registers')
            changes[name]=None
        next_paths=['TASKS.csv'] if mode=='portfolio' else [d.registered_folder(root,r).relative_to(root).as_posix()+'/TASKS.csv' for r in rows]
        for name in next_paths:
            if d.inside(root,name).exists() and name not in paths: d.fail('collision','destination register already exists')
            changes[name]=d.csv_bytes([],d.TASK_FIELDS)
        text=setting(text,'Task register',mode)
    else: d.fail('unknown_operation','unknown studio operation')
    changes['STUDIO.md']=text.encode()
    if not d.dry_run(data): d.commit(root,changes)
    return {**result,'changed':not d.dry_run(data),'dry_run':d.dry_run(data),'files':list(changes)}

def vocab(data):
    root,_,studio=d.context(data); axis=data['axis']; action=data['action']
    if axis not in ('phase','scope','originator'): d.fail('invalid_vocabulary','project owns phase/scope/originator; studio owns stages')
    text=(root/'PROJECT.md').read_text(); name=axis+'s'; rows=d.table(text,name)
    if action=='list': return {'values':[r['Value'] for r in rows],'changed':False}
    value=data['value']; table_values([value])
    if action=='add':
        if any(r['Value']==value for r in rows): return {'changed':False,'value':value}
        rows.append({'Value':value})
    elif action=='rename':
        old=data['old']; matching=[r for r in rows if r['Value']==old]
        if len(matching)!=1 or any(r['Value']==value for r in rows): d.fail('invalid_vocabulary','rename source missing or target exists')
        matching[0]['Value']=value
    else: d.fail('unknown_operation','unknown vocabulary action')
    text=replace_table(text,name,['Value'],rows)
    if action=='rename':
        affected={r['id']:{**{k:r[k] for k in d.COORDS},axis:value} for r in d.rows_for(root) if r[axis]==data['old']}
        if affected:
            template,vocab=d.configuration(root,studio); vocab[axis]=(vocab[axis]-{data['old']})|{value}
            return {**d.relocate(data,affected,config=(template,vocab),project_text=text),'values':[r['Value'] for r in rows]}
    if not d.dry_run(data): d.commit(root,{'PROJECT.md':text.encode()})
    if data.get('folder') and axis=='phase' and action=='add' and not d.dry_run(data):
        # Only an explicit folder request creates an empty phase folder.
        d.inside(root,value).mkdir(exist_ok=True)
    return {'values':[r['Value'] for r in rows],'changed':not d.dry_run(data),'dry_run':d.dry_run(data)}

def resolve_context(data):
    start=Path(data.get('path',os.getcwd())).absolute()
    if start.is_file(): start=start.parent
    if start.is_symlink(): d.fail('invalid_context','symlinked context')
    project=next((p for p in (start,*start.parents) if (p/'PROJECT.md').exists()),None)
    studio=next((p for p in (start,*start.parents) if (p/'STUDIO.md').exists()),None)
    if project:
        pi=d.fields((project/'PROJECT.md').read_text())
        if pi.get('Format version')!='3' or pi.get('Document model')!='1': d.fail('invalid_project','fresh document model 1 required')
        fid=folder_id(project); mode='project'; register=project/'TASKS.csv'
        if studio:
            _,_,si,rows=studio_context({'studio_root':str(studio)})
            matches=[r for r in valid_projects(studio,rows) if r['Project ID']==pi['Project ID'] and r['Folder ID']==fid['folder_id']]
            if len(matches)!=1 or not matches[0]['valid']: d.fail('invalid_registry','project is not uniquely valid in owning studio')
            mode=si['Task register']
            if mode=='portfolio': register=studio/'TASKS.csv'
        return {'type':'project','project_root':str(project),'studio_root':str(studio) if studio else None,'project_id':pi['Project ID'],'kind':pi['Kind'],'project_type':pi['Type'],'status':pi['Status'],'task_mode':mode,'task_register':str(register),'changed':False}
    if studio:
        _,_,_,rows=studio_context({'studio_root':str(studio)})
        choices=valid_projects(studio,rows)
        return {'type':'studio-picker' if choices else 'no-projects','studio_root':str(studio),'choices':choices,'changed':False}
    return {'type':'no-context','changed':False}

def dispatch(operation,data):
    if operation.startswith('studio.'): return studio_operation(operation.split('.',1)[1],data)
    if operation=='project.init': return project_init(data)
    if operation=='project.vocab': return vocab(data)
    if operation=='project.status':
        root,info,_=d.context(data); return {'identity':info,**d.verify(data)}
    if operation=='context.resolve': return resolve_context(data)
    d.fail('unknown_operation','unknown workspace operation')

if __name__=='__main__':
    try: print(d.json_text(dispatch(sys.argv[1],json.load(sys.stdin))))
    except (ValueError,KeyError,OSError) as e:
        print(d.json_text({'error':{'code':getattr(e,'code','invalid_input'),'message':str(e)}})); sys.exit(2)
